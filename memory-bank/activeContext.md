# Active Context

## Current Focus
The project is currently focused on implementing and refining the core voice command recognition and keyboard simulation functionality. The primary goal is to ensure robust speech recognition with minimal latency between voice commands and keyboard actions.

## Recent Changes
- Implemented basic speech recognition with Google's API
- Created database schema for storing command mappings
- Developed keyboard scripting syntax and parser
- Built initial web interface with command management
- Added WebSocket support for real-time updates
- Implemented toggle control for enabling/disabling listening

## Upcoming Priorities
1. Improve error handling and recovery for speech recognition failures
2. Add support for alternative phrases to improve recognition accuracy
3. Enhance the script testing functionality in the web interface
4. Optimize latency between command recognition and execution
5. Add more detailed feedback on command execution status
6. Implement script validation to prevent syntax errors

## Current Challenges
- Speech recognition accuracy varies with different microphones and ambient noise
- Some applications require elevated privileges for keyboard simulation
- Balancing between simplicity of script syntax and power/flexibility
- Handling recognition errors gracefully without user intervention
- Ensuring the system starts automatically with correct state after restarts

## Active Decisions
- Using pynput as the primary keyboard simulation library for its low-level access
- Structuring commands with multiple alternative phrases for better recognition
- Keeping the interface simple and focused on command management
- Maintaining a modular architecture to allow component replacement
- Using SQLite for data persistence to minimize dependencies

## Design Preferences
- Favor simple, clean UI over complex features
- Prioritize reliability over adding new features
- Maintain clear separation between components
- Keep configuration in database rather than config files
- Use real-time WebSockets for immediate feedback
- Design for extensibility in keyboard script capabilities

## Implementation Insights
- Speech recognition works best with short, distinct command phrases
- Keyboard script syntax should balance readability with power
- WebSockets provide more responsive UI updates than polling
- Threading model must carefully handle shared resources
- Database schema should be flexible for future enhancements
- Error handling is critical for long-running background processes 