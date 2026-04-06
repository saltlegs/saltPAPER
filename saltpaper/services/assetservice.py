import pygame
import moderngl
import os
from pathlib import Path

cwd = Path.cwd()
filetypes = {
    "image":    [".png", ".jpg", ".bmp", ".gif"],
    "anim":     [".png", ".jpg", ".bmp", ".gif"],
    "music":    [".wav", ".ogg", ".mp3"],
    "sound":    [".wav", ".ogg", ".mp3"],
}

class AssetService():
    def __init__(self, ctx, assets_folder_path):
        self.ctx = ctx
        self.cache = {}
        self.roots = []

        self.set_assets_folder(assets_folder_path)

    def set_assets_folder(self, path):
        path = Path(path)
        self.roots.append(path)

    def get_kind(self, asset_id):
        kind, name = id.split("_", 1)
        return kind

    def get_asset(self, id, frame=0):
        asset = self.cache.get(id)

        kind, name = id.split("_", 1)


        if asset is not None:
            return asset if kind is not "anim" else asset[frame]
        
        extensions = filetypes.get(kind)

        if extensions is None:
            raise ValueError(f"unknown asset type: {kind}")

        searched = []
        for root in self.roots:
            for ext in extensions:
                if kind == "anim":
                    i = 0
                    self.cache[id] = []
                    while i >= 0:
                        path = root / kind / name / f"{name}_{i}{ext}"
                        searched.append(str(path))
                        if path.exists():
                            asset = self._load_asset(kind, path)
                            self.cache[id].append(asset)
                        else:
                            i = -1
                    if len(self.cache[id]) <= 1: raise ValueError("animated asset must have more than one frame")
                    return self.cache[id][frame]
                else:
                    path = root / kind / f"{name}{ext}"
                    searched.append(str(path))
                    if path.exists():
                        asset = self._load_asset(kind, path)
                        self.cache[id] = asset
                        return asset

        if id == "image_missing":
            raise FileNotFoundError(f"No /image/missing.png is set")

        print(
            f"asset not found: '{id}' (type='{kind}', name='{name}'). "
            f"tried locations:" + '\n'.join(searched) + "\n",
            f"ensure the asset exists in 'game/assets' or 'engine/assets' and that the id is formatted as '<type>_<name>'."
        )

        try:
            return self.get_asset("image_missing")
        except FileNotFoundError:
            raise FileNotFoundError(f"No /image/missing.png is set")

    def _load_asset(self, kind, path: Path):
        if kind == "image":
            surf = pygame.image.load(path).convert_alpha()
            w, h = surf.get_size()
            data = pygame.image.tobytes(surf, "RGBA", False)
            texture = self.ctx.texture((w, h), 4, data)
            texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
            return texture

        if kind == "music":
            pygame.mixer.music.load(path)
            return path  # music is streamed so just return path

        if kind == "sound":
            return pygame.mixer.Sound(path)

        # tilesheet etc later
        return path
    
