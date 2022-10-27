from pyspark.sql.functions import lit, col, udf
from pyspark.sql.types import StringType
from pyspark.sql import Row
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os

# Paths
test_txs_path="/mnt/indexer-build/migrated_data/stage/all_txs"
rest_accounts="/mnt/indexer-build/migrated_data/raw/rest_Accounts"
delegator_path="/mnt/indexer-build/migrated_data/raw/delegate_Accounts"
destination_path="/mnt/indexer-build/migrated_data/stage/miners_dist"

# Variables
spark = initalizeGraphSpark("Miners-Distance")
e1_cols=["SenderId","TargetId","Year_no","Week_no","Amount"]
e1_final=["src","dst","relationship"]

listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]
listSrcDir  = [x[0] for x in os.walk(test_txs_path)]


df_new = loadFile(spark, delegator_path, True ).select("Id").withColumnRenamed("Id", "id").distinct()
df_rest = loadFile(spark, rest_accounts, True ).select("Id").withColumnRenamed("Id", "id").distinct()

all_acc = df_new.unionAll(df_rest)

def minPathExtractor(distance, id):
    if len(distance) != 0:
        return min(distance.values())
    else:
        return "NULL"

udf_minPathExtractor = udf(lambda x, y:minPathExtractor(x, y), StringType() )


for x in listSrcDir:
    if x.find("date=201827")  != -1:
        dirname = x.split("/")[-1]
        # if not (dirname in listDesDir):
            # print("Not Found it :"+dirname)
        df_file = loadFile(spark, x, True ).select(e1_cols)
        e1 = df_file.filter(df_file['Amount'] != 0).filter(col("SenderId").isNotNull()) \
            .filter(col("TargetId").isNotNull())

        delegetor = df_new.join(e1, e1.SenderId == df_new.id, "inner").select("id").distinct()
        # data_array = (delegetor.select("id").collect())
        data_array = [ str(row.id) for row in delegetor.select("id").collect()]

        e2 = e1.groupBy("SenderId","TargetId").count().withColumn("relationship",lit('txs')).withColumnRenamed("SenderId", "src") \
            .withColumnRenamed("TargetId", "dst").select(e1_final)

        g = GraphFrame(all_acc, e2).dropIsolatedVertices()
        results = g.shortestPaths(landmarks=data_array)
        final = results.select("id","distances").withColumn("distances",udf_minPathExtractor(col("distances"), col("id"))).withColumn("year_week", lit(str(dirname.split("=")[-1])))
        final.show(10)
        # final.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)