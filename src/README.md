# Voice Command Application - Source Code

## Directory Structure

The application is organized into the following modules:

- **api/** - Contains API routes and endpoints
- **core/** - Contains the main application logic and Flask app
- **db/** - Database interaction and models
- **speech/** - Speech recognition functionality
- **input/** - Input simulation and keyboard/mouse control
- **utils/** - Utility functions and helpers
- **web/** - Web interface templates and components

## Usage

To run the application:

```
python main.py
```

## Module Descriptions

### core/
Contains the main Flask application and core functionality. The `app.py` file initializes the Flask app and sets up the web server.

### api/
Contains the API routes and endpoints as a Flask Blueprint. These provide the REST API for the frontend.

### db/
Handles all database interactions using SQLite. The main file is `db.py`.

### speech/
Contains the speech recognition functionality, including OpenAI integration for processing voice commands.

### input/
Contains code for simulating keyboard and mouse input based on recognized commands.

### utils/
Utility functions and helpers used across the application.

### web/
Templates and static files for the web interface. 