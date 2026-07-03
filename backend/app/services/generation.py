from uuid import UUID
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.schemas.generation import PresentationOutline, SlideContent
from app.services.retrieval import RetrievalService
from app.services.storage import LocalStorageService
from app.services.export import ExportService

class GenerationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o", temperature=0.2)
        self.retrieval_service = RetrievalService(db)
        self.export_service = ExportService(LocalStorageService())

    async def generate_presentation(self, prompt: str, project_id: UUID) -> str:
        # Step 1: Planner
        outline = await self._plan_outline(prompt)
        
        # Step 2: Generate Slides individually
        generated_slides = []
        for slide_plan in outline.slides:
            slide_content = await self._generate_slide(slide_plan.title, slide_plan.topic, project_id)
            generated_slides.append(slide_content)
            
        # Step 3: Export to PPTX
        file_path = await self.export_service.create_pptx(generated_slides)
        return file_path

    async def _plan_outline(self, prompt: str) -> PresentationOutline:
        planner_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert presentation planner. Create a logical slide outline based on the user's request. Keep it between 5 to 10 slides."),
            ("user", "{prompt}")
        ])
        
        chain = planner_prompt | self.llm.with_structured_output(PresentationOutline)
        result = await chain.ainvoke({"prompt": prompt})
        return result

    async def _generate_slide(self, title: str, topic: str, project_id: UUID) -> SlideContent:
        # Retrieve context
        retrieved = await self.retrieval_service.retrieve(query=topic, project_id=project_id, top_k=3)
        
        if not retrieved:
            # Fallback if insufficient source material
            return SlideContent(
                title=title,
                bullet_points=["[Insufficient source material found for this topic.]"],
                speaker_notes="Please review the knowledge base to ensure sufficient material is uploaded.",
                references=[]
            )
            
        context_text = "\n\n".join([f"Source {i+1} (Page {r['page_number']}): {r['text']}" for i, r in enumerate(retrieved)])
        
        generator_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a slide generation assistant. You must generate structured slide content STRICTLY using the provided Source Context. Do not use outside knowledge. If the context does not fully answer the topic, generate what you can and add a note."),
            ("user", "Topic: {topic}\n\nContext:\n{context}")
        ])
        
        chain = generator_prompt | self.llm.with_structured_output(SlideContent)
        result = await chain.ainvoke({"topic": topic, "context": context_text})
        return result
