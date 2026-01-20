import React, { useState, useCallback } from 'react';
import { Zap } from 'lucide-react';
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
    const [notification, setNotification] = useState(null);
    const [addingRule, setAddingRule] = useState(false);
    const [refreshKey, setRefreshKey] = useState(0);

    const handleAddRule = async (formData) => {
        setAddingRule(true);
        try {
            const csrftoken = getCookie('csrftoken');
            const response = await fetch(`${API_BASE_URL}/api/optimization/rules/`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) throw new Error('Failed to add rule');

            setNotification({ type: 'success', message: 'Reguła dodana pomyślnie.' });
            setShowAddRuleModal(false);
            setRefreshKey(prev => prev + 1);
        } catch (error) {
            console.error('Error adding rule:', error);
            setNotification({ type: 'error', message: 'Nie udało się dodać reguły.' });
        } finally {
            setAddingRule(false);
            setTimeout(() => setNotification(null), 4000);
        }
    };

    const handleRefresh = useCallback(() => {
        setRefreshKey(prev => prev + 1);
    }, []);

    return (
        <div className="optimization-page">
            <div className="optimization-content">
                {/* Page Header */}
                <div className="page-header">
                    <div className="page-header-content">
                        <div className="page-header-icon">
                            <Zap size={32} />
                        </div>
                        <div>
                            <h1 className="page-title">Panel Optymalizacji</h1>
                            <p className="page-subtitle">Zarządzanie regułami optymalizacji i preferencjami urządzeń</p>
                        </div>
                    </div>
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
                        onRefresh={handleRefresh}
                        notification={notification}
                        setNotification={setNotification}
                        userRole={userRole}
                    />
                </section>

                {/* Preference Manager */}
                <section className="manager-section">
                    <PreferenceManager
                        notification={notification}
                        setNotification={setNotification}
                        userRole={userRole}
                        userId={userId}
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
                    onClose={() => setShowAddRuleModal(false)}
                    onSubmit={handleAddRule}
                    loading={addingRule}
                />
            </div>
        </div>
    );
};

export default OptimalizationPage;
