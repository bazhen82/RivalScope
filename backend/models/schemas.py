from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class AnalysisContext(BaseModel):
    niche: str = Field(default="AI-автоматизация бизнеса")
    custom_niche: Optional[str] = None
    own_brand: Optional[str] = "NeiroBridge"
    own_site: Optional[str] = "https://neirobridge.ru"
    target_audience: Optional[str] = None

    @property
    def effective_niche(self) -> str:
        if self.niche.lower() in {"другое", "custom", "other"} and self.custom_niche:
            return self.custom_niche
        return self.niche


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=10)
    context: AnalysisContext = Field(default_factory=AnalysisContext)


class UrlAnalysisRequest(BaseModel):
    url: HttpUrl
    context: AnalysisContext = Field(default_factory=AnalysisContext)
    use_selenium: bool = True


class CompetitorItem(BaseModel):
    name: str
    url: HttpUrl
    note: Optional[str] = None


class CompareCompetitorsRequest(BaseModel):
    competitors: List[CompetitorItem] = Field(..., min_length=2, max_length=6)
    context: AnalysisContext = Field(default_factory=AnalysisContext)


class AnalysisResult(BaseModel):
    summary: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    unique_offers: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    scores: Dict[str, int] = Field(default_factory=dict)
    positioning_gap: List[str] = Field(default_factory=list)
    action_plan: List[str] = Field(default_factory=list)
    raw: Optional[Dict[str, Any]] = None


class ImageAnalysisResult(BaseModel):
    description: str
    marketing_insights: List[str] = Field(default_factory=list)
    visual_style_analysis: str
    recommendations: List[str] = Field(default_factory=list)
    scores: Dict[str, int] = Field(default_factory=dict)
    animation_potential: str = ""
    raw: Optional[Dict[str, Any]] = None


class ParsedPage(BaseModel):
    url: str
    title: str = ""
    h1: str = ""
    first_paragraph: str = ""
    text_excerpt: str = ""
    screenshot_base64: Optional[str] = None


class ParseAnalysisResponse(BaseModel):
    parsed: ParsedPage
    analysis: AnalysisResult


class HistoryItem(BaseModel):
    id: str
    type: str
    title: str
    created_at: datetime
    payload: Dict[str, Any]


class HistoryResponse(BaseModel):
    items: List[HistoryItem]


class HealthResponse(BaseModel):
    status: str
    app: str
    ai_provider: str
