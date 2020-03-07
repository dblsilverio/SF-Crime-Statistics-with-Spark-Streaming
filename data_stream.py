import logging
import json
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType
import pyspark.sql.functions as psf


# TODO Create a schema for incoming resources
schema = StructType([
    StructField("crime_id", StringType(), True),
    StructField("original_crime_type_name", StringType(), True),
    StructField("report_date", StringType(), True),
    StructField("call_date", StringType(), True),
    StructField("offense_date", StringType(), True),
    StructField("call_time", StringType(), True),
    StructField("call_date_time", StringType(), True),
    StructField("disposition", StringType(), True),
    StructField("address", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("agency_id", StringType(), True),
    StructField("address_type", StringType(), True),
    StructField("common_location", StringType(), True)
])

def run_spark_job(spark):

    # TODO Create Spark Configuration
    # Create Spark configurations with max offset of 200 per trigger
    # set up correct bootstrap server and port
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "com.udacity.datastreaming.sfcrimes") \
        .option("startingOffsets", "earliest") \
        .option("maxOffsetsPerTrigger", 200) \
        .option("fetchOffset.retryIntervalMs", 10) \
        .option("spark.sql.shuffle.partitions", 200) \
        .option("spark.streaming.stopGracefullyOnShutdown", True) \
        .load()
    # spark.sparkContext.setLogLevel('WARN')

    # Show schema for the incoming resources for checks
    df.printSchema()

    # TODO extract the correct column from the kafka input resources
    # Take only value and convert it to String
    kafka_df = df.selectExpr("CAST(value AS STRING)")

    service_table = kafka_df\
        .select(psf.from_json(psf.col('value'), schema).alias("DF"))\
        .select("DF.*")

    # # TODO select original_crime_type_name and disposition
    distinct_table = service_table \
        .select(
            "original_crime_type_name",
            "disposition",
            psf.to_timestamp(psf.col("call_date_time")).alias("call_date_time"))

    # # count the number of original crime type
    agg_df = distinct_table \
        .select("original_crime_type_name", "disposition", "call_date_time") \
        .withWatermark("call_date_time", "30 minutes") \
        .groupBy(
            psf.window(distinct_table.call_date_time, "15 minutes", "10 minutes"),
            "original_crime_type_name").count()

    # # TODO Q1. Submit a screen shot of a batch ingestion of the aggregation
    # # TODO write output stream
    query = agg_df \
        .writeStream \
        .outputMode("complete") \
        .format("console") \
        .start()


    # # TODO attach a ProgressReporter
    query.awaitTermination()

    # # TODO get the right radio code json path
    radio_code_json_filepath = "data/radio_code.json"
    radio_code_df = spark.read.json(radio_code_json_filepath)

    # # clean up your data so that the column names match on radio_code_df and agg_df
    # # we will want to join on the disposition code

    # # TODO rename disposition_code column to disposition
    radio_code_df = radio_code_df.withColumnRenamed("disposition_code", "disposition")

    # # TODO join on disposition column
    join_query = agg_df.join(radio_code_df, on=['dispostion'])


    join_query.awaitTermination()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # TODO Create Spark in Standalone mode
    spark = SparkSession \
        .builder \
        .master("local[*]") \
        .appName("KafkaSparkStructuredStreaming") \
        .getOrCreate()

    logger.info("Spark started")

    run_spark_job(spark)

    spark.stop()