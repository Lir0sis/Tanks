import pygame
from pygame.constants import WINDOWHITTEST

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
    # x *= MAP_UNIT_SCALE * WINDOW_SCALE + OFFSET_X
    # y *= MAP_UNIT_SCALE * WINDOW_SCALE + OFFSET_Y
    width = MAP_UNIT_SCALE * WINDOW_SCALE * tileScale
    height = MAP_UNIT_SCALE * WINDOW_SCALE * tileScale
    surf = pygame.Surface((width, height))
    surf.fill(color)
    return surf

def screenScaleXY(xy):
    x, y = xy
    return (x * MAP_UNIT_SCALE * WINDOW_SCALE + OFFSET_X,
     y * MAP_UNIT_SCALE * WINDOW_SCALE + OFFSET_Y)