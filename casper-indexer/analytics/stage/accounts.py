from util.helper import initalizeSpark,dateParser,loadFile
from pyspark.sql.functions import *
from pyspark.sql.types import StringType

user_txs="/mnt/indexer-build/migrated_data/casper_data/stage/transactions"
distination_path="/mnt/indexer-build/migrated_data/casper_data/stage/accounts_user"
distination_path2="/mnt/indexer-build/migrated_data/casper_data/stage/delegators"
distination_path3="/mnt/indexer-build/migrated_data/casper_data/stage/all_accounts"

spark = initalizeSpark("stage")
df_txs = loadFile(spark, user_txs, True )

df_to = df_txs.select("to").withColumnRenamed("to", "account").distinct()
df_from = df_txs.select("from").withColumnRenamed("from", "account").distinct()
df = df_to.unionByName(df_from, allowMissingColumns=True)
df.show(5)
print(df.count())