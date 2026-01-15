from datetime import datetime

mock_sensor_types = {
    1: {"id": 1, "name": "temperature", "default_unit": "celsius", "min_value": -20, "max_value": 50},
    2: {"id": 2, "name": "humidity", "default_unit": "percent", "min_value": 0, "max_value": 100},
}

mock_locations = {
    1: {"id": 1, "floor": 1, "room": "101", "description": "Main server room"},
    2: {"id": 2, "floor": 1, "room": "102", "description": "Office area"},
}

mock_sensors = {
    1: {"id": 1, "name": "Temp S1", "type_id": 1, "location_id": 1, "status": "ACTIVE"},
    2: {"id": 2, "name": "Hum S1", "type_id": 2, "location_id": 1, "status": "ACTIVE"},

    3: {"id": 3, "name": "Temp S2", "type_id": 1, "location_id": 2, "status": "ACTIVE"},
    4: {"id": 4, "name": "Hum S2", "type_id": 2, "location_id": 2, "status": "ACTIVE"},
}

mock_measurements = [

    {"id": 1,  "sensor_id": 1, "timestamp": datetime(2025, 12, 1, 8, 0), "value": 22.5, "status": "OK"},
    {"id": 2,  "sensor_id": 1, "timestamp": datetime(2025, 12, 1, 9, 0), "value": 23.0, "status": "OK"},
    {"id": 3,  "sensor_id": 1, "timestamp": datetime(2025, 12, 1, 10,0), "value": 23.5, "status": "OK"},


    {"id": 4,  "sensor_id": 2, "timestamp": datetime(2025, 12, 1, 8, 0), "value": 40, "status": "OK"},
    {"id": 5,  "sensor_id": 2, "timestamp": datetime(2025, 12, 1, 9, 0), "value": 42, "status": "OK"},
    {"id": 6,  "sensor_id": 2, "timestamp": datetime(2025, 12, 1, 10,0), "value": 43, "status": "OK"},


    {"id": 7,  "sensor_id": 3, "timestamp": datetime(2025, 12, 1, 8, 0), "value": 21.0, "status": "OK"},
    {"id": 8,  "sensor_id": 3, "timestamp": datetime(2025, 12, 1, 9, 0), "value": 21.5, "status": "OK"},


    {"id": 9,  "sensor_id": 4, "timestamp": datetime(2025, 12, 1, 8, 0), "value": 45, "status": "OK"},
    {"id": 10, "sensor_id": 4, "timestamp": datetime(2025, 12, 1, 9, 0), "value": 44, "status": "OK"},
]

def measurement_filter(timestamp_range=None, room=None, metric=None):
    results = mock_measurements

    if timestamp_range:
        start, end = timestamp_range
        results = [
            m for m in results
            if start <= m["timestamp"] <= end
        ]

    if room:
        results = [
            m for m in results
            if mock_sensors[m["sensor_id"]]["location_id"] in mock_locations
            and mock_locations[mock_sensors[m["sensor_id"]]["location_id"]]["room"] == room
        ]

    if metric:
        results = [
            m for m in results
            if mock_sensor_types[mock_sensors[m["sensor_id"]]["type_id"]]["name"] == metric
        ]

    return sorted(results, key=lambda m: m["timestamp"])
