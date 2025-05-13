/**
 * Help Panel Component
 * Handles the help modal and related functionality
 */
document.addEventListener('alpine:init', () => {
  Alpine.data('helpPanel', () => ({
    init() {
      // Share the show/hide state with parent component
      this.$watch('$parent.showHelp', (value) => {
        // When help is shown, prevent body scrolling
        if (value) {
          document.body.classList.add('overflow-hidden');
        } else {
          document.body.classList.remove('overflow-hidden');
        }
      });
    }
  }));
}); 