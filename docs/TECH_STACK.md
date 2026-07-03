# Tech Stack

- **FastAPI**: High performance async web framework.
- **SQLAlchemy 2.0 (Async)**: ORM pattern mapping Python objects to Postgres tables.
- **PostgreSQL**: Relational storage for users, projects, documents, and chunks.
- **ChromaDB**: Local vector database for embedding storage and similarity search.
- **LangGraph**: Stateful multi-actor orchestration for our Planner -> Retriever -> Generator flow.
- **LangChain**: Tools for RecursiveCharacterTextSplitter and ChatPromptTemplate.
- **OpenAI SDK**: Provides access to GPT-4o and Text Embeddings.
- **python-pptx**: Generates actual binary PPTX files from Python objects without needing MS Office installed.
- **PyPDF**: Pure Python PDF parser used for knowledge extraction.
- **Passlib/Bcrypt/PyJWT**: Stateless JWT authentication handling.
