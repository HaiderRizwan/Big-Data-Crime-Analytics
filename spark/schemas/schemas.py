from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType, TimestampType

# 1. Crime Data Schema
crime_schema = StructType([
    StructField("id", StringType(), True),
    StructField("case_number", StringType(), True),
    StructField("date", TimestampType(), True),
    StructField("block", StringType(), True),
    StructField("iucr", StringType(), True),
    StructField("primary_type", StringType(), True),
    StructField("description", StringType(), True),
    StructField("location_description", StringType(), True),
    StructField("arrest", BooleanType(), True),
    StructField("domestic", BooleanType(), True),
    StructField("beat", StringType(), True),
    StructField("district", StringType(), True),
    StructField("ward", StringType(), True),
    StructField("community_area", StringType(), True),
    StructField("fbi_code", StringType(), True),
    StructField("x_coordinate", DoubleType(), True),
    StructField("y_coordinate", DoubleType(), True),
    StructField("year", IntegerType(), True),
    StructField("updated_on", TimestampType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("location", StringType(), True)
])

# 2. Police Stations Schema
police_stations_schema = StructType([
    StructField("district", StringType(), True),
    StructField("district_name", StringType(), True),
    StructField("address", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("zip", StringType(), True),
    StructField("website", StringType(), True),
    StructField("phone", StringType(), True),
    StructField("fax", StringType(), True),
    StructField("tty", StringType(), True),
    StructField("x_coordinate", DoubleType(), True),
    StructField("y_coordinate", DoubleType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("location", StringType(), True)
])

# 3. Arrests Schema
arrests_schema = StructType([
    StructField("cb_no", StringType(), True),
    StructField("case_number", StringType(), True),
    StructField("arrest_date", TimestampType(), True),
    StructField("race", StringType(), True),
    StructField("charge_1_statute", StringType(), True),
    StructField("charge_1_description", StringType(), True),
    StructField("charge_1_type", StringType(), True),
    StructField("charge_1_class", StringType(), True),
    StructField("charge_2_statute", StringType(), True),
    StructField("charge_2_description", StringType(), True),
    StructField("charge_2_type", StringType(), True),
    StructField("charge_2_class", StringType(), True),
    StructField("charge_3_statute", StringType(), True),
    StructField("charge_3_description", StringType(), True),
    StructField("charge_3_type", StringType(), True),
    StructField("charge_3_class", StringType(), True),
    StructField("charge_4_statute", StringType(), True),
    StructField("charge_4_description", StringType(), True),
    StructField("charge_4_type", StringType(), True),
    StructField("charge_4_class", StringType(), True),
    StructField("charges_statute", StringType(), True),
    StructField("charges_description", StringType(), True),
    StructField("charges_type", StringType(), True),
    StructField("charges_class", StringType(), True)
])

# 4. Violence Reduction Schema
violence_schema = StructType([
    StructField("case_number", StringType(), True),
    StructField("date", TimestampType(), True),
    StructField("block", StringType(), True),
    StructField("victimization_primary", StringType(), True),
    StructField("incident_primary", StringType(), True),
    StructField("gunshot_injury_i", StringType(), True),
    StructField("unique_id", StringType(), True),
    StructField("zip_code", StringType(), True),
    StructField("ward", StringType(), True),
    StructField("community_area", StringType(), True),
    StructField("street_outreach_organization", StringType(), True),
    StructField("area", StringType(), True),
    StructField("district", StringType(), True),
    StructField("beat", StringType(), True),
    StructField("age", StringType(), True),
    StructField("sex", StringType(), True),
    StructField("race", StringType(), True),
    StructField("victimization_fbi_cd", StringType(), True),
    StructField("incident_fbi_cd", StringType(), True),
    StructField("victimization_fbi_descr", StringType(), True),
    StructField("incident_fbi_descr", StringType(), True),
    StructField("victimization_iucr_cd", StringType(), True),
    StructField("incident_iucr_cd", StringType(), True),
    StructField("victimization_iucr_secondary", StringType(), True),
    StructField("incident_iucr_secondary", StringType(), True),
    StructField("homicide_victim_first_name", StringType(), True),
    StructField("homicide_victim_mi", StringType(), True),
    StructField("homicide_victim_last_name", StringType(), True),
    StructField("month", IntegerType(), True),
    StructField("day_of_week", IntegerType(), True),
    StructField("hour", IntegerType(), True),
    StructField("location_description", StringType(), True),
    StructField("state_house_district", StringType(), True),
    StructField("state_senate_district", StringType(), True),
    StructField("updated", TimestampType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("location", StringType(), True)
])

# 5. Sex Offenders Schema
sex_offenders_schema = StructType([
    StructField("last", StringType(), True),
    StructField("first", StringType(), True),
    StructField("block", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("race", StringType(), True),
    StructField("birth_date", StringType(), True), # Often MM/DD/YYYY, convert later
    StructField("height", StringType(), True),
    StructField("weight", IntegerType(), True),
    StructField("victim_minor", StringType(), True)
])
