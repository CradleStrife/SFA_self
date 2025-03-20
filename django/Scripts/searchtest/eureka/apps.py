import py_eureka_client.eureka_client as eureka_client
from django.apps import AppConfig
from django.conf import settings


class EurekaConfig(AppConfig):
    name = 'eureka'

    def ready(self):
            try:
                # Initialize the Eureka client
                eureka_client.init(
                    eureka_server=settings.EUREKA['server'],
                    app_name=settings.EUREKA['app_name'],
                    instance_host=settings.EUREKA['instance_host'],
                    instance_port=settings.EUREKA['instance_port']
                )
            except Exception as e:
                # print('Could not initialize Eureka client:', e)
                return

    #         instance_id = f"{settings.EUREKA['instance_host']}:{settings.EUREKA['app_name']}:{settings.EUREKA['instance_port']}"
    #         # print(f"Instance ID: {instance_id}")
    #         while True:
    #             try:
    #                 # Check the health of the Django application
    #                 health_url = f"http://{settings.EUREKA['instance_host']}:{settings.EUREKA['instance_port']}/health/"
    #                 health_response = requests.get(health_url)
    #                 status = 'UP' if health_response.status_code == 200 else 'DOWN'

    #                 # Use HTTP requests to update the status with Eureka
    #                 update_status_url = f"{settings.EUREKA['server']}/apps/{settings.EUREKA['app_name']}/{instance_id}/status?value={status}"
    #                 # print(update_status_url)
    #                 response = requests.put(update_status_url)
    #                 # print(response)
    #                 if response.status_code != 200:
    #                     # print(f"Failed to update status: {response.status_code} {response.text}")
    #             except Exception as e:
    #                 # print('Could not update status with Eureka:', e)

    #             # Heartbeat every 30 seconds
    #             time.sleep(15)

    #     thread = threading.Thread(target=register_with_eureka)
    #     thread.daemon = True
    #     thread.start()
