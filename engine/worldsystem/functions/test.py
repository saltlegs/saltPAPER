from engine.worldsystem.entity import Entity
from engine.worldsystem.components import Position, Sprite

def make_test_entity(world, layer, x, y) -> Entity:
    ent = Entity(world)

    position = Position(layer, x, y)

    sprite = Sprite(asset_id="image_joker")

    ent.add_many(position, sprite)

    return ent