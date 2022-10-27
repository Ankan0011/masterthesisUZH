from pyspark.sql import SparkSession
from delta import *
from pyspark.sql.functions import *

builder = SparkSession.builder.appName("TransactionOps") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.jars", "//mnt/indexer-build/jar/postgresql-42.5.0.jar") \
    .config("spark.executor.memory", "12g") \
    .config("spark.executor.cores", "3") \
    .config('spark.cores.max', '6') \
    .config('spark.driver.memory','4g') \
    .config('spark.worker.cleanup.enabled', 'true') \
    .config('spark.worker.cleanup.interval', '60') \
    .config('spark.shuffle.service.db.enabled', 'true') \
    .config('spark.worker.cleanup.appDataTtl', '60') \
    .config('spark.sql.debug.maxToStringFields', 100)


spark = configure_spark_with_delta_pip(builder).getOrCreate()

df = spark.read.option("header", False) \
    .option("inferSchema", "true") \
    .option("ignoreLeadingWhiteSpace", "true") \
    .option("ignoreTrailingWhiteSpace", "true") \
    .csv("/mnt/indexer-build/migrated_data/TransactionOps.csv") 

path="/mnt/indexer-build/migrated_data/raw/TransactionOps"
# col=["Id","TargetId","Amount","Entrypoint","Level","Timestamp","SenderId","Counter","BakerFee","StorageFee","AllocationFee",
# "GasLimit","GasUsed","InitiatorId","Nonce","StorageId","TokenTransfers"]

df2 = df.toDF("Id","TargetId","Amount","Entrypoint","Level","Timestamp","SenderId","Counter","BakerFee","StorageFee","AllocationFee",
"GasLimit","GasUsed","InitiatorId","Nonce","StorageId","TokenTransfers")
df2.write.option("header", True).mode('overwrite').csv(path)