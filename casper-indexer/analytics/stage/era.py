from util.helper import initalizeSpark,dateMilParser,loadFile
from pyspark.sql.functions import *
from pyspark.sql.types import StringType
import math

cycle_path="/mnt/indexer-build/migrated_data/casper_data/raw/era"
distination_path="/mnt/indexer-build/migrated_data/casper_data/curated/nakamoto"

spark = initalizeSpark("stage")

def weekExtractor(Timestamp):
    try:
        return dateMilParser(Timestamp).isocalendar()[1]
    except ValueError as e:
        print('ValueError Week Raised:', e)
    return "NULL"

def yearExtractor(Timestamp):
    try:
        return dateMilParser(Timestamp).year
    except ValueError as e:
        print('ValueError Year Raised:', e)
    return "NULL"

def cycleNakamoto(count):
    try:
        return math.floor(count/3)
    except ValueError as e:
        print('ValueError Nakamoto Raised:', e)
    return "0"

udf_NakamotoCal = udf(lambda x:cycleNakamoto(x), StringType() )
udf_weekExtractor = udf(lambda x:weekExtractor(x), StringType() )
udf_yearExtractor = udf(lambda x:yearExtractor(x), StringType() )

df_cycle = loadFile(spark, cycle_path, True )
#df_cycle.select("start").show(5)
df_parsed_time = df_cycle.withColumn("Week_no",udf_weekExtractor(col("start"))).withColumn("Year_no",udf_yearExtractor(col("start"))) \
                        .withColumn("Nakamoto_index",udf_NakamotoCal(col("validators_count")))

df_final = df_parsed_time.groupBy("Year_no","Week_no").agg(avg("Nakamoto_index").alias("Avg_Nakamoto_index"))
df_final.write.option("header", True).mode('overwrite').csv(distination_path)