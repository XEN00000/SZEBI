import React from 'react';
import { X } from 'lucide-react';

const AddAlertModal = ({
    show,
    rules,
    alertFormData,
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
                    <h2 className="modal-title">Add New Alert</h2>
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
                            <label htmlFor="alert_rule_id" className="form-label">
                                Alert Rule
                                <span className="required">*</span>
                            </label>
                            <select
                                id="alert_rule_id"
                                name="alert_rule_id"
                                className="form-select"
                                value={alertFormData.alert_rule_id}
                                onChange={onChange}
                                required
                            >
                                <option value="">Select a rule...</option>
                                {rules.map(rule => (
                                    <option key={rule.id} value={rule.id}>
                                        {rule.name} ({rule.target_metric})
                                    </option>
                                ))}
                            </select>
                            <p className="form-hint">
                                Select which rule was violated
                            </p>
                        </div>

                        <div className="form-group form-group-full">
                            <label htmlFor="triggering_value" className="form-label">
                                Triggering Value
                                <span className="required">*</span>
                            </label>
                            <input
                                type="number"
                                id="triggering_value"
                                name="triggering_value"
                                className="form-input"
                                value={alertFormData.triggering_value}
                                onChange={onChange}
                                placeholder="0.0"
                                step="0.01"
                                required
                            />
                            <p className="form-hint">
                                Metric value that triggered the alert
                            </p>
                        </div>

                        <div className="form-group form-group-full">
                            <label htmlFor="timestamp" className="form-label">
                                Timestamp (optional)
                            </label>
                            <input
                                type="datetime-local"
                                id="timestamp"
                                name="timestamp"
                                className="form-input"
                                value={alertFormData.timestamp}
                                onChange={onChange}
                            />
                            <p className="form-hint">
                                If empty, the current time will be used
                            </p>
                        </div>

                        <div className="form-group form-group-full">
                            <label htmlFor="comment" className="form-label">
                                Comment (optional)
                            </label>
                            <textarea
                                id="comment"
                                name="comment"
                                className="form-input"
                                value={alertFormData.comment}
                                onChange={onChange}
                                placeholder="Add a comment about the alert..."
                                rows="4"
                                style={{ resize: 'vertical' }}
                            />
                            <p className="form-hint">
                                Additional alert details
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
                            {loading ? 'Creating...' : 'Create Alert'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddAlertModal;
