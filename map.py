import pygame
import copy
import math
import utils

BLOCK_RADIUS = 5
impassableLayer = []
destroyableLayer = []
updateable = []
drawable = []

class Transform:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.rot = 0
    
    def getPosRot(self):
        return (self.x, self.y, self.rot)

class MyRect(pygame.Rect):
    def __init__(self, parent, left, top, width, height):
        pygame.Rect.__init__((left, top), (width, height))
        self.parent = parent

class ProjEmitter:
    def __init__(self, proj, imagePath, parent):
        self.proj = proj
        self.image = pygame.image.load(imagePath)
        self.parent = parent

    def emit(self, direction):
        proj = copy.deepcopy(self.proj)
        proj.enabled = True
        proj.owner = self.parent
        proj.setImage(self.image.copy())
        proj.direction = direction
        x, y, rot = self.parent.getPosRot()
        proj.setPosRot(x, y, rot - 90)
        proj.resize(0.075)

        updateable.append(proj)
        drawable.append(proj)

class Projectile(Transform):
    def __init__(self):
        super().__init__(0, 0)
        self.lifetime = 0.6
        self.damage = 1
        self.penetration = 1
        self.speed = 570
        self.direction = [0.0, 0.0]
        self.enabled = False

    def __eq__(self, other):
        return id(self) == id(other)

    def setImageFile(self, imagePath):
        self.image = pygame.image.load(imagePath)
        self.rect = self.image.get_rect()

    def setImage(self, image):
        self.image = image
        self.rect = self.image.get_rect()

    def setPosRot(self, x, y, rot):
        self.x, self.y = x, y
        self.image = pygame.transform.rotate(self.image, rot)
        self.rect = self.image.get_rect()

    def resize(self, scale):
        if type(scale) is tuple:
            self.image = pygame.transform.smoothscale(self.image, scale)
        elif type(scale) is float:
            self.image = pygame.transform.smoothscale(self.image, 
                (math.floor(self.rect.w * scale), math.floor(self.rect.h * scale)))
        self.rect = self.image.get_rect()

    def update(self):
        if self.enabled:
            self.x += self.direction[0] * self.speed / utils.FPS
            self.y += self.direction[1] * self.speed / utils.FPS
            self.rect.center = [math.floor(self.x), math.floor(self.y)]

            self.lifetime -= 1.0/utils.FPS
            if self.lifetime <= 0:
                drawable.remove(self)
                updateable.remove(self)
            
class Tank(Transform):
    def __init__(self, image, x = 100, y = 100):
        super().__init__(x, y)
        self.fireProj = ProjEmitter(Projectile(), './bullet.png', self)
        self.image = pygame.transform.rotate(pygame.image.load(image), -90)
        self.rect = self.image.get_rect()

        self.direction = [0.0, -1.0]
        self.velocity = [0.0, 0.0]
        self.speed = 80
        self.firerate = 0.75
        self.timeUntilShot = 0.0

    def __eq__(self, other):
        return id(self) == id(other)

    def action(self):
        if self.timeUntilShot < utils.time:
            self.timeUntilShot = utils.time + self.firerate
            self.fireProj.emit(self.direction)

    def setDirection(self, vec, keypressed):
        self.direction = vec
        if keypressed:
            self.velocity = [vec[0] * self.speed, vec[1] * self.speed]
        else:
            self.velocity = [0, 0]


    def resize(self, scale):
        if type(scale) is tuple:
            self.image = pygame.transform.smoothscale(self.image, scale)
        elif type(scale) is float:
            self.image = pygame.transform.smoothscale(self.image, 
                (math.floor(self.rect.w * scale), math.floor(self.rect.h * scale)))
        self.rect = self.image.get_rect()

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
        self.rect = self.image.get_rect()

    def update(self):
        vel = self.velocity
        if vel[0] != 0 or vel[1] != 0: 
            self.rotate()
        self.x += vel[0]/utils.FPS
        self.y += vel[1]/utils.FPS
        self.rect.center = [self.x, self.y]
    

class Map:
    def __init__(self, mapfile = 'simple.lay'):
        
        # TODO 
        # карта состоит из кубиков, 1 кубик 1/4 танка. 
        # Сам кубик, если может получать урон, то делиться еще на 4 мини-кубика
        # Выстрел каждый фрэйм проверяет касаеться ли он чего либо, при попадании удаляет ряд из 4х мини-кубиков
       
        self._rawMap = open('./maps/'+ mapfile, 'r').read()
        _initMap()

    def _initMap(self):
        pass
        # D - блок разрушаемый
        # X - блок
        # O - пустое пространство
        # P - место появления игрока
        # E - место появления врага
        # B - куст
        # W - вода
        # M - 3х3 база игрока (центр 1 блок)

