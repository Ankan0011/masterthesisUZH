from util.helper import initalizeSpark,dateParser,loadFile
from pyspark.sql.functions import *
from pyspark.sql.types import StringType

user_txs="/mnt/indexer-build/migrated_data/casper_data/raw/transactions"
distination_path="/mnt/indexer-build/migrated_data/casper_data/stage/transactions"

spark = initalizeSpark("stage")

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

df_txs = loadFile(spark, user_txs, True )

df_parsed_time = df_txs.withColumn("Week_no",udf_weekExtractor(col("timestamp"))).withColumn("Year_no",udf_yearExtractor(col("timestamp")))

df_parsed_time.select("*", concat(col("Year_no"),col("Week_no")).alias("date")).write.option("header", True).partitionBy("date").mode('overwrite') \
     .csv(distination_path)