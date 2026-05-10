import storm
import yaml
import time
from collections import defaultdict, deque

class WindowAnomalyBolt(storm.BasicBolt):
    def initialize(self, conf, context):
        import os
        with open("config/config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
        
        # Memory to store (timestamp, district)
        # Use env vars from docker-compose if available, otherwise fallback to config.yaml
        self.window_size = int(os.environ.get('WINDOW_SIZE_SECONDS', self.config['storm']['window_size_minutes'] * 60))
        self.threshold = int(os.environ.get('ANOMALY_THRESHOLD', self.config['storm']['anomaly_threshold']))
        self.crime_history = defaultdict(deque)

    def process(self, tup):
        district = tup.values[0]
        current_time = time.time()
        
        # Add current event to history
        self.crime_history[district].append(current_time)
        
        # Slide the window: remove events older than window_size
        while self.crime_history[district] and self.crime_history[district][0] < (current_time - self.window_size):
            self.crime_history[district].popleft()
            
        # Check for anomaly
        current_count = len(self.crime_history[district])
        if current_count >= self.threshold:
            # Emit anomaly: [district, count, threshold, timestamp]
            storm.emit([district, current_count, self.threshold, int(current_time)])
            storm.log(f"ANOMALY DETECTED: District {district} has {current_count} crimes!")

if __name__ == "__main__":
    WindowAnomalyBolt().run()
