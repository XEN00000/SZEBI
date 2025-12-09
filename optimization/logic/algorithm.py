def calculate_optimal_settings(device, forecast, active_rules, preference):
    """
    Algorytm wyznaczania nastaw (zgodny z metodą calculateOptimalSettings z diagramu).
    
    Argumenty:
    - device: obiekt Device (techniczne limity)
    - forecast: słownik z prognozą (cena, pogoda)
    - active_rules: lista aktywnych reguł
    - preference: obiekt UserPreference (lub None)
    """
    command = {
        "status": "ON",
        "target_value": 21.0,  # Domyślna temperatura
        "power_limit": 100     # 100% mocy
    }

    # 2. Zastosuj Preferencje Użytkownika (Komfort) 
    if preference:
        if preference.target_value is not None:
            command["target_value"] = preference.target_value
            # Jeżeli masz zdefiniowany harmonogram w JSON, tu byś go parsował
    
    # 3. Zastosuj Reguły Optymalizacji (Ekonomia/Bezpieczeństwo) 
    current_price = forecast.get('energy_price', 0.0)
    
    for rule in active_rules:
        # --- Prosty silnik reguł (interpretacja tekstu z bazy) ---
        # Zakładamy format warunku np.: "price > 0.80"
        rule_triggered = False
        
        if "price" in rule.condition and ">" in rule.condition:
            try:
                # Parsowanie warunku: bierzemy liczbę po znaku ">"
                threshold = float(rule.condition.split(">")[1])
                if current_price > threshold:
                    rule_triggered = True
            except ValueError:
                print(f"   [ALG ERROR] Błędny format reguły ID={rule.id}: {rule.condition}")

        # Jeśli reguła zadziałała, wykonaj akcję
        if rule_triggered:
            print(f"   [ALG] !!! URUCHOMIONO REGUŁĘ: {rule.name} (Cena {current_price:.2f} > limitu)")
            
            # Interpretacja akcji (przykłady)
            if "reduce_power" in rule.action:
                command["power_limit"] = 50  # Ogranicz moc do 50%
                command["status"] = "ECONOMY"
            
            elif "shutdown" in rule.action:
                command["status"] = "OFF"
                command["power_limit"] = 0
                break # Wyłączenie jest nadrzędne, przerywamy pętlę

    return command