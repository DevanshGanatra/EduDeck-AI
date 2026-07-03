# 1. Record Architecture Decisions

Date: 2026-07-04

## Status
Accepted

## Context
We need a structured way to record architectural decisions for the EduDeck AI platform to maintain a historical log of why technical choices were made. As the project evolves, understanding the rationale behind past decisions is crucial for onboarding and future scalability.

## Decision
We will use Architecture Decision Records (ADRs) as proposed by Michael Nygard. Each significant architectural, design, or technological decision will be documented in a markdown file within the `docs/architecture/` directory.

## Alternatives Considered
- **No formal documentation**: Relying on git commit messages or tribal knowledge. (Rejected: hard to search and easily lost).
- **Centralized wiki**: Using Confluence or Notion. (Rejected: disconnects documentation from the codebase).

## Rationale
Storing ADRs alongside the codebase in version control ensures they remain synchronized with the code. Markdown is lightweight and easily readable. 

## Trade-offs
- Requires discipline to write an ADR for every major decision.
- May become outdated if not actively maintained.

## Future Implications
Future developers will use this directory to understand the evolution of the system architecture without having to guess the intent behind complex systems like LangGraph or the async DB setup.
