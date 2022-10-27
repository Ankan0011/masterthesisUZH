from delta import *
from pyspark.sql.functions import *
from pyspark.sql.types import StringType

from util.helper import initalizeSpark,loadFile,dateParser

mining_cycle_path="/mnt/indexer-build/migrated_data/stage/mining_Cycle"
distination_path="/mnt/indexer-build/migrated_data/curated/mining"

spark = initalizeSpark("Degree")

def weekExtractor(Timestamp):
    try:
        return dateParser(Timestamp).isocalendar()[1]
    except ValueError as e:
        print('ValueError Raised:', e)
    return "NULL"

def yearExtractor(Timestamp):
    try:
        return dateParser(Timestamp).year
    except ValueError as e:
        print('ValueError Raised:', e)
    return "NULL"

udf_weekExtractor = udf(lambda x:weekExtractor(x), StringType() )
udf_yearExtractor = udf(lambda x:yearExtractor(x), StringType() )

df_mining = loadFile(spark, mining_cycle_path, True )
df_dateparsed = df_mining.withColumn("Week_no",udf_weekExtractor(col("FirstLevel_Timestamp"))).withColumn("Year_no",udf_yearExtractor(col("FirstLevel_Timestamp")))
df_cleaned_index = df_dateparsed.groupBy("Year_no","Week_no")\
    .agg(round(avg("Nakamoto_index"), 3)\
    .alias("Avg_Nakamoto_index"))
df_cleaned_index.write.option("header", True).mode('overwrite').csv(distination_path)