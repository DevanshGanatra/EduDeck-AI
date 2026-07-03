# AI Pipeline (Agentic RAG)

## The Generation Loop
Instead of generating a monolithic presentation in a single prompt (which leads to context loss and hallucination), EduDeck AI utilizes a multi-step Graph:

1. **Planner Node**: Takes the user prompt and generates a strict JSON `PresentationOutline` containing Slide Titles and Topics.
2. **Contextual Retrieval**: We loop over the outline. For each slide topic, we query ChromaDB for the Top-3 nearest semantic chunks.
3. **Generator Node**: We supply the specific topic and specific retrieved context into GPT-4o, outputting a strict JSON `SlideContent` (Title, Bullets, Notes, References).
4. **Formatting**: If ChromaDB yields no context, a deterministic placeholder is injected to prevent the LLM from hallucinating facts not present in the Knowledge Base.
