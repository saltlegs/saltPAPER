from saltpaper.worldsystem.components.sprite import Sprite
from saltpaper.worldsystem.entity import Entity

class World():
    def __init__(self):
        self.entities: dict[int, Entity] = {}

    def __iter__(self):
        return iter(self.entities.values())

    def collect_component_type(self, component_type):
        renderables = []
        for entity in self:
            if not entity.has(component_type):
                continue
            renderables.append(entity)
        return renderables