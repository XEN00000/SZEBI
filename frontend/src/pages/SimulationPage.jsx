import React, { useState } from 'react';

const API_BASE = '/api/simulation';

const SimulationPage = () => {
    const [simulationId, setSimulationId] = useState('');
    const [newSimulationName, setNewSimulationName] = useState('');
    const [deviceUuid, setDeviceUuid] = useState('');
    const [weatherUuid, setWeatherUuid] = useState('');
    const [deviceForm, setDeviceForm] = useState({ name: '', type: '', weatherId: '', extra: '{}' });
    const [weatherForm, setWeatherForm] = useState({ name: '', type: '', outsideId: '', extra: '{}' });
    const [output, setOutput] = useState('');

    const getCsrfToken = () => {
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    };

    const handleRequest = async ({ endpoint, method = 'GET', body }) => {
        try {
            const options = { method, credentials: 'include', headers: {} };
            if (body && method !== 'GET') {
                options.headers['Content-Type'] = 'application/json';
                options.headers['X-CSRFToken'] = getCsrfToken();
                options.body = JSON.stringify(body);
            }
            const response = await fetch(`${API_BASE}${endpoint}`, options);
            const data = await response.json();
            setOutput(JSON.stringify(data, null, 2));
        } catch (error) {
            setOutput(JSON.stringify({ error: error.message }, null, 2));
        }
    };

    const ensureId = () => {
        if (!simulationId) {
            setOutput('Provide a simulation id first.');
            return false;
        }
        return true;
    };

    const parseJsonInput = (value) => {
        if (!value) {
            return {};
        }
        try {
            return JSON.parse(value);
        } catch (error) {
            setOutput(`Invalid JSON: ${error.message}`);
            throw error;
        }
    };

    return (
        <div>
            <h1>Simulation Management</h1>

            <section>
                <h2>Simulation Configuration</h2>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        handleRequest({ endpoint: '/create', method: 'POST', body: { name: newSimulationName || undefined } });
                    }}
                >
                    <label>
                        Simulation name:
                        <input value={newSimulationName} onChange={(event) => setNewSimulationName(event.target.value)} />
                    </label>
                    <button type="submit">Create Simulation</button>
                </form>

                <label>
                    Active simulation id:
                    <input value={simulationId} onChange={(event) => setSimulationId(event.target.value)} />
                </label>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        if (!ensureId()) {
                            return;
                        }
                        handleRequest({ endpoint: `/start?id=${encodeURIComponent(simulationId)}` });
                    }}
                >
                    <button type="submit">Start Simulation</button>
                </form>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        if (!ensureId()) {
                            return;
                        }
                        handleRequest({ endpoint: `/stop?id=${encodeURIComponent(simulationId)}` });
                    }}
                >
                    <button type="submit">Stop Simulation</button>
                </form>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        handleRequest({ endpoint: '/start_default' });
                    }}
                >
                    <button type="submit">Start Default Simulation</button>
                </form>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        if (!ensureId()) {
                            return;
                        }
                        handleRequest({ endpoint: `/status?id=${encodeURIComponent(simulationId)}` });
                    }}
                >
                    <button type="submit">Get Simulation Status</button>
                </form>
            </section>

            <section>
                <h2>Device Management</h2>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        if (!ensureId()) {
                            return;
                        }
                        handleRequest({ endpoint: `/device/list?id=${encodeURIComponent(simulationId)}` });
                    }}
                >
                    <button type="submit">List Devices</button>
                </form>

                <label>
                    Device uuid:
                    <input value={deviceUuid} onChange={(event) => setDeviceUuid(event.target.value)} />
                </label>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        if (!ensureId() || !deviceUuid) {
                            if (!deviceUuid) {
                                setOutput('Provide a device uuid first.');
                            }
                            return;
                        }
                        handleRequest({ endpoint: `/device/status/${encodeURIComponent(deviceUuid)}?id=${encodeURIComponent(simulationId)}` });
                    }}
                >
                    <button type="submit">Get Device Status</button>
                </form>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        if (!ensureId() || !deviceUuid) {
                            if (!deviceUuid) {
                                setOutput('Provide a device uuid first.');
                            }
                            return;
                        }
                        handleRequest({ endpoint: `/device/remove/${encodeURIComponent(deviceUuid)}?id=${encodeURIComponent(simulationId)}`, method: 'DELETE' });
                    }}
                >
                    <button type="submit">Remove Device</button>
                </form>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        if (!ensureId()) {
                            return;
                        }
                        if (!deviceForm.weatherId) {
                            setOutput('Provide a weather id for the new device.');
                            return;
                        }
                        let extraValues = {};
                        try {
                            extraValues = parseJsonInput(deviceForm.extra);
                        } catch {
                            return;
                        }
                        const payload = {
                            simulation_id: simulationId,
                            name: deviceForm.name || undefined,
                            type: deviceForm.type || undefined,
                            weather_id: deviceForm.weatherId,
                            ...extraValues,
                        };
                        handleRequest({ endpoint: '/device/add', method: 'POST', body: payload });
                    }}
                >
                    <div>
                        <label>
                            Device name:
                            <input value={deviceForm.name} onChange={(event) => setDeviceForm({ ...deviceForm, name: event.target.value })} />
                        </label>
                    </div>
                    <div>
                        <label>
                            Device type:
                            <input value={deviceForm.type} onChange={(event) => setDeviceForm({ ...deviceForm, type: event.target.value })} />
                        </label>
                    </div>
                    <div>
                        <label>
                            Weather id:
                            <input value={deviceForm.weatherId} onChange={(event) => setDeviceForm({ ...deviceForm, weatherId: event.target.value })} />
                        </label>
                    </div>
                    <div>
                        <label>
                            Extra JSON:
                            <textarea value={deviceForm.extra} onChange={(event) => setDeviceForm({ ...deviceForm, extra: event.target.value })} />
                        </label>
                    </div>
                    <button type="submit">Add Device</button>
                </form>
            </section>

            <section>
                <h2>Weather Management</h2>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        if (!ensureId()) {
                            return;
                        }
                        handleRequest({ endpoint: `/weather/list?id=${encodeURIComponent(simulationId)}` });
                    }}
                >
                    <button type="submit">List Weathers</button>
                </form>

                <label>
                    Weather uuid:
                    <input value={weatherUuid} onChange={(event) => setWeatherUuid(event.target.value)} />
                </label>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        if (!ensureId() || !weatherUuid) {
                            if (!weatherUuid) {
                                setOutput('Provide a weather uuid first.');
                            }
                            return;
                        }
                        handleRequest({ endpoint: `/weather/status/${encodeURIComponent(weatherUuid)}?id=${encodeURIComponent(simulationId)}` });
                    }}
                >
                    <button type="submit">Get Weather Status</button>
                </form>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        if (!ensureId() || !weatherUuid) {
                            if (!weatherUuid) {
                                setOutput('Provide a weather uuid first.');
                            }
                            return;
                        }
                        handleRequest({ endpoint: `/weather/remove/${encodeURIComponent(weatherUuid)}?id=${encodeURIComponent(simulationId)}`, method: 'DELETE' });
                    }}
                >
                    <button type="submit">Remove Weather</button>
                </form>

                <form
                    onSubmit={(event) => {
                        event.preventDefault();
                        if (!ensureId()) {
                            return;
                        }
                        let extraValues = {};
                        try {
                            extraValues = parseJsonInput(weatherForm.extra);
                        } catch {
                            return;
                        }
                        const payload = {
                            simulation_id: simulationId,
                            name: weatherForm.name || undefined,
                            type: weatherForm.type || undefined,
                            outside_weather_id: weatherForm.outsideId || undefined,
                            ...extraValues,
                        };
                        handleRequest({ endpoint: '/weather/add', method: 'POST', body: payload });
                    }}
                >
                    <div>
                        <label>
                            Weather name:
                            <input value={weatherForm.name} onChange={(event) => setWeatherForm({ ...weatherForm, name: event.target.value })} />
                        </label>
                    </div>
                    <div>
                        <label>
                            Weather type:
                            <input value={weatherForm.type} onChange={(event) => setWeatherForm({ ...weatherForm, type: event.target.value })} />
                        </label>
                    </div>
                    <div>
                        <label>
                            Outside weather id (optional):
                            <input value={weatherForm.outsideId} onChange={(event) => setWeatherForm({ ...weatherForm, outsideId: event.target.value })} />
                        </label>
                    </div>
                    <div>
                        <label>
                            Extra JSON:
                            <textarea value={weatherForm.extra} onChange={(event) => setWeatherForm({ ...weatherForm, extra: event.target.value })} />
                        </label>
                    </div>
                    <button type="submit">Add Weather</button>
                </form>
            </section>

            <section>
                <h2>Latest Response</h2>
                <pre>{output}</pre>
            </section>
        </div>
    );
};

export default SimulationPage;
