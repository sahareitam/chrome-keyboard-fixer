// Initialize the extension
const initializeExtension = () => {
    console.log('Keyboard Layout Fixer extension installed');
};

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'convertText') {
        // Add request timeout handling
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Request timeout')), 10000);
        });

        // Fetch with timeout
        Promise.race([
            fetch('https://external-server-api.ew.r.appspot.com', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    text: request.text,
                    source: sender.tab ? sender.tab.url : 'extension'
                })
            }),
            timeoutPromise
        ])
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('API Error:', data.error);
                sendResponse({ error: data.error });
            } else {
                sendResponse({ convertedText: data.convertedText });
            }
        })
        .catch(error => {
            console.error('Error communicating with API:', error);
            sendResponse({
                error: error.message === 'Request timeout'
                    ? 'API request timed out'
                    : 'Failed to connect to the API'
            });
        });

        return true; // Keep message channel open for async response
    }
});

// Initialize on install
chrome.runtime.onInstalled.addListener(initializeExtension);