from math import sqrt as rc 
import math

#saca el coseno y me lo pasa de radianes a una medida usable
def coseno(num):
    return (math.cos(math.radians(num)))
    
#potencia a la dos de manera mas exacta el programa no tiene que bregar con decimales y tiene un mayor rendimiento(truco programacion comp)    
def pot(num):
    return num * num
        
    
#lo junta todo e implementacion de la formula de cleison     
def func(lad1, lad2, ai, af):
    at = abs(af - ai)
    ladx = 0; 
    
    ladx = pot(lad1) + pot(lad2) - (2*((lad1)*(lad2)))*coseno(at)
    return ladx
    

     
