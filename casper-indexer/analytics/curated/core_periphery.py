import pandas as pd
import cpnet, os
import networkx as nx
import numpy as np
from util.helper import initalizeGraphSpark,loadFile
from pyspark.sql.functions import *

# Paths
user_txs="/mnt/indexer-build/migrated_data/casper_data/stage/transactions"
destination_path="/mnt/indexer-build/migrated_data/casper_data/curated/core_periphery"
e1_final=["from","to","relationship"]

spark = initalizeGraphSpark("Core-Periphery")

listSrcDir  = [x[0] for x in os.walk(user_txs)]

alg = cpnet.Lip() #Fast Bipartition Algo

def count_dict(core, weekno):
    core_count = 0
    for i in core.values():
        if i == 1:
            core_count += 1
    return [(weekno, core_count, len(core))]


for x in listSrcDir:
    if x.find("date=20")  != -1:
        dirname = x.split("/")[-1]
        print(dirname)
        weekno=dirname.split("=")[-1]
        df_new = loadFile(spark, x, True )
        df_final = df_new.filter(col("from").isNotNull()).filter(col("to").isNotNull()) \
                .groupBy("from","to").count().withColumn("relationship",lit('txs')).select(e1_final).toPandas()

        # df_final = df_new.groupBy("src","dst").count().withColumn("relationship",lit('txs')).select(e1_final).toPandas()
        # G = nx.from_pandas_dataframe(df_final, 'src', 'dst', ['relationship'])
        G = nx.from_pandas_edgelist(df_final, "from", "to")
        alg.detect(G)
        x = alg.get_coreness()  # Get the coreness of nodes
        size = G.size()
        df_response = pd.DataFrame.from_records(count_dict(x, weekno), columns =['week_no', 'core_count', 'network_size'])
        spark_df = spark.createDataFrame(df_response)
        # spark_df.show()
        spark_df.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)

spark.stop()