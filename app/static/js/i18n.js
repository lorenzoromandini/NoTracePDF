// NoTracePDF - Internationalization (i18n)
// Languages: Italian (default), English

const translations = {
    it: {
        tagline: "I tuoi file non lasciano mai il tuo dispositivo",
        chooseTool: "Scegli uno Strumento",
        searchPlaceholder: "Cerca strumenti...",
        foundTools: "Trovato {count} strumento",
        foundTools_plural: "Trovati {count} strumenti",
        
        // Section titles
        organizeSection: "Organizza & Modifica",
        compressSection: "Comprimi & Ottimizza",
        convertToSection: "Converti in PDF",
        convertFromSection: "Converti da PDF",
        securitySection: "Sicurezza",
        extractSection: "Estrai",
        watermarkSection: "Filigrana & Numeri di Pagina",
        pageSection: "Operazioni di Pagina",
        advancedSection: "Avanzato",
        
        // Tool names and descriptions
        merge: { title: "Unisci PDF", desc: "Combina più PDF in uno" },
        split: { title: "Dividi PDF", desc: "Estrai pagine o dividi per intervallo" },
        rotate: { title: "Ruota PDF", desc: "Ruota le pagine di 90, 180 o 270 gradi" },
        compress: { title: "Comprimi PDF", desc: "Riduci la dimensione del file con preset di qualità" },
        flatten: { title: "Appiattisci PDF", desc: "Appiattisci annotazioni e moduli" },
        removeMetadata: { title: "Rimuovi Metadati", desc: "Anonimizza le informazioni del documento" },
        imagesToPdf: { title: "Immagini in PDF", desc: "Combina immagini in un PDF" },
        wordToPdf: { title: "Word in PDF", desc: "Converti DOCX in PDF" },
        excelToPdf: { title: "Excel in PDF", desc: "Converti XLSX in PDF" },
        powerpointToPdf: { title: "PowerPoint in PDF", desc: "Converti PPTX in PDF" },
        htmlToPdf: { title: "HTML in PDF", desc: "Converti codice HTML in PDF" },
        markdownToPdf: { title: "Markdown in PDF", desc: "Converti Markdown in PDF" },
        urlToPdf: { title: "URL in PDF", desc: "Converti pagina web in PDF" },
        textToPdf: { title: "Testo in PDF", desc: "Converti testo semplice in PDF" },
        rtfToPdf: { title: "RTF in PDF", desc: "Converti documento RTF in PDF" },
        pdfToImages: { title: "PDF in Immagini", desc: "Converti pagine PDF in PNG/JPG/WebP" },
        pdfToWord: { title: "PDF in Word", desc: "Converti PDF in formato DOCX" },
        pdfToExcel: { title: "PDF in Excel", desc: "Converti PDF in formato XLSX" },
        pdfToPowerpoint: { title: "PDF in PowerPoint", desc: "Converti PDF in formato PPTX" },
        passwordAdd: { title: "Proteggi con Password", desc: "Aggiungi password e imposta permessi" },
        passwordRemove: { title: "Rimuovi Password", desc: "Sblocca un PDF protetto" },
        redact: { title: "Censura Testo", desc: "Oscura permanentemente il testo" },
        extractText: { title: "Estrai Testo", desc: "Ottieni il contenuto testuale dal PDF" },
        extractImages: { title: "Estrai Immagini", desc: "Estrai tutte le immagini dal PDF" },
        extractPages: { title: "Estrai Pagine", desc: "Estrai pagine specifiche come PDF" },
        ocrExtract: { title: "Estrai OCR", desc: "Estrai testo da PDF scansionati" },
        watermark: { title: "Aggiungi Filigrana", desc: "Aggiungi filigrana di testo o immagine" },
        pageNumbers: { title: "Aggiungi Numeri di Pagina", desc: "Aggiungi numeri di pagina al PDF" },
        cropPages: { title: "Ritaglia Pagine", desc: "Riduci i margini delle pagine" },
        scalePages: { title: "Scala Contenuto", desc: "Ridimensiona il contenuto in percentuale" },
        resizePages: { title: "Ridimensiona Pagine", desc: "Cambia la dimensione della pagina" },
        batchProcess: { title: "Elaborazione Batch", desc: "Elabora più file tramite ZIP" },
        compare: { title: "Confronta PDF", desc: "Evidenzia le differenze tra PDF" },
        
        // Footer
        footerText: "Nessuna persistenza. Nessun tracciamento. 100% privato.",
        footerSubtitle: "Tutti i file vengono elaborati in memoria e cancellati definitivamente dopo il download.",
        
        // Modal
        dragDrop: "Trascina i file qui",
        orClickToBrowse: "o clicca per sfogliare",
        selectedFiles: "File Selezionati",
        process: "Elabora",
        download: "Scarica",
        processAnother: "Elabora un altro file",
        processingComplete: "Elaborazione completata!",
        filesDeleted: "I tuoi file sono stati cancellati definitivamente dal server.",
        extractedText: "Testo Estratto",
        copyText: "Copia Testo",
        copied: "Copiato!",
        
        // Upload
        previous: "Precedente",
        next: "Successivo",
        close: "Chiudi",
        
        // Errors
        error: "Si è verificato un errore"
    },
    en: {
        tagline: "Your files never leave your device",
        chooseTool: "Choose a Tool",
        searchPlaceholder: "Search tools...",
        foundTools: "Found {count} tool",
        foundTools_plural: "Found {count} tools",
        
        // Section titles
        organizeSection: "Organize & Modify",
        compressSection: "Compress & Optimize",
        convertToSection: "Convert to PDF",
        convertFromSection: "Convert from PDF",
        securitySection: "Security",
        extractSection: "Extract",
        watermarkSection: "Watermark & Page Numbers",
        pageSection: "Page Operations",
        advancedSection: "Advanced",
        
        // Tool names and descriptions
        merge: { title: "Merge PDF", desc: "Combine multiple PDFs into one" },
        split: { title: "Split PDF", desc: "Extract pages or split by range" },
        rotate: { title: "Rotate PDF", desc: "Rotate pages 90, 180, or 270 degrees" },
        compress: { title: "Compress PDF", desc: "Reduce file size with quality presets" },
        flatten: { title: "Flatten PDF", desc: "Flatten annotations and forms" },
        removeMetadata: { title: "Remove Metadata", desc: "Anonymize document info" },
        imagesToPdf: { title: "Images to PDF", desc: "Combine images into a PDF" },
        wordToPdf: { title: "Word to PDF", desc: "Convert DOCX to PDF" },
        excelToPdf: { title: "Excel to PDF", desc: "Convert XLSX to PDF" },
        powerpointToPdf: { title: "PowerPoint to PDF", desc: "Convert PPTX to PDF" },
        htmlToPdf: { title: "HTML to PDF", desc: "Convert HTML code to PDF" },
        markdownToPdf: { title: "Markdown to PDF", desc: "Convert Markdown to PDF" },
        urlToPdf: { title: "URL to PDF", desc: "Convert web page to PDF" },
        textToPdf: { title: "Text to PDF", desc: "Convert plain text to PDF" },
        rtfToPdf: { title: "RTF to PDF", desc: "Convert RTF document to PDF" },
        pdfToImages: { title: "PDF to Images", desc: "Convert PDF pages to PNG/JPG/WebP" },
        pdfToWord: { title: "PDF to Word", desc: "Convert PDF to DOCX format" },
        pdfToExcel: { title: "PDF to Excel", desc: "Convert PDF to XLSX format" },
        pdfToPowerpoint: { title: "PDF to PowerPoint", desc: "Convert PDF to PPTX format" },
        passwordAdd: { title: "Password Protect", desc: "Add password and set permissions" },
        passwordRemove: { title: "Remove Password", desc: "Unlock a protected PDF" },
        redact: { title: "Redact Text", desc: "Permanently black out text" },
        extractText: { title: "Extract Text", desc: "Get text content from PDF" },
        extractImages: { title: "Extract Images", desc: "Get all images from PDF" },
        extractPages: { title: "Extract Pages", desc: "Extract specific pages as PDFs" },
        ocrExtract: { title: "OCR Extract", desc: "Extract text from scanned PDFs" },
        watermark: { title: "Add Watermark", desc: "Add text or image watermark" },
        pageNumbers: { title: "Add Page Numbers", desc: "Add page numbers to PDF" },
        cropPages: { title: "Crop Pages", desc: "Trim page margins" },
        scalePages: { title: "Scale Content", desc: "Resize page content by percentage" },
        resizePages: { title: "Resize Pages", desc: "Change page canvas size" },
        batchProcess: { title: "Batch Process", desc: "Process multiple files via ZIP" },
        compare: { title: "Compare PDFs", desc: "Highlight differences between PDFs" },
        
        // Footer
        footerText: "Zero persistence. Zero tracking. 100% private.",
        footerSubtitle: "All files are processed in memory and permanently deleted after download.",
        
        // Modal
        dragDrop: "Drag and drop files here",
        orClickToBrowse: "or click to browse",
        selectedFiles: "Selected Files",
        process: "Process",
        download: "Download",
        processAnother: "Process Another File",
        processingComplete: "Processing complete!",
        filesDeleted: "Your files have been permanently deleted from the server.",
        extractedText: "Extracted Text",
        copyText: "Copy Text",
        copied: "Copied!",
        
        // Upload
        previous: "Previous",
        next: "Next",
        close: "Close",
        
        // Errors
        error: "An error occurred"
    }
};

// Tool to key mapping (tool ID -> translation key)
const toolKeyMap = {
    "merge": "merge",
    "split": "split",
    "rotate": "rotate",
    "compress": "compress",
    "flatten": "flatten",
    "remove-metadata": "removeMetadata",
    "images-to-pdf": "imagesToPdf",
    "word-to-pdf": "wordToPdf",
    "excel-to-pdf": "excelToPdf",
    "powerpoint-to-pdf": "powerpointToPdf",
    "html-to-pdf": "htmlToPdf",
    "markdown-to-pdf": "markdownToPdf",
    "url-to-pdf": "urlToPdf",
    "text-to-pdf": "textToPdf",
    "rtf-to-pdf": "rtfToPdf",
    "pdf-to-images": "pdfToImages",
    "pdf-to-word": "pdfToWord",
    "pdf-to-excel": "pdfToExcel",
    "pdf-to-powerpoint": "pdfToPowerpoint",
    "password-add": "passwordAdd",
    "password-remove": "passwordRemove",
    "redact": "redact",
    "extract-text": "extractText",
    "extract-images": "extractImages",
    "extract-pages": "extractPages",
    "ocr-extract": "ocrExtract",
    "watermark": "watermark",
    "page-numbers": "pageNumbers",
    "crop-pages": "cropPages",
    "scale-pages": "scalePages",
    "resize-pages": "resizePages",
    "batch-process": "batchProcess",
    "compare": "compare"
};

// Section key mapping
const sectionKeyMap = {
    "organize": "organizeSection",
    "compress": "compressSection",
    "convert-to": "convertToSection",
    "convert-from": "convertFromSection",
    "security": "securitySection",
    "extract": "extractSection",
    "watermark": "watermarkSection",
    "page": "pageSection",
    "advanced": "advancedSection"
};

class I18n {
    constructor() {
        this.currentLang = document.body.dataset.lang || 'it';
        this.translations = translations;
    }
    
    t(key, params = {}) {
        const langData = this.translations[this.currentLang];
        let text = langData[key] || key;
        
        // Replace placeholders like {count}
        Object.keys(params).forEach(param => {
            text = text.replace(`{${param}}`, params[param]);
        });
        
        return text;
    }
    
    getToolTranslation(toolId, type = 'title') {
        const key = toolKeyMap[toolId];
        if (!key) return null;
        
        const langData = this.translations[this.currentLang];
        const toolData = langData[key];
        
        if (!toolData) return null;
        
        return toolData[type];
    }
    
    getSectionTranslation(sectionId) {
        const key = sectionKeyMap[sectionId];
        if (!key) return null;
        
        return this.t(key);
    }
    
    setLanguage(lang) {
        if (this.translations[lang]) {
            this.currentLang = lang;
            document.body.dataset.lang = lang;
            localStorage.setItem('lang', lang);
            this.updatePageTranslations();
        }
    }
    
    toggleLanguage() {
        const newLang = this.currentLang === 'it' ? 'en' : 'it';
        this.setLanguage(newLang);
        return newLang;
    }
    
    getLanguage() {
        return this.currentLang;
    }
    
    updatePageTranslations() {
        // Update tagline
        const tagline = document.querySelector('.tagline');
        if (tagline) tagline.textContent = this.t('tagline');
        
        // Update section titles
        document.querySelectorAll('.tool-section-title').forEach(el => {
            const section = el.closest('.tool-section');
            const sectionId = section?.dataset.section;
            const translation = this.getSectionTranslation(sectionId);
            if (translation) el.textContent = translation;
        });
        
        // Update search placeholder
        const searchInput = document.getElementById('tool-search');
        if (searchInput) searchInput.placeholder = this.t('searchPlaceholder');
        
        // Update section title
        const sectionTitle = document.querySelector('.section-title');
        if (sectionTitle) sectionTitle.textContent = this.t('chooseTool');
        
        // Update footer
        const footerText = document.querySelector('.footer-text');
        const footerSubtitle = document.querySelector('.footer-subtitle');
        if (footerText) footerText.textContent = this.t('footerText');
        if (footerSubtitle) footerSubtitle.textContent = this.t('footerSubtitle');
        
        // Update lang toggle button
        const langLabel = document.querySelector('.lang-label');
        if (langLabel) langLabel.textContent = this.currentLang.toUpperCase();
        
        // Update all tool cards
        document.querySelectorAll('.tool-card').forEach(card => {
            const toolId = card.dataset.tool;
            const titleEl = card.querySelector('.tool-title');
            const descEl = card.querySelector('.tool-description');
            
            if (titleEl && descEl) {
                const title = this.getToolTranslation(toolId, 'title');
                const desc = this.getToolTranslation(toolId, 'desc');
                
                if (this.currentLang === 'en' && title) {
                    titleEl.textContent = title;
                    descEl.textContent = desc;
                } else if (this.currentLang === 'it') {
                    // Check for Italian data attributes first
                    const itTitle = card.dataset.titleIt;
                    const itDesc = card.dataset.descIt;
                    if (itTitle) titleEl.textContent = itTitle;
                    if (itDesc) descEl.textContent = itDesc;
                }
            }
        });
    }
    
    init() {
        // Load saved language preference
        const savedLang = localStorage.getItem('lang');
        if (savedLang && this.translations[savedLang]) {
            this.currentLang = savedLang;
            document.body.dataset.lang = savedLang;
        }
        
        this.updatePageTranslations();
    }
}

// Create global instance
window.i18n = new I18n();
