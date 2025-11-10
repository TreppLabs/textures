# Textures Project Plan

## Project Overview
A web application for generating black and white texture patterns designed for **laser-cutting projects**. Uses AI (OpenAI DALL-E 3) to create, iterate, and refine textures through a human-in-the-loop workflow. Each theme aims to produce one favorite image suitable for laser cutting.

> **Note**: This project was vibe-coded - built iteratively with rapid experimentation.

## Project Goals
1. Generate black and white textures with organic, map-like, and geometric qualities
2. Iteratively refine prompts based on user ratings (1-5 stars)
3. Develop and manage multiple named "themes" with associated prompts
4. Enable theme branching and evolution
5. Track which prompts/keywords generate favored results
6. Prepare for future SVG/vector conversion for laser cutting

## Core Concept: Human-in-the-Loop Prompt Evolution

### The Workflow
1. **Theme Creation**: User starts a new theme (fresh or branched from existing)
2. **Generation Session**: System generates 4-6 texture variations with slightly modified prompts
3. **Rating Phase**: User rates each texture (1-5 stars)
4. **Learning Phase**: System analyzes ratings to identify successful prompt patterns
5. **Iteration**: Generate new variations based on successful patterns
6. **Theme Refinement**: Over time, each theme converges on optimal prompts

### Key Innovation
The system treats prompt engineering as an evolutionary process where:
- High-rated images influence future prompt variations
- ##keywords can be tracked and weighted
- Prompt history creates a "lineage" for each theme
- Users can fork successful themes to explore variations

## Technical Architecture

### Frontend: Next.js
- **Pages**:
  - `/` - Dashboard: View all themes, recent generations
  - `/theme/[id]` - Theme workspace: Generate, view, and rate images
  - `/theme/[id]/history` - View generation history and ratings
  - `/gallery` - Browse all generated images filtered by rating/theme
  - `/analytics` - Analyze keyword effectiveness across themes

- **Components**:
  - `ImageGrid` - Display 4-6 images with rating controls
  - `ThemeSelector` - Choose/create/branch themes
  - `PromptEditor` - Edit base prompt with ##keyword highlighting
  - `RatingStars` - Star rating interface
  - `GenerationControls` - Trigger generation, set variation parameters
  - `KeywordAnalytics` - Show which keywords correlate with high ratings

### Backend: Python (FastAPI)
- **API Endpoints**:
  - `POST /api/generate` - Generate texture variations
  - `POST /api/rate` - Submit image rating
  - `GET /api/themes` - List all themes
  - `POST /api/themes` - Create new theme
  - `POST /api/themes/{id}/branch` - Branch from existing theme
  - `GET /api/themes/{id}/suggestions` - Get prompt suggestions based on ratings
  - `GET /api/analytics/keywords` - Keyword effectiveness analysis

- **Core Modules**:
  - `prompt_engine.py` - Generate prompt variations from base prompts
  - `openai_client.py` - Interface with OpenAI API
  - `rating_analyzer.py` - Analyze ratings to identify successful patterns
  - `keyword_extractor.py` - Parse and weight ##keywords
  - `theme_manager.py` - Manage theme lifecycle and lineage

### Database: SQLite (simple, file-based)
- **Tables**:
  - `themes` - Theme metadata, base prompt, parent_theme_id
  - `generations` - Generation sessions (timestamp, theme_id, parameters)
  - `images` - Individual images (path, prompt, generation_id, rating, created_at)
  - `keywords` - Extracted keywords with effectiveness scores
  - `prompt_history` - Track prompt evolution over time

## Directory Structure

```
textures/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # Next.js 13+ app directory
│   │   │   ├── page.tsx     # Dashboard
│   │   │   ├── theme/
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx
│   │   │   │       └── history/
│   │   │   ├── gallery/
│   │   │   └── analytics/
│   │   ├── components/
│   │   └── lib/             # API client, utilities
│   ├── public/
│   └── package.json
│
├── backend/                  # Python FastAPI
│   ├── src/
│   │   ├── api/             # API route handlers
│   │   ├── core/            # Core logic modules
│   │   │   ├── prompt_engine.py
│   │   │   ├── openai_client.py
│   │   │   ├── rating_analyzer.py
│   │   │   ├── keyword_extractor.py
│   │   │   └── theme_manager.py
│   │   ├── models/          # Database models
│   │   └── main.py          # FastAPI app entry
│   ├── requirements.txt
│   └── tests/
│
├── data/                     # Persistent data storage
│   ├── database/
│   │   └── textures.db      # SQLite database
│   ├── images/              # Generated images organized by theme
│   │   ├── theme_001/
│   │   │   ├── gen_001/     # Generation session
│   │   │   │   ├── img_001.png
│   │   │   │   ├── img_002.png
│   │   │   │   └── metadata.json
│   │   │   └── gen_002/
│   │   └── theme_002/
│   └── exports/             # Future: SVG/vector exports
│
├── docs/                     # Documentation
│   ├── prompts/             # Successful prompt examples
│   └── keywords/            # Keyword effectiveness notes
│
├── .env.example             # Template for environment variables
├── .env                     # Actual env vars (gitignored)
├── .gitignore
├── project.md               # This file
├── environment.md           # Environment and tooling notes
└── README.md                # Project overview and setup
```

## Data Storage Strategy

### Images
- Store as PNG files (lossless, good for B&W)
- Organize by theme and generation session
- Each generation folder includes metadata.json with prompts and parameters

### Metadata Pattern
```json
{
  "generation_id": "gen_001",
  "theme_id": "theme_001",
  "timestamp": "2025-10-19T10:30:00Z",
  "base_prompt": "organic cellular structure with flowing lines",
  "variations": [
    {
      "image_id": "img_001",
      "filename": "img_001.png",
      "prompt": "organic cellular structure with flowing lines, ##fractal ##voronoi",
      "keywords": ["fractal", "voronoi"],
      "rating": 4,
      "variation_params": {"temperature": 0.7}
    }
  ]
}
```

## Prompt Variation Strategy

### How to Generate Variations
Given a base prompt, create 4-6 variations by:

1. **Keyword Substitution**: Swap similar ##keywords
   - Example: ##organic → ##cellular, ##flowing, ##natural

2. **Descriptor Addition**: Add complementary descriptors
   - "organic lines" → "organic flowing lines"
   - "geometric pattern" → "geometric pattern with subtle chaos"

3. **Emphasis Shifting**: Change which elements are emphasized
   - "bold lines with subtle texture" → "subtle lines with bold texture"

4. **Parameter Tweaking**: Adjust OpenAI generation parameters
   - Temperature, style weights, etc.

5. **Keyword Combination**: Mix successful keywords from past high-rated images

### Keyword System
- Prefix keywords with `##` for tracking
- Categories of keywords:
  - **Structural**: ##grid, ##radial, ##fractal, ##voronoi, ##maze
  - **Organic**: ##cellular, ##flowing, ##growth, ##branching, ##veins
  - **Textural**: ##rough, ##smooth, ##grainy, ##sharp, ##soft
  - **Map-like**: ##topographic, ##contour, ##terrain, ##elevation
  - **Geometric**: ##angular, ##curved, ##symmetrical, ##tessellated

## Security Considerations

### API Key Protection
- Store OpenAI API key in `.env` file (gitignored)
- Never commit `.env` to repository
- Provide `.env.example` template
- Use environment variables in both frontend and backend

### GitHub Security
- Add comprehensive `.gitignore`:
  - `.env`
  - `node_modules/`
  - `__pycache__/`
  - `data/images/` (optional: may want to commit sample images)
  - `data/database/` (gitignore actual DB, keep schema)
  - `.DS_Store` (macOS)

### Rate Limiting
- Implement basic rate limiting on API endpoints
- Track API usage to avoid unexpected OpenAI costs
- Set generation limits per session

## Tech Stack Rationale

### Next.js (Frontend)
- ✅ Modern React framework with great DX
- ✅ Built-in API routes (could proxy Python backend)
- ✅ Server-side rendering for better performance
- ✅ Easy deployment options (Vercel, etc.)
- ✅ Great image optimization built-in

### Python + FastAPI (Backend)
- ✅ Excellent for image manipulation (Pillow, OpenCV)
- ✅ Strong ML/AI ecosystem (if we add models later)
- ✅ FastAPI is fast, modern, and easy to work with
- ✅ Simple integration with OpenAI Python SDK
- ✅ Good for prompt engineering and text manipulation

### SQLite (Database)
- ✅ File-based, no server needed
- ✅ Perfect for development and personal projects
- ✅ Easy to backup (just copy the file)
- ✅ Can migrate to PostgreSQL later if needed
- ✅ Good performance for this use case

### Alternative Considerations
- **Texture Libraries**: Could integrate Processing.js, Three.js noise functions, or Perlin noise generators
- **Vector Conversion**: Future integration with Potrace or similar for SVG generation
- **Free Texture APIs**: Could supplement with textures from Unsplash, Pexels (if they have relevant content)

## Project Phases

### Phase 1: Foundation Setup ✅ COMPLETE
- [x] Create project directory
- [x] Initialize git repository
- [x] Create documentation structure
- [x] Setup .gitignore and security basics
- [x] Environment configuration (.env, .env.example)

### Phase 2: Backend Core ✅ COMPLETE
- [x] Initialize Python/FastAPI project
- [x] Setup virtual environment
- [x] Install dependencies (FastAPI, OpenAI, Pillow, SQLite, httpx)
- [x] Create database schema (themes, generations, images, keywords, prompt_history)
- [x] Implement OpenAI client wrapper with DALL-E 3
- [x] Create API endpoints (generate, themes, images, analytics)
- [x] Implement parallel image generation (asyncio)
- [x] Add comprehensive logging system
- [x] Structure prompt system for laser-cutting constraints

### Phase 3: Frontend Foundation ✅ COMPLETE
- [x] Initialize Next.js project (TypeScript, Tailwind CSS)
- [x] Setup basic routing structure
- [x] Create theme selector UI
- [x] Implement image grid component
- [x] Add star rating component (UI ready, backend implemented)
- [x] Connect to backend API
- [x] Theme-specific galleries
- [x] Top-per-theme gallery view

### Phase 4: Core Workflow ✅ COMPLETE
- [x] Implement theme creation
- [x] Build generation session flow
- [x] Connect rating system to database (API ready)
- [x] Test full workflow: create theme → generate → rate
- [x] Basic prompt variation engine
- [x] Two-part prompt system (structure + theme)
- [x] Image persistence (database + file storage)

### Phase 5: Intelligent Iteration 🔄 IN PROGRESS
- [x] Implement keyword extraction and tracking
- [x] Build rating analyzer (backend ready)
- [x] Rating UI implementation (fully functional)
- [ ] Create prompt suggestion system (backend ready, needs UI)
- [ ] Add theme branching (backend ready, needs UI)
- [ ] Test prompt evolution based on ratings

### Phase 6: Enhancement & Polish 🔄 NEXT UP
- [x] Add generation history view (theme-specific galleries)
- [x] Create gallery with filtering (top-per-theme and all images)
- [ ] Build keyword analytics dashboard (backend ready, needs UI)
- [ ] Improve UI/UX based on usage
- [ ] Add export functionality
- [ ] Documentation and examples

### Phase 7: Advanced Features (Future)
- [ ] SVG/vector conversion for laser cutting
- [ ] Integration with free texture generators
- [ ] Advanced prompt engineering (GPT-assisted)
- [ ] Batch generation modes
- [ ] Theme templates and presets
- [ ] Export theme configurations
- [ ] API usage tracking and budgets

## Current Status

### ✅ Completed Features
- **Full-stack web application** (Next.js + FastAPI)
- **OpenAI DALL-E 3 integration** with real image generation
- **Parallel image generation** (4 images simultaneously, ~4x faster)
- **Theme management** (create, list, view theme-specific galleries)
- **Image persistence** (database + file storage, survives server restarts)
- **Gallery views** (theme-specific, top-per-theme, all images)
- **Structure prompt system** for laser-cutting constraints (flat 2D, edge connectivity)
- **Two-part prompts** (structure + theme, theme-first ordering)
- **Comprehensive logging** (logs/backend.log)
- **Rating API** (backend + frontend UI complete)
- **Rating UI** (fully functional on dashboard, theme pages, and gallery)
- **Keyword extraction** (backend ready)
- **Cost transparency** ($0.04 per image, Standard quality)

### 🔄 In Progress / Next Steps

**Priority 1: Prompt Evolution**
- Use rating data to influence future prompt variations
- Implement prompt suggestion system based on high-rated images (backend ready, needs UI)
- Test and refine prompt evolution algorithm

**Priority 2: Theme Branching**
- Add UI for branching themes (backend ready, needs UI)
- Implement theme lineage tracking
- Test branching workflow

**Priority 3: Analytics Dashboard**
- Build keyword effectiveness visualization
- Show theme performance statistics
- Display success rate analysis

**Future Enhancements**
- SVG/vector conversion for laser cutting
- Advanced prompt engineering
- Batch generation modes
- Export functionality

## Resolved Questions

1. **OpenAI API**: ✅ DALL-E 3 (Standard quality: $0.04/image, HD: $0.08/image)
2. **Image Size**: ✅ 1024×1024 (DALL-E 3 minimum, sufficient for laser cutting)
3. **Variation Strategy**: ✅ 4 variations per session, generated in parallel
4. **Theme Branching**: ✅ Backend ready, UI pending
5. **Keyword Weighting**: ✅ Automatic based on ratings (backend ready)
6. **B&W Conversion**: ✅ Requested from API via structure prompt (high contrast, no grayscale)
7. **SVG Conversion**: 🔄 Future enhancement

## Open Questions

1. **Prompt Evolution**: How aggressively should we modify prompts based on ratings?
2. **Structure Prompt**: Is current level of detail control optimal?
3. **Theme Goal**: Should we add UI to mark a theme as "complete" when favorite is found?

## Success Metrics

- Ability to generate 4-6 varied textures in one session
- Clear improvement in texture quality over multiple iterations
- Easy identification of successful prompt patterns
- Smooth workflow for creating and managing themes
- Good performance (generation time, UI responsiveness)

## Notes

- Keep architecture flexible - expect experimentation and changes
- Prioritize development speed over production robustness
- Focus on the human-in-the-loop workflow quality
- Document prompt patterns as we discover them
- This is a creative tool, so UX matters a lot
