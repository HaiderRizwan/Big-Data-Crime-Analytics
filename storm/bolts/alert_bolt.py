import storm
import yaml
import psycopg2
from pymongo import MongoClient

class AlertBolt(storm.BasicBolt):
    def initialize(self, conf, context):
        import os
        with open("config/config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
            
        # Database credentials
        pg_cfg = self.config['databases']['postgres']
        mg_cfg = self.config['databases']['mongodb']

        # Prioritize Environment Variables (Docker) over Config File (Local)
        pg_host = os.environ.get('POSTGRES_HOST', pg_cfg['host'])
        pg_port = os.environ.get('POSTGRES_PORT', pg_cfg['port'])
        pg_user = os.environ.get('POSTGRES_USER', pg_cfg['user'])
        pg_pass = os.environ.get('POSTGRES_PASSWORD', pg_cfg['password'])
        pg_db = os.environ.get('POSTGRES_DB', pg_cfg['dbname'])

        mg_host = os.environ.get('MONGO_HOST', mg_cfg['host'])
        mg_port = os.environ.get('MONGO_PORT', mg_cfg['port'])
        mg_db = os.environ.get('MONGO_DB', mg_cfg['dbname'])
        mg_col = mg_cfg['collection']

        # Connect to PostgreSQL
        self.pg_conn = psycopg2.connect(
            host=pg_host, port=pg_port, 
            user=pg_user, password=pg_pass, dbname=pg_db
        )
        self.pg_cur = self.pg_conn.cursor()
        
        # Connect to MongoDB
        self.mg_client = MongoClient(f"mongodb://{mg_host}:{mg_port}/")
        self.mg_db = self.mg_client[mg_db]
        self.mg_col = self.mg_db[mg_col]

    def process(self, tup):
        district, count, threshold, timestamp = tup.values
        
        # 1. Save to PostgreSQL
        try:
            self.pg_cur.execute(
                "INSERT INTO alerts (district_id, crime_count, threshold, severity) VALUES (%s, %s, %s, %s)",
                (district, count, threshold, "HIGH")
            )
            self.pg_conn.commit()
        except Exception as e:
            storm.log(f"Postgres Error: {e}")
            self.pg_conn.rollback()

        # 2. Save to MongoDB
        try:
            alert_doc = {
                "district": district,
                "count": count,
                "threshold": threshold,
                "timestamp": timestamp,
                "severity": "CRITICAL"
            }
            self.mg_col.insert_one(alert_doc)
        except Exception as e:
            storm.log(f"MongoDB Error: {e}")

if __name__ == "__main__":
    AlertBolt().run()
