document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeToggleIcon = document.getElementById('themeToggleIcon');
    const themeToggleText = document.getElementById('themeToggleText');
    
    const lengthRange = document.getElementById('lengthRange');
    const lengthVal = document.getElementById('lengthVal');
    const passwordForm = document.getElementById('passwordForm');
    const generateBtn = document.getElementById('generateBtn');
    
    const resultCard = document.getElementById('resultCard');
    const passwordOutput = document.getElementById('passwordOutput');
    const copyBtn = document.getElementById('copyBtn');
    const copyIcon = document.getElementById('copyIcon');
    const copyText = document.getElementById('copyText');
    
    const strengthBadge = document.getElementById('strengthBadge');
    const strengthProgress = document.getElementById('strengthProgress');
    const entropyVal = document.getElementById('entropyVal');
    const securityFeedback = document.getElementById('securityFeedback');
    
    const statTotal = document.getElementById('statTotal');
    const statAvgEntropy = document.getElementById('statAvgEntropy');
    const statWeakCount = document.getElementById('statWeakCount');
    const statMediumCount = document.getElementById('statMediumCount');
    const statStrongCount = document.getElementById('statStrongCount');
    const statVeryStrongCount = document.getElementById('statVeryStrongCount');
    
    const barWeak = document.getElementById('barWeak');
    const barMedium = document.getElementById('barMedium');
    const barStrong = document.getElementById('barStrong');
    const barVeryStrong = document.getElementById('barVeryStrong');
    
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const emptyHistoryMsg = document.getElementById('emptyHistoryMsg');
    const historyList = document.getElementById('historyList');
    
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');

    // Tooltips Initialization
    const initTooltips = () => {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    };
    initTooltips();

    // 1. Dark / Light Mode Toggle
    const setTheme = (theme) => {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        
        if (theme === 'dark') {
            themeToggleIcon.className = 'bi bi-sun-fill';
            themeToggleText.textContent = 'Light Mode';
        } else {
            themeToggleIcon.className = 'bi bi-moon-fill';
            themeToggleText.textContent = 'Dark Mode';
        }
    };

    // Load initial theme state
    const currentTheme = localStorage.getItem('theme') || 'dark';
    setTheme(currentTheme);

    themeToggleBtn.addEventListener('click', () => {
        const activeTheme = document.documentElement.getAttribute('data-bs-theme');
        const nextTheme = activeTheme === 'dark' ? 'light' : 'dark';
        setTheme(nextTheme);
    });

    // 2. Length Slider updates badge
    lengthRange.addEventListener('input', (e) => {
        lengthVal.textContent = e.target.value;
    });

    // 3. AJAX Password Generation
    passwordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Hide previous errors and show loading state
        errorAlert.classList.add('d-none');
        generateBtn.disabled = true;
        generateBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...`;
        
        const formData = new FormData(passwordForm);
        const actionUrl = passwordForm.getAttribute('action');

        try {
            const response = await fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Display result card and update contents
                resultCard.classList.remove('d-none');
                passwordOutput.textContent = data.password;
                
                // Update strength badge
                strengthBadge.textContent = data.analysis.strength;
                strengthBadge.className = `badge fs-6 px-3 py-1 fw-bold bg-${data.analysis.color}`;
                if (data.analysis.color === 'warning' || data.analysis.color === 'info') {
                    strengthBadge.classList.add('text-dark');
                } else {
                    strengthBadge.classList.add('text-white');
                }
                
                // Update strength meter
                strengthProgress.style.width = `${data.analysis.progress}%`;
                strengthProgress.setAttribute('aria-valuenow', data.analysis.progress);
                strengthProgress.className = `progress-bar progress-bar-striped progress-bar-animated bg-${data.analysis.color}`;
                
                // Update details
                entropyVal.textContent = `${data.analysis.entropy} bits`;
                securityFeedback.textContent = data.analysis.feedback;
                
                // Scroll to result on small screens
                resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                
                // Update stats and history lists
                updateStats(data.stats);
                updateHistory(data.history);
            } else {
                // Display error message
                showError(data.errors);
            }
        } catch (error) {
            showError({ __all__: 'Network error. Please try again.' });
            console.error('Error generating password:', error);
        } finally {
            // Restore button state
            generateBtn.disabled = false;
            generateBtn.innerHTML = `<i class="bi bi-shield-lock-fill"></i> Generate Password`;
        }
    });

    // 4. One-Click Copy Password
    const copyToClipboard = (text, btnEl, originalIconClass, originalText) => {
        navigator.clipboard.writeText(text).then(() => {
            const icon = btnEl.querySelector('i');
            const textSpan = btnEl.querySelector('span');
            
            // Set success state
            if (icon) icon.className = 'bi bi-check-lg text-success';
            if (textSpan) textSpan.textContent = 'Copied!';
            
            // Temporarily disable button to prevent double-clicks
            btnEl.classList.add('disabled');
            
            // Revert after 2 seconds
            setTimeout(() => {
                if (icon) icon.className = originalIconClass;
                if (textSpan) textSpan.textContent = originalText;
                btnEl.classList.remove('disabled');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            alert('Failed to copy password to clipboard.');
        });
    };

    copyBtn.addEventListener('click', () => {
        const password = passwordOutput.textContent;
        copyToClipboard(password, copyBtn, 'bi bi-copy', 'Copy');
    });

    // Delegate copy clicks on history items
    historyList.addEventListener('click', (e) => {
        const btn = e.target.closest('.copy-history-btn');
        if (!btn) return;
        
        const password = btn.getAttribute('data-password');
        copyToClipboard(password, btn, 'bi bi-copy', '');
    });

    // 5. AJAX Clear History
    clearHistoryBtn.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to clear your generation history?')) return;
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        try {
            const response = await fetch('/clear-history/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            if (response.ok && data.success) {
                updateStats(data.stats);
                updateHistory(data.history);
            }
        } catch (error) {
            console.error('Error clearing history:', error);
            alert('Failed to clear history.');
        }
    });

    // Helper: Show Error Alert
    const showError = (errors) => {
        let msg = '';
        if (typeof errors === 'string') {
            msg = errors;
        } else if (errors.non_field_errors) {
            msg = errors.non_field_errors;
        } else if (errors.__all__) {
            msg = errors.__all__[0] || errors.__all__;
        } else {
            msg = Object.values(errors).join('<br>');
        }
        errorMessage.innerHTML = msg;
        errorAlert.classList.remove('d-none');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // Helper: Update Dashboard Statistics
    const updateStats = (stats) => {
        statTotal.textContent = stats.total;
        statAvgEntropy.textContent = `${stats.avg_entropy} bits`;
        
        statWeakCount.textContent = `${stats.weak_count} (${stats.weak_pct}%)`;
        statMediumCount.textContent = `${stats.medium_count} (${stats.medium_pct}%)`;
        statStrongCount.textContent = `${stats.strong_count} (${stats.strong_pct}%)`;
        statVeryStrongCount.textContent = `${stats.very_strong_count} (${stats.very_strong_pct}%)`;
        
        barWeak.style.width = `${stats.weak_pct}%`;
        barWeak.setAttribute('aria-valuenow', stats.weak_pct);
        
        barMedium.style.width = `${stats.medium_pct}%`;
        barMedium.setAttribute('aria-valuenow', stats.medium_pct);
        
        barStrong.style.width = `${stats.strong_pct}%`;
        barStrong.setAttribute('aria-valuenow', stats.strong_pct);
        
        barVeryStrong.style.width = `${stats.very_strong_pct}%`;
        barVeryStrong.setAttribute('aria-valuenow', stats.very_strong_pct);
    };

    // Helper: Update History List
    const updateHistory = (history) => {
        if (!history || history.length === 0) {
            historyList.innerHTML = '';
            emptyHistoryMsg.classList.remove('d-none');
            clearHistoryBtn.classList.add('d-none');
            return;
        }
        
        emptyHistoryMsg.classList.add('d-none');
        clearHistoryBtn.classList.remove('d-none');
        
        let html = '';
        history.forEach(item => {
            const formattedTime = item.created_at.substring(0, 19);
            const badgeTextColor = (item.color === 'warning' || item.color === 'info') ? 'text-dark-emphasis' : 'text-white';
            
            html += `
            <div class="list-group-item bg-transparent px-0 py-3 border-bottom border-light-subtle animate-fade-in">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="badge bg-${item.color} ${badgeTextColor}">${item.strength}</span>
                    <small class="text-muted">${formattedTime}</small>
                </div>
                <div class="d-flex justify-content-between align-items-center gap-3">
                    <code class="text-break fs-6 font-monospace overflow-hidden text-nowrap text-truncate" style="max-width: 75%;">${item.password}</code>
                    <button class="btn btn-sm btn-outline-secondary px-2 py-1 rounded-2 copy-history-btn shrink-btn" data-password="${item.password}" data-bs-toggle="tooltip" data-bs-placement="top" title="Copy password">
                        <i class="bi bi-copy"></i>
                    </button>
                </div>
                <div class="d-flex gap-1 mt-2 flex-wrap">
                    <span class="badge bg-secondary-subtle text-secondary-emphasis rounded-pill xs-badge">len: ${item.length}</span>
                    <span class="badge bg-secondary-subtle text-secondary-emphasis rounded-pill xs-badge">ent: ${item.entropy}</span>
                    ${item.options.upper ? '<span class="badge bg-light text-dark rounded-pill xs-badge">A-Z</span>' : ''}
                    ${item.options.lower ? '<span class="badge bg-light text-dark rounded-pill xs-badge">a-z</span>' : ''}
                    ${item.options.digits ? '<span class="badge bg-light text-dark rounded-pill xs-badge">0-9</span>' : ''}
                    ${item.options.special ? '<span class="badge bg-light text-dark rounded-pill xs-badge">#$&</span>' : ''}
                </div>
            </div>
            `;
        });
        
        historyList.innerHTML = html;
        initTooltips(); // re-initialize tooltips for new buttons
    };
});
