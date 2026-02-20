/**
 * Batch Handler
 * 
 * Handles ZIP file upload and batch processing operations.
 * Extends the standard upload workflow for batch operations.
 */

class BatchHandler {
    constructor(options = {}) {
        this.maxFileSize = options.maxFileSize || 100 * 1024 * 1024; // 100MB
        this.acceptedTypes = ['application/zip', 'application/x-zip-compressed'];
        this.acceptedExtensions = ['.zip'];
        
        // Batch-specific state
        this.currentOperation = 'compress';
        this.operationOptions = {};
    }
    
    /**
     * Check if a file is a valid ZIP file
     */
    isValidZipFile(file) {
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        const validMime = this.acceptedTypes.includes(file.type);
        const validExt = this.acceptedExtensions.includes(extension);
        return validMime || validExt;
    }
    
    /**
     * Validate ZIP file
     */
    validateFile(file) {
        // Check file size
        if (file.size > this.maxFileSize) {
            return {
                valid: false,
                error: `File too large (max ${this.formatFileSize(this.maxFileSize)})`
            };
        }
        
        // Check file type
        if (!this.isValidZipFile(file)) {
            return {
                valid: false,
                error: 'Invalid file type. Only ZIP files are accepted.'
            };
        }
        
        return { valid: true };
    }
    
    /**
     * Set the current batch operation
     */
    setOperation(operation) {
        this.currentOperation = operation;
    }
    
    /**
     * Set operation-specific options
     */
    setOperationOptions(options) {
        this.operationOptions = options;
    }
    
    /**
     * Get options for the selected operation
     */
    getOperationOptions() {
        const options = {
            operation: this.currentOperation
        };
        
        // Add operation-specific options
        switch (this.currentOperation) {
            case 'compress':
                options.quality = this.operationOptions.quality || 'medium';
                break;
            case 'rotate':
                options.degrees = this.operationOptions.degrees || 90;
                break;
            case 'split':
                options.split_mode = this.operationOptions.split_mode || 'range';
                options.n_pages = this.operationOptions.n_pages || 1;
                break;
            case 'password':
                options.password = this.operationOptions.password;
                break;
        }
        
        return options;
    }
    
    /**
     * Prepare form data for batch API submission
     */
    prepareFormData(file, optionsForm) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Get operation options
        const options = this.getOperationOptions();
        
        // Add options from form if provided
        if (optionsForm) {
            // Operation
            const opSelect = optionsForm.querySelector('[name="operation"]');
            if (opSelect) {
                options.operation = opSelect.value;
            }
            
            // Quality for compress
            const qualityInput = optionsForm.querySelector('[name="quality"]');
            if (qualityInput) {
                options.quality = qualityInput.value;
            }
            
            // Degrees for rotate
            const degreesInput = optionsForm.querySelector('[name="rotate_degrees"]');
            if (degreesInput) {
                options.degrees = parseInt(degreesInput.value, 10);
            }
            
            // Password
            const passwordInput = optionsForm.querySelector('[name="batch_password"]');
            if (passwordInput && passwordInput.value) {
                options.password = passwordInput.value;
            }
        }
        
        // Append all options to form data
        formData.append('operation', options.operation);
        if (options.quality) formData.append('quality', options.quality);
        if (options.degrees) formData.append('degrees', options.degrees);
        if (options.split_mode) formData.append('split_mode', options.split_mode);
        if (options.n_pages) formData.append('n_pages', options.n_pages);
        if (options.password) formData.append('password', options.password);
        
        return formData;
    }
    
    /**
     * Handle batch result download
     */
    handleBatchResult(blob, filename) {
        // Create download link
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
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
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}


// Export for use in other modules
window.BatchHandler = BatchHandler;
