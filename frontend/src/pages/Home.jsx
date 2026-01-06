
import React from 'react';
import { ArrowRight, Activity, TrendingUp, Shield } from 'lucide-react';
import { Link } from 'react-router-dom';

const FeatureCard = ({ icon: Icon, title, description, link, colorClass }) => (
    <Link to={link} className={`feature-card ${colorClass}`}>
        <div className="card-bg-icon">
            <Icon size={120} />
        </div>

        <div className="card-content">
            <div className="card-icon-wrapper">
                <Icon size={32} />
            </div>
            <h3 className="card-title">
                {title}
            </h3>
            <p className="card-description">
                {description}
            </p>

            <div className="card-cta">
                Explore Module <ArrowRight size={16} className="ml-1" />
            </div>
        </div>
    </Link>
);

const Home = () => {
    return (
        <div className="home-container">
            {/* Hero Section */}
            <div className="hero-section">
                <div className="hero-content">
                    <div className="hero-text-wrapper">
                        <h1 className="hero-title">
                            Intelligent Energy Management
                        </h1>
                        <p className="hero-subtitle">
                            Optimize consumption, minimize costs, and ensure comfort with SZEBI's advanced AI-powered control systems.
                        </p>
                        <div className="hero-buttons">
                            <Link to="/optimization" className="btn btn-primary">
                                Get Started
                            </Link>
                            <a href="#" className="btn btn-link">
                                Learn more <span aria-hidden="true">→</span>
                            </a>
                        </div>
                    </div>
                </div>

                {/* Background gradient effects */}
                <div className="hero-background-effect" aria-hidden="true">
                    <div className="gradient-blob" />
                </div>
            </div>

            {/* Feature Grid */}
            <div className="features-grid">
                <FeatureCard
                    icon={TrendingUp}
                    title="Optimization"
                    description="AI-driven algorithms to schedule and optimize energy usage across all building systems."
                    link="/optimization"
                    colorClass="theme-emerald"
                />
                <FeatureCard
                    icon={Shield}
                    title="Alarms & Safety"
                    description="Real-time monitoring and alert systems to detect anomalies and ensure operational safety."
                    link="/alarms"
                    colorClass="theme-amber"
                />
                <FeatureCard
                    icon={Activity}
                    title="Deep Analysis"
                    description="Comprehensive data analytics and reporting tools to visualize consumption patterns."
                    link="/analysis"
                    colorClass="theme-purple"
                />
            </div>

            {/* Stats Section */}
            <div className="stats-section">
                <div className="stats-container">
                    <dl className="stats-grid">
                        {[
                            { name: 'Energy Savings', value: '15-30%' },
                            { name: 'Modules Active', value: '5+' },
                            { name: 'Update Frequency', value: 'Real-time' },
                        ].map((stat) => (
                            <div key={stat.name} className="stat-item">
                                <dt className="stat-label">{stat.name}</dt>
                                <dd className="stat-value">{stat.value}</dd>
                            </div>
                        ))}
                    </dl>
                </div>
            </div>
        </div>
    );
};

export default Home;
