from pyspark.sql import Row
from pyspark.sql.functions import *
from util.helper import initalizeGraphSpark,loadFile
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from graphframes import *
import os
import pandas as pd
import networkx as nx
import numpy as np
from collections import Counter

# Paths
txs_path="/mnt/indexer-build/migrated_data/casper_data/stage/transactions"
destination_path="/mnt/indexer-build/migrated_data/casper_data/stage/gini_txs"

# Variables
spark = initalizeGraphSpark("Miner-Dist")
# v1_cols=["Id","Balance"]
e1_cols=["from","to","Year_no","Week_no","denomAmount"]

listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]
listSrcDirNew  = [x[0].split("/")[-1] for x in os.walk(txs_path)]
newlist = []
newlist2 = []

for i in listSrcDirNew:
    new = i.split("=")[-1]
    newlist.append(new)

new_seq = np.sort(newlist)
for i in new_seq:
    new = str("/mnt/indexer-build/migrated_data/casper_data/stage/transactions/date="+i)
    newlist2.append(new)
# print(newlist2)

schema = StructType([
  StructField('from', StringType(), True),
  StructField('to', StringType(), True),
  StructField('Year_no', StringType(), True),
  StructField('Week_no', StringType(), True),
  StructField('denomAmount', IntegerType(), True)
  ])
temp_df = spark.createDataFrame([], schema)
temp_df.show()

listSrcDir  = [x[0] for x in os.walk(txs_path)]

for x in newlist2:
    if x.find("date=20")  != -1:
        dirname = x.split("/")[-1]
        if not (dirname in listDesDir):
            print("Not Found it :"+dirname.split("=")[-1])
            df_new = loadFile(spark, x, True ).select(e1_cols).filter(col("from").isNotNull()).filter(col("to").isNotNull())
            e1 = df_new.filter(df_new['denomAmount'] != 0)
            temp_df = temp_df.union(e1)
            print("Count :"+str(temp_df.count()))

            final = temp_df.groupBy("from","to").sum("denomAmount").withColumnRenamed("sum(denomAmount)","Amount")
            final.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)
spark.stop()