import pygame
import copy
import math

from pygame import transform
import utils
import sys
import game

updatable = []
drawable = []
gameLayer = []
impassableLayer = []
playerSpawnPoints = []
enemySpawnPoints = []

tiles = {
#    'floor' : pygame.image.load('floor.png'),
    'destructible' : pygame.image.load('brick.png'),
    'undestructible' : pygame.image.load('iron.png'),
    'water' : pygame.image.load('water.png'),
    'motherBase' : pygame.image.load('base.png'),
    'coin' : pygame.image.load('coin.png')
}

class Transform:
    def __init__(self, x, y, isNormal = False):
        
        if not isNormal:
            self.m_x, self.m_y = x, y
            self.x, self.y = x * utils.MAP_UNIT_SCALE, y * utils.MAP_UNIT_SCALE
        else:
            self.m_x, self.m_y = utils.getMatrixCoord(x), utils.getMatrixCoord(y)
            self.x, self.y = x, y
        self.rot = 0
        self.size = (1, 1)
    
    def getPosRot(self):
        x, y = self.getCenterPos()
        return (x, y, self.rot)

    def getCenterPos(self):
        return self.x + utils.MAP_UNIT_SCALE/2, self.y +utils.MAP_UNIT_SCALE/2

    def getMatrixPos(self):
        return (self.m_x, self.m_y)

    def getRot(self):
        return self.rot
    
    def getSize(self):
        w, h = self.size
        return (w * utils.MAP_UNIT_SCALE, h * utils.MAP_UNIT_SCALE)

    def setPos(self, x, y):
        self.x, self.y = x, y

        nm_x, nm_y = utils.getMatrixCoord(x), utils.getMatrixCoord(y)
        # print('----')
        # print(nm_x, nm_y)
        # print(self.m_x, self.m_y)
        if nm_x != self.m_x or nm_y != self.m_y:
            map = game.Game.getInstance().map
            # print(map.mapMatrix[self.m_y][self.m_x])
            # print(map.mapMatrix[nm_y][nm_x])
            map.mapMatrix[self.m_y][self.m_x].remove(self)
            map.mapMatrix[nm_y][nm_x].append(self)

        self.m_x = nm_x
        self.m_y = nm_y

class MyRect(pygame.Rect):
    def __init__(self, parent, tileect = None,sizes = None):
        if tileect is None and sizes is not None:
            left, top, width, height = sizes
            super().__init__((left, top), (width, height))
        elif tileect is not None and sizes is None:
            super().__init__(tileect)
        self.parent = parent

class Tile(Transform):
    weight = 1
    def __init__(self, coords, image, parent, tileSize = 1) -> None:
        x, y = coords
        super().__init__(x, y)
        self.size = (1,1)

        # self.image = utils.createSimpleSprite(color, tileSize)
        if image:
            self.image = utils.copyImage(tileSize, image)
        self._createRect(tileSize, parent)

    def getSize(self):
        w, h = self.size
        return (w * utils.MAP_UNIT_SCALE, h * utils.MAP_UNIT_SCALE)

    def getCenterPos(self):
        centerOffset = utils.MAP_UNIT_SCALE/2
        # x, y = utils.screenScaleXY((self.x, self.y))
        x, y = self.x, self.y
        x += centerOffset * self.size[0]
        y += centerOffset * self.size[1]
        return (x, y)

    def _createRect(self, size, parent):
        scale = utils.WINDOW_SCALE * utils.MAP_UNIT_SCALE
        newRect = pygame.Rect(self.x * utils.WINDOW_SCALE + utils.OFFSET_X, self.y * utils.WINDOW_SCALE + utils.OFFSET_Y, 
            scale * size, scale * size)
        self.rect = MyRect(parent, newRect)

class Point(Tile):
    weight = 1
    def __init__(self, coords) -> None:
        super().__init__(coords, tiles['coin'], self)


class Impassable():
    pass

class Undestroyable(Tile, Impassable):
    weight = 100
    def __init__(self, coords, image) -> None:
        super().__init__(coords, tiles['undestructible'], self)
    

class Destroyable(Tile, Impassable):
    weight = 1/0.33
    def __init__(self, coords, image) -> None:
        super().__init__(coords, tiles['destructible'], self)

    def kill(self):
        map = game.Game.getInstance().map
        map.mapMatrix[self.m_y][self.m_x].remove(self)

        gameLayer.remove(self.rect)
        impassableLayer.remove(self)
        drawable.remove(self)

class Water(Tile, Impassable):
    weight = 0
    def __init__(self, coords, image) -> None:
        super().__init__(coords, tiles['water'], self)
    
class MotherBase(Tile, Impassable):
    weight = 0
    def __init__(self, coords, image) -> None:
        super().__init__(coords, tiles['motherBase'], self, 3)
        
    def kill(self):
        map = game.Game.getInstance().map
        map.mapMatrix[self.m_y][self.m_x].remove(self)
        gameLayer.remove(self.rect)
        drawable.remove(self)
        impassableLayer.remove(self)
        # # print('you\'ve lost')
        sys.exit()

class Tank(Transform, Impassable):
    def __init__(self, image, x = 10, y = 10):
        super().__init__(x, y)
        self.fireProj = ProjEmitter(Projectile, './bullet.png', self)
        self.image = pygame.transform.rotate(pygame.image.load(image), -90)
        self.rect = MyRect(self, self.image.get_rect())
        self.size = (1, 1)
        self.resize(None)

        self.direction = [0.0, -1.0]
        self.velocity = [0.0, 0.0]
        self.speed = 4
        self.firerate = 0.75
        self.timeUntilShot = 0.0

    def __eq__(self, other):
        return id(self) == id(other)

    def kill(self):
        map = game.Game.getInstance().map
        map.mapMatrix[self.m_y][self.m_x].remove(self)
        gameLayer.remove(self)
        impassableLayer.remove(self)

    def action(self):
        if self.timeUntilShot < utils.time:
            self.timeUntilShot = utils.time + self.firerate
            self.fireProj.emit(self.direction)

    def setDirection(self, vec, keypressed):
        self.direction = vec
        if keypressed:
            self.velocity = [vec[0] * self.speed * utils.MAP_UNIT_SCALE,
             vec[1] * self.speed * utils.MAP_UNIT_SCALE]
        else:
            self.velocity = [0, 0]

    def getCenterPos(self):
        # width, height = self.size
        cen_off = utils.MAP_UNIT_SCALE/2
        return (self.x + self.size[0] * cen_off, self.y + self.size[1] * cen_off)
        #return (self.x, self.y)

    def resize(self, size):
        if type(size) is tuple:
            self.image = pygame.transform.smoothscale(self.image, size)
        elif type(size) is float:
            self.image = pygame.transform.smoothscale(self.image, 
                (round(self.rect.w * size), round(self.rect.h * size)))
        elif size is None:
            scale = utils.WINDOW_SCALE * utils.MAP_UNIT_SCALE
            self.image = pygame.transform.smoothscale(self.image, (round(scale * self.size[0]), round(scale * self.size[1])))
        self.rect = MyRect(self, self.image.get_rect())

    def rotate(self):
        vel = self.velocity
        rot = self.rot
        if vel[0] > 0:
            self.rot = 0
        elif vel[0] < 0:
            self.rot = 180
        elif vel[1] > 0:
            self.rot = 270
        elif vel[1] < 0:
            self.rot = 90

        rot = self.rot - rot

        self.image = pygame.transform.rotate(self.image, rot)
        self.rect = MyRect(self, self.image.get_rect())

    def onCollide(self, collider):
        if collider.parent == self:
            return
        tile = collider.parent
        # # print(type(tile))
        x1, y1 = tile.getCenterPos()
        x2, y2 = self.getCenterPos()
        # # print(x, y)
        w1, h1 = self.getSize()
        w2, h2 = tile.getSize()
        
        # print(x1, x2)
        diffx = x1-x2 - self.velocity[0] * 1/utils.FPS
        diffy = y1-y2 - self.velocity[1] * 1/utils.FPS
        print(diffx, diffy)
        signx = diffx/abs(diffx) if diffx else 0
        signy = diffy/abs(diffy) if diffy else 0

        if abs(diffx) < w1/2 + w2/2:
            if diffx < 0 and self.velocity[0] < 0 \
                or diffx > 0 and self.velocity[0] > 0:
                # print('stopping horizontal movement')
                self.velocity[0] = 0
            
        if abs(diffy) < h1/2 + h2/2:
            if diffy < 0 and self.velocity[1] < 0 \
                or diffy > 0 and self.velocity[1] > 0:
                # print('stopping vertical movement')
                self.velocity[1] = 0
                
        self.x += 0.0008 * -signx * abs((w1+w2) * diffx)
        self.y += 0.0008 * -signy * abs((h1+h2) * diffy)

    def update(self):
        indx = self.rect.collidelist(impassableLayer)
        vel = self.velocity
        if vel[0] != 0 or vel[1] != 0: 
            self.rotate()

        if indx != -1:
            self.onCollide(impassableLayer[indx])

        self.setPos(self.x + vel[0] / utils.FPS, self.y + vel[1] / utils.FPS)
        self.rect.topleft = [round(self.x * utils.WINDOW_SCALE) + utils.OFFSET_X, 
             round(self.y * utils.WINDOW_SCALE) + utils.OFFSET_Y]
    

class ProjEmitter:
    def __init__(self, proj, imagePath, parent):
        self.proj = proj
        self.image = pygame.image.load(imagePath)
        self.parent = parent

    def emit(self, direction):
        x, y, rot = self.parent.getPosRot()
        proj = self.proj(x, y, self.image.copy(), self.parent, direction)
        # x, y = self.parent.getCenterPos()
        # rot = self.parent.getRot()
        proj.resize(None)
        proj.setPosRot(x, y, rot - 90)

        map = game.Game.getInstance().map
        map.mapMatrix[proj.m_y][proj.m_x].append(proj)
        
        gameLayer.append(proj)
        updatable.append(proj)
        drawable.append(proj)

class Projectile(Transform):
    weight = 1.5
    def __init__(self, x, y, image, parent, direction):
        super().__init__(x, y, True)
        self.parent = parent
        self.direction = direction

        self.lifetime = 0.6
        self.damage = 1
        self.penetration = 1
        self.speed = 30
        self.size = (0.5, 0.75)
        
        self.enabled = True

        self.setImage(image)

    def __eq__(self, other):
        return id(self) == id(other)

    def onCollide(self, collider):
        tile = collider.parent
        if tile == self.parent:
            return
        tileType = type(tile)
        if tileType is Undestroyable:
            pass
        elif tileType is Point:
            return
        elif tileType is Destroyable:
            tile.kill()
        elif tileType is Tank:
            tile.kill()
        elif tileType is MotherBase:
            tile.kill()
        self.kill()
        return True

    def kill(self):
        map = game.Game.getInstance().map
        map.mapMatrix[self.m_y][self.m_x].remove(self)
        drawable.remove(self)
        updatable.remove(self)
        gameLayer.remove(self)

    def setImageFile(self, imagePath):
        self.image = pygame.image.load(imagePath)
        self.rect = MyRect(self, self.image.get_rect())

    def setImage(self, image):
        self.image = image
        self.rect = MyRect(self, self.image.get_rect())

    def setPosRot(self, x, y, rot):
        self.setPos(x, y)
        self.image = pygame.transform.rotate(self.image, rot)
        self.rect = MyRect(self, self.image.get_rect())

    def resize(self, size):
        if type(size) is tuple:
            self.image = pygame.transform.smoothscale(self.image, size)
        elif type(size) is float:
            self.image = pygame.transform.smoothscale(self.image, 
                (round(self.rect.w * size), round(self.rect.h * size)))
        elif size is None:
            size = utils.WINDOW_SCALE * utils.MAP_UNIT_SCALE
            self.image = pygame.transform.smoothscale(self.image, (round(size * self.size[0]), round(size * self.size[1])))
        

        self.rect = MyRect(self, self.image.get_rect())

    def update(self):
        if self.enabled:

            if self.lifetime <= 0:
                self.kill()
                return

            indx = self.rect.collidelist(gameLayer)
            if indx != -1:
                if self.onCollide(gameLayer[indx]):
                    return

            self.setPos(self.x + self.direction[0] * self.speed * utils.MAP_UNIT_SCALE / utils.FPS, 
                 self.y + self.direction[1] * self.speed * utils.MAP_UNIT_SCALE / utils.FPS)

            self.rect.center = [round(self.x * utils.WINDOW_SCALE) + utils.OFFSET_X,
                 round(self.y * utils.WINDOW_SCALE) + utils.OFFSET_Y]

            self.lifetime -= 1.0/utils.FPS
            
class SpawnPoint(Tile):
    def __init__(self, enemy, coords) -> None:
        super().__init__(coords, None, self)
        self.enemy = enemy
    
class Map:
    def __init__(self, isMaze = True, mapfile = 'simple.lay', ):
        
        # TODO 
        # карта состоит из кубиков, 1 кубик 1/4 танка. 
        # Сам кубик, если может получать урон, то делиться еще на 4 мини-кубика
        # Выстрел каждый фрэйм проверяет касаеться ли он чего либо, при попадании удаляет ряд из 4х мини-кубиков
        
        self.isMaze = isMaze
        self._rawMap = open('./maps/' + mapfile, 'r').read()
        self.mapMatrix = []

    def _getBoardSize(self):
        scale = utils.MAP_UNIT_SCALE
        if self.isMaze:
            return utils.MAZE_X * scale, utils.MAZE_Y * scale
        rows = self._rawMap.split('\n')
        y = len(rows)
        x = len(rows[0])

        return (x * scale, y * scale)

    def _initLayers(self):
        drawableList = []
        for j, row in enumerate(self.mapMatrix):
            for i, col in enumerate(row):
                for tile in col:
                    if isinstance(tile, Undestroyable):
                        gameLayer.append(tile.rect)
                        impassableLayer.append(tile.rect)
                        drawableList.append(tile)
                    elif isinstance(tile, Destroyable):
                        gameLayer.append(tile.rect)
                        impassableLayer.append(tile.rect)
                        drawableList.append(tile)
                    elif isinstance(tile, Water):
                        impassableLayer.append(tile.rect)
                        drawableList.append(tile)
                    elif isinstance(tile, SpawnPoint) and tile.enemy:
                        enemySpawnPoints.append(tile)
                    elif isinstance(tile, SpawnPoint) and not tile.enemy:
                        playerSpawnPoints.append(tile)
                    elif isinstance(tile, MotherBase):
                        gameLayer.append(tile.rect)
                        drawableList.append(tile)
        global drawable 
        drawable += drawableList

    def init(self):
        if self.isMaze:
            self.mapMatrix = utils.make_maze()
            self._initLayers()
            return
        rows = self._rawMap.split('\n')

        for j, row in enumerate(rows):
            self.mapMatrix.append([])
            for i, c in enumerate(row):
                if c == 'X':
                    tile = Undestroyable((i, j), utils.WHITE)
                    self.mapMatrix[j].append([tile])
                elif c == 'O':
                    self.mapMatrix[j].append([])
                elif c == 'D':
                    tile = Destroyable((i, j), utils.ORANGE)
                    self.mapMatrix[j].append([tile])
                elif c == 'W':
                    tile = Water((i, j), utils.BLUE)
                    self.mapMatrix[j].append([tile])
                elif c == 'E':
                    tile = SpawnPoint(True,(i, j))
                    self.mapMatrix[j].append([])
                elif c == 'P':
                    tile = SpawnPoint(False,(i, j))
                    self.mapMatrix[j].append([])
                elif c == 'M':
                    tile = MotherBase((i - 1, j - 1), utils.GREY)
                    self.mapMatrix[j].append([tile])

        self._initLayers()

    