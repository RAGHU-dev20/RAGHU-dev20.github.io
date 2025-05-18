// ATS Checker JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const atsForm = document.getElementById('atsForm');
    const evaluateResumeBtn = document.getElementById('evaluateResumeBtn');
    const atsResults = document.getElementById('atsResults');
    const atsScore = document.getElementById('atsScore');
    const strengths = document.getElementById('strengths');
    const missingElements = document.getElementById('missingElements');
    const improvementSuggestions = document.getElementById('improvementSuggestions');
    const formattingIssues = document.getElementById('formattingIssues');
    
    if (atsForm) {
        atsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const resumeFile = document.getElementById('resumeFile').files[0];
            if (!resumeFile) {
                alert('Please select a resume file to upload');
                return;
            }
            
            // Show loading state
            const spinner = evaluateResumeBtn.querySelector('.spinner-border');
            spinner.classList.remove('d-none');
            evaluateResumeBtn.disabled = true;
            
            // Create form data
            const jobDescription = document.getElementById('jobDescription').value;
            const formData = new FormData();
            formData.append('resume', resumeFile);
            formData.append('job_description', jobDescription);
            
            // Send to API
            fetch('/api/evaluate-resume', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw response;
                }
                return response.json();
            })
            .then(data => {
                // Populate results
                atsScore.textContent = data.ats_score;
                
                // Populate strengths
                strengths.innerHTML = '';
                data.strengths.forEach(strength => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item bg-transparent';
                    li.innerHTML = `<i class="fas fa-check-circle text-success me-2"></i> ${strength}`;
                    strengths.appendChild(li);
                });
                
                // Populate missing elements
                missingElements.innerHTML = '';
                data.missing_elements.forEach(element => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item bg-transparent';
                    li.innerHTML = `<i class="fas fa-times-circle text-danger me-2"></i> ${element}`;
                    missingElements.appendChild(li);
                });
                
                // Populate improvement suggestions
                improvementSuggestions.innerHTML = '';
                data.improvement_suggestions.forEach(suggestion => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item bg-transparent';
                    li.innerHTML = `<i class="fas fa-lightbulb text-warning me-2"></i> ${suggestion}`;
                    improvementSuggestions.appendChild(li);
                });
                
                // Populate formatting issues
                formattingIssues.innerHTML = '';
                data.formatting_issues.forEach(issue => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item bg-transparent';
                    li.innerHTML = `<i class="fas fa-exclamation-circle text-warning me-2"></i> ${issue}`;
                    formattingIssues.appendChild(li);
                });
                
                // Show results
                atsResults.classList.remove('d-none');
                
                // Scroll to results
                atsResults.scrollIntoView({ behavior: 'smooth' });
                
                // Reset loading state
                spinner.classList.add('d-none');
                evaluateResumeBtn.disabled = false;
            })
            .catch(error => {
                // Reset loading state
                spinner.classList.add('d-none');
                evaluateResumeBtn.disabled = false;
                
                // Handle error
                window.handleErrors(error);
            });
        });
    }
});
