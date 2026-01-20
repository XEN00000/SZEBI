import React, { useState, useEffect } from 'react';
import { Activity, Zap, BarChart3, Lock, CheckCircle, AlertCircle } from 'lucide-react';
import { getCookie } from '../../utils/csrf';

const API_BASE_URL = 'http://localhost:8000';

const OptimizationHistory = ({ notification, setNotification, userRole, refreshKey }) => {
    const [running, setRunning] = useState(false);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchHistory();
    }, [refreshKey]);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/optimization/logs/`, {
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to fetch history');

            const data = await response.json();
            const logs = Array.isArray(data) ? data : data.results || [];
            setHistory(logs);
        } catch (error) {
            console.error('Error fetching history:', error);
        } finally {
            setLoading(false);
        }
    };

    const runOptimization = async () => {
        setRunning(true);
        try {
            const csrftoken = getCookie('csrftoken');
            const response = await fetch(`${API_BASE_URL}/api/optimization/run/`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            });

            if (!response.ok) throw new Error('Failed to run optimization');
            const data = await response.json();
            setNotification({ 
                type: 'success', 
                message: 'Cykl optymalizacji uruchomiony pomyślnie.' 
            });
            
            // Pobierz zaktualizowaną historię
            setTimeout(() => fetchHistory(), 1000);
        } catch (error) {
            console.error('Error running optimization:', error);
            setNotification({ type: 'error', message: 'Nie udało się uruchomić optymalizacji.' });
        } finally {
            setRunning(false);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    const isAdmin = userRole === 'building_admin';

    const getStatusIcon = (status) => {
        if (status === 'success') return <CheckCircle size={16} />;
        if (status === 'failed') return <AlertCircle size={16} />;
        return <Activity size={16} />;
    };

    const formatDate = (timestamp) => {
        const date = new Date(timestamp);
        return date.toLocaleString('pl-PL');
    };

    return (
        <div className="optimization-history">
            <div className="history-header">
                <h3>
                    <BarChart3 size={20} />
                    Kontrola optymalizacji
                </h3>
            </div>

            {!isAdmin && (
                <div className="admin-only-notice">
                    <Lock size={16} />
                    <span>Tylko administrator może uruchomić cykl optymalizacji</span>
                </div>
            )}

            <div className="control-section-opt">
                <button
                    onClick={runOptimization}
                    disabled={running || !isAdmin}
                    className="btn-run-optimization"
                    title={!isAdmin ? "Tylko administrator może uruchomić optymalizację" : ""}
                >
                    <Activity size={18} />
                    {running ? 'Uruchamianie...' : 'Uruchom cykl optymalizacji'}
                </button>
                <p className="control-hint">{isAdmin ? 'Ręcznie uruchom cykl optymalizacji teraz' : 'Kontakt z administratorem wymagany'}</p>
            </div>

            <div className="history-section">
                <h4>Historia operacji ({history.length})</h4>
                {loading ? (
                    <div className="loading-message">Ładowanie historii...</div>
                ) : history.length === 0 ? (
                    <div className="empty-message">Brak historii. Uruchom cykl aby zobaczyć wyniki.</div>
                ) : (
                    <div className="history-list">
                        {history.slice(0, 10).map((entry, idx) => (
                            <div key={idx} className={`history-item history-${entry.status}`}>
                                <div className="history-status">
                                    {getStatusIcon(entry.status)}
                                    <span className="status-badge">{entry.status_display}</span>
                                </div>
                                <div className="history-content">
                                    <div className="history-action">{entry.action}</div>
                                    <div className="history-message">{entry.message}</div>
                                    {entry.affected_devices_count > 0 && (
                                        <div className="history-devices">Dotyczyło {entry.affected_devices_count} urządzeń</div>
                                    )}
                                </div>
                                <div className="history-time">{formatDate(entry.timestamp)}</div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default OptimizationHistory;
