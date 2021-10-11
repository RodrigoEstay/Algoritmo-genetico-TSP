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

	hof = None
	cities = None
	toolbox = None
	bestInd = None
	hofSize = None
	execTime = None
	bestTime = None
	distances = None
	pMutation = None
	Crossover = None
	population = None
	populationSize = None
	

	def __init__(self, cities, distances, execTime, popSize, pCross, pMutation, crossType, tSize):

		self.cities = cities
		self.distances = distances
		self.execTime = execTime
		self.populationSize = popSize
		self.pCrossover = pCross
		self.pMutation = pMutation

		'''
		-Creator y toolbox son parte de deap.
		-Con creator definimos "clases" FitnessMin y Individual
		
		-Cada Individual representa una solucion
		'''
		creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
		creator.create('Individual', array.array, typecode='i', fitness=creator.FitnessMin)

		#Con register definimos metodos a utilizar.
		self.toolbox = base.Toolbox()
		self.toolbox.register('randomOrder', random.sample, range(len(cities)), len(cities))
		self.toolbox.register('individualCreator', tools.initIterate, creator.Individual, self.toolbox.randomOrder)
		self.toolbox.register('populationCreator', tools.initRepeat, list, self.toolbox.individualCreator)
		#populationCreator crea una poblacion de Individuals con una soluciones propias aleatorias

		self.toolbox.register('evaluate', self.tspFitness)
		self.toolbox.register('select', tools.selTournament, tournsize=tSize)

		if crossType:
			self.toolbox.register('mate', tools.cxOrdered)
		else:	
			self.toolbox.register('mate', tools.cxPartialyMatched)

		self.toolbox.register('mutate', tools.mutShuffleIndexes, indpb=1.0 / len(cities))


	#Inicializa la población y los mejores(hof)
	def initialize(self):

		#Crea poblacion
		self.population = self.toolbox.populationCreator(n=self.populationSize)

		#Define el tamaño de la elite
		self.hofSize = self.populationSize // 10
		self.hof = tools.HallOfFame(self.hofSize)

		#asigna el fitness a cada Indiviual
		invalid_individuals = [ind for ind in self.population if not ind.fitness.valid]
		fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_individuals)
		for ind, fit in zip(invalid_individuals, fitnesses):
			ind.fitness.values = fit

		#Actualiza la elite comparando fitness
		self.hof.update(self.population)
		self.hof_size = len(self.hof.items)




	def start(self):

		timeStart = time.time()

		while int(time.time() - timeStart) < self.execTime:

			'''
			"offspring" representa a los hijos de la siguiente generacion, los cuales se generan a 
			partir de la poblacion - la elite.
			'''
			offspring = self.toolbox.select(self.population, len(self.population) - self.hofSize)
			offspring = algorithms.varAnd(offspring, self.toolbox, self.pCrossover, self.pMutation)

			#calcula el fitness de la siguiente generacion
			invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
			fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
			for ind, fit in zip(invalid_ind, fitnesses):
				ind.fitness.values = fit

			#Se agrega la elite anterior a la generacion nueva
			offspring.extend(self.hof.items)

			#Se actualiza la elite
			self.hof.update(offspring)

			#Se mata a la generación anterior y se continua con el offspring
			self.population[:] = offspring

			#Se obtiene el mejor de la población
			best = self.hof.items[0]

			#Se reporta el mejor actual y el tiempo en llegar a el
			if self.bestInd is None or self.bestInd.fitness.values[0] > best.fitness.values[0]:
				self.bestInd = best
				self.bestTime = time.time() - timeStart

				print("Tiempo:", round(time.time() - timeStart, 3), "\t\t", end="")
				print("Fitness:", round(best.fitness.values[0], 4))

		print("\n")
		print("Mejor resultado:")
		print("Tiempo:", round(self.bestTime, 3), "\t\t", end="")
		print("Fitness:", round(self.bestInd.fitness.values[0], 4))
		print("\nMejor Recorrido:")
		print(list(self.bestInd))

	#Retorna la distancia total del recorrido
	def tsp_distance(self, individual):

		distance = self.distances[individual[0]][individual[-1]]

		for i in range(len(cities) - 1):
			distance += self.distances[individual[i]][individual[i + 1]]
		return distance

	#retorna la tsp_distance como el fitness de un Individual
	def tspFitness(self, individual):
		return self.tsp_distance(individual),

	

#Lee el TSP
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

	cantidadCiudades = len(cities)
	distances = [[0] * cantidadCiudades for _ in cities]
	for i in range(cantidadCiudades):
		for j in range(i + 1, cantidadCiudades):
			# vector norm
			distance = np.linalg.norm(cities[j] - cities[i])
			distances[i][j] = distances[j][i] = distance

	return cities, distances


if __name__ == "__main__":

	tsp_path = None

	execTime = None

	numMinParams = 4

	#Cantidad de población
	popSize = 100

	#Probabilidad de cruza
	pCross = 0.9

	#Probabilidad de mutación
	pMutation = 0.1

	#Método de cruza
	crossType = True

	#Tamaño del torneo
	tSize = 3


	
	for i in range(1, len(sys.argv)):

		if sys.argv[i] == "-i":
			tsp_path = sys.argv[i+1]


			if not os.path.exists(tsp_path):
				print("Archivo invalido")
				exit()
				
		if sys.argv[i] == "-cr":
			if sys.argv[i+1] == "ox":
				crossType = True

			elif sys.argv[i+1] == "pmx":
				crossType = False				

			else:
				print("Metodo de cruza invalido")
				exit()		

		if sys.argv[i] == "-ts":
			try:
				tSize = int(sys.argv[i+1])

				if tSize < 2:
					print("Tamaño del torneo invalido")
					exit()

			except:
				print("Tamaño del torneo invalido")
				exit()

		if sys.argv[i] == "-t":

			# TODO: verificar que es un numero.
			execTime = sys.argv[i+1]
			try:
				execTime = int(execTime)

				if execTime < 1:
					print("Tiempo invalido")
					exit()

			except:
				print("Tiempo invalido")
				exit()

		if sys.argv[i] == "-p":

			popSize = sys.argv[i+1]
			try:
				popSize = int(popSize)

				if popSize < 10:
					print("Numero poblacion no valida")
					exit()

			except:
				print("Numero poblacion no valida")
				exit()

		if sys.argv[i] == "-c":

			pCross = sys.argv[i+1]
			try:
				pCross = float(pCross)

				if not(0 < pCross <= 1):
					print("Probabilidad cruza no valida")
					exit()

			except:
				print("Probabilidad cruza no valida")
				exit()

		if sys.argv[i] == "-m":

			pMutation = sys.argv[i+1]
			try:
				pMutation = float(pMutation)

				if not(0 < pMutation <= 1):
					print("Probabilidad mutation no valida")
					exit()
			except:
				print("Probabilidad mutation no valida")
				exit()

		if sys.argv[i] == "-h":
			print("Uso: -i <path del archivo> -t <tiempo en segundos> -p <numero de poblacion> -c <probabilidad de cruza> -m <probabilidad de mutacion> -cr <metodo de cruza {ox,pmx}> -ts <tamaño del torneo>")
			exit()

	if execTime is None or tsp_path is None:

		print("Huevo de Pascua")
		exit()

	

	cities, distances = read_tsp(tsp_path)

	a = Genetic_algotithm(cities, distances, execTime, popSize, pCross, pMutation, crossType, tSize)
	a.initialize()
	a.start()
