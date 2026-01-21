import React, { useEffect, useState } from 'react';
import { Plus, Edit2, Trash2, Lock, AlertCircle } from 'lucide-react';
import { getCookie } from '../../utils/csrf';

const API_BASE_URL = 'http://localhost:8000';

const PreferenceManager = ({ notification, setNotification, userRole, userId, refreshKey, onPreferenceChange }) => {
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
    }, [refreshKey]);

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
            setNotification({ type: 'error', message: 'Failed to fetch data.' });
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

            setNotification({ type: 'success', message: 'Preference added.' });
            setShowAddModal(false);
            setFormData({ device: '', target_value: '', schedule: JSON.stringify({}) });
            fetchData();
            if (onPreferenceChange) onPreferenceChange();
        } catch (error) {
            console.error('Error adding preference:', error);
            setNotification({ type: 'error', message: 'Failed to add preference.' });
        }
        setTimeout(() => setNotification(null), 4000);
    };

    const handleDeletePreference = async (prefId) => {
        const confirmed = window.confirm('Are you sure you want to delete this preference?');
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

            setNotification({ type: 'success', message: 'Preference deleted.' });
            fetchData();
            if (onPreferenceChange) onPreferenceChange();
        } catch (error) {
            console.error('Error deleting preference:', error);
            setNotification({ type: 'error', message: 'Failed to delete preference.' });
        } finally {
            setDeletingId(null);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    const displayPreferences = isAdmin ? preferences : myPreferences;
    const displayText = isAdmin ? 'All preferences' : 'My preferences';

    return (
        <div className="preferences-card">
            <div className="preferences-card-header">
                <div>
                    <h3>User Preferences</h3>
                    {isAdmin && <p className="role-notice"><Lock size={14} /> Administrator - viewing all preferences</p>}
                    {!isAdmin && <p className="role-notice">Manage your preferences for MQTT devices</p>}
                </div>
                <button
                    onClick={() => setShowAddModal(true)}
                    className="btn-add-rule"
                >
                    <Plus size={18} />
                    Add preference
                </button>
            </div>

            {devicesLoading && !devices.length && (
                <div className="devices-loading">
                    <AlertCircle size={20} />
                    <span>Loading MQTT devices...</span>
                </div>
            )}

            {devices.length === 0 && !devicesLoading && (
                <div className="error-message">
                    <AlertCircle size={20} />
                    <span>No devices available in MQTT network</span>
                </div>
            )}

            {showAddModal && devices.length > 0 && (
                <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
                    <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">Add preference for device</h2>
                            <button onClick={() => setShowAddModal(false)} className="modal-close">
                                ✕
                            </button>
                        </div>
                        <form onSubmit={handleAddPreference} className="rule-form">
                            <div className="form-grid">
                                <div className="form-group form-group-full">
                                    <label className="form-label">
                                        Device <span className="required">*</span>
                                    </label>
                                    <select
                                        value={formData.device}
                                        onChange={(e) => setFormData({ ...formData, device: e.target.value })}
                                        className="form-select"
                                        required
                                    >
                                        <option value="">Select MQTT device...</option>
                                        {devices.map(dev => (
                                            <option key={dev.uuid || dev.id} value={dev.id || dev.uuid}>
                                                {dev.name || dev.uuid} {dev.device_type ? `(${dev.device_type})` : ''}
                                            </option>
                                        ))}
                                    </select>
                                    <span className="form-hint">Devices are fetched from MQTT in real-time</span>
                                </div>

                                <div className="form-group form-group-full">
                                    <label className="form-label">Target value (e.g. temperature)</label>
                                    <input
                                        type="number"
                                        step="0.1"
                                        value={formData.target_value}
                                        onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
                                        placeholder="e.g. 21.5"
                                        className="form-input"
                                    />
                                    <span className="form-hint">Temperature or other target parameter for the device</span>
                                </div>
                            </div>

                            <div className="form-actions">
                                <button type="button" onClick={() => setShowAddModal(false)} className="btn-secondary">
                                    Cancel
                                </button>
                                <button type="submit" className="btn-primary">
                                    Add preference
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <div className="preferences-list-section">
                <h4>{isAdmin ? 'All preferences' : 'My preferences'} ({displayPreferences.length})</h4>
                {loading ? (
                    <div className="loading-message">Loading preferences...</div>
                ) : displayPreferences.length === 0 ? (
                    <div className="empty-message">No preferences found. Add a new one to start.</div>
                ) : (
                    displayPreferences.map(pref => (
                        <div key={pref.id} className="preference-card">
                            <div className="pref-header">
                                <h4>{pref.device_name}</h4>
                                <div className="pref-actions">
                                    {userRole === 'building_admin' && (
                                        <>
                                            <button className="btn-ghost-edit" title="Edit">
                                                <Edit2 size={16} />
                                            </button>
                                            <button
                                                onClick={() => handleDeletePreference(pref.id)}
                                                disabled={deletingId === pref.id}
                                                className="btn-ghost-danger"
                                                title="Delete"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </>
                                    )}
                                </div>
                            </div>
                            <div className="pref-info">
                                <p><span className="info-label">Target value:</span> {pref.target_value || '-'}</p>
                                <p><span className="info-label">Schedule:</span> {Object.keys(pref.schedule).length > 0 ? 'Set' : 'None'}</p>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default PreferenceManager;
