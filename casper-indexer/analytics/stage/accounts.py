from util.helper import initalizeSpark,loadFile
from pyspark.sql.functions import *

user_txs="/mnt/indexer-build/migrated_data/casper_data/stage/transactions"
validators="/mnt/indexer-build/migrated_data/casper_data/raw/validators" 
distination_path="/mnt/indexer-build/migrated_data/casper_data/stage/accounts_user"
distination_path2="/mnt/indexer-build/migrated_data/casper_data/stage/validators"
distination_path3="/mnt/indexer-build/migrated_data/casper_data/stage/all_accounts"

spark = initalizeSpark("stage")
df_txs = loadFile(spark, user_txs, True )
df_validator = loadFile(spark,validators , True).select("public_key")
df_validator.write.option("header", True).mode('overwrite').csv(distination_path2)

df_to = df_txs.select("to").withColumnRenamed("to", "account")
df_from = df_txs.select("from").withColumnRenamed("from", "account")
df = df_to.unionByName(df_from, allowMissingColumns=True).distinct()
df.write.option("header", True).mode('overwrite').csv(distination_path3)

df_non_val = df.subtract(df_validator)
df_non_val.write.option("header", True).mode('overwrite').csv(distination_path)