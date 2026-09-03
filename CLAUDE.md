# Medlio - Voice Enabled Customer Feedback Portal

## Project Overview
Medlio is a web application that allows users to submit voice feedback, which is then automatically transcribed and analyzed for sentiment. Admins can review these submissions via a dedicated dashboard.

### Tech Stack
- **Frontend**: React + Material UI
- **Backend**: Flask (REST API)
- **Database**: PostgreSQL
- **Storage**: Cloud Object Storage (Audio files)
- **STT**: Groq Whisper Large V3
- **AI/Sentiment**: Gemini 3.6 Flash
- **Auth**: JWT with Role-Based Access Control (User/Admin)

## Subagents
To maintain high quality and clear separation of concerns, the following roles are defined:
- **Analysis**: Requirements gathering, architectural design, and task decomposition.
- **Coder**: Implementation of frontend and backend logic.
- **Review**: Code review, standards compliance, and requirement verification.
- **Testing**: Test creation and execution (Unit, Integration, E2E) and edge-case validation.

## Documentation Plan
The project maintains detailed documentation in the `docs/` directory. Each file serves a specific purpose:
- `docs/setup.md`: Local environment setup and execution instructions.
- `docs/api_usage.md`: Detailed REST API specification.
- `docs/recording_limitations.md`: Constraints on audio uploads (size, format, duration).
- `docs/troubleshooting.md`: Guide for common errors and resolutions.
- `docs/voice_processing_flow.md`: Technical walkthrough of the audio processing pipeline.
- `docs/technical_bottlenecks.md`: Analysis of performance constraints and architectural limits.
- `docs/accuracy_challenges.md`: Documentation of STT/LLM accuracy issues and mitigations.
- `docs/future_enhancements.md`: Roadmap for future features and improvements.
- `docs/update_log.md`: Chronological log of all project updates and changes.

## Development Guidelines
- **Simplicity**: Avoid over-engineering. Stay aligned with the assessment requirements.
- **Security**: Never commit secrets. Use environment variables. Enforce authorization on the backend.
- **Code Style**: Match existing naming conventions and comment density.
- **API**: Follow RESTful principles strictly.
