from util.helper import initalizeSpark
import math
from pyspark.sql.functions import *
from pyspark.sql.types import StringType
from pyspark.sql.functions import col,min,max

baking_cycle_path="/mnt/indexer-build/migrated_data/BakerCycles.csv"
spark = initalizeSpark("Exploration")

#Max Date Time Analysis on Transaction Data
#df = loadFile(spark, test_txs_path, True )
df_baking = spark.read.option("header", True) \
    .option("inferSchema", "true") \
    .option("ignoreLeadingWhiteSpace", "true") \
    .option("ignoreTrailingWhiteSpace", "true") \
    .csv(baking_cycle_path) 

df_new = df_baking.groupBy("Cycle").agg(
    count(when(df_baking['Blocks'] != 0, df_baking['Blocks'])).alias("Blocks_Count"),
    sum(when(df_baking['Blocks'] != 0, df_baking['Blocks'])).alias("Blocks_Sum"),
    count_distinct("BakerId"),
    count(when(df_baking['BlockRewards'] != 0, df_baking['BlockRewards'])).alias("Blocks_Rewards"),
    )

df_new.show(5)