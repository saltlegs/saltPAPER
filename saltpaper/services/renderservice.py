import numpy as np
import moderngl

from saltpaper.services.layer import Layer
from saltpaper.services.assetservice import AssetService
from saltpaper.services.shaders import Shaders
from saltpaper.worldsystem.components.sprite import Sprite


class RenderService():
    def __init__(self, ctx, shaders: Shaders, world, assetservice: AssetService):
        self.ctx = ctx
        self.shaders = shaders
        self.world = world
        self.assetservice = assetservice
        self.render_queue: dict[Layer, list] = {}

        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA, moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA)

    def _queue(self, layer: Layer, pos: tuple[int, int], texture: moderngl.Texture):
        if not self.render_queue.get(layer, None):
            self.render_queue[layer] = []
        self.render_queue[layer].append((texture, pos))

    def _process_queue(self):
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA, moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA)
        for layer, items in self.render_queue.items():
            layer.fbo.use()

            by_texture: dict[int, tuple[moderngl.Texture, list]] = {}
            for texture, pos in items:
                tid = texture.glo
                if tid not in by_texture:
                    by_texture[tid] = (texture, [])
                by_texture[tid][1].append(pos)

            self.shaders.sprite['screen_size'].value = layer.dimensions
            self.shaders.sprite['sprite_texture'].value = 0

            for texture, positions in by_texture.values():
                tw, th = texture.size
                verts = []
                for x, y in positions:
                    x, y, w, h = float(x), float(y), float(tw), float(th)
                    verts += [
                        x,     y,     0.0, 0.0,
                        x + w, y,     1.0, 0.0,
                        x,     y + h, 0.0, 1.0,
                        x + w, y,     1.0, 0.0,
                        x + w, y + h, 1.0, 1.0,
                        x,     y + h, 0.0, 1.0,
                    ]

                vbo = self.ctx.buffer(np.array(verts, dtype='f4').tobytes())
                vao = self.ctx.vertex_array(
                    self.shaders.sprite,
                    [(vbo, '2f 2f', 'in_position', 'in_uv')]
                )
                texture.use(0)
                vao.render(moderngl.TRIANGLES)
                vbo.release()
                vao.release()

        self.render_queue.clear()

    def render(self, layer: Layer, pos: tuple[int, int], asset_id: str):
        texture = self.assetservice.get_asset(asset_id)
        self._queue(layer, pos, texture)

    def _render_renderables(self, renderables):
        for renderable in renderables:
            if not renderable.visible:
                continue
            self.render(renderable.layer, renderable.position, renderable.asset_id)

    def tick(self):
        self._render_renderables(self.world.collect_component_type(Sprite))
        self._process_queue()
