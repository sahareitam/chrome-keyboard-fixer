// Initialize the extension
chrome.runtime.onInstalled.addListener(() => {
    console.log('Keyboard Layout Fixer extension installed');
});

// Listen for messages from content.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'convertText') {
        // Fetch the converted text from the API
        fetch('https://external-server-api.ew.r.appspot.com', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ text: request.text })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('API Error:', data.error);
                sendResponse({ error: 'API returned an error' });
            } else {
                sendResponse({ convertedText: data.convertedText });
            }
        })
        .catch(error => {
            console.error('Error communicating with API:', error);
            sendResponse({ error: 'Failed to connect to the API' });
        });

        return true; // Keep the message channel open for asynchronous response
    }
});