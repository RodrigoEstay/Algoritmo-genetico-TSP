import os
import sys
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
				execTime = float(execTime)
			except:
				print("Tiempo invalido")
				exit()

	cities, distances = read_tsp(tsp_path)

	print(cities, distances)
