from datetime import datetime
from django.utils import timezone


def _is_device_scheduled_on(preference) -> bool:
    """
    Minimalna obsługa schedule (JSON) w preferencjach.
    Wspieramy 2 proste formaty:
      1) {"enabled": true/false}
      2) {"hours_on": [7,8,9,...]}  -> urządzenie działa tylko w tych godzinach (0-23)
    Jeśli brak/nieznany format -> True (nie blokujemy pracy).
    """
    if not preference:
        return True

    schedule = getattr(preference, "schedule", None) or {}
    if not isinstance(schedule, dict):
        return True

    if "enabled" in schedule:
        return bool(schedule.get("enabled"))

    hours_on = schedule.get("hours_on")
    if isinstance(hours_on, list):
        try:
            now_hour = timezone.localtime(timezone.now()).hour
        except Exception:
            now_hour = datetime.now().hour
        return now_hour in set(int(h) for h in hours_on if str(h).isdigit())

    return True


def calculate_optimal_settings(device, forecast, active_rules, preference):
    """
    Algorytm wyznaczania nastaw.

    Wejścia:
    - device: obiekt Device (ma m.in. priority / nominal_power / device_type)
    - forecast: dict z controller._normalize_forecast():
        {
          "consumption": [...],
          "production": [...],
          "net": [...],          # consumption - production
          "horizon_len": int
        }
    - active_rules: lista OptimizationRule (condition/action jako tekst)
    - preference: UserPreference lub None
    """

    # 0) Domyślne polecenie
    command = {
        "status": "ON",
        "target_value": 21.0,   # domyślny komfort (np. temperatura)
        "power_limit": 100      # % mocy
    }

    # 1) Preferencje: target_value + schedule
    if preference and preference.target_value is not None:
        command["target_value"] = float(preference.target_value)

    if not _is_device_scheduled_on(preference):
        command["status"] = "OFF"
        command["power_limit"] = 0
        command["reason"] = "OUT_OF_SCHEDULE"
        return command

    # 2) Wyciągnij metryki z prognozy
    net = (forecast or {}).get("net") or []
    if not net:
        # brak prognozy -> tylko preferencje, bez optymalizacji ekonomicznej
        command["reason"] = "NO_FORECAST"
        return command

    # Proste wskaźniki
    net_now = float(net[0])                 # deficyt/nadwyżka "teraz"
    net_avg = sum(net) / len(net)           # średnio w horyzoncie
    net_max = max(net)                      # najgorszy deficyt
    net_min = min(net)                      # największa nadwyżka

    # 3) Bazowa logika (działa nawet bez reguł)
    # Deficyt energii -> oszczędzaj (szczególnie urządzenia o niskim priorytecie)
    device_priority = getattr(device, "priority", 1)

    if net_now > 0:
        # im większy deficyt, tym mocniej przycinamy
        if net_now > 50:
            command["status"] = "ECONOMY"
            command["power_limit"] = 30 if device_priority >= 5 else 60
            command["reason"] = "HIGH_DEFICIT"
        elif net_now > 10:
            command["status"] = "ECONOMY"
            command["power_limit"] = 50 if device_priority >= 5 else 80
            command["reason"] = "DEFICIT"
    else:
        # nadwyżka -> pozwól działać normalnie
        command["reason"] = "SURPLUS_OR_BALANCED"

    # 4) Reguły z bazy: proste warunki na net
    # Wspieramy warunki typu:
    #   "net > 20"  -> deficyt ponad 20
    #   "net_avg > 5"
    #   "net_max > 50"
    # i akcje:
    #   "reduce_power=50"
    #   "shutdown"
    #   "set_mode=ECONOMY"
    def _get_metric_value(metric_name: str) -> float:
        if metric_name == "net":
            return net_now
        if metric_name == "net_avg":
            return net_avg
        if metric_name == "net_max":
            return net_max
        if metric_name == "net_min":
            return net_min
        return 0.0

    for rule in (active_rules or []):
        cond = (rule.condition or "").strip().lower()
        act = (rule.action or "").strip().lower()

        triggered = False

        # obsługa formatu: "<metric> > <number>"
        if ">" in cond:
            left, right = cond.split(">", 1)
            metric_name = left.strip()
            try:
                threshold = float(right.strip())
                value = _get_metric_value(metric_name)
                if value > threshold:
                    triggered = True
            except ValueError:
                print(f"   [ALG ERROR] Błędny format reguły ID={rule.id}: {rule.condition}")

        if not triggered:
            continue

        print(f"   [ALG] !!! URUCHOMIONO REGUŁĘ: {rule.name} ({rule.condition})")

        # Akcje
        if "shutdown" in act:
            command["status"] = "OFF"
            command["power_limit"] = 0
            command["reason"] = f"RULE:{rule.id}"
            break

        if "set_mode=" in act:
            # np. set_mode=ECONOMY
            mode = act.split("set_mode=", 1)[1].strip().upper()
            command["status"] = mode
            command["reason"] = f"RULE:{rule.id}"

        if "reduce_power" in act:
            # obsługa "reduce_power=50" albo samo "reduce_power"
            if "=" in act:
                try:
                    limit = int(act.split("reduce_power=", 1)[1].strip())
                    limit = max(0, min(100, limit))
                    command["power_limit"] = limit
                except ValueError:
                    command["power_limit"] = 50
            else:
                command["power_limit"] = 50

            if command["status"] == "ON":
                command["status"] = "ECONOMY"
            command["reason"] = f"RULE:{rule.id}"

    return command