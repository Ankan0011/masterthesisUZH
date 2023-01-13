from pyspark.sql import Row
from pyspark.sql.functions import *
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os
import numpy as np
from numba import njit

# Paths
txs_path="/mnt/indexer-build/migrated_data/casper_data/stage/gini_txs"
destination_path="/mnt/indexer-build/migrated_data/casper_data/curated/gini_updated"

# Variables
spark = initalizeGraphSpark("Gini")
e1_cols=["from","to","Amount"]
diff_cols=["Accounts","Debit","Credit"]

@njit(fastmath = True)
def gini(x):
    total = 0
    for i, xi in enumerate(x[:-1], 1):
        total += np.sum(np.abs(xi - x[i:]), dtype=np.float64)
    return total / (len(x)**2 * np.mean(x))


listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]
listSrcDir  = [x[0] for x in os.walk(txs_path)]

listSrcDirNew  = [x[0].split("/")[-1] for x in os.walk(txs_path)]

newlist = []
newlist2 = []

for i in listSrcDirNew:
    new = i.split("=")[-1]
    newlist.append(new)

new_seq = np.sort(newlist)
for i in new_seq:
    new = str("/mnt/indexer-build/migrated_data/casper_data/stage/gini_txs/date="+i)
    newlist2.append(new)


for x in newlist2:
    if x.find("date=20")  != -1:
        dirname = x.split("/")[-1]
        if not (dirname in listDesDir):
            print("Not Found it :"+dirname.split("=")[-1])
            df_new = loadFile(spark, x, True ).select(e1_cols).filter(col("from").isNotNull()).filter(col("to").isNotNull())
            e1 = df_new.filter(df_new['Amount'] != 0)
            total_account1 = e1.select("from")
            total_account2 = e1.select("to")
            total_acc = total_account1.union(total_account2).withColumnRenamed("from", "Accounts").distinct()
            debit = e1.groupBy("from").sum("Amount").withColumnRenamed("sum(Amount)","Debit").withColumnRenamed("from","From")
            credit = e1.groupBy("to").sum("Amount").withColumnRenamed("sum(Amount)","Credit")
            newdf = total_acc.join(debit, total_acc.Accounts ==  debit.From,"leftouter").join(credit, total_acc.Accounts == credit.to, "leftouter").select(diff_cols)
        
            df = newdf.withColumn("Balance",
                            when(newdf.Debit.isNull() , newdf.Credit)
                            .when(newdf.Credit.isNull() , -1*newdf.Debit)
                            .otherwise(newdf.Credit - newdf.Debit))
        
            print("Checking total rows :"+str(df.count()))
            df_filtered = df.filter(df['Balance'] > 0).toPandas()

            Person=Row( "year_week","gini_coff")

            data = [ Person( str(dirname.split("=")[-1]), str(gini(df_filtered.iloc[:, 3].to_numpy()))) ]
            next = spark.createDataFrame(data)
            next.show()
            next.write.option("header", True).mode('overwrite').csv(destination_path+"/"+dirname)
            
spark.stop()