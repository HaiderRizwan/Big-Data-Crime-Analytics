import os
import yaml
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, hour, date_format, count, when, avg
from spark.schemas.schemas import crime_schema, police_stations_schema, arrests_schema, violence_schema, sex_offenders_schema

# Load configuration
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

def create_spark_session():
    return SparkSession.builder \
        .appName(config['spark']['app_name']) \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.1") \
        .getOrCreate()

def main():
    spark = create_spark_session()
    
    # 1. Ingest Datasets
    print("Ingesting datasets...")
    crimes_df = spark.read.csv("data/crime_data.csv", schema=crime_schema, header=True)
    stations_df = spark.read.csv("data/police_stations.csv", schema=police_stations_schema, header=True)
    arrests_df = spark.read.csv("data/arrests.csv", schema=arrests_schema, header=True)
    violence_df = spark.read.csv("data/violence_reduction.csv", schema=violence_schema, header=True)
    sex_offenders_df = spark.read.csv("data/sex_offenders.csv", schema=sex_offenders_schema, header=True)

    # 2. Data Cleaning
    # Drop rows with critical nulls and handle basic cleaning
    crimes_df = crimes_df.dropna(subset=["id", "case_number", "date", "district"])
    
    # 3. Compute Crime Trends
    print("Computing crime trends...")
    trends_df = crimes_df.select(
        year("date").alias("year"),
        month("date").alias("month"),
        date_format("date", "EEEE").alias("day_of_week"),
        hour("date").alias("hour")
    ).groupBy("year", "month", "day_of_week", "hour").count().withColumnRenamed("count", "crime_count")

    # 4. Join Crimes and Arrests
    print("Joining Crimes and Arrests...")
    crime_arrest_join = crimes_df.join(arrests_df, "case_number", "inner")

    # 5. Compute Arrest Rates
    print("Computing arrest rates...")
    arrest_rates_df = crimes_df.groupBy("primary_type", "district") \
        .agg(
            count("*").alias("total_crimes"),
            count(when(col("arrest") == True, True)).alias("total_arrests")
        ) \
        .withColumn("arrest_rate", col("total_arrests") / col("total_crimes"))

    # 6. Violence and Gunshot Analysis
    print("Computing violence metrics...")
    violence_metrics = violence_df.groupBy("district").agg(
        count(when(col("victimization_primary") == "HOMICIDE", True)).alias("homicides"),
        count(when(col("gunshot_injury_i") == "YES", True)).alias("gunshot_incidents")
    )

    # 7. Sex Offender Proximity Analysis
    print("Analyzing Sex Offenders...")
    offender_district_count = sex_offenders_df.groupBy("block").count() # Placeholder for proximity

    # 8. Cross-Dataset Correlation: Violence vs Arrest Rate
    print("Computing correlations...")
    correlation_df = violence_metrics.join(arrest_rates_df, "district", "inner") \
        .select("district", "arrest_rate", "homicides")

    # 9. Serving Layer - Write to PostgreSQL
    db_config = config['databases']['postgres']
    
    # Prioritize Env Vars (Docker)
    db_host = os.environ.get('POSTGRES_HOST', db_config['host'])
    db_port = os.environ.get('POSTGRES_PORT', db_config['port'])
    db_name = os.environ.get('POSTGRES_DB', db_config['dbname'])
    db_user = os.environ.get('POSTGRES_USER', db_config['user'])
    db_pass = os.environ.get('POSTGRES_PASSWORD', db_config['password'])

    jdbc_url = f"jdbc:postgresql://{db_host}:{db_port}/{db_name}"
    db_properties = {
        "user": db_user,
        "password": db_pass,
        "driver": "org.postgresql.Driver"
    }

    print(f"Writing results to PostgreSQL at {jdbc_url}...")
    trends_df.write.jdbc(url=jdbc_url, table="crime_trends", mode="overwrite", properties=db_properties)
    arrest_rates_df.write.jdbc(url=jdbc_url, table="arrest_rates", mode="overwrite", properties=db_properties)
    correlation_df.write.jdbc(url=jdbc_url, table="correlations", mode="overwrite", properties=db_properties)

    print("Batch analytics complete!")
    spark.stop()

if __name__ == "__main__":
    main()
