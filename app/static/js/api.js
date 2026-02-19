/**
 * API Client
 * 
 * Handles communication with the backend API.
 * Provides progress tracking for uploads and error handling.
 */

class APIClient {
    constructor() {
        this.baseUrl = '/api/v1';
    }

    /**
     * Submit a job to the API with progress tracking
     */
    submitJob(endpoint, formData, onProgress) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            // Track upload progress
            xhr.upload.onprogress = (e) => {
                if (e.lengthComputable && onProgress) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    onProgress(percent, 'uploading');
                }
            };

            // Handle response
            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    const contentType = xhr.getResponseHeader('Content-Type');
                    
                    // Check if response is a file download
                    if (contentType && (
                        contentType.includes('application/pdf') ||
                        contentType.includes('application/zip') ||
                        contentType.includes('image/')
                    )) {
                        const blob = xhr.response;
                        const filename = this.extractFilename(xhr);
                        resolve({
                            success: true,
                            type: 'file',
                            blob: blob,
                            filename: filename,
                            contentType: contentType
                        });
                    } else if (contentType && contentType.includes('application/json')) {
                        // JSON response (e.g., text extraction)
                        try {
                            const data = JSON.parse(xhr.responseText);
                            resolve({
                                success: true,
                                type: 'json',
                                data: data
                            });
                        } catch (e) {
                            reject(new Error('Invalid JSON response'));
                        }
                    } else {
                        // Unknown response type - try as file
                        const blob = xhr.response;
                        const filename = this.extractFilename(xhr);
                        resolve({
                            success: true,
                            type: 'file',
                            blob: blob,
                            filename: filename,
                            contentType: contentType
                        });
                    }
                } else {
                    // Error response
                    try {
                        const error = JSON.parse(xhr.responseText);
                        reject(new Error(error.detail || `Server error: ${xhr.status}`));
                    } catch (e) {
                        reject(new Error(`Server error: ${xhr.status}`));
                    }
                }
            };

            xhr.onerror = () => {
                reject(new Error('Network error. Please check your connection.'));
            };

            xhr.ontimeout = () => {
                reject(new Error('Request timed out. Please try again.'));
            };

            xhr.onabort = () => {
                reject(new Error('Request cancelled.'));
            };

            // Open and send request
            xhr.open('POST', endpoint);
            xhr.responseType = 'blob';
            xhr.timeout = 120000; // 2 minute timeout
            
            if (onProgress) {
                onProgress(0, 'connecting');
            }
            
            xhr.send(formData);
        });
    }

    /**
     * Extract filename from Content-Disposition header
     */
    extractFilename(xhr) {
        const disposition = xhr.getResponseHeader('Content-Disposition');
        if (disposition) {
            const match = disposition.match(/filename[*]?=["']?(?:UTF-\d["']*)?([^"';\s]+)["']?/i);
            if (match && match[1]) {
                return decodeURIComponent(match[1]);
            }
        }
        return 'download';
    }

    /**
     * Trigger file download from blob
     */
    downloadFile(blob, filename) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Clean up blob URL after a delay
        setTimeout(() => {
            URL.revokeObjectURL(url);
        }, 1000);
    }

    /**
     * Health check
     */
    async healthCheck() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            return data.status === 'ok';
        } catch (e) {
            return false;
        }
    }
}


// Export for use in other modules
window.APIClient = APIClient;
