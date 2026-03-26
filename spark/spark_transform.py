"""
Optional Spark implementation of the core transformation.

This mirrors the Python ETL logic and demonstrates how the same pipeline could
scale to larger datasets on Spark/EMR.
"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("OpsInsightAI")
    .getOrCreate()
)

df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("data/raw/orders.csv")
)

transformed = (
    df
    .withColumn("order_ts", F.to_timestamp("order_ts"))
    .withColumn("quantity", F.col("quantity").cast("int"))
    .withColumn("unit_price", F.col("unit_price").cast("double"))
    .withColumn("processing_minutes", F.col("processing_minutes").cast("int"))
    .withColumn("revenue", F.round(F.col("quantity") * F.col("unit_price"), 2))
    .withColumn("status", F.upper(F.trim(F.col("status"))))
    .withColumn("region", F.trim(F.coalesce(F.col("region"), F.lit(""))))
)

(
    transformed
    .dropDuplicates(["order_id"])
    .write
    .mode("overwrite")
    .parquet("data/processed/orders_spark")
)

spark.stop()
