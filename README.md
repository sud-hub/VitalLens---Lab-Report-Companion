# VitalLens - Lab Report Companion

A web application for digitizing, storing, and tracking laboratory test results with AI-powered extraction and personalized health insights.

## Overview

VitalLens Lab Report Companion enables users to upload photos or PDF scans of lab reports, extracts test values and patient demographics using Google's Gemini AI, stores them in a structured database, and provides personalized historical tracking with educational insights tailored to individual characteristics.

### Supported Lab Panels

The system exclusively supports three lab panels:
- **Complete Blood Count (CBC)**: WBC, RBC, Hemoglobin, Hematocrit, Platelets, MCV
- **Metabolic Panel (CMP/BMP)**: Glucose, BUN, Creatinine, Sodium, Potassium, Chloride, CO2, Calcium
- **Lipid Panel**: Total Cholesterol, LDL, HDL, Triglycerides

### Key Features

- **AI-Powered Extraction**: Uses Google Gemini 2.0 Flash for accurate test result and patient demographic extraction
- **Personalized Reference Ranges**: Gender and age-specific reference ranges for more accurate health assessments
- **Historical Tracking**: View test results over time with interactive charts
- **Educational Insights**: Get personalized information about your test results with trend analysis
- **Privacy-Focused**: All data stored locally with JWT-based authentication
- **Educational Only**: All information includes disclaimers that it is non-diagnostic
- **Special Status Indicators**: PROTECTIVE status for excellent HDL levels (≥60 mg/dL)

## Technology Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy with Alembic migrations
- PostgreSQL (production) / SQLite (development)
- **Google Gemini 2.0 Flash** for AI-powered extraction
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

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration (optional)
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

**Important**: 
- Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- For production, use a strong random secret key and PostgreSQL database
- Never commit your `.env` file to version control

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
5. Wait for AI-powered extraction and parsing to complete
6. The system will automatically extract:
   - Test results (name, value, unit)
   - Patient demographics (gender and age, if available)
7. View the extracted test results with personalized status indicators

### 4. View Test History

1. Select a lab panel (CBC, Metabolic, or Lipid)
2. Choose a specific test from the dropdown
3. View the historical chart showing your test values over time
4. Hover over data points to see exact values and dates

### 5. View Latest Insights

1. After selecting a test, scroll to the "Latest Insight" card
2. See your most recent test value with personalized status:
   - **Status indicators**: LOW, NORMAL, HIGH, CRITICAL_LOW, CRITICAL_HIGH
   - **Special status**: PROTECTIVE for excellent HDL levels (≥60 mg/dL)
3. View trend indicator (improving, worsening, stable)
4. Read educational guidance tailored to your demographics
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
VitalLens---Lab-Report-Companion/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   ├── core/           # Configuration, security
│   │   ├── crud/           # Database operations
│   │   ├── db/             # Database models
│   │   ├── ocr/            # Gemini AI extraction engine
│   │   ├── parsing/        # Lab report parsing
│   │   ├── rules/          # Business rules & personalized ranges
│   │   │   ├── guidance_engine.py
│   │   │   ├── reference_ranges.py
│   │   │   └── personalized_ranges.py  # Gender/age-specific ranges
│   │   └── schemas/        # Pydantic schemas
│   ├── alembic/            # Database migrations
│   │   └── versions/
│   │       ├── 001_initial_migration.py
│   │       └── 002_add_patient_demographics.py
│   ├── tests/              # Test files
│   ├── seed_data.py        # Database seeding script
│   ├── requirements.txt    # Python dependencies
│   ├── PERSONALIZED_RANGES.md      # Feature documentation
│   └── IMPLEMENTATION_SUMMARY.md   # Implementation details
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

## Personalized Reference Ranges

VitalLens uses **gender and age-specific reference ranges** for more accurate health assessments:

### Gender-Specific Ranges

- **RBC (Red Blood Cells)**:
  - Males: 4.5 - 5.9 (10^6/µL)
  - Females: 4.0 - 5.2 (10^6/µL)

- **Hemoglobin**:
  - Males: 13.5 - 17.5 (g/dL)
  - Females: 12.0 - 15.5 (g/dL)

- **Hematocrit**:
  - Males: 40.0 - 54.0 (%)
  - Females: 36.0 - 46.0 (%)

- **HDL Cholesterol**:
  - Males: ≥ 40 mg/dL
  - Females: ≥ 50 mg/dL
  - **PROTECTIVE status**: ≥ 60 mg/dL (both genders)

### Age Adjustments

For patients over 60 years, reference ranges are automatically adjusted to account for normal aging processes.

### Fallback Behavior

If patient demographics (gender/age) are not detected in the lab report, the system uses standard default reference ranges.

For more details, see [`backend/PERSONALIZED_RANGES.md`](backend/PERSONALIZED_RANGES.md)

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError` when running the backend
- **Solution**: Ensure virtual environment is activated and dependencies are installed

**Issue**: Database connection errors
- **Solution**: Check `DATABASE_URL` in `.env` file and ensure database exists

**Issue**: Gemini API errors or extraction fails
- **Solution**: 
  - Verify `GEMINI_API_KEY` is set correctly in `.env`
  - Check your API key is valid at [Google AI Studio](https://aistudio.google.com/app/apikey)
  - Ensure you have API quota available
  - Check internet connectivity (Gemini requires external API calls)

**Issue**: Patient demographics not extracted
- **Solution**: 
  - Ensure lab report clearly shows patient gender and age
  - System will fall back to default ranges if demographics aren't found
  - Check the report notes field for extraction details

### Frontend Issues

**Issue**: API requests fail with CORS errors
- **Solution**: Check `BACKEND_CORS_ORIGINS` in backend `.env` includes your frontend URL

**Issue**: `npm install` fails
- **Solution**: Ensure Node.js version is 18 or higher

**Issue**: Charts not displaying
- **Solution**: Check browser console for errors and ensure test data exists

## Important Disclaimers

⚠️ **Medical Disclaimer**: This application provides educational information only and is NOT a medical diagnosis tool. All insights and guidance are for general educational purposes. Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment decisions.

⚠️ **Data Accuracy**: AI extraction may not perfectly extract all values from lab reports. Always verify extracted values against your original lab report.

⚠️ **Privacy & Data Security**: 
- This application stores data locally in your database
- **Gemini API**: Currently uses Google's Gemini API which requires sending lab report images to Google's servers
- For production use, implement appropriate security measures and comply with healthcare data regulations (HIPAA, GDPR, etc.)
- Consider the OCR engine enhancement (see Future Enhancements) for fully offline, privacy-focused processing

⚠️ **API Costs**: Google Gemini API usage may incur costs depending on your usage volume. Monitor your API usage at [Google AI Studio](https://aistudio.google.com/app/apikey).

## Future Enhancements

### 1. Advanced OCR Engine (High Priority)

**Current Implementation**: Uses Google Gemini API for extraction
- ✅ **Pros**: Highly accurate, extracts demographics automatically, minimal setup
- ❌ **Cons**: Requires external API calls, data sent to Google servers, API costs, internet dependency

**Planned Enhancement**: Offline OCR with PaddleOCR or Tesseract
- ✅ **Benefits**:
  - **Enhanced Data Security**: All processing happens locally, no data leaves your server
  - **HIPAA/GDPR Compliance**: Better suited for healthcare data regulations
  - **No API Costs**: Completely free after initial setup
  - **Offline Capability**: Works without internet connection
  - **Full Data Control**: Complete ownership of processing pipeline
  - **Privacy-First**: Ideal for sensitive medical information
- ⚠️ **Trade-offs**:
  - Requires more complex setup (OCR dependencies, models)
  - May need additional processing for demographic extraction
  - Potentially lower accuracy on poor-quality images
  - Higher computational requirements on server

**Implementation Path**:
1. Integrate PaddleOCR or Tesseract for text extraction
2. Develop custom NLP pipeline for structured data extraction
3. Add pattern matching for patient demographics
4. Implement fallback to Gemini for complex cases (optional)
5. Make extraction engine configurable (OCR vs Gemini)

### 2. Additional Personalization Features

- **Pediatric Reference Ranges**: Age-specific ranges for children
- **Pregnancy-Specific Ranges**: Adjusted ranges for pregnant women
- **Ethnicity Considerations**: Population-specific reference adjustments
- **BMI-Based Modifications**: Weight-adjusted ranges for certain tests
- **Comorbidity Awareness**: Adjusted ranges for diabetes, kidney disease, etc.

### 3. Enhanced Analytics

- **Predictive Trends**: ML-based prediction of future test values
- **Risk Scoring**: Comprehensive health risk assessment
- **Correlation Analysis**: Identify relationships between different tests
- **Anomaly Detection**: Flag unusual patterns in test results

### 4. Additional Lab Panels

- Thyroid Function Tests (TSH, T3, T4)
- Liver Function Tests (ALT, AST, Bilirubin)
- Kidney Function Tests (eGFR, Albumin)
- Vitamin Levels (D, B12, Folate)
- Hormone Panels

### 5. User Experience Improvements

- **Mobile App**: Native iOS/Android applications
- **Report Templates**: Support for multiple lab formats
- **Batch Upload**: Process multiple reports at once
- **Export Features**: PDF reports, CSV exports
- **Sharing**: Secure sharing with healthcare providers

### 6. Integration Features

- **EHR Integration**: Connect with electronic health records
- **Doctor Portal**: Allow physicians to review patient results
- **Appointment Scheduling**: Book follow-ups based on results
- **Medication Tracking**: Link test results with medications

## Development

### Backend Development

The backend follows a layered architecture:
1. **API Layer**: FastAPI routers handle HTTP requests
2. **Business Logic**: AI extraction, parsing, and rules engines
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
4. Update Gemini prompt in `app/ocr/gemini_engine.py` (or parser logic if using OCR)
5. Add guidance messages in `app/rules/guidance_engine.py`
6. Consider gender/age-specific ranges in `app/rules/personalized_ranges.py`

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug fixes
- New features (especially OCR engine implementation!)
- Documentation improvements
- Test coverage
- Performance optimizations

## License

This project is for educational purposes. Please ensure compliance with healthcare data regulations in your jurisdiction before deploying in production.

---

**Built with ❤️ for better health tracking and education**
