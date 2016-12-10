# Rohit Bakshi (rhb255) and Minae Kwon
# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, time, pygame, sys, copy, math
import numpy as np
from pygame.locals import *

FPS = 25
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'

MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.1

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)
PURPLE      = (75,    0, 130)
LIGHTPURPLE = (147, 112, 219)
ORANGE      = (255, 140,   0)
LIGHTORANGE = (255, 165,   0)
BROWN       = (139,  69,  19)
LIGHTBROWN  = (160,  82,  45)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS      = (     BLUE,      GREEN,      RED,      YELLOW, PURPLE, ORANGE, BROWN)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW, LIGHTPURPLE, LIGHTORANGE, LIGHTBROWN)
assert len(COLORS) == len(LIGHTCOLORS) # each color must have light color

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}

BLOCK_COLORS = {'S': 0,
                'Z': 1,
                'J': 2,
                'L': 3,
                'I': 4,
                'O': 5,
                'T': 6}


def fitness(weightVector):
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetromino')

    #fitness function
    score = 0
    for i in range(0,3):
        score = score + runGame(weightVector)
    print "OVERALL SCORE: " + str(score)
    return score


def printBoard(board):
    for i in range(BOARDHEIGHT):
        row = []
        for j in range (BOARDWIDTH):
            row.append(board[j][i])
        print('\t'.join(map(str,row)))
score = 0

def runGame(weightVector):
    # setup variables for the start of the game
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False # note: there is no movingUp variable
    movingLeft = False
    movingRight = False
    score = 0
    level, fallFreq = calculateLevelAndFallFreq(score)
    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()
    while True: # game loop
        if fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            fallingPiece = nextPiece
            nextPiece = getNewPiece()

            if not isValidPosition(board, fallingPiece):
                print "parital score: " + str(score)
                return score # can't fit a new piece on the board, so game over

        checkForQuit()
        boardList = generateBoardPositions(board, fallingPiece)

        bestMove = None
        bestValue = -float("inf")
        for x in boardList:
            #currentValue = evaluateBoard(x, -0.510066, 0.760666, -0.35663, -0.184483)
            currentValue = evaluateBoard(x, weightVector)
            if currentValue > bestValue:
                bestValue =  currentValue
                bestMove = x

        board = bestMove
        score = score + removeCompleteLines(board)
        level, fallFreq = calculateLevelAndFallFreq(score)
        fallingPiece = None

        # drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        drawStatus(score, level)
        drawNextPiece(nextPiece)
        if fallingPiece != None:
            drawPiece(fallingPiece)

        pygame.display.update()
        FPSCLOCK.tick(FPS)
    print score

def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()


def checkForKeyPress():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    checkForQuit()
    # for i in range(0,5):
    #     pass
    return K_UP


def showTextScreen(text):
    # This function displays large text in the
    # center of the screen until a key is pressed.
    # Draw the text drop shadow
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the text
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the additional "Press a key to play." text.
    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    while checkForKeyPress() == None:
        pygame.display.update()
        FPSCLOCK.tick()


def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def calculateLevelAndFallFreq(score):
    # Based on the score, return the level the player is on and
    # how many seconds pass until a falling piece falls one space.
    level = int(score / 10) + 1
    fallFreq = 0.27 - (level * 0.02)
    return level, fallFreq


def getNewPiece():
    # return a random new piece in a random rotation and color
    shape = random.choice(list(PIECES.keys()))
    newPiece = {'shape': shape,
                'rotation': random.randint(0, len(PIECES[shape]) - 1),
                'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                'y': -2, # start it above the board (i.e. less than 0)
                'color': BLOCK_COLORS[shape]}
    return newPiece


def addToBoard(board, piece):
    # fill in the board based on piece's location, shape, and rotation
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[x + piece['x']][y + piece['y']] = piece['color']
                if x + piece['x'] < 0 or y + piece['y'] < 0:
                    return False
    return True


def getBlankBoard():
    # create and return a new blank board data structure
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board


def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def isValidPosition(board, piece, adjX=0, adjY=0):
    # Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                return False
    return True

def isCompleteLine(board, y):
    # Return True if the line filled with boxes with no gaps.
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True


def removeCompleteLines(board):
    # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1 # start y at the bottom of the board
    while y >= 0:
        if isCompleteLine(board, y):
            # Remove the line and pull boxes down by one line.
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY-1]
            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            numLinesRemoved += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1 # move on to check next row up
    return numLinesRemoved


def convertToPixelCoords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def drawBox(boxx, boxy, color, pixelx=None, pixely=None):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if color == BLANK:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convertToPixelCoords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def drawBoard(board):
    # draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # fill the background of the board
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y])


def drawStatus(score, level):
    # draw the score text
    scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    # draw the level text
    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(levelSurf, levelRect)


def drawPiece(piece, pixelx=None, pixely=None):
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelx == None and pixely == None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != BLANK:
                drawBox(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


def drawNextPiece(piece):
    # draw the "next" text
    nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 120, 80)
    DISPLAYSURF.blit(nextSurf, nextRect)
    # draw the "next" piece
    drawPiece(piece, pixelx=WINDOWWIDTH-120, pixely=100)


#--------------------------------------AI Functions------------------------------------------------------------------
def evaluateBoard(board, weightVector):
    a = weightVector[0]
    b = weightVector[1]
    c = weightVector[2]
    d = weightVector[3]
    return a*calculateAggregateHeight(board) + b*calculateCompleteLines(board) + c*calculateHoles(board) + d*calculateBumpiness(board)

#https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
def calculateAggregateHeight(board):
    totalHeight = 0
    for x in range(BOARDWIDTH):
        column = board[x]   #starting from left
        temp = 0
        for y in range(len(column)):
            if(column[y] != '.'):
                temp = len(column) - y
                break
        totalHeight += temp
    return totalHeight

def calculateCompleteLines(board):
    totalCompleteLines = 0
    for y in range(BOARDHEIGHT):
        if(isCompleteLine(board,y)):
            totalCompleteLines += 1
    return totalCompleteLines

def calculateHoles(board):
    totalHoles = 0
    for x in range(BOARDWIDTH):
        column = board[x]   #starting from left
        temp = 0
        firstblock = False
        for y in range(len(column)):
            if(column[y] != '.'):
                firstblock = True
            if(firstblock and column[y] == '.'):
                temp+=1
        totalHoles += temp
    return totalHoles

def calculateBumpiness(board):
    heightList = []
    for x in range(BOARDWIDTH):
        column = board[x]   #starting from left
        temp = 0
        for y in range(len(column)):
            if(column[y] != '.'):
                temp = len(column) - y
                break
        heightList.append(temp)
    bumpiness = 0
    for z in range(len(heightList)-1):
        temp = abs(heightList[z] - heightList[z+1])
        bumpiness += temp
    return bumpiness

#https://luckytoilet.wordpress.com/2011/05/27/coding-a-tetris-ai-using-a-genetic-algorithm/
def calculateBlockades(board):
    totalBlockades = 0
    for x in range(BOARDWIDTH):
        column = board[x]
        temp = 0
        firstblock = False
        emptyblock = False
        for y in range(len(column)):
            if(column[y] != '.'):
                firstblock = True
            if(firstblock and column[y] == '.'):
                temp+=1
                emptyblock = True
            if(firstblock and emptyblock and column[y] == '.'):
                emptyblock = True
            if(firstblock and emptyblock and column[y] != '.'):
                temp+=1
                emptyblock = False
        totalBlockades += temp
    return totalBlockades

# true if the piece is within the board
def withinBoard(currentPiece, adjX=0, adjY=0):
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            notOnBoard = y + currentPiece['y'] + adjY < 0
            if notOnBoard or PIECES[currentPiece['shape']][currentPiece['rotation']][y][x] == BLANK:
                continue
            if not isOnBoard(x + currentPiece['x'] + adjX, y + currentPiece['y'] + adjY):
                return False
    return True

def positionPiece(board, currentPiece):
        i = 1
        while isValidPosition(board, currentPiece, adjY=i):
            i+=1
        currentPiece['y'] += i-1

#
def generateBoardPositions(board, currentPiece):

    boardList = []

    numberRotations = len(PIECES[currentPiece['shape']])
    currentRotatedPiece = copy.copy(currentPiece)

    for i in range(numberRotations):
        currentRotatedPiece['rotation'] = (currentRotatedPiece['rotation'] + 1) % len(PIECES[currentRotatedPiece['shape']])

        xshiftAmount = 0
        while True:
            if not withinBoard(currentRotatedPiece, adjX = xshiftAmount) and xshiftAmount > 0:
                break
            currentPieceShift = copy.deepcopy(currentRotatedPiece)
            currentPieceShift['x'] += xshiftAmount
            if isValidPosition(board, currentPieceShift):
                positionPiece(board, currentPieceShift)

                currBoard = copy.deepcopy(board)
                if addToBoard(currBoard, currentPieceShift):
                    boardList.append(currBoard)
            # left first
            if xshiftAmount <= 0:
                xshiftAmount -= 1
            else:
                xshiftAmount += 1

            if not withinBoard(currentRotatedPiece, adjX = xshiftAmount) and xshiftAmount <= 0:
                xshiftAmount = 1

    return boardList

def printBoard(board):
    for i in range(BOARDHEIGHT):
        row = []
        for j in range (BOARDWIDTH):
            row.append(board[j][i])

        print('\t'.join(map(str,row)))

###GENETIC###:
def genWeights ():
  height = random.uniform(-1.,1.)
  complete = random.uniform(-1.,1.)
  holes = random.uniform(-1.,1.)
  bump = random.uniform(-1.,1.)
  return np.array([height,complete,holes,bump])
  #print np.array([height,complete,holes,bump])

#creates a population of weights of size s
def makePopulation (s):
  population = np.empty([s,4])
  for i in range(0,s):
    population[i] = genWeights()
  return population

#parents are selected for reproduction. We select the two fittest individuals
#for 10% of the population until our new offsprings produced reaches 30%
#of the population size
def tournamentSelection(pop, fitnessLst):
    popSize = len(pop) #number of weight vectors
    print "popSIze:" + str(popSize)
    tenPercent = round(popSize*0.1,0)
    print "tenperc:" + str(tenPercent)

    thirtyPercent = round(popSize*0.3,0)
    # print "thirtyperc::" + str(thirtyPercent)

    potentialParents = np.zeros(tenPercent)
    # print "potential parents: "
    # print potentialParents
    offspring = []
    # print "offspring "
    # print offspring

    while (len(offspring)<thirtyPercent):
        randomTenPercent = random.sample(range(1,popSize), int(tenPercent)) #a list of random numbers
        print "rand ten percent: " + str(randomTenPercent)
        fitnessScores = []
        counter = 0
        for i in range(0, len(randomTenPercent)):
          #f = fitness(pop[i])
          #fitnessScores.append((pop[i], f))
          fitnessScores.append((fitnessLst[i][0],fitnessLst[i][1]))
          counter = counter + 1
          print "counter = " + str(counter)
        sortedFitness = sorted(fitnessScores, key=lambda x:x[1])
        print "Sorted fitness scores: "
        print sortedFitness
        w1 = sortedFitness[-1][0]
        w1score = sortedFitness[-1][1]
        w2 = sortedFitness[-2][0]
        w2score = sortedFitness[-2][1]
        new_offspring = crossover(w1, w1score, w2, w2score)
        mut_offspring = mutate(new_offspring) #need to double check if this works
        offspring.append(mut_offspring)
    print " final offspring : "
    print offspring
    return offspring

def normalize (v):
    mag = 0.0
    for i in range(0, len(v)):
        mag = mag + v[i]**2
    mag = math.sqrt(mag)
    for i in range(0, len(v)):
        if mag == 0:
            v[i] = 0.0
        else:
            v[i] = v[i]/mag
    return v

def crossover(w1, w1score, w2, w2score):
  offspring = w1 * w1score + w2 * w2score #a vector
  print "non normalized offspring: "
  print offspring
  norm_offspring = normalize(offspring)
  print "normalized: "
  print norm_offspring
  return norm_offspring

def mutate (offspring):
    rint = random.randint(1,100) #5% chance of mutating
    if rint <=5 : #mutate!
        rint2 = random.randint(0,3) #select random weight to mutate
        if 0 % 2 == 0: #randomly select if should add or subtract
            offspring[rint2] = offspring[rint2] + 0.2
        else:
            offspring[rint2] = offspring[rint2] - 0.2
        offspring = normalize(offspring) #normalize
    else: #don't mutate
        offspring
    return offspring

def new_generation(pop, fitnessLst, offspring):
    popSize = len(pop) #number of weight vectors
    thirtyPercent = round(popSize*0.3,0)
    sortedFitness = sorted(fitnessLst, key=lambda x:x[1])
    weakestThirtyP = sortedFitness[:int(thirtyPercent)]
    print weakestThirtyP
    for w in range(0,len(pop)): #delete the weakest thirty percent from pop
        for tup in weakestThirtyP:
            print tup
            print pop
            print pop[w]
            if (pop[:,w] == tup[0]).all():
                pop = np.delete(pop, w, 0)
    new_gen = np.concatenate((pop,offspring), axis = 0)
    print new_gen
    return new_gen


def main():
    fitnessLst = []
    pop = makePopulation(18)
    print "POP: "
    print pop
    for i in range(0,len(pop)):
        print "vector: "
        print pop[i]
        fscore = fitness(pop[i])
        fitnessLst.append((pop[i], fscore))
    print fitnessLst
    offspring = tournamentSelection(pop, fitnessLst)
    new_generation(pop, fitnessLst, offspring)






if __name__ == '__main__':
    wv = np.ones([4])
    wv[0] = -0.510066
    wv[1] =  0.760666
    wv[2] =  0
    wv[3] =  0
    #fitness(wv)
    #pop = makePopulation(20)
    #print "POP:"
    #print pop
    #tournamentSelection(pop)
    #w1 = np.array([ 0.39217715,  0.55730712,  0.25160626, -0.46359303])
    #w2 = np.array([ 0.10418231, -0.06398574, -0.18539031, -0.80764434])
    #crossover(w1, 0,w2, 14)
    main()