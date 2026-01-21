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
		<div style={{ padding: 16, maxWidth: 1000, margin: '0 auto' }}>
			<h1 style={{ marginBottom: 8 }}>Simulation</h1>
			<div style={{ marginBottom: 16, fontSize: 14, opacity: 0.8 }}>
				Manage simulation, weather, and devices.
			</div>

			<div style={{ display: 'grid', gap: 12, gridTemplateColumns: '1fr' }}>
				<section style={{ border: '1px solid #ddd', padding: 12, borderRadius: 6 }}>
					<h2 style={{ marginTop: 0 }}>Simulation Control</h2>
					<div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
						<button onClick={handleStart} disabled={!simId}>Start</button>
						<button onClick={handleStop} disabled={!simId}>Stop</button>
						<button onClick={handleStartDefault}>Start Default</button>
						<button onClick={refreshAll} disabled={!simId}>Refresh</button>
					</div>
					<div style={{ marginTop: 8, fontSize: 13 }}>
						<strong>ID:</strong> {simId || '...'}
					</div>
				</section>

				<section style={{ border: '1px solid #ddd', padding: 12, borderRadius: 6 }}>
					<h2 style={{ marginTop: 0 }}>Timing</h2>
					<div style={{ fontSize: 13, marginBottom: 8 }}>
						<div><strong>Base tick:</strong> {timingInfo?.base_millis_per_tick ?? '—'} ms</div>
						<div><strong>Simulated tick:</strong> {timingInfo?.simulated_millis_per_tick ?? '—'} ms</div>
						<div><strong>Speed ratio (base/simulated):</strong> {timingInfo?.speed_ratio ?? '—'}</div>
					</div>
					<form onSubmit={handleUpdateTiming} style={{ display: 'grid', gap: 8 }}>
						<label>
							Base tick (ms)
							<input
								style={{ display: 'block', width: '100%', marginTop: 4 }}
								value={baseTickMs}
								onChange={(e) => setBaseTickMs(e.target.value)}
								placeholder="e.g. 60000"
							/>
						</label>
						<label>
							Speed ratio (base/simulated)
							<input
								style={{ display: 'block', width: '100%', marginTop: 4 }}
								value={speedRatio}
								onChange={(e) => setSpeedRatio(e.target.value)}
								placeholder="e.g. 10"
							/>
						</label>
						<button type="submit" disabled={!simId}>
							Update Timing
						</button>
					</form>
				</section>

				<section style={{ border: '1px solid #ddd', padding: 12, borderRadius: 6 }}>
					<h2 style={{ marginTop: 0 }}>Weather</h2>
					<form onSubmit={handleAddWeather} style={{ display: 'grid', gap: 8 }}>
						<label>
							Name
							<input
								style={{ display: 'block', width: '100%', marginTop: 4 }}
								value={weatherName}
								onChange={(e) => setWeatherName(e.target.value)}
								placeholder="e.g. outside-1"
							/>
						</label>
						<label>
							Type
							<select
								style={{ display: 'block', width: '100%', marginTop: 4 }}
								value={weatherType}
								onChange={(e) => setWeatherType(e.target.value)}
							>
								<option value="outside">outside</option>
								<option value="inside">inside</option>
							</select>
						</label>
						<label>
							Outside reference
							<select
								style={{ display: 'block', width: '100%', marginTop: 4 }}
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
						</label>
						<button type="submit" disabled={!simId}>
							Add Weather
						</button>
					</form>

					<div style={{ marginTop: 12 }}>
						<strong>Existing Weathers</strong>
						<ul style={{ paddingLeft: 16 }}>
							{weathers.map(w => (
								<li key={w.uuid}>{w.name} — {w.type} — {w.uuid}</li>
							))}
						</ul>
					</div>

					<form onSubmit={handleRemoveWeather} style={{ marginTop: 8 }}>
						<label>
							Remove weather
							<select
								style={{ display: 'block', width: '100%', marginTop: 4 }}
								value={removeWeatherId}
								onChange={(e) => setRemoveWeatherId(e.target.value)}
							>
								<option value="">Select weather</option>
								{weathers.map(w => (
									<option key={w.uuid} value={w.uuid}>{w.name} ({w.uuid})</option>
								))}
							</select>
						</label>
						<button type="submit" disabled={!simId || !removeWeatherId} style={{ marginTop: 8 }}>
							Remove Weather
						</button>
					</form>
				</section>

				<section style={{ border: '1px solid #ddd', padding: 12, borderRadius: 6 }}>
					<h2 style={{ marginTop: 0 }}>Devices</h2>
					<form onSubmit={handleAddDevice} style={{ display: 'grid', gap: 8 }}>
						<label>
							Name
							<input
								style={{ display: 'block', width: '100%', marginTop: 4 }}
								value={deviceName}
								onChange={(e) => setDeviceName(e.target.value)}
								placeholder="e.g. lamp-1"
							/>
						</label>
						<label>
							Type
							<select
								style={{ display: 'block', width: '100%', marginTop: 4 }}
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
						</label>
						{(deviceType === 'lighting' || deviceType === 'airconditioning' || deviceType === 'heating') && (
							<label>
								Power (W)
								<input
									style={{ display: 'block', width: '100%', marginTop: 4 }}
									value={extraPower}
									onChange={(e) => setExtraPower(e.target.value)}
									placeholder="e.g. 1500"
								/>
							</label>
						)}
						{deviceType === 'lighting' && (
							<label>
								Light output
								<input
									style={{ display: 'block', width: '100%', marginTop: 4 }}
									value={extraLightOutput}
									onChange={(e) => setExtraLightOutput(e.target.value)}
									placeholder="e.g. 1"
								/>
							</label>
						)}
						{deviceType === 'airconditioning' && (
							<label>
								Cooling power
								<input
									style={{ display: 'block', width: '100%', marginTop: 4 }}
									value={extraCoolingPower}
									onChange={(e) => setExtraCoolingPower(e.target.value)}
									placeholder="e.g. 100"
								/>
							</label>
						)}
						{deviceType === 'photovoltaic' && (
							<label>
								Peak power
								<input
									style={{ display: 'block', width: '100%', marginTop: 4 }}
									value={extraPeakPower}
									onChange={(e) => setExtraPeakPower(e.target.value)}
									placeholder="e.g. 8000"
								/>
							</label>
						)}
						{deviceType === 'energystorage' && (
							<>
								<label>
									Capacity
									<input
										style={{ display: 'block', width: '100%', marginTop: 4 }}
										value={extraCapacity}
										onChange={(e) => setExtraCapacity(e.target.value)}
										placeholder="e.g. 150000"
									/>
								</label>
								<label>
									Max charge
									<input
										style={{ display: 'block', width: '100%', marginTop: 4 }}
										value={extraMaxCharge}
										onChange={(e) => setExtraMaxCharge(e.target.value)}
										placeholder="e.g. 8000"
									/>
								</label>
								<label>
									Max discharge
									<input
										style={{ display: 'block', width: '100%', marginTop: 4 }}
										value={extraMaxDischarge}
										onChange={(e) => setExtraMaxDischarge(e.target.value)}
										placeholder="e.g. 5000"
									/>
								</label>
							</>
						)}
						{deviceType === 'electricgrid' && (
							<label>
								Connection power
								<input
									style={{ display: 'block', width: '100%', marginTop: 4 }}
									value={extraConnectionPower}
									onChange={(e) => setExtraConnectionPower(e.target.value)}
									placeholder="e.g. 4000"
								/>
							</label>
						)}
						{deviceType === 'heating' && (
							<label>
								Standby power
								<input
									style={{ display: 'block', width: '100%', marginTop: 4 }}
									value={extraStandbyPower}
									onChange={(e) => setExtraStandbyPower(e.target.value)}
									placeholder="e.g. 50"
								/>
							</label>
						)}
						{deviceType === 'windturbine' && (
							<label>
								Rated power
								<input
									style={{ display: 'block', width: '100%', marginTop: 4 }}
									value={extraRatedPower}
									onChange={(e) => setExtraRatedPower(e.target.value)}
									placeholder="e.g. 3000"
								/>
							</label>
						)}
						<label>
							Weather
							<select
								style={{ display: 'block', width: '100%', marginTop: 4 }}
								value={deviceWeatherId}
								onChange={(e) => setDeviceWeatherId(e.target.value)}
							>
								<option value="">Select weather</option>
								{weathers.map(w => (
									<option key={w.uuid} value={w.uuid}>{w.name} ({w.uuid})</option>
								))}
							</select>
						</label>
						<button type="submit" disabled={!simId}>
							Add Device
						</button>
					</form>

					<div style={{ marginTop: 12 }}>
						<strong>Existing Devices</strong>
						<ul style={{ paddingLeft: 16 }}>
							{devices.map(d => (
								<li key={d.uuid}>{d.name} — {d.type} — {d.uuid}</li>
							))}
						</ul>
					</div>

					<form onSubmit={handleRemoveDevice} style={{ marginTop: 8 }}>
						<label>
							Remove device
							<select
								style={{ display: 'block', width: '100%', marginTop: 4 }}
								value={removeDeviceId}
								onChange={(e) => setRemoveDeviceId(e.target.value)}
							>
								<option value="">Select device</option>
								{devices.map(d => (
									<option key={d.uuid} value={d.uuid}>{d.name} ({d.uuid})</option>
								))}
							</select>
						</label>
						<button type="submit" disabled={!simId || !removeDeviceId} style={{ marginTop: 8 }}>
							Remove Device
						</button>
					</form>
				</section>
			</div>

			{statusMsg && (
				<div style={{ marginTop: 12, padding: 8, border: '1px solid #ccc', borderRadius: 4 }}>
					{statusMsg}
				</div>
			)}
		</div>
	);
};

export default SimulationPage;
