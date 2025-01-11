from dataclasses import dataclass,field
from playwright.async_api import ElementHandle

@dataclass
class DOMElementNode:
    tag: str
    role: str
    name: str
    bounding_box: dict
    attributes: dict[str,str] = field(default_factory=dict)

    def __repr__(self):
        return f"DOMElementNode(tag='{self.tag}', role='{self.role}', name='{self.name}', attributes={self.attributes})"
    
    def to_dict(self)->dict[str,str]:
        return {'tag':self.tag,'role':self.role,'name':self.name,'bounding_box':self.bounding_box,'attributes':self.attributes}
    
@dataclass
class DOMState:
    nodes: list[tuple[DOMElementNode,ElementHandle]]=field(default_factory=list)
    selector_map:dict[int,tuple[DOMElementNode,ElementHandle]]=field(default_factory=dict)

    def elements_to_string(self)->str:
        return '\n'.join([f'{index} - Tag: {node.tag} Role: {node.role} Name: {node.name} attributes: {node.attributes}' for index,(node,_) in enumerate(self.nodes)])