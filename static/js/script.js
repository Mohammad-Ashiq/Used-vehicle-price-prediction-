/* ==========================================================================
   USED VEHICLE PRICE PREDICTION SYSTEM - MASTER JAVASCRIPT
   Theme Switcher, Dynamic AJAX Dropdowns, Interactive Charts & Loading Overlay
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
    initTheme();
    initBrandModelDropdown();
    initPredictionLoading();
    initDashboardCharts();
    initCustomCursor();
});

/* --------------------------------------------------------------------------
   1. Theme Switcher (Dark / Light Theme with localStorage Persistence)
   -------------------------------------------------------------------------- */
function initTheme() {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');
    const currentTheme = localStorage.getItem('app_theme') || 'dark';

    // Apply saved theme
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function () {
            const activeTheme = document.documentElement.getAttribute('data-theme') || 'dark';
            const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('app_theme', newTheme);
            updateThemeIcon(newTheme);

            // Re-render dashboard charts if present to match new theme colors
            if (window.renderDashboardCharts) {
                window.renderDashboardCharts();
            }
        });
    }

    function updateThemeIcon(theme) {
        if (!themeIcon) return;
        if (theme === 'light') {
            themeIcon.className = 'bi bi-moon-stars-fill text-warning';
        } else {
            themeIcon.className = 'bi bi-sun-fill text-warning';
        }
    }
}

/* --------------------------------------------------------------------------
   2. Dynamic Dependent Dropdown (Brand -> Model via AJAX)
   -------------------------------------------------------------------------- */
function initBrandModelDropdown() {
    const brandSelect = document.getElementById('brandSelect');
    const modelSelect = document.getElementById('modelSelect');
    const categoryInput = document.getElementById('categoryInput');

    if (!brandSelect || !modelSelect || !categoryInput) return;

    brandSelect.addEventListener('change', function () {
        const selectedBrand = this.value;
        const category = categoryInput.value;

        if (!selectedBrand) {
            modelSelect.innerHTML = '<option value="">-- First Select Brand --</option>';
            modelSelect.disabled = true;
            return;
        }

        // Fetch corresponding models via API
        fetch(`/api/models/${category}?brand=${encodeURIComponent(selectedBrand)}`)
            .then(response => response.json())
            .then(data => {
                modelSelect.innerHTML = '<option value="">-- Select Model --</option>';
                if (data.models && data.models.length > 0) {
                    data.models.forEach(model => {
                        const opt = document.createElement('option');
                        opt.value = model;
                        opt.textContent = model;
                        modelSelect.appendChild(opt);
                    });
                    modelSelect.disabled = false;
                } else {
                    modelSelect.innerHTML = '<option value="">Custom / Other Model</option>';
                    modelSelect.disabled = false;
                }
            })
            .catch(err => {
                console.error("Failed to load models:", err);
            });
    });
}

/* --------------------------------------------------------------------------
   3. Loading Animation on Form Submit
   -------------------------------------------------------------------------- */
function initPredictionLoading() {
    const predictionForm = document.getElementById('predictionForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingStepText = document.getElementById('loadingStepText');

    if (!predictionForm || !loadingOverlay) return;

    predictionForm.addEventListener('submit', function (e) {
        // Validate HTML5 required fields
        if (!this.checkValidity()) {
            return;
        }

        // Show overlay
        loadingOverlay.classList.add('active');

        const steps = [
            "ReVahan AI analyzing vehicle specifications & odometer wear...",
            "Querying historical market trends & regional depreciation...",
            "Executing 120 Random Forest ensemble regression trees...",
            "ReVahan finalizing certified fair market appraisal..."
        ];

        let index = 0;
        const interval = setInterval(() => {
            index++;
            if (index < steps.length && loadingStepText) {
                loadingStepText.textContent = steps[index];
            } else {
                clearInterval(interval);
            }
        }, 700);
    });
}

/* --------------------------------------------------------------------------
   4. Dashboard Visualizations (Chart.js)
   -------------------------------------------------------------------------- */
let categoryChartInstance = null;
let avgPriceChartInstance = null;
let conditionChartInstance = null;

function initDashboardCharts() {
    const catCanvas = document.getElementById('categoryChartCanvas');
    const priceCanvas = document.getElementById('avgPriceChartCanvas');
    const condCanvas = document.getElementById('conditionChartCanvas');

    if (!catCanvas && !priceCanvas && !condCanvas) return;

    window.renderDashboardCharts = function () {
        fetch('/api/stats')
            .then(res => res.json())
            .then(data => {
                const isDark = (document.documentElement.getAttribute('data-theme') || 'dark') === 'dark';
                const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)';
                const textColor = isDark ? '#CBD5E1' : '#334155';

                // Chart 1: Category Distribution (Doughnut)
                if (catCanvas) {
                    if (categoryChartInstance) categoryChartInstance.destroy();
                    const catCtx = catCanvas.getContext('2d');
                    categoryChartInstance = new Chart(catCtx, {
                        type: 'doughnut',
                        data: {
                            labels: ['Cars', 'Bikes', 'Lorries', 'Auto-rickshaws'],
                            datasets: [{
                                data: [
                                    data.category_counts.cars || 0,
                                    data.category_counts.bikes || 0,
                                    data.category_counts.lorries || 0,
                                    data.category_counts.autos || 0
                                ],
                                backgroundColor: ['#3A86FF', '#00F5D4', '#F59E0B', '#A855F7'],
                                borderWidth: 0
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { position: 'bottom', labels: { color: textColor, padding: 15 } }
                            },
                            cutout: '68%'
                        }
                    });
                }

                // Chart 2: Average Price by Category (Bar)
                if (priceCanvas) {
                    if (avgPriceChartInstance) avgPriceChartInstance.destroy();
                    const priceCtx = priceCanvas.getContext('2d');
                    avgPriceChartInstance = new Chart(priceCtx, {
                        type: 'bar',
                        data: {
                            labels: ['Cars', 'Bikes', 'Lorries', 'Auto-rickshaws'],
                            datasets: [{
                                label: 'Average Predicted Resale Value (₹)',
                                data: [
                                    data.category_averages.cars || 0,
                                    data.category_averages.bikes || 0,
                                    data.category_averages.lorries || 0,
                                    data.category_averages.autos || 0
                                ],
                                backgroundColor: ['rgba(58, 134, 255, 0.8)', 'rgba(0, 245, 212, 0.8)', 'rgba(245, 158, 11, 0.8)', 'rgba(168, 85, 247, 0.8)'],
                                borderRadius: 8
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false },
                                tooltip: {
                                    callbacks: {
                                        label: function (context) {
                                            return ' Avg Price: ₹ ' + Number(context.raw).toLocaleString('en-IN');
                                        }
                                    }
                                }
                            },
                            scales: {
                                x: { grid: { display: false }, ticks: { color: textColor } },
                                y: {
                                    grid: { color: gridColor },
                                    ticks: {
                                        color: textColor,
                                        callback: function (val) {
                                            return '₹ ' + (val >= 100000 ? (val / 100000).toFixed(1) + 'L' : val.toLocaleString());
                                        }
                                    }
                                }
                            }
                        }
                    });
                }

                // Chart 3: Condition Spread (Polar Area or Bar)
                if (condCanvas) {
                    if (conditionChartInstance) conditionChartInstance.destroy();
                    const condCtx = condCanvas.getContext('2d');
                    const condLabels = Object.keys(data.condition_stats);
                    const condValues = Object.values(data.condition_stats);

                    conditionChartInstance = new Chart(condCtx, {
                        type: 'polarArea',
                        data: {
                            labels: condLabels.length > 0 ? condLabels : ['Excellent', 'Good', 'Fair', 'Poor'],
                            datasets: [{
                                data: condValues.length > 0 ? condValues : [0, 0, 0, 0],
                                backgroundColor: [
                                    'rgba(16, 185, 129, 0.75)',
                                    'rgba(58, 134, 255, 0.75)',
                                    'rgba(245, 158, 11, 0.75)',
                                    'rgba(239, 68, 68, 0.75)'
                                ]
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { position: 'bottom', labels: { color: textColor } }
                            },
                            scales: {
                                r: { grid: { color: gridColor }, ticks: { display: false } }
                            }
                        }
                    });
                }
            })
            .catch(err => console.error("Error loading dashboard chart stats:", err));
    };

    window.renderDashboardCharts();
}

/* --------------------------------------------------------------------------
   5. Utility: Share Valuation Result
   -------------------------------------------------------------------------- */
function copyResultLink() {
    navigator.clipboard.writeText(window.location.href).then(() => {
        alert("Valuation link copied to clipboard!");
    }).catch(err => {
        console.error("Failed to copy link:", err);
    });
}

/* --------------------------------------------------------------------------
   6. Custom Automotive Cursor & Pointer Follower
   -------------------------------------------------------------------------- */
function initCustomCursor() {
    const halo = document.getElementById('cursorHalo');
    const dot = document.getElementById('cursorDot');
    if (!halo || !dot) return;

    // Hide custom cursor on touch/mobile devices
    if (window.matchMedia('(pointer: coarse)').matches) {
        halo.style.display = 'none';
        dot.style.display = 'none';
        return;
    }

    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let haloX = mouseX;
    let haloY = mouseY;
    let isMoving = false;

    window.addEventListener('mousemove', function (e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
        dot.style.left = mouseX + 'px';
        dot.style.top = mouseY + 'px';
        if (!isMoving) {
            isMoving = true;
            halo.style.opacity = '0.7';
            dot.style.opacity = '1';
        }
    });

    window.addEventListener('mouseleave', function () {
        halo.style.opacity = '0';
        dot.style.opacity = '0';
        isMoving = false;
    });

    // Smooth trailing animation loop
    function animateCursor() {
        haloX += (mouseX - haloX) * 0.18;
        haloY += (mouseY - haloY) * 0.18;
        halo.style.left = haloX + 'px';
        halo.style.top = haloY + 'px';
        requestAnimationFrame(animateCursor);
    }
    requestAnimationFrame(animateCursor);

    // Expand halo on interactive elements hover
    const interactiveSelectors = 'a, button, select, input, textarea, .category-card, .btn-theme-toggle, .pointer-pill, .btn-primary-custom, .btn-outline-custom, .factor-card';
    document.querySelectorAll(interactiveSelectors).forEach(el => {
        el.addEventListener('mouseenter', () => {
            halo.style.width = '42px';
            halo.style.height = '42px';
            halo.style.borderColor = 'var(--accent-cyan)';
            halo.style.background = 'rgba(0, 242, 254, 0.08)';
            halo.style.transform = 'translate(-50%, -50%) scale(1.15)';
        });
        el.addEventListener('mouseleave', () => {
            halo.style.width = '24px';
            halo.style.height = '24px';
            halo.style.borderColor = 'var(--accent-gold)';
            halo.style.background = 'transparent';
            halo.style.transform = 'translate(-50%, -50%) scale(1)';
        });
    });
}

