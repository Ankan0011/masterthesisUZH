from util.helper import initalizeSpark
import math
from pyspark.sql.functions import *
from pyspark.sql.types import StringType
from pyspark.sql.functions import col,min,max

baking_cycle_path="/mnt/indexer-build/migrated_data/Cycles.csv"
spark = initalizeSpark("Exploration")


def cycleNakamoto(count):
    try:
        return math.floor(count/3)
    except ValueError as e:
        print('ValueError Raised:', e)
    return "0"

udf_NakamotoCal = udf(lambda x:cycleNakamoto(x), StringType() )

#Max Date Time Analysis on Transaction Data
#df = loadFile(spark, test_txs_path, True )
df_cycle = spark.read.option("header", True) \
    .option("inferSchema", "true") \
    .option("ignoreLeadingWhiteSpace", "true") \
    .option("ignoreTrailingWhiteSpace", "true") \
    .csv(baking_cycle_path) 

df_final=df_cycle.withColumn("Nakamoto_index",udf_NakamotoCal(col("TotalBakers")))
#df_final.show(5)
df_final.write.option("header", True).mode('overwrite').csv("/mnt/indexer-build/migrated_data/raw/mining_Cycle")