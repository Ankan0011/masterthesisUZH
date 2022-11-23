from util.helper import initalizeGraphSpark,loadFile
from pyspark.sql.functions import *
from graphframes import *
import pandas as pd
from datetime import datetime
import glob, os

# Paths
test_txs_path="/mnt/indexer-build/migrated_data/stage/SSC"
# test_txs_path="/mnt/indexer-build/migrated_data/raw/test_txs-1"
accounts_path="/mnt/indexer-build/migrated_data/raw/rest_Accounts"
destination_path="/mnt/indexer-build/migrated_data/curated/SSC"
temp_log="/mnt/indexer-build/migrated_data/logs"

# Variables
spark = initalizeGraphSpark("SSC")
v1_cols=["Id","Balance"]
e1_cols=["SenderId","TargetId","Year_no","Week_no"]
e1_final=["src","dst","relationship"]

df_accounts = loadFile(spark, accounts_path, True )
v1 = df_accounts.select(v1_cols).withColumnRenamed("Id","id")

listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]

listSrcDir  = [x[0] for x in os.walk(test_txs_path)]

for x in listSrcDir:
    if x.find("relationship=202044")  != -1:
        dirname = x.split("/")[-1]
        # if not (dirname in listDesDir):
        print("Not Found it :"+dirname)
        #print(dirname.split("=")[-1])
        df_new = loadFile(spark, x, True )
        # e1 = df_new.withColumn("relationship",lit('txs'))
        e1 = df_new.groupBy("src","dst").count().withColumn("relationship",lit('txs')).select(e1_final)
        g = GraphFrame(v1,e1).dropIsolatedVertices()
        result = g.stronglyConnectedComponents(maxIter=10)
        result.show(10)
        # final = result.select("id", "component").groupBy("component").agg(countDistinct(result["id"]).alias("count"))
        # next = final.agg(max("count").alias("max_count")).withColumn("time_week",lit(dirname.split("=")[-1])).withColumn("Total_Vertices",lit(g.vertices.count()))
        # next.show()
        # next.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)

spark.stop()