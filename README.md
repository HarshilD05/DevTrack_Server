# Jira Clone Flask Server

A Flask-based server using PyMongo that follows the MVC architecture for a Jira Storyboard clone.

## Features

- User authentication (register, login, token verification)
- Project management (create, read, update, delete)
- Task management (create, read, update, delete)
- Task status tracking and approval workflow
- File upload for tasks
- Role-based access control (admin, participant)

## Setup Instructions

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and update the configuration
6. Start MongoDB server
7. Run the application: `python app.py`

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register a new user
- POST `/api/auth/login` - Login user
- GET `/api/auth/verify-token` - Verify JWT token
- POST `/api/auth/change-password` - Change password

### Projects
- POST `/api/projects` - Create a new project
- GET `/api/projects` - Get all user projects
- GET `/api/projects/<project_id>` - Get specific project
- PUT `/api/projects/<project_id>` - Update project
- POST `/api/projects/<project_id>/admin` - Add admin to project
- POST `/api/projects/<project_id>/participant` - Add participant to project
- PUT `/api/projects/<project_id>/stages` - Update project stages
- DELETE `/api/projects/<project_id>` - Delete project

### Tasks
- POST `/api/tasks/project/<project_id>` - Create task in project
- GET `/api/tasks/project/<project_id>` - Get all tasks in project
- GET `/api/tasks/user` - Get all tasks assigned to current user
- GET `/api/tasks/<task_id>` - Get specific task
- PUT `/api/tasks/<task_id>` - Update task
- POST `/api/tasks/<task_id>/request-status` - Request task status change
- POST `/api/tasks/approve-status/<request_id>` - Approve status change request
- DELETE `/api/tasks/<task_id>` - Delete task

### Users
- GET `/api/users/profile` - Get current user profile

## Database Schema

### Users
- `_id`: ObjectId
- `username`: String
- `email`: String
- `password_hash`: String
- `verified`: Boolean
- `created_at`: DateTime
- `updated_at`: DateTime

### Projects
- `_id`: ObjectId
- `name`: String
- `description`: String
- `creator_id`: ObjectId
- `admin_users`: Array of ObjectId
- `participants`: Array of ObjectId
- `stages`: Array of String
- `created_at`: DateTime
- `updated_at`: DateTime

### Tasks
- `_id`: ObjectId
- `project_id`: ObjectId
- `title`: String
- `description`: String
- `assigned_users`: Array of ObjectId
- `status`: String
- `files`: Array of Object
- `created_at`: DateTime
- `updated_at`: DateTime
- `status_history`: Array of Object

### Status Change Requests
- `_id`: ObjectId
- `task_id`: ObjectId
- `project_id`: ObjectId
- `requested_by`: ObjectId
- `current_status`: String
- `requested_status`: String
- `created_at`: DateTime
- `status`: String
- `approved_by`: ObjectId (optional)
- `approved_at`: DateTime (optional)
