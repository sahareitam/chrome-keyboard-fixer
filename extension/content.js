console.log('Content script is running!');

// Check if the element is editable
function isEditableElement(element) {
    return element && (
        element.tagName === 'INPUT' ||
        element.tagName === 'TEXTAREA' ||
        element.isContentEditable
    );
}

// Send text to the background script for API processing
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

// Main keyboard listener
document.addEventListener('keydown', async function (e) {
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

            if (selection && selection.toString()) {
                document.execCommand('insertText', false, convertedText);
            } else if (activeElement.isContentEditable) {
                activeElement.textContent = convertedText;
            } else {
                activeElement.value = convertedText;
            }

            console.log('Text converted successfully');
        } catch (error) {
            console.error('Error converting text:', error);
        }
    }
});
