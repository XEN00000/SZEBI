import React, { useState, useCallback } from 'react';
import DashboardOptimization from '../components/optimalization/DashboardOptimization';
import RuleManager from '../components/optimalization/RuleManager';
import PreferenceManager from '../components/optimalization/PreferenceManager';
import OptimizationHistory from '../components/optimalization/OptimizationHistory';
import AddRuleModal from '../components/optimalization/AddRuleModal';
import NotificationToast from '../components/optimalization/NotificationToast';
import { getCookie } from '../utils/csrf';

const API_BASE_URL = 'http://localhost:8000';

const OptimalizationPage = ({ userRole, userId }) => {
    const [showAddRuleModal, setShowAddRuleModal] = useState(false);
    const [editingRule, setEditingRule] = useState(null);
    const [notification, setNotification] = useState(null);
    const [addingRule, setAddingRule] = useState(false);
    const [refreshKey, setRefreshKey] = useState(0);

    const handleAddRule = async (formData) => {
        setAddingRule(true);
        try {
            const csrftoken = getCookie('csrftoken');
            const method = editingRule ? 'PATCH' : 'POST';
            const url = editingRule ? `${API_BASE_URL}/api/optimization/rules/${editingRule.id}/` : `${API_BASE_URL}/api/optimization/rules/`;
            
            const response = await fetch(url, {
                method: method,
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) throw new Error('Failed to save rule');

            const message = editingRule ? 'Reguła zaktualizowana pomyślnie.' : 'Reguła dodana pomyślnie.';
            setNotification({ type: 'success', message });
            setShowAddRuleModal(false);
            setEditingRule(null);
            setRefreshKey(prev => prev + 1);
        } catch (error) {
            console.error('Error saving rule:', error);
            const message = editingRule ? 'Nie udało się zaktualizować reguły.' : 'Nie udało się dodać reguły.';
            setNotification({ type: 'error', message });
        } finally {
            setAddingRule(false);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    const handleEditClick = (rule) => {
        setEditingRule(rule);
        setShowAddRuleModal(true);
    };

    const handleRefresh = useCallback(() => {
        setRefreshKey(prev => prev + 1);
    }, []);

    const handlePreferenceChange = useCallback(() => {
        setRefreshKey(prev => prev + 1);
    }, []);

    return (
        <div className="acquisition-container">
            <div className="optimization-content">
                {/* Page Header */}
                <div className="header-section">
                    <h1 className="page-title">Panel Optymalizacji</h1>
                    <p className="page-subtitle">Zarządzanie regułami optymalizacji i preferencjami urządzeń</p>
                </div>

                {/* Notification Toast */}
                <NotificationToast 
                    notification={notification}
                    onClose={() => setNotification(null)}
                />

                {/* Dashboard */}
                <section className="dashboard-section">
                    <DashboardOptimization refreshKey={refreshKey} />
                </section>

                {/* Rule Manager */}
                <section className="manager-section">
                    <RuleManager
                        onAddClick={() => setShowAddRuleModal(true)}
                        onEditClick={handleEditClick}
                        onRefresh={handleRefresh}
                        notification={notification}
                        setNotification={setNotification}
                        userRole={userRole}
                        refreshKey={refreshKey}
                    />
                </section>

                {/* Preference Manager */}
                <section className="manager-section">
                    <PreferenceManager
                        notification={notification}
                        setNotification={setNotification}
                        userRole={userRole}
                        userId={userId}
                        refreshKey={refreshKey}
                        onPreferenceChange={handlePreferenceChange}
                    />
                </section>

                {/* Optimization History */}
                <section className="manager-section">
                    <OptimizationHistory
                        notification={notification}
                        setNotification={setNotification}
                        userRole={userRole}
                        refreshKey={refreshKey}
                    />
                </section>

                {/* Add Rule Modal */}
                <AddRuleModal
                    isOpen={showAddRuleModal}
                    onClose={() => {
                        setShowAddRuleModal(false);
                        setEditingRule(null);
                    }}
                    onSubmit={handleAddRule}
                    loading={addingRule}
                    editingRule={editingRule}
                />
            </div>
        </div>
    );
};

export default OptimalizationPage;
