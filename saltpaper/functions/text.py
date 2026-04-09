import pygame
import pygame.font as pfont
from pathlib import Path

from saltpaper.services.layer import Layer

class effect:
    drop_shadow = 'drop_shadow'

class Style:
    def __init__(
            self,
            font_path,
            size:int,
            colour:tuple[int,int,int] | tuple[int,int,int,int]|str,
            antialias:bool=True,
            wraplength:int=0,
            effects:str|list|None=None,
    ):
        self.font = pfont.Font(font_path, size)
        if type(colour) is str:
            colour = pygame.Color(colour) # type: ignore
        self.colour = colour
        self.antialias = antialias
        self.wraplength = wraplength

        if effects is None:
            self.effects = []
        elif type(effects) is str:
            self.effects = [effects]
        elif type(effects) is list:
            self.effects = effects
        else:
            raise ValueError(f'{effects} is not valid effects, must be str, list, or None')
    def render_text(self, layer:Layer, text:str, pos):
        font_surf = self.font.render(
            text,
            antialias=self.antialias,
            color=self.colour,
            wraplength=self.wraplength
        )
        if effect.drop_shadow in self.effects:
            dropshadow_surf = self.font.render(
                text,
                antialias=self.antialias,
                color=(20,20,20),
                wraplength=self.wraplength
            )
            layer.surface.blit(dropshadow_surf, (pos[0]+2, pos[1]+2))
        
        layer.surface.blit(font_surf, pos)