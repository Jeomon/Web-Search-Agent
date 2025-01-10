// Function to get a random color
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

let labels = [];

// Function to highlight visible interactive elements with numbered labels
function mark_page(elements) {
    let index = 0; // Start numbering from 1
    elements.forEach(element => {
        const { bounding_box } = element; // Destructure to access box
        if (!bounding_box) return; // Skip if no bounding box

        const { left, top, width, height } = bounding_box;
        const borderColor = getRandomColor();

        // Create bounding box
        const boundingBox = document.createElement('div');
        boundingBox.style.position = 'fixed';
        boundingBox.style.left = `${left}px`;
        boundingBox.style.top = `${top}px`;
        boundingBox.style.width = `${width}px`;
        boundingBox.style.height = `${height}px`;
        boundingBox.style.outline = `2px dashed ${borderColor}`;
        boundingBox.style.pointerEvents = 'none';
        boundingBox.style.zIndex = '9999';

        // Create a label for the number
        const label = document.createElement('span');
        label.textContent = index;
        label.style.position = 'absolute';
        label.style.top = '-19px'; // Position above the bounding box
        label.style.left = '0px';
        label.style.backgroundColor = borderColor;
        label.style.color = 'white';
        label.style.padding = '2px 4px';
        label.style.fontSize = '12px';
        label.style.borderRadius = '2px';

        // Append the label and bounding box to the document
        boundingBox.appendChild(label);
        labels.push(boundingBox);
        document.body.appendChild(boundingBox);
        index++; // Increment counter
    });
}

// Function to remove all bounding boxes and labels
function unmark_page() {
    for (const label of labels) {
        document.body.removeChild(label);
    }
    labels = [];
}
