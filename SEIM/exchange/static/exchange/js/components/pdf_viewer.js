/**
 * PDF Viewer using PDF.js
 * Provides in-browser PDF preview functionality
 */

class PDFViewer {
    constructor(options) {
        this.container = options.container;
        this.url = options.url;
        this.scale = options.scale || 1.5;
        this.pageNum = 1;
        this.pageRendering = false;
        this.pageNumPending = null;
        this.pdfDoc = null;
        this.canvas = null;
        this.ctx = null;
        
        this.init();
    }
    
    init() {
        // Create viewer structure
        this.createViewerStructure();
        
        // Load the PDF
        this.loadPDF();
    }
    
    createViewerStructure() {
        const viewerHTML = `
            <div class="pdf-viewer">
                <div class="pdf-controls">
                    <button id="prev" class="btn btn-secondary">
                        <i class="fas fa-chevron-left"></i> Previous
                    </button>
                    <span class="page-info">
                        Page: <span id="page_num"></span> / <span id="page_count"></span>
                    </span>
                    <button id="next" class="btn btn-secondary">
                        Next <i class="fas fa-chevron-right"></i>
                    </button>
                    <div class="zoom-controls">
                        <button id="zoom_out" class="btn btn-secondary">
                            <i class="fas fa-search-minus"></i>
                        </button>
                        <span class="zoom-level">100%</span>
                        <button id="zoom_in" class="btn btn-secondary">
                            <i class="fas fa-search-plus"></i>
                        </button>
                    </div>
                    <button id="download" class="btn btn-primary">
                        <i class="fas fa-download"></i> Download
                    </button>
                </div>
                <div class="pdf-canvas-container">
                    <canvas id="pdf-canvas"></canvas>
                </div>
                <div class="pdf-loading" style="display: none;">
                    <div class="spinner-border" role="status">
                        <span class="sr-only">Loading...</span>
                    </div>
                </div>
                <div class="pdf-error" style="display: none;">
                    <div class="alert alert-danger">
                        Error loading PDF. Please try again.
                    </div>
                </div>
            </div>
        `;
        
        this.container.innerHTML = viewerHTML;
        
        // Get references to elements
        this.canvas = document.getElementById('pdf-canvas');
        this.ctx = this.canvas.getContext('2d');
        
        // Bind events
        this.bindEvents();
    }
    
    bindEvents() {
        document.getElementById('prev').addEventListener('click', () => this.onPrevPage());
        document.getElementById('next').addEventListener('click', () => this.onNextPage());
        document.getElementById('zoom_in').addEventListener('click', () => this.onZoomIn());
        document.getElementById('zoom_out').addEventListener('click', () => this.onZoomOut());
        document.getElementById('download').addEventListener('click', () => this.onDownload());
    }
    
    loadPDF() {
        const loadingElement = this.container.querySelector('.pdf-loading');
        const errorElement = this.container.querySelector('.pdf-error');
        
        loadingElement.style.display = 'block';
        errorElement.style.display = 'none';
        
        // Asynchronously downloads PDF
        pdfjsLib.getDocument(this.url).promise.then(pdfDoc_ => {
            this.pdfDoc = pdfDoc_;
            document.getElementById('page_count').textContent = this.pdfDoc.numPages;
            
            // Initial/first page rendering
            this.renderPage(this.pageNum);
            loadingElement.style.display = 'none';
        }).catch(error => {
            console.error('Error loading PDF:', error);
            loadingElement.style.display = 'none';
            errorElement.style.display = 'block';
        });
    }
    
    renderPage(num) {
        this.pageRendering = true;
        
        // Using promise to fetch the page
        this.pdfDoc.getPage(num).then(page => {
            const viewport = page.getViewport({scale: this.scale});
            this.canvas.height = viewport.height;
            this.canvas.width = viewport.width;
            
            // Render PDF page into canvas context
            const renderContext = {
                canvasContext: this.ctx,
                viewport: viewport
            };
            
            const renderTask = page.render(renderContext);
            
            // Wait for rendering to finish
            renderTask.promise.then(() => {
                this.pageRendering = false;
                if (this.pageNumPending !== null) {
                    // New page rendering is pending
                    this.renderPage(this.pageNumPending);
                    this.pageNumPending = null;
                }
            });
        });
        
        // Update page counters
        document.getElementById('page_num').textContent = num;
    }
    
    queueRenderPage(num) {
        if (this.pageRendering) {
            this.pageNumPending = num;
        } else {
            this.renderPage(num);
        }
    }
    
    onPrevPage() {
        if (this.pageNum <= 1) {
            return;
        }
        this.pageNum--;
        this.queueRenderPage(this.pageNum);
    }
    
    onNextPage() {
        if (this.pageNum >= this.pdfDoc.numPages) {
            return;
        }
        this.pageNum++;
        this.queueRenderPage(this.pageNum);
    }
    
    onZoomIn() {
        this.scale += 0.25;
        this.updateZoomLevel();
        this.queueRenderPage(this.pageNum);
    }
    
    onZoomOut() {
        if (this.scale <= 0.5) {
            return;
        }
        this.scale -= 0.25;
        this.updateZoomLevel();
        this.queueRenderPage(this.pageNum);
    }
    
    updateZoomLevel() {
        const zoomLevel = Math.round(this.scale * 100);
        this.container.querySelector('.zoom-level').textContent = `${zoomLevel}%`;
    }
    
    onDownload() {
        const link = document.createElement('a');
        link.href = this.url;
        link.download = this.url.split('/').pop();
        link.click();
    }
}

// Initialize PDF viewers when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const pdfContainers = document.querySelectorAll('.pdf-viewer-container');
    
    pdfContainers.forEach(container => {
        const url = container.dataset.pdfUrl;
        if (url) {
            new PDFViewer({
                container: container,
                url: url
            });
        }
    });
});

// CSS styles for the PDF viewer
const style = document.createElement('style');
style.textContent = `
    .pdf-viewer {
        width: 100%;
        min-height: 600px;
        border: 1px solid #ddd;
        background: #f5f5f5;
        position: relative;
    }
    
    .pdf-controls {
        background: #fff;
        border-bottom: 1px solid #ddd;
        padding: 10px;
        display: flex;
        align-items: center;
        gap: 15px;
        flex-wrap: wrap;
    }
    
    .page-info {
        font-weight: 500;
    }
    
    .zoom-controls {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-left: auto;
    }
    
    .zoom-level {
        font-weight: 500;
        min-width: 50px;
        text-align: center;
    }
    
    .pdf-canvas-container {
        overflow: auto;
        height: calc(100% - 60px);
        display: flex;
        justify-content: center;
        align-items: flex-start;
        padding: 20px;
    }
    
    #pdf-canvas {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        background: white;
    }
    
    .pdf-loading,
    .pdf-error {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    
    @media (max-width: 768px) {
        .pdf-controls {
            justify-content: center;
        }
        
        .zoom-controls {
            margin-left: 0;
        }
    }
`;
document.head.appendChild(style);
