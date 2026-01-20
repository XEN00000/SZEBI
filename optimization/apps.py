import os
from django.apps import AppConfig

class OptimizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'optimization'

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return
        
        # Import w środku, żeby uniknąć side-effectów przy manage.py/migrations
        from optimization.integration.mqtt.device_listener import DeviceStateListener

        listener = DeviceStateListener(
            mqtt_host="mqtt",
            mqtt_port=1883,
            topic=os.getenv("SIM_DEVICE_STATE_TOPIC", "szebi/device/state/#"),
        )
        listener.start()