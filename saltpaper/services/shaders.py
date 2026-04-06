
_SPRITE_VERT = """
#version 330
in vec2 in_position;
in vec2 in_uv;

out vec2 uv;

uniform vec2 screen_size;

void main() {
    vec2 clip = (in_position / screen_size) * 2.0 - 1.0;
    clip.y = -clip.y;  // OpenGL Y is flipped vs pygame
    gl_Position = vec4(clip, 0.0, 1.0);
    uv = in_uv;
}
"""

_SPRITE_FRAG = """
#version 330
in vec2 uv;
out vec4 fragColor;

uniform sampler2D sprite_texture;

void main() {
    fragColor = texture(sprite_texture, uv);
}
"""

_COMPOSITE_VERT = """
#version 330
in vec2 in_position;
in vec2 in_uv;

out vec2 uv;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    uv = in_uv;
}
"""

_COMPOSITE_FRAG = """
#version 330
in vec2 uv;
out vec4 fragColor;

uniform sampler2D layer_texture;
uniform float opacity;

void main() {
    vec4 color = texture(layer_texture, uv);
    fragColor = vec4(color.rgb, color.a * opacity);
}
"""

_CIRCLE_VERT = """
#version 330
in vec2 in_position;
in vec2 in_uv;
in vec4 in_color;
in float in_radius;
in float in_width;

out vec2 uv;
out vec4 v_color;
out float v_radius;
out float v_width;

uniform vec2 screen_size;

void main() {
    vec2 clip = (in_position / screen_size) * 2.0 - 1.0;
    clip.y = -clip.y;
    gl_Position = vec4(clip, 0.0, 1.0);
    uv = in_uv;
    v_color = in_color;
    v_radius = in_radius;
    v_width = in_width;
}
"""

_CIRCLE_FRAG = """
#version 330
in vec2 uv;
in vec4 v_color;
in float v_radius;
in float v_width;
out vec4 fragColor;

void main() {
    float dist = length(uv - 0.5) * 2.0 * (v_radius + 1.0);
    float alpha;
    if (v_width <= 0.0) {
        alpha = 1.0 - smoothstep(v_radius - 1.0, v_radius + 1.0, dist);
    } else {
        float inner = v_radius - v_width;
        alpha = smoothstep(inner - 1.0, inner + 1.0, dist)
              - smoothstep(v_radius - 1.0, v_radius + 1.0, dist);
    }
    fragColor = vec4(v_color.rgb, v_color.a * alpha);
}
"""

_ELLIPSE_VERT = """
#version 330
in vec2 in_position;
in vec2 in_uv;
in vec4 in_color;
in vec2 in_axes;
in float in_angle;
in float in_width;

out vec2 uv;
out vec4 v_color;
out vec2 v_axes;
out float v_angle;
out float v_width;

uniform vec2 screen_size;

void main() {
    vec2 clip = (in_position / screen_size) * 2.0 - 1.0;
    clip.y = -clip.y;
    gl_Position = vec4(clip, 0.0, 1.0);
    uv = in_uv;
    v_color = in_color;
    v_axes = in_axes;
    v_angle = in_angle;
    v_width = in_width;
}
"""

_ELLIPSE_FRAG = """
#version 330
in vec2 uv;
in vec4 v_color;
in vec2 v_axes;
in float v_angle;
in float v_width;
out vec4 fragColor;

void main() {
    float max_axis = max(v_axes.x, v_axes.y);
    vec2 centered = (uv - 0.5) * 2.0 * (max_axis + 1.0);
    float c = cos(-v_angle);
    float s = sin(-v_angle);
    vec2 rotated = vec2(c * centered.x - s * centered.y,
                        s * centered.x + c * centered.y);
    float dist = length(rotated / v_axes);
    float aa = 1.5 / max_axis;
    float alpha;
    if (v_width <= 0.0) {
        alpha = 1.0 - smoothstep(1.0 - aa, 1.0 + aa, dist);
    } else {
        float inner = 1.0 - v_width / max_axis;
        alpha = smoothstep(inner - aa, inner + aa, dist)
              - smoothstep(1.0 - aa, 1.0 + aa, dist);
    }
    fragColor = vec4(v_color.rgb, v_color.a * alpha);
}
"""

_LINE_VERT = """
#version 330
in vec2 in_position;
in vec2 in_uv;
in vec4 in_color;
in float in_half_width;
in float in_quad_half_width;

out vec2 uv;
out vec4 v_color;
out float v_half_width;
out float v_quad_half_width;

uniform vec2 screen_size;

void main() {
    vec2 clip = (in_position / screen_size) * 2.0 - 1.0;
    clip.y = -clip.y;
    gl_Position = vec4(clip, 0.0, 1.0);
    uv = in_uv;
    v_color = in_color;
    v_half_width = in_half_width;
    v_quad_half_width = in_quad_half_width;
}
"""

_LINE_FRAG = """
#version 330
in vec2 uv;
in vec4 v_color;
in float v_half_width;
in float v_quad_half_width;
out vec4 fragColor;

void main() {
    float dist = abs(uv.y - 0.5) * 2.0 * v_quad_half_width;
    float alpha = 1.0 - smoothstep(v_half_width - 1.0, v_half_width + 1.0, dist);
    fragColor = vec4(v_color.rgb, v_color.a * alpha);
}
"""

_STRIP_VERT = """
#version 330
in vec2 in_position;
in vec4 in_color;

out vec4 v_color;

uniform vec2 screen_size;

void main() {
    vec2 clip = (in_position / screen_size) * 2.0 - 1.0;
    clip.y = -clip.y;
    gl_Position = vec4(clip, 0.0, 1.0);
    v_color = in_color;
}
"""

_STRIP_FRAG = """
#version 330
in vec4 v_color;
out vec4 fragColor;

void main() {
    fragColor = v_color;
}
"""

class Shaders:
    def __init__(self, ctx):
        self.ctx = ctx
        self.sprite = ctx.program(
            vertex_shader=_SPRITE_VERT,
            fragment_shader=_SPRITE_FRAG
        )
        self.composite = ctx.program(
            vertex_shader=_COMPOSITE_VERT,
            fragment_shader=_COMPOSITE_FRAG
        )
        self.circle = ctx.program(
            vertex_shader=_CIRCLE_VERT,
            fragment_shader=_CIRCLE_FRAG
        )
        self.ellipse_prog = ctx.program(
            vertex_shader=_ELLIPSE_VERT,
            fragment_shader=_ELLIPSE_FRAG
        )
        self.line = ctx.program(
            vertex_shader=_LINE_VERT,
            fragment_shader=_LINE_FRAG
        )
        self.strip = ctx.program(
            vertex_shader=_STRIP_VERT,
            fragment_shader=_STRIP_FRAG
        )
