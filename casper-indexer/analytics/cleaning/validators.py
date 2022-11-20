from util.helper import initalizeSpark,loadJsonFile

usr_validator="/mnt/indexer-build/migrated_data/casper_data/validators.json"
destination_folder="/mnt/indexer-build/migrated_data/casper_data/raw/validators"

spark = initalizeSpark("Cleaning")
df = loadJsonFile(spark, usr_validator)

df.write.option("header", True).mode('overwrite').csv(destination_folder)