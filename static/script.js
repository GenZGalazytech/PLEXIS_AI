// Store authentication token
// Store current event name for chat
let currentEventName = null;

// Check if user is authenticated on page load
window.addEventListener('DOMContentLoaded', function() {
    // Auth removed: show main content directly
    showMainContent();
    
    // Set today's date as default for event date
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('eventDate').value = today;
    
    // Show selected files
    document.getElementById('imageFiles').addEventListener('change', function(e) {
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '';
        
        if (e.target.files.length > 0) {
            fileList.innerHTML = '<strong>Selected files:</strong><br>';
            Array.from(e.target.files).forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-list-item';
                fileItem.textContent = ` ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
                fileList.appendChild(fileItem);
            });
        }
    });
});

function showAuthSection() {
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('mainContent').style.display = 'none';
}

function showMainContent() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('mainContent').style.display = 'block';
}

function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `result-message ${type}`;
    element.style.display = 'block';
    
    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

async function uploadImages() {
    const eventName = document.getElementById('eventName').value.trim();
    const eventDate = document.getElementById('eventDate').value;
    const folderName = document.getElementById('folderName').value.trim();
    const fileInput = document.getElementById('imageFiles');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadBtnText = document.getElementById('uploadBtnText');
    const uploadSpinner = document.getElementById('uploadSpinner');
    
    // Validation
    if (!eventName) {
        showMessage('uploadResult', 'Please enter an event name', 'error');
        return;
    }
    
    if (!eventDate) {
        showMessage('uploadResult', 'Please select an event date', 'error');
        return;
    }
    
    if (!fileInput.files || fileInput.files.length === 0) {
        showMessage('uploadResult', 'Please select at least one image file', 'error');
        return;
    }
    
    // Show loading state
    uploadBtn.disabled = true;
    uploadBtnText.style.display = 'none';
    uploadSpinner.style.display = 'inline-block';
    
    try {
        const formData = new FormData();
        formData.append('event_name', eventName);
        formData.append('event_date', eventDate);
        if (folderName) {
            formData.append('folderName', folderName);
        }
        
        Array.from(fileInput.files).forEach(file => {
            formData.append('files', file);
        });
        
        const response = await fetch('/upload-image', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('uploadResult', data.message || 'Images uploaded successfully!', 'success');
            // Store event name and show chat interface
            currentEventName = eventName;
            showChatInterface(eventName);
            // Reset form
            document.getElementById('eventName').value = '';
            document.getElementById('eventDate').value = new Date().toISOString().split('T')[0];
            document.getElementById('folderName').value = '';
            fileInput.value = '';
            document.getElementById('fileList').innerHTML = '';
        } else {
            showMessage('uploadResult', data.detail || 'Failed to upload images', 'error');
        }
    } catch (error) {
        showMessage('uploadResult', `Error: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtnText.style.display = 'inline';
        uploadSpinner.style.display = 'none';
    }
}

async function searchImages() {
    const eventName = document.getElementById('searchEventName').value.trim();
    const queryText = document.getElementById('searchQuery').value.trim();
    const searchBtn = document.getElementById('searchBtn');
    const searchBtnText = document.getElementById('searchBtnText');
    const searchSpinner = document.getElementById('searchSpinner');
    const resultsSection = document.getElementById('resultsSection');
    const resultsContainer = document.getElementById('resultsContainer');
    
    // Validation
    if (!eventName) {
        showMessage('searchResult', 'Please enter an event name', 'error');
        return;
    }
    
    if (!queryText) {
        showMessage('searchResult', 'Please enter a search query', 'error');
        return;
    }
    
    // Show loading state
    searchBtn.disabled = true;
    searchBtnText.style.display = 'none';
    searchSpinner.style.display = 'inline-block';
    resultsContainer.innerHTML = '';
    resultsSection.style.display = 'none';
    
    try {
        const response = await fetch('/search-images', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event_name: eventName,
                query_text: queryText
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (data.results && data.results.length > 0) {
                showMessage('searchResult', data.message || `Found ${data.results.length} results`, 'success');
                displayResults(data.results);
                resultsSection.style.display = 'block';
            } else {
                showMessage('searchResult', data.message || 'No images found matching your query', 'error');
                resultsContainer.innerHTML = `
                    <div class="no-results">
                        <div class="no-results-icon">🔍</div>
                        <p>No images found matching your search query.</p>
                        <p style="margin-top: 10px; font-size: 0.9rem; color: var(--text-secondary);">
                            Try different keywords or check the event name.
                        </p>
                    </div>
                `;
                resultsSection.style.display = 'block';
            }
        } else {
            showMessage('searchResult', data.detail || 'Failed to search images', 'error');
        }
    } catch (error) {
        showMessage('searchResult', `Error: ${error.message}`, 'error');
    } finally {
        searchBtn.disabled = false;
        searchBtnText.style.display = 'inline';
        searchSpinner.style.display = 'none';
    }
}

function displayResults(results) {
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = '';
    
    results.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        
        const similarityPercent = (result.similarity * 100).toFixed(1);
        const similarityColor = result.similarity > 0.7 ? 'var(--success-color)' : 
                               result.similarity > 0.5 ? 'var(--warning-color)' : 'var(--primary-color)';
        
        resultItem.innerHTML = `
            <img src="${result.image_url}" alt="${result.filename}" class="result-image" 
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'200\'%3E%3Crect fill=\'%23e2e8f0\' width=\'200\' height=\'200\'/%3E%3Ctext fill=\'%239ca3af\' font-family=\'sans-serif\' font-size=\'14\' x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' dy=\'.3em\'%3EImage not found%3C/text%3E%3C/svg%3E'">
            <div class="result-info">
                <div class="result-filename">${result.filename}</div>
                <span class="result-similarity" style="background: ${similarityColor}">
                    ${similarityPercent}% match
                </span>
            </div>
        `;
        
        resultsContainer.appendChild(resultItem);
    });
}

// Chat Interface Functions
function showChatInterface(eventName) {
    const chatSection = document.getElementById('chatSection');
    const chatEventName = document.getElementById('chatEventName');
    
    currentEventName = eventName;
    chatEventName.textContent = eventName;
    chatSection.style.display = 'block';
    
    // Scroll to chat
    chatSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Focus on chat input
    setTimeout(() => {
        document.getElementById('chatInput').focus();
    }, 300);
    
    // Setup example query click handlers
    setupExampleQueries();
}

function closeChat() {
    const chatSection = document.getElementById('chatSection');
    chatSection.style.display = 'none';
    currentEventName = null;
}

function setupExampleQueries() {
    const exampleQueries = document.querySelectorAll('.example-queries li');
    exampleQueries.forEach(li => {
        li.addEventListener('click', function() {
            const query = this.textContent.replace(/[""]/g, '');
            document.getElementById('chatInput').value = query;
            sendChatMessage();
        });
    });
}

async function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    const queryText = chatInput.value.trim();
    const chatSendBtn = document.getElementById('chatSendBtn');
    const chatSendBtnText = document.getElementById('chatSendBtnText');
    const chatSpinner = document.getElementById('chatSpinner');
    const chatMessages = document.getElementById('chatMessages');
    
    if (!queryText) {
        return;
    }
    
    if (!currentEventName) {
        alert('Please upload images first to start chatting!');
        return;
    }
    
    // Remove welcome message if it exists
    const welcomeMessage = chatMessages.querySelector('.chat-welcome');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    // Add user message to chat
    addChatMessage('user', queryText);
    
    // Clear input and disable button
    chatInput.value = '';
    chatSendBtn.disabled = true;
    chatSendBtnText.style.display = 'none';
    chatSpinner.style.display = 'inline-block';
    
    // Add loading message
    const loadingId = 'loading-' + Date.now();
    addChatMessage('assistant', 'Searching for images...', loadingId);
    
    try {
        const response = await fetch('/search-images', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event_name: currentEventName,
                query_text: queryText
            })
        });
        
        const data = await response.json();
        
        // Remove loading message
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) {
            loadingMsg.remove();
        }
        
        if (response.ok) {
            if (data.results && data.results.length > 0) {
                addChatMessageWithResults('assistant', 
                    `Found ${data.results.length} image${data.results.length > 1 ? 's' : ''} matching your query:`, 
                    data.results);
            } else {
                addChatMessage('assistant', 
                    `I couldn't find any images matching "${queryText}". Try different keywords or check if images were uploaded for this event.`);
            }
        } else {
            addChatMessage('assistant', `Error: ${data.detail || 'Failed to search images'}`);
        }
    } catch (error) {
        // Remove loading message
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) {
            loadingMsg.remove();
        }
        addChatMessage('assistant', `Error: ${error.message}`);
    } finally {
        chatSendBtn.disabled = false;
        chatSendBtnText.style.display = 'inline';
        chatSpinner.style.display = 'none';
        chatInput.focus();
    }
}

function addChatMessage(role, text, messageId = null) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    if (messageId) {
        messageDiv.id = messageId;
    }
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-bubble">${escapeHtml(text)}</div>
        <div class="message-time">${time}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollChatToBottom();
}

function addChatMessageWithResults(role, text, results) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    let resultsHTML = '';
    if (results && results.length > 0) {
        resultsHTML = '<div class="message-results">';
        results.forEach(result => {
            const similarityPercent = (result.similarity * 100).toFixed(1);
            resultsHTML += `
                <div class="message-result-item" onclick="window.open('${result.image_url}', '_blank')">
                    <img src="${result.image_url}" alt="${result.filename}" class="message-result-image" 
                         onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'200\'%3E%3Crect fill=\'%23e2e8f0\' width=\'200\' height=\'200\'/%3E%3Ctext fill=\'%239ca3af\' font-family=\'sans-serif\' font-size=\'14\' x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' dy=\'.3em\'%3EImage not found%3C/text%3E%3C/svg%3E'">
                    <div class="message-result-info">
                        <div class="message-result-similarity">${similarityPercent}% match</div>
                    </div>
                </div>
            `;
        });
        resultsHTML += '</div>';
    } else {
        resultsHTML = '<div class="message-no-results">No images found matching your query.</div>';
    }
    
    messageDiv.innerHTML = `
        <div class="message-bubble">${escapeHtml(text)}</div>
        ${resultsHTML}
        <div class="message-time">${time}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollChatToBottom();
}

function scrollChatToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Allow Enter key to trigger search and chat
document.addEventListener('DOMContentLoaded', function() {
    const searchQuery = document.getElementById('searchQuery');
    if (searchQuery) {
        searchQuery.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchImages();
            }
        });
    }
    
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
    
    const jwtToken = document.getElementById('jwtToken');
    if (jwtToken) {
        jwtToken.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                setAuthToken();
            }
        });
    }
});

