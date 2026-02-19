/**
 * Drag and Drop File Upload Handler
 * 
 * Handles file selection via drag-and-drop or click-to-browse.
 * Validates file types and sizes, displays file list with removal.
 */

class UploadHandler {
    constructor(options = {}) {
        this.uploadZone = options.uploadZone;
        this.fileInput = options.fileInput;
        this.fileListContainer = options.fileListContainer;
        this.filesContainer = options.filesContainer;
        this.onFilesChange = options.onFilesChange || (() => {});
        
        this.maxFileSize = options.maxFileSize || 100 * 1024 * 1024; // 100MB default
        this.acceptedTypes = options.acceptedTypes || [];
        this.acceptedExtensions = options.acceptedExtensions || [];
        this.multiple = options.multiple || false;
        
        this.files = [];
        
        this.init();
    }

    init() {
        if (!this.uploadZone || !this.fileInput) {
            console.error('UploadHandler: Missing required elements');
            return;
        }

        // Drag and drop events
        this.uploadZone.addEventListener('dragenter', (e) => this.handleDragEnter(e));
        this.uploadZone.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadZone.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Click to open file browser
        this.uploadZone.addEventListener('click', () => this.fileInput.click());
        
        // File input change
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Prevent default drag behaviors on document
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });
    }

    handleDragEnter(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadZone.classList.add('drag-over');
    }

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadZone.classList.add('drag-over');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Only remove class if leaving the zone entirely
        const rect = this.uploadZone.getBoundingClientRect();
        if (e.clientX < rect.left || e.clientX >= rect.right ||
            e.clientY < rect.top || e.clientY >= rect.bottom) {
            this.uploadZone.classList.remove('drag-over');
        }
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadZone.classList.remove('drag-over');
        
        const droppedFiles = e.dataTransfer.files;
        this.processFiles(droppedFiles);
    }

    handleFileSelect(e) {
        const selectedFiles = e.target.files;
        this.processFiles(selectedFiles);
        
        // Reset input so same file can be selected again
        e.target.value = '';
    }

    processFiles(fileList) {
        const errors = [];
        
        for (const file of fileList) {
            // Validate file type
            const validation = this.validateFile(file);
            if (!validation.valid) {
                errors.push({ file: file.name, error: validation.error });
                continue;
            }
            
            // For single file mode, replace existing
            if (!this.multiple) {
                this.files = [file];
            } else {
                // Check for duplicates
                if (!this.files.some(f => f.name === file.name && f.size === file.size)) {
                    this.files.push(file);
                }
            }
        }
        
        // Update UI
        this.renderFileList();
        this.onFilesChange(this.files, errors);
    }

    validateFile(file) {
        // Check file size
        if (file.size > this.maxFileSize) {
            return {
                valid: false,
                error: `File too large (max ${this.formatFileSize(this.maxFileSize)})`
            };
        }

        // Check file type/extension
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (this.acceptedExtensions.length > 0) {
            if (!this.acceptedExtensions.includes(extension)) {
                return {
                    valid: false,
                    error: `Invalid file type. Accepted: ${this.acceptedExtensions.join(', ')}`
                };
            }
        }

        if (this.acceptedTypes.length > 0) {
            const mimeMatch = this.acceptedTypes.some(type => {
                if (type.includes('*')) {
                    const baseType = type.split('/')[0];
                    return file.type.startsWith(baseType);
                }
                return file.type === type;
            });

            if (!mimeMatch && this.acceptedExtensions.length === 0) {
                return {
                    valid: false,
                    error: `Invalid file type. Accepted: ${this.acceptedTypes.join(', ')}`
                };
            }
        }

        return { valid: true };
    }

    removeFile(index) {
        this.files.splice(index, 1);
        this.renderFileList();
        this.onFilesChange(this.files, []);
    }

    clearFiles() {
        this.files = [];
        this.renderFileList();
        this.onFilesChange(this.files, []);
    }

    renderFileList() {
        if (!this.filesContainer || !this.fileListContainer) return;

        if (this.files.length === 0) {
            this.fileListContainer.classList.add('hidden');
            return;
        }

        this.fileListContainer.classList.remove('hidden');
        
        this.filesContainer.innerHTML = this.files.map((file, index) => `
            <li class="file-item">
                <div class="file-info">
                    <svg class="file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                    <span class="file-name">${this.escapeHtml(file.name)}</span>
                    <span class="file-size">${this.formatFileSize(file.size)}</span>
                </div>
                <button class="file-remove" data-index="${index}" type="button" aria-label="Remove file">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </li>
        `).join('');

        // Add remove event listeners
        this.filesContainer.querySelectorAll('.file-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const index = parseInt(btn.dataset.index, 10);
                this.removeFile(index);
            });
        });
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setAcceptedTypes(types, extensions) {
        this.acceptedTypes = types || [];
        this.acceptedExtensions = extensions || [];
    }

    setMultiple(multiple) {
        this.multiple = multiple;
        this.fileInput.multiple = multiple;
    }

    getFiles() {
        return this.files;
    }

    hasFiles() {
        return this.files.length > 0;
    }
}


// Export for use in other modules
window.UploadHandler = UploadHandler;
