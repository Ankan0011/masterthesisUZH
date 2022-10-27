from util.helper import initalizeSpark,loadFile
import math
from pyspark.sql.functions import *
from pyspark.sql.types import StringType
from pyspark.sql.functions import col,min,max

baking_cycle_path="/mnt/indexer-build/migrated_data/raw/mining_Cycle"
usr_txs_path="/mnt/indexer-build/migrated_data/stage/user_txs"
spark = initalizeSpark("Exploration")
col =["Level","Timestamp"]

df_cycle = loadFile(spark, baking_cycle_path, True )
df_txs = loadFile(spark, usr_txs_path, True )
df_level=df_txs.select(*col).groupBy("Level").agg(max("Timestamp").alias("Timestamp"))

#Join to find the timestamp of start and end date of each cycle
FirstLevel =df_cycle.join(df_level, df_cycle.FirstLevel == df_level.Level, "inner").select(df_cycle["*"],df_level["Timestamp"]).withColumnRenamed("Timestamp", "FirstLevel_Timestamp")
First_Last_Level =FirstLevel.join(df_level, FirstLevel.LastLevel == df_level.Level, "inner").select(FirstLevel["*"],df_level["Timestamp"]).withColumnRenamed("Timestamp", "LastLevel_Timestamp")

First_Last_Level.write.option("header", True).mode('overwrite').csv("/mnt/indexer-build/migrated_data/stage/mining_Cycle")