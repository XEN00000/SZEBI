import React from 'react';
import { AlertTriangle, CheckCircle2, X } from 'lucide-react';

const NotificationToast = ({ notification, onClose }) => {
    if (!notification) return null;

    return (
        <div className={`notification-toast notification-${notification.type}`}>
            <div className="notification-content">
                {notification.type === 'success' ? (
                    <CheckCircle2 size={20} />
                ) : (
                    <AlertTriangle size={20} />
                )}
                <span>{notification.message}</span>
            </div>
            <button onClick={onClose} className="notification-close">
                <X size={16} />
            </button>
        </div>
    );
};

export default NotificationToast;
