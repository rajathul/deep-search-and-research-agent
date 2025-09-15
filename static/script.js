document.addEventListener('DOMContentLoaded', () => {
    // Initialize scientific animations
    initScientificAnimations();
    
    // Add typing effect to search input
    initSearchEffects();
    
    // Initialize custom number input
    initNumberInput();

    // Set default date values
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date_from').value = '2020-01-01';
    document.getElementById('date_to').value = today;

    console.log('Multi-Agent Research System initialized');

    // Initialize timer system
    initResearchTimer();

    // Initialize deep research toggle
    initDeepResearchToggle();
    
    // Initialize model selection
    initModelSelection();

    // Toggle advanced options visibility
    const toggleLink = document.getElementById('advanced-toggle');
    const advancedOptions = document.getElementById('advanced-options');
    toggleLink.addEventListener('click', (e) => {
        e.preventDefault();
        const isHidden = advancedOptions.style.display === 'none';
        advancedOptions.style.display = isHidden ? 'flex' : 'none';
    });
});

function initDeepResearchToggle() {
    const toggle = document.getElementById('deep-research-toggle');
    const modeDescription = document.getElementById('mode-description');
    
    toggle.addEventListener('change', function() {
        if (this.checked) {
            modeDescription.textContent = 'Comprehensive multi-step research with question decomposition';
            console.log('Deep Research mode enabled');
        } else {
            modeDescription.textContent = 'Quick intelligent search across sources';
            console.log('Deep Search mode enabled');
        }
    });
}

function initModelSelection() {
    const modelSelect = document.getElementById('model-select');
    
    modelSelect.addEventListener('change', function() {
        const selectedModel = this.value;
        console.log('Model changed to:', selectedModel);
        
        // Update visual feedback based on model type
        const modelSelection = document.querySelector('.model-selection');
        modelSelection.classList.remove('gemini-model', 'ollama-model');
        
        if (selectedModel.includes('gemini')) {
            modelSelection.classList.add('gemini-model');
        } else {
            modelSelection.classList.add('ollama-model');
        }
    });
    
    // Set initial state
    const initialModel = modelSelect.value;
    if (initialModel.includes('gemini')) {
        document.querySelector('.model-selection').classList.add('gemini-model');
    } else {
        document.querySelector('.model-selection').classList.add('ollama-model');
    }
}

document.getElementById('research-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const question = document.getElementById('question').value;
    const loading = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');
    const resultsContainer = document.getElementById('results-container');
    const form = document.getElementById('research-form');
    const isDeepResearch = document.getElementById('deep-research-toggle').checked;
    const selectedModel = document.getElementById('model-select').value;

    console.log('=== RESEARCH SUBMISSION ===');
    console.log('Question:', question);
    console.log('Mode:', isDeepResearch ? 'Deep Research' : 'Deep Search');
    console.log('Model:', selectedModel);
    console.log('====================================');
    
    form.style.display = 'none';
    resultsContainer.innerHTML = '';
    loading.style.display = 'flex';
    
    // Start the research timer
    resetResearchTimer();
    startResearchTimer();

    // Different loading messages based on research mode
    let loadingMessages;
    if (isDeepResearch) {
        loadingMessages = [
            "Breaking down your question into sub-questions...",
            "Analyzing research strategy for each component...",
            "Searching academic papers and videos...",
            "Processing transcripts and abstracts...",
            "Synthesizing comprehensive deep research report..."
        ];
    } else {
        loadingMessages = [
            "Analyzing your question...",
            "AI selecting optimal research strategy...",
            "Searching across academic papers...",
            "Scanning video content...",
            "Processing transcripts and abstracts...",
            "Synthesizing comprehensive report..."
        ];
    }
    
    let messageIndex = 0;
    loadingText.textContent = loadingMessages[messageIndex];
    const textInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % loadingMessages.length;
        loadingText.textContent = loadingMessages[messageIndex];
    }, 3000); // Slightly longer for deep research messages

    try {
        const formData = new FormData();
        formData.append('question', question);
        formData.append('research_mode', isDeepResearch ? 'deep_research' : 'deep_search');
        formData.append('model', selectedModel);

        // Add webpage URL field
        const webpageUrl = document.getElementById('webpage_url').value;
        formData.append('webpage_url', webpageUrl);
        console.log('JavaScript: Webpage URL being sent:', webpageUrl); // Debug log

        const dateFrom = document.getElementById('date_from').value;
        const dateTo = document.getElementById('date_to').value;
        if (dateFrom && dateTo) {
            formData.append('date_from', dateFrom);
            formData.append('date_to', dateTo);
        }

        const maxSources = document.getElementById('max_sources').value;
        formData.append('max_sources', maxSources);

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

            // Handle the response structure
            let html = '';
            if (data.answer && data.answer.result) {
                // The planner returns {result: "synthesized report", strategy: {...}, agent: "Planner Agent"}
                html = marked.parse(data.answer.result);
                
                // Add strategy information for both modes
                if (data.answer.strategy) {
                    const strategy = data.answer.strategy;
                    let strategyInfo = `
                        <div class="strategy-info" style="background: rgba(74, 20, 140, 0.2); padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #6a1b9a;">
                            <h4><i class="fas fa-brain"></i> AI Research Strategy</h4>
                            <p><strong>Mode:</strong> ${isDeepResearch ? 'Deep Research' : 'Deep Search'}</p>
                            <p><strong>Model:</strong> ${selectedModel}</p>
                            <p><strong>Reasoning:</strong> ${strategy.reasoning}</p>
                            <p><strong>Sources Used:</strong> ${strategy.use_arxiv ? 'ArXiv' : ''} ${strategy.use_arxiv && strategy.use_youtube ? '+ ' : ''}${strategy.use_youtube ? 'YouTube' : ''}</p>`;
                    
                    // Add decomposition info for deep research
                    if (isDeepResearch && data.answer.sub_questions) {
                        strategyInfo += `<p><strong>Sub-questions researched:</strong> ${data.answer.sub_questions.length} components</p>`;
                        strategyInfo += `<details style="margin-top: 0.5rem;"><summary style="cursor: pointer; font-weight: 500;">View Research Components</summary>`;
                        strategyInfo += `<ul style="margin-top: 0.5rem; padding-left: 1.5rem;">`;
                        data.answer.sub_questions.forEach((sq, idx) => {
                            strategyInfo += `<li style="margin-bottom: 0.25rem;">${sq}</li>`;
                        });
                        strategyInfo += `</ul></details>`;
                    }
                    
                    strategyInfo += `</div>`;
                    html = strategyInfo + html;
                }
            } else if (typeof data.answer === 'string') {
                // Fallback for direct string response
                html = marked.parse(data.answer);
            } else {
                html = '<div class="alert alert-warning">No results found</div>';
            }

            // Process citations
            html = html.replace(/\[([\d,\s]+)\]/g, (match, innerContent) => {
                const links = innerContent.split(',')
                    .map(num => num.trim())
                    .map(num => `<a href="#source-${num}" class="citation-link">${num}</a>`)
                    .join(', ');
                return `[${links}]`;
            });

            typewriterEffect(resultsContainer, html);
        }
    } catch (error) {
        resultsContainer.innerHTML = `<div class="alert alert-danger">An error occurred: ${error.message}</div>`;
    } finally {
        clearInterval(textInterval);
        
        // Stop the timer and get completion time
        const completionTime = stopResearchTimer();
        
        loading.style.display = 'none';
        form.style.display = 'flex';
        
        // Add completion time to results if research was successful
        if (completionTime && resultsContainer.innerHTML && !resultsContainer.innerHTML.includes('alert-danger')) {
            const completionBadge = `
                <div class="completion-time-badge" style="
                    background: linear-gradient(135deg, #4caf50, #45a049);
                    color: white;
                    padding: 0.8rem 1.5rem;
                    border-radius: 12px;
                    margin-bottom: 1.5rem;
                    text-align: center;
                    font-family: 'Poppins', sans-serif;
                    font-weight: 600;
                    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
                    animation: completion-glow 2s ease-in-out;
                ">
                    <i class="fas fa-clock" style="margin-right: 0.5rem;"></i>
                    Research completed in ${completionTime.formatted}
                </div>
            `;
            resultsContainer.insertAdjacentHTML('afterbegin', completionBadge);
        }
        
        // Don't clear the question to allow for follow-up searches
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

// Scientific Animations
function initScientificAnimations() {
    createFloatingParticles();
    createDNAHelix();
    addMouseTrackingEffect();
}

function initSearchEffects() {
    const questionInput = document.getElementById('question');
    const researchForm = document.getElementById('research-form');
    
    questionInput.addEventListener('input', () => {
        if (questionInput.value.length > 0) {
            researchForm.style.boxShadow = '0 0 20px rgba(186, 104, 200, 0.5)';
            researchForm.style.transform = 'scale(1.02)';
        } else {
            researchForm.style.boxShadow = 'none';
            researchForm.style.transform = 'scale(1)';
        }
    });
    
    questionInput.addEventListener('focus', () => {
        researchForm.style.transition = 'all 0.3s ease';
    });
    
    questionInput.addEventListener('blur', () => {
        if (questionInput.value.length === 0) {
            researchForm.style.boxShadow = 'none';
            researchForm.style.transform = 'scale(1)';
        }
    });
}

function initNumberInput() {
    const numberInput = document.getElementById('max_sources');
    const upBtn = document.querySelector('.number-up');
    const downBtn = document.querySelector('.number-down');
    
    const min = parseInt(numberInput.getAttribute('min'));
    const max = parseInt(numberInput.getAttribute('max'));
    
    function updateValue(newValue) {
        if (newValue >= min && newValue <= max) {
            numberInput.value = newValue;
            
            // Add a subtle animation effect
            numberInput.style.transform = 'scale(1.05)';
            setTimeout(() => {
                numberInput.style.transform = 'scale(1)';
            }, 150);
        }
    }
    
    upBtn.addEventListener('click', () => {
        const currentValue = parseInt(numberInput.value);
        updateValue(currentValue + 1);
    });
    
    downBtn.addEventListener('click', () => {
        const currentValue = parseInt(numberInput.value);
        updateValue(currentValue - 1);
    });
    
    // Add keyboard support
    numberInput.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            const currentValue = parseInt(numberInput.value);
            updateValue(currentValue + 1);
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            const currentValue = parseInt(numberInput.value);
            updateValue(currentValue - 1);
        }
    });
    
    // Add smooth transition for the input
    numberInput.style.transition = 'transform 0.15s ease';
}

function createFloatingParticles() {
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'particles';
    document.body.appendChild(particlesContainer);

    // Create 20 particles
    for (let i = 0; i < 20; i++) {
        setTimeout(() => {
            createParticle(particlesContainer);
        }, i * 800); // Stagger particle creation
    }

    // Continue creating particles every 3 seconds
    setInterval(() => {
        createParticle(particlesContainer);
    }, 3000);
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    // Random size between 2-6px
    const size = Math.random() * 4 + 2;
    particle.style.width = size + 'px';
    particle.style.height = size + 'px';
    
    // Random horizontal position
    particle.style.left = Math.random() * 100 + '%';
    
    // Random animation duration between 15-30s
    const duration = Math.random() * 15 + 15;
    particle.style.animationDuration = duration + 's';
    
    container.appendChild(particle);
    
    // Remove particle after animation completes
    setTimeout(() => {
        if (particle.parentNode) {
            particle.parentNode.removeChild(particle);
        }
    }, duration * 1000);
}

function createDNAHelix() {
    const dnaHelix = document.createElement('div');
    dnaHelix.className = 'dna-helix';
    
    // Create two DNA strands
    for (let i = 0; i < 2; i++) {
        const strand = document.createElement('div');
        strand.className = 'dna-strand';
        dnaHelix.appendChild(strand);
    }
    
    // Create DNA base pairs
    for (let i = 0; i < 20; i++) {
        const base = document.createElement('div');
        base.className = 'dna-base';
        base.style.top = (i * 20) + 'px';
        base.style.animationDelay = (i * 0.1) + 's';
        dnaHelix.appendChild(base);
    }
    
    document.body.appendChild(dnaHelix);
}

function addMouseTrackingEffect() {
    const card = document.querySelector('.card');
    
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const deltaX = (x - centerX) / centerX;
        const deltaY = (y - centerY) / centerY;
        
        // Much more subtle rotation - reduced from 5 to 1.5
        const rotateX = deltaY * 1.5;
        const rotateY = deltaX * 1.5;
        
        card.style.transform = `perspective(2000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(2px)`;
        card.style.transition = 'transform 0.1s ease-out';
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(2000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
        card.style.transition = 'transform 0.3s ease-out';
    });
}

// Simple Research Timer Management
let simpleTimer = {
    startTime: null,
    interval: null,
    isRunning: false
};

function initResearchTimer() {
    // Simple timer initialization
    const timerDisplay = document.getElementById('simple-timer-display');
    if (timerDisplay) {
        timerDisplay.textContent = '00:00';
    }
}

function startResearchTimer() {
    if (simpleTimer.isRunning) return;
    
    simpleTimer.startTime = Date.now();
    simpleTimer.isRunning = true;
    
    const timerDisplay = document.getElementById('simple-timer-display');
    const timerContainer = document.querySelector('.simple-timer');
    
    // Remove completed state if present
    if (timerContainer) {
        timerContainer.classList.remove('completed');
    }
    
    simpleTimer.interval = setInterval(() => {
        const elapsed = Date.now() - simpleTimer.startTime;
        const totalSeconds = Math.floor(elapsed / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        
        if (timerDisplay) {
            timerDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }
    }, 1000);
}

function stopResearchTimer() {
    if (!simpleTimer.isRunning) return;
    
    clearInterval(simpleTimer.interval);
    simpleTimer.isRunning = false;
    
    // Calculate final time
    const elapsed = Date.now() - simpleTimer.startTime;
    const totalSeconds = Math.floor(elapsed / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    
    // Add completion styling
    const timerContainer = document.querySelector('.simple-timer');
    if (timerContainer) {
        timerContainer.classList.add('completed');
    }
    
    // Return the formatted time
    return {
        elapsed: elapsed,
        formatted: `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`,
        totalSeconds: totalSeconds
    };
}

function resetResearchTimer() {
    if (simpleTimer.interval) {
        clearInterval(simpleTimer.interval);
    }
    
    simpleTimer.isRunning = false;
    const timerDisplay = document.getElementById('simple-timer-display');
    const timerContainer = document.querySelector('.simple-timer');
    
    if (timerDisplay) {
        timerDisplay.textContent = '00:00';
    }
    
    if (timerContainer) {
        timerContainer.classList.remove('completed');
    }
}