import pygame
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class DisplayService():
    def __init__(
            self,
            dimensions,
            eventmapper,
            func=None,
            caption="saltpaper",
            vsync=True # for testing
    ):
        self.dimensions = dimensions
        self.func = func
        self.caption = caption
        self.eventmapper = eventmapper

        self.layers = []

        pygame.init()


        self.display = pygame.display.set_mode(dimensions, vsync=vsync)

        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()

        self.running = True
        self.dirty = True

    def mount(self, func=None):
        self.func = func

    def refresh_sorting(self):
        self.layers_by_tick = sorted(self.layers, key=lambda l: l.tick_priority)
        self.layers_by_render = sorted(self.layers, key=lambda l: l.render_priority)

    def add_layer(self, layer):
        self.layers.append(layer)
        self.refresh_sorting()

    def remove_layer(self, layer):
        for i, item in enumerate(self.layers):
            if item is layer:
                self.layers.pop(i)
                self.refresh_sorting()
                return True
        return False

    def get_layers(self):
        return self.layers

    def tick(self):
        self.events = pygame.event.get()
        self.eventmapper.tick(self.events)
        for event in self.events:
            if event.type == pygame.QUIT:
                self.running = False

        for layer in self.layers_by_tick:
            if layer.ticking:
                layer.tick()

        for layer in self.layers_by_render:
            if not layer.visible:
                continue
            surf = layer.render()
            offset = layer.offset
            self.display.blit(surf, offset)
            
        if self.func:
            self.func(self)

        pygame.display.flip()

if __name__ == "__main__":
    from pathlib import Path
    from engine.services.layer import Layer
    from engine.map.tilemap import TileMap

    cwd = Path.cwd()
    duck_image_path = cwd / "engine" / "assets" / "images" / "duck.jpg"
    duck_image = pygame.image.load(duck_image_path)
    test_image_path = cwd / "engine" / "assets" / "images" / "test.png"
    dimensions = duck_image.get_size()
    display = DisplayService(dimensions, vsync=False)
    fps = 5000

    tilemap = TileMap(test_image_path, 16)


    layer1 = Layer(
        dimensions=dimensions,
        surface=duck_image.copy(),
        opacity_percent=50
    )

    layer2 = Layer(
        dimensions=dimensions,
        surface=duck_image.copy(),
        opacity_percent=50
    )

    display.add_layer(layer1)
    display.add_layer(layer2)

    while display.running:
        layer1.loopscroll(1,0)
        layer2.loopscroll(0,1)
        display.tick()
        display.clock.tick(fps)
        pygame.display.set_caption(f"{display.caption} - {display.clock.get_fps():.0f}fps (limit {fps})")
    