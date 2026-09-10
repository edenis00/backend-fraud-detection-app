# Fraud Detection Backend API

A FastAPI and PostgreSQL backend for a simulated credit-card fraud detection and transaction analysis system.

The system records transactions, applies rule-based fraud checks, creates fraud alerts, provides dashboard analytics, and generates stored transaction reports.

## Technology Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT authentication
- Pydantic
- Uvicorn

## Features

- User registration and login
- JWT-protected API endpoints
- Simulated transaction recording
- Rule-based fraud detection
- Fraud alert generation and review workflow
- Transaction history, search, filtering, and pagination
- Dashboard analytics
- Report generation and retrieval
- PostgreSQL database migrations

## Fraud Detection Rules

The backend evaluates each transaction using these rules:

1. **High Transaction Amount**  
   Flags a transaction above the configured amount threshold.

2. **High Transaction Frequency**  
   Flags repeated transactions using the same card reference within a configured time window.

3. **Unusual Location**  
   Flags a transaction whose location differs from the established location pattern of the same card reference.

A transaction that triggers one or more rules is marked as `suspicious`, and a fraud alert is created for each triggered rule.

## Project Structure

```text
app/
├── alerts/             # Fraud alert models, routes, schemas, services
├── analysis/           # Dashboard and analytical endpoints
├── auth/               # Registration, login, JWT dependencies
├── core/               # Settings, enums, security utilities
├── database/           # SQLAlchemy base, session, model registry
├── fraud_detection/    # Fraud rules and rule-evaluation service
├── reports/            # Report models, generation, retrieval
├── transactions/       # Transaction models, routes, schemas, services
├── users/              # User models and response schemas
└── main.py             # FastAPI application entry point

alembic/                # Database migration files
requirements.txt
alembic.ini
.env                    # Local secrets; never commit this file
```

## Installation

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```
2. Access the API documentation at `http://localhost:8000/docs`.

## API Endpoints

- **User Management**
  - `POST /auth/register`: Register a new user.
  - `POST /auth/login`: Log in a user.

- **Transaction Management**
  - `POST /transactions`: Create a new transaction.
  - `GET /transactions`: Retrieve all transactions.

- **Fraud Detection**
  - `GET /alerts`: Get fraud alerts.

## Authentication Flow
1. Register with POST /api/auth/register.
2. Login with POST /api/auth/login.
3. Copy the returned access_token.
4. Send the token with protected requests:
Authorization: Bearer <access_token>

## Main API Endpoints
| Authentication | | |
|---|---|---|
| **Method** | **Endpoint** | **Description** |
| POST | `/api/auth/register` | Register a user |
| POST | `/api/auth/login` | Login and receive JWT access token |
| GET | `/api/auth/me` | Get the authenticated user |

| Transactions | | |
|---|---|---|
| **Method** | **Endpoint** | **Description** |
| POST | `/api/transactions` | Create and evaluate a transaction |
| GET | `/api/transactions` | List/filter transactions |
| GET | `/api/transactions/search` | Search transactions |
| GET | `/api/transactions/{id}` | Retrieve one transaction |

| Fraud Alerts | | |
|---|---|---|
| **Method** | **Endpoint** | **Description** |
| GET | `/api/alerts` | List fraud alerts |
| GET | `/api/alerts/{id}` | Get an alert |
| PUT | `/api/alerts/{id}` | Update alert review status |

| Analysis | | |
|---|---|---|
| **Method** | **Endpoint** | **Description** |
| GET | `/api/analysis/summary` | Dashboard totals |
| GET | `/api/analysis/trends` | Daily transaction trends |
| GET | `/api/analysis/by-type` | Transaction distribution by type |
| GET | `/api/analysis/by-location` | Transaction distribution by location |
| GET | `/api/analysis/fraud` | Fraud and alert statistics |

| Reports | | |
|---|---|---|
| **Method** | **Endpoint** | **Description** |
| POST | `/api/reports/generate` | Generate and store a report |
| GET | `/api/reports` | List generated reports |
| GET | `/api/reports/{id}` | Retrieve a report |

## Frontend Integration
The React frontend should use:
http://127.0.0.1:8000/api
For local development, set:
VITE_API_BASE_URL=http://127.0.0.1:8000/api
The frontend must send the JWT access token for protected endpoints and redirect users to login when the backend returns 401 Unauthorized.

## Security Notes
- Passwords are hashed using Argon2.
- JWT tokens expire after the configured duration.
- Protected endpoints require authentication.
- Full credit-card numbers are rejected.
- Use masked card references or safe internal card identifiers only.
- Fraud detection runs only in the backend.
- .env is excluded from version control.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.