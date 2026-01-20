import React, { useState, useEffect } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

const AddRuleModal = ({ isOpen, onClose, onSubmit, loading, editingRule = null }) => {
    const [formData, setFormData] = useState({
        name: '',
        conditions: [],
        action: '',
        priority: 1,
        is_active: true
    });
    const [newCondition, setNewCondition] = useState({
        field: '',
        operator: '>',
        value: ''
    });
    const [availableConditions, setAvailableConditions] = useState([]);
    const [availableActions, setAvailableActions] = useState([]);

    useEffect(() => {
        if (isOpen) {
            fetchOptions();
            if (editingRule) {
                setFormData({
                    name: editingRule.name,
                    conditions: editingRule.conditions || [],
                    action: editingRule.action,
                    priority: editingRule.priority,
                    is_active: editingRule.is_active
                });
            } else {
                setFormData({
                    name: '',
                    conditions: [],
                    action: '',
                    priority: 1,
                    is_active: true
                });
            }
        }
    }, [isOpen, editingRule]);

    const fetchOptions = async () => {
        try {
            const [condRes, actRes] = await Promise.all([
                fetch(`${API_BASE_URL}/api/optimization/conditions/`),
                fetch(`${API_BASE_URL}/api/optimization/actions/`)
            ]);

            const conditions = await condRes.json();
            const actions = await actRes.json();

            setAvailableConditions(conditions);
            setAvailableActions(actions);
        } catch (error) {
            console.error('Error fetching options:', error);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : type === 'number' ? parseInt(value) : value
        }));
    };

    const handleConditionChange = (e) => {
        const { name, value } = e.target;
        setNewCondition(prev => ({
            ...prev,
            [name]: name === 'value' ? (value === '' ? '' : isNaN(value) ? value : parseFloat(value)) : value
        }));
    };

    const addCondition = () => {
        if (!newCondition.field.trim()) {
            alert('Podaj pole warunku');
            return;
        }
        setFormData(prev => ({
            ...prev,
            conditions: [...prev.conditions, { ...newCondition }]
        }));
        setNewCondition({ field: '', operator: '>', value: '' });
    };

    const removeCondition = (index) => {
        setFormData(prev => ({
            ...prev,
            conditions: prev.conditions.filter((_, i) => i !== index)
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (formData.conditions.length === 0) {
            alert('Dodaj co najmniej jeden warunek');
            return;
        }
        onSubmit(formData);
        setFormData({
            name: '',
            conditions: [],
            action: '',
            priority: 1,
            is_active: true
        });
        setNewCondition({ field: '', operator: '>', value: '' });
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2 className="modal-title">{editingRule ? 'Edytuj regułę' : 'Dodaj nową regułę'}</h2>
                    <button onClick={onClose} className="modal-close">
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="rule-form">
                    <div className="form-grid">
                        <div className="form-group form-group-full">
                            <label className="form-label">
                                Nazwa reguły <span className="required">*</span>
                            </label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="np. Wymuszenie oszczędzania w szczycie"
                                className="form-input"
                                required
                            />
                            <span className="form-hint">Opisowa nazwa reguły optymalizacji</span>
                        </div>

                        <div className="form-group form-group-full">
                            <label className="form-label">
                                Warunki <span className="required">*</span>
                            </label>
                            <div className="conditions-list">
                                {formData.conditions.length > 0 && (
                                    <div className="conditions-display">
                                        {formData.conditions.map((cond, idx) => (
                                            <div key={idx} className="condition-tag">
                                                <span>{cond.field} {cond.operator} {cond.value}</span>
                                                <button
                                                    type="button"
                                                    onClick={() => removeCondition(idx)}
                                                    className="condition-remove"
                                                    title="Usuń warunek"
                                                >
                                                    <Trash2 size={14} />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                                <div className="condition-input-group">
                                    <select
                                        name="field"
                                        value={newCondition.field}
                                        onChange={handleConditionChange}
                                        className="form-select form-input-sm"
                                    >
                                        <option value="">Wybierz pole...</option>
                                        {availableConditions.map(cond => (
                                            <option key={cond.value} value={cond.value}>
                                                {cond.label}
                                            </option>
                                        ))}
                                    </select>
                                    <select
                                        name="operator"
                                        value={newCondition.operator}
                                        onChange={handleConditionChange}
                                        className="form-select form-input-sm"
                                    >
                                        <option value=">">&gt;</option>
                                        <option value="<">&lt;</option>
                                        <option value="=">=</option>
                                        <option value="!=">{`!=`}</option>
                                        <option value=">=">&gt;=</option>
                                        <option value="<=">&lt;=</option>
                                    </select>
                                    <input
                                        type="text"
                                        name="value"
                                        value={newCondition.value}
                                        onChange={handleConditionChange}
                                        placeholder="wartość"
                                        className="form-input form-input-sm"
                                    />
                                    <button
                                        type="button"
                                        onClick={addCondition}
                                        className="btn-add-condition"
                                    >
                                        <Plus size={16} /> Dodaj
                                    </button>
                                </div>
                            </div>
                            <span className="form-hint">Dodaj warunki które muszą być spełnione dla aktywacji reguły</span>
                        </div>

                        <div className="form-group form-group-full">
                            <label className="form-label">
                                Akcja <span className="required">*</span>
                            </label>
                            <select
                                name="action"
                                value={formData.action}
                                onChange={handleChange}
                                className="form-select"
                                required
                            >
                                <option value="">Wybierz akcję...</option>
                                {availableActions.map(action => (
                                    <option key={action.value} value={action.value}>
                                        {action.label} - {action.description}
                                    </option>
                                ))}
                            </select>
                            <span className="form-hint">Wybierz akcję która będzie wykonana gdy wszystkie warunki będą spełnione</span>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Priorytet</label>
                            <input
                                type="number"
                                name="priority"
                                value={formData.priority}
                                onChange={handleChange}
                                min="1"
                                max="100"
                                className="form-input"
                            />
                            <span className="form-hint">Wyższy numer = ważniejsza reguła</span>
                        </div>

                        <div className="form-group">
                            <label className="form-label">
                                <input
                                    type="checkbox"
                                    name="is_active"
                                    checked={formData.is_active}
                                    onChange={handleChange}
                                />
                                {' '}Aktywna
                            </label>
                        </div>
                    </div>

                    <div className="form-actions">
                        <button type="button" onClick={onClose} className="btn-secondary">
                            Anuluj
                        </button>
                        <button type="submit" className="btn-primary" disabled={loading}>
                            {loading ? (editingRule ? 'Aktualizowanie...' : 'Dodawanie...') : (editingRule ? 'Zaktualizuj regułę' : 'Dodaj regułę')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddRuleModal;
