import React from 'react';
import { X } from 'lucide-react';

const AddRuleModal = ({
    show,
    formData,
    loading,
    onClose,
    onChange,
    onSubmit
}) => {
    if (!show) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2 className="modal-title">Add New Alert Rule</h2>
                    <button 
                        className="modal-close"
                        onClick={onClose}
                    >
                        <X size={24} />
                    </button>
                </div>

                <form onSubmit={onSubmit} className="rule-form">
                    <div className="form-grid">
                        <div className="form-group form-group-full">
                            <label htmlFor="name" className="form-label">
                                Rule Name
                                <span className="required">*</span>
                            </label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                className="form-input"
                                value={formData.name}
                                onChange={onChange}
                                placeholder="e.g. High energy usage"
                                required
                            />
                        </div>

                        <div className="form-group form-group-full">
                            <label htmlFor="target_metric" className="form-label">
                                Target Metric
                                <span className="required">*</span>
                            </label>
                            <input
                                type="text"
                                id="target_metric"
                                name="target_metric"
                                className="form-input"
                                value={formData.target_metric}
                                onChange={onChange}
                                placeholder="e.g. power_consumption"
                                required
                            />
                            <p className="form-hint">
                                Name of the metric to monitor
                            </p>
                        </div>

                        <div className="form-group">
                            <label htmlFor="operator" className="form-label">
                                Operator
                                <span className="required">*</span>
                            </label>
                            <select
                                id="operator"
                                name="operator"
                                className="form-select"
                                value={formData.operator}
                                onChange={onChange}
                                required
                            >
                                <option value="GREATER_THAN">Greater than</option>
                                <option value="LESS_THAN">Less than</option>
                                <option value="EQUALS">Equals</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label htmlFor="priority" className="form-label">
                                Priority
                                <span className="required">*</span>
                            </label>
                            <select
                                id="priority"
                                name="priority"
                                className="form-select"
                                value={formData.priority}
                                onChange={onChange}
                                required
                            >
                                <option value="LOW">Low</option>
                                <option value="MEDIUM">Medium</option>
                                <option value="HIGH">High</option>
                                <option value="CRITICAL">Critical</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label htmlFor="threshold_min" className="form-label">
                                Minimum Threshold
                            </label>
                            <input
                                type="number"
                                id="threshold_min"
                                name="threshold_min"
                                className="form-input"
                                value={formData.threshold_min}
                                onChange={onChange}
                                placeholder="0.0"
                                step="0.01"
                            />
                            <p className="form-hint">
                                Used for the "less than" or "equals" operators
                            </p>
                        </div>

                        <div className="form-group">
                            <label htmlFor="threshold_max" className="form-label">
                                Maximum Threshold
                            </label>
                            <input
                                type="number"
                                id="threshold_max"
                                name="threshold_max"
                                className="form-input"
                                value={formData.threshold_max}
                                onChange={onChange}
                                placeholder="100.0"
                                step="0.01"
                            />
                            <p className="form-hint">
                                Used for the "greater than" operator
                            </p>
                        </div>

                        <div className="form-group form-group-full">
                            <label htmlFor="duration_seconds" className="form-label">
                                Duration (seconds)
                            </label>
                            <input
                                type="number"
                                id="duration_seconds"
                                name="duration_seconds"
                                className="form-input"
                                value={formData.duration_seconds}
                                onChange={onChange}
                                placeholder="0"
                                min="0"
                            />
                            <p className="form-hint">
                                How long the condition must be met before triggering an alert
                            </p>
                        </div>
                    </div>

                    <div className="form-actions">
                        <button
                            type="button"
                            className="btn-secondary"
                            onClick={onClose}
                            disabled={loading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn-primary"
                            disabled={loading}
                        >
                            {loading ? 'Creating...' : 'Create Rule'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddRuleModal;
