import pyglet

from . import window

_current = None


class Scene(object):
    tick_interval = 1.0 / 30

    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.actors = set()
        self.on_init()

    def add_sprite(self, img):
        img = pyglet.resource.image(img)
        sprite = pyglet.sprite.Sprite(img, batch=self.batch)
        return sprite

    def add_entity(self, entity):
        entity.sprite.batch = self.batch
        return entity

    def add_actor(self, actor):
        self.actors.add(actor)
        if len(self.actors) == 1:
            pyglet.clock.schedule_interval_soft(self._tick, self.tick_interval)

    def _tick(self, dt):
        kill = set()
        for actor in self.actors:
            if actor(dt) is False:
                kill.add(actor)
        if kill:
            self.actors.difference_update(kill)
        if not self.actors:
            pyglet.clock.unschedule(self._tick)

    def show(self):
        global _current
        if _current:
            _current.hide()
            window.pop_handlers()
        _current = self
        window.push_handlers(self)
        if self.actors:
            pyglet.clock.schedule_interval_soft(self._tick, self.tick_interval)

    def hide(self):
        if self.actors:
            pyglet.clock.unschedule(self._tick)

    def draw(self):
        self.batch.draw()

    def on_init(self):
        pass
