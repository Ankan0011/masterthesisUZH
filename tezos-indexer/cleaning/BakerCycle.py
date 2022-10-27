from pyspark.sql import SparkSession
from delta import *
from pyspark.sql.functions import *

builder = SparkSession.builder.appName("BakerCycle") \
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

df = spark.read.option("header", True) \
    .option("inferSchema", "true") \
    .option("ignoreLeadingWhiteSpace", "true") \
    .option("ignoreTrailingWhiteSpace", "true") \
    .csv("/mnt/indexer-build/migrated_data/BakerCycles.csv") 

path="/mnt/indexer-build/migrated_data/raw/BakerCycle"
col = ["Id", "Cycle", "BakerId", "DelegatorsCount","DelegatedBalance","StakingBalance","ActiveStake","SelectedStake","Blocks",
"Endorsements","BlockRewards","EndorsementRewards","BlockFees","DoubleBakingRewards","DoubleEndorsingRewards","DoublePreendorsingRewards",
"RevelationRewards","ExpectedBlocks"]

df2 = df.select(*col)
df2.write.option("header", True).mode('overwrite').csv(path)
