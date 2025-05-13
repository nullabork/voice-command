/**
 * Recognition Panel Component
 * Handles speech recognition display and system messages
 */
document.addEventListener('alpine:init', () => {
  Alpine.data('recognitionPanel', () => ({
    speechChunks: [],
    systemMessages: [],
    maxSpeechChunks: 20,
    maxSystemMessages: 10,
    isActive: false,
    
    init() {
      this.setupSocketListeners();
      this.setupEventListeners();
      
      // Share the active state with parent component
      this.$watch('$parent.isActive', (value) => {
        this.isActive = value;
      });
    },
    
    setupSocketListeners() {
      socket.on('speech_chunk', (data) => {
        this.addSpeechChunk(data.text);
      });
      
      socket.on('system_message', (data) => {
        this.addSystemMessage(data.type, data.message);
      });
    },
    
    setupEventListeners() {
      document.addEventListener('get-recent-speech', (event) => {
        const callback = event.detail?.callback;
        if (callback && typeof callback === 'function') {
          // Get the most recent speech chunk, if available
          const recentSpeech = this.speechChunks.length > 0 
            ? this.speechChunks[this.speechChunks.length - 1] 
            : '';
          callback(recentSpeech);
        }
      });
    },
    
    addSpeechChunk(text) {
    //   this.speechChunks.push(text); insert into the first position
      this.speechChunks.unshift(text);
      
      // Keep the maximum number of chunks
      if (this.speechChunks.length > this.maxSpeechChunks) {
        this.speechChunks = this.speechChunks.slice(0, this.maxSpeechChunks);
      }
      
      // Scroll to bottom
      this.$nextTick(() => {
        const speechOutput = document.getElementById('speech-output');
        if (speechOutput) {
          speechOutput.scrollTop = speechOutput.scrollHeight;
        }
      });
    },
    
    addSystemMessage(type, message) {
      this.systemMessages.push({
        type: type || 'info',
        message: message
      });
      
      // Keep the maximum number of messages
      if (this.systemMessages.length > this.maxSystemMessages) {
        this.systemMessages = this.systemMessages.slice(-this.maxSystemMessages);
      }
    },
    
    clearSpeechChunks() {
      this.speechChunks = [];
    }
  }));
}); 