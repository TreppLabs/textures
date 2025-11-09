# Textures Generator

A human-in-the-loop texture generation system that uses AI (OpenAI API with DALL-E) to create, iterate, and refine black and white organic textures. The system enables theme-based prompt evolution through user ratings and feedback.

## 🎯 Project Overview

This system treats prompt engineering as an evolutionary process where:
- High-rated images influence future prompt variations
- Keywords can be tracked and weighted for effectiveness
- Prompt history creates a "lineage" for each theme
- Users can fork successful themes to explore variations

## 🏗️ Architecture

### Frontend (Next.js 14+)
- **Framework**: Next.js with TypeScript and Tailwind CSS
- **Pages**: Dashboard, Theme workspace, Gallery, Analytics
- **Components**: ImageGrid, ThemeSelector, RatingStars, GenerationControls, PromptEditor

### Backend (Python FastAPI)
- **Framework**: FastAPI with SQLAlchemy
- **Database**: SQLite with comprehensive schema
- **AI Integration**: OpenAI API for texture generation
- **Core Modules**: Prompt engine, keyword extractor, rating analyzer, theme manager

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (Note: Current setup uses Node 19.7.0, may need upgrade for full compatibility)
- Python 3.11+
- OpenAI API key

### Installation

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd textures
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

2. **Backend setup**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend setup**:
   ```bash
   cd frontend
   npm install
   cp .env.local.example .env.local
   ```

### Running the Application

1. **Start the backend**:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn src.main:app --reload --port 8000
   ```

2. **Start the frontend** (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
textures/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # Next.js 13+ app directory
│   │   │   ├── page.tsx     # Dashboard
│   │   │   ├── theme/[id]/  # Theme workspace
│   │   │   ├── gallery/     # Image gallery
│   │   │   └── analytics/   # Analytics dashboard
│   │   ├── components/      # React components
│   │   └── lib/             # API client, utilities
│   └── package.json
│
├── backend/                  # Python FastAPI
│   ├── src/
│   │   ├── api/             # API route handlers
│   │   ├── core/            # Core business logic
│   │   ├── models/          # Database models
│   │   └── main.py          # FastAPI app entry
│   └── requirements.txt
│
├── data/                     # Persistent data storage
│   ├── database/            # SQLite database
│   ├── images/              # Generated images
│   └── exports/             # Future: SVG/vector exports
│
├── docs/                     # Documentation
├── .env.example             # Environment template
└── README.md
```

## 🔧 Key Features

### Theme Management
- Create and manage multiple texture themes
- Branch themes to explore variations
- Track theme lineage and evolution

### Intelligent Generation
- Generate 4-6 texture variations per session
- AI-powered prompt variation based on ratings
- Keyword tracking with `##keyword` syntax

### Rating & Learning
- 1-5 star rating system for each image
- Automatic keyword effectiveness analysis
- Prompt suggestions based on successful patterns

### Analytics Dashboard
- Keyword effectiveness metrics
- Theme performance statistics
- Success rate analysis

## 🎨 Usage Workflow

1. **Create a Theme**: Start with a base prompt describing your desired texture style
2. **Generate Variations**: Create 4-6 texture variations with slight prompt modifications
3. **Rate Images**: Rate each generated texture (1-5 stars)
4. **Learn & Iterate**: The system analyzes your ratings to improve future generations
5. **Branch & Explore**: Create theme branches to explore different directions

## 🔑 Environment Variables

### Backend (.env)
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=dall-e-3
DATABASE_URL=sqlite:///./data/database/textures.db
IMAGES_DIR=./data/images
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🛠️ Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Database Management
```bash
# Access SQLite database
sqlite3 data/database/textures.db

# Backup database
cp data/database/textures.db data/database/textures.db.backup
```

## 📊 Database Schema

- **themes**: Theme metadata and base prompts
- **generations**: Generation sessions
- **images**: Individual images with ratings
- **keywords**: Keyword effectiveness tracking
- **prompt_history**: Prompt evolution over time

## 🚧 Current Status

✅ **Completed**:
- Project structure and setup
- Backend core modules (OpenAI client, prompt engine, rating analyzer)
- Database schema and models
- Frontend components and pages
- Theme management system
- OpenAI DALL-E 3 integration with real image generation
- Image persistence and retrieval (database + file storage)
- Gallery and Recent Images views
- Image rating endpoints

🔄 **Next Steps**:
- Rating UI implementation
- Prompt evolution based on ratings
- Analytics dashboard
- Theme branching workflow

## 🤝 Contributing

This is a personal creative tool project. Feel free to fork and adapt for your own use!

## 📄 License

MIT License - see LICENSE file for details.
