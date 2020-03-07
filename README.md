# Data Streaming ND

## SF Crime Statistics with Spark Streaming

This project was developed in fulfillment of Data Streaming Nanodegree - Apache Spark and Spark Streaming module.

## Requirements

* Spark 2.4.3
* Scala 2.11.x
* Java 1.8.x
* Kafka build with Scala 2.11.x
* Python 3.6.x or 3.7.x

## Questions

### 1. *How did changing values on the SparkSession property parameters affect the throughput and latency of the data?*

While testing locally some values for *maxOffsetsPerTrigger* and *fetchOffset.retryIntervalMs*, it was clear that a bigger offset and slightly smaller interval could handle more rows processed per second with little effort, according to Streaming query progress log.
Balancing these properties according to hardware constraints might lead to better results easily.

### 2. *What were the 2-3 most efficient SparkSession property key/value pairs? Through testing multiple variations on values, how can you tell these were the most optimal?*

Tested these properties:
* **maxOffsetsPerTrigger** - *Rate limit on maximum number of offsets processed per trigger interval.*
* **spark.sql.shuffle.partitions** - *Configures the number of partitions to use when shuffling data for joins or aggregations.*
* **spark.driver.cores** - Number of cores to use for the driver process.

*Changing values for *spark.driver.cores* did not seen to make effect locally.*

Some results:

* **#1** *maxOffsetsPerTrigger=200* AND *spark.sql.shuffle.partitions=200* - Processed 75 rows per second
* **#2** *maxOffsetsPerTrigger=200* AND *spark.sql.shuffle.partitions=400* - Processed 108 rows per second
* **#3** *maxOffsetsPerTrigger=400* AND *spark.sql.shuffle.partitions=400* - Processed 139 rows per second

Test #3 almost doubled the performance from test #1, and outperformed well test #2. Some variation occured throughout the tests, but in a consistent way, such as test config #1 never outperformed the others configs.

## Extras
Sample [screenshots](screenshots.zip) showing streaming logs are compressed.