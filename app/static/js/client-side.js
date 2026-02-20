/**
 * Client-Side PDF Processor
 * 
 * Processes PDFs entirely in the browser using pdf-lib.js.
 * Used for files under 20MB for maximum privacy (zero server contact).
 * 
 * Supported operations: merge, split, rotate
 */

class ClientSideProcessor {
    constructor() {
        this.maxFileSize = 20 * 1024 * 1024; // 20MB
        this.supportedOperations = ['merge', 'split', 'rotate'];
    }
    
    /**
     * Check if files can be processed client-side
     * @param {File[]} files - Array of files to check
     * @param {string} operation - Operation type
     * @returns {boolean}
     */
    canProcessClientSide(files, operation) {
        // Check if operation is supported
        if (!this.supportedOperations.includes(operation)) {
            return false;
        }
        
        // Check if all files are under the size limit
        for (const file of files) {
            if (file.size > this.maxFileSize) {
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Merge multiple PDFs into one
     * @param {File[]} files - PDF files to merge
     * @returns {Promise<{blob: Blob, filename: string}>}
     */
    async merge(files) {
        const { PDFDocument } = PDFLib;
        
        // Create new PDF document
        const mergedPdf = await PDFDocument.create();
        
        // Process each file
        for (const file of files) {
            const arrayBuffer = await file.arrayBuffer();
            const pdf = await PDFDocument.load(arrayBuffer);
            const pages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
            pages.forEach(page => mergedPdf.addPage(page));
        }
        
        // Save to bytes
        const pdfBytes = await mergedPdf.save();
        
        // Create blob
        const blob = new Blob([pdfBytes], { type: 'application/pdf' });
        
        // Generate filename
        const baseName = files[0].name.replace(/\.pdf$/i, '');
        const filename = `${baseName}_merged.pdf`;
        
        return { blob, filename };
    }
    
    /**
     * Split PDF by page range or extract pages
     * @param {File} file - PDF file to split
     * @param {Object} options - Split options
     * @returns {Promise<{blob: Blob, filename: string}>}
     */
    async split(file, options = {}) {
        const { PDFDocument } = PDFLib;
        
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await PDFDocument.load(arrayBuffer);
        const totalPages = pdf.getPageCount();
        
        // Create new PDF for result
        const resultPdf = await PDFDocument.create();
        
        // Determine pages to extract
        let pagesToExtract = [];
        
        if (options.pages && Array.isArray(options.pages)) {
            // Specific pages (1-indexed from UI, convert to 0-indexed)
            pagesToExtract = options.pages.map(p => p - 1).filter(i => i >= 0 && i < totalPages);
        } else if (options.start !== undefined && options.end !== undefined) {
            // Page range
            const start = Math.max(0, (options.start || 1) - 1);
            const end = Math.min(totalPages, options.end || totalPages);
            for (let i = start; i < end; i++) {
                pagesToExtract.push(i);
            }
        } else {
            // Default: extract all pages
            pagesToExtract = Array.from({ length: totalPages }, (_, i) => i);
        }
        
        // Copy pages
        if (pagesToExtract.length > 0) {
            const copiedPages = await resultPdf.copyPages(pdf, pagesToExtract);
            copiedPages.forEach(page => resultPdf.addPage(page));
        }
        
        // Save to bytes
        const pdfBytes = await resultPdf.save();
        
        // Create blob
        const blob = new Blob([pdfBytes], { type: 'application/pdf' });
        
        // Generate filename
        const baseName = file.name.replace(/\.pdf$/i, '');
        const filename = `${baseName}_split.pdf`;
        
        return { blob, filename };
    }
    
    /**
     * Rotate pages in PDF
     * @param {File} file - PDF file to rotate
     * @param {number} degrees - Rotation angle (90, 180, 270)
     * @param {string|number[]} pages - 'all' or array of page numbers (1-indexed)
     * @returns {Promise<{blob: Blob, filename: string}>}
     */
    async rotate(file, degrees = 90, pages = 'all') {
        const { PDFDocument, degrees: PDFDegrees } = PDFLib;
        
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await PDFDocument.load(arrayBuffer);
        const totalPages = pdf.getPageCount();
        
        // Convert degrees to pdf-lib degrees
        const rotationAngle = this._degreesToRotation(degrees);
        
        // Determine which pages to rotate
        let pagesToRotate = [];
        if (pages === 'all') {
            pagesToRotate = Array.from({ length: totalPages }, (_, i) => i);
        } else if (Array.isArray(pages)) {
            // Convert 1-indexed to 0-indexed
            pagesToRotate = pages.map(p => p - 1).filter(i => i >= 0 && i < totalPages);
        }
        
        // Rotate pages
        for (const pageIndex of pagesToRotate) {
            const page = pdf.getPage(pageIndex);
            const currentRotation = page.getRotation().angle;
            page.setRotation(PDFDegrees(currentRotation + rotationAngle));
        }
        
        // Save to bytes
        const pdfBytes = await pdf.save();
        
        // Create blob
        const blob = new Blob([pdfBytes], { type: 'application/pdf' });
        
        // Generate filename
        const baseName = file.name.replace(/\.pdf$/i, '');
        const filename = `${baseName}_rotated.pdf`;
        
        return { blob, filename };
    }
    
    /**
     * Convert degrees to pdf-lib rotation value
     * @private
     */
    _degreesToRotation(degrees) {
        // Normalize to 0-359
        const normalized = ((degrees % 360) + 360) % 360;
        return normalized;
    }
    
    /**
     * Format file size for display
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    /**
     * Get the maximum file size for client-side processing
     */
    getMaxFileSize() {
        return this.maxFileSize;
    }
    
    /**
     * Check if a single file is under the size limit
     */
    isUnderLimit(file) {
        return file.size <= this.maxFileSize;
    }
}


// Export for use in other modules
window.ClientSideProcessor = ClientSideProcessor;
