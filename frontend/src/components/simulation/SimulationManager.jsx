import React, { useState } from 'react';
import { getCookie } from '../../utils/csrf';

const API_BASE_URL = 'http://localhost:8000';

const SimulationManager = ({ onSimulationRun }) => {
    // State for forms
    const [simName, setSimName] = useState('');
    const [simId, setSimId] = useState('');
    const [deviceName, setDeviceName] = useState('');
    const [deviceType, setDeviceType] = useState('');
    const [deviceWeatherId, setDeviceWeatherId] = useState('');
    const [removeDeviceId, setRemoveDeviceId] = useState('');
    const [weatherName, setWeatherName] = useState('');
    const [weatherType, setWeatherType] = useState('');
    const [weatherOutsideId, setWeatherOutsideId] = useState('');
    const [removeWeatherId, setRemoveWeatherId] = useState('');
    const [statusMsg, setStatusMsg] = useState('');
    const [running, setRunning] = useState(false);

    // Create simulation
    const handleCreateSimulation = async (e) => {
        e.preventDefault();
        setStatusMsg('');
        
        const nameRegex = /^[a-z][a-z0-9-]*$/;
        if (!nameRegex.test(simName)) {
            setStatusMsg('Błąd: Nazwa musi być małymi literami, cyframi lub myślnikiem (np. "test-1").');
            return;
        }

        const csrftoken = getCookie('csrftoken') || '';
        try {
            const res = await fetch(`${API_BASE_URL}/api/simulation/create`, {
                method: 'POST',
                credentials: 'include',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ name: simName })
            });
            const data = await res.json();
            setStatusMsg(data.status + (data.id ? ` (ID: ${data.id})` : ''));
        } catch {
            setStatusMsg('Error creating simulation');
        }
    };

    // Start simulation
    const handleStartSimulation = async (e) => {
        e.preventDefault();
        setStatusMsg('');
        setRunning(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/simulation/start?id=${simId}`, {
                method: 'GET',
                credentials: 'include',
            });
            const data = await res.json();
            setStatusMsg(data.status);
            if (onSimulationRun) onSimulationRun();
        } catch {
            setStatusMsg('Error starting simulation');
        } finally {
            setRunning(false);
        }
    };

    // Stop simulation
    const handleStopSimulation = async (e) => {
        e.preventDefault();
        setStatusMsg('');
        setRunning(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/simulation/stop?id=${simId}`, {
                method: 'GET',
                credentials: 'include',
            });
            const data = await res.json();
            setStatusMsg(data.status);
        } catch {
            setStatusMsg('Error stopping simulation');
        } finally {
            setRunning(false);
        }
    };

    // Add device
    const handleAddDevice = async (e) => {
        e.preventDefault();
        setStatusMsg('');

        const nameRegex = /^[a-z][a-z0-9-]*$/;
        if (!nameRegex.test(deviceName)) {
            setStatusMsg('Błąd: Nazwa urządzenia musi być małymi literami, cyframi lub myślnikiem.');
            return;
        }

        const csrftoken = getCookie('csrftoken') || '';
        try {
            const res = await fetch(`${API_BASE_URL}/api/simulation/device/add`, {
                method: 'POST',
                credentials: 'include',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ simulation_id: simId, name: deviceName, type: deviceType, weather_id: deviceWeatherId })
            });
            const data = await res.json();
            setStatusMsg(data.status + (data.uuid ? ` (Device UUID: ${data.uuid})` : ''));
        } catch {
            setStatusMsg('Error adding device');
        }
    };

    // Remove device
    const handleRemoveDevice = async (e) => {
        e.preventDefault();
        setStatusMsg('');
        const csrftoken = getCookie('csrftoken') || '';
        try {
            const res = await fetch(`${API_BASE_URL}/api/simulation/device/remove/${removeDeviceId}?id=${simId}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: { 
                    'X-CSRFToken': csrftoken
                },
            });
            const data = await res.json();
            setStatusMsg(data.status);
        } catch {
            setStatusMsg('Error removing device');
        }
    };

    // Add weather
    const handleAddWeather = async (e) => {
        e.preventDefault();
        setStatusMsg('');
        const csrftoken = getCookie('csrftoken') || '';
        try {
            const res = await fetch(`${API_BASE_URL}/api/simulation/weather/add`, {
                method: 'POST',
                credentials: 'include',
                headers: { 
                    'Content-Type': 'application/json', 
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ simulation_id: simId, name: weatherName, type: weatherType, outside_weather_id: weatherOutsideId })
            });
            const data = await res.json();
            setStatusMsg(data.status + (data.uuid ? ` (Weather UUID: ${data.uuid})` : ''));
        } catch {
            setStatusMsg('Error adding weather');
        }
    };

    // Remove weather
    const handleRemoveWeather = async (e) => {
        e.preventDefault();
        setStatusMsg('');
        const csrftoken = getCookie('csrftoken') || '';
        try {
            const res = await fetch(`${API_BASE_URL}/api/simulation/weather/remove/${removeWeatherId}?id=${simId}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: { 
                    'X-CSRFToken': csrftoken
                },
            });
            const data = await res.json();
            setStatusMsg(data.status);
        } catch {
            setStatusMsg('Error removing weather');
        }
    };

    return (
        <div className="flex flex-col gap-6">
             {/* Simulation Control Card */}
            <div className="data-card" style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
                <div className="card-header" style={{ backgroundColor: 'rgba(255, 255, 255, 0.01)' }}>
                    <h2 className="card-title">Sterowanie Symulacją</h2>
                </div>
                <div className="p-6">
                    <div className="form-grid">
                        <div className="form-group">
                             <label className="form-label">ID Symulacji (Globalne)</label>
                             <input 
                                className="form-input" 
                                value={simId} 
                                onChange={e => setSimId(e.target.value)} 
                                placeholder="Wpisz ID symulacji do sterowania..."
                                style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)' }}
                             />
                        </div>
                         <div className="form-group flex justify-end items-end gap-3 flex-wrap">
                            <button 
                                onClick={handleStartSimulation} 
                                disabled={running || !simId}
                                className={`btn-control btn-start flex-1 min-w-[120px] ${running || !simId ? 'btn-disabled' : ''}`}
                            >
                                Uruchom
                            </button>
                            <button 
                                onClick={handleStopSimulation} 
                                disabled={!running || !simId}
                                className={`btn-control btn-stop flex-1 min-w-[120px] ${!running || !simId ? 'btn-disabled' : ''}`}
                            >
                                Zatrzymaj
                            </button>
                        </div>
                    </div>

                    <div className="border-t border-white/10 my-6"></div>

                    <h3 className="text-lg font-semibold text-white mb-4">Utwórz nową symulację</h3>
                    <form onSubmit={handleCreateSimulation} className="form-grid items-end">
                        <div className="form-group">
                            <label className="form-label">Nazwa Symulacji</label>
                            <input 
                                className="form-input" 
                                value={simName} 
                                onChange={e => setSimName(e.target.value)} 
                                placeholder="Np. test-sim-1"
                                style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)' }}
                            />
                        </div>
                        <div className="form-group flex gap-3">
                             <button type="submit" className="btn-primary flex-1">Utwórz Pustą</button>
                             <button 
                                type="button" 
                                className="btn-secondary flex-1"
                                onClick={async (e) => {
                                    e.preventDefault();
                                    setStatusMsg('Uruchamianie domyślnej symulacji...');
                                    try {
                                        const res = await fetch(`${API_BASE_URL}/api/simulation/start_default`, {
                                            method: 'GET',
                                            credentials: 'include',
                                        });
                                        const data = await res.json();
                                        setStatusMsg(data.status + (data.id ? ` (ID: ${data.id})` : ''));
                                        if (data.id) setSimId(data.id);
                                        if (onSimulationRun) onSimulationRun();
                                    } catch {
                                        setStatusMsg('Błąd uruchamiania domyślnej symulacji');
                                    }
                                }}
                             >
                                 Uruchom Domyślną
                             </button>
                        </div>
                    </form>
                </div>
            </div>

            {/* Devices Management */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="data-card" style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
                    <div className="card-header" style={{ backgroundColor: 'rgba(255, 255, 255, 0.01)' }}>
                        <h2 className="card-title">Zarządzanie Urządzeniami</h2>
                    </div>
                    <div className="p-6 flex flex-col gap-6">
                        <form onSubmit={handleAddDevice} className="flex flex-col gap-4">
                            <h4 className="text-sm font-bold text-gray-400 uppercase">Dodaj Urządzenie</h4>
                            <div className="form-group">
                                <label className="form-label">Nazwa</label>
                                <input className="form-input" style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)' }} value={deviceName} onChange={e => setDeviceName(e.target.value)} placeholder="Nazwa urządzenia"/>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Typ</label>
                                <input className="form-input" style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)' }} value={deviceType} onChange={e => setDeviceType(e.target.value)} placeholder="Typ (np. ENERGY_METER)"/>
                            </div>
                            <div className="form-group">
                                <label className="form-label">ID Pogody (Opcjonalne)</label>
                                <input className="form-input" style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)' }} value={deviceWeatherId} onChange={e => setDeviceWeatherId(e.target.value)} placeholder="UUID pogody"/>
                            </div>
                            <button type="submit" className="btn-secondary w-full" disabled={!simId}>Dodaj do {simId || '...'}</button>
                        </form>

                        <div className="border-t border-white/10"></div>

                        <form onSubmit={handleRemoveDevice} className="flex flex-col gap-4">
                            <h4 className="text-sm font-bold text-gray-400 uppercase">Usuń Urządzenie</h4>
                            <div className="form-group">
                                <label className="form-label">UUID Urządzenia</label>
                                <input className="form-input" style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)' }} value={removeDeviceId} onChange={e => setRemoveDeviceId(e.target.value)} placeholder="UUID do usunięcia"/>
                            </div>
                            <button type="submit" className="btn-ghost-danger w-full justify-center" disabled={!simId}>Usuń z {simId || '...'}</button>
                        </form>
                    </div>
                </div>

                {/* Weather Management */}
                <div className="data-card" style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
                    <div className="card-header" style={{ backgroundColor: 'rgba(255, 255, 255, 0.01)' }}>
                        <h2 className="card-title">Zarządzanie Pogodą</h2>
                    </div>
                    <div className="p-6 flex flex-col gap-6">
                        <form onSubmit={handleAddWeather} className="flex flex-col gap-4">
                             <h4 className="text-sm font-bold text-gray-400 uppercase">Dodaj Warunki Pogodowe</h4>
                            <div className="form-group">
                                <label className="form-label">Nazwa</label>
                                <input className="form-input" style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)' }} value={weatherName} onChange={e => setWeatherName(e.target.value)} placeholder="Nazwa warunków"/>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Typ</label>
                                <input className="form-input" style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)' }} value={weatherType} onChange={e => setWeatherType(e.target.value)} placeholder="Typ pogody"/>
                            </div>
                             <div className="form-group">
                                <label className="form-label">ID Pogody Zewn.</label>
                                <input className="form-input" style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)' }} value={weatherOutsideId} onChange={e => setWeatherOutsideId(e.target.value)} placeholder="Opcjonalne ID"/>
                            </div>
                            <button type="submit" className="btn-secondary w-full" disabled={!simId}>Dodaj do {simId || '...'}</button>
                        </form>
                         <div className="border-t border-white/10"></div>

                        <form onSubmit={handleRemoveWeather} className="flex flex-col gap-4">
                            <h4 className="text-sm font-bold text-gray-400 uppercase">Usuń Warunki</h4>
                            <div className="form-group">
                                <label className="form-label">UUID Pogody</label>
                                <input className="form-input" style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)' }} value={removeWeatherId} onChange={e => setRemoveWeatherId(e.target.value)} placeholder="UUID do usunięcia"/>
                            </div>
                             <button type="submit" className="btn-ghost-danger w-full justify-center" disabled={!simId}>Usuń z {simId || '...'}</button>
                        </form>
                    </div>
                </div>
            </div>

             {/* Status Notification */}
            {statusMsg && (
                <div className="notification-toast notification-success fixed bottom-4 right-4 animate-bounce">
                    <div className="notification-content">
                        <span>{statusMsg}</span>
                    </div>
                    <button className="notification-close" onClick={() => setStatusMsg('')}>×</button>
                </div>
            )}
        </div>
    );
};

export default SimulationManager;