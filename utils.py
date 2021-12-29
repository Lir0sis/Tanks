import pygame
import game
import math
import map
import queue
import random
import time

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
CELL_CENTER_TRESH = 0.42

MAZE_X = 36 + 1
MAZE_Y = 30 + 1

FPS = 120

time = time.time()
deltaTime = 0.0

class Counter(dict):
    def __getitem__(self, idx):
        self.setdefault(idx, 0)
        return dict.__getitem__(self, idx)

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
    fm_coord = coord / MAP_UNIT_SCALE
    m_coord = math.floor(fm_coord)
    return m_coord

def getCenteredMatrixCoord(coord, treshold = CELL_CENTER_TRESH):
    fm_coord = coord / MAP_UNIT_SCALE
    m_coord = math.floor(fm_coord)
    if m_coord + treshold < fm_coord and \
        m_coord + 1 - treshold > fm_coord:
        return m_coord
    else:
        return None

def getLegalNeighbours(pos, mapMatrix, ignoreList):
    x, y = pos
    neighbors = []
    for dx, dy in [[0, -1], [0, 1], [-1, 0], [1, 0]]:
        cell = mapMatrix[y + dy][x + dx]
        if cell == []:
            neighbors.append((dx + x, dy + y))
        else:
            for obj in cell:
                if not isinstance(obj, map.Impassable) or obj in ignoreList:
                    neighbors.append((dx + x, dy + y))
                
    return neighbors

def getCostlyNeighbors(item, mapMatrix, ignoreList):
    cost, pos = item
    x, y = pos
    neighbors = []
    for dx, dy in [[0, -1], [0, 1], [-1, 0], [1, 0]]:
        cell_x, cell_y = x + dx, y + dy
        if cell_x < 0 or cell_x >= len(mapMatrix[0]) or cell_y < 0 or cell_y >= len(mapMatrix):
            continue
        cell = mapMatrix[cell_y][cell_x]
        if cell == []:
            neighbors.append((cost + 1, (cell_x, cell_y)))
        elif cell != []:
            if cell == None:
                neighbors.append((cost + 1, (cell_x, cell_y)))
            if isinstance(cell, map.Destroyable):
                neighbors.append((cost + cell.weight, (cell_x, cell_y)))
        else:
            for obj in cell:
                if obj in ignoreList:
                    neighbors.append((cost + 1, (cell_x, cell_y)))
                elif isinstance(obj, map.Destroyable):
                    neighbors.append((cost + obj.weight, (cell_x, cell_y)))
                    break
                elif not isinstance(obj, map.Impassable):
                    neighbors.append((cost + obj.weight, (cell_x, cell_y)))
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

def bfs(start_pos, end_pos, matrix, ignoreList = []):
        nodes = {start_pos: None}
        to_visit = [start_pos]
        while to_visit:
            pos = to_visit.pop(0)
            if pos == end_pos:
                break
            else:
                neighbors = getLegalNeighbours(pos, matrix, ignoreList)
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

def uniformCostSearch(start_pos, end_pos, matrix, ignoreList = []):
    nodes = {start_pos: None}
    to_visit = queue.PriorityQueue()
    to_visit.put((1, start_pos))
    while not to_visit.empty():
        item = to_visit.get()
        _ , pos = item
        if pos == end_pos:
            break
        else:
            for cost, next_pos in getCostlyNeighbors(item, matrix, ignoreList):
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

def dfs(start_pos, end_pos, matrix, ignoreList = []):
    nodes = {start_pos: None}
    to_visit = [start_pos]
    while to_visit:
        pos = to_visit.pop(-1)
        if pos == end_pos:
            break
        else:
            neighbors = getLegalNeighbours(pos, matrix, ignoreList)
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

def starA(start_pos, end_pos, matrix, ignoreList = []):
    start_pos = tuple(start_pos)
    end_pos = tuple(end_pos)

    if start_pos == end_pos:
        return []
    x2, y2 = end_pos

    nodes = {start_pos: None}
    closedList = set()
    openedList = [(start_pos,(1, 0))]

    while openedList:
        pos, val = openedList.pop(0)
        cost, _ = val 

        closedList.add(pos)
        if pos == end_pos:
            break
        else:
            for new_cost, next_pos in getCostlyNeighbors((cost, pos), matrix, ignoreList):
                x, y = next_pos
                f = new_cost + abs(x2-x) + abs(y2-y)
                
                found = next(((x, i) for i, x in enumerate(closedList) if x[0] == next_pos), 0)
                if found:
                    new_item, i = found
                    closedList.remove(next_pos)
                    openedList[i] = new_item
                    openedList.sort(key=lambda item: item[1][1])
                    continue

                if next_pos in closedList:
                    continue

                nodes[next_pos] = pos
                if next_pos in openedList and openedList[next_pos][0] <= new_cost:
                    continue

                openedList.append(((next_pos),(new_cost, f)))
                #if(len(openedList) > 1):
                openedList.sort(key= lambda item: item[1][1])
                
                
    path = []
    pos = end_pos
    while pos in nodes.keys():
        path.append(pos)
        pos = nodes[pos]
    path.reverse()
    return path

def greedy(start_pos, end_pos, matrix, ignoreList):
    if start_pos == end_pos:
        return []
    x1, y1 = start_pos
    x2, y2 = end_pos

    nodes = {start_pos: None}
    closedList = set()
    openedList = [(start_pos,abs(x2-x1)**2 + abs(y2-y1)**2)]

    while openedList:
        pos, _ = openedList.pop(0)
        closedList.add(pos)

        if pos == end_pos:
            break
        else:
            for _, next_pos in getCostlyNeighbors((0, pos), matrix, ignoreList):
                f = abs(x2-next_pos[0])**2 + abs(y2-next_pos[1])**2

                if next_pos in closedList:
                    continue

                nodes[next_pos] = pos   
                if next_pos in openedList:
                    continue

                openedList.append(((next_pos),f))
                openedList.sort(key=lambda item: item[1])
                
    path = []
    pos = end_pos
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
    #sign = empty/abs(empty) if empty != 0 else taken/abs(taken)
    return True if abs(empty) < 1 and abs(taken) < 1 else False

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
    
    visited = 1
    while visited < n:
        neighbours = getMazeNeighbours(cell, mapMatrix)
        if not neighbours:
            cell = to_visit.pop()
            continue

        direction, next_cell = random.choice(neighbours)
        x, y = getWallToBrake(direction, cell)
        mapMatrix[y][x] = []
        to_visit.append(cell)
        cell = next_cell
        visited += 1

    mapMatrix = fill_maze(mapMatrix)

    return mapMatrix

def fill_maze(mapMatrix):
    while True:
        x = round(random.random() * (MAZE_X - 2))
        y = round(random.random() * (MAZE_Y - 2))

        if mapMatrix[y][x] == []:
            tile = map.SpawnPoint(False, (x, y))
            mapMatrix[y][x].append(tile)
            map.playerSpawnPoints.append(tile)
            break

    for j, row in enumerate(mapMatrix):
        for i, column in enumerate(row):
            r = random.random() * 100
            if mapMatrix[j][i] == []:
                continue

            if r > 1 and r < 60 and isinstance(mapMatrix[j][i][0], map.Undestroyable) and \
                1 <= i < MAZE_X - 1 and 1 <= j < MAZE_Y - 1 and \
                isReplacable((i, j), mapMatrix):

                mapMatrix[j][i] = [map.Destroyable((i, j), ORANGE)]
    return mapMatrix

def getNpoints(mapMatrix, n):
    height = len(mapMatrix) - 2
    width = len(mapMatrix[0]) - 2
    points = []

    while len(points) < n:
        x = round(random.random() * width)
        y = round(random.random() * height)
        if mapMatrix[y][x] == []:
            tile = map.Point((x, y))
            mapMatrix[y][x].append(tile)
            points.append(tile)

            map.drawable.append(tile)
            map.gameLayer.append(tile.rect)

    return points


def miniMax(maxDepth, game):
            nextMove = None
            simple_board = game.map.getSimple()

            def maximize(alpha, beta, board, depth):
                if depth == 0:
                    return board.getScore() 
    
                actions = board.getActions(0) 
                best = -999.0
                score = None
                for shoot, move in actions:
                    new_board = board.clone()
                    result = None

                    if shoot:
                        new_board.applyAction(0, (True, shoot))
                    if move:
                        result = new_board.applyAction(0, (False, move))
                    if result:
                        score = result
                    else:
                        score = minimize(alpha, beta, 0, new_board, depth - 1)

                    best = max(score, best)
                    alpha = max(alpha, best)

                    if depth == maxDepth and alpha == score:
                        nextMove = (shoot, move)
 
                    if alpha >= beta:
                        return alpha    
                return best
            
            def minimize(alpha, beta, enemy, board, depth):
                if (depth == 0):
                    return board.getScore()

                actions = board.getActions(enemy)
                best = 999.0
                score = None
                for action in actions:
                    new_board = board.clone()
                    val1, val2 = None, None
                    if action[0]:
                        new_board.applyAction(enemy + 1, (True, action[0]))
                    if action[1]:
                        val1 = new_board.applyAction(enemy + 1, (False, action[1]))

                    if not val1 and (enemy + 1 < len(new_board.enemies)):
                        val2 = minimize(alpha, beta, enemy + 1, new_board, depth)
                        score = min(i for i in [val1, val2] if i is not None)
                    else:    
                        score = maximize(alpha, beta, new_board, depth - 1)
                    best = min(score, best)
                    beta = min(beta, best)
                    if alpha >= beta:
                        return beta
                return best

            maximize(-999.0, 999.0, simple_board, maxDepth)
            return nextMove
        