import React from 'react';
import { NotebookTabs, SquarePen } from 'lucide-react';

const ActiveAlertsTable = ({ alerts, loading, onRefresh, formatTimestamp, onOpenActionModal, onOpenCommentModal }) => (
    <div className="rules-card">
        <div className="rules-card-header">
            <h3>Active Alerts</h3>
            <button className="btn-secondary" onClick={onRefresh} disabled={loading}>
                {loading ? 'Refreshing...' : 'Refresh'}
            </button>
        </div>
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
                    {loading ? (
                        <tr>
                            <td colSpan="11" className="table-empty">Loading...</td>
                        </tr>
                    ) : alerts.filter(a => a.status !== 'CLOSED').length === 0 ? (
                        <tr>
                            <td colSpan="11" className="table-empty">No active alerts</td>
                        </tr>
                    ) : (
                        alerts
                            .filter(alert => alert.status !== 'CLOSED')
                            .sort((a, b) => new Date(b.timestamp_generated) - new Date(a.timestamp_generated))
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
                                                onClick={() => onOpenActionModal(alert)}
                                                disabled={alert.status === 'CLOSED'}
                                                title={alert.status === 'CLOSED' ? 'Alert closed' : 'Manage alert'}
                                            >
                                                <SquarePen size={16} />
                                            </button>
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

export default ActiveAlertsTable;
