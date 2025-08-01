document.addEventListener('DOMContentLoaded', () => {
    // Set default date values
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date_from').value = '2020-01-01';
    document.getElementById('date_to').value = today;

    // Toggle advanced options visibility
    const toggleLink = document.getElementById('advanced-toggle');
    const advancedOptions = document.getElementById('advanced-options');
    toggleLink.addEventListener('click', (e) => {
        e.preventDefault();
        const isHidden = advancedOptions.style.display === 'none';
        advancedOptions.style.display = isHidden ? 'flex' : 'none';
    });
});

document.getElementById('research-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const question = document.getElementById('question').value;
    const loading = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');
    const resultsContainer = document.getElementById('results-container');
    const form = document.getElementById('research-form');
    
    form.style.display = 'none';
    resultsContainer.innerHTML = '';
    loading.style.display = 'flex';

    const loadingMessages = [
        "Generating arXiv query...",
        "Searching for relevant papers...",
        "Analyzing research findings...",
        "Synthesizing your report..."
    ];
    let messageIndex = 0;
    loadingText.textContent = loadingMessages[messageIndex];
    const textInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % loadingMessages.length;
        loadingText.textContent = loadingMessages[messageIndex];
    }, 2500);

    try {
        const formData = new FormData();
        formData.append('question', question);

        const dateFrom = document.getElementById('date_from').value;
        const dateTo = document.getElementById('date_to').value;
        if (dateFrom && dateTo) {
            formData.append('date_from', dateFrom);
            formData.append('date_to', dateTo);
        }

        const response = await fetch('/research', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            resultsContainer.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
        } else {
            marked.setOptions({
              gfm: true,
              breaks: true,
            });

            let html = marked.parse(data.answer);

            html = html.replace(/\[([\d,\s]+)\]/g, (match, innerContent) => {
                const links = innerContent.split(',')
                    .map(num => num.trim())
                    .map(num => `<a href="#source-${num}" class="citation-link">${num}</a>`)
                    .join(', ');
                return `[${links}]`;
            });

            // Apply typewriter effect to the content
            typewriterEffect(resultsContainer, html);
        }
    } catch (error) {
        resultsContainer.innerHTML = `<div class="alert alert-danger">An error occurred: ${error.message}</div>`;
    } finally {
        clearInterval(textInterval);
        loading.style.display = 'none';
        form.style.display = 'flex';
        document.getElementById('question').value = '';
    }
});

function addCitationEventListeners() {
    const citations = document.querySelectorAll('.citation-link');
    citations.forEach(citation => {
        citation.addEventListener('click', function(e) {
            e.preventDefault();
            const sourceId = this.getAttribute('href');
            const sourceElement = document.querySelector(sourceId);
            if (sourceElement) {
                sourceElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                sourceElement.classList.add('highlight');
                setTimeout(() => {
                    sourceElement.classList.remove('highlight');
                }, 2000);
            }
        });
    });
}

function addTooltips() {
    const citations = document.querySelectorAll('.citation-link');
    citations.forEach(citation => {
        const sourceId = citation.getAttribute('href'); // e.g., "#source-1"
        const sourceElement = document.querySelector(sourceId); // The <li> element
        if (sourceElement) {
            // Find the link within the <li> to get its title text
            const sourceTitle = sourceElement.querySelector('a').textContent;
            citation.setAttribute('data-tooltip', sourceTitle);
        }
    });
}

function typewriterEffect(container, html) {
    // Create a temporary div to parse the HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    
    // Clear the container
    container.innerHTML = '';
    
    let elementIndex = 0;
    const elements = Array.from(tempDiv.children);
    
    function typeNextElement() {
        if (elementIndex >= elements.length) {
            // All elements are done, add event listeners
            addCitationEventListeners();
            addTooltips();
            return;
        }
        
        const currentElement = elements[elementIndex];
        const newElement = document.createElement(currentElement.tagName);
        
        // Copy attributes
        Array.from(currentElement.attributes).forEach(attr => {
            newElement.setAttribute(attr.name, attr.value);
        });
        
        container.appendChild(newElement);
        
        // Get the text content without HTML tags for typing effect
        const textContent = currentElement.textContent;
        let charIndex = 0;
        
        // For elements with HTML content (like links), we need special handling
        if (currentElement.innerHTML !== currentElement.textContent) {
            // Element has HTML content, type it more smoothly
            newElement.innerHTML = currentElement.innerHTML;
            newElement.style.opacity = '0';
            newElement.style.animation = 'fadeInUp 0.6s ease forwards';
            elementIndex++;
            setTimeout(typeNextElement, 300);
        } else {
            // Plain text element, use character-by-character typing
            newElement.classList.add('typewriter-multiline');
            
            function typeChar() {
                if (charIndex < textContent.length) {
                    newElement.textContent = textContent.substring(0, charIndex + 1);
                    charIndex++;
                    setTimeout(typeChar, 30); // Adjust speed here (30ms per character)
                } else {
                    // Remove the blinking cursor and move to next element
                    newElement.classList.remove('typewriter-multiline');
                    elementIndex++;
                    setTimeout(typeNextElement, 200);
                }
            }
            
            typeChar();
        }
    }
    
    // Start typing the first element
    setTimeout(typeNextElement, 500);
}