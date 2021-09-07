import pygame
import copy
import math
import utils
import sys

updateable = []
drawable = []
gameLayer = []
impassableLayer = []

# tiles = {
#     'floor' : pygame.image.load('floor.png'),
#     'destructible' : pygame.image.load('brick.png'),
#     'undestructible' : pygame.image.load('iron.png'),
#     'water' : pygame.image.load('water.png'),
#     'motherBase' : pygame.image.load('base.png')
# }

class Transform:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.rot = 0
        self.size = (1, 1)
    
    def getPosRot(self):
        return (self.x, self.y, self.rot)

    def getRot(self):
        return self.rot
    
    def getSize(self):
        w, h = self.size
        return (w * utils.MAP_UNIT_SCALE, h * utils.MAP_UNIT_SCALE)

class MyRect(pygame.Rect):
    def __init__(self, parent, object = None,sizes = None):
        if object is None and sizes is not None:
            left, top, width, height = sizes
            super().__init__((left, top), (width, height))
        elif object is not None and sizes is None:
            super().__init__(object)
        self.parent = parent

class Tile:
    def __init__(self, coords, color, parent, tileSize = 1) -> None:
        self.size = (1,1)
        self.x, self.y = coords 
        self.image = utils.createSimpleSprite(color, tileSize)
        self._createRect(tileSize, parent)

    def getPos(self):
        return (self.x, self.y)

    def getSize(self):
        w, h = self.size
        return (w * utils.MAP_UNIT_SCALE, h * utils.MAP_UNIT_SCALE)

    def getCentralPos(self):
        centerOffset = utils.MAP_UNIT_SCALE/2
        #x, y = utils.screenScaleXY((self.x, self.y))
        x = self.x * utils.MAP_UNIT_SCALE
        y = self.y * utils.MAP_UNIT_SCALE
        x += centerOffset * self.size[0]
        y += centerOffset * self.size[1]
        return (x, y)

    def _createRect(self, size, parent):
        scale = utils.MAP_UNIT_SCALE * utils.WINDOW_SCALE
        newRect = pygame.Rect(self.x * scale + utils.OFFSET_X, self.y * scale + utils.OFFSET_Y, 
            scale * size, scale * size)
        self.rect = MyRect(parent, newRect)

class Undestroyable(Tile):
    def __init__(self, coords, image) -> None:
        super().__init__(coords, image, self)
    

class Destroyable(Tile):
    def __init__(self, coords, image) -> None:
        super().__init__(coords, image, self)

    def kill(self):
        gameLayer.remove(self)
        impassableLayer.remove(self)
        drawable.remove(self)

class Water(Tile):
    def __init__(self, coords, image) -> None:
        super().__init__(coords, image, self)
    
class MotherBase(Tile):
    def __init__(self, coords, image) -> None:
        super().__init__(coords, image, self, 3)
        
    def kill(self):
        gameLayer.remove(self)
        drawable.remove(self)
        # print('you\'ve lost')
        sys.exit()

class Tank(Transform):
    def __init__(self, image, x = 100, y = 100):
        super().__init__(x, y)
        self.fireProj = ProjEmitter(Projectile(), './bullet.png', self)
        self.image = pygame.transform.rotate(pygame.image.load(image), -90)
        self.rect = MyRect(self, self.image.get_rect())
        self.size = (2, 2)
        self.resize(None)

        self.direction = [0.0, -1.0]
        self.velocity = [0.0, 0.0]
        self.speed = 4
        self.firerate = 0.75
        self.timeUntilShot = 0.0

    def __eq__(self, other):
        return id(self) == id(other)

    def kill(self):
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
        return (self.x, self.y)
        #return (self.x, self.y)

    def resize(self, size):
        if type(size) is tuple:
            self.image = pygame.transform.smoothscale(self.image, size)
        elif type(size) is float:
            self.image = pygame.transform.smoothscale(self.image, 
                (math.floor(self.rect.w * size), math.floor(self.rect.h * size)))
        elif size is None:
            scale = utils.WINDOW_SCALE * utils.MAP_UNIT_SCALE
            self.image = pygame.transform.smoothscale(self.image, (math.floor(scale * self.size[0]), math.floor(scale * self.size[1])))
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
        obj = collider.parent
        # print(type(obj))
        x1, y1 = obj.getCentralPos()
        x2, y2 = self.getCenterPos()
        # print(x, y)
        w1, h1 = self.getSize()
        w2, h2 = obj.getSize()
        
        print(x1, x2)
        diffx = x1-x2 - self.velocity[0] * 1/utils.FPS
        diffy = y1-y2 - self.velocity[1] * 1/utils.FPS
        
        signx = diffx/abs(diffx)
        signy = diffy/abs(diffy)

        if abs(diffx) < w1/2 + w2/2:
            if diffx < 0 and self.velocity[0] < 0 \
                or diffx > 0 and self.velocity[0] > 0:
                print('stopping horizontal movement')
                self.velocity[0] = 0
            
        if abs(diffy) < h1/2 + h2/2:
            if diffy < 0 and self.velocity[1] < 0 \
                or diffy > 0 and self.velocity[1] > 0:
                print('stopping vertical movement')
                self.velocity[1] = 0
                
        self.x += 0.0008 * -signx * abs((w1+w2) * diffx)
        self.y += 0.0008 * -signy * abs((h1+h2) * diffy)


        

    def update(self):
        indx = self.rect.collidelist(impassableLayer)
        vel = self.velocity
        if vel[0] != 0 or vel[1] != 0: 
            self.rotate()

        if indx is not -1:
            self.onCollide(impassableLayer[indx])
        
        scale = utils.WINDOW_SCALE
        self.x += vel[0] / utils.FPS 
        self.y += vel[1] / utils.FPS
        
        self.rect.center = [math.floor(self.x * scale) + utils.OFFSET_X, math.floor(self.y * scale) + utils.OFFSET_Y]
    

class ProjEmitter:
    def __init__(self, proj, imagePath, parent):
        self.proj = proj
        self.image = pygame.image.load(imagePath)
        self.parent = parent

    def emit(self, direction):
        proj = copy.deepcopy(self.proj)
        proj.enabled = True
        proj.parent = self.parent
        proj.setImage(self.image.copy())
        proj.direction = direction
        # x, y = self.parent.getCenterPos()
        # rot = self.parent.getRot()
        x, y, rot = self.parent.getPosRot()

        proj.resize(None)
        proj.setPosRot(x * utils.WINDOW_SCALE, y * utils.WINDOW_SCALE, rot - 90)

        
        gameLayer.append(proj)
        updateable.append(proj)
        drawable.append(proj)

class Projectile(Transform):
    def __init__(self):
        super().__init__(0, 0)
        self.lifetime = 0.6
        self.damage = 1
        self.penetration = 1
        self.speed = 570
        self.size = (1, 1.5)
        self.direction = [0.0, -1.0]
        self.enabled = False

    def __eq__(self, other):
        return id(self) == id(other)

    def onCollide(self, collider):
        obj = collider.parent
        if obj == self.parent:
            return
        objType = type(obj)
        if objType is Undestroyable:
            pass
        elif objType is Destroyable:
            obj.kill()
        elif objType is Tank:
            obj.kill()
        elif objType is MotherBase:
            obj.kill()
        self.kill()

    def kill(self):
        drawable.remove(self)
        updateable.remove(self)
        gameLayer.remove(self)

    def setImageFile(self, imagePath):
        self.image = pygame.image.load(imagePath)
        self.rect = MyRect(self, self.image.get_rect())

    def setImage(self, image):
        self.image = image
        self.rect = MyRect(self, self.image.get_rect())

    def setPosRot(self, x, y, rot):
        self.x, self.y = x, y
        self.image = pygame.transform.rotate(self.image, rot)
        self.rect = MyRect(self, self.image.get_rect())

    def resize(self, size):
        if type(size) is tuple:
            self.image = pygame.transform.smoothscale(self.image, size)
        elif type(size) is float:
            self.image = pygame.transform.smoothscale(self.image, 
                (math.floor(self.rect.w * size), math.floor(self.rect.h * size)))
        elif size is None:
            size = utils.WINDOW_SCALE * utils.MAP_UNIT_SCALE
            self.image = pygame.transform.smoothscale(self.image, (math.floor(size * self.size[0]), math.floor(size * self.size[1])))
        

        self.rect = MyRect(self, self.image.get_rect())

    def update(self):
        if self.enabled:
            indx = self.rect.collidelist(gameLayer)
            if indx != -1:
                self.onCollide(gameLayer[indx])

            self.x += self.direction[0] * self.speed / utils.FPS
            self.y += self.direction[1] * self.speed / utils.FPS
            self.rect.center = [math.floor(self.x) + utils.OFFSET_X, math.floor(self.y) + utils.OFFSET_Y]

            self.lifetime -= 1.0/utils.FPS
            if self.lifetime <= 0:
                self.kill()
            
class SpawnPoint:
    def __init__(self, enemy, coords) -> None:
        self.enemy = enemy
        self.x, self.y = coords
    
class Map:
    def __init__(self, mapfile = 'simple.lay'):
        
        # TODO 
        # карта состоит из кубиков, 1 кубик 1/4 танка. 
        # Сам кубик, если может получать урон, то делиться еще на 4 мини-кубика
        # Выстрел каждый фрэйм проверяет касаеться ли он чего либо, при попадании удаляет ряд из 4х мини-кубиков

        self.playerSpawnPoints = []
        self.enemySpawnPoints = []

        self._rawMap = open('./maps/' + mapfile, 'r').read()
        self.mapMatrix = []

    def _getBoardSize(self):
        rows = self._rawMap.split('\n')
        y = len(rows)
        x = len(rows[0])

        return (x * utils.MAP_UNIT_SCALE, y * utils.MAP_UNIT_SCALE)

    def init(self):
        drawableList = []
        rows = self._rawMap.split('\n')

        for j, row in enumerate(rows):
            self.mapMatrix.append([])
            for i, c in enumerate(row):
                if c == 'X':
                    tile = Undestroyable((i, j), utils.WHITE)
                    gameLayer.append(tile.rect)
                    impassableLayer.append(tile.rect)
                    drawableList.append(tile)

                    self.mapMatrix[j].append(tile)
                elif c == 'D':
                    tile = Destroyable((i, j), utils.ORANGE)
                    gameLayer.append(tile.rect)
                    impassableLayer.append(tile.rect)
                    drawableList.append(tile)

                    self.mapMatrix[j].append(tile)
                elif c == 'W':
                    tile = Water((i, j), utils.BLUE)
                    impassableLayer.append(tile.rect)
                    drawableList.append(tile)

                    self.mapMatrix[j].append(tile)
                elif c == 'E':
                    tile = SpawnPoint(True,(i, j))
                    self.enemySpawnPoints.append(tile)
                    self.mapMatrix[j].append(tile)
                elif c == 'P':
                    tile = SpawnPoint(False,(i, j))
                    self.playerSpawnPoints.append(tile)
                    self.mapMatrix[j].append(tile)
                elif c == 'M':
                    tile = MotherBase((i - 1, j - 1), utils.GREY)
                    gameLayer.append(tile.rect)
                    drawableList.append(tile)

                    self.mapMatrix[j].append(tile)
        #print(tempList)
        global drawable 
        drawable += drawableList
                

