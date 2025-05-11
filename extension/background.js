// Global variables for request tracking
let activeRequests = 0;
const MAX_CONCURRENT_REQUESTS = 3;
const REQUEST_DELAY_MS = 500;
const API_ENDPOINT = 'https://your-api-endpoint.example.com/api/convert';
const TRANSLATION_ENDPOINT = 'https://your-api-endpoint.example.com/api/translate';

// Simple request manager
function sendRequest(text, sendResponse) {
    // Check if we can make a new request
    if (activeRequests >= MAX_CONCURRENT_REQUESTS) {
        // If not, try again after delay
        setTimeout(() => sendRequest(text, sendResponse), REQUEST_DELAY_MS);
        return;
    }

    // Increment active requests counter
    activeRequests++;

    // Send the request to the server
    fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 429) {
                throw new Error('Rate limit exceeded');
            }
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
            error: error.message === 'Rate limit exceeded'
                ? 'Too many requests, please try again later'
                : 'Failed to connect to the API'
        });
    })
    .finally(() => {
        // Decrement active requests counter
        activeRequests--;
    });
}


// New function for translation requests
function sendTranslationRequest(text, sendResponse) {
    // Check if we can make a new request
    if (activeRequests >= MAX_CONCURRENT_REQUESTS) {
        // If not, try again after delay
        setTimeout(() => sendTranslationRequest(text, sendResponse), REQUEST_DELAY_MS);
        return;
    }

    // Increment active requests counter
    activeRequests++;

    // Send the request to the server
    fetch(TRANSLATION_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 429) {
                throw new Error('Rate limit exceeded');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error('API Error:', data.error);
            sendResponse({ error: data.error });
        } else {
            sendResponse({ translatedText: data.translatedText });
        }
    })
    .catch(error => {
        console.error('Error communicating with API:', error);
        sendResponse({
            error: error.message === 'Rate limit exceeded'
                ? 'Too many requests, please try again later'
                : 'Failed to connect to the API'
        });
    })
    .finally(() => {
        // Decrement active requests counter
        activeRequests--;
    });
}

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'convertText') {
        // Process the conversion request
        sendRequest(request.text, sendResponse);
        return true; // Keep message channel open for async response
    } else if (request.action === 'translateText') {
        // Process the translation request
        sendTranslationRequest(request.text, sendResponse);
        return true; // Keep message channel open for async response
    }
});

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
    console.log('Keyboard Layout Fixer extension installed');
});