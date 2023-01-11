from pyspark.sql.functions import lit
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os
import numpy as np
import networkx as nx
import powerlaw
from scipy.stats import kstest

# Paths
test_txs_path="/mnt/indexer-build/migrated_data/stage/SSC"
# test_txs_path="/mnt/indexer-build/migrated_data/raw/test_txs-1"
accounts_path="/mnt/indexer-build/migrated_data/raw/rest_Accounts"
destination_path="/mnt/indexer-build/migrated_data/curated/powerlaw_revised"

# Variables
spark = initalizeGraphSpark("PowerLawFit")
v1_cols=["Id","Balance"]
e1_cols=["SenderId","TargetId","Year_no","Week_no"]
e1_final=["src","dst","relationship"]
final_columns = ["powerlaw_alpha", "exponential_fit_p", "trucatedpower_fit_p", "lognormal_fit_p",  "exponential_fit_r", "trucatedpower_fit_r", "lognormal_fit_r","time_week"]

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
                k = np.sort(np.asarray([d for d in dict(G.degree()).values()]), )
                fit = powerlaw.Fit(k, discrete=True)
                # xmin  = fit.power_law.xmin
                alpha = fit.power_law.alpha  
                # print(kstest(k, 'powerlaw', args =(alpha,xmin), N = len(k)))
                # kstest(k, 'norm')
                r1, p1 = fit.distribution_compare('power_law', 'exponential', normalized_ratio=True)
                r2, p2 = fit.distribution_compare('power_law', 'truncated_power_law')
                r3, p3 = fit.distribution_compare('power_law', 'lognormal')
                
                # coeff = nx.degree_assortativity_coefficient(G)
                # print("Coefficient is :"+str(coeff))
                data = [(str(alpha),str(p1), str(p2), str(p3), str(r1), str(r2), str(r3), dirname.split("=")[-1])]
                next = spark.createDataFrame(data).toDF(*final_columns)
                # next.show()
                next.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)
            except NameError:
                print("Exception")
                print(NameError)

spark.stop()