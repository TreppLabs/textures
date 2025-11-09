# Textures Generator

A web application for generating black and white texture patterns designed for **laser-cutting projects**. Uses AI (OpenAI DALL-E 3) to create, iterate, and refine textures through a human-in-the-loop workflow. Each theme aims to produce one favorite image suitable for laser cutting.

> **Note**: This project was vibe-coded - built iteratively with rapid experimentation. The code prioritizes functionality over perfection.

## 🎯 Purpose

Generate laser-cuttable black and white patterns where:
- **Black portions** are cut out (creating voids/windows)
- **White portions** remain as solid material
- Patterns connect edge-to-edge for structural integrity
- Each theme produces one favorite image through iterative refinement

## 🚀 Quick Start

### Prerequisites
- Node.js 20.18.0+ (use `asdf` with `.tool-versions` or install directly)
- Python 3.11+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- ~$0.04 per image (Standard quality, 1024×1024)

### Installation

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd textures
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
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
   # .env.local is already configured for localhost:8000
   ```

### Running

1. **Start backend** (terminal 1):
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start frontend** (terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open**: http://localhost:3000

## 🏗️ Architecture

- **Frontend**: Next.js 14+ (TypeScript, Tailwind CSS)
- **Backend**: FastAPI (Python) with SQLite
- **AI**: OpenAI DALL-E 3 API
- **Storage**: Images in `data/images/`, database in `data/database/`

## 🎨 Workflow

1. **Create a Theme** with a base prompt describing your texture style
2. **Generate Variations** (default: 4 images in parallel)
3. **Rate Images** (1-5 stars) to identify favorites
4. **Iterate** - system learns from ratings to improve future generations
5. **Select Favorite** - each theme aims for one perfect image

## 📁 Key Files

- `prompts/structure.md` - Laser-cutting constraints (applied to all images)
- `backend/src/core/structure_prompt.py` - Loads and combines structure + theme prompts
- `backend/src/api/generate.py` - Parallel image generation
- `frontend/src/app/` - Next.js pages (Dashboard, Gallery, Theme workspace)

## 🔑 Environment Variables

**Backend** (`.env`):
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=dall-e-3
DATABASE_URL=sqlite:///./data/database/textures.db
IMAGES_DIR=./data/images
```

**Frontend** (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 💰 Cost

- **Standard quality** (1024×1024): $0.04 per image
- **HD quality** (1024×1024): $0.08 per image
- Default: 4 variations = $0.16 per generation session

## 🚧 Status

✅ **Working**: Image generation, theme management, galleries, parallel generation, structure prompts  
🔄 **Future**: Rating UI, prompt evolution, analytics dashboard

## 📄 License

MIT License
