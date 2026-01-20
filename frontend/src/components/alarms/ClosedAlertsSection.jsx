import React from 'react';
import { ChevronDown, ChevronUp, Info, NotebookTabs } from 'lucide-react';

const ClosedAlertsSection = ({ alerts, showClosedAlerts, toggleClosedAlerts, formatTimestamp, onOpenCommentModal }) => (
    <div className="rules-card">
        <div
            className="rules-card-header"
            style={{ cursor: 'pointer' }}
            onClick={toggleClosedAlerts}
        >
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                Closed Alerts ({alerts.filter(a => a.status === 'CLOSED').length})
                {showClosedAlerts ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </h3>
        </div>
        {showClosedAlerts && (
            <div className="rules-table-wrapper">
                <table className="rules-table">
                    <thead>
                        <tr>
                            <th>Rule</th>
                            <th>Comment</th>
                            <th>Triggering Value</th>
                            <th>Generated At</th>
                            <th>Acknowledged At</th>
                            <th>Closed At</th>
                            <th>Status</th>
                            <th>Priority</th>
                            <th>Acknowledged By</th>
                            <th>Closed By</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {alerts.filter(a => a.status === 'CLOSED').length === 0 ? (
                            <tr>
                                <td colSpan="11" className="table-empty">No closed alerts</td>
                            </tr>
                        ) : (
                            alerts
                                .filter(alert => alert.status === 'CLOSED')
                                .sort((a, b) => new Date(b.timestamp_closed) - new Date(a.timestamp_closed))
                                .map(alert => (
                                    <tr key={alert.id}>
                                        <td>{alert.alert_rule?.name ?? '-'}</td>
                                        <td>
                                            {alert.alert_comment ? (
                                                <button
                                                    className="btn-ghost-edit"
                                                    onClick={() => onOpenCommentModal(alert)}
                                                >
                                                    <NotebookTabs size={16} />
                                                </button>
                                            ) : (
                                                '-'
                                            )}
                                        </td>
                                        <td>{alert.triggering_value ?? '-'}</td>
                                        <td>{formatTimestamp(alert.timestamp_generated)}</td>
                                        <td>{formatTimestamp(alert.timestamp_acknowledged)}</td>
                                        <td>{formatTimestamp(alert.timestamp_closed)}</td>
                                        <td>{alert.status ?? '-'}</td>
                                        <td>{alert.priority ?? '-'}</td>
                                        <td>{alert.acknowledged_by?.username ?? '-'}</td>
                                        <td>{alert.closed_by?.username ?? '-'}</td>
                                        <td>
                                            <div className="table-actions">
                                                <button
                                                    className="btn-ghost-edit"
                                                    onClick={() => onOpenCommentModal(alert)}
                                                    title="Show details"
                                                >
                                                    <Info size={16} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                        )}
                    </tbody>
                </table>
            </div>
        )}
    </div>
);

export default ClosedAlertsSection;
