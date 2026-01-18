import pygame
from pathlib import Path

class TileType():
    def __init__(self, id, size):
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)

    def get_surface(self, rot:int=0) -> pygame.surface.Surface:
        if rot == 0:
            return self.surface
        else:
            return pygame.transform.rotate(self.surface, (90 * rot))


class TileMap():
    def __init__(self, path, size):
        self.path = path
        self.base = pygame.image.load(path)
        self.size = size
        self.tiles = []
        self.load_tilesheet()

    def load_tilesheet(self, path=None):
        if path == None:
            path = self.path
        width,height = self.base.get_size()
        if not width == height:
            raise ValueError("tilesheets should be exactly square")
        if not width % self.size == 0:
            raise ValueError("tilesheet size is not a multiple of tile size")
        tilewidth = width // self.size
        tilestotal = tilewidth * tilewidth

        for i in range(tilestotal):
            tile = TileType(i, self.size)
            offsetx = (i % tilewidth) * self.size
            offsety = (i // tilewidth) * self.size
            tile.surface.blit(self.base, (0, 0), (offsetx, offsety, self.size, self.size))
            
            if not self._is_fully_transparent(tile.surface):
                self.tiles.append(tile)
    
    def _is_fully_transparent(self, surface):
        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                r, g, b, a = surface.get_at((x, y))
                if a > 0:  # Found a non-transparent pixel
                    return False
        return True
    
    def __len__(self):
        return len(self.tiles)

if __name__ == "__main__":
    cwd = Path.cwd()
    test_image = cwd / "engine" / "assets" / "images" / "test.png"
    tilemap = TileMap(test_image, 16)
    print(len(tilemap))