import React, { useState, useEffect } from 'react';
import { getCookie } from '../utils/csrf';

const API_URL = 'http://localhost:8000';

const AcquisitionPage = () => {
  const [status, setStatus] = useState({ running: false, status_text: 'Ładowanie...' });
  const [stats, setStats] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const fetchData = async () => {
    try {
      const resStatus = await fetch(`${API_URL}/acquisition/api/status/`, { credentials: 'include' });
      const dataStatus = await resStatus.json();
      setStatus(dataStatus);

      const resStats = await fetch(`${API_URL}/acquisition/api/stats/`, { credentials: 'include' });
      const dataStats = await resStats.json();
      if (dataStats.stats) setStats(dataStats.stats);

      const resLogs = await fetch(`${API_URL}/acquisition/api/logs/?level=ERROR`, { credentials: 'include' });
      const dataLogs = await resLogs.json();
      if (dataLogs.logs) setLogs(dataLogs.logs);

      setErrorMsg(null);
    } catch (err) {
      console.error("Błąd pobierania danych:", err);
      if (status.status_text === 'Ładowanie...') {
          setErrorMsg("Brak połączenia z serwerem");
      }
    }
  };

  const handleControl = async (action) => {
    setLoading(true);
    try {
      const csrftoken = getCookie('csrftoken') || '';
      const response = await fetch(`${API_URL}/acquisition/api/status/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        credentials: 'include',
        body: JSON.stringify({ action }),
      });
      const data = await response.json();
      if (data.success) fetchData();
    } catch (error) {
      alert('Błąd komunikacji');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const formatDate = (isoString) => {
    if (!isoString) return '-';
    return new Date(isoString).toLocaleString('pl-PL');
  };

  return (
    <div className="acquisition-container">
      <div className="acquisition-content">

        <div className="header-section">
            <h1 className="page-title">Panel Akwizycji Danych</h1>
            <p className="page-subtitle">Zarządzanie procesem MQTT i monitoring urządzeń</p>

            <div className="status-card">
                <div className="status-indicator-box">
                    <span className="status-label">Status Usługi</span>
                    <div className="status-divider"></div>
                    <div className="status-display">
                        <div className={`status-led ${status.running ? 'led-active' : 'led-inactive'}`}>
                           <div className="led-reflection"></div>
                        </div>
                        <span className={`status-text ${status.running ? 'text-active' : 'text-inactive'}`}>
                            {status.running ? 'AKTYWNY' : 'NIEAKTYWNY'}
                        </span>
                    </div>
                </div>

                <div className="control-buttons">
                    <button
                        onClick={() => handleControl('start')}
                        disabled={status.running || loading}
                        className={`btn-control btn-start ${status.running ? 'btn-disabled' : ''}`}
                    >
                        Uruchom System
                    </button>

                    <button
                        onClick={() => handleControl('stop')}
                        disabled={!status.running || loading}
                        className={`btn-control btn-stop ${!status.running ? 'btn-disabled' : ''}`}
                    >
                        Zatrzymaj System
                    </button>
                </div>
            </div>
        </div>

        {errorMsg && (
            <div className="error-banner">
                {errorMsg}
            </div>
        )}

        <div className="data-card">
            <div className="card-header">
                <h2 className="card-title">Podłączone Urządzenia</h2>
                <span className="badge-count">TOTAL: {stats.length}</span>
            </div>

            <div className="table-responsive">
                <table className="sensor-table">
                    <thead>
                        <tr>
                            <th>Nazwa Sensora</th>
                            <th className="text-center">Stan</th>
                            <th className="text-right">Liczba Pomiarów</th>
                            <th className="text-right">Ostatnia Aktywność</th>
                        </tr>
                    </thead>
                    <tbody>
                        {stats.length === 0 ? (
                            <tr>
                                <td colSpan="4" className="empty-state">
                                    Brak danych. System oczekuje na pakiety MQTT.
                                </td>
                            </tr>
                        ) : stats.map((sensor, idx) => (
                            <tr key={idx}>
                                <td className="font-medium">{sensor.sensor_name}</td>
                                <td className="text-center">
                                    <span className={`status-dot ${['ACTIVE', 'ON'].includes(sensor.status) ? 'bg-green' : 'bg-gray'}`}></span>
                                    {sensor.status}
                                </td>
                                <td className="text-right font-mono">{sensor.total_measurements.toLocaleString()}</td>
                                <td className="text-right text-muted">{formatDate(sensor.last_seen)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>

        <div className="data-card">
            <div className="card-header">
                <h2 className="card-title">Dziennik Błędów</h2>
            </div>

            <div className="logs-container">
                {logs.length === 0 ? (
                    <div className="empty-state">Brak błędów w rejestrze.</div>
                ) : (
                    <ul className="logs-list">
                        {logs.map((log) => (
                            <li key={log.id} className="log-item">
                                <div className="log-header">
                                    <span className="badge-error">{log.level}</span>
                                    <span className="log-time">{new Date(log.timestamp).toLocaleString()}</span>
                                </div>
                                <p className="log-message">{log.message}</p>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>

      </div>
    </div>
  );
};

export default AcquisitionPage;