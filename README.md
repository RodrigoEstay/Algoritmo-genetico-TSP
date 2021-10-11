# Algoritmo-genetico-TSP

## Descripción

Algoritmo genético para resolver el problema del vendedor viajero simétrico, donde sólo se consideran distancias euclidianas en dos dimensiones. En esta implementación se considera un máximo de tiempo para el término del programa, no el número de generaciones, guardando el mejor resultado, es decir, un comportamiento de "Any-Time Behavior".

## Requerimientos

Se debe utilizar Python 3.X, e instalar los requerimientos presentes en `requirements.txt`, donde en Linux se puede realizar de la siguiente manera:

```console
pip3 install -r requirements.txt
```

## Ejecución

Los parámetros de ejecución aceptados son:

```console
python3 ga-tsp.py -i "path del archivo" -t "tiempo en segundos" -p "numero de poblacion" -c "probabilidad de cruza" -m "probabilidad de mutacion"
```

Para el correcto funcionamiento se deben específicar como mínimo un path al archivo que describe el problema del TSP con `-i`, el cual debe tener un formato utilizado en [TSPLIB 95](http://elib.zib.de/pub/mp-testdata/tsp/tsplib/tsp/index.html), también se debe definir el máximo tiempo de ejecución en segundos con `-t`.De todas maneras se puede consultar por ayuda:

```console
python3 ga-tsp.py -h
```

## Ejemplo 

Considerando los datos de un archivo `TSP_Data/a280.tsp`, y 10 segundos de ejecución, considerando los siguientes parámetros para el algoritmo genético:

- Tamaño de población de 250
- Probabilidad de cruce de 0.75 (75%)
- Probabilidad de mutación de 0.02 (2%)
- Ocupando cruzamiento ordenado (ox)
- Tamaño de torneo de 4 individuos

```console
python3 ga-tsp.py -i TSP_Data/a280.tsp -t 10 -p 250 -c 0.75 -m 0.02 -cr ox -ts 4
```

## Salida

El programa imprime el tiempo y fitness de la solución actual solamente si mejoró respecto a la mejor obtenida, donde el fitness es la distancia total del recorrido obtenido. Al término del tiempo de ejecución se indica el tiempo y fitness de la mejor solución obtenida y su recorrido.

