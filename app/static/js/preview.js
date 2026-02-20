/**
 * PDF Preview Component
 * 
 * Renders PDF previews using PDF.js.
 * Allows users to preview uploaded PDFs before processing.
 */

class PDFPreview {
    constructor(options = {}) {
        this.container = options.container || document.getElementById('preview-container');
        this.canvas = options.canvas || document.getElementById('preview-canvas');
        this.filenameEl = options.filenameEl || document.getElementById('preview-filename');
        this.pageInfoEl = options.pageInfoEl || document.getElementById('preview-page-info');
        this.prevBtn = options.prevBtn || document.getElementById('preview-prev');
        this.nextBtn = options.nextBtn || document.getElementById('preview-next');
        this.closeBtn = options.closeBtn || document.getElementById('preview-close');
        
        // State
        this.currentPdf = null;
        this.currentPage = 1;
        this.totalPages = 0;
        this.currentFile = null;
        
        // Set PDF.js worker
        if (typeof pdfjsLib !== 'undefined') {
            pdfjsLib.GlobalWorkerOptions.workerSrc = 
                'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        }
        
        this.init();
    }
    
    init() {
        // Close button handler
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.hide());
        }
        
        // Navigation handlers
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prevPage());
        }
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextPage());
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (!this.container.classList.contains('hidden')) {
                if (e.key === 'Escape') {
                    this.hide();
                } else if (e.key === 'ArrowLeft') {
                    this.prevPage();
                } else if (e.key === 'ArrowRight') {
                    this.nextPage();
                }
            }
        });
    }
    
    /**
     * Check if a file is a PDF
     */
    isPDF(file) {
        return file.type === 'application/pdf' || 
               file.name.toLowerCase().endsWith('.pdf');
    }
    
    /**
     * Show preview for a file
     * @param {File} file - PDF file to preview
     */
    async show(file) {
        if (!this.isPDF(file)) {
            console.warn('File is not a PDF');
            return;
        }
        
        this.currentFile = file;
        this.currentPage = 1;
        
        try {
            // Read file
            const arrayBuffer = await file.arrayBuffer();
            
            // Load PDF
            this.currentPdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
            this.totalPages = this.currentPdf.numPages;
            
            // Update UI
            this.filenameEl.textContent = file.name;
            this.updatePageInfo();
            this.updateNavButtons();
            
            // Show container
            this.container.classList.remove('hidden');
            
            // Render first page
            await this.renderPage(1);
            
        } catch (error) {
            console.error('Failed to load PDF:', error);
            this.hide();
        }
    }
    
    /**
     * Render a specific page
     * @param {number} pageNum - Page number (1-indexed)
     */
    async renderPage(pageNum) {
        if (!this.currentPdf) return;
        
        try {
            const page = await this.currentPdf.getPage(pageNum);
            
            // Calculate scale to fit in container
            const containerWidth = this.container.querySelector('.preview-canvas-wrapper')?.clientWidth || 600;
            const viewport = page.getViewport({ scale: 1 });
            const scale = Math.min(containerWidth / viewport.width, 1.5);
            const scaledViewport = page.getViewport({ scale });
            
            // Set canvas dimensions
            this.canvas.width = scaledViewport.width;
            this.canvas.height = scaledViewport.height;
            
            // Render
            const context = this.canvas.getContext('2d');
            await page.render({
                canvasContext: context,
                viewport: scaledViewport
            }).promise;
            
            this.currentPage = pageNum;
            this.updatePageInfo();
            this.updateNavButtons();
            
        } catch (error) {
            console.error('Failed to render page:', error);
        }
    }
    
    /**
     * Navigate to next page
     */
    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.renderPage(this.currentPage + 1);
        }
    }
    
    /**
     * Navigate to previous page
     */
    prevPage() {
        if (this.currentPage > 1) {
            this.renderPage(this.currentPage - 1);
        }
    }
    
    /**
     * Update page info display
     */
    updatePageInfo() {
        if (this.pageInfoEl) {
            this.pageInfoEl.textContent = `Page ${this.currentPage} of ${this.totalPages}`;
        }
    }
    
    /**
     * Update navigation button states
     */
    updateNavButtons() {
        if (this.prevBtn) {
            this.prevBtn.disabled = this.currentPage <= 1;
        }
        if (this.nextBtn) {
            this.nextBtn.disabled = this.currentPage >= this.totalPages;
        }
    }
    
    /**
     * Hide preview
     */
    hide() {
        this.container.classList.add('hidden');
        this.currentPdf = null;
        this.currentFile = null;
        this.currentPage = 1;
        this.totalPages = 0;
    }
    
    /**
     * Check if preview is visible
     */
    isVisible() {
        return !this.container.classList.contains('hidden');
    }
}


// Export for use in other modules
window.PDFPreview = PDFPreview;
