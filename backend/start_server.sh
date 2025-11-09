#!/bin/bash
cd "$(dirname "$0")/src"
python3 -c "
import uvicorn
from main import app
print('🚀 Starting Textures API backend server...')
print('📍 Server will be at: http://localhost:8000')
print('📝 Logs will appear below:')
print('=' * 50)
uvicorn.run(app, host='0.0.0.0', port=8000, reload=False)
"

