from playwright.async_api import Page

# Recursive function to build the A11y tree in text format and map names to coordinates
async def build_a11y_tree(node: dict, page: Page, level: int = 0, coordinates: list = None):
    if coordinates is None:
        coordinates = []

    # Skip nodes with no name
    if not node.get('name').strip() and not node.get('children') and node.get('role') not in ['combobox']:
        return "", coordinates

    # Indentation based on depth level in the tree
    indent = '  ' * level
    
    # Start by building the string with role and name
    tree_string = f"{indent}Role: {node['role']}, Name: {node['name']}"
    
    # Include all other attributes dynamically (excluding 'children', 'role', and 'name')
    extra_info = []
    for key, value in node.items():
        if key not in ['role', 'name', 'children']:
            extra_info.append(f"{key.capitalize()}: {value}")

    bounding_box = None
    
    # Try to locate the bounding box if it's an interactive element
    try:
        if node.get('role') == 'text':  # Handle text elements separately
            locator = page.get_by_text(node['name'], exact=True)
        elif node.get('role') == 'combobox' and node.get('expanded') == True:
            # Handle combo box suggestions
            locator = page.get_by_role('listbox').get_by_role('option')
        else:
            locator = page.get_by_role(node['role'], name=node.get('name'))

        count = await locator.count()
        if count > 0:
            # Loop through all matched elements instead of just the first one
            for index in range(count):
                element = locator.nth(index)

                # Check if the element is visible before fetching the bounding box
                is_visible = await element.is_visible()

                if is_visible:
                    bounding_box = await element.bounding_box()
                    if bounding_box:
                        # Add the bounding box to the coordinates list
                        x, y, width, height = bounding_box.values()
                        x_center, y_center = x + width / 2, y + height / 2
                        if node.get('role') == 'combobox' and node.get('expanded') == True:
                            option_name = ' '.join((await element.text_content()).split())
                            # Add the option name to the tree string as a child node
                            tree_string += f"\n{indent}  Role: option, Name: {option_name}"
                            coordinate = dict(role='option', name=option_name, x=x_center, y=y_center)
                        else:
                            coordinate = dict(role=node['role'], name=node['name'], x=x_center, y=y_center)
                        coordinates.append(coordinate)
                        
    except Exception as e:
        print(f"Error: {e}")

    # Add any extra information found dynamically
    if extra_info:
        tree_string += " (" + ", ".join(extra_info) + ")"
    
    # print(tree_string)
    tree_string += "\n"  # Add newline for formatting

    # If the node has children, recursively build the tree for them
    if 'children' in node:
        for child in node['children']:
            child_tree_string, coordinates = await build_a11y_tree(child, page, level + 1, coordinates)
            tree_string += child_tree_string
    
    return tree_string, coordinates
