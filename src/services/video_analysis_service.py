from typing import Dict, Optional
from fastapi import UploadFile, HTTPException, BackgroundTasks
from tempfile import NamedTemporaryFile
import shutil
import os

from services.match_service import MatchService
from services.player_match_statistics_service import PlayerMatchStatisticsService
from analysis_engine import analyze_football_match

# In-memory store for analysis status
# In production, use Redis or similar
_analysis_status: Dict[str, Dict] = {}

async def start_video_analysis(
    match_id: str,
    video_file: UploadFile,
    background_tasks: BackgroundTasks,
    match_service: MatchService,
    player_stats_service: PlayerMatchStatisticsService,
) -> Dict:
    """Start video analysis in background and return status tracking ID."""
    
    # Validate match exists
    match = match_service.get_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Save uploaded video to temp file
    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        try:
            shutil.copyfileobj(video_file.file, temp_video)
            temp_video_path = temp_video.name
        finally:
            video_file.file.close()

    # Initialize status tracking
    _analysis_status[match_id] = {
        "status": "pending",
        "progress": 0.0,
        "error": None
    }

    # Start analysis in background
    background_tasks.add_task(
        _run_analysis,
        match_id=match_id,
        video_path=temp_video_path,
        match_service=match_service,
        player_stats_service=player_stats_service
    )

    return {
        "status": "accepted",
        "message": "Video analysis started"
    }

def get_analysis_status(match_id: str) -> Dict:
    """Get current status of video analysis for a match."""
    if match_id not in _analysis_status:
        raise HTTPException(status_code=404, detail="No analysis found for match")
    return _analysis_status[match_id]

async def _run_analysis(
    match_id: str,
    video_path: str,
    match_service: MatchService,
    player_stats_service: PlayerMatchStatisticsService
):
    """Background task to run video analysis and persist results."""
    try:
        # Update status to running
        _analysis_status[match_id].update({
            "status": "running",
            "progress": 0.0
        })

        # Run analysis (this blocks until complete)
        results = analyze_football_match(
            video_path=video_path,
            match_id=match_id,
            db_connection=match_service.db_connection
        )

        # Update status on success
        _analysis_status[match_id].update({
            "status": "completed",
            "progress": 1.0,
            "results": results
        })

    except Exception as e:
        # Update status on failure
        _analysis_status[match_id].update({
            "status": "failed",
            "error": str(e)
        })
        raise
    
    finally:
        # Clean up temp file
        try:
            os.unlink(video_path)
        except:
            pass