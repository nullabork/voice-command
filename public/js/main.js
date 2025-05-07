/**
 * Voice Command Application
 * Frontend Alpine.js component
 */
console.log('main.js script started');

// Define the component when Alpine initializes
// Attach the listener directly, as main.js loads before Alpine.js
document.addEventListener('alpine:init', () => {
    console.log('alpine:init event fired');
    
    Alpine.data('voiceCommandApp', () => ({
        commands: [],
        isActive: false,
        recentSpeech: '',
        newCommand: {
            phrases: [],
            currentPhrase: '',  // For the input field
            script: '',
            understand_sentiment: false,
            partial_match: false
        },
        editingCommand: null,
        previewResult: {
            show: false,
            success: true,
            message: ''
        },
        socket: null,
        // Settings
        showSettings: false,
        showHelp: false,  // Flag for help modal visibility
        openaiApiKey: '',
        apiKeyStatus: {
            isSet: false,
            apiKey: ''
        },
        // OpenAI stats
        openaiStats: {
            requestCount: 0
        },
        // Triggered command tracking
        triggeredCommandId: null,
        // Shortcut key settings
        shortcutKey: '',
        shortcutKeyInput: '',
        listeningForShortcut: false,
        sentimentMode: false,
        // AI timeout settings
        aiTimeout: {
            enabled: false,
            seconds: 60
        },
        aiTimeoutRemaining: 0,
        // Script execution state
        scriptsEnabled: true,

        /**
         * Initializes the application
         */
        init() {
            console.log('Initializing voice command app component (Alpine)');
            // Load commands on page load
            this.fetchCommands();
            
            // Get active state
            this.fetchActiveState();
            
            // Get API key status
            this.fetchApiKeyStatus();
            
            // Get OpenAI stats
            this.fetchOpenAIStats();
            
            // Get shortcut key and sentiment mode status
            this.fetchShortcutKey();
            this.fetchSentimentMode();
            
            // Get AI timeout settings
            this.fetchAiTimeoutSettings();
            
            // Connect to WebSocket
            this.connectWebSocket();
            
            // Set up auto-refresh of OpenAI stats
            setInterval(() => {
                this.fetchOpenAIStats();
            }, 30000); // Refresh every 30 seconds
            
            // Add global keyboard event listener for shortcut key
            this.setupShortcutKeyListener();
        },

        /**
         * Set up listener for the global shortcut key
         */
        setupShortcutKeyListener() {
            document.addEventListener('keydown', (event) => {
                // If we're in settings modal capturing a new shortcut
                if (this.listeningForShortcut) {
                    // Prevent default browser actions
                    event.preventDefault();
                    
                    // Generate shortcut string (e.g., "ctrl+shift+p")
                    const modifiers = [];
                    if (event.ctrlKey) modifiers.push('ctrl');
                    if (event.altKey) modifiers.push('alt');
                    if (event.shiftKey) modifiers.push('shift');
                    if (event.metaKey) modifiers.push('meta');
                    
                    // Get the key (excluding modifier keys)
                    let key = event.key.toLowerCase();
                    if (['control', 'alt', 'shift', 'meta'].includes(key)) {
                        // Only modifier was pressed, wait for the actual key
                        return;
                    }
                    
                    // Create the shortcut string
                    this.shortcutKeyInput = modifiers.length > 0 
                        ? [...modifiers, key].join('+') 
                        : key;
                    
                    // Stop listening for shortcut
                    this.listeningForShortcut = false;
                    return;
                }
                
                // If not capturing, check if the pressed keys match the shortcut
                if (this.shortcutKey) {
                    const modifierMap = {
                        'ctrl': event.ctrlKey,
                        'alt': event.altKey,
                        'shift': event.shiftKey,
                        'meta': event.metaKey
                    };
                    
                    const parts = this.shortcutKey.split('+');
                    const keyPart = parts[parts.length - 1].toLowerCase();
                    const modifierParts = parts.slice(0, -1).map(m => m.toLowerCase());
                    
                    // Check if all modifiers in the shortcut are pressed
                    const modifiersMatch = modifierParts.every(mod => modifierMap[mod]);
                    
                    // Check if the key matches
                    const keyMatches = event.key.toLowerCase() === keyPart;
                    
                    // If all parts match, toggle sentiment mode
                    if (modifiersMatch && keyMatches) {
                        console.log('Shortcut key pressed - toggling sentiment mode');
                        this.toggleSentimentMode();
                        event.preventDefault();
                    }
                }
            });
        },

        /**
         * Starts listening for a shortcut key combination
         */
        captureShortcutKey() {
            this.listeningForShortcut = true;
            this.shortcutKeyInput = 'Press a key combination...';
        },

        /**
         * Saves the shortcut key to the database
         */
        async saveShortcutKey() {
            if (!this.shortcutKeyInput || this.shortcutKeyInput === 'Press a key combination...') {
                this.shortcutKeyInput = ''; // Clear input if it's the placeholder
                return;
            }

            try {
                console.log('Saving shortcut key:', this.shortcutKeyInput);
                const response = await fetch('api/shortcut-key', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        shortcut_key: this.shortcutKeyInput
                    })
                });

                if (response.ok) {
                    // Update local shortcut key
                    this.shortcutKey = this.shortcutKeyInput;
                    
                    // Show success message
                    this.previewResult = {
                        show: true,
                        success: true,
                        message: 'Shortcut key saved successfully'
                    };
                } else {
                    console.error('Failed to save shortcut key');
                    this.previewResult = {
                        show: true,
                        success: false,
                        message: 'Failed to save shortcut key'
                    };
                }
            } catch (error) {
                console.error('Error saving shortcut key:', error);
                this.previewResult = {
                    show: true,
                    success: false,
                    message: 'Error saving shortcut key: ' + error.message
                };
            }
        },

        /**
         * Fetches the shortcut key from the API
         */
        async fetchShortcutKey() {
            try {
                console.log('Fetching shortcut key...');
                const response = await fetch('api/shortcut-key');
                if (response.ok) {
                    const data = await response.json();
                    this.shortcutKey = data.shortcut_key;
                    this.shortcutKeyInput = data.shortcut_key;
                    console.log('Shortcut key loaded:', this.shortcutKey || 'None set');
                } else {
                    console.error('Failed to fetch shortcut key');
                }
            } catch (error) {
                console.error('Error fetching shortcut key:', error);
            }
        },

        /**
         * Fetches the sentiment mode state from the API
         */
        async fetchSentimentMode() {
            try {
                console.log('Fetching sentiment mode state...');
                const response = await fetch('api/sentiment-mode');
                if (response.ok) {
                    const data = await response.json();
                    this.sentimentMode = data.active;
                    console.log('Sentiment mode state:', this.sentimentMode ? 'Active' : 'Inactive');
                } else {
                    console.error('Failed to fetch sentiment mode state');
                }
            } catch (error) {
                console.error('Error fetching sentiment mode state:', error);
            }
        },

        /**
         * Toggles the sentiment mode
         */
        async toggleSentimentMode() {
            try {
                console.log('Toggling sentiment mode...');
                
                // If we have a socket connection, use it for faster toggling
                if (this.socket) {
                    this.socket.emit('toggle_sentiment_mode');
                    return; // The server will send back an update via WebSocket
                }
                
                // Fallback to REST API
                const response = await fetch('api/sentiment-mode', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    this.sentimentMode = data.active;
                    
                    // Show notification
                    this.previewResult = {
                        show: true,
                        success: true,
                        message: `Sentiment mode ${this.sentimentMode ? 'activated' : 'deactivated'}`
                    };
                    
                    console.log('Sentiment mode toggled to:', this.sentimentMode);
                } else {
                    console.error('Failed to toggle sentiment mode');
                }
            } catch (error) {
                console.error('Error toggling sentiment mode:', error);
            }
        },

        /**
         * Fetches all commands from the API
         */
        async fetchCommands() {
            try {
                console.log('Fetching commands...');
                const response = await fetch('api/commands');
                if (response.ok) {
                    this.commands = await response.json();
                    console.log('Commands loaded:', this.commands);
                } else {
                    console.error('Failed to fetch commands');
                }
            } catch (error) {
                console.error('Error fetching commands:', error);
            }
        },

        /**
         * Fetches the OpenAI API key status
         */
        async fetchApiKeyStatus() {
            try {
                console.log('Fetching API key status...');
                const response = await fetch('api/openai-key');
                if (response.ok) {
                    const data = await response.json();
                    this.apiKeyStatus = {
                        isSet: data.isSet,
                        apiKey: data.apiKey
                    };
                    console.log('API key status:', this.apiKeyStatus.isSet ? 'Set' : 'Not set');
                } else {
                    console.error('Failed to fetch API key status');
                }
            } catch (error) {
                console.error('Error fetching API key status:', error);
            }
        },
        
        /**
         * Fetches the OpenAI stats
         */
        async fetchOpenAIStats() {
            try {
                console.log('Fetching OpenAI stats...');
                const response = await fetch('api/openai-stats');
                if (response.ok) {
                    const data = await response.json();
                    this.openaiStats.requestCount = data.requestCount;
                    console.log('OpenAI request count:', this.openaiStats.requestCount);
                } else {
                    console.error('Failed to fetch OpenAI stats');
                }
            } catch (error) {
                console.error('Error fetching OpenAI stats:', error);
            }
        },

        /**
         * Saves the OpenAI API key
         */
        async saveApiKey() {
            if (!this.openaiApiKey.trim()) {
                alert('Please enter a valid API key');
                return;
            }

            try {
                console.log('Saving API key...');
                const response = await fetch('api/openai-key', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        apiKey: this.openaiApiKey
                    })
                });

                if (response.ok) {
                    // Clear the input field
                    this.openaiApiKey = '';
                    
                    // Refresh the API key status
                    await this.fetchApiKeyStatus();
                    
                    // Show success message
                    this.previewResult = {
                        show: true,
                        success: true,
                        message: 'API key saved successfully'
                    };
                } else {
                    console.error('Failed to save API key');
                    this.previewResult = {
                        show: true,
                        success: false,
                        message: 'Failed to save API key'
                    };
                }
            } catch (error) {
                console.error('Error saving API key:', error);
                this.previewResult = {
                    show: true,
                    success: false,
                    message: 'Error saving API key: ' + error.message
                };
            }
        },

        /**
         * Adds a phrase to the current command being edited
         */
        addPhrase() {
            if (!this.newCommand.currentPhrase) return;
            
            // Don't add duplicate phrases
            if (!this.newCommand.phrases.includes(this.newCommand.currentPhrase)) {
                this.newCommand.phrases.push(this.newCommand.currentPhrase);
            }
            
            // Clear the input field
            this.newCommand.currentPhrase = '';
        },
        
        /**
         * Removes a phrase from the current command being edited
         */
        removePhrase(phrase) {
            this.newCommand.phrases = this.newCommand.phrases.filter(p => p !== phrase);
        },

        /**
         * Adds a new command
         */
        async addCommand() {
            // Make sure we have at least one phrase
            if (this.newCommand.currentPhrase && !this.newCommand.phrases.includes(this.newCommand.currentPhrase)) {
                this.newCommand.phrases.push(this.newCommand.currentPhrase);
            }
            
            if (this.newCommand.phrases.length === 0) {
                alert("Please add at least one voice phrase");
                return;
            }
            
            // Validate API key if sentiment analysis is enabled
            if (this.newCommand.understand_sentiment && !this.apiKeyStatus.isSet) {
                if (confirm("Sentiment analysis requires an OpenAI API key. Would you like to set it up now?")) {
                    this.showSettings = true;
                    return;
                }
            }
            
            try {
                console.log('Adding command:', this.newCommand);
                const response = await fetch('api/commands', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        phrases: this.newCommand.phrases,
                        script: this.newCommand.script,
                        understand_sentiment: this.newCommand.understand_sentiment,
                        partial_match: this.newCommand.partial_match
                    })
                });

                if (response.ok) {
                    const newCommand = await response.json();
                    this.commands.push(newCommand);
                    console.log('Command added successfully');
                    
                    // Reset form
                    this.newCommand.phrases = [];
                    this.newCommand.currentPhrase = '';
                    this.newCommand.script = '';
                    this.newCommand.understand_sentiment = false;
                    this.newCommand.partial_match = false;
                } else {
                    console.error('Failed to add command');
                }
            } catch (error) {
                console.error('Error adding command:', error);
            }
        },

        /**
         * Prepares a command for editing
         */
        startEditing(command) {
            console.log('Starting to edit command:', command);
            this.editingCommand = {
                id: command.id,
                phrases: [...command.phrases]
            };
            
            // Update the form with the command data
            this.newCommand.phrases = [...command.phrases];
            this.newCommand.currentPhrase = '';
            this.newCommand.script = command.script;
            this.newCommand.understand_sentiment = command.understand_sentiment || false;
            this.newCommand.partial_match = command.partial_match || false;
        },
        
        /**
         * Cancels command editing
         */
        cancelEditing() {
            console.log('Canceling edit');
            this.editingCommand = null;
            this.newCommand.phrases = [];
            this.newCommand.currentPhrase = '';
            this.newCommand.script = '';
            this.newCommand.understand_sentiment = false;
            this.newCommand.partial_match = false;
        },
        
        /**
         * Saves edited command
         */
        async saveEdit() {
            if (!this.editingCommand) return;
            
            // Make sure we have at least one phrase
            if (this.newCommand.currentPhrase && !this.newCommand.phrases.includes(this.newCommand.currentPhrase)) {
                this.newCommand.phrases.push(this.newCommand.currentPhrase);
            }
            
            if (this.newCommand.phrases.length === 0) {
                alert("Please add at least one voice phrase");
                return;
            }
            
            // Validate API key if sentiment analysis is enabled
            if (this.newCommand.understand_sentiment && !this.apiKeyStatus.isSet) {
                if (confirm("Sentiment analysis requires an OpenAI API key. Would you like to set it up now?")) {
                    this.showSettings = true;
                    return;
                }
            }
            
            try {
                console.log('Saving edited command:', this.newCommand);
                const response = await fetch(`api/commands/${this.editingCommand.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        phrases: this.newCommand.phrases,
                        script: this.newCommand.script,
                        understand_sentiment: this.newCommand.understand_sentiment,
                        partial_match: this.newCommand.partial_match
                    })
                });

                if (response.ok) {
                    // Update the command in the local array
                    const index = this.commands.findIndex(cmd => cmd.id === this.editingCommand.id);
                    if (index !== -1) {
                        this.commands[index] = {
                            id: this.editingCommand.id,
                            phrases: [...this.newCommand.phrases],
                            phrase: this.newCommand.phrases[0], // For backward compatibility
                            script: this.newCommand.script,
                            understand_sentiment: this.newCommand.understand_sentiment,
                            partial_match: this.newCommand.partial_match
                        };
                    }
                    
                    console.log('Command updated successfully');
                    
                    // Reset form after saving edit
                    this.editingCommand = null;
                    this.newCommand.phrases = [];
                    this.newCommand.currentPhrase = '';
                    this.newCommand.script = '';
                    this.newCommand.understand_sentiment = false;
                    this.newCommand.partial_match = false;
                } else {
                    console.error('Failed to update command');
                }
            } catch (error) {
                console.error('Error updating command:', error);
            }
        },

        /**
         * Deletes a command
         */
        async deleteCommand(id) {
            if (!confirm('Are you sure you want to delete this command?')) {
                return;
            }

            try {
                console.log('Deleting command with ID:', id);
                const response = await fetch(`api/commands/${id}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    this.commands = this.commands.filter(cmd => cmd.id !== id);
                    console.log('Command deleted successfully');
                    
                    // If we were editing this command, clear the form
                    if (this.editingCommand && this.editingCommand.id === id) {
                        this.editingCommand = null;
                        this.newCommand.phrases = [];
                        this.newCommand.currentPhrase = '';
                        this.newCommand.script = '';
                        this.newCommand.understand_sentiment = false;
                        this.newCommand.partial_match = false;
                    }
                } else {
                    console.error('Failed to delete command');
                }
            } catch (error) {
                console.error('Error deleting command:', error);
            }
        },
        
        /**
         * Previews/tests a command script
         */
        previewScript(script) {
            console.log('Previewing script:', script);
            if (!this.socket) {
                alert('Socket connection not available. Cannot preview script.');
                return;
            }
            
            // Show preview result with loading
            this.previewResult = {
                show: true,
                success: true,
                message: 'Executing script...'
            };
            
            // Send the script to the server for execution
            this.socket.emit('test_script', { script });
        },
        
        /**
         * Closes the preview result notification
         */
        closePreviewResult() {
            this.previewResult.show = false;
        },

        /**
         * Fetches the active state from the API
         */
        async fetchActiveState() {
            try {
                console.log('Fetching active state...');
                const response = await fetch('api/active');
                if (response.ok) {
                    const data = await response.json();
                    this.isActive = data.active;
                    console.log('Active state:', this.isActive);
                }
            } catch (error) {
                console.error('Error fetching active state:', error);
            }
        },

        /**
         * Toggles the active state
         */
        async toggleActiveState() {
            console.log('Toggling active state to:', this.isActive);
            try {
                const response = await fetch('api/active', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ active: this.isActive })
                });

                if (!response.ok) {
                    console.error('Failed to toggle active state');
                    // Revert UI if request failed
                    this.isActive = !this.isActive;
                }
            } catch (error) {
                console.error('Error toggling active state:', error);
                // Revert UI on error
                this.isActive = !this.isActive;
            }
        },

        /**
         * Connects to the WebSocket server
         */
        connectWebSocket() {
            console.log('Connecting to WebSocket...');
            try {
                // Ensure io is defined (from socket.io.min.js)
                if (typeof io === 'undefined') {
                    console.error('Socket.IO client (io) is not loaded!');
                    return;
                }
                this.socket = io();

                this.socket.on('connect', () => {
                    console.log('Connected to WebSocket server');
                });

                this.socket.on('speech_chunk', (data) => {
                    console.log('Received speech chunk:', data.text);
                    this.recentSpeech = data.text;
                });
                
                this.socket.on('script_result', (data) => {
                    console.log('Script execution result:', data);
                    this.previewResult = {
                        show: true,
                        success: data.success,
                        message: data.message
                    };
                });
                
                // Listen for command triggered events
                this.socket.on('command_triggered', (data) => {
                    console.log('Command triggered:', data);
                    // Set the triggered command ID to flash the row
                    this.triggeredCommandId = data.command_id;
                    
                    // Refresh OpenAI stats if a command was triggered
                    this.fetchOpenAIStats();
                });
                
                // Listen for sentiment mode change events
                this.socket.on('sentiment_mode', (data) => {
                    console.log('Sentiment mode update:', data);
                    this.sentimentMode = data.active;
                    
                    // Reset timeout remaining if sentiment mode is turned off
                    if (!data.active) {
                        this.aiTimeoutRemaining = 0;
                    }
                });

                this.socket.on('scripts_execution', (data) => {
                    console.log('Script execution update:', data);
                    this.scriptsEnabled = data.active;
                });
                
                // Listen for AI timeout events
                this.socket.on('ai_timeout', (data) => {
                    console.log('AI timeout update:', data);
                    if (data.active) {
                        this.aiTimeoutRemaining = data.remainingSeconds;
                    } else {
                        this.aiTimeoutRemaining = 0;
                    }
                });
                
                // Listen for AI timeout countdown updates
                this.socket.on('ai_timeout_update', (data) => {
                    if (data.active) {
                        this.aiTimeoutRemaining = data.remainingSeconds;
                    } else {
                        this.aiTimeoutRemaining = 0;
                    }
                });

                this.socket.on('disconnect', () => {
                    console.log('Disconnected from WebSocket server');
                });
            } catch (error) {
                console.error('Error connecting to WebSocket:', error);
            }
        },

        /**
         * Uses the most recent speech for a new command
         */
        useRecentSpeech() {
            if (this.recentSpeech) {
                console.log('Using recent speech:', this.recentSpeech);
                this.newCommand.currentPhrase = this.recentSpeech;
            }
        },

        /**
         * Fetches the AI mode timeout settings
         */
        async fetchAiTimeoutSettings() {
            try {
                console.log('Fetching AI timeout settings...');
                const response = await fetch('api/ai-timeout');
                if (response.ok) {
                    const data = await response.json();
                    this.aiTimeout.enabled = data.enabled;
                    this.aiTimeout.seconds = data.seconds;
                    console.log('AI timeout settings loaded:', this.aiTimeout);
                } else {
                    console.error('Failed to fetch AI timeout settings');
                }
            } catch (error) {
                console.error('Error fetching AI timeout settings:', error);
            }
        },

        /**
         * Saves the AI mode timeout settings
         */
        async saveAiTimeout() {
            try {
                console.log('Saving AI timeout settings...');
                const response = await fetch('api/ai-timeout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        enabled: this.aiTimeout.enabled,
                        seconds: parseInt(this.aiTimeout.seconds)
                    })
                });

                if (response.ok) {
                    // Show success message
                    this.previewResult = {
                        show: true,
                        success: true,
                        message: this.aiTimeout.enabled ? 
                            `AI timeout set to ${this.aiTimeout.seconds} seconds` : 
                            'AI timeout disabled'
                    };
                } else {
                    console.error('Failed to save AI timeout settings');
                }
            } catch (error) {
                console.error('Error saving AI timeout settings:', error);
            }
        },

        /**
         * Toggles the scripts execution state
         */
        async toggleScriptsEnabled() {
            try {
                console.log('Toggling scripts execution state...');
                
                // If we have a socket connection, use it for faster toggling
                if (this.socket) {
                    this.socket.emit('toggle_scripts_execution');
                    return; // The server will send back an update via WebSocket
                }
                
                // Fallback to REST API
                const response = await fetch('api/scripts-execution', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    this.scriptsEnabled = data.active;
                    
                    // Show notification
                    this.previewResult = {
                        show: true,
                        success: true,
                        message: `Script execution ${this.scriptsEnabled ? 'enabled' : 'disabled'}`
                    };
                    
                    console.log('Script execution toggled to:', this.scriptsEnabled);
                } else {
                    console.error('Failed to toggle script execution');
                }
            } catch (error) {
                console.error('Error toggling script execution:', error);
            }
        }
    }));
});

console.log('main.js script finished'); 