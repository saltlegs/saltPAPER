import pygame
import sys
import random
from pathlib import Path

from engine.map.tilemap import TileMap
from engine.services.input import EventMapper, Event
from engine.services.input import Criteria as cr
from engine.services.display import DisplayService
from engine.services.layer import Layer


cwd = Path.cwd()
tilemap_path = cwd / "engine" / "assets" / "tilemaps" / "test.png"
tilemap = TileMap(tilemap_path, 16)

dimensions = 768,624
FPS = 120

eventmapper = EventMapper()
display = DisplayService(
    dimensions=dimensions,
    eventmapper=eventmapper,
    caption="eeeeee",
    vsync=False,
    target_frame_rate=60,
)

TILE_SIZE = 48

def fill_layer_with_tiles(layer, tile_size=TILE_SIZE):
    tiles_x = (layer.dimensions[0] // tile_size) + 2 
    tiles_y = (layer.dimensions[1] // tile_size) + 2
    
    for y in range(tiles_y):
        for x in range(tiles_x):
            tile = random.choice(tilemap.tiles).get_surface()
            tile = pygame.transform.scale(tile, (tile_size, tile_size))
            layer.surface.blit(tile, (x * tile_size, y * tile_size))

tile_layer = Layer(
    dimensions=dimensions,
    render_priority=1,
    opacity_percent=50
)

tile_layer2 = Layer(
    dimensions=dimensions,
    render_priority=1,
    opacity_percent=50
)

fill_layer_with_tiles(tile_layer)
fill_layer_with_tiles(tile_layer2)

display.add_layer(tile_layer)
display.add_layer(tile_layer2)
mouse = pygame.mouse
def scroll_layer1(f, dx, dy): 
    tile_layer.loopscroll(dx,dy)

speed = 2
layer1_events = [
    Event(["K_UP", "CONTROLLER_BUTTON_DPAD_UP"], cr.on_held, scroll_layer1, [0, -speed]),
    Event(["K_RIGHT", "CONTROLLER_BUTTON_DPAD_RIGHT"], cr.on_held, scroll_layer1, [speed, 0]),
    Event(["K_DOWN", "CONTROLLER_BUTTON_DPAD_DOWN"], cr.on_held, scroll_layer1, [0, speed]),
    Event(["K_LEFT", "CONTROLLER_BUTTON_DPAD_LEFT"], cr.on_held, scroll_layer1, [-speed, 0]),
]
for event in layer1_events:
    eventmapper.register_event(event)

def main():
    while display.running:
        display.tick()
        pygame.display.set_caption(f"{display.caption} - {display.clock.get_fps():.0f}fps (limit {FPS}) - delta {display.delta:.2f})")
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # test, not final
    main()