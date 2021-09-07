import pygame
import math

WHITE = (255, 255, 255)
ORANGE = (255, 150, 100)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREY = (100, 100, 100)
BLACK = (0, 0, 0)


OFFSET_Y = 0
OFFSET_X = 0
MAP_UNIT_SCALE = 10
WINDOW_SCALE = 1
FPS = 60

time = 0.0

def createSimpleSprite(color, tileScale):
    width = MAP_UNIT_SCALE * WINDOW_SCALE * tileScale
    height = MAP_UNIT_SCALE * WINDOW_SCALE * tileScale
    surf = pygame.Surface((width, height))
    surf.fill(color)
    return surf

def duplicateImage(tileScale, image):
    width = MAP_UNIT_SCALE * WINDOW_SCALE * tileScale
    height = MAP_UNIT_SCALE * WINDOW_SCALE * tileScale
    img = image.copy()
    img = pygame.transform.scale(img, (math.floor(width), math.floor(height)))
    return img

def screenScaleXY(xy):
    x, y = xy
    return (x * MAP_UNIT_SCALE * WINDOW_SCALE + OFFSET_X,
     y * MAP_UNIT_SCALE * WINDOW_SCALE + OFFSET_Y)