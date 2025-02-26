import requests
import time
import os

EUREKA_SERVER = "http://eureka-server:8761/eureka"
APP_NAME = "django"
INSTANCE_HOST = "django"
#Current_host = '192.168.10.222' #for remote server
Current_host = os.getenv('CURRENT_HOST', 'localhost') # local
INSTANCE_PORT = 8000
HEALTH_CHECK_URL = f"http://{INSTANCE_HOST}:{INSTANCE_PORT}/health/"
INSTANCE_ID = f"{Current_host}:{APP_NAME}:{INSTANCE_PORT}"
RENEWAL_INTERVAL = 10  # Interval for checking health in seconds
print('starting.............')
print("url:",HEALTH_CHECK_URL)
def update_status_in_eureka(status):
    update_status_url = f"{EUREKA_SERVER}/apps/{APP_NAME}/{INSTANCE_ID}/status?value={status}"
    print('here:',update_status_url)
    try:
        response = requests.put(update_status_url)
        print('phase2:', response)
        if response.status_code != 200:
            print(f"Failed to update status: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error updating status in Eureka: {e}")

def main():
    print('Entering main loop...')
    while True:
        print('Looping.......')
        try:
            
            response = requests.get(HEALTH_CHECK_URL)
            print('Health check response:', response)
            if response.status_code == 200:
                update_status_in_eureka("UP")
            else:
                update_status_in_eureka("DOWN")
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            update_status_in_eureka("DOWN")
        
        time.sleep(RENEWAL_INTERVAL)

if __name__ == "__main__":
    main()
