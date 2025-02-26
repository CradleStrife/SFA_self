import os
import time
import requests
import py_eureka_client.eureka_client as eureka_client
#internal docker network communication = http://eureka-server:8761/eureka/
EUREKA_SERVER = "http://eureka-server:8761/eureka/"
Server = os.getenv('Server', "http://eureka-server:8761/" )
APP_NAME = "elasticsearch"
CURRENT_HOST = os.getenv('CURRENT_HOST', 'elasticsearch')
INSTANCE_PORT = 9200

def is_eureka_server_up():
    try:
        response = requests.get(Server)
        print(response)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

print("Initializing Eureka client for Elasticsearch...", flush=True)

# Wait for Eureka server to be available
while not is_eureka_server_up():
    print("Waiting for Eureka server to be up...", flush=True)
    time.sleep(5)

try:
    # Initialize the Eureka client
    eureka_client.init(
        eureka_server=EUREKA_SERVER,
        app_name=APP_NAME,
        instance_host=CURRENT_HOST,
        instance_port=INSTANCE_PORT,
        renewal_interval_in_secs=10,  # Heartbeat interval
        instance_id=f"{CURRENT_HOST}:{APP_NAME}:{INSTANCE_PORT}"
    )
    print("Eureka client initialized and Elasticsearch registered.", flush=True)
except Exception as e:
    print(f"Could not initialize Eureka client: {e}", flush=True)
