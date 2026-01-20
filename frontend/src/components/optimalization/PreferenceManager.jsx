import React, { useEffect, useState } from 'react';
import { Plus, Edit2, Trash2, Lock, AlertCircle } from 'lucide-react';
import { getCookie } from '../../utils/csrf';

const API_BASE_URL = 'http://localhost:8000';

const PreferenceManager = ({ notification, setNotification, userRole, userId }) => {
    const [preferences, setPreferences] = useState([]);
    const [devices, setDevices] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showAddModal, setShowAddModal] = useState(false);
    const [formData, setFormData] = useState({
        device: '',
        target_value: '',
        schedule: JSON.stringify({})
    });
    const [deletingId, setDeletingId] = useState(null);
    const [devicesLoading, setDevicesLoading] = useState(false);
    const [myPreferences, setMyPreferences] = useState([]);

    const isAdmin = userRole === 'building_admin';

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            // Preferencje
            const prefRes = await fetch(`${API_BASE_URL}/api/optimization/preferences/`, {
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });

            if (prefRes.ok) {
                const prefData = await prefRes.json();
                const prefList = Array.isArray(prefData) ? prefData : prefData.results || [];
                setPreferences(prefList);
                
                // Filtruj tylko moje preferencje dla zwykłego użytkownika
                if (!isAdmin && userId) {
                    const myPrefs = prefList.filter(p => p.user_id === userId);
                    setMyPreferences(myPrefs);
                }
            }

            // Urządzenia z MQTT
            setDevicesLoading(true);
            const devRes = await fetch(`${API_BASE_URL}/api/optimization/devices/`, {
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });

            if (devRes.ok) {
                const devData = await devRes.json();
                const devList = Array.isArray(devData) ? devData : devData.results || [];
                setDevices(devList);
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            setNotification({ type: 'error', message: 'Nie udało się pobrać danych.' });
        } finally {
            setLoading(false);
            setDevicesLoading(false);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    const handleAddPreference = async (e) => {
        e.preventDefault();
        try {
            const csrftoken = getCookie('csrftoken');
            const response = await fetch(`${API_BASE_URL}/api/optimization/preferences/`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    device: parseInt(formData.device),
                    target_value: formData.target_value ? parseFloat(formData.target_value) : null,
                    schedule: JSON.parse(formData.schedule)
                })
            });

            if (!response.ok) throw new Error('Failed to add preference');

            setNotification({ type: 'success', message: 'Preferencja dodana.' });
            setShowAddModal(false);
            setFormData({ device_id: '', target_value: '', schedule: JSON.stringify({}) });
            fetchData();
        } catch (error) {
            console.error('Error adding preference:', error);
            setNotification({ type: 'error', message: 'Nie udało się dodać preferencji.' });
        }
        setTimeout(() => setNotification(null), 4000);
    };

    const handleDeletePreference = async (prefId) => {
        const confirmed = window.confirm('Czy na pewno chcesz usunąć tę preferencję?');
        if (!confirmed) return;

        setDeletingId(prefId);
        try {
            const csrftoken = getCookie('csrftoken');
            const response = await fetch(`${API_BASE_URL}/api/optimization/preferences/${prefId}/`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            });

            if (!response.ok) throw new Error('Failed to delete preference');

            setNotification({ type: 'success', message: 'Preferencja usunięta.' });
            fetchData();
        } catch (error) {
            console.error('Error deleting preference:', error);
            setNotification({ type: 'error', message: 'Nie udało się usunąć preferencji.' });
        } finally {
            setDeletingId(null);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    const displayPreferences = isAdmin ? preferences : myPreferences;
    const displayText = isAdmin ? 'Wszystkie preferencje' : 'Moje preferencje';

    return (
        <div className="preferences-card">
            <div className="preferences-card-header">
                <div>
                    <h3>Preferencje użytkownika</h3>
                    {isAdmin && <p className="role-notice"><Lock size={14} /> Administrator - przeglądanie wszystkich preferencji</p>}
                    {!isAdmin && <p className="role-notice">Zarządzaj swoimi preferencjami dla urządzeń z MQTT</p>}
                </div>
                <button 
                    onClick={() => setShowAddModal(true)}
                    className="btn-add-rule"
                >
                    <Plus size={18} />
                    Dodaj preferencję
                </button>
            </div>

            {devicesLoading && !devices.length && (
                <div className="devices-loading">
                    <AlertCircle size={20} />
                    <span>Wczytywanie urządzeń z MQTT...</span>
                </div>
            )}

            {devices.length === 0 && !devicesLoading && (
                <div className="error-message">
                    <AlertCircle size={20} />
                    <span>Brak dostępnych urządzeń w sieci MQTT</span>
                </div>
            )}

            {showAddModal && devices.length > 0 && (
                <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
                    <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">Dodaj preferencję dla urządzenia</h2>
                            <button onClick={() => setShowAddModal(false)} className="modal-close">
                                ✕
                            </button>
                        </div>
                        <form onSubmit={handleAddPreference} className="rule-form">
                            <div className="form-grid">
                                <div className="form-group form-group-full">
                                    <label className="form-label">
                                        Urządzenie <span className="required">*</span>
                                    </label>
                                    <select
                                        value={formData.device_id}
                                        onChange={(e) => setFormData({ ...formData, device_id: e.target.value })}
                                        className="form-select"
                                        required
                                    >
                                        <option value="">Wybierz urządzenie z MQTT...</option>
                                        {devices.map(dev => (
                                            <option key={dev.uuid || dev.id} value={dev.id || dev.uuid}>
                                                {dev.name || dev.uuid} {dev.device_type ? `(${dev.device_type})` : ''}
                                            </option>
                                        ))}
                                    </select>
                                    <span className="form-hint">Urządzenia są pobierane z MQTT w czasie rzeczywistym</span>
                                </div>

                                <div className="form-group form-group-full">
                                    <label className="form-label">Docelowa wartość (np. temperatura)</label>
                                    <input
                                        type="number"
                                        step="0.1"
                                        value={formData.target_value}
                                        onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
                                        placeholder="np. 21.5"
                                        className="form-input"
                                    />
                                    <span className="form-hint">Temperatura lub inny parametr docelowy dla urządzenia</span>
                                </div>
                            </div>

                            <div className="form-actions">
                                <button type="button" onClick={() => setShowAddModal(false)} className="btn-secondary">
                                    Anuluj
                                </button>
                                <button type="submit" className="btn-primary">
                                    Dodaj preferencję
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <div className="preferences-list-section">
                <h4>{isAdmin ? 'Wszystkie preferencje' : 'Moje preferencje'} ({displayPreferences.length})</h4>
                {loading ? (
                    <div className="loading-message">Ładowanie preferencji...</div>
                ) : preferences.length === 0 ? (
                    <div className="empty-message">Brak preferencji. Dodaj nową aby zacząć.</div>
                ) : (
                    preferences.map(pref => (
                        <div key={pref.id} className="preference-card">
                            <div className="pref-header">
                                <h4>{pref.device_name}</h4>
                                <div className="pref-actions">
                                    {userRole === 'building_admin' && (
                                        <>
                                            <button className="btn-ghost-edit" title="Edytuj">
                                                <Edit2 size={16} />
                                            </button>
                                            <button
                                                onClick={() => handleDeletePreference(pref.id)}
                                                disabled={deletingId === pref.id}
                                                className="btn-ghost-danger"
                                                title="Usuń"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </>
                                    )}
                                </div>
                            </div>
                            <div className="pref-info">
                                <p><span className="info-label">Docelowa wartość:</span> {pref.target_value || '-'}</p>
                                <p><span className="info-label">Harmonogram:</span> {Object.keys(pref.schedule).length > 0 ? 'Ustawiony' : 'Brak'}</p>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default PreferenceManager;
