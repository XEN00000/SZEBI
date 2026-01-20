import React, { useState, useEffect, useCallback } from 'react';
import { TrendingUp, Calendar, Zap, Sun, Loader2, RefreshCw, AlertCircle, Cpu, FileText, Play } from 'lucide-react';

const ROLES = {
    ADMIN: 'building_admin',
    MAINTENANCE: 'maintenance_engineer',
};

const Forecasting = ({ user }) => {
    const [forecasts, setForecasts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [statusMessage, setStatusMessage] = useState(null);
    const [error, setError] = useState(null);

    // Pobieranie danych tylko dla Administratora
    const fetchLatestForecast = useCallback(async () => {
        if (user.role !== ROLES.ADMIN) return;

        setLoading(true);
        setError(null);
        try {
            const response = await fetch('http://localhost:8000/api/forecasting/latest/');
            if (response.ok) {
                const data = await response.json();
                setForecasts(data);
            }
        } catch (err) {
            console.error("Błąd pobierania danych:", err);
        } finally {
            setLoading(false);
        }
    }, [user.role]);

    useEffect(() => {
        fetchLatestForecast();
    }, [fetchLatestForecast]);

    const handleTrainModels = async () => {
        setIsProcessing(true);
        setStatusMessage("Inżynier: Trwa przygotowanie danych historycznych i trenowanie modeli...");
        setError(null);
        try {
            const response = await fetch('http://localhost:8000/api/forecasting/train/', { method: 'POST' });
            if (response.ok) {
                setStatusMessage("Sukces: Modele XGBoost, RF i LSTM zostały wytrenowane i zwalidowane.");
            } else {
                setError("Błąd podczas cyklu treningowego.");
            }
        } catch (err) {
            setError("Błąd komunikacji podczas treningu.");
        } finally {
            setIsProcessing(false);
        }
    };

    const handleGenerateForecast = async () => {
        setIsProcessing(true);
        setStatusMessage("Administrator: PredictionManager generuje nową prognozę...");
        setError(null);
        try {
            const response = await fetch('http://localhost:8000/api/forecasting/generate/', { method: 'POST' });
            if (response.ok) {
                setStatusMessage("Sukces: Nowa prognoza została wygenerowana i zapisana w bazie.");
                await fetchLatestForecast();
            }
        } catch (err) {
            setError("Błąd połączenia podczas generowania.");
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="home-container" style={{ gap: '2rem' }}>
            <div className="hero-section" style={{ overflow: 'visible' }}>
                <h2 className="hero-title" style={{ fontSize: '1.875rem', textAlign: 'left', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <TrendingUp className="text-cyan-500" style={{ color: 'var(--primary-color)' }} />
                    Moduł Prognozowania Energii
                </h2>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>

                {/* PANEL INŻYNIERA - Tylko dla MAINTENANCE */}
                {user.role === ROLES.MAINTENANCE && (
                    <div style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', borderRadius: '1rem', border: '1px solid var(--border-color)', gridColumn: '1 / -1' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                            <Cpu className="text-blue-400" size={24} />
                            <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#60a5fa' }}>Panel Inżyniera Utrzymania Ruchu</h3>
                        </div>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                            Zgodnie z procedurą: System pobierze dane historyczne, przeprowadzi trening XGBoost, RF, LSTM i wybierze model z najniższym MAPE.
                        </p>
                        <button onClick={handleTrainModels} disabled={isProcessing} className="login-btn" style={{ width: 'fit-content', padding: '0.75rem 2rem', marginTop: 0, backgroundColor: '#2563eb' }}>
                            {isProcessing ? <Loader2 className="animate-spin" /> : <><RefreshCw size={18} /> Ręczne trenowanie modeli</>}
                        </button>
                    </div>
                )}

                {/* PANEL ADMINISTRATORA - Tylko dla ADMIN */}
                {user.role === ROLES.ADMIN && (
                    <div style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', borderRadius: '1rem', border: '1px solid var(--border-color)', gridColumn: '1 / -1' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                            <FileText className="text-emerald-400" size={24} />
                            <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#34d399' }}>Panel Administratora Budynku</h3>
                        </div>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                            Generowanie serii danych prognozy na podstawie aktualnie aktywnych modeli w repozytorium.
                        </p>
                        <button onClick={handleGenerateForecast} disabled={isProcessing} className="login-btn" style={{ width: 'fit-content', padding: '0.75rem 2rem', marginTop: 0, backgroundColor: '#059669' }}>
                            {isProcessing ? <Loader2 className="animate-spin" /> : <><Play size={18} /> Generuj prognozę</>}
                        </button>
                    </div>
                )}
            </div>

            {/* KOMUNIKATY STATUSU */}
            {(statusMessage || error) && (
                <div style={{
                    padding: '1rem', borderRadius: '0.5rem',
                    backgroundColor: error ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                    border: `1px solid ${error ? '#ef4444' : '#10b981'}`,
                    color: error ? '#ef4444' : '#10b981',
                    display: 'flex', alignItems: 'center', gap: '0.75rem'
                }}>
                    {error ? <AlertCircle size={20} /> : <Loader2 className="animate-spin" size={20} />}
                    <span>{error || statusMessage}</span>
                </div>
            )}

            {/* TABELA - Widoczna tylko dla ADMINISTRATORA */}
            {user.role === ROLES.ADMIN && (
                <div className="stats-section" style={{ padding: '1rem', margin: 0 }}>
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                                    <th style={{ padding: '1rem' }}>DATA I GODZINA</th>
                                    <th style={{ padding: '1rem' }}><Zap size={14} style={{ display: 'inline', marginRight: '4px' }} /> ZUŻYCIE (KWH)</th>
                                    <th style={{ padding: '1rem' }}><Sun size={14} style={{ display: 'inline', marginRight: '4px' }} /> PRODUKCJA (KWH)</th>
                                    <th style={{ padding: '1rem' }}>STATUS</th>
                                </tr>
                            </thead>
                            <tbody style={{ color: 'var(--text-primary)', fontSize: '0.875rem' }}>
                                {forecasts.map((row, idx) => (
                                    <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                        <td style={{ padding: '1rem' }}><Calendar size={14} className="text-muted inline mr-2" /> {row.date}</td>
                                        <td style={{ padding: '1rem', color: 'var(--primary-color)', fontWeight: 'bold' }}>{row.consumption}</td>
                                        <td style={{ padding: '1rem', color: 'var(--accent-emerald)', fontWeight: 'bold' }}>{row.production}</td>
                                        <td style={{ padding: '1rem' }}>
                                            <span style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem', borderRadius: '1rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent-emerald)' }}>Predicted</span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Forecasting;