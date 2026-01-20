from optimization.integration.repositories import (
    DeviceRepository,
    RuleRepository,
    UserPreferenceRepository
)
from optimization.integration.clients import SimulationClient
from optimization.logic.algorithm import calculate_optimal_settings
from optimization.integration.forecasting_repository import ForecastingRepository


class OptimizationController:
    """
    Główny kontroler logiki biznesowej.
    Zarządza przepływem danych między repozytoriami, algorytmem a światem zewnętrznym.
    """

    def __init__(self):
        self.device_repo = DeviceRepository()
        self.rule_repo = RuleRepository()
        self.pref_repo = UserPreferenceRepository()
        self.simulation_client = SimulationClient()

    # ---------------------------
    # ADAPTER: komenda do symulacji
    # ---------------------------
    def _build_simulation_command(self, base: dict, *, reason: str | None = None) -> dict:
        """
        Ujednolica payload przekazywany do SimulationClient.publish_command().

        publish_command() powinien dostać prosty dict z komendą, np:
          {"status": "OFF", "power_limit": 0, "reason": "..."}

        Ta metoda pilnuje:
        - domyślnych pól
        - typów
        - nie wysyłamy "dziwnych" kluczy, których symulacja może nie znać
        """
        base = dict(base or {})

        # Minimalny, bezpieczny zestaw pól
        cmd = {
            "status": str(base.get("status", "ON")).upper(),
            "power_limit": int(base.get("power_limit", 100)),
        }

        # target_value jest opcjonalne (np. HVAC)
        if "target_value" in base and base["target_value"] is not None:
            try:
                cmd["target_value"] = float(base["target_value"])
            except (TypeError, ValueError):
                pass

        # reason – pole diagnostyczne (bezpieczne, bo string)
        if reason:
            cmd["reason"] = reason
        elif "reason" in base and base["reason"] is not None:
            cmd["reason"] = str(base["reason"])

        # Wymuś zakres mocy 0..100
        if cmd["power_limit"] < 0:
            cmd["power_limit"] = 0
        if cmd["power_limit"] > 100:
            cmd["power_limit"] = 100

        return cmd

    def _send_to_simulation(self, device_id: int, command: dict) -> bool:
        """
        Jedno miejsce wysyłki komend do symulacji (MQTT).
        """
        ok = self.simulation_client.publish_command(device_id, command)
        if not ok:
            print(f"[CONTROLLER][WARN] publish_command() zwróciło False dla device_id={device_id}")
        return ok

    # ---------------------------
    # Alarmy
    # ---------------------------
    def receive_alarm(self, alarm_data: dict):
        """
        Obsługa payloadu z modułu Alarmów.
        """
        print(f"\n[CONTROLLER] !!! OTRZYMANO ALARM ZEWNĘTRZNY !!!")

        priority = alarm_data.get("priority")          # 'CRITICAL'
        metric = alarm_data.get("rule_metric")         # np. 'temp_sensor_1'
        value = alarm_data.get("triggering_value")     # np. 99.9

        print(f"Priorytet: {priority} | Metryka: {metric} | Wartość: {value}")

        if str(priority).upper() == "CRITICAL":
            print("[CONTROLLER] -> ALARM KRYTYCZNY! Analizuję cel...")

            # TODO: później mapowanie metric -> device_id (np. z repozytorium urządzeń)
            target_device_id = 1

            print(f"[CONTROLLER] -> Wysyłam Emergency Shutdown dla ID={target_device_id}")

            raw_cmd = {
                "status": "OFF",
                "power_limit": 0,
            }
            cmd = self._build_simulation_command(
                raw_cmd,
                reason=f"EXTERNAL_ALARM_CRITICAL metric={metric} value={value}"
            )
            self._send_to_simulation(target_device_id, cmd)
        else:
            print("[CONTROLLER] -> Alarm niekrytyczny. Loguję i ignoruję.")

    # ---------------------------
    # Forecasting
    # ---------------------------
    def _normalize_forecast(self, latest_forecast):
        """
        Normalizuje wynik ForecastingService.get_latest_forecast() do formatu dla algorytmu.

        Forecasting zwraca dict:
          {"consumption": [...], "production": [...]}

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

    # ---------------------------
    # Cykl optymalizacji
    # ---------------------------
    def run_optimization_cycle(self):
        """
        Główna pętla sterowania wyzwalana czasowo lub na żądanie.
        """
        print("\n=== [START] CYKL OPTYMALIZACJI ===")

        # 1) PROGNOZA
        repo = ForecastingRepository()
        latest_forecast = repo.get_latest_forecast()
        forecast = self._normalize_forecast(latest_forecast)

        if forecast["horizon_len"] == 0:
            print("[WARN] Brak prognozy z forecasting. Kończę cykl.")
            print("       RAW:", forecast["_raw"])
            return

        print(f"[FORECAST] Horyzont: {forecast['horizon_len']} kroków")
        print(
            f"          consumption[0]={forecast['consumption'][0]:.2f}, "
            f"production[0]={forecast['production'][0]:.2f}, "
            f"net[0]={forecast['net'][0]:.2f}"
        )

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
            device_id = getattr(device, "id", None)
            device_name = getattr(device, "name", str(device))

            print(f"\n--- Przetwarzanie urządzenia: {device_name} (id={device_id}) ---")

            if device_id is None:
                print("   [ERROR] Urządzenie nie ma id -> pomijam.")
                failed_count += 1
                continue

            try:
                preference = self.pref_repo.get_preference_for_device(device_id)
                if preference is None:
                    print("   [INFO] Brak preferencji -> algorytm użyje domyślnych.")

                settings = calculate_optimal_settings(
                    device=device,
                    forecast=forecast,
                    active_rules=active_rules,
                    preference=preference,
                )

                if not isinstance(settings, dict) or not settings:
                    print("   [WARN] Algorytm zwrócił puste settings -> pomijam wysyłkę.")
                    failed_count += 1
                    continue

                cmd = self._build_simulation_command(settings, reason="OPTIMIZATION_CYCLE")

                print(f"   [WYNIK] Komenda do symulacji: {cmd}")

                ok = self._send_to_simulation(device_id, cmd)
                if ok:
                    processed_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                failed_count += 1
                print(f"   [ERROR] Błąd urządzenia id={device_id}: {e}")

        print(f"\n=== [KONIEC] Wysłano komendy dla {processed_count} urządzeń | Błędy: {failed_count} ===\n")