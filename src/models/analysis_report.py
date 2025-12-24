from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AnalysisReportBase(BaseModel):
    match_id: str
    report_type: Optional[str] = None
    report_data: Optional[Dict[str, Any]] = None
    generated_by: Optional[str] = None

class AnalysisReportCreate(AnalysisReportBase):
    pass

class AnalysisReport(AnalysisReportBase):
    id: str
    generated_at: datetime

    class Config:
        from_attributes = True
