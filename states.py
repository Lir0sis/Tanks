from .map import *

class States:
    class SimpleTank:
        def __init__(self, pos, speed, fireRate, parent) -> None:
            self.pos = pos
            self.speed = speed
            self.parent = parent
            self.untilShot = 0
            self.fireRate = fireRate
            self.nextAction = (None, None)

        def move(self, dir):
            self.pos = [self.pos[0] + dir[0], self.pos[1] + dir[1]]
            self.untilShot -= 1/self.speed

        def action(self, direc):
            if 0 >= self.untilShot:
                self.parent.projectiles.append(Map.SimpleProj(direc, self.speed * 4))
                self.untilShot = self.fireRate

        def applyAction(self):
            if (self.nextAction[1]):
                self.move(self.nextAction[1])
            if (self.nextAction[0]):
                self.action(self.nextAction[0])

    class SimpleProj:
        def __init__(self, pos, dir, speed, oponents) -> None:
            self.pos = pos
            self.dir = dir
            self.speed = speed
            self.moves = 2
            self.oponents = oponents

        def move(self, mapMatrix):
            self.moves -= 1
            if self.moves == 0:
                return None
            new_pos = [self.pos[0] + self.dir[0] * self.speed, self.pos[1] + self.dir[1] * self.speed]
            for i in range(self.pos[0],new_pos[0]+1):
                for j in range(self.pos[1], new_pos[1] + 1):
                    if isinstance(mapMatrix[j][i], Destroyable):
                        self.moves = 0
                        mapMatrix[j][i] = None
                        return
                    tobeRemoved = None
                    for o in self.oponents:
                        if (i == o.pos[0] and j == o.pos[1]):
                            tobeRemoved = (o)
                            break
                    if tobeRemoved:
                        self.oponents.remove(tobeRemoved)

    class SimpleMap:
        def __init__(self, matrix, players, enemies) -> None:
            self.mapMatrix = self._getTilesMatrix(matrix)
            self.players = self._parseTanks([p.child for p in players])
            self.enemies = self._parseTanks([p.child for p in enemies])
            self.projectiles = []
        
        def __hash__(self) -> int:
            h = 0

            for player in self.players:
                h += hash(player)

            for enemy in self.enemies:
                h += hash(enemy)

            for wall in self.mapMatrix:
                h += hash(wall)

            return h


        def _parseTanks(self, tanks):
            parsed_tanks = []

            for tank in tanks:
                    parsed_tanks.append(Map.SimpleTank((tank.m_x, tank.m_y), tank.speed / utils.MAP_UNIT_SCALE, tank.firerate, self))

            return parsed_tanks

        def _getTilesMatrix(self, matrix):   
            mapMatrix = []
            for i, row in enumerate(matrix):
                mapMatrix.append([])
                for j, el in enumerate(row):
                    tile = matrix[i][j]
                    if isinstance(tile, Tile):
                        mapMatrix[i].append(tile)
                    else:
                        mapMatrix[i].append(None)
            
            return mapMatrix

        class Turn(enum.Enum):
            WON = 0
            LOST = 1
            NONE = 2
            WRONG = 3 
        
        def clone(self):
            return copy.deepcopy(self)

        def getScore(self):
            pathA = utils.starA(self.players[0].pos, self.enemies[0].pos,self.mapMatrix)
            pathB = utils.starA(self.players[0].pos, self.enemies[1].pos,self.mapMatrix)
            score = min(len(pathA), len(pathB))
            return 1/ score

        def applyActions(self): # REDO seperate action queue per player | turn activation
            tank = self.players + self.enemies
            for t in tank:
                t.applyAction()

            prevE = len(self.enemies)
            prevP = len(self.players)
            for proj in self.projectiles:
                proj.move()
            if prevE > len(self.enemies):
                return self.getScore() * 2
            elif prevP > len(self.players):
                return self.getScore() * 1/2
            return None

        def queueAction(self, player, action):
            tank = (self.players + self.enemies)[player]
            tank.nextAction = action

        def getActions(self, player):
            tank = (self.players + self.enemies)[player]
            pos = tank.pos

            directions = [[0, -1],[-1, 0], [0, 1], [1, 0]]
            shoot_dirs = []
            actions = []
            
            if tank.untilShot <= 0:
                for direction in directions:
                    shootcell = self.mapMatrix[pos[1]+ direction[1]][pos[0]+ direction[0]]
                    if not isinstance(shootcell, Destroyable) and isinstance(shootcell, Impassable):
                        pass
                    else:
                        shoot_dirs.append(direction)

            for direction2 in directions:
                moveDir = direction2
                movecell = self.mapMatrix[pos[1]+ direction2[1]][pos[0]+ direction2[0]]
                if isinstance(movecell, Impassable):
                    continue
                else:
                    actions.append((None, moveDir))

                for direction1 in shoot_dirs:
                    # shootcell = self.mapMatrix[pos[1]+ direction[1], pos[0]+ direction[0]]
                    actions.append((direction1, moveDir))

            actions += [(s, None) for s in shoot_dirs]
            return actions
