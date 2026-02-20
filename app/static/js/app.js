/**
 * NoTracePDF - Main Application
 * 
 * Coordinates the UI interactions, file uploads, and API calls.
 * Implements privacy-first design: no persistence, no tracking.
 */

class NoTracePDFApp {
    constructor() {
        // DOM Elements
        this.toolCards = document.querySelectorAll('.tool-card');
        this.modal = document.getElementById('tool-modal');
        this.modalBackdrop = document.querySelector('.modal-backdrop');
        this.modalTitle = document.getElementById('modal-title');
        this.modalClose = document.querySelector('.modal-close');
        this.uploadZone = document.getElementById('upload-zone');
        this.fileInput = document.getElementById('file-input');
        this.fileListContainer = document.getElementById('file-list');
        this.filesContainer = document.getElementById('files-container');
        this.toolOptions = document.getElementById('tool-options');
        this.progressSection = document.getElementById('progress-section');
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        this.resultSection = document.getElementById('result-section');
        this.textResult = document.getElementById('text-result');
        this.extractedTextContent = document.getElementById('extracted-text-content');
        this.copyTextBtn = document.getElementById('copy-text-btn');
        this.errorSection = document.getElementById('error-section');
        this.errorText = document.getElementById('error-text');
        this.btnBack = document.getElementById('btn-back');
        this.btnProcess = document.getElementById('btn-process');
        this.btnDownload = document.getElementById('btn-download');
        this.btnNew = document.getElementById('btn-new');

        // State
        this.currentTool = null;
        this.currentConfig = null;
        this.apiClient = new APIClient();
        this.uploadHandler = null;
        this.lastResult = null;
        
        // Client-side processor for small files
        this.clientSideProcessor = new ClientSideProcessor();
        
        // PDF Preview
        this.pdfPreview = new PDFPreview();
        
        // Theme toggle
        this.themeToggle = document.getElementById('theme-toggle');
        this.initTheme();

        // Language toggle
        this.langToggle = document.getElementById('lang-toggle');
        this.initLanguage();

        // Search functionality
        this.searchInput = document.getElementById('tool-search');
        this.searchClear = document.getElementById('search-clear');
        this.searchResultsCount = document.getElementById('search-results-count');
        this.initSearch();

        // Initialize i18n
        if (window.i18n) {
            window.i18n.init();
        }

        // Initialize
        this.init();
    }
    
    /**
     * Initialize language toggle
     */
    initLanguage() {
        if (!this.langToggle) return;
        
        this.langToggle.addEventListener('click', () => {
            if (window.i18n) {
                window.i18n.toggleLanguage();
                // Re-run search if there's a query
                if (this.searchInput && this.searchInput.value) {
                    this.handleSearch(this.searchInput.value);
                }
            }
        });
    }
    
    /**
     * Initialize search functionality
     */
    initSearch() {
        if (!this.searchInput) return;
        
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });
        
        if (this.searchClear) {
            this.searchClear.addEventListener('click', () => {
                this.searchInput.value = '';
                this.handleSearch('');
                this.searchInput.focus();
            });
        }
        
        // Keyboard shortcut: "/" to focus search
        document.addEventListener('keydown', (e) => {
            if (e.key === '/' && !this.modal.classList.contains('hidden') === false) {
                const target = e.target;
                if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
                    e.preventDefault();
                    this.searchInput.focus();
                }
            }
        });
    }
    
    /**
     * Handle search input and filter tools
     */
    handleSearch(query) {
        const normalizedQuery = query.toLowerCase().trim();
        
        // Toggle clear button
        if (this.searchClear) {
            if (normalizedQuery.length > 0) {
                this.searchClear.classList.remove('hidden');
            } else {
                this.searchClear.classList.add('hidden');
            }
        }
        
        // Get current and other language for searching
        const currentLang = window.i18n ? window.i18n.getLanguage() : 'it';
        const otherLang = currentLang === 'it' ? 'en' : 'it';
        
        // Get all tool sections and cards
        const toolSections = document.querySelectorAll('.tool-section');
        let totalVisible = 0;
        
        toolSections.forEach(section => {
            const cards = section.querySelectorAll('.tool-card');
            let sectionVisible = 0;
            
            cards.forEach(card => {
                const title = card.querySelector('.tool-title')?.textContent.toLowerCase() || '';
                const description = card.querySelector('.tool-description')?.textContent.toLowerCase() || '';
                const toolId = card.dataset.tool || '';
                
                // Get translations for both languages
                let titleEn = title;
                let descEn = description;
                let titleIt = title;
                let descIt = description;
                
                if (window.i18n) {
                    const toolKey = card.dataset.tool;
                    const trans = window.i18n.translations['en'][window.i18n.toolKeyMap[toolKey]];
                    if (trans) {
                        titleEn = trans.title.toLowerCase();
                        descEn = trans.desc.toLowerCase();
                    }
                    const transIt = window.i18n.translations['it'][window.i18n.toolKeyMap[toolKey]];
                    if (transIt) {
                        titleIt = transIt.title.toLowerCase();
                        descIt = transIt.desc.toLowerCase();
                    }
                }
                
                // Check if query matches any language (current, other, or tool ID)
                const matchesCurrentLang = title.includes(normalizedQuery) || descEn.includes(normalizedQuery);
                const matchesOtherLang = titleEn.includes(normalizedQuery) || descEn.includes(normalizedQuery) ||
                                        titleIt.includes(normalizedQuery) || descIt.includes(normalizedQuery);
                const matchesToolId = toolId.includes(normalizedQuery);
                
                if (normalizedQuery === '' || matchesCurrentLang || matchesOtherLang || matchesToolId) {
                    card.classList.remove('hidden');
                    sectionVisible++;
                    totalVisible++;
                } else {
                    card.classList.add('hidden');
                }
            });
            
            // Show/hide entire section based on visible cards
            if (sectionVisible > 0) {
                section.classList.remove('hidden');
            } else {
                section.classList.add('hidden');
            }
        });
        
        // Update results count
        if (this.searchResultsCount) {
            if (normalizedQuery.length > 0) {
                if (window.i18n) {
                    const key = totalVisible === 1 ? 'foundTools' : 'foundTools_plural';
                    this.searchResultsCount.textContent = window.i18n.t(key, { count: totalVisible });
                } else {
                    this.searchResultsCount.textContent = `Found ${totalVisible} tool${totalVisible !== 1 ? 's' : ''}`;
                }
                this.searchResultsCount.classList.remove('hidden');
            } else {
                this.searchResultsCount.classList.add('hidden');
            }
        }
    }
    
    /**
     * Initialize theme from localStorage
     */
    initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeIcon(savedTheme);
        
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }
    
    /**
     * Toggle between light and dark theme
     */
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        this.updateThemeIcon(newTheme);
    }
    
    /**
     * Update theme toggle button icon
     */
    updateThemeIcon(theme) {
        if (!this.themeToggle) return;
        
        const sunIcon = this.themeToggle.querySelector('.sun-icon');
        const moonIcon = this.themeToggle.querySelector('.moon-icon');
        
        if (theme === 'dark') {
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        } else {
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        }
    }

    init() {
        // Tool card click handlers
        this.toolCards.forEach(card => {
            card.addEventListener('click', () => {
                const toolId = card.dataset.tool;
                this.openTool(toolId);
            });
        });

        // Modal close handlers
        this.modalClose.addEventListener('click', () => this.closeModal());
        this.modalBackdrop.addEventListener('click', () => this.closeModal());
        
        // Keyboard handler for escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
                this.closeModal();
            }
        });

        // Button handlers
        this.btnBack.addEventListener('click', () => this.goBack());
        this.btnProcess.addEventListener('click', () => this.processFiles());
        this.btnDownload.addEventListener('click', () => this.downloadResult());
        this.btnNew.addEventListener('click', () => this.resetModal());

        // Copy text button
        if (this.copyTextBtn) {
            this.copyTextBtn.addEventListener('click', () => this.copyExtractedText());
        }

        // Initialize upload handler
        this.uploadHandler = new UploadHandler({
            uploadZone: this.uploadZone,
            fileInput: this.fileInput,
            fileListContainer: this.fileListContainer,
            filesContainer: this.filesContainer,
            onFilesChange: (files, errors) => this.handleFilesChange(files, errors)
        });
        
        // Preview button click handler
        this.filesContainer.addEventListener('click', (e) => {
            const previewBtn = e.target.closest('.preview-btn');
            if (previewBtn) {
                const index = parseInt(previewBtn.dataset.fileIndex, 10);
                const files = this.uploadHandler.getFiles();
                if (files[index]) {
                    this.pdfPreview.show(files[index]);
                }
            }
        });
    }

    openTool(toolId) {
        const config = TOOL_CONFIG[toolId];
        if (!config) {
            console.error('Unknown tool:', toolId);
            return;
        }

        this.currentTool = toolId;
        this.currentConfig = config;

        // Update modal title
        this.modalTitle.textContent = config.name;

        // Check if this tool requires file upload
        if (config.noFileUpload) {
            // Hide upload zone for tools that don't need files (like URL to PDF)
            this.uploadZone.classList.add('hidden');
            this.uploadHandler.clearFiles();
        } else {
            // Configure upload handler
            const acceptedTypes = config.acceptMime ? config.acceptMime.split(',') : [];
            const acceptedExtensions = config.accepts || [];
            this.uploadHandler.setAcceptedTypes(acceptedTypes, acceptedExtensions);
            this.uploadHandler.setMultiple(config.multipleFiles);

            // Update file input accept attribute
            this.fileInput.accept = acceptedExtensions.join(',');
            this.uploadZone.classList.remove('hidden');
        }

        // Generate options HTML
        const optionsHTML = generateOptionsHTML(toolId);
        this.toolOptions.innerHTML = optionsHTML;
        
        if (optionsHTML) {
            this.toolOptions.classList.remove('hidden');
            this.setupOptionVisibility();
        } else {
            this.toolOptions.classList.add('hidden');
        }

        // Show modal
        this.modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        // Reset state
        this.resetModalState();

        // For noFileUpload tools, enable process button immediately if options are valid
        if (config.noFileUpload) {
            this.btnProcess.disabled = false;
        }
    }

    setupOptionVisibility() {
        // Handle showIf conditions for options
        const conditionalOptions = this.toolOptions.querySelectorAll('[data-showif]');
        
        conditionalOptions.forEach(option => {
            const [key, value] = option.dataset.showif.split('=');
            const sourceInput = this.toolOptions.querySelector(`[name="${key}"]`);
            
            if (sourceInput) {
                const updateVisibility = () => {
                    const currentValue = sourceInput.type === 'radio' 
                        ? this.toolOptions.querySelector(`[name="${key}"]:checked`)?.value
                        : sourceInput.value;
                    
                    if (currentValue === option.dataset.showifValue) {
                        option.classList.remove('hidden');
                    } else {
                        option.classList.add('hidden');
                    }
                };

                if (sourceInput.type === 'radio') {
                    this.toolOptions.querySelectorAll(`[name="${key}"]`).forEach(radio => {
                        radio.addEventListener('change', updateVisibility);
                    });
                } else {
                    sourceInput.addEventListener('change', updateVisibility);
                }

                // Initial check
                updateVisibility();
            }
        });
    }

    closeModal() {
        this.modal.classList.add('hidden');
        document.body.style.overflow = '';
        this.resetModalState();
    }

    resetModalState() {
        // Clear files
        this.uploadHandler.clearFiles();
        
        // Hide sections
        this.fileListContainer.classList.add('hidden');
        this.progressSection.classList.add('hidden');
        this.resultSection.classList.add('hidden');
        this.textResult.classList.add('hidden');
        this.errorSection.classList.add('hidden');

        // Reset buttons
        this.btnBack.classList.add('hidden');
        this.btnProcess.classList.remove('hidden');
        this.btnProcess.disabled = true;
        this.btnDownload.classList.add('hidden');
        this.btnNew.classList.add('hidden');

        // Reset progress
        this.progressFill.style.width = '0%';
        this.progressText.textContent = 'Uploading...';

        // Reset options form
        if (this.toolOptions) {
            this.toolOptions.reset && this.toolOptions.reset();
        }

        // Clear last result
        this.lastResult = null;

        // Show upload zone (unless noFileUpload tool)
        const config = this.currentConfig;
        if (config && config.noFileUpload) {
            this.uploadZone.classList.add('hidden');
            this.btnProcess.disabled = false;
        } else {
            this.uploadZone.classList.remove('hidden');
        }
    }

    handleFilesChange(files, errors) {
        // Display validation errors
        if (errors.length > 0) {
            const messages = errors.map(e => `${e.file}: ${e.error}`).join('\n');
            this.showError(messages);
            setTimeout(() => this.hideError(), 5000);
        }

        // Enable/disable process button
        const config = this.currentConfig;
        const minFiles = config.multipleFiles ? 2 : 1;
        this.btnProcess.disabled = files.length < minFiles;
    }

    async processFiles() {
        const files = this.uploadHandler.getFiles();
        const config = this.currentConfig;

        // For noFileUpload tools, files array is empty
        if (!config.noFileUpload && files.length === 0) return;

        // Validate required fields
        if (!this.validateOptions()) {
            return;
        }

        // Show progress
        this.uploadZone.classList.add('hidden');
        this.fileListContainer.classList.add('hidden');
        this.toolOptions.classList.add('hidden');
        this.progressSection.classList.remove('hidden');
        this.btnProcess.disabled = true;

        try {
            // Check if we can process client-side (for small files)
            if (this.clientSideProcessor.canProcessClientSide(files, this.currentTool)) {
                // Process in browser - zero server contact
                await this.processClientSide(files);
                return;
            }
            
            // Otherwise, submit to API
            let formData = collectFormData(this.currentTool, files, this.toolOptions);
            
            // Handle watermark image type switch
            if (this.currentTool === 'watermark') {
                const watermarkType = this.toolOptions.querySelector('[name="watermarkType"]:checked')?.value;
                if (watermarkType === 'image') {
                    formData = collectFormData('watermark', files, this.toolOptions);
                    // Update endpoint for image watermark
                    this.currentConfig.endpoint = '/api/v1/pdf/watermark/image';
                } else {
                    this.currentConfig.endpoint = '/api/v1/pdf/watermark/text';
                }
            }

            // Submit to API
            this.progressText.textContent = 'Uploading...';
            
            const result = await this.apiClient.submitJob(
                this.currentConfig.endpoint,
                formData,
                (percent, stage) => {
                    if (stage === 'uploading') {
                        this.progressFill.style.width = `${percent}%`;
                        this.progressText.textContent = `Uploading... ${percent}%`;
                    } else {
                        this.progressText.textContent = 'Connecting...';
                    }
                }
            );

            // Show processing complete
            this.progressFill.style.width = '100%';
            this.progressText.textContent = 'Processing complete!';

            // Store result
            this.lastResult = result;

            // Show appropriate result
            setTimeout(() => {
                this.progressSection.classList.add('hidden');

                if (result.type === 'json' && this.currentConfig.returnsText) {
                    // Text extraction result
                    this.showTextResult(result.data);
                } else {
                    // File download result
                    this.showFileResult();
                }
            }, 500);

        } catch (error) {
            this.progressSection.classList.add('hidden');
            this.showError(error.message);
            this.btnProcess.disabled = false;
            if (!config.noFileUpload) {
                this.uploadZone.classList.remove('hidden');
                this.fileListContainer.classList.remove('hidden');
            }
            this.toolOptions.classList.remove('hidden');
        }
    }
    
    /**
     * Process files entirely in the browser (no server contact)
     */
    async processClientSide(files) {
        try {
            this.progressText.textContent = 'Processing in browser (zero server contact)...';
            this.progressFill.style.width = '50%';
            
            let result;
            const options = this._collectClientSideOptions();
            
            switch (this.currentTool) {
                case 'merge':
                    result = await this.clientSideProcessor.merge(files);
                    break;
                case 'split':
                    result = await this.clientSideProcessor.split(files[0], options);
                    break;
                case 'rotate':
                    result = await this.clientSideProcessor.rotate(
                        files[0],
                        options.degrees || 90,
                        options.pages || 'all'
                    );
                    break;
                default:
                    throw new Error('Unsupported client-side operation');
            }
            
            this.progressFill.style.width = '100%';
            this.progressText.textContent = 'Processing complete!';
            
            // Store result
            this.lastResult = {
                type: 'file',
                blob: result.blob,
                filename: result.filename
            };
            
            // Show result
            setTimeout(() => {
                this.progressSection.classList.add('hidden');
                this.showFileResult();
            }, 500);
            
        } catch (error) {
            this.progressSection.classList.add('hidden');
            this.showError(`Client-side processing failed: ${error.message}`);
            this.btnProcess.disabled = false;
            this.uploadZone.classList.remove('hidden');
            this.fileListContainer.classList.remove('hidden');
            this.toolOptions.classList.remove('hidden');
        }
    }
    
    /**
     * Collect options for client-side processing
     */
    _collectClientSideOptions() {
        const options = {};
        
        if (!this.toolOptions) return options;
        
        // Get rotation degrees
        const degreesInput = this.toolOptions.querySelector('[name="degrees"]:checked');
        if (degreesInput) {
            options.degrees = parseInt(degreesInput.value, 10);
        }
        
        // Get pages
        const pagesSelect = this.toolOptions.querySelector('[name="pages"]');
        if (pagesSelect && pagesSelect.value !== 'all') {
            const pageNumbersInput = this.toolOptions.querySelector('[name="pageNumbers"]');
            if (pageNumbersInput && pageNumbersInput.value) {
                // Parse page numbers
                const pages = pageNumbersInput.value.split(',')
                    .map(s => parseInt(s.trim(), 10))
                    .filter(n => !isNaN(n));
                options.pages = pages;
            }
        }
        
        // Get split mode options
        const modeSelect = this.toolOptions.querySelector('[name="mode"]');
        if (modeSelect) {
            options.mode = modeSelect.value;
        }
        
        const startInput = this.toolOptions.querySelector('[name="start"]');
        if (startInput) {
            options.start = parseInt(startInput.value, 10);
        }
        
        const endInput = this.toolOptions.querySelector('[name="end"]');
        if (endInput) {
            options.end = parseInt(endInput.value, 10);
        }
        
        return options;
    }

    validateOptions() {
        const requiredInputs = this.toolOptions.querySelectorAll('[required]');
        for (const input of requiredInputs) {
            const group = input.closest('.option-group');
            if (group && group.classList.contains('hidden')) {
                continue; // Skip hidden required fields
            }

            if (!input.value || (input.type === 'checkbox' && !input.checked)) {
                this.showError(`Please fill in: ${input.name}`);
                return false;
            }
        }
        return true;
    }

    showTextResult(data) {
        // Format extracted text
        let textContent = '';
        if (data.pages) {
            for (const page of data.pages) {
                textContent += `--- Page ${page.page_number} ---\n`;
                textContent += page.text || '(No text extracted)';
                textContent += '\n\n';
            }
        } else if (data.text) {
            textContent = data.text;
        } else {
            textContent = JSON.stringify(data, null, 2);
        }

        this.extractedTextContent.textContent = textContent;
        this.textResult.classList.remove('hidden');
        
        // Show buttons
        this.btnNew.classList.remove('hidden');
        this.resultSection.classList.add('hidden');
    }

    showFileResult() {
        this.resultSection.classList.remove('hidden');
        this.btnDownload.classList.remove('hidden');
        this.btnNew.classList.remove('hidden');
    }

    downloadResult() {
        if (!this.lastResult || this.lastResult.type !== 'file') {
            return;
        }

        this.apiClient.downloadFile(this.lastResult.blob, this.lastResult.filename);

        // Show deletion confirmation - files permanently deleted from server
        // The resultSection displays: "Your files have been permanently deleted from the server"
        this.btnDownload.classList.add('hidden');
        
        // Reset state after download
        setTimeout(() => {
            this.resetModalState();
        }, 2000);
    }

    copyExtractedText() {
        const text = this.extractedTextContent.textContent;
        navigator.clipboard.writeText(text).then(() => {
            const originalText = this.copyTextBtn.textContent;
            this.copyTextBtn.textContent = 'Copied!';
            setTimeout(() => {
                this.copyTextBtn.textContent = originalText;
            }, 2000);
        }).catch(() => {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            
            const originalText = this.copyTextBtn.textContent;
            this.copyTextBtn.textContent = 'Copied!';
            setTimeout(() => {
                this.copyTextBtn.textContent = originalText;
            }, 2000);
        });
    }

    showError(message) {
        this.errorText.textContent = message;
        this.errorSection.classList.remove('hidden');
    }

    hideError() {
        this.errorSection.classList.add('hidden');
    }

    goBack() {
        this.uploadZone.classList.remove('hidden');
        this.fileListContainer.classList.remove('hidden');
        this.toolOptions.classList.remove('hidden');
        this.progressSection.classList.add('hidden');
        this.resultSection.classList.add('hidden');
        this.textResult.classList.add('hidden');
        this.errorSection.classList.add('hidden');
        this.btnBack.classList.add('hidden');
        this.btnProcess.classList.remove('hidden');
        this.btnProcess.disabled = !this.uploadHandler.hasFiles();
        this.btnDownload.classList.add('hidden');
        this.btnNew.classList.add('hidden');
    }

    resetModal() {
        this.resetModalState();
    }
}


// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new NoTracePDFApp();
});
