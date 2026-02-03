from engine.worldsystem.entity import Entity
from engine.worldsystem.components import Position, Sprite

def make_test_entity() -> Entity:
    ent = Entity()

    position = Position()

    sprite = Sprite(asset_id="image_joker")