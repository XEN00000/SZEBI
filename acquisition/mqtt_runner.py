import threading
import time
import traceback

# Importy dopasowane do Twojej struktury folderów
from .logic.MQTT_manager import MQTTManager
from .logic.database_manager import DatabaseManager
from .data_logic.handle_data import HandleData
from .data_logic.validator import Validator
from .data_logic.deduplicator import Deduplicator
from .data_logic.transformer import Transformer
from .models import DataLog, DataLogLevel

_worker_thread = None
_stop_event = threading.Event()

def is_running():
    return _worker_thread is not None and _worker_thread.is_alive()

def start_mqtt_worker():
    global _worker_thread, _stop_event
    
    if is_running():
        return "Akwizycja już działa!"

    print("SYSTEM: Uruchamianie Workera MQTT...")
    _stop_event.clear()
    
    _worker_thread = threading.Thread(target=_acquisition_loop, daemon=True)
    _worker_thread.start()
    return "Uruchomiono proces akwizycji."

def stop_mqtt_worker():
    global _stop_event
    if not is_running():
        return "Akwizycja nie jest uruchomiona."
    
    print("SYSTEM: Zatrzymywanie Workera MQTT...")
    _stop_event.set() 
    return "Wysłano sygnał zatrzymania."

def _acquisition_loop():
    """
    Główna pętla logiczna
    """
    try:
        # 1. Inicjalizacja komponentów
        db_manager = DatabaseManager()
        validator = Validator()
        deduplicator = Deduplicator()
        transformer = Transformer()

        data_handler = HandleData(
            db_manager=db_manager,
            validator=validator,
            deduplicator=deduplicator,
            transformer=transformer
        )

        # 2. Konfiguracja MQTT
        mqtt_manager = MQTTManager(
            broker_url="localhost:1883",
            topics=["environment/#"]
        )
        
        # 3. Połączenie
        if not mqtt_manager.connect():
            print("WORKER ERROR: Nie udało się połączyć z MQTT.")
            return

        print("WORKER: Połączono. Rozpoczynam nasłuchiwanie.")

        # 4. Pętla pracy
        while not _stop_event.is_set():
            if mqtt_manager.get_connection_status():
                raw_messages = mqtt_manager.receive()

                if raw_messages:
                    for message in raw_messages:
                        data_handler.process(message)

            for _ in range(10):
                if _stop_event.is_set(): break
                time.sleep(0.1)

        print("WORKER: Zatrzymano pętlę bezpiecznie.")

    except Exception as e:
        error_msg = f"KRYTYCZNY BŁĄD WORKER: {e}"
        print(error_msg)
        print(traceback.format_exc())
        
        try:
            DatabaseManager().insert_data_log(DataLog(
                level=DataLogLevel.CRITICAL,
                message=error_msg[:255]
            ))
        except:
            pass