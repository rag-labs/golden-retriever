from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.json_fitter import router as json_fitter_router
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(
    title='Restaurant JSON Fitter API',
    description='API for fitting restaurant information into JSON schema',
    version='1.0'
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the json_fitter router
app.include_router(json_fitter_router, prefix='/api')

@app.get('/health')
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy'}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=port, 
        reload=os.getenv('FASTAPI_DEBUG', 'False').lower() == 'true'
    ) 