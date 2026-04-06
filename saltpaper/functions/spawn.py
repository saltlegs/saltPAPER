from saltpaper.worldsystem.entity import Entity
from saltpaper.worldsystem.components import Position, Sprite

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saltpaper import Event, Layer, World, AssetService

def make_display_entity(world, layer, position, asset_id) -> Entity:
    
    ent = Entity(world)
    position = Position(layer, position)
    sprite = Sprite(asset_id)
    ent.add_many(position, sprite)

    return ent

def make_button(
        world: 'World',
        assetservice:'AssetService',
        layer:'Layer',
        position:tuple[int,int],
        asset_id:str,
        event:'Event',
        eat_trigger:bool=True
) -> tuple[Entity, 'Event']:
    from saltpaper.worldsystem.components import Clickable
    
    ent = Entity(world)
    asset_dims = assetservice.get_asset(asset_id).size
    position_obj = Position(layer, position, *asset_dims)
    bounds = (*position, *asset_dims)
    sprite = Sprite(asset_id)
    event.eat_trigger = eat_trigger
    clickable = Clickable(event, layer, bounds)

    ent.add_many(position_obj, sprite, clickable)
    return ent, event
