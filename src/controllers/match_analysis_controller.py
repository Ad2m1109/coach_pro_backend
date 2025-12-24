from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends
from typing import Dict
from database import get_db
from services.video_analysis_service import start_video_analysis, get_analysis_status
from services.match_service import MatchService
from services.player_match_statistics_service import PlayerMatchStatisticsService

router = APIRouter(prefix="/matches", tags=["match-analysis"])

@router.post("/{match_id}/analyze")
async def analyze_match_video(
    match_id: str,
    video: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db = Depends(get_db)
) -> Dict:
    """Start video analysis for a match. Returns immediately with status tracking info."""
    match_service = MatchService(db)
    player_stats_service = PlayerMatchStatisticsService(db)
    
    return await start_video_analysis(
        match_id=match_id,
        video_file=video,
        background_tasks=background_tasks,
        match_service=match_service,
        player_stats_service=player_stats_service
    )

@router.get("/{match_id}/analysis-status")
async def check_analysis_status(match_id: str) -> Dict:
    """Get current status of video analysis for a match."""
    return get_analysis_status(match_id)