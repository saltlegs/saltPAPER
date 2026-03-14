import pygame
import sys
from statistics import mean
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saltpaper import InputService

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class DisplayService():

    def __init__(
            self,
            dimensions,
            inputservice,
            target_frame_rate:int=120,
            caption="saltpaper engine display",
            vsync=True, # for testing
            iconpath=None
    ):
        self.dimensions = dimensions
        self._caption = caption
        self.inputservice:'InputService' = inputservice
        self.target_frame_rate = target_frame_rate

        self.layers = []

        self.refresh_sorting()

        pygame.init()

        self.funcs = []
        if iconpath is not None:
            iconsurf = pygame.image.load(iconpath)
            pygame.display.set_icon(iconsurf)
        self.display = pygame.display.set_mode(dimensions, vsync=vsync)

        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.delta = 1
        self.deltas = []

        self.running = True
        self.dirty = True

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, value):
        self._caption = value
        pygame.display.set_caption(value)

    def mount(self, func=None):
        if not func: return
        self.funcs.append(func)

    def refresh_sorting(self):
        self.layers_by_tick = sorted(self.layers, key=lambda l: l.tick_priority)
        self.layers_by_render = sorted(self.layers, key=lambda l: l.render_priority)

    def add_layer(self, layer):
        self.layers.append(layer)
        self.refresh_sorting()

    def add_many_layers(self, layers:list):
        self.layers.extend(layers)
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
        if len(self.layers) == 0:
            raise ValueError("the display service has no layers to display. make sure they are added with displayservice.add_layer(layer)")

        self.events = pygame.event.get()
        self.inputservice.tick(self.events)
        for event in self.events:
            if event.type == pygame.QUIT:
                self.running = False

        for layer in self.layers_by_tick:
            if layer.ticking:
                layer.tick(self.delta)

        for layer in self.layers_by_render:
            if not layer.visible:
                continue
            surf = layer.render()
            offset = layer.offset
            self.display.blit(surf, offset)
            
        for func in self.funcs:
            func(self, self.delta)

        pygame.display.flip() 
        delta_entry = self.clock.tick(self.target_frame_rate) / 1000
        self.deltas.append(delta_entry)
        if len(self.deltas) > 10:
            self.deltas.pop(0)
        self.delta = mean(self.deltas)

        return self.delta