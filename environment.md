# Environment & Tooling Documentation

## Development Environment

### Hardware
- **Machine**: MacBook Pro with Apple Silicon (M1/M2/M3)
- **Architecture**: ARM64
- **Implications**: 
  - Use arm64-compatible packages
  - Some Python packages may need special installation
  - Docker images should use ARM variants when available

### Operating System
- **OS**: macOS
- **Shell**: zsh

## Development Philosophy

### Project Nature
- **Purpose**: Personal creative tool for texture generation
- **Robustness**: Development/experimental, not production-ready
- **Coding Approach**: LLM-assisted development (GitHub Copilot, etc.)
- **Architecture**: Flexible and modifiable, expect frequent changes
- **Deployment**: GitHub repository (public)

### Security Posture
- Basic security protections for public GitHub repo
- Protect API keys and secrets
- No need for enterprise-level security
- Focus on preventing accidental exposure of credentials

## Tech Stack

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **UI Library**: React 18+
- **Styling**: TailwindCSS (recommended for rapid development)
- **State Management**: React hooks + Context (keep it simple)

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ASGI Server**: Uvicorn
- **Database**: SQLite with SQLAlchemy
- **Image Processing**: Pillow (PIL)
- **AI Integration**: OpenAI Python SDK

### External Services
- **AI Provider**: OpenAI API
- **Model**: GPT-5 / DALL-E 3 (to be determined during experimentation)
- **Authentication**: API key stored in environment variables

## Environment Variables

### Backend (.env in root)
```bash
# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_MODEL=dall-e-3

# Application
ENV=development
DEBUG=true

# Database
DATABASE_URL=sqlite:///./data/database/textures.db

# Storage
IMAGES_DIR=./data/images
EXPORTS_DIR=./data/exports

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (.env.local in frontend/)
```bash
# API Connection
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Package Management

### Python
- **Environment**: venv (Python's built-in virtual environment)
- **Location**: `backend/venv/`
- **Activation**: `source backend/venv/bin/activate`
- **Package File**: `backend/requirements.txt`

### Node.js
- **Version**: 18+ or 20+ (LTS)
- **Package Manager**: npm or pnpm
- **Location**: `frontend/`

## Development Workflow

### Daily Development
1. Activate Python venv: `source backend/venv/bin/activate`
2. Start backend: `cd backend && uvicorn src.main:app --reload --port 8000`
3. Start frontend: `cd frontend && npm run dev`
4. Access app at `http://localhost:3000`
5. API docs at `http://localhost:8000/docs`

## Git Workflow

### Commit Message Convention
```
<type>: <description>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- refactor: Code refactoring
- chore: Maintenance tasks
```

## Security Best Practices

### API Key Management
1. **Never commit** `.env` files
2. **Always commit** `.env.example` as a template
3. Store API keys only in `.env` files
4. Use environment variables in code
5. Add `.env` to `.gitignore` immediately

## Useful Commands Reference

### Python/Backend
```bash
# Create virtual environment
python3 -m venv backend/venv

# Activate virtual environment
source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run backend
cd backend && uvicorn src.main:app --reload --port 8000
```

### Node.js/Frontend
```bash
# Create Next.js app
npx create-next-app@latest frontend --typescript --tailwind --app

# Install dependencies
cd frontend && npm install

# Run development server
npm run dev
```

### Database
```bash
# Open database
sqlite3 data/database/textures.db

# Backup database
cp data/database/textures.db data/database/textures.db.backup
```

## Development Guidelines

### Safety First
- **Always check before installing/downloading** anything that might affect local environment
- **Confirm before changing** Python/Node versions or environment variables
- **Verify before modifying** system-wide configurations that could disrupt other projects
- **Ask permission** before running commands that install packages or modify global settings

## Notes & Observations

### 2025-10-19: Initial Setup
- Project created at `~/textures`
- Git repository initialized
- Documentation structure created
- Ready to begin Phase 2 (Backend Core)

---

**Last Updated**: October 19, 2025
