// Verify that the script is running
console.log('Content script is running!');

// Check if element is editable
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

// Get input's default text direction
function getInputDefaultDirection(element) {
    const dir = element.getAttribute('dir');
    if (dir) return dir;

    const style = window.getComputedStyle(element);
    return style.direction;
}

// Check if text contains Hebrew characters
function isHebrewText(text) {
    return /[\u0590-\u05FF]/.test(text);
}

// Send text to background script for API processing
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

// Replace text in element
function replaceText(element, newText) {
    if (element.isContentEditable || element.getAttribute('contenteditable') === 'true') {
        element.textContent = newText;

        // Position cursor at the end of text
        const range = document.createRange();
        const sel = window.getSelection();
        range.selectNodeContents(element);
        range.collapse(false);
        sel.removeAllRanges();
        sel.addRange(range);
    } else {
        element.value = newText;
        // Trigger events to update the page
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));

        // Update cursor position
        element.selectionStart = newText.length;
        element.selectionEnd = newText.length;
    }
}

// Handle keydown event
async function handleKeydown(e) {
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'z') {
        e.preventDefault();

        const activeElement = document.activeElement;
        if (!isEditableElement(activeElement)) {
            console.log('No editable element selected');
            return;
        }

        let textToConvert = '';
        let selection = window.getSelection();

        if (selection && selection.toString()) {
            textToConvert = selection.toString();
        } else if (activeElement.isContentEditable) {
            textToConvert = activeElement.textContent;
        } else if (activeElement.value) {
            textToConvert = activeElement.value;
        }

        if (!textToConvert) {
            console.log('No text to convert');
            return;
        }

        try {
            const convertedText = await processTextThroughBackground(textToConvert);
            replaceText(activeElement, convertedText);
            console.log('Text converted successfully');
        } catch (error) {
            console.error('Error converting text:', error);
        }
    }
}

// Initialize MutationObserver to detect dynamic elements
const observer = new MutationObserver((mutations) => {
    mutations.forEach(mutation => {
        // Check for added nodes
        mutation.addedNodes.forEach(node => {
            if (node.nodeType === 1) { // ELEMENT_NODE
                // Check the added element itself
                if (isEditableElement(node)) {
                    node.addEventListener('keydown', handleKeydown);
                }

                // Check child elements of the added node
                const editableElements = node.querySelectorAll('input, textarea, [contenteditable="true"], [role="textbox"]');
                editableElements.forEach(element => {
                    if (isEditableElement(element)) {
                        element.addEventListener('keydown', handleKeydown);
                    }
                });
            }
        });
    });
});

// Configure the observer
const observerConfig = {
    childList: true,    // Watch for changes in child elements
    subtree: true,      // Watch all descendants, not just direct children
    attributes: true,   // Watch for attribute changes
    attributeFilter: ['contenteditable', 'role'] // Only watch specific attributes
};

// Start observing the document body
observer.observe(document.body, observerConfig);

// Add main keyboard listener
document.addEventListener('keydown', handleKeydown);

// Setup listeners for all existing editable elements on load
document.querySelectorAll('input, textarea, [contenteditable="true"], [role="textbox"]').forEach(element => {
    if (isEditableElement(element)) {
        element.addEventListener('keydown', handleKeydown);
    }
});