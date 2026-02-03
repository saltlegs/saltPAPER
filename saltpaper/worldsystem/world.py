from saltpaper.worldsystem.components.sprite import Sprite
from saltpaper.worldsystem.entity import Entity

class World():
    def __init__(self):
        self.entities: list[Entity] = []

    def collect_component_type(self, component_type):
        renderables = []
        for entity in self.entities:
            if not entity.has(component_type):
                continue
            renderables.append(entity)
        return renderables