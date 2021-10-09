import os
import sys
import array
import csv
import codecs
import random
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import numpy as np
import time

class Genetic_algotithm():

	population_size = None
	p_crossover = None
	p_mutation = None
	cities = None
	distances = None
	toolbox = None
	hofSize = None
	hof = None
	execTime = None
	population = None

	bestTime = None
	bestInd = None

	def __init__(self, cities, distances, execTime, popSize, pCross, pMutation):

		self.cities = cities
		self.distances = distances
		self.execTime = execTime
		self.population_size = popSize
		self.p_crossover = pCross
		self.p_mutation = pMutation

		creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
		creator.create('Individual', array.array, typecode='i', fitness=creator.FitnessMin)

		self.toolbox = base.Toolbox()
		self.toolbox.register('randomOrder', random.sample, range(len(cities)), len(cities))
		self.toolbox.register('individualCreator', tools.initIterate, creator.Individual, self.toolbox.randomOrder)
		self.toolbox.register('populationCreator', tools.initRepeat, list, self.toolbox.individualCreator)

		self.toolbox.register('evaluate', self.tspFitness)
		self.toolbox.register('select', tools.selTournament, tournsize=3)
		self.toolbox.register('mate', tools.cxOrdered)
		self.toolbox.register('mutate', tools.mutShuffleIndexes, indpb=1.0 / len(cities))


	def initialize(self):
		self.population = self.toolbox.populationCreator(n=self.population_size)

		self.hofSize = self.population_size // 10
		self.hof = tools.HallOfFame(self.hofSize)

		invalid_individuals = [ind for ind in self.population if not ind.fitness.valid]
		fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_individuals)
		for ind, fit in zip(invalid_individuals, fitnesses):
			ind.fitness.values = fit

		self.hof.update(self.population)
		self.hof_size = len(self.hof.items)


	def start(self):

		timeStart = time.time()

		while int(time.time() - timeStart) < self.execTime:

			offspring = self.toolbox.select(self.population, len(self.population) - self.hofSize)

			offspring = algorithms.varAnd(offspring, self.toolbox, self.p_crossover, self.p_mutation)

			invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
			fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
			for ind, fit in zip(invalid_ind, fitnesses):
				ind.fitness.values = fit

			offspring.extend(self.hof.items)

			self.hof.update(offspring)

			self.population[:] = offspring

			best = self.hof.items[0]

			if self.bestInd is None or self.bestInd.fitness.values[0] > best.fitness.values[0]:
				self.bestInd = best
				self.bestTime = time.time() - timeStart

			print(round(time.time() - timeStart, 3), round(best.fitness.values[0], 4))

		print("MEJOR DE SIEMPRE")
		print(round(self.bestTime, 3), round(self.bestInd.fitness.values[0], 4))
		print(list(self.bestInd))

		



	def tsp_distance(self, individual):

		distance = self.distances[individual[0]][individual[-1]]

		for i in range(len(cities) - 1):
			distance += self.distances[individual[i]][individual[i + 1]]
		return distance

	def tspFitness(self, individual):
		return self.tsp_distance(individual),

	

	

		






def read_tsp(tsp_path):

	cities = []

	with open(tsp_path, "br") as file:

		reader = csv.reader(codecs.iterdecode(file, 'utf-8'), delimiter=' ', skipinitialspace=True)

		for row in reader:
			if row[0] in ('DISPLAY_DATA_SECTION', 'NODE_COORD_SECTION'):
				break
		for row in reader:
			if row[0] == 'EOF':
				break
			del row[0]
			cities.append(np.asarray(row, dtype=np.float32))

	cunt = len(cities)
	distances = [[0] * cunt for _ in cities]
	for i in range(cunt):
		for j in range(i + 1, cunt):
			# vector norm
			distance = np.linalg.norm(cities[j] - cities[i])
			distances[i][j] = distances[j][i] = distance

	return cities, distances


if __name__ == "__main__":

	numMinParams = 4

	popSize = 100
	pCross = 0.9
	pMutation = 0.1


	if len(sys.argv) < numMinParams:
		print("Uso: -i <path del archivo> -t <tiempo en segundos>")
		exit()

	for i in range(len(sys.argv[1:])):

		if sys.argv[i] == "-i":
			tsp_path = sys.argv[i+1]

			if not os.path.exists(tsp_path):
				print("Archivo invalido")
				exit()
			
		if sys.argv[i] == "-t":

			# TODO: verificar que es un numero.
			execTime = sys.argv[i+1]
			try:
				execTime = int(execTime)
			except:
				print("Tiempo invalido")
				exit()

		if sys.argv[i] == "-p":

			popSize = sys.argv[i+1]
			try:
				popSize = int(popSize)
			except:
				print("Numero poblacion no valida")
				exit()

		if sys.argv[i] == "-c":

			pCross = sys.argv[i+1]
			try:
				pCross = float(pCross)
			except:
				print("Probabilidad cruza no valida")
				exit()

		if sys.argv[i] == "-m":

			pMutation = sys.argv[i+1]
			try:
				pMutation = float(pMutation)
			except:
				print("Probabilidad mutation no valida")
				exit()


	cities, distances = read_tsp(tsp_path)

	a = Genetic_algotithm(cities, distances, execTime, popSize, pCross, pMutation)
	a.initialize()
	a.start()
