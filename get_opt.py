from virus import read_tsp
import sys
import csv
import codecs


def read_tour(filepath):

	tour = []

	with open(filepath[:-4] + ".opt.tour", "br") as file:

		reader = csv.reader(codecs.iterdecode(file, 'utf-8'), delimiter=' ', skipinitialspace=True)

		for row in reader:
			if row[0] in ('TOUR_SECTION'):
				break
		for row in reader:
			if row[0] == 'EOF':
				break
			tour.append(int(row[0]))

	print(tour)

	return tour


def calculate_opt_distance(distances, tour):

	optDist = 0

	for i in range(len(tour)):

		if i == 0:
			continue

		if tour[i] == -1:
			print(tour[i-1], tour[0], distances[tour[i-1]-1][tour[0]-1])
			optDist += distances[tour[i-1]-1][tour[0]-1]
		else:
			print(tour[i-1], tour[i], distances[tour[i-1]-1][tour[i]-1])
			optDist += distances[tour[i-1]-1][tour[i]-1]

	return optDist



if len(sys.argv) < 2:
	print("ya pue el archivo")
	exit()

filePath = sys.argv[1]

cities, distances = read_tsp(filePath)
tour = read_tour(filePath)

print(calculate_opt_distance(distances, tour))

