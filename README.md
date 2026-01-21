# SZEBI
**System Zarządzania Energią w Budynkach Inteligentnych**

The SZEBI project aims to create an intelligent IT system for energy management in commercial and public buildings. The system is designed to optimize energy consumption, minimize operational costs, improve user comfort, and support sustainable development through advanced monitoring, data analysis, and predictive control.

---

## Technology Stack

- **Backend:** Django 5.2, Django REST Framework
- **Database:** PostgreSQL
- **Frontend:** React 19, Vite, Lucide React
- **Async Processing:** Celery, Redis
- **Infrastructure:** Docker, Docker Compose
- **IoT / Messaging:** Mosquitto (MQTT)
- **Data Science:** Pandas, Scikit-learn, XGBoost, TensorFlow
- **Utilities:** PyWebPush, ReportLab

---

## Architecture & Code Ownership

The system is modularized into distinct domains, each handled by specific teams using a Domain-Driven Design approach.

| Module | Directory | Responsibility | Code Owners |
|--------|-----------|----------------|-------------|
| **Core** | `core/` | System architecture, User management, Authentication/Authorization (RBAC). | Jęcek Łukasz, Murza Łukasz |
| **Simulation** | `simulation/` | Simulation of building environment, devices, and energy usage patterns. | Kowalczyk Tobiasz, Majkowski Kacper |
| **Acquisition** | `acquisition/` | Data ingestion from sensors, MQTT message processing, raw data storage. | Depcik Magdalena, Świercz Alicja |
| **Analysis** | `analysis/` | Historical data analysis, statistical reporting, report generation (PDF/PNG). | Adamczyk Zuzanna, Silchankava Nadzeya |
| **Forecasting** | `forecasting/` | Predictive modeling for energy consumption and production. | Synowiec Magdalena, Szczęsna Beata |
| **Optimization** | `optimization/` | Rule-based control, optimization algorithms, device scheduling. | Bartoszek Ireneusz, Kaźmierczak Szymon |
| **Alarms** | `alarms/` | Anomaly detection, alert rules management, notification delivery. | Kaźmierczak Aleksander, Wasiel Filip |

---

## System Roles

The system operates on a Role-Based Access Control (RBAC) model. Roles are defined in the `core` module and can be managed by a Superuser via the Admin Panel.

| Role Display Name | Codename | Description |
|-------------------|----------|-------------|
| **Administrator Budynku** | `building_admin` | Full system control, user management, and configuration. |
| **Inżynier Utrzymania Ruchu** | `maintenance_engineer` | Handling alarms, device monitoring, and technical maintenance. |
| **Dostawca Energii** | `energy_provider` | External stakeholder access to energy consumption and forecasts. |
| **Pracownik** | `worker` | Basic system access with limited visibility. |

> **Note:** A Superuser can view, create, and assign roles to users via the [Admin Panel](http://localhost:8000/admin/).

---

## Repository Structure

```text
SZEBI/
├── acquisition/       # Data ingestion & sensor handling
├── alarms/            # Alert definitions & notification logic
├── analysis/          # Reporting & data visualization logic
├── core/              # Project settings, Auth & Base models
├── forecasting/       # ML models & prediction logic
├── frontend/          # React + Vite application
├── mosquitto/         # MQTT Broker configuration
├── optimization/      # Control rules & optimization engines
├── simulation/        # Environment & device simulation
├── szebi_core/        # Application entry point & configuration
├── docker-compose.yml # Main orchestration file
├── manage.py          # Django management script
└── requirements.txt   # Python dependencies
```

---

## Getting Started

### Prerequisites
*   **Docker Desktop** (latest version recommended)
*   **Git**

### Installation & Execution

1.  **Clone the repository**
    ```bash
    git clone https://github.com/XEN00000/SZEBI.git
    cd SZEBI
    ```

2.  **Configuration (.env)**
    Create a `.env` file in the root directory. This is required for the application to start.
    
    ```ini
    DEBUG=1
    DJANGO_PRODUCTION=0
    
    # Database Configuration
    POSTGRES_DB=szebi_db
    POSTGRES_USER=szebi_user
    POSTGRES_PASSWORD=changeme
    POSTGRES_HOST=db
    POSTGRES_PORT=5432
    
    # Security
    ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
    
    # Email Configuration (Example: Gmail SMTP)
    EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_USE_TLS=1
    EMAIL_USE_SSL=0
    EMAIL_HOST_USER=your_email@gmail.com
    EMAIL_HOST_PASSWORD=your_app_password
    DEFAULT_FROM_EMAIL=your_email@gmail.com
    ```

3.  **Start the application**
    Use Docker Compose to build and start all services (Backend, Frontend, DB, MQTT, Redis, Celery).
    ```bash
    docker compose up --build
    ```

4.  **Create an Admin User**
    Once the containers are running, open a new terminal window to create a superuser for accessing the Django Admin panel.
    ```bash
    docker compose exec web python manage.py createsuperuser
    ```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | `http://localhost:5173` | Main User Interface (React) |
| **Backend API** | `http://localhost:8000` | REST API Roots |
| **Admin Panel** | `http://localhost:8000/admin/` | Django Administration |

---