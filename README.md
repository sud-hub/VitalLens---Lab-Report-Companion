# VitalLens - Lab Report Companion

A web application for digitizing, storing, and tracking laboratory test results using offline OCR technology.

## Overview

Lab Report Companion enables users to upload photos or PDF scans of lab reports, extracts test values using offline OCR, stores them in a structured database, and provides historical tracking with educational insights.

### Supported Lab Panels

The system exclusively supports three lab panels:
- **Complete Blood Count (CBC)**: WBC, RBC, Hemoglobin, Hematocrit, Platelets, MCV
- **Metabolic Panel (CMP/BMP)**: Glucose, BUN, Creatinine, Sodium, Potassium, Chloride, CO2, Calcium
- **Lipid Panel**: Total Cholesterol, LDL, HDL, Triglycerides

### Key Features

- **Offline OCR Processing**: Uses PaddleOCR for local text extraction (no external API calls)
- **Historical Tracking**: View test results over time with interactive charts
- **Educational Insights**: Get general information about your test results with trend analysis
- **Privacy-Focused**: All data stored locally with JWT-based authentication
- **Educational Only**: All information includes disclaimers that it is non-diagnostic

## Technology Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy with Alembic migrations
- PostgreSQL (production) / SQLite (development)
- PaddleOCR for offline OCR
- JWT authentication with bcrypt password hashing

### Frontend
- React 18 with TypeScript
- Vite build tool
- Axios for HTTP requests
- Recharts for data visualization
- React Router for navigation

## Prerequisites

### Backend Requirements
- Python 3.11 or higher
- pip (Python package manager)

### Frontend Requirements
- Node.js 18 or higher
- npm (Node package manager)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sud-hub/VitalLens---Lab-Report-Companion.git
cd lab-report-companion
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
python -m venv .venv
```

**Activate virtual environment:**

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

**Install packages:**
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DATABASE_URL=sqlite:///./lab_companion.db

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration (optional)
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

**Important**: For production, use a strong random secret key and PostgreSQL database.

#### Initialize Database

Run migrations to create database tables:

```bash
python -m alembic upgrade head
```

#### Seed Database with Test Data

Populate the database with lab panels, test types, and aliases:

```bash
python seed_data.py
```

This creates:
- 3 lab panels (CBC, METABOLIC, LIPID)
- All test types with reference ranges
- Common test name aliases for parsing

### 3. Frontend Setup

#### Install Node Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
VITE_API_URL=http://localhost:8000
```

## Running the Application

### Start Backend Server

From the `backend` directory with virtual environment activated:

```bash
uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`

API documentation (Swagger UI): `http://localhost:8000/docs`

### Start Frontend Development Server

From the `frontend` directory:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage Guide

### 1. Register an Account

1. Navigate to `http://localhost:5173`
2. Click "Register" or go to `/register`
3. Enter your email and password (minimum 8 characters)
4. Click "Register"

### 2. Log In

1. Go to the login page
2. Enter your registered email and password
3. Click "Login"
4. You'll be redirected to the dashboard

### 3. Upload a Lab Report

1. On the dashboard, find the "Upload Report" section
2. Click "Choose File" and select a lab report image (JPEG, PNG) or PDF
3. Maximum file size: 10MB
4. Click "Upload"
5. Wait for OCR processing and parsing to complete
6. View the extracted test results

### 4. View Test History

1. Select a lab panel (CBC, Metabolic, or Lipid)
2. Choose a specific test from the dropdown
3. View the historical chart showing your test values over time
4. Hover over data points to see exact values and dates

### 5. View Latest Insights

1. After selecting a test, scroll to the "Latest Insight" card
2. See your most recent test value with status (LOW, NORMAL, HIGH)
3. View trend indicator (improving, worsening, stable)
4. Read educational guidance about the test
5. **Important**: Always read the disclaimer - this is educational information, not medical advice

## Database Management

### Create a New Migration

After modifying database models:

```bash
cd backend
python -m alembic revision --autogenerate -m "description of changes"
```

### Apply Migrations

```bash
python -m alembic upgrade head
```

### Rollback Migration

```bash
python -m alembic downgrade -1
```

### Reset Database

```bash
python -m alembic downgrade base
python -m alembic upgrade head
python seed_data.py
```

## Testing

### Backend Tests

Run all tests:
```bash
cd backend
python -m pytest
```

Run with verbose output:
```bash
python -m pytest -v
```

Run specific test file:
```bash
python -m pytest tests/test_lab_parser.py -v
```

Run specific test:
```bash
python -m pytest tests/test_lab_parser.py::TestLabParser::test_parse_cbc -v
```

### Frontend Tests

Run tests:
```bash
cd frontend
npm run test
```

## Project Structure

```
lab-report-companion/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   ├── core/           # Configuration, security
│   │   ├── crud/           # Database operations
│   │   ├── db/             # Database models
│   │   ├── ocr/            # OCR engine
│   │   ├── parsing/        # Lab report parsing
│   │   ├── rules/          # Business rules
│   │   └── schemas/        # Pydantic schemas
│   ├── alembic/            # Database migrations
│   ├── tests/              # Test files
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── App.tsx        # Root component
│   └── package.json       # Node dependencies
└── README.md              # This file
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### Users
- `GET /users/me` - Get current user profile (protected)

### Reports
- `POST /reports/upload` - Upload lab report (protected)

### Panels & Tests
- `GET /panels` - Get all lab panels (protected)
- `GET /panels/{panel_key}/tests` - Get tests for a panel (protected)

### Test Results
- `GET /tests/{test_key}/history` - Get test history (protected)
- `GET /tests/{test_key}/latest-insight` - Get latest insight (protected)

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError` when running the backend
- **Solution**: Ensure virtual environment is activated and dependencies are installed

**Issue**: Database connection errors
- **Solution**: Check `DATABASE_URL` in `.env` file and ensure database exists

**Issue**: OCR processing fails
- **Solution**: Ensure PaddleOCR dependencies are installed correctly. On Windows, you may need Visual C++ redistributables.

### Frontend Issues

**Issue**: API requests fail with CORS errors
- **Solution**: Check `BACKEND_CORS_ORIGINS` in backend `.env` includes your frontend URL

**Issue**: `npm install` fails
- **Solution**: Ensure Node.js version is 18 or higher

**Issue**: Charts not displaying
- **Solution**: Check browser console for errors and ensure test data exists

## Important Disclaimers

⚠️ **Medical Disclaimer**: This application provides educational information only and is NOT a medical diagnosis tool. All insights and guidance are for general educational purposes. Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment decisions.

⚠️ **Data Accuracy**: OCR technology may not perfectly extract all values from lab reports. Always verify extracted values against your original lab report.

⚠️ **Privacy**: This application stores data locally. For production use, implement appropriate security measures and comply with healthcare data regulations (HIPAA, GDPR, etc.).

## Development

### Backend Development

The backend follows a layered architecture:
1. **API Layer**: FastAPI routers handle HTTP requests
2. **Business Logic**: OCR, parsing, and rules engines
3. **Data Access**: CRUD operations abstract database access
4. **Models**: SQLAlchemy ORM models define database schema

### Frontend Development

The frontend is a single-page application:
- **Pages**: Top-level route components
- **Components**: Reusable UI components
- **API Client**: Axios instance with JWT interceptors

### Adding New Lab Panels

To add support for additional lab panels:
1. Add panel to seed data in `seed_data.py`
2. Add test types with reference ranges
3. Add test aliases for parsing variations
4. Update parser logic in `app/parsing/lab_parser.py`
5. Add guidance messages in `app/rules/guidance_engine.py`
