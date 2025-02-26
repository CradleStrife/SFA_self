import os
import requests
import time

EUREKA_SERVER = "http://eureka-server:8761/eureka"
APP_NAME = "elasticsearch"
#CURRENT_HOST = '192.168.10.222' #for remote server
CURRENT_HOST = os.getenv('CURRENT_HOST', 'localhost')  # Get current host from environment variable
INSTANCE_HOST = "elasticsearch"
INSTANCE_PORT = 9200
HEALTH_CHECK_URL = f"http://{INSTANCE_HOST}:{INSTANCE_PORT}/_cluster/health"
INSTANCE_ID = f"{CURRENT_HOST}:{APP_NAME}:{INSTANCE_PORT}"
RENEWAL_INTERVAL = 10  # Interval for checking health in seconds

print('Starting Elasticsearch monitoring script...', flush=True)
print(f'INSTANCE_ID: {INSTANCE_ID}', flush=True)

def update_status_in_eureka(status):
    update_status_url = f"{EUREKA_SERVER}/apps/{APP_NAME}/{INSTANCE_ID}/status?value={status}"
    print(f"Updating status to {status}: {update_status_url}", flush=True)
    try:
        response = requests.put(update_status_url)
        print('Phase2:', response, flush=True)
        if response.status_code != 200:
            print(f"Failed to update status: {response.status_code} {response.text}", flush=True)
    except Exception as e:
        print(f"Error updating status in Eureka: {e}", flush=True)

def main():
    print('Entering main loop...', flush=True)
    while True:
        try:
            response = requests.get(HEALTH_CHECK_URL)
            print('Health check response:', response, flush=True)
            if response.status_code == 200 and response.json().get('status') in ['green', 'yellow']:
                update_status_in_eureka("UP")
            else:
                update_status_in_eureka("DOWN")
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}", flush=True)
            update_status_in_eureka("DOWN")
        
        time.sleep(RENEWAL_INTERVAL)

if __name__ == "__main__":
    print('Calling main...', flush=True)
    main()
