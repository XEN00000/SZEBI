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
        Mapuje wewnętrzny wynik algorytmu (status/power_limit/target_value)
        na format rozumiany przez symulację:

        - is_active: bool
        - is_on: bool
        - level: 0.0..1.0   (dla SMART_DEVICE: ogrzewanie/klima/światło)
        """
        base = dict(base or {})
        status = str(base.get("status", "ON")).upper()
        power_limit = base.get("power_limit", 100)

        # power_limit 0..100 -> level 0.0..1.0
        try:
            power_limit = int(power_limit)
        except (TypeError, ValueError):
            power_limit = 100
        power_limit = max(0, min(100, power_limit))
        level = power_limit / 100.0

        # Domyślnie: urządzenie aktywne
        cmd = {"is_active": True}

        # Mapowanie statusów na is_on/level
        if status == "OFF":
            cmd["is_active"] = False      # pełne wyłączenie (jak opisał kolega)
            cmd["is_on"] = False
            cmd["level"] = 0.0
        elif status in ("ECONOMY", "ON"):
            cmd["is_on"] = True
            cmd["level"] = level
        else:
            # nieznany status -> zachowaj bezpiecznie
            cmd["is_on"] = True
            cmd["level"] = level

        # Opcjonalnie diagnostyka (jeśli symulacja to toleruje)
        # Jak chcesz 100% zgodność z opisem kolegi, to usuń te 2 linie.
        if reason:
            cmd["reason"] = reason

        return cmd

    def _send_to_simulation(self, device_uuid: str, command: dict) -> bool:
        ok = self.simulation_client.publish_command(device_uuid, command)
        if not ok:
            print(f"[CONTROLLER][WARN] publish_command() zwróciło False dla uuid={device_uuid}")
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
            # self._send_to_simulation(target_device_id, cmd)
            self.run_optimization_cycle()  # tymczasowo uruchamiamy cykl optymalizacji
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
            # device_id = getattr(device, "id", None)
            device_uuid = getattr(device, "uuid", None)
            device_name = getattr(device, "name", str(device))

            print(f"\n--- Przetwarzanie urządzenia: {device_name} (uuid={device_uuid}) ---")

            if device_uuid is None:
                print("   [ERROR] Urządzenie nie ma uuid -> pomijam.")
                failed_count += 1
                continue

            try:
                preference = self.pref_repo.get_preference_for_device(device_uuid)
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

                ok = self._send_to_simulation(device_uuid, cmd)
                if ok:
                    processed_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                failed_count += 1
                print(f"   [ERROR] Błąd urządzenia id={device_id}: {e}")

        print(f"\n=== [KONIEC] Wysłano komendy dla {processed_count} urządzeń | Błędy: {failed_count} ===\n")