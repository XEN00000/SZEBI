
import React, { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { Menu, X, Rocket, Zap, BarChart } from 'lucide-react';

const Layout = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const location = useLocation();

    const navItems = [
        { name: 'Optimization', path: '/optimization', icon: Rocket },
        { name: 'Alarms', path: '/alarms', icon: Zap },
        { name: 'Analysis', path: '/analysis', icon: BarChart },
    ];

    const isActive = (path) => location.pathname.startsWith(path);

    return (
        <div className="app-container">
            {/* Navigation */}
            <nav className="navbar">
                <div className="nav-content">
                    <div className="nav-header">
                        <Link to="/" className="logo-container">
                            <div className="logo-icon">
                                <span>S</span>
                            </div>
                            <span className="logo-text">SZEBI</span>
                        </Link>

                        <button
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            className="mobile-menu-btn"
                        >
                            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>

                    <div className={`nav-links ${isMenuOpen ? 'open' : ''}`}>
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.name}
                                    to={item.path}
                                    className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
                                    onClick={() => setIsMenuOpen(false)}
                                >
                                    <Icon size={18} />
                                    <span>{item.name}</span>
                                </Link>
                            );
                        })}
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="main-content">
                <div className="content-wrapper">
                    <Outlet />
                </div>
            </main>

            {/* Footer */}
            <footer className="footer">
                <div className="footer-content">
                    <div className="footer-left">
                        © 2024 SZEBI Project. Intelligent Energy Management.
                    </div>
                    <div className="footer-right">
                        <a href="#">Documentation</a>
                        <a href="#">Support</a>
                        <a href="#">Github</a>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default Layout;
