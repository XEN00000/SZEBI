import React, { useEffect, useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const DashboardSimulation = ({ refreshKey }) => {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        fetch(`${API_BASE_URL}/api/simulation/summary`, {
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        })
            .then(res => {
                if (!res.ok) throw new Error('Błąd pobierania podsumowania');
                return res.json();
            })
            .then(data => setSummary(data))
            .catch(() => setError('Nie udało się pobrać podsumowania.'))
            .finally(() => setLoading(false));
    }, [refreshKey]);

    const formatDate = (dateStr) => {
        if (!dateStr) return '-';
        return new Date(dateStr).toLocaleString('pl-PL');
    };

    if (loading) return (
         <div className="status-card h-32 flex items-center justify-center">
            <span className="text-secondary animate-pulse">Ładowanie podsumowania...</span>
         </div>
    );

    if (error) return (
        <div className="status-card h-32 flex items-center justify-center">
            <span className="text-red-500">{error}</span>
        </div>
    );

    return (
        <div className="status-card flex-row justify-between items-stretch gap-8">
            <div className="status-indicator-box flex-1 justify-between">
                <span className="status-label">Liczba Symulacji</span>
                <div className="status-divider"></div>
                <div className="status-display">
                     <span className="stat-value text-3xl font-bold text-active">
                        {summary ? summary.total_simulations : 0}
                     </span>
                </div>
            </div>

            <div className="status-indicator-box flex-1 justify-between">
                <span className="status-label">Ostatnia Aktywność</span>
                <div className="status-divider"></div>
                <div className="status-display">
                    <span className="status-text text-white font-mono text-sm">
                        {summary ? formatDate(summary.last_simulation_date) : '-'}
                    </span>
                </div>
            </div>
        </div>
    );
};

export default DashboardSimulation;