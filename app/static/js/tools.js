/**
 * Tool Configurations
 * 
 * Defines the options and parameters for each PDF/image tool.
 */

const TOOL_CONFIG = {
    // PDF Operations
    merge: {
        name: 'Merge PDF',
        endpoint: '/api/v1/pdf/merge',
        multipleFiles: true,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: null, // No additional options for merge
    },

    split: {
        name: 'Split PDF',
        endpoint: '/api/v1/pdf/split',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'mode',
                label: 'Split Mode',
                type: 'select',
                default: 'range',
                options: [
                    { value: 'range', label: 'Extract page range' },
                    { value: 'every_n', label: 'Split every N pages' },
                    { value: 'specific', label: 'Extract specific pages' }
                ]
            },
            {
                key: 'start',
                label: 'Start Page',
                type: 'number',
                default: 1,
                min: 1,
                showIf: { mode: 'range' }
            },
            {
                key: 'end',
                label: 'End Page',
                type: 'number',
                default: 1,
                min: 1,
                showIf: { mode: 'range' }
            },
            {
                key: 'n_pages',
                label: 'Pages per split',
                type: 'number',
                default: 1,
                min: 1,
                showIf: { mode: 'every_n' }
            },
            {
                key: 'pages',
                label: 'Page numbers',
                type: 'text',
                placeholder: 'e.g., 1, 3, 5-7',
                hint: 'Comma-separated page numbers or ranges (1-indexed)',
                showIf: { mode: 'specific' }
            }
        ]
    },

    rotate: {
        name: 'Rotate PDF',
        endpoint: '/api/v1/pdf/rotate',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'pages',
                label: 'Pages to rotate',
                type: 'select',
                default: 'all',
                options: [
                    { value: 'all', label: 'All pages' },
                    { value: 'specific', label: 'Specific pages' }
                ]
            },
            {
                key: 'pageNumbers',
                label: 'Page numbers',
                type: 'text',
                placeholder: 'e.g., 1, 3, 5',
                hint: 'Comma-separated page numbers (1-indexed)',
                showIf: { pages: 'specific' }
            },
            {
                key: 'degrees',
                label: 'Rotation angle',
                type: 'radio',
                default: '90',
                options: [
                    { value: '90', label: '90° clockwise' },
                    { value: '180', label: '180°' },
                    { value: '270', label: '270° clockwise' }
                ]
            }
        ]
    },

    compress: {
        name: 'Compress PDF',
        endpoint: '/api/v1/pdf/compress',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'quality',
                label: 'Quality preset',
                type: 'radio',
                default: 'medium',
                options: [
                    { value: 'low', label: 'Low (smallest file, 72 DPI)' },
                    { value: 'medium', label: 'Medium (balanced, 150 DPI)' },
                    { value: 'high', label: 'High (best quality, 300 DPI)' }
                ]
            }
        ]
    },

    'password-add': {
        name: 'Password Protect',
        endpoint: '/api/v1/pdf/password/add',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'password',
                label: 'Password',
                type: 'password',
                required: true,
                placeholder: 'Enter a strong password'
            },
            {
                key: 'permissions',
                label: 'Allowed permissions',
                type: 'checkbox',
                options: [
                    { value: 'print', label: 'Print' },
                    { value: 'copy', label: 'Copy content' },
                    { value: 'edit', label: 'Edit' },
                    { value: 'annotate', label: 'Add annotations' },
                    { value: 'fill_forms', label: 'Fill forms' },
                    { value: 'extract', label: 'Extract content' }
                ]
            }
        ]
    },

    'password-remove': {
        name: 'Remove Password',
        endpoint: '/api/v1/pdf/password/remove',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'password',
                label: 'Current Password',
                type: 'password',
                required: true,
                placeholder: 'Enter the current password'
            }
        ]
    },

    watermark: {
        name: 'Add Watermark',
        endpoint: '/api/v1/pdf/watermark/text',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'watermarkType',
                label: 'Watermark type',
                type: 'radio',
                default: 'text',
                options: [
                    { value: 'text', label: 'Text watermark' },
                    { value: 'image', label: 'Image watermark' }
                ]
            },
            {
                key: 'text',
                label: 'Watermark text',
                type: 'text',
                required: true,
                placeholder: 'e.g., CONFIDENTIAL',
                showIf: { watermarkType: 'text' }
            },
            {
                key: 'fontSize',
                label: 'Font size',
                type: 'number',
                default: 48,
                min: 12,
                max: 200,
                showIf: { watermarkType: 'text' }
            },
            {
                key: 'color',
                label: 'Color',
                type: 'color',
                default: '#808080',
                showIf: { watermarkType: 'text' }
            },
            {
                key: 'imageFile',
                label: 'Watermark image',
                type: 'file',
                accepts: ['.png', '.jpg', '.jpeg', '.webp'],
                acceptMime: 'image/png,image/jpeg,image/webp',
                showIf: { watermarkType: 'image' }
            },
            {
                key: 'scale',
                label: 'Image scale',
                type: 'range',
                default: 0.5,
                min: 0.1,
                max: 1.0,
                step: 0.1,
                showIf: { watermarkType: 'image' }
            },
            {
                key: 'opacity',
                label: 'Opacity',
                type: 'range',
                default: 0.3,
                min: 0.1,
                max: 1.0,
                step: 0.1
            },
            {
                key: 'position',
                label: 'Position',
                type: 'select',
                default: 'diagonal',
                options: [
                    { value: 'center', label: 'Center' },
                    { value: 'diagonal', label: 'Diagonal' },
                    { value: 'top-left', label: 'Top Left' },
                    { value: 'top-right', label: 'Top Right' },
                    { value: 'bottom-left', label: 'Bottom Left' },
                    { value: 'bottom-right', label: 'Bottom Right' }
                ]
            },
            {
                key: 'pages',
                label: 'Apply to',
                type: 'select',
                default: 'all',
                options: [
                    { value: 'all', label: 'All pages' },
                    { value: 'first', label: 'First page only' },
                    { value: 'last', label: 'Last page only' }
                ]
            }
        ]
    },

    'extract-text': {
        name: 'Extract Text',
        endpoint: '/api/v1/pdf/extract/text',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'pages',
                label: 'Pages to extract (optional)',
                type: 'text',
                placeholder: 'e.g., 1, 3, 5-7',
                hint: 'Leave empty for all pages'
            }
        ],
        returnsText: true
    },

    'extract-images': {
        name: 'Extract Images',
        endpoint: '/api/v1/pdf/extract/images',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'format',
                label: 'Output format',
                type: 'select',
                default: 'original',
                options: [
                    { value: 'original', label: 'Original format' },
                    { value: 'png', label: 'PNG' },
                    { value: 'jpg', label: 'JPG' },
                    { value: 'webp', label: 'WebP' }
                ]
            },
            {
                key: 'pages',
                label: 'Pages to extract from (optional)',
                type: 'text',
                placeholder: 'e.g., 1, 3, 5',
                hint: 'Leave empty for all pages'
            }
        ]
    },

    'extract-pages': {
        name: 'Extract Pages',
        endpoint: '/api/v1/pdf/extract/pages',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'pages',
                label: 'Pages to extract',
                type: 'text',
                required: true,
                placeholder: 'e.g., 1, 3, 5-7',
                hint: 'Comma-separated page numbers or ranges (1-indexed)'
            }
        ]
    },

    'pdf-to-images': {
        name: 'PDF to Images',
        endpoint: '/api/v1/image/pdf-to-images',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'format',
                label: 'Output format',
                type: 'radio',
                default: 'png',
                options: [
                    { value: 'png', label: 'PNG (lossless)' },
                    { value: 'jpg', label: 'JPG (smaller)' },
                    { value: 'webp', label: 'WebP (modern)' }
                ]
            },
            {
                key: 'pages',
                label: 'Pages to convert',
                type: 'select',
                default: 'all',
                options: [
                    { value: 'all', label: 'All pages' },
                    { value: 'first', label: 'First page only' }
                ]
            },
            {
                key: 'dpi',
                label: 'Resolution (DPI)',
                type: 'select',
                default: '200',
                options: [
                    { value: '72', label: '72 DPI (low)' },
                    { value: '150', label: '150 DPI (medium)' },
                    { value: '200', label: '200 DPI (default)' },
                    { value: '300', label: '300 DPI (high)' }
                ]
            },
            {
                key: 'quality',
                label: 'Quality (JPG/WebP only)',
                type: 'range',
                default: 85,
                min: 1,
                max: 100,
                step: 5
            }
        ]
    },

    'images-to-pdf': {
        name: 'Images to PDF',
        endpoint: '/api/v1/image/images-to-pdf',
        multipleFiles: true,
        accepts: ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'],
        acceptMime: 'image/png,image/jpeg,image/webp,image/gif,image/bmp',
        options: [
            {
                key: 'page_size',
                label: 'Page size',
                type: 'select',
                default: 'a4',
                options: [
                    { value: 'a4', label: 'A4 (210×297mm)' },
                    { value: 'letter', label: 'US Letter (8.5×11in)' },
                    { value: 'fit', label: 'Fit to image' },
                    { value: 'original', label: 'Original image size' }
                ]
            },
            {
                key: 'fit_to_page',
                label: 'Scale images to fit page',
                type: 'checkbox',
                options: [
                    { value: 'fit', label: 'Scale to fit page' }
                ]
            }
        ]
    },

    // =====================================================
    // Phase 2: Extended PDF Operations
    // =====================================================

    'crop-pages': {
        name: 'Crop Pages',
        endpoint: '/api/v1/pdf/crop',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'left',
                label: 'Left margin (points)',
                type: 'number',
                default: 0,
                min: 0,
                hint: '1 point = 1/72 inch'
            },
            {
                key: 'right',
                label: 'Right margin (points)',
                type: 'number',
                default: 0,
                min: 0
            },
            {
                key: 'top',
                label: 'Top margin (points)',
                type: 'number',
                default: 0,
                min: 0
            },
            {
                key: 'bottom',
                label: 'Bottom margin (points)',
                type: 'number',
                default: 0,
                min: 0
            },
            {
                key: 'pages',
                label: 'Pages to crop (optional)',
                type: 'text',
                placeholder: 'e.g., 1, 3, 5-7',
                hint: 'Leave empty for all pages'
            }
        ]
    },

    'scale-pages': {
        name: 'Scale Content',
        endpoint: '/api/v1/pdf/scale',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'scale',
                label: 'Scale factor',
                type: 'number',
                default: 1.0,
                min: 0.1,
                max: 10,
                step: 0.1,
                hint: 'e.g., 0.5 = 50%, 2.0 = 200%'
            },
            {
                key: 'pages',
                label: 'Pages to scale (optional)',
                type: 'text',
                placeholder: 'e.g., 1, 3, 5-7',
                hint: 'Leave empty for all pages'
            }
        ]
    },

    'resize-pages': {
        name: 'Resize Pages',
        endpoint: '/api/v1/pdf/resize',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'width',
                label: 'Width (points)',
                type: 'number',
                default: 595.28,
                min: 1,
                hint: 'A4=595.28, Letter=612'
            },
            {
                key: 'height',
                label: 'Height (points)',
                type: 'number',
                default: 841.89,
                min: 1,
                hint: 'A4=841.89, Letter=792'
            },
            {
                key: 'pages',
                label: 'Pages to resize (optional)',
                type: 'text',
                placeholder: 'e.g., 1, 3, 5-7',
                hint: 'Leave empty for all pages'
            }
        ]
    },

    'page-numbers': {
        name: 'Add Page Numbers',
        endpoint: '/api/v1/pdf/page-numbers',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'format',
                label: 'Format',
                type: 'text',
                default: 'Page {page} of {total}',
                hint: 'Use {page} and {total} placeholders'
            },
            {
                key: 'position',
                label: 'Position',
                type: 'select',
                default: 'bottom-center',
                options: [
                    { value: 'bottom-center', label: 'Bottom Center' },
                    { value: 'bottom-left', label: 'Bottom Left' },
                    { value: 'bottom-right', label: 'Bottom Right' },
                    { value: 'top-center', label: 'Top Center' },
                    { value: 'top-left', label: 'Top Left' },
                    { value: 'top-right', label: 'Top Right' }
                ]
            },
            {
                key: 'font_size',
                label: 'Font size',
                type: 'number',
                default: 12,
                min: 6,
                max: 72
            },
            {
                key: 'color',
                label: 'Color',
                type: 'color',
                default: '#000000'
            },
            {
                key: 'start_at',
                label: 'Start at page',
                type: 'number',
                default: 1,
                min: 1
            }
        ]
    },

    'flatten': {
        name: 'Flatten PDF',
        endpoint: '/api/v1/pdf/flatten',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: null
    },

    'remove-metadata': {
        name: 'Remove Metadata',
        endpoint: '/api/v1/pdf/metadata/remove',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'fields',
                label: 'Fields to remove',
                type: 'checkbox',
                options: [
                    { value: 'title', label: 'Title' },
                    { value: 'author', label: 'Author' },
                    { value: 'subject', label: 'Subject' },
                    { value: 'keywords', label: 'Keywords' },
                    { value: 'creator', label: 'Creator' },
                    { value: 'producer', label: 'Producer' },
                    { value: 'creationDate', label: 'Creation Date' },
                    { value: 'modDate', label: 'Modification Date' }
                ]
            }
        ]
    },

    'compare': {
        name: 'Compare PDFs',
        endpoint: '/api/v1/pdf/compare',
        multipleFiles: true,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'highlight_add',
                label: 'Additions color',
                type: 'color',
                default: '#00FF00'
            },
            {
                key: 'highlight_del',
                label: 'Deletions color',
                type: 'color',
                default: '#FF0000'
            },
            {
                key: 'include_summary',
                label: 'Include summary page',
                type: 'checkbox',
                options: [
                    { value: 'true', label: 'Yes' }
                ]
            },
            {
                key: 'dpi',
                label: 'Comparison DPI',
                type: 'select',
                default: '150',
                options: [
                    { value: '72', label: '72 DPI (fast)' },
                    { value: '150', label: '150 DPI (balanced)' },
                    { value: '300', label: '300 DPI (accurate)' }
                ]
            }
        ]
    },

    'redact': {
        name: 'Redact Text',
        endpoint: '/api/v1/pdf/redact',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: [
            {
                key: 'patterns',
                label: 'Text to redact',
                type: 'text',
                required: true,
                placeholder: 'e.g., CONFIDENTIAL, SSN',
                hint: 'Comma-separated text patterns'
            },
            {
                key: 'match_exact',
                label: 'Match exact text only',
                type: 'checkbox',
                options: [
                    { value: 'true', label: 'Exact match only' }
                ]
            },
            {
                key: 'case_sensitive',
                label: 'Case sensitive',
                type: 'checkbox',
                options: [
                    { value: 'true', label: 'Case sensitive' }
                ]
            },
            {
                key: 'fill_color',
                label: 'Fill color',
                type: 'color',
                default: '#000000'
            },
            {
                key: 'pages',
                label: 'Pages to redact (optional)',
                type: 'text',
                placeholder: 'e.g., 1, 3, 5-7',
                hint: 'Leave empty for all pages'
            }
        ]
    },

    // =====================================================
    // Phase 3: Document Conversions
    // =====================================================

    // PDF to Office
    'pdf-to-word': {
        name: 'PDF to Word',
        endpoint: '/api/v1/convert/pdf-to-word',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: null
    },

    'pdf-to-excel': {
        name: 'PDF to Excel',
        endpoint: '/api/v1/convert/pdf-to-excel',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: null
    },

    'pdf-to-powerpoint': {
        name: 'PDF to PowerPoint',
        endpoint: '/api/v1/convert/pdf-to-powerpoint',
        multipleFiles: false,
        accepts: ['.pdf'],
        acceptMime: 'application/pdf',
        options: null
    },

    // Office to PDF
    'word-to-pdf': {
        name: 'Word to PDF',
        endpoint: '/api/v1/convert/word-to-pdf',
        multipleFiles: false,
        accepts: ['.docx', '.doc'],
        acceptMime: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword',
        options: null
    },

    'excel-to-pdf': {
        name: 'Excel to PDF',
        endpoint: '/api/v1/convert/excel-to-pdf',
        multipleFiles: false,
        accepts: ['.xlsx', '.xls'],
        acceptMime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel',
        options: null
    },

    'powerpoint-to-pdf': {
        name: 'PowerPoint to PDF',
        endpoint: '/api/v1/convert/powerpoint-to-pdf',
        multipleFiles: false,
        accepts: ['.pptx', '.ppt'],
        acceptMime: 'application/vnd.openxmlformats-officedocument.presentationml.presentation,application/vnd.ms-powerpoint',
        options: null
    },

    // Web content to PDF
    'html-to-pdf': {
        name: 'HTML to PDF',
        endpoint: '/api/v1/convert/html-to-pdf',
        multipleFiles: false,
        accepts: ['.html', '.htm'],
        acceptMime: 'text/html',
        options: [
            {
                key: 'html',
                label: 'HTML Content',
                type: 'textarea',
                required: true,
                placeholder: '<html>...</html>',
                hint: 'Paste HTML code or upload an HTML file'
            },
            {
                key: 'base_url',
                label: 'Base URL (optional)',
                type: 'text',
                placeholder: 'https://example.com',
                hint: 'For resolving relative URLs'
            }
        ],
        acceptsText: true
    },

    'markdown-to-pdf': {
        name: 'Markdown to PDF',
        endpoint: '/api/v1/convert/markdown-to-pdf',
        multipleFiles: false,
        accepts: ['.md', '.markdown'],
        acceptMime: 'text/markdown',
        options: [
            {
                key: 'markdown',
                label: 'Markdown Content',
                type: 'textarea',
                required: true,
                placeholder: '# Heading\n\nYour content here...',
                hint: 'Paste Markdown code or upload a .md file'
            }
        ],
        acceptsText: true
    },

    'url-to-pdf': {
        name: 'URL to PDF',
        endpoint: '/api/v1/convert/url-to-pdf',
        multipleFiles: false,
        accepts: [],
        acceptMime: '',
        options: [
            {
                key: 'url',
                label: 'Web Page URL',
                type: 'text',
                required: true,
                placeholder: 'https://example.com',
                hint: 'Enter a public URL to convert'
            },
            {
                key: 'timeout',
                label: 'Timeout (seconds)',
                type: 'number',
                default: 30,
                min: 5,
                max: 120
            }
        ],
        noFileUpload: true
    },

    // Text/RTF to PDF
    'text-to-pdf': {
        name: 'Text to PDF',
        endpoint: '/api/v1/convert/text-to-pdf',
        multipleFiles: false,
        accepts: ['.txt'],
        acceptMime: 'text/plain',
        options: [
            {
                key: 'text',
                label: 'Text Content',
                type: 'textarea',
                placeholder: 'Paste or type your text here...',
                hint: 'Leave empty to upload a file instead'
            },
            {
                key: 'font_size',
                label: 'Font size',
                type: 'number',
                default: 12,
                min: 6,
                max: 72
            },
            {
                key: 'font_family',
                label: 'Font family',
                type: 'select',
                default: 'helv',
                options: [
                    { value: 'helv', label: 'Helvetica (sans-serif)' },
                    { value: 'cour', label: 'Courier (monospace)' },
                    { value: 'tim', label: 'Times (serif)' }
                ]
            }
        ],
        acceptsText: true
    },

    'rtf-to-pdf': {
        name: 'RTF to PDF',
        endpoint: '/api/v1/convert/rtf-to-pdf',
        multipleFiles: false,
        accepts: ['.rtf'],
        acceptMime: 'application/rtf,text/rtf',
        options: null
    }
};


/**
 * Generate HTML for tool options
 */
function generateOptionsHTML(toolId) {
    const config = TOOL_CONFIG[toolId];
    if (!config || !config.options) {
        return '';
    }

    let html = '';
    
    for (const option of config.options) {
        const showIfAttr = option.showIf 
            ? `data-showif="${option.showIf.key}=${option.showIf.value}" data-showif-value="${option.showIf.value}"`
            : '';
        const hiddenClass = option.showIf ? 'hidden' : '';

        html += `<div class="option-group ${hiddenClass}" data-option="${option.key}" ${showIfAttr}>`;
        
        // Label
        html += `<label class="option-label">${option.label}`;
        if (option.hint) {
            html += ` <span class="option-hint">(${option.hint})</span>`;
        }
        html += `</label>`;

        // Input based on type
        switch (option.type) {
            case 'text':
            case 'password':
                html += `<input type="${option.type}" 
                    class="option-input" 
                    name="${option.key}" 
                    placeholder="${option.placeholder || ''}"
                    ${option.required ? 'required' : ''}>`;
                break;

            case 'number':
                html += `<input type="number" 
                    class="option-input" 
                    name="${option.key}" 
                    value="${option.default}"
                    min="${option.min || ''}"
                    max="${option.max || ''}">`;
                break;

            case 'color':
                html += `<input type="color" 
                    class="option-input" 
                    name="${option.key}" 
                    value="${option.default}">`;
                break;

            case 'select':
                html += `<select class="option-select" name="${option.key}">`;
                for (const opt of option.options) {
                    html += `<option value="${opt.value}" ${opt.value === option.default ? 'selected' : ''}>${opt.label}</option>`;
                }
                html += `</select>`;
                break;

            case 'radio':
                html += `<div class="option-group-inline">`;
                for (const opt of option.options) {
                    html += `<label class="option-radio">
                        <input type="radio" name="${option.key}" value="${opt.value}" 
                            ${opt.value === option.default ? 'checked' : ''}>
                        ${opt.label}
                    </label>`;
                }
                html += `</div>`;
                break;

            case 'checkbox':
                html += `<div class="option-group-inline">`;
                for (const opt of option.options) {
                    html += `<label class="option-checkbox">
                        <input type="checkbox" name="${option.key}" value="${opt.value}">
                        ${opt.label}
                    </label>`;
                }
                html += `</div>`;
                break;

            case 'range':
                html += `<div class="range-container">
                    <input type="range" class="range-input" name="${option.key}"
                        value="${option.default}" min="${option.min}" max="${option.max}" step="${option.step || 1}"
                        oninput="this.nextElementSibling.textContent = this.value">
                    <span class="range-value">${option.default}</span>
                </div>`;
                break;

            case 'file':
                html += `<input type="file" class="option-input" name="${option.key}"
                    accept="${option.acceptMime || ''}">`;
                break;

            case 'textarea':
                html += `<textarea class="option-textarea" name="${option.key}"
                    rows="6"
                    placeholder="${option.placeholder || ''}"
                    ${option.required ? 'required' : ''}></textarea>`;
                if (option.hint) {
                    html += `<span class="option-hint">${option.hint}</span>`;
                }
                break;
        }

        html += `</div>`;
    }

    return html;
}


/**
 * Parse page input string to array
 * Examples: "1, 3, 5-7" -> [1, 3, 5, 6, 7]
 */
function parsePageInput(input) {
    if (!input || !input.trim()) return null;
    
    const pages = new Set();
    const parts = input.split(',').map(s => s.trim());
    
    for (const part of parts) {
        if (part.includes('-')) {
            const [start, end] = part.split('-').map(n => parseInt(n.trim(), 10));
            if (!isNaN(start) && !isNaN(end)) {
                for (let i = start; i <= end; i++) {
                    pages.add(i);
                }
            }
        } else {
            const num = parseInt(part, 10);
            if (!isNaN(num)) {
                pages.add(num);
            }
        }
    }
    
    return Array.from(pages).sort((a, b) => a - b);
}


/**
 * Collect form data for API submission
 */
function collectFormData(toolId, files, optionsForm) {
    const config = TOOL_CONFIG[toolId];
    const formData = new FormData();
    
    // Add files - special handling for different tools
    if (config.noFileUpload) {
        // URL to PDF and similar tools don't need file upload
        // Files array will be empty
    } else if (toolId === 'compare') {
        // Compare needs two files: file1 and file2
        if (files.length >= 2) {
            formData.append('file1', files[0]);
            formData.append('file2', files[1]);
        } else {
            // Error case handled elsewhere
            formData.append('file1', files[0]);
        }
    } else if (config.multipleFiles) {
        for (const file of files) {
            formData.append('files', file);
        }
    } else if (files && files.length > 0) {
        formData.append('file', files[0]);
    }
    
    // Collect options
    if (optionsForm && config.options) {
        for (const option of config.options) {
            const input = optionsForm.querySelector(`[name="${option.key}"]`);
            if (!input) continue;

            // Skip if this option is hidden due to showIf
            const group = input.closest('.option-group');
            if (group && group.classList.contains('hidden')) {
                continue;
            }
            
            switch (option.type) {
                case 'checkbox':
                    const checkboxes = optionsForm.querySelectorAll(`[name="${option.key}"]:checked`);
                    if (checkboxes.length > 0) {
                        const values = Array.from(checkboxes).map(cb => cb.value);
                        formData.append(option.key, JSON.stringify(values));
                    }
                    break;
                    
                case 'radio':
                    const radio = optionsForm.querySelector(`[name="${option.key}"]:checked`);
                    if (radio) {
                        formData.append(option.key, radio.value);
                    }
                    break;

                case 'textarea':
                case 'text':
                    // Special handling for page inputs
                    if (option.key === 'pages' || option.key === 'pageNumbers') {
                        const parsed = parsePageInput(input.value);
                        if (parsed) {
                            formData.append(option.key, JSON.stringify(parsed));
                        }
                    } else if (option.key === 'patterns') {
                        // Special handling for redact patterns - parse comma-separated
                        const patterns = input.value.split(',').map(s => s.trim()).filter(s => s);
                        if (patterns.length > 0) {
                            formData.append(option.key, JSON.stringify(patterns));
                        }
                    } else {
                        // For text/textarea fields, only add if not empty
                        if (input.value && input.value.trim()) {
                            formData.append(option.key, input.value);
                        }
                    }
                    break;

                case 'file':
                    if (input.files && input.files[0]) {
                        formData.append(option.key === 'imageFile' ? 'image' : option.key, input.files[0]);
                    }
                    break;
                    
                default:
                    if (input.value) {
                        formData.append(option.key, input.value);
                    }
            }
        }
    }
    
    return formData;
}


// Export for use in other modules
window.TOOL_CONFIG = TOOL_CONFIG;
window.generateOptionsHTML = generateOptionsHTML;
window.collectFormData = collectFormData;
window.parsePageInput = parsePageInput;
