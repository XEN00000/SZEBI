def calculate_optimal_settings(device, forecast, active_rules, preference):
    """
    Algorytm wyznaczania nastaw (zgodny z metodą calculateOptimalSettings z diagramu).
    
    Argumenty:
    - device: obiekt Device (techniczne limity)
    - forecast: słownik z prognozą (cena, pogoda)
    - active_rules: lista aktywnych reguł
    - preference: obiekt UserPreference (lub None)
    """
    
    # 1. Ustawienia domyślne (Bezpieczne)
    command = {
        "status": "ON",
        "target_value": 21.0,  # Domyślna temperatura/jasność
        "power_limit": 100     # 100% mocy
    }

    # 2. Zastosuj Preferencje Użytkownika (Komfort)
    if preference:
        if preference.target_value is not None:
            command["target_value"] = preference.target_value
            print(f"   [ALG] Zastosowano preferencję użytkownika: {preference.target_value}")
        
        # Tutaj można by obsłużyć harmonogram (schedule)
        # if preference.schedule...

    # 3. Zastosuj Reguły Optymalizacji (Ekonomia/Bezpieczeństwo)
    # Prosty silnik reguł: sprawdzamy cenę energii
    current_price = forecast.get('energy_price', 0.0)
    
    for rule in active_rules:
        # Przykładowa logika parsująca warunek tekstowy (uproszczona)
        # Np. rule.condition = "price > 1.0"
        
        rule_triggered = False
        
        if "price" in rule.condition and ">" in rule.condition:
            # Bardzo prosty parser: wyciągamy liczbę z końca stringa
            try:
                threshold = float(rule.condition.split(">")[1])
                if current_price > threshold:
                    rule_triggered = True
            except ValueError:
                print(f"   [ERR] Błąd parsowania reguły: {rule.condition}")

        if rule_triggered:
            print(f"   [ALG] !!! URUCHOMIONO REGUŁĘ: {rule.name} (Cena {current_price} > limitu)")
            
            # Interpretacja akcji (np. "reduce_power_50")
            if "reduce_power" in rule.action:
                command["power_limit"] = 50
                print("   [ALG] -> Zredukowano moc do 50%")
            
            if "reduce_target" in rule.action:
                command["target_value"] -= 2.0
                print("   [ALG] -> Obniżono cel o 2.0 jednostki")
                
            if "shutdown" in rule.action:
                command["status"] = "OFF"
                command["power_limit"] = 0
                print("   [ALG] -> WYŁĄCZENIE URZĄDZENIA")
                break # Wyłączenie jest nadrzędne, przerywamy pętlę

    return command