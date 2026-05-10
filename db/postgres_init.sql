-- Table for Crime Trends (Batch Analytics)
CREATE TABLE IF NOT EXISTS crime_trends (
    year INT,
    month INT,
    day_of_week VARCHAR(20),
    hour INT,
    crime_count INT,
    PRIMARY KEY (year, month, day_of_week, hour)
);

-- Table for Geospatial Hotspots (K-Means Centroids)
CREATE TABLE IF NOT EXISTS hotspots (
    cluster_id INT PRIMARY KEY,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    incident_count INT
);

-- Table for Cross-Dataset Correlations
CREATE TABLE IF NOT EXISTS correlations (
    district VARCHAR(50),
    metric_name VARCHAR(100),
    metric_value DOUBLE PRECISION,
    correlation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for Real-time Alerts (from Storm)
CREATE TABLE IF NOT EXISTS alerts (
    alert_id SERIAL PRIMARY KEY,
    district_id VARCHAR(50),
    crime_count INT,
    threshold INT,
    severity VARCHAR(20),
    alert_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for Arrest Rates
CREATE TABLE IF NOT EXISTS arrest_rates (
    primary_type VARCHAR(100),
    district VARCHAR(50),
    race VARCHAR(50),
    arrest_rate DOUBLE PRECISION,
    total_crimes INT,
    total_arrests INT
);
