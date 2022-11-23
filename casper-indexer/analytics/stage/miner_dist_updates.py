from pyspark.sql.functions import lit, col, udf
from pyspark.sql.types import StringType
from pyspark.sql import Row
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os

# Paths
txs_path="/mnt/indexer-build/migrated_data/casper_data/stage/transactions"
destination_path="/mnt/indexer-build/migrated_data/casper_data/stage/miners_dist"
all_accounts="/mnt/indexer-build/migrated_data/casper_data/stage/all_accounts"
validator_path="/mnt/indexer-build/migrated_data/casper_data/stage/validators"

# Variables
spark = initalizeGraphSpark("Miners-Distance")
e1_cols=["from","to","Year_no","Week_no","denomAmount"]
e1_final=["src","dst","relationship"]

listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]
listSrcDir  = [x[0] for x in os.walk(txs_path)]

df_new = loadFile(spark, validator_path, True ).withColumnRenamed("public_key", "id").distinct()
all_acc = loadFile(spark, all_accounts, True ).withColumnRenamed("account", "id").distinct()

def minPathExtractor(distance, id):
    if len(distance) != 0:
        return min(distance.values())
    else:
        return "NULL"

udf_minPathExtractor = udf(lambda x, y:minPathExtractor(x, y), StringType() )


for x in listSrcDir:
    if x.find("date=20")  != -1:
        dirname = x.split("/")[-1]
        # if not (dirname in listDesDir):
            # print("Not Found it :"+dirname)
        df_file = loadFile(spark, x, True ).select(e1_cols)
        e1 = df_file.filter(df_file['denomAmount'] != 0).filter(col("to").isNotNull()) \
            .filter(col("from").isNotNull())

        delegetor = df_new.join(e1, df_new["id"] == e1["from"], "inner").select("id").distinct()
        print("Checking the count :"+str(delegetor.count()))
        # data_array = (delegetor.select("id").collect())
        data_array = [ str(row.id) for row in delegetor.select("id").collect()]

        e2 = e1.groupBy("from","to").count().withColumn("relationship",lit('txs')).withColumnRenamed("from", "src") \
            .withColumnRenamed("to", "dst").select(e1_final)

        g = GraphFrame(all_acc, e2).dropIsolatedVertices()
        results = g.shortestPaths(landmarks=data_array)
        final = results.select("id","distances").withColumn("distances",udf_minPathExtractor(col("distances"), col("id"))).withColumn("year_week", lit(str(dirname.split("=")[-1])))
        # final.show(10)
        final.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)