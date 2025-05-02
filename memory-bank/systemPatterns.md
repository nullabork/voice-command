# System Patterns

## Architecture Overview
The Voice Command System follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐     ┌───────────────────┐
│  Web Interface  │◄────┤   Flask Server    │
└────────┬────────┘     └─────────┬─────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐     ┌───────────────────┐
│   WebSockets    │◄────┤  API Endpoints    │
└────────┬────────┘     └─────────┬─────────┘
         │                        │
         └───────────┬────────────┘
                     │
         ┌───────────▼───────────┐
         │    Database Layer     │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐   ┌───────────────────┐
         │  Speech Recognition   │◄──┤   Microphone      │
         └───────────┬───────────┘   └───────────────────┘
                     │
         ┌───────────▼───────────┐   ┌───────────────────┐
         │ Input Simulation      │──►│ Operating System  │
         └───────────────────────┘   └───────────────────┘
```

## Design Patterns

### Observer Pattern
- The Speech Recognition module publishes events when speech is recognized
- The Web Interface observes these events via WebSockets
- This allows real-time updating without polling

### Command Pattern
- Voice commands are mapped to keyboard scripts
- Each script is a sequence of commands to be executed
- This provides abstraction between the trigger (voice) and the actions (keyboard)

### Factory Pattern
- Database factories create command objects from database records
- Input simulation factory creates appropriate keyboard action objects based on script syntax

### Singleton Pattern
- Speech recognition manager is a singleton to ensure only one instance is running
- Database connection is managed as a singleton

## Key Module Interactions

### Speech Recognition Flow
1. Audio is captured from the microphone
2. Speech recognition processes audio chunks
3. Recognized text is matched against command phrases
4. Matching commands trigger script execution
5. Recognition events are broadcast via WebSockets

### Command Management Flow
1. User defines command phrases and scripts via web interface
2. API endpoints process CRUD operations
3. Database layer persists command definitions
4. Speech recognition module loads updated commands

### Error Handling Patterns
- Automatic restart of speech recognition on failure
- Circuit breaker pattern for external services (e.g., Google speech API)
- Graceful degradation when components fail

## Threading Model
- Main thread serves the web interface and API endpoints
- Speech recognition runs in a dedicated background thread
- Command execution runs in separate threads to prevent blocking

## State Management
- Listening state is persisted in the database
- Command definitions are loaded from database at startup
- Real-time state is shared via WebSockets between server and client 