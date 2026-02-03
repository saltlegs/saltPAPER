from engine.worldsystem.components.sprite import Sprite
from engine.worldsystem.entity import Entity

class World():
    def __init__(self):
        self.entities: list[Entity] = []

    def collect_renderables(self):
        renderables = []
        for entity in self.entities:
            if not entity.has(Sprite):
                continue
            renderables.append(entity)
        return renderables