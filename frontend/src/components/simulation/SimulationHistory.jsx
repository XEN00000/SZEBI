import React, { useEffect, useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const SimulationHistory = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        fetch(`${API_BASE_URL}/api/simulation/history/`, {
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        })
            .then(res => {
                if (!res.ok) throw new Error('Błąd pobierania historii');
                return res.json();
            })
            .then(data => setHistory(data))
            .catch(() => setError('Nie udało się pobrać historii.'))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div>Ładowanie historii...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Historia symulacji</h3>
            {history.length > 0 ? (
                <ul className="list-disc ml-6">
                    {history.map(sim => (
                        <li key={sim.id}>
                            {sim.name} ({sim.date})
                        </li>
                    ))}
                </ul>
            ) : (
                <div>Brak przeprowadzonych symulacji.</div>
            )}
        </div>
    );
};

export default SimulationHistory;