import React from 'react';
import { Trash2 } from 'lucide-react';

const RuleList = ({ rules, loading, onRefresh, onDelete, deletingId }) => (
    <div className="rules-card">
        <div className="rules-card-header">
            <h3>Rule List</h3>
            <button className="btn-secondary" onClick={onRefresh} disabled={loading}>
                {loading ? 'Refreshing...' : 'Refresh'}
            </button>
        </div>
        <div className="rules-table-wrapper">
            <table className="rules-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Metric</th>
                        <th>Operator</th>
                        <th>Min Threshold</th>
                        <th>Max Threshold</th>
                        <th>Priority</th>
                        <th>Duration (s)</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {loading ? (
                        <tr>
                            <td colSpan="8" className="table-empty">Loading...</td>
                        </tr>
                    ) : rules.length === 0 ? (
                        <tr>
                            <td colSpan="8" className="table-empty">No rules to display</td>
                        </tr>
                    ) : (
                        rules.map(rule => (
                            <tr key={rule.id}>
                                <td>{rule.name}</td>
                                <td>{rule.target_metric}</td>
                                <td>{rule.operator}</td>
                                <td>{rule.threshold_min ?? '-'}</td>
                                <td>{rule.threshold_max ?? '-'}</td>
                                <td>{rule.priority}</td>
                                <td>{rule.duration_seconds}</td>
                                <td>
                                    <div className="table-actions">
                                        <button
                                            className="btn-ghost-danger"
                                            onClick={() => onDelete(rule.id)}
                                            disabled={deletingId === rule.id}
                                        >
                                            {deletingId === rule.id ? 'Deleting...' : <Trash2 size={16} />}
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

export default RuleList;
