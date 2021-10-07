import random
import array
import numpy
import json

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

#Abre el archivo con la matriz de distancias:
# git clone https://github.com/juan-carvajal/TSP_Data.git

with open("TSP_Data/gr17.json", "r") as tsp_data:
    tsp = json.load(tsp_data)

distance_map = tsp["DistanceMatrix"]

IND_SIZE = tsp["TourSize"]

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", array.array, typecode='i', fitness=creator.FitnessMin)

toolbox = base.Toolbox()

toolbox.register("indices", random.sample, range(IND_SIZE), IND_SIZE)

toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalTSP(individual):
    distance = distance_map[individual[-1]][individual[0]]
    for gene1, gene2 in zip(individual[0:-1], individual[1:]):
        distance += distance_map[gene1][gene2]
    return distance,

#Tipo de crossover:
toolbox.register("mate", tools.cxPartialyMatched)

#Tipo de mutación con la probabilidad
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)

#Tipo de selección
toolbox.register("select", tools.selTournament, tournsize=30)

#Evaluación del fitness
toolbox.register("evaluate", evalTSP)

def main():
    random.seed(169)

	#Tamaño de la población
    pop = toolbox.population(n=1000)

	#El mejor de la población
    hof = tools.HallOfFame(1)

    #Obtiene estadísticas
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

	#Algoritmo genético utilizado
    algorithms.eaSimple(pop, toolbox, 0.7, 0.2, 50, stats=stats,
                        halloffame=hof)

    return pop, stats, hof

if __name__ == "__main__":
    pop,stats,hof=main()
    print(hof)
    print(evalTSP(hof[0]))
