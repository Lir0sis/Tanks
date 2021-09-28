import pygame
import math
import map
import queue

WHITE = (255, 255, 255)
ORANGE = (255, 150, 100)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
CYAN = (0, 170, 221)
GREY = (100, 100, 100)
BLACK = (0, 0, 0)


OFFSET_Y = 0
OFFSET_X = 0
MAP_UNIT_SCALE = 10
WINDOW_SCALE = 1
MATRIX_CENTER_BORDER = 0.45

MAZE_X = 30 + 1
MAZE_Y = 30 + 1

FPS = 120

time = 0.0

def createSimpleSprite(color, tileScale):
    width = MAP_UNIT_SCALE * WINDOW_SCALE * tileScale
    height = MAP_UNIT_SCALE * WINDOW_SCALE * tileScale
    surf = pygame.Surface((width, height))
    surf.fill(color)
    return surf

def copyImage(tileScale, image):
    width = MAP_UNIT_SCALE * WINDOW_SCALE * tileScale
    height = MAP_UNIT_SCALE * WINDOW_SCALE * tileScale
    img = image.copy()
    img = pygame.transform.scale(img, (math.floor(width), math.floor(height)))
    return img

def screenScaleXY(xy):
    x, y = xy
    return (x * MAP_UNIT_SCALE * WINDOW_SCALE + OFFSET_X,
     y * MAP_UNIT_SCALE * WINDOW_SCALE + OFFSET_Y)


def getMatrixCoord(coord):
    m_coord = round(coord / MAP_UNIT_SCALE)
    if m_coord + MATRIX_CENTER_BORDER < coord / MAP_UNIT_SCALE or \
    m_coord + 1 - MATRIX_CENTER_BORDER > coord / MAP_UNIT_SCALE:
        return m_coord

def getLegalNeighbours(pos, mapMatrix):
    x, y = pos
    neighbors = []
    for dx, dy in [[0, -1], [0, 1], [-1, 0], [1, 0]]:
        cell = mapMatrix[y + dy][x + dx]
        if cell == []:
            neighbors.append((dx + x, dy + y))
        else:
            for obj in cell:
                if not isinstance(obj, map.Impassable):
                    neighbors.append((dx + x, dy + y))
                
    return neighbors

def getCostlyNeighbors(item, mapMatrix):
    cost, pos = item
    x, y = pos
    neighbors = []
    for dx, dy in [[0, -1], [0, 1], [-1, 0], [1, 0]]:
        cell_x, cell_y = x + dx, y + dy
        if cell_x < 0 or cell_y < 0:
            continue
        cell = mapMatrix[cell_y][cell_x]
        if cell == []:
            neighbors.append((cost + 1, (cell_x, cell_y)))
        else:
            for obj in cell:
                if isinstance(obj, map.Destroyable):
                    neighbors.append((cost + 1/0.6, (cell_x, cell_y)))
                    break
                elif not isinstance(obj, map.Impassable):
                    neighbors.append((cost + 1, (cell_x, cell_y)))
                    break
    
    return neighbors

def getMazeNeighbours(cell, mapMatrix):
    height = len(mapMatrix)
    width = len(mapMatrix[0])

    def _hasAllWalls(neighbour):
        x, y = neighbour
        walls = 0
        for dx, dy in [[0, -1], [0, 1], [-1, 0], [1, 0]]:
            cell_y, cell_x = y + dy, x + dx
            cell = mapMatrix[cell_y][cell_x]
            if cell != [] and isinstance(cell[0], map.Impassable):
                walls +=1
        return True if walls == 4 else False
    
    x, y = cell
    neighbors = []
    for dx, dy in [[0, -1], [0, 1], [-1, 0], [1, 0]]:
        cell_y, cell_x = y + dy * 2, x + dx * 2

        if 1 <= cell_x < width -1 and 1 <= cell_y < height - 1:
            if _hasAllWalls((cell_x, cell_y)):
                neighbors.append(([dx, dy], (cell_x, cell_y)))
                
    return neighbors

def bfs(self, start_pos, end_pos):

        nodes = {start_pos: None}
        to_visit = [start_pos]
        while to_visit:
            pos = to_visit.pop(0)
            if pos == end_pos:
                break
            else:
                neighbors = self.getLegalNeighbours(pos)
                for neighbor in neighbors:
                    if neighbor not in nodes:
                        nodes[neighbor] = pos
                        to_visit.append(neighbor)
        path = []
        pos = end_pos
        while pos in nodes:
            path.append(pos)
            pos = nodes[pos]
        path.reverse()

        return path

def uniformCostSearch(start_pos, end_pos, matrix):
    nodes = {start_pos: None}
    to_visit = queue.PriorityQueue()
    to_visit.put((1, start_pos))
    while not to_visit.empty():
        item = to_visit.get()
        _ , pos = item
        if pos == end_pos:
            break
        else:
            for cost, next_pos in getCostlyNeighbors(item, matrix):
                if next_pos not in nodes:
                    nodes[next_pos] = pos
                    to_visit.put((cost, next_pos))
    path = []
    pos = end_pos
    while pos in nodes:
        path.append(pos)
        pos = nodes[pos]
    path.reverse()
    return path

def dfs(start_pos, end_pos, matrix):
    nodes = {start_pos: None}
    to_visit = [start_pos]
    while to_visit:
        pos = to_visit.pop(-1)
        if pos == end_pos:
            break
        else:
            neighbors = getLegalNeighbours(pos, matrix)
            for neighbor in neighbors:
                if neighbor not in nodes:
                    nodes[neighbor] = pos
                    to_visit.append(neighbor)
    path = []
    pos = end_pos
    while pos in nodes:
        path.append(pos)
        pos = nodes[pos]
    path.reverse()
    return path

def starA(start_pos, end_pos, matrix):
    x2, y2 = end_pos

    nodes = {start_pos: None}
    closedList = set()
    openedList = {start_pos : [1, 0]}
    to_visit = queue.PriorityQueue()
    to_visit.put((0, start_pos))

    while not to_visit.empty():
        _, pos = to_visit.get()
        cost = openedList[pos][0]
        closedList.add(pos)
        del openedList[pos]
        if pos == end_pos:
            break
        else:
            for new_cost, next_pos in getCostlyNeighbors((cost, pos), matrix):
                x, y = next_pos
                f = new_cost + abs(x2-x)**2 + abs(y2-y)**2

                if next_pos in closedList:
                    continue

                nodes[next_pos] = pos

                if next_pos in openedList and openedList[next_pos][0] <= new_cost:
                    continue

                openedList[next_pos] = [new_cost, f]
                to_visit.put((f, next_pos))
    
    path = []
    pos = end_pos
    #print(nodes)
    while pos in nodes:
        path.append(pos)
        pos = nodes[pos]
    path.reverse()
    return path

def isReplacable(cell, mapMatrix):
    x, y = cell
    empty = 0
    taken = 0
    for dx, dy in [[0, -1], [0, 1], [-1, 0], [1, 0]]:
        cell_x, cell_y = x + dx, y + dy
        if cell_x < 0 or cell_y < 0:
            continue
        cell = mapMatrix[cell_y][cell_x]
        if cell == []:
            empty += dx + dy
        else:
            taken += dx + dy
        
        return True if abs(empty) < 2 and abs(taken) < 2 else False

def getWallToBrake(direction, cell):
    x, y = cell
    dx, dy = direction
    return (x +dx, y +dy)

def make_maze():
    n = (MAZE_X - 1) * (MAZE_Y - 1) / 4
    mapMatrix = [[[map.Undestroyable((i, j), ORANGE)] 
        if i % 2 == 0 or j % 2 == 0 else [] for i in range(MAZE_X)] for j in range(MAZE_Y)]
    cell = [1, 1]
    mapMatrix[cell[1]][cell[0]] = []
    to_visit = []
    
    # Total number of visited cells during maze construction
    visited = 1
    while visited < n:
        neighbours = getMazeNeighbours(cell, mapMatrix)
        if not neighbours:
            cell = to_visit.pop()
            continue

        import random
        # Choose a random neighbouring cell and move to it.
        direction, next_cell = random.choice(neighbours)
        x, y = getWallToBrake(direction, cell)
        mapMatrix[y][x] = []
        to_visit.append(cell)
        cell = next_cell
        visited += 1

    for j, row in enumerate(mapMatrix):
        for i, column in enumerate(row):
            r = random.random() * 100
            
            if r > 40 and r < 55 and mapMatrix[j][i] != [] and \
                isReplacable((i, j), mapMatrix):

                mapMatrix[j][i] = [map.Destroyable((i, j), ORANGE)]

    return mapMatrix

            
