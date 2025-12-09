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
        Obsługa alarmów przychodzących z zewnątrz (IAlertListener)[cite: 112].
        """
        severity = alarm_data.get('severity')
        device_id = alarm_data.get('device_id')
        
        print(f"\n[CONTROLLER] !!! OTRZYMANO ALARM !!!")
        print(f"Urządzenie ID: {device_id} | Poziom: {severity}")
        print(f"Treść: {alarm_data.get('message')}")

        if severity == 'CRITICAL':
            print(f"[CONTROLLER] -> Uruchamiam procedurę awaryjną (Emergency Shutdown)...")
            # Natychmiastowe wysłanie komendy wyłączenia
            self.simulation_client.publish_command(device_id, {"status": "OFF", "reason": "ALARM_CRITICAL"})
        else:
            print("[CONTROLLER] -> Alarm zanotowany, brak akcji krytycznej.")

    def run_optimization_cycle(self):
        """
        Główna pętla sterowania wyzwalana czasowo lub na żądanie[cite: 108, 179].
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
            
            # A. Pobierz preferencje dla tego konkretnego urządzenia
            preference = self.pref_repo.get_preference_for_device(device.id)
            
            # B. Uruchom Czysty Algorytm 
            settings = calculate_optimal_settings(
                device=device,
                forecast=forecast,
                active_rules=active_rules,
                preference=preference
            )
            
            print(f"   [WYNIK] Wyznaczone nastawy: {settings}")
            # 3. WYSYŁANIE ROZKAZÓW (Do symulacji) 
            self.simulation_client.publish_command(device.id, settings)
            processed_count += 1

        print(f"\n=== [KONIEC] Przetworzono {processed_count} urządzeń ===\n")