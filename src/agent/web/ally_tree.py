from playwright.sync_api import Page
from time import sleep

# JavaScript code with var instead of let, wrapped in an IIFE
js_code = """
(() => {
    function dfs_ally_tree(element, a11yTree) {
        // Initialize the a11yTree array if not passed
        if (!a11yTree) {
            a11yTree = [];
        }

        // Function to check if the element is in the viewport
        function isElementInViewport(el) {
            var rect = el.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        }

        // Function to check if the element is covered by another element
        function isElementCovered(el) {
            var rect = el.getBoundingClientRect();
            var centerX = rect.left + rect.width / 2;
            var centerY = rect.top + rect.height / 2;
            var elementAtCenter = document.elementFromPoint(centerX, centerY);

            // Check if the element at the center point of the current element is not itself
            return elementAtCenter && elementAtCenter !== el && !el.contains(elementAtCenter);
        }

        // Function to check if the element's width or height is zero
        function isElementSizeZero(el) {
            var rect = el.getBoundingClientRect();
            return rect.width === 0 || rect.height === 0;
        }

        // Base case: Check if the current element is interactive
        var interactiveTags = ['button', 'a', 'input', 'select', 'textarea', 'details', 'li'];
        var interactiveRoles = ['button', 'link', 'textbox', 'checkbox', 'combobox', 'menu', 'slider', 'option', 'searchbox'];

        var role = element?.getAttribute('role');
        var tagName = element.tagName?.toLowerCase();

        // Check if the element is interactive by tag or role
        if (interactiveTags.includes(tagName) || interactiveRoles.includes(role)) {
            // Gather relevant data for the A11y tree node
            var boundingBox = element.getBoundingClientRect();
            var visible = !isElementSizeZero(element) && !isElementCovered(element);  // Check visibility
            var aria = element?.getAttribute('aria-label')

            var a11yNode = {
                tag: tagName,
                role: role || tagName,  // Use tag name if no role
                name: aria || element.innerText || tagName,
                boundingBox: {
                    x: boundingBox.x,
                    y: boundingBox.y,
                    width: boundingBox.width,
                    height: boundingBox.height
                },
                visible: visible  // Use the visibility check
            };

            a11yTree.push(a11yNode);
        }

        // Recursively traverse child nodes if they exist
        var children = element && element.children;
        if (children) {
            for (var i = 0; i < children.length; i++) {
                dfs_ally_tree(children[i], a11yTree);
            }
        }

        return a11yTree;
    }

    // Start traversal from document.body
    return dfs_ally_tree(document.body);
})();
"""


async def extract_accessibility_tree(page:Page):
    # Inject and execute the JavaScript code to build the custom A11y tree
    a11y_tree = await page.evaluate(js_code)
    return a11y_tree

def remove_redundant_elements(a11y_tree):
    seen_names = set()
    filtered_tree = []

    for element in a11y_tree:
        # Use the 'name' as a key to identify redundant elements
        if element['name'] not in seen_names:
            filtered_tree.append(element)
            seen_names.add(element['name'])
    
    return filtered_tree

def generate_tree_string(a11y_tree, indent_level=0):
    """ Generate the hierarchical tree string """
    tree_string = ""
    indent = " " * (indent_level * 4)  # 4 spaces per indent level

    for element in a11y_tree:
        # Format the element with role, name, and bounding box details
        if element['visible']:
            if element['role']=='a':
                element['role']='link'
            if element['role']=='li':
                element['role']='presentation'

            tree_string += f"{indent}Role: {element['role']}, Name: {element['name'].replace('\n','')}\n"
            # tree_string += f"{indent}Role: {element['role']}, Name: {element['name']}, Visible: {element['visible']}, BoundingBox: {element['boundingBox']}\n"

            # Recursively generate tree string for child elements
            if 'children' in element and element['children']:
                tree_string += generate_tree_string(element['children'], indent_level + 1)

    return tree_string

def generate_coordinate_mapping(a11y_tree):
    """ Generate the coordinate mapping between role+name and center coordinates as a list of dicts """
    coord_mapping = []

    for element in a11y_tree:
        if element['visible']:
            # Calculate center coordinates
            bounding_box = element['boundingBox']
            center_x = bounding_box['x'] + bounding_box['width'] / 2
            center_y = bounding_box['y'] + bounding_box['height'] / 2

            if element['role']=='a':
                element['role']='link'
            if element['role']=='li':
                element['role']='presentation'

            # Append a dictionary with role, name, and coordinates
            coord_mapping.append({
                'role': element['role'],
                'name': element['name'].replace('\n', ''),  # Remove newline characters from the name
                'x': center_x,
                'y': center_y
            })

            # Recursively add children to the mapping if they exist
            if 'children' in element and element['children']:
                coord_mapping.extend(generate_coordinate_mapping(element['children']))

    return coord_mapping

# Main script to run Playwright and execute the DFS-based DOM traversal
async def ally_tree_with_cordinates(page:Page):
        # Extract the custom accessibility tree
        a11y_tree = await extract_accessibility_tree(page)

        # Remove redundant elements based on their names
        unique_a11y_tree = remove_redundant_elements(a11y_tree)

        # Generate and print the hierarchical tree string
        tree_string = generate_tree_string(unique_a11y_tree)

        # Generate and print the coordinate mapping
        coord_mapping = generate_coordinate_mapping(unique_a11y_tree)
        # print(tree_string)

        return tree_string,coord_mapping