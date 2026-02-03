import pygame

from engine.services.layer import Layer
from engine.services.assetservice import AssetService

class RenderService():
    def __init__(self, assetservice: AssetService):
        self.assetservice = assetservice
        self.render_queue:dict[Layer, list] = {}
        
    def _queue(self, layer:Layer, pos:tuple[int,int], surface:pygame.Surface):
        item = (surface, pos)
        if not self.render_queue.get(layer, None):
            self.render_queue[layer] = []
        self.render_queue[layer].append(item)

    def _process_queue(self):
        for layer, items in self.render_queue.items():
            layer.surface.blits(items)
        self.render_queue.clear()

    def render(self, layer:Layer, pos:tuple[int,int], asset_id:str):
        surf = self.assetservice.get_asset(asset_id)
        self._queue(layer, pos, surf)

    def tick(self):
        self._process_queue()
