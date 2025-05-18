// Main JavaScript file for CareerCraft AI

document.addEventListener('DOMContentLoaded', function() {
    // Career Roadmap Handler
    const roadmapButton = document.getElementById('generateRoadmap');
    if (roadmapButton) {
        roadmapButton.addEventListener('click', async () => {
            const form = document.getElementById('roadmapForm');
            const resultDiv = document.getElementById('roadmapResult');
            const careerPath = form.querySelector('select[name="career_path"]').value;

            if (!careerPath) {
                showErrorAlert('Please select a career path');
                return;
            }

            try {
                roadmapButton.disabled = true;
                resultDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p class="mt-2">Generating roadmap...</p></div>';
                resultDiv.classList.remove('d-none');

                const formData = new FormData(form);
                const careerPath = formData.get('career_path');

                if (!careerPath) {
                    throw new Error('Please select a career path');
                }

                const response = await fetch('/api/career-roadmap', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ career_path: careerPath })
                });

                if (!response.ok) {
                    throw new Error('Failed to generate roadmap');
                }

                const result = await response.json();
                resultDiv.innerHTML = `
                    <div class="roadmap-timeline">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5>Entry Level: ${result.entry_level.title}</h5>
                                <p><strong>Skills:</strong> ${result.entry_level.skills.join(', ')}</p>
                                <p><strong>Timeframe:</strong> ${result.entry_level.timeframe}</p>
                                <ul>
                                    ${result.entry_level.milestones.map(m => `<li>${m}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5>Mid Level: ${result.mid_level.title}</h5>
                                <p><strong>Skills:</strong> ${result.mid_level.skills.join(', ')}</p>
                                <p><strong>Timeframe:</strong> ${result.mid_level.timeframe}</p>
                                <ul>
                                    ${result.mid_level.milestones.map(m => `<li>${m}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-body">
                                <h5>Senior Level: ${result.senior_level.title}</h5>
                                <p><strong>Skills:</strong> ${result.senior_level.skills.join(', ')}</p>
                                <p><strong>Timeframe:</strong> ${result.senior_level.timeframe}</p>
                                <ul>
                                    ${result.senior_level.milestones.map(m => `<li>${m}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                `;
            } catch (error) {
                const errorMessage = error.message || 'Failed to generate roadmap. Please try again.';
                resultDiv.innerHTML = `<div class="alert alert-danger">${errorMessage}</div>`;
                console.error('Roadmap generation error:', error);
            } finally {
                roadmapButton.disabled = false;
            }
        });
    }

    // Interview Questions Handler
    const questionsButton = document.getElementById('generateQuestions');
    if (questionsButton) {
        questionsButton.addEventListener('click', async () => {
            const form = document.getElementById('interviewForm');
            const resultDiv = document.getElementById('interviewResult');
            const domain = form.querySelector('select[name="domain"]').value;
            const numQuestions = form.querySelector('input[name="num_questions"]').value;

            if (!domain) {
                showErrorAlert('Please select a domain');
                return;
            }

            try {
                questionsButton.disabled = true;
                resultDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p class="mt-2">Generating questions...</p></div>';
                resultDiv.classList.remove('d-none');
                const response = await fetch('/api/interview-questions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ domain, num_questions: numQuestions })
                });

                if (!response.ok) {
                    throw new Error('Failed to generate questions');
                }

                const result = await response.json();
                resultDiv.innerHTML = `
                    <div class="accordion" id="questionsAccordion">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Technical Questions</h5>
                            </div>
                            <div class="card-body">
                                ${result.technical_questions.map((q, i) => `
                                    <div class="mb-3">
                                        <p class="fw-bold">${i + 1}. ${q.question}</p>
                                        <p class="text-muted"><small>Ideal Answer: ${q.ideal_answer}</small></p>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        <div class="card mt-3">
                            <div class="card-header">
                                <h5 class="mb-0">Behavioral Questions</h5>
                            </div>
                            <div class="card-body">
                                ${result.behavioral_questions.map((q, i) => `
                                    <div class="mb-3">
                                        <p class="fw-bold">${i + 1}. ${q.question}</p>
                                        <p class="text-muted"><small>Tips: ${q.tips}</small></p>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `;
                resultDiv.classList.remove('d-none');
            } catch (error) {
                console.error('Error generating questions:', error);
                resultDiv.innerHTML = '<div class="alert alert-danger">Failed to generate questions. Please try again.</div>';
                resultDiv.classList.remove('d-none');
            } finally {
                questionsButton.disabled = false;
            }
        });
    }

    // Profile Import Handler
    const importButton = document.getElementById('importProfile');
    if (importButton) {
        importButton.addEventListener('click', async () => {
            const form = document.getElementById('importForm');
            const resultDiv = document.getElementById('importResult');
            const platform = form.querySelector('select[name="platform"]').value;
            const profileUrl = form.querySelector('input[name="profile_url"]').value;

            if (!platform || !profileUrl) {
                showErrorAlert('Please fill in all fields');
                return;
            }

            try {
                importButton.disabled = true;
                const response = await fetch('/api/import-profile', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ platform, profile_url: profileUrl })
                });

                if (!response.ok) {
                    throw new Error('Failed to import profile');
                }

                const result = await response.json();
                if (result.success && result.profile) {
                    resultDiv.innerHTML = `
                        <div class="card">
                            <div class="card-body">
                                <div class="d-flex align-items-center mb-3">
                                    <img src="${result.profile.avatar_url}" class="rounded-circle me-3" width="64" height="64">
                                    <div>
                                        <h5 class="card-title mb-1">${result.profile.name || 'N/A'}</h5>
                                        <p class="card-text text-muted mb-0">${result.profile.bio || 'No bio available'}</p>
                                    </div>
                                </div>
                                <div class="row mt-3">
                                    <div class="col-4">
                                        <div class="text-center">
                                            <h6>${result.profile.public_repos}</h6>
                                            <small class="text-muted">Repositories</small>
                                        </div>
                                    </div>
                                    <div class="col-4">
                                        <div class="text-center">
                                            <h6>${result.profile.followers}</h6>
                                            <small class="text-muted">Followers</small>
                                        </div>
                                    </div>
                                    <div class="col-4">
                                        <div class="text-center">
                                            <h6>${result.profile.following}</h6>
                                            <small class="text-muted">Following</small>
                                        </div>
                                    </div>
                                </div>
                                <p class="mt-3 mb-0"><i class="fas fa-map-marker-alt me-2"></i>${result.profile.location || 'Location not specified'}</p>
                            </div>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            ${result.error || 'Failed to import profile'}
                        </div>
                    `;
                }
                resultDiv.classList.remove('d-none');

                // Reset form
                form.reset();
            } catch (error) {
                showErrorAlert('Failed to import profile. Please check the URL and try again.');
            } finally {
                importButton.disabled = false;
            }
        });
    }

    // Helper function to show error alerts
    function showErrorAlert(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        const container = document.querySelector('.modal.show .modal-body') || document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            setTimeout(() => alertDiv.remove(), 5000);
        }
    }
});