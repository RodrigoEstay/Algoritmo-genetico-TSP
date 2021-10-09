#Fuente: https://datalore.jetbrains.com/view/notebook/nkK5LtMrTtl73dOCnC5G9R

import os
import sys
import pickle
import array
import csv
import codecs
import random
from urllib.request import urlopen
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

URL_PREFIX = 'http://elib.zib.de/pub/mp-testdata/tsp/tsplib/tsp/'

def read_tsp_data(tsp_name):
    """
    This function reads the tsp problem sample into an array of coordinates.
    :param tsp_name: the tsp problem name.
    :return: a 2-dimensional array with the city coordinates.
    """
    try:
        locations = pickle.load(open(os.path.join('tsp-data', tsp_name + '-loc.pickle'), 'rb'))
        distances = pickle.load(open(os.path.join('tsp-data', tsp_name + '-dist.pickle'), 'rb'))
        return locations, distances
    except(OSError, IOError):
        pass

    locations = []
    # open url with tsp data
    tsp_url = URL_PREFIX + tsp_name + '.tsp'
    with urlopen(tsp_url) as f:
        # read the data as a csv file delimited with whitespaces (utf-8 character encoding)
        reader = csv.reader(codecs.iterdecode(f, 'utf-8'), delimiter=' ', skipinitialspace=True)
        # ignore all the lines upto the start of the city coordinates
        for row in reader:
            if row[0] in ('DISPLAY_DATA_SECTION', 'NODE_COORD_SECTION'):
                break
        for row in reader:
            # if we reach the end of the data exit
            if row[0] == 'EOF':
                break
            # delete the index, we need the coordinates only
            del row[0]
            locations.append(np.asarray(row, dtype=np.float32))

    # calculate distances using vector norm
    number_cities = len(locations)
    distances = [[0] * number_cities for _ in locations]
    for i in range(number_cities):
        for j in range(i + 1, number_cities):
            # vector norm
            distance = np.linalg.norm(locations[j] - locations[i])
            distances[i][j] = distances[j][i] = distance

    if not os.path.exists('tsp-data'):
        os.makedirs('tsp-data')
    pickle.dump(locations, open(os.path.join('tsp-data', tsp_name + '-loc.pickle'), 'wb'))
    pickle.dump(distances, open(os.path.join('tsp-data', tsp_name + '-dist.pickle'), 'wb'))
    return locations, distances


CITIES, DISTANCES = read_tsp_data('bayg29')
NUMBER_CITIES = len(CITIES)

NUM_GENERATIONS = 200
POPULATION_SIZE = 100
P_CROSSOVER = 0.9
P_MUTATION = 0.1


''' 
Individual es una solución.
Es un recorrido de las ciudades.
Inicialmente es aleatoria.
'''
'''
individual = list(range(NUMBER_CITIES))
individual = random.sample(individual, len(individual))
print(individual)
'''

'''
retorna la distancia total recorrida de un Individual.
'''
def tsp_distance(individual: list) -> float:
    """
    Returns the traveling distance for particular ordering of cities.
    :param individual: an ordered list of cities to visit.
    :return: the total travelled distance.
    """
    # get distance between first and last city
    distance = DISTANCES[individual[0]][individual[-1]]
    # add all other distances
    for i in range(NUMBER_CITIES - 1):
        distance += DISTANCES[individual[i]][individual[i + 1]]
    return distance

'''
Se crean las clases FitnessMin y Individual

'''
creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
creator.create('Individual', array.array, typecode='i', fitness=creator.FitnessMin)

toolbox = base.Toolbox()
# Create operator to shuffle the cities
toolbox.register('randomOrder', random.sample, range(NUMBER_CITIES), NUMBER_CITIES)
# Create initial random individual operator
toolbox.register('individualCreator', tools.initIterate, creator.Individual, toolbox.randomOrder)
# Create random population operator
toolbox.register('populationCreator', tools.initRepeat, list, toolbox.individualCreator)

def tspFitness(individual) -> tuple:
    return tsp_distance(individual),
#PARAMETROSSS----------------------------------------
toolbox.register('evaluate', tspFitness)
toolbox.register('select', tools.selTournament, tournsize=3)
toolbox.register('mate', tools.cxOrdered)
toolbox.register('mutate', tools.mutShuffleIndexes, indpb=1.0 / NUMBER_CITIES)

population = toolbox.populationCreator(n=POPULATION_SIZE)

HALL_OF_FAME_SIZE = 10
hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register('min', np.min)
stats.register('avg', np.mean)

logbook = tools.Logbook()
logbook.header = ['gen', 'nevals'] + stats.fields

invalid_individuals = [ind for ind in population if not ind.fitness.valid]
fitnesses = toolbox.map(toolbox.evaluate, invalid_individuals)
for ind, fit in zip(invalid_individuals, fitnesses):
    ind.fitness.values = fit

hof.update(population)
hof_size = len(hof.items)

record = stats.compile(population)
logbook.record(gen=0, nevals=len(invalid_individuals), **record)
print(logbook.stream)

for gen in range(1, NUM_GENERATIONS + 1):
    # Select the next generation individuals
    offspring = toolbox.select(population, len(population) - hof_size)

    # Vary the pool of individuals
    offspring = algorithms.varAnd(offspring, toolbox, P_CROSSOVER, P_MUTATION)

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # add the best back to population:
    offspring.extend(hof.items)

    # Update the hall of fame with the generated individuals
    hof.update(offspring)

    # Replace the current population by the offspring
    population[:] = offspring

    # Append the current generation statistics to the logbook
    record = stats.compile(population) if stats else {}
    logbook.record(gen=gen, nevals=len(invalid_ind), **record)
    print(logbook.stream)

best = hof.items[0]
print('Best Individual = ', best)
print('Best Fitness = ', best.fitness.values[0])
plt.figure(1)

# plot genetic flow statistics:
minFitnessValues, meanFitnessValues = logbook.select("min", "avg")
plt.figure(2)
sns.set_style("whitegrid")
plt.plot(minFitnessValues, color='red')
plt.plot(meanFitnessValues, color='green')
plt.xlabel('Generation')
plt.ylabel('Min / Average Fitness')
plt.title('Min and Average fitness over Generations')
# show both plots:
plt.show()

# now plot the best travelling path.
plt.scatter(*zip(*CITIES), marker='.', color='red')
locs = [CITIES[i] for i in best]
locs.append(locs[0])
plt.plot(*zip(*locs), linestyle='-', color='blue')






















