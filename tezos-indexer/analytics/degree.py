
import sys
import os
from delta import *
from pyspark.sql.functions import *
from pyspark.sql.types import StringType
from datetime import datetime

# sys.path.append('/mnt/indexer-build/tezos-indexer/util')

from util.helper import initalizeSpark,loadFile,dateParser


def weekExtractor(Timestamp):
    try:
        return dateParser(Timestamp).isocalendar()[1]
    except ValueError as e:
        print('ValueError Raised:', e)
    return "NULL"

def yearExtractor(Timestamp):
    try:
        return dateParser(Timestamp).year
    except ValueError as e:
        print('ValueError Raised:', e)
    return "NULL"

udf_weekExtractor = udf(lambda x:weekExtractor(x), StringType() )
udf_yearExtractor = udf(lambda x:yearExtractor(x), StringType() )

test_txs_path="/mnt/indexer-build/migrated_data/raw/TransactionOps"
test_acc_path="/mnt/indexer-build/migrated_data/raw/rest_Accounts"
spark = initalizeSpark("Degree")

df_txs = loadFile(spark, test_txs_path, True )
df_Acc = loadFile(spark, test_acc_path, True )

#Dataframe containing all the Users accounts details
df_users=df_Acc.filter(df_Acc['Type'] == 0).alias('df_users')

#Joined the transaction table to extract all the 
df_txs_user =df_txs.alias('df_txs').join(df_users, df_txs.SenderId == df_users.Id, "inner").select('df_txs.*')
df_final = df_txs_user.withColumn("Week_no",udf_weekExtractor(col("Timestamp"))).withColumn("Year_no",udf_yearExtractor(col("Timestamp")))
#df_new.show(5)
#df_final.write.option("header", True).mode('overwrite').csv("/mnt/indexer-build/migrated_data/stage/user_txs")