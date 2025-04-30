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
            script: ''
        },
        editingCommand: null,
        previewResult: {
            show: false,
            success: true,
            message: ''
        },
        socket: null,

        /**
         * Initializes the application
         */
        init() {
            console.log('Initializing voice command app component (Alpine)');
            // Load commands on page load
            this.fetchCommands();
            
            // Get active state
            this.fetchActiveState();
            
            // Connect to WebSocket
            this.connectWebSocket();
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
            
            try {
                console.log('Adding command:', this.newCommand);
                const response = await fetch('api/commands', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        phrases: this.newCommand.phrases,
                        script: this.newCommand.script
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
            
            try {
                console.log('Saving edited command:', this.newCommand);
                const response = await fetch(`api/commands/${this.editingCommand.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        phrases: this.newCommand.phrases,
                        script: this.newCommand.script
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
                            script: this.newCommand.script
                        };
                    }
                    
                    console.log('Command updated successfully');
                    
                    // Reset form
                    this.editingCommand = null;
                    this.newCommand.phrases = [];
                    this.newCommand.currentPhrase = '';
                    this.newCommand.script = '';
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
                const response = await fetch('api/toggle');
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
                const response = await fetch('api/toggle', {
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
        }
    }));
});

console.log('main.js script finished'); 