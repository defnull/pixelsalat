import pyglet
from pyglet.gl import gl

window = pyglet.window.Window(resizable=True)
from . import scene

pyglet.clock.set_fps_limit(30)
fps_display = pyglet.clock.ClockDisplay()

keys = pyglet.window.key.KeyStateHandler()
window.push_handlers(keys)


@window.event
def on_draw():
    window.clear()
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

    if scene._current:
        scene._current.draw()
    fps_display.draw()


from . import game
