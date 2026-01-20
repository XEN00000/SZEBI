import React, { useEffect, useState } from 'react';
import { Plus } from 'lucide-react';
import NotificationToast from '../components/alarms/NotificationToast';
import PageHeader from '../components/alarms/PageHeader';
import ActiveAlertsTable from '../components/alarms/ActiveAlertsTable';
import ClosedAlertsSection from '../components/alarms/ClosedAlertsSection';
import RuleList from '../components/alarms/RuleList';
import InfoBox from '../components/alarms/InfoBox';
import AlertActionModal from '../components/alarms/AlertActionModal';
import AddRuleModal from '../components/alarms/AddRuleModal';
import AddAlertModal from '../components/alarms/AddAlertModal';
import CommentModal from '../components/alarms/CommentModal';

const API_BASE_URL = 'http://localhost:8000';

// Helper function to get CSRF token from cookies
const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

// Helper function to format timestamp
const formatTimestamp = (timestamp) => {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
};

const AlarmsPage = () => {
    const [showAddRuleModal, setShowAddRuleModal] = useState(false);
    const [showAddAlertModal, setShowAddAlertModal] = useState(false);
    const [rules, setRules] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [rulesLoading, setRulesLoading] = useState(false);
    const [alertsLoading, setAlertsLoading] = useState(false);
    const [deletingId, setDeletingId] = useState(null);
    const [showAlertActionModal, setShowAlertActionModal] = useState(false);
    const [showCommentModal, setShowCommentModal] = useState(false);
    const [selectedAlert, setSelectedAlert] = useState(null);
    const [selectedCommentAlert, setSelectedCommentAlert] = useState(null);
    const [alertComment, setAlertComment] = useState('');
    const [alertActionLoading, setAlertActionLoading] = useState(false);
    const [isAddingComment, setIsAddingComment] = useState(false);
    const [newCommentText, setNewCommentText] = useState('');
    const [commentUpdateLoading, setCommentUpdateLoading] = useState(false);
    const [showClosedAlerts, setShowClosedAlerts] = useState(false);
    const [alertFormData, setAlertFormData] = useState({
        alert_rule_id: '',
        triggering_value: '',
        timestamp: '',
        comment: ''
    });
    const [formData, setFormData] = useState({
        name: '',
        target_metric: '',
        operator: 'GREATER_THAN',
        threshold_min: '',
        threshold_max: '',
        duration_seconds: 0,
        priority: 'MEDIUM'
    });
    const [notification, setNotification] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchRules = async () => {
        setRulesLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/alert-rules/`, {
                method: 'GET',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch alert rules');
            }

            const data = await response.json();
            setRules(Array.isArray(data) ? data : data.results || data.alerts || []);
        } catch (error) {
            setNotification({ type: 'error', message: 'Failed to fetch rules.' });
        } finally {
            setRulesLoading(false);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    
    const fetchAlertsData = async () => {
        setAlertsLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/alerts/`, {
                method: 'GET',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch alerts');
            }

            const data = await response.json();
            setAlerts(Array.isArray(data) ? data : data.alerts || []);
        } catch (error) {
            setNotification({ type: 'error', message: 'Failed to fetch alerts.' });
        } finally {
            setAlertsLoading(false);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    const handleDelete = async (ruleId) => {
        const confirmed = window.confirm('Are you sure you want to delete this rule?');
        if (!confirmed) return;
        setDeletingId(ruleId);
        try {
            const csrftoken = getCookie('csrftoken');
            const response = await fetch(`${API_BASE_URL}/api/alert-rules/${ruleId}/`, {
                method: 'DELETE',
                credentials: 'include',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            });

            if (!response.ok) {
                throw new Error('Failed to delete alert rule');
            }

            setNotification({ type: 'success', message: 'Rule deleted.' });
            fetchRules();
        } catch (error) {
            setNotification({ type: 'error', message: 'Failed to delete rule.' });
        } finally {
            setDeletingId(null);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    const openAlertActionModal = (alert) => {
        setSelectedAlert(alert);
        setAlertComment('');
        setShowAlertActionModal(true);
    };

    const openCommentModal = (alert) => {
        setSelectedCommentAlert(alert);
        setIsAddingComment(false);
        setNewCommentText('');
        setShowCommentModal(true);
    };

    const handleAddComment = async () => {
        if (!selectedCommentAlert || !newCommentText.trim()) return;
        setCommentUpdateLoading(true);
        try {
            const csrftoken = getCookie('csrftoken');
            
            const response = await fetch(`${API_BASE_URL}/api/alerts/${selectedCommentAlert.id}/add_comment/`, {
                method: 'POST',
                credentials: 'include',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ 
                    comment: newCommentText 
                })
            });

            if (!response.ok) {
                throw new Error('Failed to add comment');
            }

            setNotification({ type: 'success', message: 'Comment added' });
            setIsAddingComment(false);
            setNewCommentText('');
            fetchAlertsData();
            
            // Update local state
            const existingComment = selectedCommentAlert.alert_comment?.text || '';
            const separator = existingComment ? '\n\n---\n\n' : '';
            const updatedComment = existingComment + separator + newCommentText;
            
            setSelectedCommentAlert({
                ...selectedCommentAlert,
                alert_comment: {
                    ...selectedCommentAlert.alert_comment,
                    text: updatedComment
                }
            });
        } catch (error) {
            setNotification({ type: 'error', message: 'Failed to add comment' });
        } finally {
            setCommentUpdateLoading(false);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    const handleAcknowledgeAlert = async () => {
        if (!selectedAlert) return;
        setAlertActionLoading(true);
        try {
            const existingComment = selectedAlert.alert_comment?.text || '';
            const separator = existingComment && alertComment ? '\n\n---\n\n' : '';
            const updatedComment = existingComment + separator + alertComment;
            const body = alertComment ? { comment: updatedComment } : {};
            const csrftoken = getCookie('csrftoken');
            
            const response = await fetch(`${API_BASE_URL}/api/alerts/${selectedAlert.id}/acknowledge/`, {
                method: 'POST',
                credentials: 'include',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                throw new Error('Failed to acknowledge alert');
            }

            setNotification({ type: 'success', message: 'Alert acknowledged' });
            setShowAlertActionModal(false);
            setSelectedAlert(null);
            setAlertComment('');
            fetchAlertsData();
        } catch (error) {
            setNotification({ type: 'error', message: 'Failed to acknowledge alert' });
        } finally {
            setAlertActionLoading(false);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    const handleCloseAlert = async () => {
        if (!selectedAlert) return;
        setAlertActionLoading(true);
        try {
            const existingComment = selectedAlert.alert_comment?.text || '';
            const separator = existingComment && alertComment ? '\n\n---\n\n' : '';
            const updatedComment = existingComment + separator + alertComment;
            const body = alertComment ? { comment: updatedComment } : {};
            const csrftoken = getCookie('csrftoken');
            
            const response = await fetch(`${API_BASE_URL}/api/alerts/${selectedAlert.id}/close/`, {
                method: 'POST',
                credentials: 'include',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                throw new Error('Failed to close alert');
            }

            setNotification({ type: 'success', message: 'Alert closed' });
            setShowAlertActionModal(false);
            setSelectedAlert(null);
            setAlertComment('');
            fetchAlertsData();
        } catch (error) {
            setNotification({ type: 'error', message: 'Failed to close alert' });
        } finally {
            setAlertActionLoading(false);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    useEffect(() => {
        fetchRules();
        fetchAlertsData();
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleAlertInputChange = (e) => {
        const { name, value } = e.target;
        setAlertFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleAlertSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const alertData = {
                alert_rule_id: parseInt(alertFormData.alert_rule_id),
                triggering_value: parseFloat(alertFormData.triggering_value),
                timestamp: alertFormData.timestamp || undefined,
                comment: alertFormData.comment || undefined
            };

            const csrftoken = getCookie('csrftoken');
            const response = await fetch(`${API_BASE_URL}/api/alerts/`, {
                method: 'POST',
                credentials: 'include',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(alertData)
            });

            if (!response.ok) {
                throw new Error('Failed to create alert');
            }
            
            setNotification({
                type: 'success',
                message: 'Alert created successfully!'
            });
            setAlertFormData({
                alert_rule_id: '',
                triggering_value: '',
                timestamp: '',
                comment: ''
            });
            setShowAddAlertModal(false);
            fetchAlertsData();
        } catch (error) {
            console.error(error);
            setNotification({
                type: 'error',
                message: 'Failed to create alert. Please try again.'
            });
        } finally {
            setLoading(false);
            setTimeout(() => setNotification(null), 5000);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            // Prepare data for API
            const ruleData = {
                name: formData.name,
                target_metric: formData.target_metric,
                operator: formData.operator,
                threshold_min: formData.threshold_min ? parseFloat(formData.threshold_min) : null,
                threshold_max: formData.threshold_max ? parseFloat(formData.threshold_max) : null,
                duration_seconds: parseInt(formData.duration_seconds) || 0,
                priority: formData.priority
            };

            const csrftoken = getCookie('csrftoken');
            const response = await fetch(`${API_BASE_URL}/api/alert-rules/`, {
                method: 'POST',
                credentials: 'include',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(ruleData)
            });

            if (!response.ok) {
                throw new Error('Failed to create alert rule');
            }
            
            setNotification({
                type: 'success',
                message: 'Alert rule created successfully!'
            });
            setFormData({
                name: '',
                target_metric: '',
                operator: 'GREATER_THAN',
                threshold_min: '',
                threshold_max: '',
                duration_seconds: 0,
                priority: 'MEDIUM'
            });
            setShowAddRuleModal(false);
            fetchRules();
        } catch (error) {
            console.error(error);
            setNotification({
                type: 'error',
                message: 'Failed to create rule. Please try again.'
            });
        } finally {
            setLoading(false);
            setTimeout(() => setNotification(null), 5000);
        }
    };

    return (
        <div className="alarms-page">
            <NotificationToast
                notification={notification}
                onClose={() => setNotification(null)}
            />

            <PageHeader
                title="Alarm System"
                subtitle="Manage alarm rules and monitor system status"
            />

            <button 
                className="btn-add-rule"
                onClick={() => setShowAddAlertModal(true)}
                style={{ bottom: '90px' }}
            >
                <Plus size={20} />
                Add Alert
            </button>

            <ActiveAlertsTable
                alerts={alerts}
                loading={alertsLoading}
                onRefresh={fetchAlertsData}
                formatTimestamp={formatTimestamp}
                onOpenActionModal={openAlertActionModal}
                onOpenCommentModal={openCommentModal}
            />

            <ClosedAlertsSection
                alerts={alerts}
                showClosedAlerts={showClosedAlerts}
                toggleClosedAlerts={() => setShowClosedAlerts(!showClosedAlerts)}
                formatTimestamp={formatTimestamp}
                onOpenCommentModal={openCommentModal}
            />

            <button 
                className="btn-add-rule"
                onClick={() => setShowAddRuleModal(true)}
            >
                <Plus size={20} />
                Add Rule
            </button>

            <RuleList
                rules={rules}
                loading={rulesLoading}
                onRefresh={fetchRules}
                onDelete={handleDelete}
                deletingId={deletingId}
            />

            <InfoBox />

            <AlertActionModal
                show={showAlertActionModal}
                selectedAlert={selectedAlert}
                alertActionLoading={alertActionLoading}
                alertComment={alertComment}
                setAlertComment={setAlertComment}
                onAcknowledge={handleAcknowledgeAlert}
                onCloseAlert={handleCloseAlert}
                onCloseModal={() => setShowAlertActionModal(false)}
            />

            <AddRuleModal
                show={showAddRuleModal}
                formData={formData}
                loading={loading}
                onClose={() => setShowAddRuleModal(false)}
                onChange={handleInputChange}
                onSubmit={handleSubmit}
            />

            <AddAlertModal
                show={showAddAlertModal}
                rules={rules}
                alertFormData={alertFormData}
                loading={loading}
                onClose={() => setShowAddAlertModal(false)}
                onChange={handleAlertInputChange}
                onSubmit={handleAlertSubmit}
            />

            <CommentModal
                show={showCommentModal}
                selectedCommentAlert={selectedCommentAlert}
                isAddingComment={isAddingComment}
                setIsAddingComment={setIsAddingComment}
                newCommentText={newCommentText}
                setNewCommentText={setNewCommentText}
                commentUpdateLoading={commentUpdateLoading}
                formatTimestamp={formatTimestamp}
                onAddComment={handleAddComment}
                onClose={() => setShowCommentModal(false)}
            />
        </div>
    );
};

export default AlarmsPage;
