"""
FastAPI backend for WriteCoach
Exposes microservices as REST APIs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from main import WriteCoachPipeline

app = FastAPI(
    title="WriteCoach API",
    description="AI-powered writing analysis and improvement service",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = WriteCoachPipeline()

# Request/Response models
class AnalysisRequest(BaseModel):
    text: str
    user_id: Optional[str] = "default_user"
    format: Optional[str] = None

class AnalysisResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None

class ProgressRequest(BaseModel):
    user_id: str

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]

# API endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to WriteCoach API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "input_handler": "online",
            "text_analyzer": "online",
            "format_classifier": "online",
            "suggestion_generator": "online",
            "progress_tracker": "online",
            "output_formatter": "online"
        }
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest):
    """Analyze text and return results"""
    try:
        # Validate input
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Process through pipeline
        analysis_results = pipeline.text_analyzer.analyze(request.text)
        
        # Format classification
        format_type, confidence = pipeline.format_classifier.classify(request.text, request.format)
        format_rules = pipeline.format_classifier.apply_format_rules(
            request.text, format_type, analysis_results
        )
        
        # Generate suggestions
        suggestions = pipeline.suggestion_generator.generate_suggestions(
            request.text, analysis_results, format_type
        )
        
        # Track progress
        progress_result = pipeline.progress_tracker.track_submission(
            request.user_id, analysis_results, suggestions
        )
        
        # Format for web
        web_output = pipeline.output_formatter.format_for_web(
            analysis_results, suggestions, format_rules, progress_result.get('overall_progress')
        )
        
        return AnalysisResponse(success=True, data=web_output)
    
    except Exception as e:
        return AnalysisResponse(success=False, data={}, error=str(e))

@app.get("/progress/{user_id}", response_model=AnalysisResponse)
async def get_progress(user_id: str):
    """Get user progress report"""
    try:
        report = pipeline.progress_tracker.get_user_report(user_id)
        
        if report.get('status') == 'no_data':
            raise HTTPException(status_code=404, detail="No data found for user")
        
        return AnalysisResponse(success=True, data=report)
    
    except HTTPException:
        raise
    except Exception as e:
        return AnalysisResponse(success=False, data={}, error=str(e))

@app.post("/validate")
async def validate_input(request: Dict[str, Any]):
    """Validate input text"""
    try:
        text = request.get('text', '')
        format_type = request.get('format')
        
        result = pipeline.input_handler.validate_input(text, format_type)
        
        return {"success": True, "data": result}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

# Individual microservice endpoints
@app.post("/services/analyze")
async def analyze_service(request: Dict[str, Any]):
    """Text analysis service endpoint"""
    try:
        text = request.get('text', '')
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        result = pipeline.text_analyzer.analyze(text)
        return {"success": True, "data": result}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/services/classify")
async def classify_service(request: Dict[str, Any]):
    """Format classification service endpoint"""
    try:
        text = request.get('text', '')
        specified_format = request.get('format')
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        format_type, confidence = pipeline.format_classifier.classify(text, specified_format)
        
        return {
            "success": True,
            "data": {
                "format": format_type,
                "confidence": confidence
            }
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/services/suggest")
async def suggest_service(request: Dict[str, Any]):
    """Suggestion generation service endpoint"""
    try:
        text = request.get('text', '')
        analysis = request.get('analysis', {})
        format_type = request.get('format', 'general')
        
        if not text or not analysis:
            raise HTTPException(status_code=400, detail="Text and analysis are required")
        
        result = pipeline.suggestion_generator.generate_suggestions(text, analysis, format_type)
        
        return {"success": True, "data": result}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)