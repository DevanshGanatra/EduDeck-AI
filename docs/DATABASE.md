# Database Schema

## Core Entities
- **User**: Authentication layer.
- **Project**: Represents a workspace. Holds default AI settings (language, slide count, templates). Cascades delete to all children.
- **Document**: Represents an uploaded PDF. Holds extensive telemetry (total_pages, reading_time, processing durations, validation statuses).
- **DocumentChunk**: The granular text block. Stores `vector_reference` linking it to ChromaDB, alongside snippet indexes, page numbers, and text density quality metrics.
- **GenerationJob & Session**: Tracks AI usage and cost metrics.
- **Presentation & Slide**: Maps immutable exports for history.
