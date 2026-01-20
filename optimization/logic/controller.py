from optimization.integration.repositories import DeviceRepository, RuleRepository, UserPreferenceRepository
from optimization.integration.clients import SimulationClient
from optimization.logic.algorithm import calculate_optimal_settings
from optimization.integration.forecasting_repository import ForecastingRepository

class OptimizationController:
    """
    Główny kontroler logiki biznesowej
    Zarządza przepływem danych między repozytoriami, algorytmem a światem zewnętrznym.
    """
    def __init__(self):
        # Wstrzykiwanie zależności (Repositories & Clients)
        self.device_repo = DeviceRepository()
        self.rule_repo = RuleRepository()
        self.pref_repo = UserPreferenceRepository()
        
        self.simulation_client = SimulationClient()

    def receive_alarm(self, alarm_data):
        """
        Obsługa payloadu z modułu Alarmów (ExternalAlarmSerializer).
        Metoda działa jako ADAPTER - tłumaczy format zewnętrzny na wewnętrzne akcje.
        """
        print(f"\n[CONTROLLER] !!! OTRZYMANO ALARM ZEWNĘTRZNY !!!")
        
        # 1. Pobieramy dane z pól specyficznych dla modułu Alarmów
        priority = alarm_data.get('priority')          # Np. 'CRITICAL'
        metric = alarm_data.get('rule_metric')         # Np. 'temp_sensor_1'
        value = alarm_data.get('triggering_value')     # Np. 99.9
        
        print(f"Priorytet: {priority} | Metryka: {metric} | Wartość: {value}")

        if priority == 'CRITICAL':
            print(f"[CONTROLLER] -> ALARM KRYTYCZNY! Analizuję cel...")
            
            # 2. Logika dopasowania urządzenia (Adapter logic)
            # W idealnym świecie szukalibyśmy urządzenia po 'metric', 
            # ale tutaj dla demonstracji zakładamy, że dotyczy to urządzenia ID=1.
            target_device_id = 1 
            
            print(f"[CONTROLLER] -> Wysyłam Emergency Shutdown dla ID={target_device_id}")
            
            # 3. Wysłanie komendy wyłączenia do Symulacji
            self.simulation_client.publish_command(target_device_id, {
                "status": "OFF", 
                "reason": "EXTERNAL_ALARM_CRITICAL",
                "details": f"Metric: {metric}, Value: {value}"
            })
            
        else:
            print("[CONTROLLER] -> Alarm niekrytyczny (INFO/WARNING). Loguję i ignoruję.")

    def _normalize_forecast(self, latest_forecast):
        """
        Normalizuje wynik ForecastingService.get_latest_forecast() do formatu dla algorytmu.

        Forecasting zwraca dict:
          {
            "consumption": [float, ...],
            "production": [float, ...]
          }

        Tworzymy też:
          - net: consumption - production
        """
        raw = latest_forecast or {}

        def _to_float_list(x):
            if not isinstance(x, list):
                return []
            out = []
            for v in x:
                try:
                    out.append(float(v))
                except (TypeError, ValueError):
                    out.append(0.0)
            return out

        consumption = _to_float_list(raw.get("consumption"))
        production = _to_float_list(raw.get("production"))

        # jeśli długości różne, przytnij do krótszej
        n = min(len(consumption), len(production))
        consumption = consumption[:n]
        production = production[:n]

        net = [c - p for c, p in zip(consumption, production)]

        return {
            "consumption": consumption,
            "production": production,
            "net": net,
            "horizon_len": n,
            "_raw": raw,
        }
    
   

    def run_optimization_cycle(self):
        """
        Główna pętla sterowania wyzwalana czasowo lub na żądanie.
        [cite_start]Realizuje Use Case: Wykonanie cyklu optymalizacji[cite: 174].
        """
        print("\n=== [START] CYKL OPTYMALIZACJI ===")

        # 1) PROGNOZA
        repo = ForecastingRepository()
        latest_forecast = repo.get_latest_forecast()
        forecast = self._normalize_forecast(latest_forecast)

        if forecast["horizon_len"] == 0:
            print("[WARN] Brak prognozy (consumption/production) z forecasting. Kończę cykl.")
            print("       RAW:", forecast["_raw"])
            return

        print(f"[FORECAST] Horyzont: {forecast['horizon_len']} kroków")
        print(f"          consumption[0]={forecast['consumption'][0]:.2f}, production[0]={forecast['production'][0]:.2f}, net[0]={forecast['net'][0]:.2f}")

        # 2) URZĄDZENIA
        devices = self.device_repo.get_all_active_devices()
        if not devices:
            print("[INFO] Brak aktywnych urządzeń. Kończę cykl.")
            return

        # 3) REGUŁY
        active_rules = self.rule_repo.get_active_rules() or []
        print(f"[DATA] Urządzeń: {len(devices)} | Aktywne reguły: {len(active_rules)}")

        # 4) PRZETWARZANIE
        processed_count = 0
        failed_count = 0

        for device in devices:
            print(f"\n--- Przetwarzanie urządzenia: {getattr(device, 'name', device)} (id={getattr(device, 'id', '?')}) ---")

            try:
                preference = self.pref_repo.get_preference_for_device(device.id)
                if preference is None:
                    print("   [INFO] Brak preferencji -> algorytm powinien użyć domyślnych.")

                settings = calculate_optimal_settings(
                    device=device,
                    forecast=forecast,          # <- teraz to ma sens
                    active_rules=active_rules,
                    preference=preference
                )

                if not isinstance(settings, dict) or not settings:
                    print("   [WARN] Algorytm zwrócił puste settings -> pomijam wysyłkę.")
                    failed_count += 1
                    continue

                print(f"   [WYNIK] Nastawy: {settings}")

                self.simulation_client.publish_command(device.id, settings)
                processed_count += 1

            except Exception as e:
                failed_count += 1
                print(f"   [ERROR] Błąd urządzenia id={getattr(device, 'id', '?')}: {e}")

        print(f"\n=== [KONIEC] Wysłano komendy dla {processed_count} urządzeń | Błędy: {failed_count} ===\n")