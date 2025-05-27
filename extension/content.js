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
// Add a history stack to store previous text states
const textHistory = {
    element: null,
    originalText: null,
    hasRecentConversion: false,
    timestamp: 0
};
// Add event listener for standard Ctrl+Z (undo)
document.addEventListener('keydown', handleUndoKeydown, true);

// Function to handle Ctrl+Z for undoing the conversion
function handleUndoKeydown(e) {
    // Check if it's Ctrl+Z without Shift
    if (e.ctrlKey && !e.shiftKey && e.key.toLowerCase() === 'z') {
        // Check if we have a recent conversion (within last 10 seconds)
        const now = Date.now();
        if (textHistory.hasRecentConversion &&
            textHistory.element &&
            textHistory.originalText !== null &&
            (now - textHistory.timestamp < 10000)) {

            const element = textHistory.element;

            // Only if the undo target is the currently focused element
            if (document.activeElement === element) {
                e.preventDefault(); // Prevent default undo
                e.stopPropagation(); // Stop event from bubbling

                console.log('Undoing recent conversion');

                // Restore the original text
                if (element.isContentEditable) {
                    element.textContent = textHistory.originalText;
                } else {
                    element.value = textHistory.originalText;

                    // Trigger input and change events
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                }

                // Reset the history to prevent multiple undos
                textHistory.hasRecentConversion = false;

                return false;
            }
        }
    }

    // Otherwise, let the default undo happen
    return true;
}

function positionCursorIntelligently(element, originalText, convertedText) {
    if (!convertedText || convertedText.length === 0) return;

    // Check if there was text before conversion
    const hadExistingTextBefore = originalText && originalText.length > 0;

    // Analyze the first part of the text to see if it's in Hebrew
    // We'll check the first 5 characters or less if the text is shorter
    const charsToCheck = Math.min(5, convertedText.length);
    const firstPart = convertedText.substring(0, charsToCheck);

    // Count Hebrew characters in the first part
    let hebrewCount = 0;
    for (let i = 0; i < firstPart.length; i++) {
        if (/[\u0590-\u05FF]/.test(firstPart[i])) {
            hebrewCount++;
        }
    }

    // Check if we have predominately Hebrew at the beginning
    const startsWithHebrew = hebrewCount > firstPart.length / 2;

    // Find the last non-whitespace character
    let lastNonWhitespaceIndex = convertedText.length - 1;
    while (lastNonWhitespaceIndex >= 0 && /\s/.test(convertedText[lastNonWhitespaceIndex])) {
        lastNonWhitespaceIndex--;
    }

    if (lastNonWhitespaceIndex < 0) {
        lastNonWhitespaceIndex = 0;
    }

    // Check if the last character is RTL or LTR
    const isLastCharRTL = /[\u0590-\u05FF\u0600-\u06FF]/.test(convertedText[lastNonWhitespaceIndex]);

    // Log our detection
    console.log(`Text analysis - Starts with Hebrew: ${startsWithHebrew}, Last char is RTL: ${isLastCharRTL}`);

    // Decision making:
    // 1. If the text starts with Hebrew and we had existing text, put cursor at the end
    // 2. Otherwise, decide based on the last character
    const shouldPutCursorAtEnd = startsWithHebrew || !isLastCharRTL;

    console.log(`Decision: Putting cursor at ${shouldPutCursorAtEnd ? 'end' : 'beginning'}`);

    // Set text direction based on predominant language
    const isMainlyHebrew = (startsWithHebrew || isLastCharRTL);
    const textDirection = isMainlyHebrew ? 'rtl' : 'ltr';

    // Position the cursor
    if (element.isContentEditable) {
        const range = document.createRange();
        const sel = window.getSelection();

        if (element.firstChild) {
            // Set direction
            element.style.direction = textDirection;

            if (shouldPutCursorAtEnd) {
                // Put cursor at the end
                range.setStart(element.firstChild, convertedText.length);
            } else {
                // Put cursor at the beginning
                range.setStart(element.firstChild, 0);
            }

            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
        }
    } else {
        // For input/textarea elements
        // Set direction
        element.style.direction = textDirection;
        element.style.textAlign = isMainlyHebrew ? 'right' : 'left';

        if (shouldPutCursorAtEnd) {
            // Put cursor at the end
            element.selectionStart = convertedText.length;
            element.selectionEnd = convertedText.length;
        } else {
            // Put cursor at the beginning
            element.selectionStart = 0;
            element.selectionEnd = 0;
        }
    }
}
// Enhanced state tracking object
const editState = {
    activeElement: null
};



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
// Process text through translation API
function processTextThroughTranslation(text) {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({ action: 'translateText', text }, response => {
            if (chrome.runtime.lastError) {
                console.error('Error communicating with background:', chrome.runtime.lastError);
                reject('Background communication error');
            } else if (response.error) {
                console.error('Error from API:', response.error);
                reject('API error');
            } else {
                resolve(response.translatedText);
            }
        });
    });
}

// Process text through rephrasing API
function processTextThroughRephrasing(text) {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({ action: 'rephraseToPrompt', text }, response => {
            if (chrome.runtime.lastError) {
                console.error('Error communicating with background:', chrome.runtime.lastError);
                reject('Background communication error');
            } else if (response.error) {
                console.error('Error from API:', response.error);
                reject('API error');
            } else {
                resolve(response.rephrasedText);
            }
        });
    });
}

// Handle focus
function handleFocus(e) {
    const element = e.target;
    if (isEditableElement(element)) {
        editState.activeElement = element;
    }
}

async function handleKeydown(e) {
    const element = e.target;

    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'z') {
        e.preventDefault();

        if (!isEditableElement(element)) {
            console.log('No editable element selected');
            return;
        }

        let textToConvert = '';

        // Get all text from the element
        if (element.isContentEditable) {
            textToConvert = element.textContent;
        } else {
            textToConvert = element.value;
        }

        if (!textToConvert) {
            console.log('No text to convert');
            return;
        }

        console.log('Sending full text for conversion:', textToConvert);

        try {
            // Store original text in history before conversion
            textHistory.element = element;
            textHistory.originalText = textToConvert;
            textHistory.hasRecentConversion = true;
            textHistory.timestamp = Date.now();

            // Convert the text
            const convertedText = await processTextThroughBackground(textToConvert);

            // Replace all text in the element
            if (element.isContentEditable) {
                element.textContent = convertedText;
            } else {
                element.value = convertedText;

                // Trigger input and change events
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }

            // Intelligently position cursor
            positionCursorIntelligently(element, originalText, convertedText);

            console.log('Full text converted successfully');
        } catch (error) {
            console.error('Error converting text:', error);
        }
    }
    // Handle Ctrl+Alt+X for translation
     if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'x') {
        e.preventDefault();

        if (!isEditableElement(element)) {
            console.log('No editable element selected');
            return;
        }

        let textToTranslate = '';

        // Get all text from the element
        if (element.isContentEditable) {
            textToTranslate = element.textContent;
        } else {
            textToTranslate = element.value;
        }

        if (!textToTranslate) {
            console.log('No text to translate');
            return;
        }

        console.log('Sending text for translation:', textToTranslate);

        try {
            // Store original text in history before translation
            textHistory.element = element;
            textHistory.originalText = textToTranslate;
            textHistory.hasRecentConversion = true;
            textHistory.timestamp = Date.now();

            // Translate the text
            const translatedText = await processTextThroughTranslation(textToTranslate);

            // Replace all text in the element
            if (element.isContentEditable) {
                element.textContent = translatedText;
            } else {
                element.value = translatedText;

                // Trigger input and change events
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }

            // Intelligently position cursor
            positionCursorIntelligently(element, textToTranslate, translatedText);

            console.log('Text translated successfully');
        } catch (error) {
            console.error('Error translating text:', error);
        }
    }
    // Handle Ctrl+Shift+y (rephrase to prompt)
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'h') {
        e.preventDefault();

        if (!isEditableElement(element)) {
            console.log('No editable element selected');
            return;
        }

        let textToRephrase = '';

        // Get all text from the element
        if (element.isContentEditable) {
            textToRephrase = element.textContent;
        } else {
            textToRephrase = element.value;
        }

        if (!textToRephrase) {
            console.log('No text to rephrase');
            return;
        }

        console.log('Sending text for rephrasing to prompt:', textToRephrase);

        try {
            // Store original text in history
            textHistory.element = element;
            textHistory.originalText = textToRephrase;
            textHistory.hasRecentConversion = true;
            textHistory.timestamp = Date.now();

            // Rephrase the text
            const rephrasedText = await processTextThroughRephrasing(textToRephrase);

            // Replace all text in the element
            if (element.isContentEditable) {
                element.textContent = rephrasedText;
            } else {
                element.value = rephrasedText;

                // Trigger input and change events
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }

            // Position cursor at the end of the new text
            if (element.isContentEditable) {
                const range = document.createRange();
                const sel = window.getSelection();
                if (element.firstChild) {
                    range.setStart(element.firstChild, rephrasedText.length);
                    range.collapse(true);
                    sel.removeAllRanges();
                    sel.addRange(range);
                }
            } else {
                element.selectionStart = rephrasedText.length;
                element.selectionEnd = rephrasedText.length;
            }

            console.log('Text rephrased to prompt successfully');
        } catch (error) {
            console.error('Error rephrasing text:', error);
        }
    }
}

// Initialize event listeners
function initializeElementListeners(element) {
    if (isEditableElement(element)) {
        element.addEventListener('keydown', handleKeydown);
        element.addEventListener('focus', handleFocus);
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