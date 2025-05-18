// Resume Builder JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const resumeForm = document.getElementById('resumeForm');
    const livePreview = document.getElementById('livePreview');

    // Function to update live preview
    function updateLivePreview() {
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const phone = document.getElementById('phone').value;
        const location = document.getElementById('location').value;
        const summary = document.getElementById('summary').value;
        const education = document.getElementById('education').value;
        const experience = document.getElementById('experience').value;
        const skills = document.getElementById('skills').value;
        
        livePreview.innerHTML = `
            <div class="resume">
                <div class="resume-header">
                    <h1>${name || 'Your Name'}</h1>
                    <p>${email || 'email@example.com'} | ${phone || 'Phone'} | ${location || 'Location'}</p>
                </div>
                
                <div class="resume-section">
                    <h2>Professional Summary</h2>
                    <p>${summary || 'Your professional summary will appear here'}</p>
                </div>
                
                <div class="resume-section">
                    <h2>Education</h2>
                    <p>${education || 'Your education details will appear here'}</p>
                </div>
                
                <div class="resume-section">
                    <h2>Experience</h2>
                    <p>${experience || 'Your work experience will appear here'}</p>
                </div>
                
                <div class="resume-section">
                    <h2>Skills</h2>
                    <p>${skills || 'Your skills will appear here'}</p>
                </div>
            </div>
        `;
    }

    // Add input event listeners to all form fields
    const formInputs = resumeForm.querySelectorAll('input, textarea');
    formInputs.forEach(input => {
        input.addEventListener('input', updateLivePreview);
    });

    // Initial preview
    updateLivePreview();
    const generateResumeBtn = document.getElementById('generateResumeBtn');
    const resumeModal = new bootstrap.Modal(document.getElementById('resumeModal'));
    const resumeContent = document.getElementById('resumeContent');
    const keywordScore = document.getElementById('keywordScore');
    const improvementTips = document.getElementById('improvementTips');
    const printResumeBtn = document.getElementById('printResumeBtn');
    
    if (resumeForm) {
        resumeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate form
            if (!resumeForm.checkValidity()) {
                resumeForm.classList.add('was-validated');
                return;
            }
            
            // Show loading state
            const spinner = generateResumeBtn.querySelector('.spinner-border');
            spinner.classList.remove('d-none');
            generateResumeBtn.disabled = true;
            
            // Get form data
            const formData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                location: document.getElementById('location').value,
                summary: document.getElementById('summary').value,
                education: document.getElementById('education').value,
                experience: document.getElementById('experience').value,
                skills: document.getElementById('skills').value,
                target_position: document.getElementById('target_position').value
            };
            
            // Send to API
            fetch('/api/generate-resume', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                if (!response.ok) {
                    throw response;
                }
                return response.json();
            })
            .then(data => {
                // Populate modal with resume content
                resumeContent.innerHTML = data.html_content;
                keywordScore.textContent = data.keyword_score;
                
                // Populate improvement tips
                improvementTips.innerHTML = '';
                data.improvement_tips.forEach(tip => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item bg-transparent';
                    li.innerHTML = `<i class="fas fa-lightbulb text-warning me-2"></i> ${tip}`;
                    improvementTips.appendChild(li);
                });
                
                // Show modal
                resumeModal.show();
                
                // Reset loading state
                spinner.classList.add('d-none');
                generateResumeBtn.disabled = false;
            })
            .catch(error => {
                // Reset loading state
                spinner.classList.add('d-none');
                generateResumeBtn.disabled = false;
                
                // Handle error
                window.handleErrors(error);
            });
        });
    }
    
    // Print/Save Resume as PDF
    if (printResumeBtn) {
        printResumeBtn.addEventListener('click', function() {
            const printWindow = window.open('', '_blank');
            
            // Create a styled document for printing
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Resume - ${document.getElementById('name').value}</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            color: #000;
                            background: #fff;
                            margin: 0;
                            padding: 20px;
                        }
                        .container {
                            max-width: 800px;
                            margin: 0 auto;
                        }
                        @media print {
                            body {
                                padding: 0;
                            }
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        ${resumeContent.innerHTML}
                    </div>
                    <script>
                        window.onload = function() {
                            window.print();
                            window.onfocus = function() { window.close(); }
                        }
                    </script>
                </body>
                </html>
            `);
            
            printWindow.document.close();
        });
    }
});
