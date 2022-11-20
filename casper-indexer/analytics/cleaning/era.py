from util.helper import initalizeSpark,loadFile

usr_era="/mnt/indexer-build/migrated_data/casper_data/Era.txt"
destination_folder="/mnt/indexer-build/migrated_data/casper_data/raw/era"

spark = initalizeSpark("Cleaning")
df = loadFile(spark, usr_era, True)
df.write.option("header", True).mode('overwrite').csv(destination_folder)