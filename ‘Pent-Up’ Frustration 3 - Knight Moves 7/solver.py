import pygame
import sys

GRIDWIDTH = 8
GRIDHEIGHT = 8
WINDOWWIDTH = 800
WINDOWHEIGHT = 800
FrameRate = 15

pygame.init()
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

def is_knight_move_3d(p1, p2):
    diffs = sorted(abs(a - b) for a, b in zip(p1, p2))
    return diffs == [0, 1, 2]

def createEmptyGrid(width, height):
    grid = [[[None, None, None] for x in range(width)] for x in range(height)] #3rd none is the region id of the segment, False is referring to if it's highlighted or not
    return grid

def setSquare(grid, x, y, z, val):
    if x<len(grid) and y<len(grid[0]):
        grid[x][y][z] = val

def setRegion(grid, x, y, regionId):
    grid[x][y][2] = regionId

def getdefinedsquares(grid, document):
    with open(file=f"./{document}.txt") as f:
        rawtext = f.read()
        f.close()
    data = [x.split(" ") for x in rawtext.split('\n')] #split along newlines, then split every element along spaces
    for i in data:
        if len(i) == 3:
            setSquare(grid, int(i[0]), int(i[1]), 0, int(i[2]))
        elif len(i) == 2:
            setSquare(grid, int(i[0]), int(i[1]), 0, None)
        else:
            pass
    return [x.pop(2) for x in data] #return the data in the form of [[x, y],...]


def PGRenderGrid(grid, windowheight, windowwidth):
    gap = 1  # gap to be subtracted from height and width when drawing
    blockwidth = windowwidth / len(grid[0])   # width of one block
    blockheight = windowheight / len(grid)    # height of one block
    color = (255, 255, 255)
    # Draw the grid
    for i in range(len(grid)):        # i = row index
        for j in range(len(grid[i])): # j = column index
                if [i,j] in highlightedsquares:
                    color = (255,0,0)
                pygame.draw.rect(
                    screen,
                    getColor(grid,i,j),
                    (i * blockwidth, j * blockheight, blockwidth - gap, blockheight - gap)
                )
                color = (255, 255, 255)
                if grid[i][j][0] != None:
                    text_surface = font.render(str(grid[i][j][0]), True, (0,0,0))  # (text, antialias, color)
                    screen.blit(text_surface, ((i+0.5) * blockwidth, (j+0.5) * blockheight))

def HandleClick(grid, windowheight, windowwidth, x, y):
    #Identify which tile was clicked.
    blockwidth = windowwidth / len(grid) #height and width of one block are defined
    blockheight = windowheight / len(grid[0])
    clickedblockX = int(x // blockwidth)
    clickedblockY = int(y // blockheight)
    print(clickedblockX, " ", clickedblockY, " ", grid[clickedblockX][clickedblockY][2])
    #Toggle this tile
    if highlightmode: 
        if [clickedblockX, clickedblockY] not in highlightedsquares:
            highlightedsquares.append([clickedblockX,clickedblockY])
        else:
            highlightedsquares.pop(highlightedsquares.index([clickedblockX, clickedblockY]))
    return grid

def getregions(grid, document):
    regions = []
    with open(file=f"./{document}.txt") as f:
        rawtext = f.read()
        f.close()
    data = [x.split(" ") for x in rawtext.split('\n')] #split along newlines, then split every element along spaces
    data = [x for x in data if x != ['']]
    for i in data:
        regions.append([(i[q:q+2]) for q in range(0, len(i), 2)])
    for i in regions:
        for j in i:
            setRegion(grid, int(j[0]),int(j[1]),regions.index(i))
    return regions #return the data in the form of [[x, y],...]
       
def getColor(grid, x, y):
    if (grid[x][y][2] != None) and ([x,y] not in highlightedsquares):
        amt = grid[x][y][2] + 1
        H = 255 // 13
        color = ((255-H*amt**1.5)%255,(255-H*amt**2)%255,(255+H**amt^4)%255)
        return color
    if [x,y] in highlightedsquares:
        return (255,0,0)
    else:
        return (255,255,255)

movevectors = [
    [-2,-1,0], [-2,0,-1], [-2,0,1], [-2,1,0],
    [-1,-2,0], [-1,2,0],
    [0,-2,-1], [0,-2,1], [0,2,-1], [0,2,1],
    [1,-2,0], [1,2,0],
    [2,-1,0], [2,0,-1], [2,0,1], [2,1,0]
]
class Path(object):
    def init(self, grid):
        self.grid = grid
        self.towers = [] #2d coords
        self.positions = [[7,0,0]]
        self.scores = [0]
        self.currentpos = [] #3d coords
        self.currentscore = 0
        self.length = 0
        self.moveindex=0

    def ismovevalid(self,dest): #check if a move is possible. If not, end the path. Possibly delete the path as well. Coordinates need to be 3 dimensional
        if not is_knight_move_3d(self.currentpos,dest):
            return False
        if 0<dest[0]>len(self.grid) or 0<dest[1]>len(self.grid[0]) or 0>dest[2]>1:
            return False
        if dest[2]==1:
            towertemp = self.checkregionfortower(self.grid[dest[0]][dest[1]][2])
            if towertemp==[dest[0],dest[1]]:
                return True
            elif towertemp != None:
                return False
            if towertemp==None:
                return True
        if dest[2]<self.currentpos[2]:
            if (self.currentscore/self.moveindex+1)%1==0:
                return True
            else:
                return False
        return True
            
    def makeMove(self,dest):
        self.moveindex+=1
        self.positions.append(dest)
        if dest[2]==self.currentpos[2]:
            self.currentscore += self.moveindex
        elif dest[2]>self.currentpos[2]:
            self.score*=self.moveindex
            self.towers.append([dest[0],dest[1]])
        elif dest[2]<self.currentpos[2]:
            self.score/self.moveindex
        self.currentpos = dest


    def attemptMove(self,dest):
        if self.ismovevalid(dest):
            self.makeMove(dest)

    def checkregionfortower(self,regionId):
        for i in regions:
            if i in self.towers:
                return i
        else: return None
    
    def tryBranch(self): #try every theoretically possible move. If no possible moves remain, close path and check validity. 
        for i in movevectors:
            pass
    
    def checkBranchValidity(self): #check if there are 13 towers etc, ie if it's a possible candidate
        pass

    def discardPath(self): #pop path from path list, discard
        pass

    def render(self):
        pass

maingrid = createEmptyGrid(GRIDWIDTH, GRIDHEIGHT)
screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption("Knight Moves 7")
knownsquaresonpath = getdefinedsquares(maingrid, 'definedsquares')

highlightedsquares = []
highlightmode = False
active = True
while active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            active = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            maingrid = HandleClick(maingrid, WINDOWHEIGHT, WINDOWWIDTH, pos[0], pos[1])
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: #Set regions
                highlightmode = not highlightmode
                #print("Pause!")
            if event.key == pygame.K_w: #Write regions
                highlightmode = False
                with open("./regions.txt", "a") as f:
                    f.write(" ".join([str(" ".join(str(y) for y in x)) for x in highlightedsquares]))
                    f.write("\n")
                    f.close()
                highlightedsquares = []
    screen.fill((0, 0, 0))
    regions = getregions(maingrid,"regions")
    PGRenderGrid(maingrid, WINDOWHEIGHT, WINDOWWIDTH)
    pygame.display.flip()
    clock.tick(FrameRate)

pygame.quit()
sys.exit()