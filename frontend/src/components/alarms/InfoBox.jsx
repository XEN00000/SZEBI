import React from 'react';
import { Info } from 'lucide-react';

const InfoBox = () => (
    <div className="info-box">
        <Info size={20} />
        <div>
            <h3 className="info-title">Alarm Rules Management</h3>
            <p className="info-text">
                Create monitoring rules that automatically generate alerts 
                when metric values exceed defined thresholds.
            </p>
        </div>
    </div>
);

export default InfoBox;
