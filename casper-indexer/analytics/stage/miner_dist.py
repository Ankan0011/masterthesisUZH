from pyspark.sql import Row
from pyspark.sql.functions import *
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os
import pandas as pd
import networkx as nx
import numpy as np
from collections import Counter

# Paths
txs_path="/mnt/indexer-build/migrated_data/casper_data/stage/transactions"
destination_path="/mnt/indexer-build/migrated_data/casper_data/stage/miners_dist_node"

# Variables
spark = initalizeGraphSpark("Miner-Dist")
# v1_cols=["Id","Balance"]
e1_cols=["from","to","Year_no","Week_no","denomAmount"]

listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]

listSrcDir  = [x[0] for x in os.walk(txs_path)]

for x in listSrcDir:
    if x.find("date=20")  != -1:
        dirname = x.split("/")[-1]
        if not (dirname in listDesDir):
            print("Not Found it :"+dirname.split("=")[-1])
            df_new = loadFile(spark, x, True ).select(e1_cols).filter(col("from").isNotNull()).filter(col("to").isNotNull())
            e1 = df_new.filter(df_new['denomAmount'] != 0).toPandas()

            # e1 = df_new.groupBy("src","dst").count().withColumn("relationship",lit('txs')).select(e1_final).toPandas()
            G = nx.from_pandas_edgelist(
                e1, 
                "from",
                "to", 
                "denomAmount",
                create_using=nx.MultiDiGraph())
            ins = dict(G.in_degree(weight='denomAmount'))
            outs = dict(G.out_degree(weight='denomAmount'))
            z = (Counter(ins)-Counter(outs))
            df_pandas = pd.DataFrame.from_dict(z, orient='index')
            df_pandas['node'] = df_pandas.index
            df_pandas['year_week'] = str(dirname.split("=")[-1])
            # Write out the df_pandas dataframe for all the node balance
            next = spark.createDataFrame(df_pandas).withColumnRenamed("0","balance")
            # next.show()
            next.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)
spark.stop()