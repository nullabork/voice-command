# Implementation Plan

1.  **Project Setup:**
    - Initialize Python project (`requirements.txt`, `.gitignore`).
    - Create basic directory structure (`/`, `/public`, `/public/js`).
    - Create main application file (e.g., `app.py`).

2.  **Backend - Database & Core Models:**
    - Set up SQLite database connection.
    - Define database schema (e.g., a `commands` table with `phrase` and `script` columns).
    - Implement basic CRUD functions for the database table.

3.  **Backend - HTTP Server & Static Files:**
    - Implement a basic HTTP server (using chosen library/framework).
    - Configure it to serve static files from the `public` directory.

4.  **Frontend - Basic UI Shell:**
    - Create `public/index.html`.
    - Include Alpine.js and DaisyUI via CDNs.
    - Set up basic page layout (e.g., title, area for command list, add form, toggle).

5.  **Backend - API Endpoints:**
    - Create API endpoint `GET /api/commands` to fetch all commands.
    - Create API endpoint `POST /api/commands` to add a new command.
    - Create API endpoint `DELETE /api/commands/{id}` to remove a command.
    - Create API endpoint `POST /api/toggle` (or similar) to get/set the active state.

6.  **Frontend - API Integration:**
    - Use Alpine.js in `main.js` (or separate files in `public/js/`) to:
        - Fetch and display the list of commands.
        - Submit the 'add command' form to the API.
        - Implement deletion buttons/actions.
        - Implement the state toggle switch, calling the API.

7.  **Backend - Speech Recognition:**
    - Integrate the `speech_recognition` library.
    - Implement microphone listening loop.
    - Process audio to detect speech chunks between silence.

8.  **Backend - WebSocket:**
    - Implement a WebSocket server.
    - Push recognized speech chunks to connected clients.

9.  **Frontend - WebSocket Integration:**
    - Connect to the backend WebSocket from the frontend JavaScript.
    - Display incoming speech chunks in a designated area on the page.

10. **Backend - Script Parsing & Execution:**
    - Implement the parser for the custom keyboard script format.
    - Integrate the `pynput` library.
    - Implement the core logic: When the backend is 'active', match recognized phrases to stored commands and execute the corresponding script using `pynput`.

11. **Refinement & Testing:**
    - Test end-to-end functionality: speaking, recognition, script execution.
    - Test UI interactions.
    - Refine UI/UX based on testing.
    - Test keyboard injection in target applications (e.g., DCS).
    - Add error handling and logging.
