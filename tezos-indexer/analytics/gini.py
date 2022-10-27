from util.helper import initalizeGraphSpark,loadFile,dateParser
from pyspark.sql.functions import *
from pyspark.sql.types import StringType

# Paths
txs_path="/mnt/indexer-build/migrated_data/raw/TransactionOps"
account_path="/mnt/indexer-build/migrated_data/raw/delegate_Accounts"
destination_path="/mnt/indexer-build/migrated_data/stage/all_txs"
e1_final=["src","dst","relationship"]

spark = initalizeGraphSpark("Gini")

df_txs = loadFile(spark, txs_path, True )
df_account = loadFile(spark, account_path, True )

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

df_final = df_txs.withColumn("Week_no",udf_weekExtractor(col("Timestamp"))).withColumn("Year_no",udf_yearExtractor(col("Timestamp")))

# df_final.select("*", concat(col("Year_no"),col("Week_no")).alias("date")).write.option("header", True).partitionBy("date").mode('overwrite') \
    # .csv(destination_path)