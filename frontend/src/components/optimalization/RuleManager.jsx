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
            setNotification({ type: 'error', message: 'Failed to fetch rules.' });
        } finally {
            setLoading(false);
            setTimeout(() => setNotification(null), 4000);
        }
    }, [setNotification]);

    useEffect(() => {
        fetchRules();
    }, [refreshKey, fetchRules]);

    const handleDelete = async (ruleId) => {
        const confirmed = window.confirm('Are you sure you want to delete this rule?');
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

            setNotification({ type: 'success', message: 'Rule deleted.' });
            fetchRules();
        } catch (error) {
            console.error('Error deleting rule:', error);
            setNotification({ type: 'error', message: 'Failed to delete rule.' });
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
                message: `Rule ${!rule.is_active ? 'activated' : 'deactivated'}.`
            });
            fetchRules();
        } catch (error) {
            console.error('Error updating rule:', error);
            setNotification({ type: 'error', message: 'Failed to update rule.' });
        }
        setTimeout(() => setNotification(null), 4000);
    };

    const isAdmin = userRole === 'building_admin';

    return (
        <div className="rules-card">
            <div className="rules-card-header">
                <div>
                    <h3>Optimization Rules Management</h3>
                    {!isAdmin && <p className="role-notice"><Lock size={14} /> Only administrator can modify rules</p>}
                </div>
                {isAdmin && (
                    <button onClick={onAddClick} className="btn-add-rule">
                        <Plus size={18} />
                        Add rule
                    </button>
                )}
            </div>

            <div className="rules-table-wrapper">
                <table className="rules-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Conditions</th>
                            <th>Action</th>
                            <th>Priority</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan="6" className="table-empty">Loading rules...</td>
                            </tr>
                        ) : rules.length === 0 ? (
                            <tr>
                                <td colSpan="6" className="table-empty">No rules found. Add a new rule to start.</td>
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
                                            <span className="empty-value">No conditions</span>
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
                                                {rule.is_active ? 'Active' : 'Inactive'}
                                            </button>
                                        ) : (
                                            <span className={`status-label ${rule.is_active ? 'active' : 'inactive'}`}>
                                                {rule.is_active ? 'Active' : 'Inactive'}
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
