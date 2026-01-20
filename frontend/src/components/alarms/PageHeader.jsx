import React from 'react';
import { Bell } from 'lucide-react';

const PageHeader = ({ title, subtitle }) => (
    <div className="page-header">
        <div className="page-header-content">
            <div className="page-header-icon">
                <Bell size={32} />
            </div>
            <div>
                <h1 className="page-title">{title}</h1>
                <p className="page-subtitle">{subtitle}</p>
            </div>
        </div>
    </div>
);

export default PageHeader;
