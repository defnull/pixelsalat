import json
import time
import pyglet
from pyglet.gl import gl
from pyglet.window import key, mouse
from loot import keys

from loot.scene import Scene


class Tile(object):
    def __init__(self, map, x, y):
        self.map = map
        self.size = 32
        self.x = x
        self.y = y
        self._tex = 0
        self.is_wall = False
        self.sprite = pyglet.sprite.Sprite(self.map.grid[0])
        self.sprite.position = x * self.size, y * self.size
        self.sprite.batch = self.map.batch

    def _get_tex(self):
        return self._tex

    def _set_tex(self, n):
        self._tex = n % len(self.map.grid)
        self.sprite.image = self.map.grid[self._tex]

    def dump(self):
        return {
            'x': self.x,
            'y': self.y,
            'tex': self._tex
        }

    @classmethod
    def load(cls, map, data):
        tile = cls(map, data['x'], data['y'])
        tile.tex = data['tex']
        return tile

    tex = property(_get_tex, _set_tex)


class TileMap(object):
    def __init__(self, img, w, h):
        self.batch = pyglet.graphics.Batch()
        self.width = w
        self.height = h
        self.img = img
        self.image = pyglet.image.load(self.img)
        self.image_grid = pyglet.image.ImageGrid(self.image, 16, 16)
        self.grid = pyglet.image.TextureGrid(self.image_grid)
        self.tiles = {}

    def dump(self):
        return {
            'width': self.width,
            'height': self.height,
            'image': self.img,
            'tiles': [
                self.tiles[key].dump() for key in sorted(self.tiles)
                ]
        }

    @classmethod
    def load(cls, data):
        tilemap = cls(data['image'], data['width'], data['height'])
        for tile_data in data['tiles']:
            tile = Tile.load(tilemap, tile_data)
            tilemap.tiles[tile.x, tile.y] = tile
        return tilemap

    def get_tile_at(self, x, y):
        pos = x // 32, y // 32
        if pos not in self.tiles:
            self.tiles[pos] = Tile(self, *pos)
        return self.tiles[pos]

    def draw(self):
        self.batch.draw()


class Hero(object):
    def __init__(self):
        image = pyglet.image.load('art/hero.png')
        self.grid = pyglet.image.ImageGrid(image, 4, 3)
        self.sprite = pyglet.sprite.Sprite(self.grid[6])
        self.sprite.scale = 2
        self.running = False
        self.soffset = 0

    def move(self, dx, dy):
        self.running = dx or dy
        self.sprite.x += dx
        self.sprite.y += dy

        if dx < 0:
            self.soffset = 0
        if dx > 0:
            self.soffset = 6
        if dy > 0:
            self.soffset = 9
        if dy < 0:
            self.soffset = 3

        if self.running:
            frame = int(time.time() * 5) % 3
            self.sprite.image = self.grid[self.soffset + frame]


class LevelEditorScene(Scene):
    def on_init(self):
        try:
            self.load_map()
        except IOError:
            self.map = TileMap('art/tiles.png', 16, 16)

        self.brush_sprite = pyglet.sprite.Sprite(self.map.grid[0])
        self.brush = 0

        self.hero = Hero()
        self.add_entity(self.hero)
        self.add_actor(self.tick)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        tile = self.map.get_tile_at(x, y)
        tile.tex = self.brush

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons & mouse.RIGHT:
            tile = self.map.get_tile_at(x, y)
            self.brush = tile.tex

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y > 0:
            self.brush += 1
        elif scroll_y < 0:
            self.brush -= 1
        self.brush %= len(self.map.image_grid)
        self.brush_sprite.image = self.map.grid[self.brush]

    def on_key_press(self, symbol, modifier):
        if symbol == key.S:
            self.save_map()

    def on_resize(self, width, height):
        self.brush_sprite.x = width - self.brush_sprite.width
        self.brush_sprite.y = height - self.brush_sprite.height

    def save_map(self):
        fname = 'level.json'
        with open(fname, 'wb') as fp:
            json.dump(self.map.dump(), fp)
            print("Saved ...")

    def load_map(self):
        fname = 'level.json'
        with open(fname, 'rb') as fp:
            self.map = TileMap.load(json.load(fp))

    def tick(self, dt):
        speed = dt * 50
        dx, dy = 0, 0
        if keys[key.LEFT]:
            dx -= speed
        if keys[key.RIGHT]:
            dx += speed
        if keys[key.UP]:
            dy += speed
        if keys[key.DOWN]:
            dy -= speed
        self.hero.move(dx, dy)

    def draw(self):
        self.map.draw()
        self.brush_sprite.draw()
        Scene.draw(self)


LevelEditorScene().show()
