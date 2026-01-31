import pygame
import sys
from statistics import mean
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class DisplayService():
    def __init__(
            self,
            dimensions,
            eventmapper,
            target_frame_rate:int=120,
            func=None,
            caption="saltpaper engine display",
            vsync=True # for testing
    ):
        self.dimensions = dimensions
        self.func = func
        self.caption = caption
        self.eventmapper = eventmapper
        self.target_frame_rate = target_frame_rate

        self.layers = []

        pygame.init()


        self.display = pygame.display.set_mode(dimensions, vsync=vsync)

        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.delta = 1
        self.deltas = []

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
        delta_entry = self.clock.tick(self.target_frame_rate) / 1000
        self.deltas.append(delta_entry)
        if len(self.deltas) > 10:
            self.deltas.pop(0)
        self.delta = mean(self.deltas) # will raise if empty but deltas should never be empty at this point of execution 

if __name__ == "__main__":
    from pathlib import Path
    from engine.services.layer import Layer
    from engine.map.tilemap import TileMap
    from engine.services.input import EventMapper

    cwd = Path.cwd()
    duck_image_path = cwd / "engine" / "assets" / "images" / "duck.jpg"
    duck_image = pygame.image.load(duck_image_path)
    test_image_path = cwd / "engine" / "assets" / "images" / "test.png"
    dimensions = duck_image.get_size()
    eventmapper = EventMapper()
    display = DisplayService(
        dimensions=dimensions,
        eventmapper=eventmapper,
        vsync=False,
        target_frame_rate=120,
    )

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
        layer1.loopscroll(50,0, display.delta)
        layer2.loopscroll(0,50, display.delta)
        display.tick()
        pygame.display.set_caption(f"{display.caption} - {display.clock.get_fps():.0f}fps (limit {display.target_frame_rate}) - delta {display.delta:.2f})")
    