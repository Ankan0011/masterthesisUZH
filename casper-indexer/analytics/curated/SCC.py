from util.helper import initalizeGraphSpark,loadFile
from pyspark.sql.functions import *
from graphframes import *
import pandas as pd
from datetime import datetime
import glob, os


# Paths
user_txs="/mnt/indexer-build/migrated_data/casper_data/stage/transactions"
accounts_path="/mnt/indexer-build/migrated_data/casper_data/stage/accounts_user"
destination_path="/mnt/indexer-build/migrated_data/casper_data/curated/SSC"
e1_final=["from","to","relationship"]


# Paths
# test_txs_path="/mnt/indexer-build/migrated_data/stage/SSC"
# # test_txs_path="/mnt/indexer-build/migrated_data/raw/test_txs-1"
# accounts_path="/mnt/indexer-build/migrated_data/raw/rest_Accounts"
# destination_path="/mnt/indexer-build/migrated_data/curated/SSC"
temp_log="/mnt/indexer-build/migrated_data/logs"

# Variables
spark = initalizeGraphSpark("SSC")
v1_cols=["Id","Balance"]
e1_cols=["SenderId","TargetId","Year_no","Week_no"]
# e1_final=["src","dst","relationship"]
e1_final=["from","to","relationship"]

df_accounts = loadFile(spark, accounts_path, True )
v1 = df_accounts.withColumnRenamed("account","id")

listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]

listSrcDir  = [x[0] for x in os.walk(user_txs)]

for x in listSrcDir:
    if x.find("date=20")  != -1:
        dirname = x.split("/")[-1]
        if not (dirname in listDesDir):
            print("Not Found it :"+dirname)
            #print(dirname.split("=")[-1])
            df_new = loadFile(spark, x, True )
            # e1 = df_new.withColumn("relationship",lit('txs'))
            #e1 = df_new.groupBy("src","dst").count().withColumn("relationship",lit('txs')).select(e1_final)
            e1 = df_new.filter(col("from").isNotNull()).filter(col("to").isNotNull()) \
                .groupBy("from","to").count().withColumn("relationship",lit('txs')).select(e1_final) \
                .withColumnRenamed("from","src").withColumnRenamed("to","dst")

            g = GraphFrame(v1,e1).dropIsolatedVertices()
            result = g.stronglyConnectedComponents(maxIter=10)
            final = result.select("id", "component").groupBy("component").agg(countDistinct(result["id"]).alias("count"))
            next = final.agg(max("count").alias("max_count")).withColumn("time_week",lit(dirname.split("=")[-1])).withColumn("Total_Vertices",lit(g.vertices.count()))
            # next.show()
            next.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)

spark.stop()