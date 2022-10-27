from pyspark.sql.functions import lit
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os
import networkx as nx

# Paths
test_txs_path="/mnt/indexer-build/migrated_data/stage/SSC"
# test_txs_path="/mnt/indexer-build/migrated_data/raw/test_txs-1"
accounts_path="/mnt/indexer-build/migrated_data/raw/rest_Accounts"
destination_path="/mnt/indexer-build/migrated_data/curated/assortativity_coeff"

# Variables
spark = initalizeGraphSpark("Debug")
v1_cols=["Id","Balance"]
e1_cols=["SenderId","TargetId","Year_no","Week_no"]
e1_final=["src","dst","relationship"]
final_columns = ["assortative_coeff","time_week"]

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
            try:
                G = nx.from_pandas_edgelist(e1, "src", "dst", create_using=nx.DiGraph())
                coeff = nx.degree_assortativity_coefficient(G)
                # print("Coefficient is :"+str(coeff))
                data = [(str(coeff), dirname.split("=")[-1])]
                next = spark.createDataFrame(data).toDF(*final_columns)
                # next.show()
                next.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)
            except NameError:
                print("Exception")
                print(NameError)

spark.stop()