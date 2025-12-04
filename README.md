# Evalhub

Infrastructure for LLM evaluations with a modern React frontend.

## Overview

Evalhub is a full-stack application for evaluating and benchmarking Large Language Models (LLMs). It provides:

- **FastAPI Backend** - RESTful API for managing datasets, guidelines, evaluations, and traces
- **React Frontend** - Modern, responsive UI built with React 19, TypeScript, and Tailwind CSS
- **PostgreSQL Database** - Robust data storage with SQLAlchemy ORM
- **AWS S3 Integration** - File storage for datasets and evaluation results

## Architecture

### Backend (Python/FastAPI)
- **API Routes**: `/api/auth`, `/api/users`, `/api/datasets`, `/api/guidelines`, `/api/evaluations`
- **Database**: PostgreSQL with Alembic migrations
- **Authentication**: JWT-based auth with bcrypt password hashing
- **Storage**: AWS S3 for file uploads

### Frontend (TypeScript/React)
- **Pages**: Home, Submit Evaluation, Datasets, Guidelines, Compare, Results
- **UI Components**: 40+ reusable components built with Radix UI
- **Styling**: Tailwind CSS v4 with custom design system
- **State Management**: TanStack Query for server state
- **Routing**: Wouter (lightweight React router)

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- PostgreSQL database
- AWS account (for S3 storage)

### Backend Setup

1. **Install Python dependencies**:
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

2. **Configure environment variables**:
Create a `.env` file in the project root:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/evalhub

# JWT
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=180

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-2
S3_BUCKET_NAME=evalhub-bucket

# Debug
DEBUG=true
```

3. **Run database migrations**:
```bash
alembic upgrade head
```

4. **Start the backend server**:
```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

### Frontend Setup

1. **Install Node.js dependencies**:
```bash
cd frontend && npm install
```

2. **Start the development server**:
```bash
cd frontend && npm run dev:client
```

The frontend will be available at `http://localhost:5173`

The Vite dev server is configured to proxy API requests to `http://localhost:8000/api`

### Full-Stack Development

Run both servers simultaneously:

**Terminal 1 (Backend)**:
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 (Frontend)**:
```bash
cd frontend && npm run dev:client
```

## Production Build

1. **Build the frontend**:
```bash
cd frontend && npm run build:client
```

This creates optimized static files in `dist/public/`

2. **Start the production server**:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The FastAPI server will serve both the API (at `/api/*`) and the static frontend files.

## Project Structure

```
Evalhub/
├── backend/                      # FastAPI backend
│   ├── auth/                 # Authentication endpoints
│   ├── core/                 # Core configuration & utilities
│   ├── datasets/             # Dataset management
│   ├── evaluations/          # Evaluation tracking (traces)
│   ├── guidelines/           # Evaluation guidelines
│   ├── users/                # User management
│   └── main.py               # FastAPI app entry point
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── ui/           # Reusable UI components
│   │   │   ├── layout.tsx    # Main layout with navbar
│   │   │   └── ...
│   │   ├── pages/            # Application pages
│   │   │   ├── home.tsx      # Landing page
│   │   │   ├── submit.tsx    # Evaluation submission wizard
│   │   │   ├── datasets.tsx  # Dataset browser
│   │   │   └── ...
│   │   ├── lib/              # Utilities & config
│   │   └── hooks/            # Custom React hooks
│   ├── index.html            # HTML entry point
│   └── public/               # Static assets
├── alembic/                  # Database migrations
├── samples_from_evals/       # Sample data
├── tests/                    # Backend tests
├── attached_assets/          # Frontend images & assets
├── package.json              # Node.js dependencies
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
├── pyproject.toml            # Python dependencies
└── README.md                 # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

### Datasets
- `GET /api/datasets` - List all datasets
- `POST /api/datasets` - Create dataset
- `GET /api/datasets/{id}` - Get dataset details
- `DELETE /api/datasets/{id}` - Delete dataset

### Guidelines
- `GET /api/guidelines` - List all guidelines
- `POST /api/guidelines` - Create guideline
- `GET /api/guidelines/{id}` - Get guideline details
- `DELETE /api/guidelines/{id}` - Delete guideline

### Evaluations
- `GET /api/evaluations/traces` - List evaluation runs
- `POST /api/evaluations/traces` - Create evaluation run
- `GET /api/evaluations/traces/{id}` - Get trace details
- `GET /api/evaluations/traces/{id}/events` - Get trace events

### Users
- `GET /api/users/me` - Get current user
- `PUT /api/users/me` - Update current user

## Frontend Features

### Landing Page
- Hero section with animated visuals
- Live leaderboard preview
- Featured datasets showcase
- Evaluation guidelines preview

### Evaluation Submission Wizard
6-step process for running custom evaluations:
1. Select dataset (standard or custom upload)
2. Choose evaluation guidelines
3. Pick models to evaluate
4. Select judge model
5. Enter API keys (client-side only)
6. Review and submit

### Dataset Viewer
- Browse all datasets with search
- View dataset details and metadata
- Inspect individual samples in table format
- Export to CSV

### Design System
- **Colors**: Black primary, Mint green accent, Zinc grays
- **Typography**: Display font for headings, sans-serif for body
- **Components**: 40+ reusable UI components
- **Responsive**: Mobile-first design with hamburger menu

## Development Scripts

### Backend
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=api

# Format code
black api/
isort api/

# Type checking
mypy api/
```

### Frontend
```bash
# Development server
cd frontend && npm run dev:client

# Build for production
cd frontend && npm run build:client

# Preview production build
npm run preview

# Type checking
npm run check
```

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET` | Secret key for JWT tokens | Required |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRATION` | Token expiration (minutes) | `180` |
| `AWS_ACCESS_KEY_ID` | AWS access key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required |
| `AWS_REGION` | AWS region | `us-east-2` |
| `S3_BUCKET_NAME` | S3 bucket name | `evalhub-bucket` |
| `DEBUG` | Enable debug mode | `false` |

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

MIT License - see LICENSE file for details
