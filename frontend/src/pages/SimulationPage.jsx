import React, { useEffect, useState } from 'react';
import { getCookie } from '../utils/csrf';

const API_BASE_URL = 'http://localhost:8000';

const SimulationPage = () => {
	const [simId, setSimId] = useState('');
	const [statusMsg, setStatusMsg] = useState('');
	const [devices, setDevices] = useState([]);
	const [weathers, setWeathers] = useState([]);
	const [timingInfo, setTimingInfo] = useState(null);
	const [baseTickMs, setBaseTickMs] = useState('');
	const [speedRatio, setSpeedRatio] = useState('');

	const [deviceName, setDeviceName] = useState('');
	const [deviceType, setDeviceType] = useState('lighting');
	const [deviceWeatherId, setDeviceWeatherId] = useState('');
	const [removeDeviceId, setRemoveDeviceId] = useState('');
	const [extraPower, setExtraPower] = useState('');
	const [extraLightOutput, setExtraLightOutput] = useState('');
	const [extraCoolingPower, setExtraCoolingPower] = useState('');
	const [extraPeakPower, setExtraPeakPower] = useState('');
	const [extraCapacity, setExtraCapacity] = useState('');
	const [extraMaxCharge, setExtraMaxCharge] = useState('');
	const [extraMaxDischarge, setExtraMaxDischarge] = useState('');
	const [extraConnectionPower, setExtraConnectionPower] = useState('');
	const [extraStandbyPower, setExtraStandbyPower] = useState('');
	const [extraRatedPower, setExtraRatedPower] = useState('');

	const [weatherName, setWeatherName] = useState('');
	const [weatherType, setWeatherType] = useState('outside');
	const [weatherOutsideId, setWeatherOutsideId] = useState('');
	const [removeWeatherId, setRemoveWeatherId] = useState('');

	const refreshTiming = async (id = simId) => {
		if (!id) return;
		try {
			const res = await fetch(`${API_BASE_URL}/api/simulation/timing?id=${id}`, {
				method: 'GET',
				credentials: 'include',
			});
			const data = await res.json();
			if (res.ok) {
				setTimingInfo(data.simulation || null);
			} else {
				setTimingInfo(null);
			}
		} catch {
			setTimingInfo(null);
		}
	};

	const ensureSimulation = async () => {
		try {
			await fetch(`${API_BASE_URL}/api/simulation/`, {
				method: 'GET',
				credentials: 'include',
			});
			const csrftoken = getCookie('csrftoken') || '';
			const res = await fetch(`${API_BASE_URL}/api/simulation/create`, {
				method: 'POST',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': csrftoken,
				},
				body: JSON.stringify({ name: 'szebi' }),
			});
			const data = await res.json();
			if (data.id) setSimId(data.id);
		} catch {
			setStatusMsg('Error initializing simulation');
		}
	};

	const refreshDevices = async (id = simId) => {
		if (!id) return;
		try {
			const res = await fetch(`${API_BASE_URL}/api/simulation/device/list?id=${id}`, {
				method: 'GET',
				credentials: 'include',
			});
			const data = await res.json();
			if (res.ok) {
				setDevices(data.devices || []);
			} else {
				setDevices([]);
			}
		} catch {
			setDevices([]);
		}
	};

	const refreshWeathers = async (id = simId) => {
		if (!id) return;
		try {
			const res = await fetch(`${API_BASE_URL}/api/simulation/weather/list?id=${id}`, {
				method: 'GET',
				credentials: 'include',
			});
			const data = await res.json();
			if (res.ok) {
				setWeathers(data.weathers || []);
			} else {
				setWeathers([]);
			}
		} catch {
			setWeathers([]);
		}
	};

	const refreshAll = async () => {
		await refreshWeathers();
		await refreshDevices();
		await refreshTiming();
	};

	useEffect(() => {
		ensureSimulation();
	}, []);

	useEffect(() => {
		if (!simId) return;
		refreshAll();
	}, [simId]);

	const handleStart = async () => {
		if (!simId) return;
		setStatusMsg('');
		try {
			const res = await fetch(`${API_BASE_URL}/api/simulation/start?id=${simId}`, {
				method: 'GET',
				credentials: 'include',
			});
			const data = await res.json();
			setStatusMsg(data.status || 'Simulation started');
			await refreshAll();
		} catch {
			setStatusMsg('Error starting simulation');
		}
	};

	const handleStop = async () => {
		if (!simId) return;
		setStatusMsg('');
		try {
			const res = await fetch(`${API_BASE_URL}/api/simulation/stop?id=${simId}`, {
				method: 'GET',
				credentials: 'include',
			});
			const data = await res.json();
			setStatusMsg(data.status || 'Simulation stopped');
			await refreshAll();
		} catch {
			setStatusMsg('Error stopping simulation');
		}
	};

	const handleStartDefault = async () => {
		setStatusMsg('');
		try {
			const res = await fetch(`${API_BASE_URL}/api/simulation/start_default`, {
				method: 'GET',
				credentials: 'include',
			});
			const data = await res.json();
			if (data.id) setSimId(data.id);
			setStatusMsg(data.status || 'Simulation started');
			await refreshAll();
		} catch {
			setStatusMsg('Error starting default simulation');
		}
	};

	const handleUpdateTiming = async (e) => {
		e.preventDefault();
		if (!simId) return;
		setStatusMsg('');
		const csrftoken = getCookie('csrftoken') || '';
		const payload = { simulation_id: simId };
		if (baseTickMs !== '') payload.base_millis_per_tick = Number(baseTickMs);
		if (speedRatio !== '') payload.speed_ratio = Number(speedRatio);
		try {
			const res = await fetch(`${API_BASE_URL}/api/simulation/timing/update`, {
				method: 'POST',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': csrftoken,
				},
				body: JSON.stringify(payload),
			});
			const data = await res.json();
			if (!res.ok) {
				setStatusMsg(data.status || 'Error updating timing');
				return;
			}
			setTimingInfo(data.simulation || null);
			setStatusMsg(data.status || 'Timing updated');
			setBaseTickMs('');
			setSpeedRatio('');
		} catch {
			setStatusMsg('Error updating timing');
		}
	};

	const handleAddDevice = async (e) => {
		e.preventDefault();
		if (!simId) return;
		setStatusMsg('');
		const csrftoken = getCookie('csrftoken') || '';
		const extra = {};
		if (deviceType === 'lighting' || deviceType === 'airconditioning' || deviceType === 'heating') {
			if (extraPower) extra.power = Number(extraPower);
		}
		if (deviceType === 'lighting') {
			if (extraLightOutput) extra.light_output = Number(extraLightOutput);
		}
		if (deviceType === 'airconditioning') {
			if (extraCoolingPower) extra.cooling_power = Number(extraCoolingPower);
		}
		if (deviceType === 'photovoltaic') {
			if (extraPeakPower) extra.peak_power = Number(extraPeakPower);
		}
		if (deviceType === 'energystorage') {
			if (extraCapacity) extra.capacity = Number(extraCapacity);
			if (extraMaxCharge) extra.max_charge = Number(extraMaxCharge);
			if (extraMaxDischarge) extra.max_discharge = Number(extraMaxDischarge);
		}
		if (deviceType === 'electricgrid') {
			if (extraConnectionPower) extra.connection_power = Number(extraConnectionPower);
		}
		if (deviceType === 'heating') {
			if (extraStandbyPower) extra.standby_power = Number(extraStandbyPower);
		}
		if (deviceType === 'windturbine') {
			if (extraRatedPower) extra.rated_power = Number(extraRatedPower);
		}
		try {
			const res = await fetch(`${API_BASE_URL}/api/simulation/device/add`, {
				method: 'POST',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': csrftoken,
				},
				body: JSON.stringify({
					simulation_id: simId,
					name: deviceName,
					type: deviceType,
					weather_id: deviceWeatherId,
					...extra,
				}),
			});
			const data = await res.json();
			setStatusMsg(data.status || 'Device added');
			setDeviceName('');
			setExtraPower('');
			setExtraLightOutput('');
			setExtraCoolingPower('');
			setExtraPeakPower('');
			setExtraCapacity('');
			setExtraMaxCharge('');
			setExtraMaxDischarge('');
			setExtraConnectionPower('');
			setExtraStandbyPower('');
			setExtraRatedPower('');
			await refreshAll();
		} catch {
			setStatusMsg('Error adding device');
		}
	};

	const handleRemoveDevice = async (e) => {
		e.preventDefault();
		if (!simId || !removeDeviceId) return;
		setStatusMsg('');
		const csrftoken = getCookie('csrftoken') || '';
		try {
			const res = await fetch(`${API_BASE_URL}/api/simulation/device/remove/${removeDeviceId}?id=${simId}`, {
				method: 'DELETE',
				credentials: 'include',
				headers: { 'X-CSRFToken': csrftoken },
			});
			const data = await res.json();
			setStatusMsg(data.status || 'Device removed');
			setRemoveDeviceId('');
			await refreshAll();
		} catch {
			setStatusMsg('Error removing device');
		}
	};

	const handleAddWeather = async (e) => {
		e.preventDefault();
		if (!simId) return;
		setStatusMsg('');
		const csrftoken = getCookie('csrftoken') || '';
		try {
			const res = await fetch(`${API_BASE_URL}/api/simulation/weather/add`, {
				method: 'POST',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': csrftoken,
				},
				body: JSON.stringify({
					simulation_id: simId,
					name: weatherName,
					type: weatherType,
					outside_weather_id: weatherType === 'inside' ? weatherOutsideId : undefined,
				}),
			});
			const data = await res.json();
			setStatusMsg(data.status || 'Weather added');
			setWeatherName('');
			await refreshAll();
		} catch {
			setStatusMsg('Error adding weather');
		}
	};

	const handleRemoveWeather = async (e) => {
		e.preventDefault();
		if (!simId || !removeWeatherId) return;
		setStatusMsg('');
		const csrftoken = getCookie('csrftoken') || '';
		try {
			const res = await fetch(`${API_BASE_URL}/api/simulation/weather/remove/${removeWeatherId}?id=${simId}`, {
				method: 'DELETE',
				credentials: 'include',
				headers: { 'X-CSRFToken': csrftoken },
			});
			const data = await res.json();
			setStatusMsg(data.status || 'Weather removed');
			setRemoveWeatherId('');
			await refreshAll();
		} catch {
			setStatusMsg('Error removing weather');
		}
	};

	return (
		<div className="simulation-container">
			<div className="simulation-content">
				
				<div className="header-section">
					<h1 className="page-title">Simulation Control</h1>
					<p className="page-subtitle">Manage simulation, weather, and devices.</p>
				</div>

				<div className="simulation-grid" style={{ display: 'grid', gap: '2rem' }}>
					
					{/* Control Section */}
					<div className="data-card">
						<div className="card-header">
							<h2 className="card-title">Status & Control</h2>
							<span className="badge-count">ID: {simId || 'NONE'}</span>
						</div>
						<div style={{ padding: '2rem' }}>
							<div className="control-buttons" style={{ flexWrap: 'wrap', justifyContent: 'center' }}>
								<button 
									className={`btn-control btn-start ${!simId ? 'btn-disabled' : ''}`}
									onClick={handleStart} 
									disabled={!simId}
								>
									Start
								</button>
								<button 
									className={`btn-control btn-stop ${!simId ? 'btn-disabled' : ''}`}
									onClick={handleStop} 
									disabled={!simId}
								>
									Stop
								</button>
								<button 
									className="btn-control btn-secondary"
									onClick={handleStartDefault}
								>
									Start Default
								</button>
								<button 
									className={`btn-control btn-secondary ${!simId ? 'btn-disabled' : ''}`}
									onClick={refreshAll} 
									disabled={!simId}
								>
									Refresh
								</button>
							</div>
							
							{statusMsg && (
								<div className="notification-toast notification-success" style={{ position: 'relative', top: 'unset', right: 'unset', marginTop: '1rem' }}>
									<div className="notification-content">{statusMsg}</div>
								</div>
							)}
						</div>
					</div>

					{/* Timing Section */}
					<div className="data-card">
						<div className="card-header">
							<h2 className="card-title">Timing Configuration</h2>
						</div>
						<div style={{ padding: '2rem' }}>
							<div className="status-indicator-box" style={{ marginBottom: '2rem', justifyContent: 'space-around', width: '100%' }}>
								<div className="status-display">
									<span className="status-label">Base Tick:</span>
									<span className="font-mono">{timingInfo?.base_millis_per_tick ?? '—'} ms</span>
								</div>
								<div className="status-divider"></div>
								<div className="status-display">
									<span className="status-label">Sim Tick:</span>
									<span className="font-mono">{timingInfo?.simulated_millis_per_tick ?? '—'} ms</span>
								</div>
								<div className="status-divider"></div>
								<div className="status-display">
									<span className="status-label">Ratio:</span>
									<span className="font-mono">{timingInfo?.speed_ratio ?? '—'}</span>
								</div>
							</div>

							<form onSubmit={handleUpdateTiming} className="form-grid" style={{ marginBottom: 0 }}>
								<div className="form-group">
									<label className="form-label">Base tick (ms)</label>
									<input
										className="form-input"
										value={baseTickMs}
										onChange={(e) => setBaseTickMs(e.target.value)}
										placeholder="e.g. 60000"
									/>
								</div>
								<div className="form-group">
									<label className="form-label">Speed ratio</label>
									<input
										className="form-input"
										value={speedRatio}
										onChange={(e) => setSpeedRatio(e.target.value)}
										placeholder="e.g. 10"
									/>
								</div>
								<div className="form-actions" style={{ gridColumn: '1 / -1', borderTop: 'none', paddingTop: 0 }}>
									<button type="submit" className="btn-primary" disabled={!simId}>
										Update Timing
									</button>
								</div>
							</form>
						</div>
					</div>

					{/* Weather Section */}
					<div className="data-card">
						<div className="card-header">
							<h2 className="card-title">Weather Conditions</h2>
							<span className="badge-count">{weathers.length}</span>
						</div>
						
						<div className="rule-form">
							<form onSubmit={handleAddWeather} className="form-grid">
								<div className="form-group">
									<label className="form-label">Name</label>
									<input
										className="form-input"
										value={weatherName}
										onChange={(e) => setWeatherName(e.target.value)}
										placeholder="e.g. outside-1"
									/>
								</div>
								<div className="form-group">
									<label className="form-label">Type</label>
									<select
										className="form-select"
										value={weatherType}
										onChange={(e) => setWeatherType(e.target.value)}
									>
										<option value="outside">outside</option>
										<option value="inside">inside</option>
									</select>
								</div>
								
								{weatherType === 'inside' && (
									<div className="form-group">
										<label className="form-label">Outside reference</label>
										<select
											className="form-select"
											value={weatherOutsideId}
											onChange={(e) => setWeatherOutsideId(e.target.value)}
										>
											<option value="">Select outside weather</option>
											{weathers
												.filter(w => (w.type || '').toLowerCase().includes('outside'))
												.map(w => (
													<option key={w.uuid} value={w.uuid}>{w.name} ({w.uuid})</option>
												))}
										</select>
									</div>
								)}

								<div className="form-actions" style={{ gridColumn: '1 / -1', borderTop: 'none', paddingTop: 0 }}>
									<button type="submit" className="btn-primary" disabled={!simId}>
										Add Weather
									</button>
								</div>
							</form>
						</div>

						<div className="table-responsive">
							<table className="sensor-table">
								<thead>
									<tr>
										<th>Name</th>
										<th>Type</th>
										<th>UUID</th>
										<th className="text-right">Action</th>
									</tr>
								</thead>
								<tbody>
									{weathers.length === 0 ? (
										<tr><td colSpan="4" className="empty-state">No weather conditions defined.</td></tr>
									) : (
										weathers.map(w => (
											<tr key={w.uuid}>
												<td className="font-medium">{w.name}</td>
												<td><span className="badge-count" style={{ fontSize: '0.7em' }}>{w.type}</span></td>
												<td className="font-mono" style={{ fontSize: '0.8em' }}>{w.uuid}</td>
												<td className="text-right">
													<button 
														className="btn-ghost-danger"
														onClick={() => { setRemoveWeatherId(w.uuid); handleRemoveWeather({ preventDefault: () => {} }); }} // Hacky reuse of handler, ideally split it
													>
														Remove
													</button>
												</td>
											</tr>
										))
									)}
								</tbody>
							</table>
						</div>
					</div>

					{/* Devices Section */}
					<div className="data-card">
						<div className="card-header">
							<h2 className="card-title">Simulated Devices</h2>
							<span className="badge-count">{devices.length}</span>
						</div>

						<div className="rule-form">
							<form onSubmit={handleAddDevice} className="form-grid">
								<div className="form-group">
									<label className="form-label">Name</label>
									<input
										className="form-input"
										value={deviceName}
										onChange={(e) => setDeviceName(e.target.value)}
										placeholder="e.g. lamp-1"
									/>
								</div>
								<div className="form-group">
									<label className="form-label">Type</label>
									<select
										className="form-select"
										value={deviceType}
										onChange={(e) => setDeviceType(e.target.value)}
									>
										<option value="lighting">lighting</option>
										<option value="airconditioning">airconditioning</option>
										<option value="photovoltaic">photovoltaic</option>
										<option value="energystorage">energystorage</option>
										<option value="electricgrid">electricgrid</option>
										<option value="heating">heating</option>
										<option value="windturbine">windturbine</option>
									</select>
								</div>
								
								{/* Dynamic Fields based on Type */}
								{(deviceType === 'lighting' || deviceType === 'airconditioning' || deviceType === 'heating') && (
									<div className="form-group">
										<label className="form-label">Power (W)</label>
										<input className="form-input" value={extraPower} onChange={(e) => setExtraPower(e.target.value)} placeholder="e.g. 1500" />
									</div>
								)}
								{deviceType === 'lighting' && (
									<div className="form-group">
										<label className="form-label">Light output</label>
										<input className="form-input" value={extraLightOutput} onChange={(e) => setExtraLightOutput(e.target.value)} placeholder="e.g. 1" />
									</div>
								)}
								{deviceType === 'airconditioning' && (
									<div className="form-group">
										<label className="form-label">Cooling power</label>
										<input className="form-input" value={extraCoolingPower} onChange={(e) => setExtraCoolingPower(e.target.value)} placeholder="e.g. 100" />
									</div>
								)}
								{deviceType === 'photovoltaic' && (
									<div className="form-group">
										<label className="form-label">Peak power</label>
										<input className="form-input" value={extraPeakPower} onChange={(e) => setExtraPeakPower(e.target.value)} placeholder="e.g. 8000" />
									</div>
								)}
								{deviceType === 'energystorage' && (
									<>
										<div className="form-group"><label className="form-label">Capacity</label><input className="form-input" value={extraCapacity} onChange={(e) => setExtraCapacity(e.target.value)} placeholder="e.g. 150000" /></div>
										<div className="form-group"><label className="form-label">Max charge</label><input className="form-input" value={extraMaxCharge} onChange={(e) => setExtraMaxCharge(e.target.value)} placeholder="e.g. 8000" /></div>
										<div className="form-group"><label className="form-label">Max discharge</label><input className="form-input" value={extraMaxDischarge} onChange={(e) => setExtraMaxDischarge(e.target.value)} placeholder="e.g. 5000" /></div>
									</>
								)}
								{deviceType === 'electricgrid' && (
									<div className="form-group">
										<label className="form-label">Connection power</label>
										<input className="form-input" value={extraConnectionPower} onChange={(e) => setExtraConnectionPower(e.target.value)} placeholder="e.g. 4000" />
									</div>
								)}
								{deviceType === 'heating' && (
									<div className="form-group">
										<label className="form-label">Standby power</label>
										<input className="form-input" value={extraStandbyPower} onChange={(e) => setExtraStandbyPower(e.target.value)} placeholder="e.g. 50" />
									</div>
								)}
								{deviceType === 'windturbine' && (
									<div className="form-group">
										<label className="form-label">Rated power</label>
										<input className="form-input" value={extraRatedPower} onChange={(e) => setExtraRatedPower(e.target.value)} placeholder="e.g. 3000" />
									</div>
								)}

								<div className="form-group">
									<label className="form-label">Weather</label>
									<select
										className="form-select"
										value={deviceWeatherId}
										onChange={(e) => setDeviceWeatherId(e.target.value)}
									>
										<option value="">Select weather</option>
										{weathers.map(w => (
											<option key={w.uuid} value={w.uuid}>{w.name} ({w.uuid})</option>
										))}
									</select>
								</div>

								<div className="form-actions" style={{ gridColumn: '1 / -1', borderTop: 'none', paddingTop: 0 }}>
									<button type="submit" className="btn-primary" disabled={!simId}>
										Add Device
									</button>
								</div>
							</form>
						</div>

						<div className="table-responsive">
							<table className="sensor-table">
								<thead>
									<tr>
										<th>Name</th>
										<th>Type</th>
										<th>UUID</th>
										<th className="text-right">Action</th>
									</tr>
								</thead>
								<tbody>
									{devices.length === 0 ? (
										<tr><td colSpan="4" className="empty-state">No devices added.</td></tr>
									) : (
										devices.map(d => (
											<tr key={d.uuid}>
												<td className="font-medium">{d.name}</td>
												<td><span className="badge-count" style={{ fontSize: '0.7em' }}>{d.type}</span></td>
												<td className="font-mono" style={{ fontSize: '0.8em' }}>{d.uuid}</td>
												<td className="text-right">
													<button 
														className="btn-ghost-danger"
														onClick={() => { setRemoveDeviceId(d.uuid); handleRemoveDevice({ preventDefault: () => {} }); }}
													>
														Remove
													</button>
												</td>
											</tr>
										))
									)}
								</tbody>
							</table>
						</div>
					</div>

				</div>
			</div>
		</div>
	);
};

export default SimulationPage;
