from pyspark.sql import Row
from pyspark.sql.functions import *
from pyspark.sql.types import StringType, IntegerType
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os
import pandas as pd
import networkx as nx
import numpy as np
import multiprocessing as mp
from numba import njit


# Paths
test_txs_path="/mnt/indexer-build/migrated_data/stage/Gini_txs"
# accounts_path="/mnt/indexer-build/migrated_data/raw/rest_Accounts"
# destination_path="/mnt/indexer-build/migrated_data/curated/gini"
destination_path="/mnt/indexer-build/migrated_data/curated/gini_revised/"

# Variables
spark = initalizeGraphSpark("Gini")
# v1_cols=["Id","Balance"]
e1_cols=["SenderId","TargetId","Amount"]
diff_cols=["Accounts","Debit","Credit"]


# def gini_sum(i, xi, x_arr):
#     temp=0
#     temp += np.sum(np.abs(xi - x_arr[i:]), dtype=np.float64)
#     return temp

@njit(fastmath = True)
def gini(x):
    total = 0
    for i, xi in enumerate(x[:-1], 1):
        total += np.sum(np.abs(xi - x[i:]), dtype=np.float64)
    return total / (len(x)**2 * np.mean(x))

# def gini(x_arr):
#     total = 0
#     # pool = mp.Pool(mp.cpu_count())
#     # total = [pool.apply(gini_sum, args= (i, xi, x_arr)) for i, xi in enumerate(x_arr[:-1], 1)]
#     for i, xi in enumerate(x_arr[:-1], 1):
#         total = gini_sum(i, xi, x_arr)
#     print("Reached Destination")
#     return total / (len(x_arr)**2 * np.mean(x_arr))

listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]
listSrcDir  = [x[0] for x in os.walk(test_txs_path)]
listSrcDirNew  = [x[0].split("/")[-1] for x in os.walk(test_txs_path)]

newlist = []
newlist2 = []

for i in listSrcDirNew:
    new = i.split("=")[-1]
    newlist.append(new)

new_seq = np.sort(newlist)
for i in new_seq:
    new = str("/mnt/indexer-build/migrated_data/stage/Gini_txs/date="+i)
    newlist2.append(new)


#print(listSrcDir
for x in newlist2:
    if x.find("date=20")  != -1:
        dirname = x.split("/")[-1]
        if not (dirname in listDesDir):
            print("Not Found it :"+dirname.split("=")[-1])
            df_new = loadFile(spark, x, True ).select(e1_cols).select(e1_cols).filter(col("SenderId").isNotNull()).filter(col("TargetId").isNotNull())
            e1 = df_new.filter(df_new['Amount'] != 0)
            total_account1 = e1.select("SenderId")
            total_account2 = e1.select("TargetId")
            total_acc = total_account1.union(total_account2).withColumnRenamed("SenderId", "Accounts").distinct()
            debit = e1.groupBy("SenderId").sum("Amount").withColumnRenamed("sum(Amount)","Debit")
            credit = e1.groupBy("TargetId").sum("Amount").withColumnRenamed("sum(Amount)","Credit")
            newdf = total_acc.join(debit, total_acc.Accounts ==  debit.SenderId,"leftouter").join(credit, total_acc.Accounts == credit.TargetId, "leftouter").select(diff_cols)
            # df = newdf.withColumn("Balance", udf_Balance(col("Debit"),col("Credit")))
            df = newdf.withColumn("Balance",
                            when(newdf.Debit.isNull() , newdf.Credit)
                            .when(newdf.Credit.isNull() , -1*newdf.Debit)
                            .otherwise(newdf.Credit - newdf.Debit))

            print("Checking total rows :"+str(df.count()))
            df_filtered = df.filter(df['Balance'] > 0).toPandas()

            Person=Row( "year_week","gini_coff")

            # futures = [gini.remote(df_filtered.iloc[:, 3].to_numpy()) for i in range(20)]
            # gini_coeff = ray.get(futures)

            data = [ Person( str(dirname.split("=")[-1]), str(gini(df_filtered.iloc[:, 3].to_numpy()))) ]
            next = spark.createDataFrame(data)
            next.show()
            next.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)

spark.stop()