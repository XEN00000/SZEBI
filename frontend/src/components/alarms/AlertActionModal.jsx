import React from 'react';
import { CheckCircle2, X, XCircle } from 'lucide-react';

const AlertActionModal = ({
    show,
    selectedAlert,
    alertActionLoading,
    alertComment,
    setAlertComment,
    onAcknowledge,
    onCloseAlert,
    onCloseModal
}) => {
    if (!show || !selectedAlert) return null;

    return (
        <div className="modal-overlay" onClick={onCloseModal}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2 className="modal-title">
                        {selectedAlert.status === 'NEW' ? 'Manage Alert' : 'Close Alert'}
                    </h2>
                    <button 
                        className="modal-close"
                        onClick={onCloseModal}
                    >
                        <X size={24} />
                    </button>
                </div>

                <div className="rule-form">
                    <div className="form-group form-group-full">
                        <label className="form-label">Alert Rule</label>
                        <div style={{ padding: '8px 12px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', borderRadius: '6px' }}>
                            {selectedAlert.alert_rule?.name || 'No name'}
                        </div>
                    </div>

                    <div className="form-group form-group-full">
                        <label className="form-label">Status</label>
                        <div style={{ padding: '8px 12px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', borderRadius: '6px' }}>
                            {selectedAlert.status}
                        </div>
                    </div>

                    <div className="form-group form-group-full">
                        <label className="form-label">Triggering Value</label>
                        <div style={{ padding: '8px 12px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', borderRadius: '6px' }}>
                            {selectedAlert.triggering_value ?? '-'}
                        </div>
                    </div>

                    {selectedAlert.alert_comment?.text && (
                        <div className="form-group form-group-full">
                            <label className="form-label">Existing Comment</label>
                            <div style={{ 
                                padding: '12px', 
                                background: 'rgba(255, 255, 255, 0.05)', 
                                border: '1px solid var(--border-color)',
                                borderRadius: '6px',
                                minHeight: '60px',
                                whiteSpace: 'pre-wrap',
                                wordWrap: 'break-word',
                                opacity: 0.8
                            }}>
                                {selectedAlert.alert_comment.text}
                            </div>
                        </div>
                    )}

                    <div className="form-group form-group-full">
                        <label htmlFor="alertComment" className="form-label">
                            {selectedAlert.alert_comment?.text ? 'Add New Comment Part' : 'Comment'}
                        </label>
                        <textarea
                            id="alertComment"
                            className="form-input"
                            value={alertComment}
                            onChange={(e) => setAlertComment(e.target.value)}
                            placeholder="Add comment (optional)..."
                            rows="4"
                            style={{ resize: 'vertical' }}
                        />
                    </div>

                    <div className="form-actions" style={{ gap: '12px' }}>
                        <button
                            type="button"
                            className="btn-secondary"
                            onClick={onCloseModal}
                            disabled={alertActionLoading}
                        >
                            Cancel
                        </button>
                        {selectedAlert.status === 'NEW' && (
                            <button
                                type="button"
                                className="btn-primary"
                                onClick={onAcknowledge}
                                disabled={alertActionLoading}
                                style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
                            >
                                <CheckCircle2 size={16} />
                                {alertActionLoading ? 'Acknowledging...' : 'Acknowledge'}
                            </button>
                        )}
                        <button
                            type="button"
                            className="btn-ghost-danger"
                            onClick={onCloseAlert}
                            disabled={alertActionLoading}
                            style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
                        >
                            <XCircle size={16} />
                            {alertActionLoading ? 'Closing...' : 'Close'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AlertActionModal;
