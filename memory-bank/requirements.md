# Application Requirements

## Core Functionality
- Listen to the default OS microphone device for user speech.
- Perform speech-to-text processing on audio chunks, detecting text between periods of silence.
- Match recognized phrases against a user-defined list of phrases.
- Each phrase is mapped to a script containing a sequence of keyboard actions (keystrokes, combinations, delays).
- Execute the corresponding keyboard script when a phrase is matched.
- Inject the keyboard actions into the active operating system window.
- Automatically restart speech recognition if it fails unexpectedly.
- Maintain listening state across server restarts.

## Configuration & Management (via Web Interface)
- **View Mappings:** Display a list of all currently defined voice phrase-to-keyboard script mappings.
- **Add Mappings:** Allow users to define new mappings:
    - Input a voice phrase (or potentially use a recently spoken chunk).
    - Input a keyboard script according to the specified format.
- **Edit Mappings:** Allow users to edit existing phrase-to-script mappings.
- **Remove Mappings:** Allow users to delete existing mappings.
- **Test Scripts:** Allow testing of keyboard scripts from the UI before saving.
- **Real-time Speech Display:** Show the recognized text chunks from the microphone in real-time on the web interface (facilitates adding new phrases).
- **Activation Toggle:** Provide a control (e.g., a toggle switch) on the web page to enable or disable the core voice listening and command execution functionality of the backend.
- **Feedback System:** Provide visual feedback about script execution results.

## Keyboard Script Format
- **Comments:**
    - Lines starting with `--` are ignored.
    - Text after `#` on any line is ignored.
- **Delays:** Lines ending with `ms` (milliseconds) or `s` (seconds) specify delays.
- **Typing:** Lines starting with `type "` denote typing the enclosed string.
- **Hotkeys:** Key combinations use `+` (e.g., `shift+f`, `ctrl+alt+delete`).
- **Single Keys:** Any other non-empty, non-comment line represents a single key press (e.g., `enter`, `f1`, `a`).

## Non-Functional Requirements
- The application should be responsive enough to inject commands relatively quickly after a phrase is spoken.
- The web interface should be simple and intuitive.
- The system should be resilient to failures, with automatic recovery.
- The codebase should be modular and well-organized for maintainability.
- The system should provide clear feedback on actions to the user.
