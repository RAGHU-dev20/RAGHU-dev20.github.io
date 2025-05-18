// Career Assistance Test (CAT) JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const introCard = document.getElementById('introCard');
    const questionsCard = document.getElementById('questionsCard');
    const processingCard = document.getElementById('processingCard');
    const resultsPreviewCard = document.getElementById('resultsPreviewCard');
    const startCatBtn = document.getElementById('startCatBtn');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const nextBtnText = document.getElementById('nextBtnText');
    const questionsContainer = document.getElementById('questionsContainer');
    const testProgress = document.getElementById('testProgress');
    
    // Store questions and answers
    let currentQuestionSet = [];
    let allAnswers = {};
    let currentProgress = 0;
    let isLastSet = false;
    
    if (startCatBtn) {
        startCatBtn.addEventListener('click', function() {
            // Hide intro card and show questions card
            introCard.classList.add('d-none');
            questionsCard.classList.remove('d-none');
            
            // Get initial questions
            getQuestions();
        });
    }
    
    // Previous button click handler
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            // This is a simple implementation - in a real app, we would store previous questions
            // For now, just warn the user
            if (confirm('Going back will reset your current answers for this section. Continue?')) {
                getQuestions();
            }
        });
    }
    
    // Next button click handler
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            // Get current answers
            const currentAnswers = collectCurrentAnswers();
            
            // Validate answers (simple implementation)
            if (!validateAnswers(currentAnswers)) {
                alert('Please answer all questions before proceeding.');
                return;
            }
            
            // Save answers
            Object.assign(allAnswers, currentAnswers);
            
            // Show loading state
            const spinner = nextBtn.querySelector('.spinner-border');
            spinner.classList.remove('d-none');
            nextBtn.disabled = true;
            
            if (isLastSet) {
                // Process final results
                processResults();
            } else {
                // Get next questions
                getQuestions(allAnswers);
            }
        });
    }
    
    // Fetch questions from API
    function getQuestions(previousAnswers = {}) {
        // Show loading state if not already shown
        const spinner = nextBtn.querySelector('.spinner-border');
        spinner.classList.remove('d-none');
        nextBtn.disabled = true;
        
        // Convert previous answers to query string
        const queryString = previousAnswers ? `?answers=${encodeURIComponent(JSON.stringify(previousAnswers))}` : '';
        
        // Get questions from API
        fetch(`/api/cat-questions${queryString}`)
            .then(response => {
                if (!response.ok) {
                    throw response;
                }
                return response.json();
            })
            .then(data => {
                // Update progress
                currentProgress = data.progress;
                testProgress.style.width = `${currentProgress}%`;
                
                // Store current questions
                currentQuestionSet = data.questions;
                
                // Check if this is the last set
                isLastSet = currentProgress >= 90;
                
                // Update next button text
                nextBtnText.textContent = isLastSet ? 'Finish' : 'Next';
                
                // Show prev button if not first set
                if (Object.keys(previousAnswers).length > 0) {
                    prevBtn.classList.remove('d-none');
                } else {
                    prevBtn.classList.add('d-none');
                }
                
                // Render questions
                renderQuestions(currentQuestionSet);
                
                // Reset loading state
                spinner.classList.add('d-none');
                nextBtn.disabled = false;
            })
            .catch(error => {
                // Reset loading state
                spinner.classList.add('d-none');
                nextBtn.disabled = false;
                
                // Handle error
                window.handleErrors(error);
            });
    }
    
    // Render questions
    function renderQuestions(questions) {
        questionsContainer.innerHTML = '';
        
        questions.forEach(question => {
            const questionElement = document.createElement('div');
            questionElement.className = 'mb-4';
            
            switch (question.type) {
                case 'text':
                    questionElement.innerHTML = `
                        <label for="${question.id}" class="form-label">${question.question}</label>
                        <textarea class="form-control" id="${question.id}" rows="3" required></textarea>
                    `;
                    break;
                    
                case 'multiselect':
                    questionElement.innerHTML = `
                        <label class="form-label">${question.question}</label>
                        <div id="${question.id}" class="d-flex flex-wrap gap-2">
                            ${question.options.map((option, index) => `
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" value="${option}" id="${question.id}_${index}">
                                    <label class="form-check-label" for="${question.id}_${index}">${option}</label>
                                </div>
                            `).join('')}
                        </div>
                    `;
                    break;
                    
                case 'scale':
                    questionElement.innerHTML = `
                        <label class="form-label">${question.question}</label>
                        <div class="range-container">
                            <input type="range" class="form-range" min="1" max="5" id="${question.id}">
                            <div class="d-flex justify-content-between">
                                <span>1</span>
                                <span>2</span>
                                <span>3</span>
                                <span>4</span>
                                <span>5</span>
                            </div>
                        </div>
                    `;
                    break;
                    
                default:
                    questionElement.innerHTML = `
                        <label for="${question.id}" class="form-label">${question.question}</label>
                        <input type="text" class="form-control" id="${question.id}" required>
                    `;
            }
            
            questionsContainer.appendChild(questionElement);
        });
    }
    
    // Collect current answers
    function collectCurrentAnswers() {
        const answers = {};
        
        currentQuestionSet.forEach(question => {
            switch (question.type) {
                case 'multiselect':
                    const selected = [];
                    const checkboxes = document.querySelectorAll(`#${question.id} input[type="checkbox"]:checked`);
                    checkboxes.forEach(checkbox => {
                        selected.push(checkbox.value);
                    });
                    answers[question.id] = selected;
                    break;
                    
                case 'scale':
                    answers[question.id] = document.getElementById(question.id).value;
                    break;
                    
                default:
                    answers[question.id] = document.getElementById(question.id).value;
            }
        });
        
        return answers;
    }
    
    // Validate answers (simple validation)
    function validateAnswers(answers) {
        for (let question of currentQuestionSet) {
            if (question.type === 'multiselect') {
                if (!answers[question.id] || answers[question.id].length === 0) {
                    return false;
                }
            } else if (!answers[question.id] || answers[question.id].trim() === '') {
                return false;
            }
        }
        return true;
    }
    
    // Process final results
    function processResults() {
        // Hide questions card and show processing card
        questionsCard.classList.add('d-none');
        processingCard.classList.remove('d-none');
        
        // Send answers to API
        fetch('/api/cat-results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(allAnswers)
        })
        .then(response => {
            if (!response.ok) {
                throw response;
            }
            return response.json();
        })
        .then(data => {
            // Hide processing card and show results preview
            processingCard.classList.add('d-none');
            resultsPreviewCard.classList.remove('d-none');
        })
        .catch(error => {
            // Hide processing card and show questions card again
            processingCard.classList.add('d-none');
            questionsCard.classList.remove('d-none');
            
            // Reset loading state on next button
            const spinner = nextBtn.querySelector('.spinner-border');
            spinner.classList.add('d-none');
            nextBtn.disabled = false;
            
            // Handle error
            window.handleErrors(error);
        });
    }
});
