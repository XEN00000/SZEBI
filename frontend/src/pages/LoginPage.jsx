import React, { useState, useEffect } from 'react';
import { User, Lock, LogIn, Rocket, Zap, BarChart, Database, TrendingUp } from 'lucide-react';
import { getCookie } from '../utils/csrf';

const LoginPage = ({ onLoginSuccess }) => {
    const [credentials, setCredentials] = useState({ username: '', password: '' });

    const handleSubmit = async (e) => {
        e.preventDefault();

        const csrftoken = getCookie('csrftoken');

        try {
            const response = await fetch('http://localhost:8000/api/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                credentials: 'include',
                body: JSON.stringify(credentials),
            });

            if (response.ok) {
                const data = await response.json();
                onLoginSuccess(data.user);
            } else {
                alert("Login error!");
            }
        } catch (error) {
            console.error("Login error:", error);
            alert("Connection error.")
        }
    };

    return (
        <div className="login-container">
            <div className="hero-background-effect" aria-hidden="true" style={{ top: '0', zIndex: 0 }}>
                <div className="gradient-blob" />
            </div>
            <nav className="navbar">
                <div className="nav-content">
                    <div className="nav-header">
                        <div className="logo-container">
                            <div className="logo-icon"><span>S</span></div>
                            <span className="logo-text">SZEBI</span>
                        </div>
                    </div>

                    <div className="nav-links">
                        <div className="nav-item">
                            <Rocket size={18} />
                            <span>Optimization</span>
                        </div>
                        <div className="nav-item">
                            <Zap size={18} />
                            <span>Alarms</span>
                        </div>
                        <div className="nav-item">
                            <BarChart size={18} />
                            <span>Analysis</span>
                        </div>
                        <div className="nav-item">
                            <Database size={18} />
                            <span>Acquisition</span>
                        </div>
                        <div className="nav-item">
                            <TrendingUp size={18} />
                            <span>Forecasting</span>
                        </div>
                    </div>
                </div>
            </nav>

            <div className="login-content">
                <div className="login-card">
                    <div className="login-header">
                        <h1 className="login-title">Welcome back</h1>
                        <p className="login-subtitle">Log in to access the dashboard</p>
                    </div>

                    <form onSubmit={handleSubmit} className="login-form">
                        <div className="form-group">
                            <label className="form-label">Username</label>
                            <div className="input-wrapper">
                                <input
                                    type="text"
                                    placeholder="Enter username"
                                    className="form-input"
                                    value={credentials.username}
                                    onChange={e => setCredentials({ ...credentials, username: e.target.value })}
                                />
                                <User className="input-icon" size={20} />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Password</label>
                            <div className="input-wrapper">
                                <input
                                    type="password"
                                    placeholder="Enter password"
                                    className="form-input"
                                    value={credentials.password}
                                    onChange={e => setCredentials({ ...credentials, password: e.target.value })}
                                />
                                <Lock className="input-icon" size={20} />
                            </div>
                        </div>

                        <button type="submit" className="login-btn">
                            Login <LogIn size={18} />
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;