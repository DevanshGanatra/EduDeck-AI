# API Reference

*Note: Access complete Swagger documentation at `http://localhost:8080/docs`.*

### Authentication (`/api/v1/auth`)
- `POST /register`: Create new user.
- `POST /login`: OAuth2 Password Bearer login, returns JWT token.
- `GET /me`: Returns current user.

### Projects (`/api/v1/projects`)
- `POST /`: Create AI Workspace.
- `GET /`: List paginated projects.
- `GET /{id}`: Project dashboard metrics.
- `PATCH /{id}`: Update defaults.
- `POST /{id}/archive`: Soft delete/archive.

### Documents (`/api/v1/documents`)
- `POST /upload`: Multipart upload (PDF).
- `GET /{id}/progress`: Poll background extraction status.
- `GET /{id}/chunks`: Paginated knowledge viewing.
- `GET /{id}/chunks/search?q=`: Native ILIKE database text search.

### Retrieval (`/api/v1/retrieval`)
- `POST /project/{id}/vectorize`: Batch embed all chunks into ChromaDB.
- `POST /project/{id}/playground`: Top-K semantic similarity test.

### Generation (`/api/v1/generation`)
- `POST /generate`: Triggers end-to-end LangGraph pipeline. Returns PPTX download URL.
