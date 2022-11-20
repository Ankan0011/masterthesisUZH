from pyspark.sql.functions import lit
from util.helper import initalizeGraphSpark,loadFile
from graphframes import *
import os
import networkx as nx

# Paths
test_txs_path="/mnt/indexer-build/migrated_data/stage/SSC"
# test_txs_path="/mnt/indexer-build/migrated_data/raw/test_txs-1"
accounts_path="/mnt/indexer-build/migrated_data/raw/rest_Accounts"
destination_path="/mnt/indexer-build/migrated_data/curated/SSC"

# Variables
spark = initalizeGraphSpark("Debug")
v1_cols=["Id","Balance"]
e1_cols=["SenderId","TargetId","Year_no","Week_no"]
e1_final=["src","dst","relationship"]
final_columns = ["max_count","time_week","Total_Vertices"]