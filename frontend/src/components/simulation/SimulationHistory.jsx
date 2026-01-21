import React, { useEffect, useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const SimulationHistory = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        fetch(`${API_BASE_URL}/api/simulation/history`, {
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        })
            .then(res => {
                if (!res.ok) throw new Error('Error fetching history');
                return res.json();
            })
            .then(data => setHistory(data))
            .catch(() => setError('Failed to fetch history.'))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div>Loading history...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div className="data-card mt-6" style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
            <div className="card-header" style={{ backgroundColor: 'rgba(255, 255, 255, 0.01)' }}>
                <h2 className="card-title">Simulation History</h2>
            </div>

            <div className="logs-container">
                {history.length > 0 ? (
                    <ul className="logs-list">
                        {history.map(sim => (
                            <li key={sim.id} className="log-item">
                                <div className="log-header">
                                    <span className="badge-count" style={{ borderRadius: '0.375rem' }}>
                                        {sim.name}
                                    </span>
                                    <span className="log-time">{sim.date}</span>
                                </div>
                                <p className="log-message text-sm text-gray-400">
                                    Simulation ID: <span className="font-mono text-white">{sim.id}</span>
                                </p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <div className="empty-state">
                        No simulation history found.
                    </div>
                )}
            </div>
        </div>
    );
};

export default SimulationHistory;