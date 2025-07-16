// Handle chatbot interactions and API calls
document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendMessage');
    const chatForm = document.getElementById('chatForm');
    const closeChatBtn = document.getElementById('closeChat');
    const chatContainer = document.querySelector('.chat-container');

    // Get prediction ID from URL and determine if it's a prediction-specific chat
    const url = window.location.pathname;
    const urlParts = url.split('/').filter(Boolean);
    const isPredictionSpecific = urlParts.length > 1 && urlParts[1] !== 'query';
    const predictionId = isPredictionSpecific ? urlParts[1] : null;

    // Create loading animation element
    function createLoadingAnimation() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.innerHTML = '<div></div><div></div><div></div><div></div>';
        return loadingDiv;
    }

    // Format the response text with proper HTML
    function formatResponse(text) {
        if (!text) return '';
        
        // Replace markdown-style bold text
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Replace markdown-style italic text
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Replace markdown-style code
        text = text.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Replace line breaks with HTML line breaks
        text = text.replace(/\n/g, '<br>');
        
        // First, remove any existing bullet points from the text
        text = text.replace(/•\s*/g, '');
        text = text.replace(/-\s*/g, '');
        text = text.replace(/\*\s*/g, '');
        
        // Then add bullet points to lines that should have them
        text = text.replace(/<br>\s*([^<].*?)(?=<br>|$)/g, function(match, content) {
            // Skip if the line already has HTML tags
            if (content.trim().startsWith('<')) return match;
            return '<br><li>' + content.trim() + '</li>';
        });
        
        // Wrap bullet points in a list if they exist
        if (text.includes('<li>')) {
            text = '<ul class="suggestions-bullet-list">' + text + '</ul>';
        }
        
        // Add spacing between sections
        text = text.replace(/<br><br>/g, '</p><p>');
        
        // Wrap the entire content in a paragraph
        text = '<p>' + text + '</p>';
        
        // Add special formatting for important sections
        text = text.replace(/<strong>Important:<\/strong>/g, '<div class="important-note"><strong>Important:</strong>');
        text = text.replace(/<strong>Warning:<\/strong>/g, '<div class="warning-note"><strong>Warning:</strong>');
        text = text.replace(/<strong>Note:<\/strong>/g, '<div class="info-note"><strong>Note:</strong>');
        
        return text;
    }

    // Add welcome message based on mode
    const welcomeMessage = document.createElement('div');
    welcomeMessage.className = 'message bot-message';
    if (isPredictionSpecific) {
        welcomeMessage.innerHTML = `
            <p>Hello! I'm your personal health assistant for this specific test result. 
            I can help you understand your results and provide personalized recommendations. 
            How can I assist you today?</p>
        `;
    } else {
        welcomeMessage.innerHTML = `
            <p>Hello! I'm your general healthcare assistant. I can help answer your health-related questions 
            and provide general medical information. How can I assist you today?</p>
        `;
    }
    chatMessages.appendChild(welcomeMessage);

    // Automatically fetch suggestions when in prediction-specific mode
    if (isPredictionSpecific && predictionId) {
        const loadingMessage = document.createElement('div');
        loadingMessage.className = 'message system-message';
        loadingMessage.innerHTML = '<p>Generating health suggestions...</p>';
        loadingMessage.appendChild(createLoadingAnimation());
        chatMessages.appendChild(loadingMessage);

        fetch(`/chatbot/${predictionId}/suggestions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            chatMessages.removeChild(loadingMessage);
            if (data.success) {
                const suggestionDiv = document.createElement('div');
                suggestionDiv.className = 'message suggestion-message';
                
                // Format the suggestions with proper HTML
                const formattedSuggestions = formatResponse(data.suggestion);
                
                suggestionDiv.innerHTML = `
                    <div class="suggestion-section">
                        <h4 class="section-title">Health Suggestions</h4>
                        <div class="section-content suggestion-list">
                            ${formattedSuggestions}
                        </div>
                    </div>
                `;
                chatMessages.appendChild(suggestionDiv);
                scrollToBottom();
            } else {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'message error-message';
                errorDiv.textContent = data.error || 'Sorry, I encountered an error generating suggestions. Please try again.';
                chatMessages.appendChild(errorDiv);
            }
        })
        .catch(error => {
            chatMessages.removeChild(loadingMessage);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message error-message';
            errorDiv.textContent = 'Sorry, I encountered an error generating suggestions. Please try again.';
            chatMessages.appendChild(errorDiv);
            console.error('Error:', error);
        });
    }

    // Add event listeners for sending messages
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage();
        });
    }

    if (sendButton && userInput) {
        sendButton.addEventListener('click', function(e) {
            e.preventDefault();
            sendMessage();
        });

        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to chat
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'message user-message';
        userMessageDiv.textContent = message;
        chatMessages.appendChild(userMessageDiv);
        userInput.value = '';
        scrollToBottom();

        // Add loading message
        const loadingMessage = document.createElement('div');
        loadingMessage.className = 'message system-message';
        loadingMessage.innerHTML = '<p>Analyzing your question...</p>';
        loadingMessage.appendChild(createLoadingAnimation());
        chatMessages.appendChild(loadingMessage);
        scrollToBottom();

        // Determine the API endpoint based on mode
        const endpoint = isPredictionSpecific && predictionId ? 
            `/chatbot/${predictionId}/query/` : 
            '/chatbot/query/';

        // Send message to chatbot API
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            chatMessages.removeChild(loadingMessage);
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'message bot-message';
            
            // Format the response with proper HTML
            const formattedResponse = formatResponse(data.response);
            
            botMessageDiv.innerHTML = `<p>${formattedResponse}</p>`;
            chatMessages.appendChild(botMessageDiv);
            scrollToBottom();
        })
        .catch(error => {
            chatMessages.removeChild(loadingMessage);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message error-message';
            errorDiv.textContent = 'Sorry, I encountered an error. Please try again.';
            chatMessages.appendChild(errorDiv);
            console.error('Error:', error);
            scrollToBottom();
        });
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Handle close button click
    if (closeChatBtn) {
        closeChatBtn.addEventListener('click', function() {
            chatContainer.style.display = 'none';
        });
    }
});