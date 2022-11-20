from pyspark.sql.functions import lit,col
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os
import networkx as nx

# Paths
user_txs="/mnt/indexer-build/migrated_data/casper_data/stage/transactions"
accounts_path="/mnt/indexer-build/migrated_data/casper_data/stage/all_accounts"
destination_path="/mnt/indexer-build/migrated_data/casper_data/curated/assortativity_coefficient"

# Variables
spark = initalizeGraphSpark("Curated")
#v1_cols=["Id","Balance"]
e1_cols=["SenderId","TargetId","Year_no","Week_no"]
e1_final=["from","to","relationship"]
final_columns = ["max_count","time_week"]

df_accounts = loadFile(spark, accounts_path, True )
df_accounts.withColumnRenamed("account","id")

listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]

listSrcDir  = [x[0] for x in os.walk(user_txs)]

for x in listSrcDir:
    if x.find("date=20")  != -1:
        dirname = x.split("/")[-1]
        if not (dirname in listDesDir):
            print("Not Found it :"+dirname)
            df_new = loadFile(spark, x, True )
            e1 = df_new.filter(col("from").isNotNull()).filter(col("to").isNotNull()) \
                .groupBy("from","to").count().withColumn("relationship",lit('txs')).select(e1_final).toPandas()
            
            try:
                G = nx.from_pandas_edgelist(e1, "from", "to", create_using=nx.DiGraph())
                coeff = nx.degree_assortativity_coefficient(G)
                # print("Coefficient is :"+str(coeff))
                data = [(str(coeff), dirname.split("=")[-1])]
                next = spark.createDataFrame(data).toDF(*final_columns)
                #next.show()
                next.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)
            except NameError:
                print("Exception")
                print(NameError)

spark.stop()