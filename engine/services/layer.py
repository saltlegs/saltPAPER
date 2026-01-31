import pygame
import numpy as np

class Layer:
    def __init__(
            self,
            dimensions,
            render_priority=0,
            tick_priority=0,
            opacity_percent=100,
            surface=None,
            func=None,
    ):
        self.dimensions = dimensions
        self.surface = surface if surface else pygame.Surface(dimensions, pygame.HWSURFACE | pygame.SRCALPHA)
        self.visible = True
        self.ticking = True
        self.opacity_percent = opacity_percent
        self.offset = (0,0)
        self.func = func
        self.render_priority = render_priority
        self.tick_priority = tick_priority
        
        # loopscroll()
        self._loopscroll_accum_x = 0.0
        self._loopscroll_accum_y = 0.0

    def tick(self):
        if self.func:
            self.func(self)
    
    def render(self):
        if self.opacity_percent >= 100:
            return self.surface
        
        surf = self.surface.copy()
        surf.set_alpha(int(self.opacity_percent * 2.55))
        return surf
    

    def loopscroll(self, dx, dy, dt=1.0):
        self._loopscroll_accum_x += dx * dt
        self._loopscroll_accum_y += dy * dt

        scroll_x = int(self._loopscroll_accum_x)
        scroll_y = int(self._loopscroll_accum_y)

        self._loopscroll_accum_x -= scroll_x
        self._loopscroll_accum_y -= scroll_y

        if scroll_x == 0 and scroll_y == 0:
            return

        surf = self.surface
        scroll_area_x = (abs(scroll_x), surf.get_height())
        scroll_area_y = (surf.get_width(), abs(scroll_y))
        if scroll_x != 0:
            tempx = pygame.Surface(scroll_area_x, pygame.SRCALPHA)
        if scroll_y != 0:
            tempy = pygame.Surface(scroll_area_y, pygame.SRCALPHA)

        top = 0
        left = 0
        right = surf.get_width()
        bottom = surf.get_height()

        if scroll_x > 0: # image is moving right, copy rightmost chunk to left
            tempx.blit(surf, (0,0), ((right-scroll_x, top), (scroll_x, bottom)))
            surf.scroll(scroll_x, 0)
            surf.blit(tempx, (left,top))
        elif scroll_x < 0: # image is moving left, copy leftmost chunk to right
            tempx.blit(surf, (0,0), ((0, top), (-scroll_x, bottom)))
            surf.scroll(scroll_x, 0)
            surf.blit(tempx, (right+scroll_x,top))
        
        if scroll_y > 0: # image is moving down, copy bottom chunk to top
            tempy.blit(surf, (0,0), ((left, bottom-scroll_y), (right, scroll_y)))
            surf.scroll(0, scroll_y)
            surf.blit(tempy, (left, top))
        elif scroll_y < 0: # image is moving up, copy top chunk to bottom
            tempy.blit(surf, (0,0), ((left, 0), (right, -scroll_y)))
            surf.scroll(0, scroll_y)
            surf.blit(tempy, (left, bottom+scroll_y))

        self.surface = surf
