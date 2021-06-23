from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import (
    RenderContext, Fbo, Color,
    ClearColor, ClearBuffers, Rectangle, PushMatrix, PopMatrix
)
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty

from kivymd.app import MDApp

shader_gradient = '''
#ifdef GL_ES
precision mediump float;
#endif

uniform vec2      resolution;           // viewport resolution (in pixels)
uniform float     time;                 // shader playback time (in seconds)

void main(void)
{
    // Normalized pixel coordinates (from 0 to 1)
    vec2 p = gl_FragCoord.xy/resolution.xy;
    
    vec2 q = p - vec2(0.5, 0.5);

    // Time varying pixel color
    vec3 col = 0.7 + 0.2*cos((time)+p.xyx+vec3(0,2,4));
    //vec3 col = mix( vec3(1.0, 0.5, 0.1), vec3(0.2, 0.9, 0.5), p.y);
    
    //col *= length(q);

    gl_FragColor = vec4(col, 1.0);
}
'''

KV = '''
#: import ew kivy.uix.effectwidget
Screen:
    FloatLayout:

        ShaderWidget:
            id: shader_widget
            pos_hint: {"center_x":.5, "center_y":.5}

        BoxLayout:
            size_hint: .5, .5
            orientation: "vertical"
            pos_hint: {"center_x":.5, "center_y":.5}

            BoxLayout:
                MDLabel:
                    text: "Hello World"
                    font_style: "H3"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1,1,1,1

            BoxLayout:
                orientation: "vertical"

                AnchorLayout:
                    MDRaisedButton:
                        text: "Button1"
                        on_release:
                            print("Button1")
                AnchorLayout:
                    MDRaisedButton:
                        text: "Button2"
                        on_release:
                            print("Button2")
'''


class ShaderWidget(BoxLayout):

    fs = StringProperty(None)

    texture = ObjectProperty(None)

    def __init__(self, **kwargs):

        self.canvas = RenderContext(use_parent_projection=True,
                                    use_parent_modelview=True,
                                    use_parent_frag_modelview=True
                                    )

        with self.canvas:
            self.fbo = Fbo(size=self.size)
            self.fbo_color = Color(1, 1, 1, 1)
            self.fbo_rect = Rectangle(size=self.size, pos=self.pos)

        # with self.fbo.before:
        #     PushMatrix()

        with self.fbo:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()
            #self.fbo_rectangle = Rectangle(size=self.size)
        
        # with self.fbo.after:
        #     PopMatrix()

        super(ShaderWidget, self).__init__(**kwargs)

        self.fs = shader_gradient
        Clock.schedule_interval(self.update_glsl, 0)

    def update_glsl(self, *largs):
        self.canvas['time'] = Clock.get_boottime()
        self.canvas['resolution'] = [float(v) for v in self.size]

    def on_fs(self, instance, value):

        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('compilation failed')

    def add_widget(self, *args, **kwargs):
        c = self.canvas
        self.canvas = self.fbo
        super(ShaderWidget, self).add_widget(*args, **kwargs)
        self.canvas = c

    def remove_widget(self, *args, **kwargs):
        c = self.canvas
        self.canvas = self.fbo
        super(ShaderWidget, self).remove_widget(*args, **kwargs)
        self.canvas = c

    def on_size(self, instance, value):
        self.fbo.size = value
        self.texture = self.fbo.texture
        self.fbo_rect.size = value

    def on_pos(self, instance, value):
        self.fbo_rect.pos = value

    def on_texture(self, instance, value):
        self.fbo_rect.texture = value


class ShaderTestApp(MDApp):
    def build(self):
        return Builder.load_string(KV)


ShaderTestApp().run()
