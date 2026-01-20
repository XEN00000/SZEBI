import React, { useEffect, useState } from 'react';
import { Activity, Zap, AlertCircle, TrendingUp } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

const DashboardOptimization = ({ refreshKey }) => {
    const [devices, setDevices] = useState([]);
    const [stats, setStats] = useState({
        total_devices: 0,
        active_preferences: 0,
        recent_optimizations: 0
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchDashboardData();
        const interval = setInterval(fetchDashboardData, 5000); // odświeża co 5 sekund
        return () => clearInterval(interval);
    }, [refreshKey]);

    const fetchDashboardData = async () => {
        setLoading(true);
        try {
            const [devicesRes, prefsRes, logsRes] = await Promise.all([
                fetch(`${API_BASE_URL}/api/optimization/devices/`, {
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' }
                }),
                fetch(`${API_BASE_URL}/api/optimization/preferences/`, {
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' }
                }),
                fetch(`${API_BASE_URL}/api/optimization/logs/`, {
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' }
                })
            ]);

            let devicesList = [];
            if (devicesRes.ok) {
                const devicesData = await devicesRes.json();
                devicesList = Array.isArray(devicesData) ? devicesData : devicesData.results || [];
                setDevices(devicesList);
            }

            let activePreferences = 0;
            if (prefsRes.ok) {
                const prefsData = await prefsRes.json();
                const prefsList = Array.isArray(prefsData) ? prefsData : prefsData.results || [];
                activePreferences = prefsList.filter(p => p.is_active).length;
            }

            let recentOptimizations = 0;
            if (logsRes.ok) {
                const logsData = await logsRes.json();
                const logsList = Array.isArray(logsData) ? logsData : logsData.results || [];
                recentOptimizations = logsList.filter(l => l.status === 'success').length;
            }
            
            setStats({
                total_devices: devicesList.length,
                active_preferences: activePreferences,
                recent_optimizations: recentOptimizations
            });
            setError(null);
        } catch (err) {
            console.error('Error fetching dashboard data:', err);
            setError('Nie udało się pobrać danych.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard-optimization">
            <div className="dashboard-header">
                <h2 className="dashboard-title">
                    <TrendingUp size={24} />
                    Przegląd Optymalizacji
                </h2>
                <button 
                    onClick={fetchDashboardData}
                    className="btn-refresh"
                    disabled={loading}
                >
                    {loading ? 'Ładowanie...' : 'Odśwież'}
                </button>
            </div>

            {error && (
                <div className="error-message">
                    <AlertCircle size={20} />
                    <span>{error}</span>
                </div>
            )}

            <div className="stats-grid-opt">
                <div className="stat-card-opt">
                    <div className="stat-icon stat-icon-blue">
                        <Zap size={24} />
                    </div>
                    <div className="stat-content">
                        <p className="stat-label">Urządzenia aktywne</p>
                        <p className="stat-value">{devices.length}</p>
                    </div>
                </div>

                <div className="stat-card-opt">
                    <div className="stat-icon stat-icon-amber">
                        <Activity size={24} />
                    </div>
                    <div className="stat-content">
                        <p className="stat-label">Aktywne preferencje</p>
                        <p className="stat-value">{stats.active_preferences}</p>
                    </div>
                </div>

                <div className="stat-card-opt">
                    <div className="stat-icon stat-icon-emerald">
                        <TrendingUp size={24} />
                    </div>
                    <div className="stat-content">
                        <p className="stat-label">Ostatnie optymalizacje</p>
                        <p className="stat-value">{stats.recent_optimizations}</p>
                    </div>
                </div>
            </div>

            <div className="devices-section-opt">
                <h3 className="section-title">Urządzenia</h3>
                {loading ? (
                    <div className="loading-message">Ładowanie urządzeń...</div>
                ) : devices.length === 0 ? (
                    <div className="empty-message">Brak dostępnych urządzeń</div>
                ) : (
                    <div className="devices-grid-opt">
                        {devices.map((device) => (
                            <div key={device.id} className="device-card-opt">
                                <div className="device-header-opt">
                                    <h4 className="device-name">{device.name}</h4>
                                    <span className={`device-status ${device.is_active ? 'status-active' : 'status-inactive'}`}>
                                        {device.is_active ? 'Aktywne' : 'Nieaktywne'}
                                    </span>
                                </div>
                                <div className="device-info-opt">
                                    <p><span className="info-label">Typ:</span> {device.device_type}</p>
                                    <p><span className="info-label">Moc nominalna:</span> {device.nominal_power} W</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DashboardOptimization;
