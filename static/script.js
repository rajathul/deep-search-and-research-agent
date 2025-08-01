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

            resultsContainer.innerHTML = html;
            addCitationEventListeners();
            addTooltips(); // <--- ADD THIS FUNCTION CALL
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
    // ... (This function remains unchanged)
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

/**
 * NEW FUNCTION: Finds each citation, gets the corresponding source title,
 * and adds it as a data-attribute for the CSS tooltip.
 */
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