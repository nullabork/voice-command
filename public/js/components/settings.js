/**
 * Settings Component
 * Handles application settings
 */
document.addEventListener('alpine:init', () => {
  Alpine.data('settingsPanel', () => ({
    openaiApiKey: '',
    apiKeyStatus: {
      isSet: false,
      apiKey: ''
    },
    aiTimeout: {
      enabled: false,
      seconds: 60
    },
    openaiStats: {
      requestCount: 0
    },
    
    init() {
      this.loadApiKeyStatus();
      this.loadAiTimeoutSettings();
      this.loadOpenAiStats();
      
      // Listen for settings toggle from parent
      this.$watch('$parent.showSettings', (value) => {
        if (value) {
          this.refreshSettings();
        }
      });
    },
    
    refreshSettings() {
      this.loadApiKeyStatus();
      this.loadAiTimeoutSettings();
      this.loadOpenAiStats();
    },
    
    loadApiKeyStatus() {
      fetch('/api/openai-key')
        .then(response => response.json())
        .then(data => {
          this.apiKeyStatus = data;
        });
    },
    
    saveApiKey() {
      fetch('/api/openai-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey: this.openaiApiKey })
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            this.loadApiKeyStatus();
            this.openaiApiKey = '';
          }
        });
    },
    
    loadAiTimeoutSettings() {
      fetch('/api/ai-timeout')
        .then(response => response.json())
        .then(data => {
          this.aiTimeout = data;
        });
    },
    
    saveAiTimeout() {
      fetch('/api/ai-timeout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.aiTimeout)
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Update UI with saved values
            this.aiTimeout.enabled = data.enabled;
            this.aiTimeout.seconds = data.seconds;
          }
        })
        .catch(error => {
          console.error('Error saving AI timeout settings:', error);
        });
    },
    
    loadOpenAiStats() {
      fetch('/api/openai-stats')
        .then(response => response.json())
        .then(data => {
          this.openaiStats = data;
        });
    }
  }));
}); 