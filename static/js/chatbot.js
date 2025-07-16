// Floating chatbot icon and interaction handling
function createChatbotIcon() {
    // Check if the icon already exists to avoid duplicates
    if (document.querySelector('.chatbot-icon')) {
        return;
    }
    
    const iconContainer = document.createElement('div');
    iconContainer.className = 'chatbot-icon';
    iconContainer.innerHTML = `
        <button class="chat-toggle-btn" aria-label="Open chat">
            <i class="fas fa-comments"></i>
        </button>
    `;
    document.body.appendChild(iconContainer);

    // Add click event listener
    const toggleBtn = iconContainer.querySelector('.chat-toggle-btn');
    toggleBtn.addEventListener('click', () => {
        // Clear any stored prediction ID to ensure we use the general chat
        localStorage.removeItem('selectedPredictionId');
        window.location.href = '/chatbot/';
    });

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        .chatbot-icon {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 1000;
        }

        .chat-toggle-btn {
            width: 60px;
            height: 60px;
            border-radius: 30px;
            background: var(--accent-color);
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .chat-toggle-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
        }
    `;
    document.head.appendChild(style);
}

// Function to store selected prediction ID - only used by the history page chat button
function setSelectedPrediction(predictionId) {
    localStorage.setItem('selectedPredictionId', predictionId);
}

// Initialize chatbot icon when document is loaded
document.addEventListener('DOMContentLoaded', createChatbotIcon);

// Also initialize on page changes for single-page applications
window.addEventListener('popstate', createChatbotIcon);