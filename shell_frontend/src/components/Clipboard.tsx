import { useEffect } from 'react';

const Clipboard = () => {
  useEffect(() => {
    // COPY on Selection
    const handleSelection = async () => {
      const selection = window.getSelection();
      if (selection && selection.toString().length > 0) {
        try {
          await navigator.clipboard.writeText(selection.toString());
          console.log('Copied to clipboard:', selection.toString());
        } catch (error) {
          console.error('Failed to copy to clipboard:', error);
        }
      }
    };

    // PASTE on Right-Click
    const handleRightClick = async (event: MouseEvent) => {
      event.preventDefault();
      try {
        const clipboardText = await navigator.clipboard.readText();
        const activeElement = document.activeElement as HTMLElement;

        if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {
          const input = activeElement as HTMLInputElement | HTMLTextAreaElement;
          const start = input.selectionStart ?? 0;
          const end = input.selectionEnd ?? 0;
          const newValue = input.value.slice(0, start) + clipboardText + input.value.slice(end);
          input.value = newValue;
          input.setSelectionRange(start + clipboardText.length, start + clipboardText.length);

          input.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
          console.log('No input or textarea focused to paste into.');
        }
      } catch (error) {
        console.error('Failed to read clipboard:', error);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('contextmenu', handleRightClick);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('contextmenu', handleRightClick);
    };
  }, []);

  return null; // Behavioral, no UI
};

export default Clipboard;
