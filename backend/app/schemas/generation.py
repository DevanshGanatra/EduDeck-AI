from pydantic import BaseModel, Field
from typing import List

class SlidePlan(BaseModel):
    title: str = Field(description="The title of the slide.")
    topic: str = Field(description="The specific topic or concept to be covered on this slide.")

class PresentationOutline(BaseModel):
    slides: List[SlidePlan] = Field(description="List of planned slides for the presentation.")

class SlideContent(BaseModel):
    title: str = Field(description="The title of the slide.")
    bullet_points: List[str] = Field(description="3-5 concise bullet points summarizing the content.")
    speaker_notes: str = Field(description="Detailed speaker notes explaining the bullet points.")
    references: List[str] = Field(description="List of source references or citations used for this slide.")
