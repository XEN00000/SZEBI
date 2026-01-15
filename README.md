# SZEBI

The goal of the SZEBI project is to create an intelligent IT system for energy management in commercial and public buildings. The system is designed to optimize energy consumption, minimize operational costs, improve user comfort, and support sustainable development.

---

# Run Instructions (Docker)

## Requirements
- Docker  
- Docker Compose  
- Git  

## Clone the repository
```bash
git clone https://github.com/XEN00000/SZEBI.git
cd SZEBI
```

## Start the application
```bash
docker compose up --build
```

---

## Access URLs

**Frontend (Main Application)**  
```
http://localhost:5173
```
> This is the primary entry point for users and the default URL that should be used during normal operation.

**Backend API**  
```
http://localhost:8000
```

**Admin Panel**  
```
http://localhost:8000/admin/
```

---

## Create an admin user (on a separate terminal)
```bash
docker compose exec web python manage.py createsuperuser
```