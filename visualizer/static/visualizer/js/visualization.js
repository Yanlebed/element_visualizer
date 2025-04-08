// static/visualizer/js/visualization.js

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the visualization result page
    const visualizationImg = document.querySelector('.visualization img');
    if (!visualizationImg) return;

    // Setup only the element info popup functionality
    setupElementInfoPopup(visualizationImg);
});

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
                position: fixed; /* Changed from absolute to fixed for better positioning */
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
                max-width: 100%;
                height: auto;
                margin: 0 auto;
                display: block;
            }
            
            /* Static visualization container */
            .visualization {
                overflow: hidden;
                max-height: 70vh;
                position: relative;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin: 1rem 0;
                text-align: center;
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
        console.log("Image clicked");

        // Get the image's position and dimensions
        const rect = visualizationImg.getBoundingClientRect();

        // Calculate click position relative to the image
        // This is a direct calculation without any scaling or panning
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;

        // Calculate the ratio of the displayed image to its natural size
        const displayRatio = rect.width / visualizationImg.naturalWidth;

        // Convert click coordinates to the original image coordinates
        const originalX = clickX / displayRatio;
        const originalY = clickY / displayRatio;

        console.log("Click coordinates:", clickX, clickY);
        console.log("Original image coordinates:", originalX, originalY);

        // Find the element that was clicked
        const element = findElementAtPosition(originalX, originalY);

        if (element) {
            console.log("Element found:", element);
            showElementInfo(element, e.clientX, e.clientY);
        } else {
            console.log("No element found at click position");
            // No element found, hide the popup
            popup.style.display = 'none';
        }
    });

    // Function to find element at click position with a distance threshold
    function findElementAtPosition(clickX, clickY) {
        // Define a reasonable maximum distance for considering a click "on" an element
        const maxDistanceThreshold = 10; // Units in coordinate space

        let bestMatch = null;
        let bestDistance = Infinity;

        for (const id in elementData) {
            const element = elementData[id];

            // First check direct hit - if click is inside element bounds
            if (clickX >= element.min_x && clickX <= element.max_x &&
                clickY >= element.min_y && clickY <= element.max_y) {
                console.log("Direct hit on element:", element.id);
                return element; // Direct hit - return immediately
            }

            // If not a direct hit, calculate distance to element center
            const centerX = (element.min_x + element.max_x) / 2;
            const centerY = (element.min_y + element.max_y) / 2;

            const distance = Math.sqrt(
                Math.pow(clickX - centerX, 2) +
                Math.pow(clickY - centerY, 2)
            );

            console.log(`Element ${element.id} distance: ${distance}`);

            // Only consider this element if it's closer than current best and within threshold
            if (distance < bestDistance && distance < maxDistanceThreshold) {
                bestDistance = distance;
                bestMatch = element;
            }
        }

        // Only return an element if it's within our threshold
        return (bestDistance < maxDistanceThreshold) ? bestMatch : null;
    }

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
}