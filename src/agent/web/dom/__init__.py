from src.agent.web.dom.config import INTERACTIVE_ROLES, SAFE_ATTRIBUTES
from src.agent.web.dom.views import DOMElementNode, DOMState
from playwright.async_api import Page,ElementHandle

class DOM:
    def __init__(self, page: Page):
        self.page = page

    async def _fetch_accessibility_tree(self) -> dict:
        """Fetch the accessibility tree from the page."""
        await self.page.wait_for_timeout(2 * 1000)
        return await self.page.accessibility.snapshot(interesting_only=False)

    def deduplicate(self, nodes: list[dict]) -> list[DOMElementNode]:
        """Deduplicate nodes based on unique attributes."""
        seen = set()
        deduplicated = []
        for node in nodes:
            identifier = (
                node['role'],
                node['name'],
                node['tag'],
                frozenset(node['attributes'].items())  # Convert attributes to a hashable type
            )
            if identifier not in seen:
                seen.add(identifier)
                deduplicated.append(DOMElementNode(**node))
        return deduplicated

    async def _extract_interactive_elements_from_tree(self) -> list[dict]:
        """Extract interactive elements from the accessibility tree."""
        accessibility_tree = await self._fetch_accessibility_tree()
        interactive_elements = []

        def traverse_node(node: dict[str, str]):
            """Recursively process nodes to extract interactive elements."""
            role = node.get("role")
            name = node.get("name")
            children = node.get("children", [])
            if role in INTERACTIVE_ROLES and name.strip():
                interactive_elements.append({"role": role, "name": name})
            for child in children:
                traverse_node(child)

        traverse_node(accessibility_tree)
        return interactive_elements

    async def is_element_in_viewport(self, box: dict) -> bool:
        """Check if the element is in the viewport."""
        viewport_size = self.page.viewport_size
        scroll_offsets = await self.page.evaluate(
            "({ x: window.scrollX, y: window.scrollY })"
        )
        scroll_x = scroll_offsets["x"]
        scroll_y = scroll_offsets["y"]
        viewport_width = viewport_size["width"]
        viewport_height = viewport_size["height"]

        return not (
            box["x"] + box["width"] <= scroll_x or  # Entirely to the left
            box["y"] + box["height"] <= scroll_y or  # Entirely above
            box["x"] >= scroll_x + viewport_width or  # Entirely to the right
            box["y"] >= scroll_y + viewport_height  # Entirely below
        )
    
    async def is_element_covered(self, current_element: ElementHandle) -> bool:
        # Get the element under the point (this is a JSHandle)
        top_element = await self.page.evaluate_handle(
            """
            (el) => {
                const rect = el.getBoundingClientRect();
                const point = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
                return document.elementFromPoint(point.x, point.y);
            }
            """, current_element)

        # Check if no element is returned (top_element is None)
        if top_element is None:
            return False

        # Compare `current_element` and `top_element` by comparing a unique property like outerHTML
        is_inside = await self.page.evaluate("([current, top]) => {return current.contains(top);}", [current_element, top_element])

        # If top_element is inside current_element, it means it's covered by it
        if is_inside:
            return False

        return True


    async def get_state(self) -> DOMState:
        """Get the state of all interactive elements on the page."""
        nodes = []
        interactive_elements = await self._extract_interactive_elements_from_tree()

        # Check each interactive element for visibility and obstruction
        for element in interactive_elements:
            matching_nodes = self.page.get_by_role(role=element["role"], name=element["name"])
            count = await matching_nodes.count()
            for index in range(count):
                element_handle = await matching_nodes.nth(index).element_handle()
                if not await element_handle.is_visible() or await element_handle.get_attribute('aria-hidden') == 'true':
                    continue

                # Get the coordinates for the interactive element
                box = await element_handle.bounding_box()
                if not box:
                    continue

                # Skip if element is out of the viewport
                if not await self.is_element_in_viewport(box):
                    continue  # Discard elements outside the scrolled viewport
                
                # Skip if element is covered
                if await self.is_element_covered(element_handle):
                    continue  # Discard elements covered by another element

                # Proceed with the element as it is not in the viewport
                tag_name = await element_handle.evaluate("el => el.tagName.toLowerCase()")
                attributes = await element_handle.evaluate(
                    "el => Object.fromEntries([...el.attributes].map(attr => [attr.name, attr.value]))"
                )
                safe_attributes = {key: value for key, value in attributes.items() if key in SAFE_ATTRIBUTES}

                node = {
                    "tag": tag_name,
                    "role": element.get("role"),
                    "name": element.get("name"),
                    "bounding_box": {
                        "left": box.get('x'),
                        "top": box.get('y'),
                        "width": box.get('width'),
                        "height": box.get('height'),
                    },
                    "attributes": safe_attributes,
                }
                nodes.append(node)

        nodes = self.deduplicate(nodes)
        selector_map = await self.build_selector_map(nodes)
        return DOMState(nodes, selector_map)

    async def build_selector_map(self, nodes: list[DOMElementNode]) -> dict[int, DOMElementNode]:
        """Build a map from element index to node."""
        return {index: node for index, node in enumerate(nodes)}