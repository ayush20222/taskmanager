# Task Manager API

A simple Django REST API for managing tasks with user authentication.

## Features

- User registration and authentication using JWT
- Full CRUD operations for tasks
- Pagination for task listing
- Filter tasks by completion status
- Search tasks by title and description
- API documentation with Swagger and ReDoc
- Unit tests for all endpoints

## Installation

1. Clone the repository
2. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate  

## API Documentation
Swagger UI: http://localhost:8000/swagger/

ReDoc: http://localhost:8000/redoc/

## API Endpoints
Authentication
POST /api/auth/register/ - Register a new user

POST /api/auth/login/ - Login and get JWT token

Tasks (Requires Authentication)
GET /api/tasks/ - List all tasks (paginated)

POST /api/tasks/ - Create a new task

GET /api/tasks/{id}/ - Get task details

PUT /api/tasks/{id}/ - Update a task

DELETE /api/tasks/{id}/ - Delete a task

## Steps to Run:

1. Create a new Django project and app:
```bash
django-admin startproject task_manager
cd task_manager
python manage.py startapp tasks
