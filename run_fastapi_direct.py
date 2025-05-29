#!/usr/bin/env python3
"""
Run FastAPI directly without uvicorn (только для разработки!)
"""

import os
from fastapi_main import app

if __name__ == "__main__":
    import uvicorn
    
    # Для разработки можно так, но в production нужен полноценный ASGI сервер
    port = int(os.getenv('PORT', 8001))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")