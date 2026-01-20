import React, { useEffect, useState, useCallback } from 'react';
import { Trash2, Edit2, Plus, Lock } from 'lucide-react';
import { getCookie } from '../../utils/csrf';

const API_BASE_URL = 'http://localhost:8000';

const RuleManager = ({ onAddClick, onRefresh, notification, setNotification, userRole, refreshKey, onEditClick }) => {
    const [rules, setRules] = useState([]);
    const [loading, setLoading] = useState(false);
    const [deletingId, setDeletingId] = useState(null);

    const fetchRules = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/optimization/rules/`, {
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to fetch rules');

            const data = await response.json();
            const rulesList = Array.isArray(data) ? data : data.results || [];
            setRules(rulesList.sort((a, b) => b.priority - a.priority));
        } catch (error) {
            console.error('Error fetching rules:', error);
            setNotification({ type: 'error', message: 'Nie udało się pobrać reguł.' });
        } finally {
            setLoading(false);
            setTimeout(() => setNotification(null), 4000);
        }
    }, [setNotification]);

    useEffect(() => {
        fetchRules();
    }, [refreshKey, fetchRules]);

    const handleDelete = async (ruleId) => {
        const confirmed = window.confirm('Czy na pewno chcesz usunąć tę regułę?');
        if (!confirmed) return;

        setDeletingId(ruleId);
        try {
            const csrftoken = getCookie('csrftoken');
            const response = await fetch(`${API_BASE_URL}/api/optimization/rules/${ruleId}/`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            });

            if (!response.ok) throw new Error('Failed to delete rule');

            setNotification({ type: 'success', message: 'Reguła usunięta.' });
            fetchRules();
        } catch (error) {
            console.error('Error deleting rule:', error);
            setNotification({ type: 'error', message: 'Nie udało się usunąć reguły.' });
        } finally {
            setDeletingId(null);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    const toggleActive = async (rule) => {
        try {
            const csrftoken = getCookie('csrftoken');
            const response = await fetch(`${API_BASE_URL}/api/optimization/rules/${rule.id}/`, {
                method: 'PATCH',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    ...rule,
                    is_active: !rule.is_active
                })
            });

            if (!response.ok) throw new Error('Failed to update rule');

            setNotification({ 
                type: 'success', 
                message: `Reguła ${!rule.is_active ? 'aktywowana' : 'dezaktywowana'}.` 
            });
            fetchRules();
        } catch (error) {
            console.error('Error updating rule:', error);
            setNotification({ type: 'error', message: 'Nie udało się zaktualizować reguły.' });
        }
        setTimeout(() => setNotification(null), 4000);
    };

    const isAdmin = userRole === 'building_admin';

    return (
        <div className="rules-card">
            <div className="rules-card-header">
                <div>
                    <h3>Zarządzanie regułami optymalizacji</h3>
                    {!isAdmin && <p className="role-notice"><Lock size={14} /> Tylko administrator może modyfikować reguły</p>}
                </div>
                {isAdmin && (
                    <button onClick={onAddClick} className="btn-add-rule">
                        <Plus size={18} />
                        Dodaj regułę
                    </button>
                )}
            </div>

            <div className="rules-table-wrapper">
                <table className="rules-table">
                    <thead>
                        <tr>
                            <th>Nazwa</th>
                            <th>Warunki</th>
                            <th>Akcja</th>
                            <th>Priorytet</th>
                            <th>Status</th>
                            <th>Akcje</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan="6" className="table-empty">Ładowanie reguł...</td>
                            </tr>
                        ) : rules.length === 0 ? (
                            <tr>
                                <td colSpan="6" className="table-empty">Brak reguł. Dodaj nową regułę aby zacząć.</td>
                            </tr>
                        ) : (
                            rules.map(rule => (
                                <tr key={rule.id}>
                                    <td>{rule.name}</td>
                                    <td className="condition-cell">
                                        {Array.isArray(rule.conditions) && rule.conditions.length > 0 ? (
                                            <div className="conditions-list-inline">
                                                {rule.conditions.map((cond, idx) => (
                                                    <span key={idx} className="condition-badge">
                                                        {cond.field} {cond.operator} {cond.value}
                                                    </span>
                                                ))}
                                            </div>
                                        ) : (
                                            <span className="empty-value">Brak warunków</span>
                                        )}
                                    </td>
                                    <td>{rule.action}</td>
                                    <td>
                                        <span className="priority-badge">{rule.priority}</span>
                                    </td>
                                    <td>
                                        {isAdmin ? (
                                            <button
                                                onClick={() => toggleActive(rule)}
                                                className={`status-toggle ${rule.is_active ? 'active' : 'inactive'}`}
                                            >
                                                {rule.is_active ? 'Aktywna' : 'Nieaktywna'}
                                            </button>
                                        ) : (
                                            <span className={`status-label ${rule.is_active ? 'active' : 'inactive'}`}>
                                                {rule.is_active ? 'Aktywna' : 'Nieaktywna'}
                                            </span>
                                        )}
                                    </td>
                                    <td>
                                        <div className="table-actions">
                                            {isAdmin && (
                                                <>
                                                    <button 
                                                        onClick={() => onEditClick(rule)}
                                                        className="btn-ghost-edit" 
                                                        title="Edytuj"
                                                    >
                                                        <Edit2 size={16} />
                                                    </button>
                                                    <button
                                                        onClick={() => handleDelete(rule.id)}
                                                        disabled={deletingId === rule.id}
                                                        className="btn-ghost-danger"
                                                        title="Usuń"
                                                    >
                                                        <Trash2 size={16} />
                                                    </button>
                                                </>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default RuleManager;
