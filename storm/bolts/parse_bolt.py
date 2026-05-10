import storm
import json

class ParseBolt(storm.BasicBolt):
    def process(self, tup):
        try:
            line = tup.values[0]
            data = json.loads(line)
            
            # Validation: Ensure mandatory fields exist
            required_fields = ["case_number", "district", "primary_type"]
            if all(field in data and data[field] for field in required_fields):
                # Emit the district and the whole record for downstream processing
                storm.emit([data['district'], json.dumps(data)])
            else:
                storm.log(f"Discarding malformed message: {line}")
        except Exception as e:
            storm.log(f"Error in ParseBolt: {e}")

if __name__ == "__main__":
    ParseBolt().run()
