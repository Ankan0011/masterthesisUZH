from pyspark.sql.functions import *
from pyspark.sql.window import Window
from pyspark.sql.types import IntegerType
import os

from util.helper import initalizeGraphSpark,loadFile

miner_dist="/mnt/indexer-build/migrated_data/stage/miner_dist_updated/*"
miner_dist_nodes="/mnt/indexer-build/migrated_data/stage/miners_dist_node/*"
destination_path="/mnt/indexer-build/migrated_data/curated/miner_dist"

listDesDir =[x[0].split("/")[-1] for x in os.walk(destination_path)]
listSrcDir  = [x[0] for x in os.walk(miner_dist)]
listSrcDirNode  = [x[0] for x in os.walk(miner_dist_nodes)]

spark = initalizeGraphSpark("Mining")

df_dist = loadFile(spark, miner_dist, True )
df_balance = loadFile(spark, miner_dist_nodes, True )

df_users = df_dist.filter(df_dist['distances'] != 'NULL')
# print("User_df_count :"+str(df_users.count()))

df_balance_clean = df_balance.withColumn("node", df_balance["node"].cast(IntegerType()))

w = Window().partitionBy('year_week')

df_norm = df_balance_clean \
        .withColumn('min_balance',min(col('balance')).over(w)) \
        .withColumn('max_balance',max(col('balance')).over(w)) \
        .withColumn('norm_balance',((col('balance')-col('min_balance'))/(col('max_balance')-col('min_balance')))) \
        .drop('min_balance','max_balance')


df_merged = df_users.join(df_norm, (df_users.year_week == df_norm.year_week) & (df_users.id == df_norm.node)) \
                .select(df_users["*"],df_norm["norm_balance"])
df_merged.groupBy("year_week","distances").agg(avg("norm_balance").alias("norm_balance")).orderBy("year_week")
df_merged.write.option("header", True).mode('overwrite').csv(destination_path)

# df_merged.groupBy("distances").agg(avg("norm_balance").alias("norm_balance")).show(10)