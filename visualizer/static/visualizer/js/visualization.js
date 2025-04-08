// static/visualizer/js/visualization.js

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the visualization result page
    const visualizationImg = document.querySelector('.visualization img');
    if (!visualizationImg) return;

    // Add zoom functionality
    setupZoomFunctionality(visualizationImg);

    // Add element info popup functionality
    setupElementInfoPopup(visualizationImg);
});

function setupZoomFunctionality(visualizationImg) {
    let scale = 1;
    let panX = 0;
    let panY = 0;
    let isDragging = false;
    let startX, startY;
    const zoomStep = 0.2;  // Increased zoom step for better visibility
    const maxZoom = 10;    // Maximum zoom level

    // Create zoom and pan controls
    const visualizationContainer = document.querySelector('.visualization');
    const zoomControls = document.createElement('div');
    zoomControls.className = 'zoom-controls';
    zoomControls.innerHTML = `
        <div class="btn-group">
            <button id="zoom-in" class="btn btn-sm btn-outline-primary">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.5 4.5a.5.5 0 0 0-1 0v3h-3a.5.5 0 0 0 0 1h3v3a.5.5 0 0 0 1 0v-3h3a.5.5 0 0 0 0-1h-3v-3z"/>
                </svg>
                Zoom In
            </button>
            <button id="zoom-out" class="btn btn-sm btn-outline-secondary">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM4.5 7.5a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-7z"/>
                </svg>
                Zoom Out
            </button>
            <button id="reset-view" class="btn btn-sm btn-outline-dark">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
                    <path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
                </svg>
                Reset View
            </button>
        </div>
        <div class="mt-2 instructions text-muted small">
            <p>Tip: You can drag to pan the view and use mouse wheel to zoom. Click on a tag to see element details.</p>
        </div>
    `;

    // Insert zoom controls before the visualization
    visualizationContainer.insertBefore(zoomControls, visualizationContainer.firstChild);

    // Function to update the transform
    function updateTransform() {
        visualizationImg.style.transform = `scale(${scale}) translate(${panX}px, ${panY}px)`;
    }

    // Add zoom in functionality
    document.getElementById('zoom-in').addEventListener('click', function() {
        if (scale < maxZoom) {
            scale += zoomStep;
            updateTransform();
        }
    });

    // Add zoom out functionality
    document.getElementById('zoom-out').addEventListener('click', function() {
        if (scale > zoomStep) {
            scale -= zoomStep;
            updateTransform();
        }
    });

    // Add reset functionality
    document.getElementById('reset-view').addEventListener('click', function() {
        scale = 1;
        panX = 0;
        panY = 0;
        updateTransform();
    });

    // Mouse wheel zoom
    visualizationContainer.addEventListener('wheel', function(e) {
        e.preventDefault();

        // Get mouse position relative to the image
        const rect = visualizationContainer.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        // Calculate zoom change
        const delta = -Math.sign(e.deltaY) * zoomStep;
        const newScale = Math.max(zoomStep, Math.min(maxZoom, scale + delta));

        if (newScale !== scale) {
            // Calculate new pan offsets to zoom toward mouse position
            const scaleRatio = newScale / scale;
            panX = mouseX - scaleRatio * (mouseX - panX);
            panY = mouseY - scaleRatio * (mouseY - panY);

            scale = newScale;
            updateTransform();
        }
    }, { passive: false });

    // Pan with mouse drag
    visualizationContainer.addEventListener('mousedown', function(e) {
        isDragging = true;
        startX = e.clientX - panX;
        startY = e.clientY - panY;
        visualizationContainer.style.cursor = 'grabbing';
    });

    document.addEventListener('mousemove', function(e) {
        if (isDragging) {
            panX = e.clientX - startX;
            panY = e.clientY - startY;
            updateTransform();
        }
    });

    document.addEventListener('mouseup', function() {
        if (isDragging) {
            isDragging = false;
            visualizationContainer.style.cursor = 'grab';
        }
    });

    // Prevent context menu on right-click for better interaction
    visualizationContainer.addEventListener('contextmenu', function(e) {
        e.preventDefault();
    });

    // Add styles for the zoom functionality
    const style = document.createElement('style');
    style.textContent = `
        .visualization {
            overflow: hidden;
            max-height: 70vh;
            position: relative;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 1rem 0;
            cursor: grab;
        }
        .visualization img {
            transition: transform 0.05s ease-out;
            transform-origin: center center;
            display: block;
            margin: 0 auto;
        }
        .zoom-controls {
            margin-bottom: 1rem;
            text-align: center;
        }
        .instructions {
            opacity: 0.8;
        }
    `;
    document.head.appendChild(style);
}

function setupElementInfoPopup(visualizationImg) {
    // Check if element data is available
    if (typeof elementData === 'undefined') {
        console.warn('Element data not available for interactive tags');
        return;
    }

    // Create popup if it doesn't exist
    let popup = document.getElementById('elementInfoPopup');
    if (!popup) {
        popup = document.createElement('div');
        popup.id = 'elementInfoPopup';
        popup.className = 'element-info-popup';
        popup.style.display = 'none';
        document.body.appendChild(popup);

        // Add CSS for the popup
        const style = document.createElement('style');
        style.textContent = `
            .element-info-popup {
                position: absolute;
                display: none;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                z-index: 1000;
                max-width: 300px;
                font-size: 14px;
            }
            
            .element-info-popup h4 {
                margin-top: 0;
                margin-bottom: 10px;
                color: #333;
                border-bottom: 1px solid #eee;
                padding-bottom: 5px;
            }
            
            .element-info-popup p {
                margin: 5px 0;
            }
            
            .element-info-popup .close-button {
                position: absolute;
                top: 5px;
                right: 10px;
                cursor: pointer;
                font-size: 16px;
                color: #999;
            }
            
            .element-info-popup .close-button:hover {
                color: #333;
            }
            
            /* Make the visualization image clickable */
            .visualization img {
                cursor: pointer;
            }
        `;
        document.head.appendChild(style);
    }

    // Add close button to popup
    popup.innerHTML = '<span class="close-button">&times;</span><div class="popup-content"></div>';
    const closeButton = popup.querySelector('.close-button');
    const popupContent = popup.querySelector('.popup-content');

    closeButton.addEventListener('click', function() {
        popup.style.display = 'none';
    });

    // Add click handler to the visualization image
    visualizationImg.addEventListener('click', function(e) {
        // Don't show popup during drag operations
        if (window.isDragging) return;

        // For simplicity, just show element info directly when image is clicked
        // Find the closest element to where the user clicked
        const rect = visualizationImg.getBoundingClientRect();
        const clickX = (e.clientX - rect.left) / scale - panX;
        const clickY = (e.clientY - rect.top) / scale - panY;

        // Find any element ID to display
        let closestElement = null;
        let minDistance = Infinity;

        for (const id in elementData) {
            const element = elementData[id];
            const centerX = (element.min_x + element.max_x) / 2;
            const centerY = (element.min_y + element.max_y) / 2;

            const distance = Math.sqrt(
                Math.pow(clickX - centerX, 2) +
                Math.pow(clickY - centerY, 2)
            );

            if (distance < minDistance) {
                minDistance = distance;
                closestElement = element;
            }
        }

        if (closestElement) {
            showElementInfo(closestElement, e.clientX, e.clientY);
        }
    });

    // Function to show element info popup
    function showElementInfo(element, x, y) {
        // Create HTML content for popup
        let html = `
            <h4>Element Details</h4>
            <p><strong>ID:</strong> ${element.id}</p>
        `;

        if (element.family) {
            html += `<p><strong>Family:</strong> ${element.family}</p>`;
        }

        if (element.document) {
            html += `<p><strong>Document:</strong> ${element.document}</p>`;
        }

        html += `
            <p><strong>Coordinates:</strong><br>
            X: ${element.min_x.toFixed(4)} to ${element.max_x.toFixed(4)}<br>
            Y: ${element.min_y.toFixed(4)} to ${element.max_y.toFixed(4)}</p>
        `;

        if (element.is_kit_ds1) {
            html += `<p><strong>Type:</strong> KIT(DS)1</p>`;
        }

        popupContent.innerHTML = html;

        // Position the popup
        popup.style.left = (x + 10) + 'px';
        popup.style.top = (y + 10) + 'px';
        popup.style.display = 'block';
    }

    // Hide popup when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target !== visualizationImg && !popup.contains(e.target)) {
            popup.style.display = 'none';
        }
    });

    // Define variables if they're not already defined (needed for popup click handler)
    if (typeof scale === 'undefined') {
        var scale = 1;
    }

    if (typeof panX === 'undefined') {
        var panX = 0;
    }

    if (typeof panY === 'undefined') {
        var panY = 0;
    }

    window.isDragging = false; // Use window scope to share across functions
}