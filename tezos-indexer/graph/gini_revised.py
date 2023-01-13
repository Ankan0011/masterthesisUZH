from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os
import numpy as np


# Paths
test_txs_path="/mnt/indexer-build/migrated_data/stage/all_txs"
# accounts_path="/mnt/indexer-build/migrated_data/raw/rest_Accounts"
# destination_path="/mnt/indexer-build/migrated_data/curated/gini"
destination_path="/mnt/indexer-build/migrated_data/stage/Gini_txs/"

# Variables
spark = initalizeGraphSpark("Gini")
# v1_cols=["Id","Balance"]
e1_cols=["SenderId","TargetId","Year_no","Week_no","Amount"]


listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]

listSrcDirNew  = [x[0].split("/")[-1] for x in os.walk(test_txs_path)]
newlist = []
newlist2 = []

for i in listSrcDirNew:
    new = i.split("=")[-1]
    newlist.append(new)

new_seq = np.sort(newlist)
for i in new_seq:
    new = str("/mnt/indexer-build/migrated_data/stage/all_txs/date="+i)
    newlist2.append(new)

# print(newlist2)

listSrcDir  = [x[0] for x in os.walk(test_txs_path)]
#print(listSrcDir)
schema = StructType([
  StructField('SenderId', StringType(), True),
  StructField('TargetId', StringType(), True),
  StructField('Year_no', StringType(), True),
  StructField('Week_no', StringType(), True),
  StructField('Amount', IntegerType(), True)
  ])
temp_df = spark.createDataFrame([], schema)
temp_df.show()

for x in newlist2:
    if x.find("date=20")  != -1:
        dirname = x.split("/")[-1]
        if not (dirname in listDesDir):
            print("Not Found it :"+dirname.split("=")[-1])
            df_new = loadFile(spark, x, True ).select(e1_cols).filter(col("SenderId").isNotNull()).filter(col("TargetId").isNotNull())
            e1 = df_new.filter(df_new['Amount'] != 0)
            temp_df = temp_df.union(e1)
            print("Count :"+str(temp_df.count()))
            # df_new.show(10)

            final = temp_df.groupBy("SenderId","TargetId").sum("Amount").withColumnRenamed("sum(Amount)","Amount")
            final.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)
            #temp_df = e1
spark.stop()