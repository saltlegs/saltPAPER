import pygame
import numpy as np
import moderngl

class Layer:
    def __init__(
            self,
            ctx,
            dimensions:tuple[int,int],
            render_priority:int=0,
            tick_priority:int=0,
            opacity_percent:int=100,
            offset:tuple[int,int]=(0,0)
    ):
        self.ctx = ctx
        self.dimensions = dimensions
        self.texture = ctx.texture(dimensions, 4)
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.fbo = ctx.framebuffer(color_attachments=[self.texture])
        self.visible = True
        self.ticking = True
        self.opacity_percent = opacity_percent
        self.offset:tuple[int,int] = offset
        
        self.render_priority = render_priority
        self.tick_priority = tick_priority
        
        self.funcs = []

        # loopscroll()
        self._loopscroll_accum_x = 0.0
        self._loopscroll_accum_y = 0.0

    def mount(self, func=None):
        """mount a function to be called when this layer ticks. gives the layer and delta as arguments (i.e. `main(layer, delta)`)"""
        if not func: return
        self.funcs.append(func)

    def tick(self, delta):
        for func in self.funcs:
            func(self, delta)
    
    def render(self):
        return self.texture

    def clear(self):
        self.fbo.clear(0.0, 0.0, 0.0, 0.0)
    
    def relative_coords(self, coords):
        x, y = coords
        newcoords = (x - self.offset[0], y - self.offset[1])
        return newcoords
    

    def loopscroll(self, dx, dy, dt=1.0):
        raise NotImplementedError("loopscroll must be reimplemented as a UV offset uniform for OpenGL")
