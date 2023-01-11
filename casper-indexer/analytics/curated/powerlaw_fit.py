from pyspark.sql.functions import lit,col
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os
import networkx as nx
import powerlaw
import numpy as np

# Paths
user_txs="/mnt/indexer-build/migrated_data/casper_data/stage/transactions"
accounts_path="/mnt/indexer-build/migrated_data/casper_data/stage/all_accounts"
destination_path="/mnt/indexer-build/migrated_data/casper_data/curated/powerlaw_revised"

# Variables
spark = initalizeGraphSpark("Curated")
#v1_cols=["Id","Balance"]
e1_cols=["SenderId","TargetId","Year_no","Week_no"]
e1_final=["from","to","relationship"]
final_columns = ["powerlaw_alpha", "exponential_fit_p", "trucatedpower_fit_p", "lognormal_fit_p",  "exponential_fit_r", "trucatedpower_fit_r", "lognormal_fit_r","time_week"]
# final_columns = ["powerlaw_alpha","time_week"]

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
                k = np.sort(np.asarray([d for d in dict(G.degree()).values()]), )
                fit = powerlaw.Fit(k, discrete=True)
                alpha = fit.power_law.alpha
                r1, p1 = fit.distribution_compare('power_law', 'exponential', normalized_ratio=True)
                r2, p2 = fit.distribution_compare('power_law', 'truncated_power_law')
                r3, p3 = fit.distribution_compare('power_law', 'lognormal')

                # coeff = nx.degree_assortativity_coefficient(G)
                # print("Coefficient is :"+str(coeff))
                data = [(str(alpha),str(p1), str(p2), str(p3), str(r1), str(r2), str(r3), dirname.split("=")[-1])]
                # data = [(str(alpha), dirname.split("=")[-1])]
                next = spark.createDataFrame(data).toDF(*final_columns)
                # next.show()
                next.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)
            except NameError:
                print("Exception")
                print(NameError)

spark.stop()