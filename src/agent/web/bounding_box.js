
    // Inject custom scrollbar styles
// const customCSS = `
//     ::-webkit-scrollbar {
//         width: 10px;
//     }
//     ::-webkit-scrollbar-track {
//         background: #27272a;
//     }
//     ::-webkit-scrollbar-thumb {
//         background: #888;
//         border-radius: 0.375rem;
//     }
//     ::-webkit-scrollbar-thumb:hover {
//        background: #555;
//     }
// `
// const customStyle = document.createElement('style');
// customStyle.innerHTML = customCSS;
// document.head.appendChild(customStyle);

// Function to get a random color
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// Helper function to check if an element is interactive
function isInteractiveElement(el) {
    const tagName = el.tagName.toLowerCase();
    const interactiveTags = ['button', 'a', 'input', 'textarea', 'select', 'iframe', 'video','li'];
    const interactiveRoles = ['button', 'link', 'textbox', 'checkbox', 'combobox', 'menu', 'slider', 'option', 'searchbox'];
    const role = el.getAttribute('role');
    const hasClickEvent = el.hasAttribute('onclick') || typeof el.onclick === 'function';
    const cursorStyle = window.getComputedStyle(el).cursor;
    const isInteractive = interactiveTags.includes(tagName) ||interactiveRoles.includes(role) || hasClickEvent || cursorStyle === 'pointer';
    return isInteractive;
}

// Helper function to check if an element is visible
function isVisible(el) {
    const style = window.getComputedStyle(el);
    const isDisplayed = style.display !== 'none'; // Not display: none
    const isVisible = style.visibility !== 'hidden'; // Not visibility: hidden
    const isOpaque = parseFloat(style.opacity) > 0; // Opacity greater than 0
    const hasDimensions = el.offsetWidth > 1 && el.offsetHeight > 1; // Has non-zero dimensions
    return isDisplayed && isVisible && isOpaque && hasDimensions;
}

// Helper function to determine if an element has an interactive parent (e.g., a button)
function hasInteractiveParent(el) {
    let parent = el.parentElement;
    while (parent) {
        if (isInteractiveElement(parent)) {
            return true; // Stop if we find an interactive parent
        }
        parent = parent.parentElement;
    }
    return false; // No interactive parent found
}

let labels=[]
const minArea=20

// Function to highlight visible interactive elements with numbered labels
function mark_page() {
    const coordinates=[]
    const elements = document.body.querySelectorAll('*');
    let counter = 1; // Start numbering from 1
    elements.forEach(element => {
        // Skip elements that are inside other interactive elements
        if (hasInteractiveParent(element)) return;
        if (isInteractiveElement(element) && isVisible(element)) { // Apply only if visible and interactive
            const rects = Array.from(element.getClientRects());
            rects.forEach(rect => {
                const boundingBox = document.createElement('div');
                const borderColor = getRandomColor();

                // Calculate width, height, and area
                const width = rect.width;
                const height = rect.height;
                const area = width * height;

                // Skip the element if the area is too small
                if (area < minArea) return;

                // Create bounding box
                boundingBox.style.position = 'fixed';
                boundingBox.style.left = `${rect.left}px`;
                boundingBox.style.top = `${rect.top}px`;
                boundingBox.style.width = `${rect.width}px`;
                boundingBox.style.height = `${rect.height}px`;
                boundingBox.style.outline = `2px dashed ${borderColor}`;
                boundingBox.style.pointerEvents = 'none';
                boundingBox.style.zIndex = '9999';

                // Create a label for the number
                const label = document.createElement('span');
                label.textContent = counter;
                label.style.position = 'absolute';
                label.style.top = '-19px'; // Position above the bounding box
                label.style.left = '0px';
                label.style.backgroundColor = borderColor; // Match the border color
                label.style.color = 'white';
                label.style.padding = '2px 4px';
                label.style.fontSize = '12px';
                label.style.borderRadius = '2px';

                // Calculate center coordinates
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const elementType= element.tagName.toUpperCase()
                const text=element.textContent?.trim()

                coordinates.push({ 'elementType': elementType , 'label': counter, 'x': centerX, 'y': centerY, 'text': text});

                // Append the label and bounding box to the document
                boundingBox.appendChild(label);
                labels.push(boundingBox)
                document.body.appendChild(boundingBox);
                counter++; // Increment the counter for the next element
            });
        }
    });
    return coordinates
}

function unmark_page(){
    for(const label of labels){
        document.body.removeChild(label)
    }
    labels=[]
}