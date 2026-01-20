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
                alert("Błąd logowania!");
            }
        } catch (error) {
            console.error("Login error:", error);
            alert("Błąd połączenia z serwerem.")
        }
    };

    return (
        <div className="login-container">
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
                        <h1 className="login-title">Witaj ponownie</h1>
                        <p className="login-subtitle">Zaloguj się, aby uzyskać dostęp do panelu</p>
                    </div>

                    <form onSubmit={handleSubmit} className="login-form">
                        <div className="form-group">
                            <label className="form-label">Nazwa użytkownika</label>
                            <div className="input-wrapper">
                                <User className="input-icon" size={20} />
                                <input
                                    type="text"
                                    placeholder="Wprowadź login"
                                    className="form-input"
                                    value={credentials.username}
                                    onChange={e => setCredentials({ ...credentials, username: e.target.value })}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Hasło</label>
                            <div className="input-wrapper">
                                <Lock className="input-icon" size={20} />
                                <input
                                    type="password"
                                    placeholder="Wprowadź hasło"
                                    className="form-input"
                                    value={credentials.password}
                                    onChange={e => setCredentials({ ...credentials, password: e.target.value })}
                                />
                            </div>
                        </div>

                        <button type="submit" className="login-btn">
                            Zaloguj <LogIn size={18} />
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;