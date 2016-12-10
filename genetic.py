import random, ai
import numpy as np
#initializing vectors
NUM_PARAMS = 4

#Creates a p vector
# class Individual:
#   def __init__(self, height, cleared, holes, bump):
#     self.h = height
#     self.c = cleared
#     self.ho = holes
#     self.b = bump

def genWeights ():
  height = random.uniform(-5.,5.)
  complete = random.uniform(-5.,5.)
  holes = random.uniform(-5.,5.)
  bump = random.uniform(-5.,5.)
  return np.array([height,complete,holes,bump])

#creates a population of weights of size s
def makePopulation (s):
  population = np.empty([NUM_PARAMS,s])
  for i in range(0,s):
    population[i] = genWeights()
  return population

#Rohit creates board states with 500 or so tetronimo pieces
#with the generated weights
#and then we pass it in to the fitness function

#fitness function is equal to total # of lines cleared for a single
#individual
def fitness(boardList):
  num_cleared = 0
  for board in boardList:
    num_cleared = num_cleared + ai.calculateCompleteLines(board)
  return num_cleared

def crossover(ind1, ind2):
  ind1*fitness()


#parents are selected for reproduction. We select the two fittest individuals
#for 10% of the population until our new offsprings produced reaches 30%
#of the population size
def tournamentSelection(pop):
  popSize = len(pop) #number of weight vectors
  tenPercent = round(popsize*0.1,0)
  thirtyPercent = round(popsize*0.3,0)
  potentialParents = np.zeros(tenPercent)
  offspring = np.zeros(thirtyPercent)
  while (len(offspring)<thirtyPercent):
    randomTenPercent = random.sample(range(1,popSize), tenPercent) #a list of random numbers
    fitnessScores = {}
    for i in range(0, len(randomTenPercent)-1):
      #create board states using this weight vec
      #boardStates = createBoard(pop[i])
      f = fitness(boardStates)
      fitnessScores[pop[i]] = f

    sortedFitness = sorted(fitnessScores.values(), key=lambda x:x[1])
    w1 = sortedFitness[-1][0]
    w1score = sortedFitness[-1][1]
    w2 = sortedFitness[-2][0]
    w2score = sortedFitness[-2][1]
    offspring.append(crossover(w1, w1score w2, w2score))






if __name__ == '__main__':
    makePopulation(4)
