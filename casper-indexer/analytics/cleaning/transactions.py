from util.helper import initalizeSpark,loadFile

usr_transfers="/mnt/indexer-build/migrated_data/casper_data/Transfer.txt"
destination_folder="/mnt/indexer-build/migrated_data/casper_data/raw/transactions"

spark = initalizeSpark("Cleaning")
df = loadFile(spark, usr_transfers, True)
df.write.option("header", True).mode('overwrite').csv(destination_folder)