from pyspark.sql import Row
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os
import pandas as pd
import networkx as nx
import numpy as np
from collections import Counter

# Paths
test_txs_path="/mnt/indexer-build/migrated_data/stage/all_txs"
# accounts_path="/mnt/indexer-build/migrated_data/raw/rest_Accounts"
# destination_path="/mnt/indexer-build/migrated_data/curated/gini"
destination_path="/mnt/indexer-build/migrated_data/stage/miners_dist_node/"

# Variables
spark = initalizeGraphSpark("Gini")
# v1_cols=["Id","Balance"]
e1_cols=["SenderId","TargetId","Year_no","Week_no","Amount"]

def gini(x):
    total = 0
    for i, xi in enumerate(x[:-1], 1):
        total += np.sum(np.abs(xi - x[i:]), dtype=np.float128)
    return total / (len(x)**2 * np.mean(x))


listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]

listSrcDir  = [x[0] for x in os.walk(test_txs_path)]

for x in listSrcDir:
    if x.find("date=20")  != -1:
        dirname = x.split("/")[-1]
        if not (dirname in listDesDir):
            print("Not Found it :"+dirname.split("=")[-1])
            df_new = loadFile(spark, x, True ).select(e1_cols)
            e1 = df_new.filter(df_new['Amount'] != 0).toPandas()

            # e1 = df_new.groupBy("src","dst").count().withColumn("relationship",lit('txs')).select(e1_final).toPandas()
            G = nx.from_pandas_edgelist(
                e1, 
                "SenderId",
                "TargetId", 
                "Amount",
                create_using=nx.MultiDiGraph())
            ins = dict(G.in_degree(weight='Amount'))
            outs = dict(G.out_degree(weight='Amount'))
            z = (Counter(ins)-Counter(outs))
            df_pandas = pd.DataFrame.from_dict(z, orient='index')
            df_pandas['node'] = df_pandas.index
            df_pandas['year_week'] = str(dirname.split("=")[-1])
            # Write out the df_pandas dataframe for all the node balance
            next = spark.createDataFrame(df_pandas).withColumnRenamed("0","balance")
                # Person=Row( "year_week","gini_coff")
                # data = [ Person( str(dirname.split("=")[-1]), str(gini(df_pandas.iloc[:, 0].to_numpy()))) ]
                # next = spark.createDataFrame(data)
            # next.show()
            next.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)
spark.stop()