// Existing utility functions
function isEditableElement(element) {
    if (!element) return false;

    return (
        element.tagName === 'INPUT' ||
        element.tagName === 'TEXTAREA' ||
        element.isContentEditable ||
        element.getAttribute('contenteditable') === 'true' ||
        element.getAttribute('role') === 'textbox' ||
        element.getAttribute('role') === 'textinput' ||
        element.classList.contains('editable') ||
        element.getAttribute('aria-multiline') === 'true' ||
        (element.getAttribute('data-testid') &&
         element.getAttribute('data-testid').includes('edit')) ||
        element.getAttribute('contenteditable') === '' ||
        (element.getAttribute('class') &&
         element.getAttribute('class').includes('textbox'))
    );
}

// Enhanced state tracking object
const editState = {
    startPosition: null,
    lastConvertedPosition: null,
    activeElement: null,
    isTyping: false
};

// Reset edit state
function resetEditState() {
    editState.startPosition = null;
    editState.lastConvertedPosition = null;
    editState.isTyping = false;
}

// Process text through background script
function processTextThroughBackground(text) {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({ action: 'convertText', text }, response => {
            if (chrome.runtime.lastError) {
                console.error('Error communicating with background:', chrome.runtime.lastError);
                reject('Background communication error');
            } else if (response.error) {
                console.error('Error from API:', response.error);
                reject('API error');
            } else {
                resolve(response.convertedText);
            }
        });
    });
}

// Get current cursor position
function getCurrentPosition(element) {
    if (element.isContentEditable) {
        const selection = window.getSelection();
        return selection.rangeCount ? selection.getRangeAt(0).startOffset : 0;
    }
    return element.selectionStart;
}

// Replace text maintaining cursor position
function replaceText(element, newText, startPos, endPos) {
    if (element.isContentEditable) {
        const fullText = element.textContent;
        const before = fullText.substring(0, startPos);
        const after = fullText.substring(endPos);
        element.textContent = before + newText + after;

        // Set cursor position after the converted text
        const range = document.createRange();
        const sel = window.getSelection();
        const newCursorPos = before.length + newText.length;

        if (element.firstChild) {
            range.setStart(element.firstChild, newCursorPos);
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
        }

        return newCursorPos;
    } else {
        const fullText = element.value;
        const before = fullText.substring(0, startPos);
        const after = fullText.substring(endPos);
        const newValue = before + newText + after;
        element.value = newValue;

        // Set cursor position after the converted text
        const newCursorPos = before.length + newText.length;
        element.selectionStart = newCursorPos;
        element.selectionEnd = newCursorPos;

        // Trigger events
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));

        return newCursorPos;
    }
}

// Handle when user starts typing
function handleInput(e) {
    const element = e.target;
    if (!editState.isTyping) {
        editState.isTyping = true;
        editState.startPosition = getCurrentPosition(element) - 1;
    }
}

// Handle focus
function handleFocus(e) {
    const element = e.target;
    if (isEditableElement(element)) {
        editState.activeElement = element;
        // Don't reset state here to allow multiple conversions
    }
}

// Handle cursor movement
function handleCursorMove(e) {
    if (e.type === 'click' || e.key.startsWith('Arrow')) {
        resetEditState();
    }
}

// Handle keyboard shortcuts
async function handleKeydown(e) {
    const element = e.target;

    // Handle cursor movement with arrow keys
    if (e.key.startsWith('Arrow')) {
        handleCursorMove(e);
        return;
    }

    // Check for Windows/Linux (Ctrl+Shift+Z) or Mac (Command+Shift+Z)
    const isMac = navigator.platform.toLowerCase().includes('mac');
    const isShortcutTriggered = e.shiftKey && e.key.toLowerCase() === 'z' &&
        ((isMac && e.metaKey) || (!isMac && e.ctrlKey));

    if (isShortcutTriggered) {
        e.preventDefault();

        if (!isEditableElement(element)) {
            console.log('No editable element selected');
            return;
        }

        const currentPosition = getCurrentPosition(element);

        // If this is the first conversion or we're starting fresh
        if (editState.startPosition === null) {
            editState.startPosition = currentPosition;
            editState.lastConvertedPosition = currentPosition;
            console.log('Starting position set:', currentPosition);
            return;
        }

        // Get positions for conversion
        let startPos, endPos;
        if (editState.lastConvertedPosition !== null &&
            editState.lastConvertedPosition !== currentPosition) {
            // Cursor has moved after last conversion - swap positions
            startPos = editState.lastConvertedPosition;
            endPos = currentPosition;
        } else {
            // Use original positions
            startPos = editState.startPosition;
            endPos = currentPosition;
        }

        // Ensure proper order of positions
        const actualStartPos = Math.min(startPos, endPos);
        const actualEndPos = Math.max(startPos, endPos);

        let textToConvert = '';
        // Get text between positions
        if (element.isContentEditable) {
            textToConvert = element.textContent.substring(actualStartPos, actualEndPos);
        } else {
            textToConvert = element.value.substring(actualStartPos, actualEndPos);
        }

        if (!textToConvert) {
            console.log('No text to convert');
            return;
        }

        try {
            const convertedText = await processTextThroughBackground(textToConvert);
            const newCursorPos = replaceText(element, convertedText, actualStartPos, actualEndPos);

            // Store positions for next conversion
            editState.lastConvertedPosition = newCursorPos;
            // Keep original start position to maintain the text segment
            console.log('Text converted successfully. Positions updated for next conversion');
        } catch (error) {
            console.error('Error converting text:', error);
        }
    }
}

// Initialize event listeners
function initializeElementListeners(element) {
    if (isEditableElement(element)) {
        element.addEventListener('keydown', handleKeydown);
        element.addEventListener('input', handleInput);
        element.addEventListener('focus', handleFocus);
        element.addEventListener('click', handleCursorMove);
    }
}

// Set up mutation observer
const observer = new MutationObserver((mutations) => {
    mutations.forEach(mutation => {
        mutation.addedNodes.forEach(node => {
            if (node.nodeType === 1) { // ELEMENT_NODE
                initializeElementListeners(node);

                // Handle child elements
                const editableElements = node.querySelectorAll('input, textarea, [contenteditable="true"], [role="textbox"]');
                editableElements.forEach(initializeElementListeners);
            }
        });
    });
});

// Configure and start the observer
const observerConfig = {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['contenteditable', 'role']
};

observer.observe(document.body, observerConfig);

// Initialize existing elements
document.querySelectorAll('input, textarea, [contenteditable="true"], [role="textbox"]').forEach(initializeElementListeners);