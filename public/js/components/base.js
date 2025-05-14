/**
 * Base Application Component
 * Core functionality and shared state for the Voice Command System
 */

// Initialize Socket.IO globally so all components can access it
const socket = io();

document.addEventListener('alpine:init', () => {
  // Create main app component
  Alpine.data('baseApp', () => ({
    // Shared State
    isActive: false,
    sentimentMode: false,
    scriptsEnabled: true,
    showSettings: false,
    showHelp: false,
    showCommandForm: false,
    previewResult: {
      show: false,
      success: true,
      message: ''
    },
    shortcutKey: '',
    aiTimeoutRemaining: 0,
    aiTimeoutInterval: null,
    
    // Initialize the app
    init() {
      this.loadActiveState();
      this.loadSentimentModeState();
      this.loadScriptsEnabledState();
      this.loadShortcutKey();
      this.setupSocketListeners();
      
      // Listen for preview result events from command list
      this.$el.addEventListener('preview-result', (event) => {
        this.showPreviewResult(event.detail.success, event.detail.message);
      });
      
      // Listen for close command form events
      this.$el.addEventListener('close-command-form', () => {
        this.showCommandForm = false;
      });
      
      // Listen for show command form events
      this.$el.addEventListener('show-command-form', () => {
        this.showCommandForm = true;
      });
      
      // Listen for custom events
      this.$watch('showHelp', (value) => {
        // If help modal is closed, make sure body scroll is restored
        if (!value) {
          document.body.classList.remove('overflow-hidden');
        }
      });
      
      // Listen for help event from child components
      this.$el.addEventListener('show-help', () => {
        this.showHelp = true;
      });
    },
    
    // Setup Socket.IO event listeners
    setupSocketListeners() {
      socket.on('connect', () => {
        console.log('Connected to server');
      });
      
      socket.on('active_state', (data) => {
        this.isActive = data.active;
      });
      
      socket.on('sentiment_mode', (data) => {
        this.sentimentMode = data.active;
      });
      
      socket.on('scripts_execution', (data) => {
        this.scriptsEnabled = data.active;
      });
      
      socket.on('ai_timeout', (data) => {
        if (data.active) {
          this.startAiTimeoutCounter(data.remainingSeconds);
        } else {
          this.stopAiTimeoutCounter();
        }
      });
    },
    
    // Active State
    loadActiveState() {
      fetch('/api/active')
        .then(response => response.json())
        .then(data => {
          this.isActive = data.active;
        });
    },
    
    toggleActiveState() {
        
        this.isActive = !this.isActive;
      fetch('/api/active', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ active: this.isActive })
      });
    },
    
    // Sentiment Mode
    loadSentimentModeState() {
      fetch('/api/sentiment-mode')
        .then(response => response.json())
        .then(data => {
          this.sentimentMode = data.active;
        });
    },
    
    toggleSentimentMode() {
      fetch('/api/sentiment-mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ active: !this.sentimentMode })
      })
        .then(response => response.json())
        .then(data => {
          this.sentimentMode = data.active;
        });
    },
    
    // Scripts Execution
    loadScriptsEnabledState() {
      fetch('/api/scripts-execution')
        .then(response => response.json())
        .then(data => {
          this.scriptsEnabled = data.active;
        });
    },
    
    toggleScriptsEnabled() {
      fetch('/api/scripts-execution', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
        .then(response => response.json())
        .then(data => {
          this.scriptsEnabled = data.active;
        });
    },
    
    // Shortcut Key
    loadShortcutKey() {
      fetch('/api/shortcut-key')
        .then(response => response.json())
        .then(data => {
          this.shortcutKey = data.shortcutKey;
        });
    },
    
    // AI Timeout Counter
    startAiTimeoutCounter(seconds) {
      this.stopAiTimeoutCounter();
      this.aiTimeoutRemaining = seconds;
      
      this.aiTimeoutInterval = setInterval(() => {
        this.aiTimeoutRemaining--;
        if (this.aiTimeoutRemaining <= 0) {
          this.stopAiTimeoutCounter();
        }
      }, 1000);
    },
    
    stopAiTimeoutCounter() {
      if (this.aiTimeoutInterval) {
        clearInterval(this.aiTimeoutInterval);
        this.aiTimeoutInterval = null;
      }
      this.aiTimeoutRemaining = 0;
    },
    
    // Preview Result Toast
    showPreviewResult(success, message) {
      this.previewResult = {
        show: true,
        success,
        message
      };
      
      // Auto-hide after 3 seconds
      setTimeout(() => {
        this.closePreviewResult();
      }, 3000);
    },
    
    closePreviewResult() {
      this.previewResult.show = false;
    }
  }));
}); 