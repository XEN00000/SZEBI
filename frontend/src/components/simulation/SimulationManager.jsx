import React, { useState } from 'react';

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
        try {
            const res = await fetch(`${API_BASE_URL}/api/simulation/create/`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
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
            const res = await fetch(`${API_BASE_URL}/api/simulation/start/?id=${simId}`, {
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
            const res = await fetch(`${API_BASE_URL}/api/simulation/stop/?id=${simId}`, {
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
        try {
            const res = await fetch(`${API_BASE_URL}/api/simulation/device/add/`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
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
        try {
            const res = await fetch(`${API_BASE_URL}/api/simulation/device/remove/${removeDeviceId}/?id=${simId}`, {
                method: 'DELETE',
                credentials: 'include',
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
        try {
            const res = await fetch(`${API_BASE_URL}/api/simulation/weather/add/`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
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
        try {
            const res = await fetch(`${API_BASE_URL}/api/simulation/weather/remove/${removeWeatherId}/?id=${simId}`, {
                method: 'DELETE',
                credentials: 'include',
            });
            const data = await res.json();
            setStatusMsg(data.status);
        } catch {
            setStatusMsg('Error removing weather');
        }
    };

    return (
        <div>
            <h3>Simulation Management</h3>
            <form onSubmit={handleCreateSimulation}>
                <div>
                    <label>Simulation Name: </label>
                    <input value={simName} onChange={e => setSimName(e.target.value)} />
                    <button type="submit">Create Simulation</button>
                </div>
            </form>
            <form onSubmit={handleStartSimulation}>
                <div>
                    <label>Simulation ID: </label>
                    <input value={simId} onChange={e => setSimId(e.target.value)} />
                    <button type="submit" disabled={running}>Start Simulation</button>
                </div>
            </form>
            <form onSubmit={handleStopSimulation}>
                <div>
                    <label>Simulation ID: </label>
                    <input value={simId} onChange={e => setSimId(e.target.value)} />
                    <button type="submit" disabled={running}>Stop Simulation</button>
                </div>
            </form>
            <form onSubmit={handleAddDevice}>
                <div>
                    <label>Simulation ID: </label>
                    <input value={simId} onChange={e => setSimId(e.target.value)} />
                </div>
                <div>
                    <label>Device Name: </label>
                    <input value={deviceName} onChange={e => setDeviceName(e.target.value)} />
                </div>
                <div>
                    <label>Device Type: </label>
                    <input value={deviceType} onChange={e => setDeviceType(e.target.value)} />
                </div>
                <div>
                    <label>Weather ID: </label>
                    <input value={deviceWeatherId} onChange={e => setDeviceWeatherId(e.target.value)} />
                </div>
                <button type="submit">Add Device</button>
            </form>
            <form onSubmit={handleRemoveDevice}>
                <div>
                    <label>Simulation ID: </label>
                    <input value={simId} onChange={e => setSimId(e.target.value)} />
                </div>
                <div>
                    <label>Device UUID: </label>
                    <input value={removeDeviceId} onChange={e => setRemoveDeviceId(e.target.value)} />
                </div>
                <button type="submit">Remove Device</button>
            </form>
            <form onSubmit={handleAddWeather}>
                <div>
                    <label>Simulation ID: </label>
                    <input value={simId} onChange={e => setSimId(e.target.value)} />
                </div>
                <div>
                    <label>Weather Name: </label>
                    <input value={weatherName} onChange={e => setWeatherName(e.target.value)} />
                </div>
                <div>
                    <label>Weather Type: </label>
                    <input value={weatherType} onChange={e => setWeatherType(e.target.value)} />
                </div>
                <div>
                    <label>Outside Weather ID: </label>
                    <input value={weatherOutsideId} onChange={e => setWeatherOutsideId(e.target.value)} />
                </div>
                <button type="submit">Add Weather</button>
            </form>
            <form onSubmit={handleRemoveWeather}>
                <div>
                    <label>Simulation ID: </label>
                    <input value={simId} onChange={e => setSimId(e.target.value)} />
                </div>
                <div>
                    <label>Weather UUID: </label>
                    <input value={removeWeatherId} onChange={e => setRemoveWeatherId(e.target.value)} />
                </div>
                <button type="submit">Remove Weather</button>
            </form>
            <div>{statusMsg}</div>
        </div>
    );
};

export default SimulationManager;