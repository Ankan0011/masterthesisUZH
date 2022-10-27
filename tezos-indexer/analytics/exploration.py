from util.helper import initalizeSpark,loadFile
from pyspark.sql.functions import col,min,max

test_txs_path="/mnt/indexer-build/migrated_data/stage/user_txs"
spark = initalizeSpark("Exploration")

#Max Date Time Analysis on Transaction Data
df_txs = loadFile(spark, test_txs_path, True )

#df=df_txs.withColumn("Timestamp", col("Timestamp").cast("timestamp"))
#df.select(min("Timestamp")).show()