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
      // Open the command form modal
      this.$dispatch('show-command-form');
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
    captureIndex: null, // Track which input is capturing speech
    
    init() {
      this.resetForm();
      console.log('Command form initialized');
      // Listen for edit command events
      document.addEventListener('edit-command', (event) => {
        this.startEditingCommand(event.detail);
      });
      
      // Listen for speech chunks
      document.addEventListener('speech-chunk', (event) => {
        this.handleSpeechChunk(event.detail.text);
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
      this.captureIndex = null;
    },
    
    // Handle incoming speech chunk
    handleSpeechChunk(text) {
      if (this.captureIndex === null || text.trim() === '') {
        return;
      }
      
      if (this.captureIndex === -1) {
        // Update current phrase input
        this.newCommand.currentPhrase = text;
      } else if (this.captureIndex >= 0 && this.captureIndex < this.newCommand.phrases.length) {
        // Update existing phrase
        this.newCommand.phrases[this.captureIndex] = text;
      }
    },
    
    // Toggle speech capture for an input
    toggleSpeechCapture(index) {
      if (this.captureIndex === index) {
        // If already capturing on this input, turn it off
        this.captureIndex = null;
      } else {
        // Turn off any current capture and enable for this input
        this.captureIndex = index;
      }
    },
    
    // Handle phrase input for dynamic inputs
    addEmptyInput() {
      if (this.newCommand.currentPhrase.trim() !== '') {
        this.newCommand.phrases.push(this.newCommand.currentPhrase.trim());
        this.newCommand.currentPhrase = '';
      }
    },
    
    // Clean up empty inputs when focus is lost
    cleanupEmptyInputs() {
      // Remove empty phrases
      this.newCommand.phrases = this.newCommand.phrases.filter(phrase => phrase.trim() !== '');
    },
    
    // Handle input in an existing phrase
    handlePhraseInput(index) {
      // We don't need this anymore as we're not automatically creating inputs
    },
    
    // Handle blur on an existing phrase
    handlePhraseBlur(index) {
      // If phrase is empty, remove it
      if (this.newCommand.phrases[index].trim() === '') {
        this.removePhrase(index);
      }
      
      // Clean up all empty phrases
      this.cleanupEmptyInputs();
    },
    
    // Handle blur on the current (last) phrase input
    handleCurrentPhraseBlur() {
      // If the current phrase is not empty, add it to phrases
      if (this.newCommand.currentPhrase.trim() !== '') {
        this.newCommand.phrases.push(this.newCommand.currentPhrase.trim());
        this.newCommand.currentPhrase = '';
      }
      
      // Clean up all empty phrases
      this.cleanupEmptyInputs();
    },
    
    // Remove a phrase by index
    removePhrase(index) {
      this.newCommand.phrases.splice(index, 1);
    },
    
    addCommand() {
      // Add the current phrase if it's not empty
      if (this.newCommand.currentPhrase.trim()) {
        this.newCommand.phrases.push(this.newCommand.currentPhrase.trim());
        this.newCommand.currentPhrase = '';
      }
      
      // Clean up any empty phrases
      this.newCommand.phrases = this.newCommand.phrases.filter(phrase => phrase.trim() !== '');
      
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
            // Close the command form modal
            this.$dispatch('close-command-form');
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
        this.newCommand.phrases.push(this.newCommand.currentPhrase.trim());
        this.newCommand.currentPhrase = '';
      }
      
      // Clean up any empty phrases
      this.newCommand.phrases = this.newCommand.phrases.filter(phrase => phrase.trim() !== '');
      
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
            // Close the command form modal
            this.$dispatch('close-command-form');
          }
        });
    },
    
    cancelEdit() {
      this.resetForm();
      // Close the command form modal
      this.$dispatch('close-command-form');
    }
  }));
}); 