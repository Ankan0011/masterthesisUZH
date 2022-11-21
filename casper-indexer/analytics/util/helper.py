
from pyspark.sql import SparkSession
from delta import *
from pyspark.sql.functions import *
from datetime import datetime

def initalizeSpark(AppName):
        print("Importing the Spark Initiallization")
        builder = SparkSession.builder.appName(AppName) \
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
        return spark

#Graph Spark packages
def initalizeGraphSpark(AppName):
        print("Importing the Graph Initialization")
        spark = SparkSession.builder.appName(AppName) \
                .config("spark.driver.extraJavaOptions", "-Xss400M") \
                .config("spark.jars", "//mnt/indexer-build/jar/postgresql-42.5.0.jar") \
                .config("spark.driver.extraClassPath","//mnt/indexer-build/jar/graphframes_graphframes-0.8.1-spark3.0-s_2.12.jar") \
                .config("spark.executor.memory", "8g") \
                .config("spark.executor.cores", "2") \
                .config('spark.cores.max', '4') \
                .config('spark.driver.memory','16g') \
                .config('spark.executor.instances','3') \
                .config('spark.dynamicAllocation.enabled', 'true') \
                .config('spark.dynamicAllocation.shuffleTracking.enabled', 'true') \
                .config('spark.dynamicAllocation.executorIdleTimeout', '60s')\
                .config('spark.dynamicAllocation.minExecutors', '0')\
                .config('spark.dynamicAllocation.maxExecutors', '5')\
                .config('spark.dynamicAllocation.initialExecutors', '1')\
                .config('spark.dynamicAllocation.executorAllocationRatio', '1')\
                .config('spark.worker.cleanup.enabled', 'true') \
                .config('spark.worker.cleanup.interval', '60') \
                .config('spark.shuffle.service.db.enabled', 'true') \
                .config('spark.worker.cleanup.appDataTtl', '60') \
                .config('spark.excludeOnFailure.killExcludedExecutors','true') \
                .config('spark.sql.debug.maxToStringFields', 100).getOrCreate()
        spark.sparkContext.setCheckpointDir(dirName="/mnt/indexer-build/migrated_data/temp")
        # spark.sparkContext.setSystemProperty('logger.File', '/mnt/indexer-build/migrated_data/logs/sample.log')
        # logger = spark._jvm.org.apache.log4j.LogManager.getLogger('default')

        return spark

def loadFile(spark, path, header):
        print("Loading the csv files")
        df = spark.read.option("header", header).option("inferSchema", "true") \
                .option("ignoreLeadingWhiteSpace", "true") \
                .option("ignoreTrailingWhiteSpace", "true") \
                .csv(path+"/*.csv")
        return df

def loadJsonFile(spark, path):
        print("Loading the json files")
        df = spark.read.option("multiline","true") \
                .option("ignoreLeadingWhiteSpace", "true") \
                .option("ignoreTrailingWhiteSpace", "true") \
                .json(path)
        return df

#To Parse the Date timestamp to Date Object
def dateParser(Timestamp):    
    mydate = datetime.strptime(Timestamp, "%Y-%m-%d %H:%M:%S")
    return mydate

#To Parse the Date timestamp to Date Object
def dateMilParser(Timestamp):    
    mydate = datetime.strptime(Timestamp, "%Y-%m-%d %H:%M:%S.%f")
    return mydate