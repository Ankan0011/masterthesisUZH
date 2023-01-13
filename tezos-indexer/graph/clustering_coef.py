from pyspark.sql.functions import lit
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os
import numpy as np
import networkx as nx
import powerlaw
import ray

ray.init()

@ray.remote
def ERGraphCoef(n, avg_clust):
    G_rand = nx.erdos_renyi_graph(n, avg_clust)    
    print("Reached end")
    return G_rand


# Method to find average degree
# Parameter: g_fdegrees : dict containing all the nodes and degree
def avg_degreeFun(g_fdegrees):
    sum = 0
    count = 0
    for i in g_fdegrees:
        sum = sum + i[1]
        count = count + 1
    return sum/count

# Paths
test_txs_path="/mnt/indexer-build/migrated_data/stage/SSC"
# test_txs_path="/mnt/indexer-build/migrated_data/raw/test_txs-1"
accounts_path="/mnt/indexer-build/migrated_data/raw/rest_Accounts"
destination_path="/mnt/indexer-build/migrated_data/curated/avg_clustering_new"

# Variables
spark = initalizeGraphSpark("PowerLawFit")
v1_cols=["Id","Balance"]
e1_cols=["SenderId","TargetId","Year_no","Week_no"]
e1_final=["src","dst","relationship"]
final_columns = ["avg_cluster_rand","avg_cluster","time_week"]

df_accounts = loadFile(spark, accounts_path, True )
v1 = df_accounts.select(v1_cols).withColumnRenamed("Id","id")

listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]

listSrcDir  = [x[0] for x in os.walk(test_txs_path)]

for x in listSrcDir:
    if x.find("relationship=20")  != -1:
        dirname = x.split("/")[-1]
        if not (dirname in listDesDir):
            print("Not Found it :"+dirname)
            df_new = loadFile(spark, x, True )
            e1 = df_new.groupBy("src","dst").count().withColumn("relationship",lit('txs')).select(e1_final).toPandas()
                    #.sample(False, 0.2, 42) \
                    
            try:
                G = nx.from_pandas_edgelist(e1, "src", "dst", create_using=nx.DiGraph())
                avg_clust = nx.average_clustering(G)
                n = G.number_of_nodes()
                # edges = G.number_of_edges()
                # all_deg = G.degree()
                # avg_degree = avg_degreeFun(all_deg)
                p = avg_clust
                print("Avg Clustering :"+str(avg_clust))
                print("p we got :"+str(p))
                

                # print("Starting ray :")

                # futures = [ERGraphCoef.remote(n=n, avg_clust= avg_clust) for i in range(25)]
                # G_rand = ray.get(futures)
        
                #  avg_clust_rand = nx.average_clustering(G_rand)
                # ERGraphCoef(n, avg_clust)
                G_rand = nx.erdos_renyi_graph(n, p)    
                avg_clust_rand = nx.average_clustering(G_rand)
                # coeff = nx.degree_assortativity_coefficient(G)
                print("Coefficient is :"+str(avg_clust))
                print("Coefficient is Random Graph:"+str(avg_clust_rand))
                
                data = [(str(avg_clust_rand),str(avg_clust), dirname.split("=")[-1])]
                next = spark.createDataFrame(data).toDF(*final_columns)
                # next.show()
                next.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)
            except NameError:
                print("Exception")
                print(NameError)

spark.stop()