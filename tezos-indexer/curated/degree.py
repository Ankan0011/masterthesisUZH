from delta import *
from pyspark.sql.functions import *

from util.helper import initalizeSpark,loadFile

user_txs_path="/mnt/indexer-build/migrated_data/stage/user_txs"
distination_path="/mnt/indexer-build/migrated_data/curated/weekly_degree"

spark = initalizeSpark("Degree")

df_txs = loadFile(spark, user_txs_path, True )

df_agg = df_txs.groupBy("Year_no","Week_no","SenderId").agg(countDistinct("TargetId").alias("TargetCount"),sum("Amount").alias("Sum_Amount"))

df_agg.write.option("header", True).mode('overwrite').csv(distination_path)