from src.agent.web.dom.config import INTERACTIVE_ROLES,SAFE_ATTRIBUTES
from src.agent.web.dom.views import DOMElementNode,DOMState
from playwright.async_api import Page

class DOM:
    def __init__(self, page:Page):
        self.page = page
    
    async def _fetch_accessibility_tree(self) -> dict:
        return await self.page.accessibility.snapshot(interesting_only=False)
    
    async def _extract_interactive_elements_from_tree(self) -> list[dict]:
        accessibility_tree =await self._fetch_accessibility_tree()        
        interactive_elements = []
        def traverse_node(node:dict[str,str]):
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
    
    async def get_state(self)->DOMState:
        nodes = []
        interactive_elements =await self._extract_interactive_elements_from_tree()
        for element in interactive_elements:
            matching_nodes = self.page.get_by_role(element["role"], name=element["name"])
            count=await matching_nodes.count()
            for index in range(count):
                element_handle =await matching_nodes.nth(index).element_handle()
                if not await element_handle.is_visible():
                    continue
                tag_name = await element_handle.evaluate('el => el.tagName.toLowerCase()')
                attributes =await element_handle.evaluate('el => Object.fromEntries([...el.attributes].map(attr => [attr.name, attr.value]))')
                box=await element_handle.bounding_box()
                safe_attributes = {key: value for key, value in attributes.items() if key in SAFE_ATTRIBUTES}
                params = {
                    'tag': tag_name,
                    'role': element.get('role'),
                    'name': element.get('name'),
                    'bounding_box':{'left':box['x'],'top':box['y'],'width':box['width'],'height':box['height']},
                    'attributes': safe_attributes
                }
                nodes.append(DOMElementNode(**params))
        selector_map=await self.build_selector_map(nodes)
        return DOMState(nodes,selector_map)
    
    async def build_selector_map(self,nodes:list[DOMElementNode])->dict[int,DOMElementNode]:
        return {index: node for index, node in enumerate(nodes)}




        
