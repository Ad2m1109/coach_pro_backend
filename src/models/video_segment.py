from pydantic import BaseModel
from typing import Optional

class VideoSegmentBase(BaseModel):
    match_id: str
    event_id: Optional[str] = None
    analysis_report_id: Optional[str] = None
    start_time_sec: float
    end_time_sec: float
    description: Optional[str] = None
    video_url: Optional[str] = None

class VideoSegmentCreate(VideoSegmentBase):
    pass

class VideoSegment(VideoSegmentBase):
    id: str

    class Config:
        from_attributes = True
