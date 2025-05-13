/**
 * Commands Components
 * Handles command list display and management and command form
 */
document.addEventListener('alpine:init', () => {
  // Command List Component
  Alpine.data('commandList', () => ({
    commands: [],
    triggeredCommandId: null,
    
    init() {
      this.loadCommands();
      this.setupListeners();
    },
    
    setupListeners() {
      // Listen for command triggered events
      socket.on('command_triggered', (data) => {
        this.triggeredCommandId = data.command_id;
      });
      
      // Listen for command modifications
      document.addEventListener('command-added', () => this.loadCommands());
      document.addEventListener('command-updated', () => this.loadCommands());
      document.addEventListener('command-deleted', () => this.loadCommands());
    },
    
    loadCommands() {
      fetch('/api/commands')
        .then(response => response.json())
        .then(data => {
          this.commands = data;
        });
    },
    
    previewScript(script) {
      fetch('/api/script-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ script })
      })
        .then(response => response.json())
        .then(data => {
          // Use the shared toast from the parent
          this.$dispatch('preview-result', {
            success: data.success,
            message: data.result || data.error
          });
        });
    },
    
    startEditing(command) {
      // Dispatch event to the command form component
      this.$dispatch('edit-command', command);
    },
    
    deleteCommand(commandId) {
      if (!confirm('Are you sure you want to delete this command?')) {
        return;
      }
      
      fetch(`/api/commands/${commandId}`, {
        method: 'DELETE'
      })
        .then(response => {
          if (response.ok) {
            this.loadCommands();
            document.dispatchEvent(new CustomEvent('command-deleted'));
          }
        });
    }
  }));
  
  // Command Form Component
  Alpine.data('commandForm', () => ({
    newCommand: {
      phrases: [],
      currentPhrase: '',
      script: '',
      understand_sentiment: false,
      partial_match: false
    },
    editingCommand: null,
    editingCommandId: null,
    
    init() {
      this.resetForm();
      console.log('Command form initialized');
      // Listen for edit command events
      document.addEventListener('edit-command', (event) => {
        this.startEditingCommand(event.detail);
      });
    },
    
    resetForm() {
      this.newCommand = {
        phrases: [],
        currentPhrase: '',
        script: '',
        understand_sentiment: false,
        partial_match: false
      };
      this.editingCommand = null;
      this.editingCommandId = null;
    },
    
    addPhrase() {
      if (!this.newCommand.currentPhrase.trim()) {
        return;
      }
      
      // Don't add duplicates
      if (!this.newCommand.phrases.includes(this.newCommand.currentPhrase.trim())) {
        this.newCommand.phrases.push(this.newCommand.currentPhrase.trim());
      }
      
      this.newCommand.currentPhrase = '';
    },
    
    removePhrase(phrase) {
      this.newCommand.phrases = this.newCommand.phrases.filter(p => p !== phrase);
    },
    
    useRecentSpeech() {
      // Get the most recent speech from recognition panel
      document.dispatchEvent(new CustomEvent('get-recent-speech', {
        detail: {
          callback: (text) => {
            if (text) {
              this.newCommand.currentPhrase = text;
            }
          }
        }
      }));
    },
    
    addCommand() {
      // Add the current phrase if it's not empty
      if (this.newCommand.currentPhrase.trim()) {
        this.addPhrase();
      }
      
      if (this.newCommand.phrases.length === 0) {
        alert('You must add at least one phrase.');
        return;
      }
      
      fetch('/api/commands', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.newCommand)
      })
        .then(response => response.json())
        .then(data => {
          if (data.id) {
            document.dispatchEvent(new CustomEvent('command-added'));
            this.resetForm();
          }
        });
    },
    
    startEditingCommand(command) {
        console.log('Starting edit for command:', command);
      this.editingCommand = command;
      this.editingCommandId = command.id;
      this.newCommand = {
        phrases: [...command.phrases],
        currentPhrase: '',
        script: command.script,
        understand_sentiment: command.understand_sentiment,
        partial_match: command.partial_match
      };
    },
    
    saveEdit() {
      // Add the current phrase if it's not empty
      if (this.newCommand.currentPhrase.trim()) {
        this.addPhrase();
      }
      
      if (this.newCommand.phrases.length === 0) {
        alert('You must add at least one phrase.');
        return;
      }
      
      fetch(`/api/commands/${this.editingCommandId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.newCommand)
      })
        .then(response => response.json())
        .then(data => {
          if (data.id) {
            document.dispatchEvent(new CustomEvent('command-updated'));
            this.resetForm();
          }
        });
    },
    
    cancelEdit() {
      this.resetForm();
    }
  }));
}); 