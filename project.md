# Textures Project Plan

## Project Overview
A human-in-the-loop texture generation system that uses AI (OpenAI API with GPT-5/DALL-E) to create, iterate, and refine black and white organic textures. The system enables theme-based prompt evolution through user ratings and feedback.

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

### Phase 1: Foundation Setup (Current)
- [x] Create project directory
- [x] Initialize git repository
- [x] Create documentation structure
- [ ] Setup .gitignore and security basics

### Phase 2: Backend Core (Days 1-2)
- [ ] Initialize Python/FastAPI project
- [ ] Setup virtual environment
- [ ] Install dependencies (FastAPI, OpenAI, Pillow, SQLite)
- [ ] Create database schema
- [ ] Implement OpenAI client wrapper
- [ ] Create basic API endpoints (generate, rate)
- [ ] Test image generation with OpenAI API

### Phase 3: Frontend Foundation (Days 2-3)
- [ ] Initialize Next.js project
- [ ] Setup basic routing structure
- [ ] Create theme selector UI
- [ ] Implement image grid component
- [ ] Add star rating component
- [ ] Connect to backend API

### Phase 4: Core Workflow (Days 3-5)
- [ ] Implement theme creation
- [ ] Build generation session flow
- [ ] Connect rating system to database
- [ ] Test full workflow: create theme → generate → rate
- [ ] Basic prompt variation engine

### Phase 5: Intelligent Iteration (Days 5-7)
- [ ] Implement keyword extraction and tracking
- [ ] Build rating analyzer
- [ ] Create prompt suggestion system
- [ ] Add theme branching
- [ ] Test prompt evolution based on ratings

### Phase 6: Enhancement & Polish (Days 7-10)
- [ ] Add generation history view
- [ ] Create gallery with filtering
- [ ] Build keyword analytics dashboard
- [ ] Improve UI/UX
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

## Immediate Next Steps

### Step 1: Environment Setup
1. Create `.gitignore` file
2. Create `.env.example` template
3. Setup Python virtual environment
4. Initialize Next.js project in `frontend/`
5. Initialize Python project in `backend/`

### Step 2: Database Schema
1. Design SQLite schema
2. Create migration script
3. Add sample data for testing
4. Document database structure

### Step 3: OpenAI Integration
1. Setup OpenAI API client
2. Test DALL-E 3 image generation
3. Experiment with prompts for B&W textures
4. Document successful prompt patterns
5. Test variation strategies

## Open Questions to Explore

1. **OpenAI API**: Which model/endpoint? DALL-E 3 or GPT-5 with vision?
2. **Image Size**: What resolution? (1024x1024 standard? Higher for laser cutting?)
3. **Variation Strategy**: How much variation between the 4-6 images?
4. **Theme Branching**: Simple fork or inherit prompt elements?
5. **Keyword Weighting**: Manual or automatic based on ratings?
6. **B&W Conversion**: Request B&W from API or post-process?
7. **SVG Conversion**: Which tool/library for future vectorization?

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
