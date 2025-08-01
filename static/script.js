document.getElementById('research-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const question = document.getElementById('question').value;
    const loading = document.getElementById('loading');
    const resultsContainer = document.getElementById('results-container');

    loading.style.display = 'block';
    resultsContainer.innerHTML = '';

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
            // Configure marked to open links in a new tab
            marked.use({ renderer: new marked.Renderer() });
            marked.setOptions({
              renderer: new marked.Renderer(),
              gfm: true,
              breaks: true,
            });

            let html = marked.parse(data.answer);

            // Dynamically create citation links
            //html = html.replace(/\[(\d+)\]/g, '<a href="#source-$1" class="citation-link">[$1]</a>');
            html = html.replace(/\[([\d,\s]+)\]/g, (match, innerContent) => {
                const links = innerContent.split(',')
                    .map(num => num.trim())
                    .map(num => `<a href="#source-${num}" class="citation-link">${num}</a>`)
                    .join(', ');
                return `[${links}]`;
            });

            resultsContainer.innerHTML = html;
            addCitationEventListeners();
        }
    } catch (error) {
        resultsContainer.innerHTML = `<div class="alert alert-danger">An error occurred: ${error.message}</div>`;
    } finally {
        loading.style.display = 'none';
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
