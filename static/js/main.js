document.addEventListener('DOMContentLoaded', function() {
    // Initialize all show more/less toggles
    initShowMoreToggles();
    
    // Initialize filter form submission
    initFilterForm();
    
    // Initialize shortlist buttons
    initShortlistButtons();
    
    // Initialize search suggestions
    initSearchSuggestions();
    
    // Initialize summarize functionality
    initSummarizeButtons();
});

/**
 * Initialize show more/less toggles for filter sections
 */
function initShowMoreToggles() {
    const showMoreBtns = document.querySelectorAll('.show-more-btn');
    
    showMoreBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const showText = this.querySelector('.show-text');
            const hideText = this.querySelector('.hide-text');
            const showIcon = this.querySelector('.show-icon');
            const hideIcon = this.querySelector('.hide-icon');
            
            showText.classList.toggle('d-none');
            hideText.classList.toggle('d-none');
            showIcon.classList.toggle('d-none');
            hideIcon.classList.toggle('d-none');
        });
    });
}

/**
 * Initialize filter form for auto-submission on change
 */
function initFilterForm() {
    const filterCheckboxes = document.querySelectorAll('.filter-checkbox');
    
    filterCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // Submit the form when a filter is changed
            // document.getElementById('filter-form').submit();
            
            // Uncommenting the above line would submit the form immediately on change.
            // For better UX, we're keeping the "Apply Filters" button instead.
        });
    });
}

/**
 * Initialize shortlist buttons to toggle candidate shortlisting
 */
function initShortlistButtons() {
    const shortlistBtns = document.querySelectorAll('.shortlist-btn');
    const shortlistActions = document.querySelectorAll('.shortlist-action');
    
    // Initialize shortlist buttons
    shortlistBtns.forEach(btn => {
        const candidateId = btn.getAttribute('data-candidate-id');
        
        // Check if candidate is already shortlisted
        fetch(`/api/check-shortlist/${candidateId}`)
            .then(response => response.json())
            .then(data => {
                if (data.shortlisted) {
                    btn.classList.add('text-primary');
                    btn.querySelector('i').classList.remove('far');
                    btn.querySelector('i').classList.add('fas');
                }
            });
        
        // Add click event to toggle shortlist status
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleShortlist(candidateId, btn);
        });
    });
    
    // Initialize shortlist dropdown actions
    shortlistActions.forEach(action => {
        const candidateId = action.getAttribute('data-candidate-id');
        
        // Check if candidate is already shortlisted
        fetch(`/api/check-shortlist/${candidateId}`)
            .then(response => response.json())
            .then(data => {
                if (data.shortlisted) {
                    action.textContent = 'Remove from shortlist';
                }
            });
        
        // Add click event to toggle shortlist status
        action.addEventListener('click', function(e) {
            e.preventDefault();
            const btn = document.querySelector(`.shortlist-btn[data-candidate-id="${candidateId}"]`);
            toggleShortlist(candidateId, btn);
            
            // Update dropdown text
            if (this.textContent === 'Add to shortlist') {
                this.textContent = 'Remove from shortlist';
            } else {
                this.textContent = 'Add to shortlist';
            }
        });
    });
}

/**
 * Toggle shortlist status for a candidate
 */
function toggleShortlist(candidateId, btn) {
    fetch('/api/shortlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ candidate_id: candidateId }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'added') {
                // Mark as shortlisted
                btn.classList.add('text-primary');
                btn.querySelector('i').classList.remove('far');
                btn.querySelector('i').classList.add('fas');
            } else {
                // Mark as not shortlisted
                btn.classList.remove('text-primary');
                btn.querySelector('i').classList.remove('fas');
                btn.querySelector('i').classList.add('far');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

/**
 * Initialize search suggestions functionality
 */
function initSearchSuggestions() {
    const searchInput = document.getElementById('search-input');
    const suggestionsContainer = document.getElementById('search-suggestions');
    
    if (!searchInput || !suggestionsContainer) return;
    
    let debounceTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimeout);
        
        const query = this.value.trim();
        
        if (query.length < 2) {
            suggestionsContainer.style.display = 'none';
            return;
        }
        
        debounceTimeout = setTimeout(() => {
            fetch(`/api/search-suggestions?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsContainer.innerHTML = '';
                    
                    if (data.length === 0) {
                        suggestionsContainer.style.display = 'none';
                        return;
                    }
                    
                    data.forEach(suggestion => {
                        const item = document.createElement('div');
                        item.className = 'suggestion-item';
                        
                        const icon = suggestion.type === 'candidate' ? 'user' : 'tag';
                        
                        item.innerHTML = `
                            <i class="fas fa-${icon} me-2 text-secondary"></i>
                            <span>${suggestion.text}</span>
                            <div class="suggestion-subtext">${suggestion.subtext}</div>
                        `;
                        
                        item.addEventListener('click', function() {
                            if (suggestion.type === 'candidate') {
                                searchInput.value = suggestion.text;
                            } else {
                                searchInput.value = suggestion.text;
                            }
                            document.getElementById('search-form').submit();
                        });
                        
                        suggestionsContainer.appendChild(item);
                    });
                    
                    suggestionsContainer.style.display = 'block';
                });
        }, 300);
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = 'none';
        }
    });
}

/**
 * Initialize summarize buttons to show candidate summaries
 */
function initSummarizeButtons() {
    const summarizeBtns = document.querySelectorAll('.summarize-btn');
    
    summarizeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const candidateId = this.getAttribute('data-candidate-id');
            
            // For this demo, we'll just toggle a class to show a static summary
            // In a real application, this would make an API call to generate a summary
            
            const card = this.closest('.candidate-card');
            
            if (card.classList.contains('summarized')) {
                // Remove the summary and restore the original content
                card.classList.remove('summarized');
                this.innerHTML = '<i class="fas fa-file-alt me-1"></i> Summarize';
            } else {
                // Add the summary class and change the button text
                card.classList.add('summarized');
                this.innerHTML = '<i class="fas fa-times me-1"></i> Close';
                
                // In a real application, we would show a loading indicator and fetch
                // the summary from the server here
            }
        });
    });
}
