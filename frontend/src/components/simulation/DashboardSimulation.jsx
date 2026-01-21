import React, { useEffect, useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const DashboardSimulation = ({ refreshKey }) => {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        fetch(`${API_BASE_URL}/api/simulation/summary/`, {
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

    if (loading) return <div>Ładowanie podsumowania...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">Panel symulacji</h2>
            {summary ? (
                <div>
                    <div>Liczba symulacji: {summary.total_simulations}</div>
                    <div>Ostatnia symulacja: {summary.last_simulation_date}</div>
                    {/* Dodaj więcej pól według potrzeb */}
                </div>
            ) : (
                <div>Brak danych do wyświetlenia.</div>
            )}
        </div>
    );
};

export default DashboardSimulation;