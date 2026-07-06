import os
import json
import uuid
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.core import Project, Presentation, Document
from app.models.ai import GenerationJob, JobStatus
from app.services.retrieval import RetrievalService
from app.services.export import ExportService

class GenerationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Initialize Gemini API
        from app.core.config import settings
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.retrieval_service = RetrievalService(db)
        self.export_service = ExportService(db)

    async def generate_presentation(self, prompt: str, project_id: UUID) -> str:
        """
        Main pipeline to generate presentation from a prompt and knowledge base.
        Returns the download URL for the PPTX.
        """
        # 1. Fetch project documents to check if we have any
        result = await self.db.execute(select(Document).where(Document.project_id == project_id))
        documents = result.scalars().all()
        
        context_chunks = []
        if documents:
            # 2. Retrieve relevant context from Postgres pgvector
            results = await self.retrieval_service.retrieve(query=prompt, project_id=project_id, top_k=10)
            for res in results:
                context_chunks.append(res["text"])

        # 3. Build Prompt for LLM
        context_text = "\n\n".join(context_chunks)
        
        system_prompt = f"""
You are an expert Presentation Creator AI. 
Your goal is to create a professional presentation based on the user's prompt and the provided Context.
You MUST output ONLY a valid JSON object with the following structure:
{{
  "title": "Presentation Title",
  "slides": [
    {{
      "title": "Slide Title",
      "content": ["Bullet point 1", "Bullet point 2"],
      "speaker_notes": "Notes for the speaker"
    }}
  ]
}}
Do NOT wrap the JSON in Markdown code blocks (like ```json). Return raw JSON only.

Context from Knowledge Base:
{context_text}

User Request: {prompt}
"""
        
        # 4. Call LLM
        response = self.model.generate_content(system_prompt)
        response_text = response.text.strip()
        
        # Strip potential markdown blocks if the model ignores the instruction
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        try:
            presentation_data = json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            print("Failed to decode JSON from LLM:", response_text)
            raise ValueError("Failed to generate valid presentation format from AI.")

        # 5. Create Job & Presentation DB Records
        job = GenerationJob(project_id=project_id, status=JobStatus.COMPLETED)
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        # We need a template_id (use a dummy one for MVP or fetch first)
        from app.models.core import PresentationTemplate
        template_res = await self.db.execute(select(PresentationTemplate).limit(1))
        template = template_res.scalars().first()
        
        if not template:
            template = PresentationTemplate(name="Default", description="Default minimalist template")
            self.db.add(template)
            await self.db.commit()
            await self.db.refresh(template)

        presentation = Presentation(
            job_id=job.id,
            template_id=template.id,
            title=presentation_data.get("title", "Untitled Presentation")
        )
        self.db.add(presentation)
        await self.db.commit()
        await self.db.refresh(presentation)
        
        # Save Slides (optional for MVP, but good for persistence)
        from app.models.core import Slide
        for i, slide_data in enumerate(presentation_data.get("slides", [])):
            db_slide = Slide(
                presentation_id=presentation.id,
                slide_number=i+1,
                content_json=json.dumps(slide_data)
            )
            self.db.add(db_slide)
        await self.db.commit()

        # 6. Export to PPTX
        download_url = await self.export_service.export_presentation(presentation, presentation_data)
        
        # Update URL
        presentation.file_url = download_url
        await self.db.commit()
        
        return download_url
