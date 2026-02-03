import pygame
import os
from pathlib import Path

cwd = Path.cwd()
engine_assets = cwd / "engine" / "assets"
game_assets = cwd / "game" / "assets"


filetypes = {
    "image": [".png", ".jpg", ".bmp", ".gif"],
    "music": [".wav", ".ogg", ".mp3"],
    "sound": [".wav", ".ogg", ".mp3"],
    "tilesheet": [".tls"], # todo
    "room": [".room"] #todo
}

class AssetService():
    def __init__(self):
        self.cache = {}
        self.roots = [game_assets, engine_assets]

    def get_asset(self, id):
        asset = self.cache.get(id)
        if asset is not None:
            return asset

        kind, name = id.split("_", 1)
        extensions = filetypes.get(kind)

        if extensions is None:
            raise ValueError(f"unknown asset type: {kind}")

        searched = []
        for root in self.roots:
            for ext in extensions:
                path = root / kind / f"{name}{ext}"
                searched.append(str(path))
                if path.exists():
                    asset = self._load_asset(kind, path)
                    self.cache[id] = asset
                    return asset

        print(
            f"asset not found: '{id}' (type='{kind}', name='{name}'). "
            f"tried locations:" + '\n'.join(searched) + "\n",
            f"ensure the asset exists in 'game/assets' or 'engine/assets' and that the id is formatted as '<type>_<name>'."
        )

        return self.get_asset("image_missing")

    def _load_asset(self, kind, path: Path):
        if kind == "image":
            return pygame.image.load(path).convert_alpha()

        if kind == "music":
            pygame.mixer.music.load(path)
            return path  # music is streamed so just return path

        if kind == "sound":
            return pygame.mixer.Sound(path)

        # tilesheet etc later
        return path
    
def _test():
    from engine.services.displayservice import DisplayService
    from engine.services.layer import Layer
    from engine.services.inputservice import InputService
    from engine.services.renderservice import RenderService
    from engine.worldsystem.functions.test import make_test_entity
    from engine.worldsystem.world import World

    ins = InputService()
    ds = DisplayService(
        dimensions=(400,300),
        inputservice = ins,
        target_frame_rate=60,
        caption="asset service test"
    )
    main_layer = Layer(
        dimensions=ds.dimensions
    )
    ds.add_layer(main_layer)
    world = World()
    ass = AssetService()
    rs = RenderService(world, ass)

    test_entity = make_test_entity(world, main_layer, 100,100)

    while ds.running:
        ds.tick()
        rs.tick()