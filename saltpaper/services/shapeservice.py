import math
import numpy as np
import moderngl

from saltpaper.services.layer import Layer
from saltpaper.services.shaders import Shaders


def _norm_color(color):
    if len(color) == 3:
        return (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0, 1.0)
    return (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0, color[3] / 255.0)


class ShapeService():
    def __init__(self, ctx, shaders: Shaders):
        self.ctx = ctx
        self.shaders = shaders
        self.queue: dict = {}
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA, moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA)

    def _ensure_layer(self, layer: Layer):
        if layer not in self.queue:
            self.queue[layer] = {'circle': [], 'ellipse': [], 'line': [], 'strip': []}

    # --- public API (mirrors pygame.draw, swap surface for layer) ---

    def circle(self, layer: Layer, color, center, radius, width=0):
        """pygame.draw.circle equivalent. width=0 means filled."""
        self._ensure_layer(layer)
        self.queue[layer]['circle'].append(self._circle_verts(color, center, radius, width))

    def aacircle(self, layer: Layer, color, center, radius, width=0):
        """Antialiased circle — same as circle(), AA is always on."""
        self.circle(layer, color, center, radius, width)

    def ellipse(self, layer: Layer, color, center, axes, angle=0, width=0):
        """
        Ellipse with rotation support.
        center: (x, y) in pixels
        axes: (semi_x, semi_y) in pixels (half-widths)
        angle: rotation in radians
        width: 0 = filled, >0 = outline width in pixels
        """
        self._ensure_layer(layer)
        self.queue[layer]['ellipse'].append(self._ellipse_verts(color, center, axes, angle, width))

    def line(self, layer: Layer, color, start_pos, end_pos, width=1):
        """pygame.draw.line equivalent."""
        self._ensure_layer(layer)
        seg = self._segment_verts(color, start_pos, end_pos, width)
        if seg:
            self.queue[layer]['line'].append(np.array(seg, dtype='f4'))

    def lines(self, layer: Layer, color, closed, points, width=1):
        """pygame.draw.lines equivalent."""
        pts = list(points)
        if closed and len(pts) >= 2:
            pts = pts + [pts[0]]
        if len(pts) < 2:
            return
        self._ensure_layer(layer)
        result = self._polyline_verts(color, pts, width)
        if len(result):
            self.queue[layer]['line'].append(result)

    def aaline(self, layer: Layer, color, start_pos, end_pos):
        """pygame.draw.aaline equivalent — always antialiased."""
        self.line(layer, color, start_pos, end_pos, 1)

    def aalines(self, layer: Layer, color, closed, points):
        """pygame.draw.aalines equivalent — always antialiased."""
        self.lines(layer, color, closed, points, 1)

    def polyline_strip(self, layer: Layer, color, points):
        """
        Fast GL_LINE_STRIP polyline. Much cheaper than aalines for long trails.
        points: numpy array (N, 2) or list of (x, y) in screen pixels.
        Uses native GL lines — no quad expansion, 1 vertex per point.
        """
        pts = np.asarray(points, dtype='f4')
        if len(pts) < 2:
            return
        col = _norm_color(color)
        N = len(pts)
        verts = np.empty((N, 6), dtype='f4')
        verts[:, :2] = pts
        verts[:, 2:] = col
        self._ensure_layer(layer)
        self.queue[layer]['strip'].append(verts)

    # --- vertex builders ---

    def _circle_verts(self, color, center, radius, width):
        pad = 1.0
        r = float(radius)
        w = float(width)
        cx, cy = float(center[0]), float(center[1])
        half = r + pad
        col = _norm_color(color)
        x0, y0 = cx - half, cy - half
        x1, y1 = cx + half, cy + half
        # vertex format: x y u v r g b a radius width  (10 floats)
        v = [*col, r, w]
        return np.array([
            x0, y0, 0.0, 0.0, *v,
            x1, y0, 1.0, 0.0, *v,
            x0, y1, 0.0, 1.0, *v,
            x1, y0, 1.0, 0.0, *v,
            x1, y1, 1.0, 1.0, *v,
            x0, y1, 0.0, 1.0, *v,
        ], dtype='f4')

    def _ellipse_verts(self, color, center, axes, angle, width):
        pad = 1.0
        ax, ay = float(axes[0]), float(axes[1])
        ang = float(angle)
        w = float(width)
        cx, cy = float(center[0]), float(center[1])
        half = max(ax, ay) + pad
        col = _norm_color(color)
        x0, y0 = cx - half, cy - half
        x1, y1 = cx + half, cy + half
        # vertex format: x y u v r g b a semi_x semi_y angle width  (12 floats)
        v = [*col, ax, ay, ang, w]
        return np.array([
            x0, y0, 0.0, 0.0, *v,
            x1, y0, 1.0, 0.0, *v,
            x0, y1, 0.0, 1.0, *v,
            x1, y0, 1.0, 0.0, *v,
            x1, y1, 1.0, 1.0, *v,
            x0, y1, 0.0, 1.0, *v,
        ], dtype='f4')

    def _segment_verts(self, color, a, b, width):
        ax, ay = float(a[0]), float(a[1])
        bx, by = float(b[0]), float(b[1])
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        if length == 0:
            return []
        dx /= length
        dy /= length
        nx, ny = -dy, dx
        hw = max(float(width) / 2.0, 0.5)
        qhw = hw + 1.0
        col = _norm_color(color)
        # vertex format: x y u v r g b a half_width quad_half_width  (10 floats)
        v = [*col, hw, qhw]
        return [
            ax - nx * qhw, ay - ny * qhw, 0.0, 0.0, *v,
            ax + nx * qhw, ay + ny * qhw, 0.0, 1.0, *v,
            bx - nx * qhw, by - ny * qhw, 1.0, 0.0, *v,
            ax + nx * qhw, ay + ny * qhw, 0.0, 1.0, *v,
            bx + nx * qhw, by + ny * qhw, 1.0, 1.0, *v,
            bx - nx * qhw, by - ny * qhw, 1.0, 0.0, *v,
        ]

    def _polyline_verts(self, color, points, width):
        """Vectorised version of _segment_verts for a whole polyline (numpy)."""
        pts = np.array(points, dtype='f4')    # (N, 2)
        a = pts[:-1]                           # segment starts (N-1, 2)
        b = pts[1:]                            # segment ends   (N-1, 2)
        diff = b - a
        lengths = np.hypot(diff[:, 0], diff[:, 1])
        mask = lengths > 0
        a, b, diff, lengths = a[mask], b[mask], diff[mask], lengths[mask]
        if len(a) == 0:
            return []
        d = diff / lengths[:, np.newaxis]           # unit direction
        n = np.column_stack([-d[:, 1], d[:, 0]])    # unit normal
        hw = max(float(width) / 2.0, 0.5)
        qhw = hw + 1.0
        col = _norm_color(color)
        nq = n * qhw                                # (N-1, 2)
        # 6 vertices per segment: two triangles (0,1,2) and (1,3,2)
        #   0 = a - nq   1 = a + nq   2 = b - nq   3 = b + nq
        c0 = a - nq;  c1 = a + nq;  c2 = b - nq;  c3 = b + nq
        N = len(a)
        pos = np.empty((N * 6, 2), dtype='f4')
        pos[0::6] = c0;  pos[1::6] = c1;  pos[2::6] = c2
        pos[3::6] = c1;  pos[4::6] = c3;  pos[5::6] = c2
        uv_tile = np.tile([[0,0],[0,1],[1,0],[0,1],[1,1],[1,0]], (N, 1)).astype('f4')
        colors  = np.full((N * 6, 4), col, dtype='f4')
        hw_col  = np.full((N * 6, 1), hw,  dtype='f4')
        qhw_col = np.full((N * 6, 1), qhw, dtype='f4')
        data = np.concatenate([pos, uv_tile, colors, hw_col, qhw_col], axis=1)
        return data.ravel()

    # --- flush ---

    def tick(self):
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA, moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA)
        for layer, types in self.queue.items():
            layer.fbo.use()
            W, H = layer.dimensions

            if types['circle']:
                prog = self.shaders.circle
                prog['screen_size'].value = (W, H)
                data = np.concatenate(types['circle'])
                vbo = self.ctx.buffer(data.tobytes())
                vao = self.ctx.vertex_array(
                    prog,
                    [(vbo, '2f 2f 4f 1f 1f', 'in_position', 'in_uv', 'in_color', 'in_radius', 'in_width')]
                )
                vao.render(moderngl.TRIANGLES)
                vbo.release()
                vao.release()

            if types['ellipse']:
                prog = self.shaders.ellipse_prog
                prog['screen_size'].value = (W, H)
                data = np.concatenate(types['ellipse'])
                vbo = self.ctx.buffer(data.tobytes())
                vao = self.ctx.vertex_array(
                    prog,
                    [(vbo, '2f 2f 4f 2f 1f 1f', 'in_position', 'in_uv', 'in_color', 'in_axes', 'in_angle', 'in_width')]
                )
                vao.render(moderngl.TRIANGLES)
                vbo.release()
                vao.release()

            if types['line']:
                prog = self.shaders.line
                prog['screen_size'].value = (W, H)
                data = np.concatenate(types['line'])
                vbo = self.ctx.buffer(data.tobytes())
                vao = self.ctx.vertex_array(
                    prog,
                    [(vbo, '2f 2f 4f 1f 1f', 'in_position', 'in_uv', 'in_color', 'in_half_width', 'in_quad_half_width')]
                )
                vao.render(moderngl.TRIANGLES)
                vbo.release()
                vao.release()

            if types['strip']:
                prog = self.shaders.strip
                prog['screen_size'].value = (W, H)
                # concatenate all strips into one VBO, track per-strip offsets
                strips = types['strip']
                counts = [len(s) for s in strips]
                starts = [0] + list(np.cumsum(counts[:-1]))
                big = np.concatenate(strips)  # (total_verts, 6)
                vbo = self.ctx.buffer(big.tobytes())
                vao = self.ctx.vertex_array(
                    prog,
                    [(vbo, '2f 4f', 'in_position', 'in_color')]
                )
                for first, count in zip(starts, counts):
                    vao.render(moderngl.LINE_STRIP, vertices=count, first=first)
                vbo.release()
                vao.release()

        self.queue.clear()
