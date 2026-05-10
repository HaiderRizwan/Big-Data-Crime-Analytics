import os
import yaml
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count as spark_count
from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import VectorAssembler
from spark.schemas.schemas import crime_schema

# Load configuration
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

def main():
    spark = SparkSession.builder \
        .appName("CrimeHotspotDetection") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.1") \
        .getOrCreate()

    # 1. Load Data
    print("Loading crime data for clustering...")
    df = spark.read.csv("data/crime_data.csv", schema=crime_schema, header=True)

    # 2. Preprocessing
    # Filter out records without coordinates
    df_clean = df.select("latitude", "longitude").dropna()

    # Assemble features into a single vector column
    assembler = VectorAssembler(inputCols=["latitude", "longitude"], outputCol="features")
    data_vec = assembler.transform(df_clean)

    # 3. Train K-Means Model
    print("Training K-Means model (k=10)...")
    kmeans = KMeans(k=10, seed=42)
    model = kmeans.fit(data_vec)

    # 4. Centroids + incident counts per cluster (for map bubble size / DB schema)
    centers = model.clusterCenters()
    predicted = model.transform(data_vec)
    counts_df = predicted.groupBy("prediction").agg(
        spark_count("*").alias("incident_count")
    )

    centroids_data = []
    for i, center in enumerate(centers):
        centroids_data.append((i, float(center[0]), float(center[1])))

    centroids_df = spark.createDataFrame(centroids_data, ["cluster_id", "latitude", "longitude"])
    hotspots_df = (
        centroids_df.join(
            counts_df,
            col("cluster_id") == col("prediction"),
            "left",
        )
        .drop("prediction")
        .fillna(0, subset=["incident_count"])
    )

    # 5. Save to PostgreSQL
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

    print(f"Saving hotspots to PostgreSQL at {jdbc_url}...")
    hotspots_df.write.jdbc(url=jdbc_url, table="hotspots", mode="overwrite", properties=db_properties)

    print("Hotspot detection complete!")
    spark.stop()

if __name__ == "__main__":
    main()
