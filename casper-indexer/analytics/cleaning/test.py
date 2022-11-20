from util.helper import initalizeSpark,loadFile
import math
from pyspark.sql.functions import *
from pyspark.sql.types import StringType
from pyspark.sql.functions import col,min,max

#baking_cycle_path="/mnt/indexer-build/migrated_data/raw/mining_Cycle"
usr_txs_path="/mnt/indexer-build/migrated_data/casper_data/Delegators.txt"
spark = initalizeSpark("Cleaning")
col =["Level","Timestamp"]

df_cycle = loadFile(spark, usr_txs_path, True )
#df1 = df_cycle.filter(df_cycle['from'] == '013725fe8df379be1e1cc8c571fc4d21b584dc8bb126000c7ab70db1ed4fb9d751')
df_cycle.select(countDistinct("validator")).show()
# df_cycle.show(5)