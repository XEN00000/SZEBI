from optimization.integration.repositories import DeviceRepository, RuleRepository, UserPreferenceRepository
from optimization.integration.clients import ForecastClient, SimulationClient
from optimization.logic.algorithm import calculate_optimal_settings

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
        
        self.forecast_client = ForecastClient()
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

    def run_optimization_cycle(self):
        """
        Główna pętla sterowania wyzwalana czasowo lub na żądanie.
        [cite_start]Realizuje Use Case: Wykonanie cyklu optymalizacji[cite: 174].
        """
        print("\n=== [START] CYKL OPTYMALIZACJI ===")

        # 1. POBIERANIE DANYCH 
        devices = self.device_repo.get_all_active_devices()
        if not devices:
            print("[INFO] Brak aktywnych urządzeń. Kończę cykl.")
            return

        forecast = self.forecast_client.get_energy_forecast()
        active_rules = self.rule_repo.get_active_rules()
        
        print(f"--> Znaleziono urządzeń: {len(devices)}")
        print(f"--> Prognoza: Cena={forecast.get('energy_price', 0):.2f} PLN, Temp={forecast.get('temperature', 0):.1f}C")

        # 2. PRZETWARZANIE (Dla każdego urządzenia)
        processed_count = 0
        for device in devices:
            print(f"\n--- Przetwarzanie: {device.name} ---")
            
            # [cite_start]A. Pobierz preferencje dla tego konkretnego urządzenia 
            preference = self.pref_repo.get_preference_for_device(device.id)
            
            # [cite_start]B. Uruchom Czysty Algorytm (calculateOptimalSettings )
            settings = calculate_optimal_settings(
                device=device,
                forecast=forecast,
                active_rules=active_rules,
                preference=preference
            )
            
            print(f"   [WYNIK] Wyznaczone nastawy: {settings}")

            # [cite_start]3. WYSYŁANIE ROZKAZÓW (Do symulacji )
            self.simulation_client.publish_command(device.id, settings)
            processed_count += 1

        print(f"\n=== [KONIEC] Przetworzono {processed_count} urządzeń ===\n")