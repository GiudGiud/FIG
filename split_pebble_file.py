import numpy as np

Rpeb = 1.5

all_pebbles = open("same_univ2", "r")
# all_pebbles = open("try_01", "r")

pebbles_a1 = open("pebbles_a1", 'w')
pebbles_a2 = open("pebbles_a2", 'w')
pebbles_a3 = open("pebbles_a3", 'w')
pebbles_a4 = open("pebbles_a4", 'w')

N_out = 0
N_pebbles = 0

for line in all_pebbles.readlines():

    N_pebbles += 1
    line_split = line.split(" ")
    line_split = [elem for elem in line_split if elem]
    # print(line_split)
    x = float(line_split[0])
    y = float(line_split[1])
    R2 = x**2 + y**2

    if R2 > 35**2 and R2 < (46.1 + Rpeb) **2:
        pebbles_a1.write(line.replace("1000000", "1000001"))
    if R2 > (46.1 - Rpeb)**2 and R2 < (58.3 + Rpeb) **2:
        pebbles_a2.write(line.replace("1000000", "1000002"))
    if R2 > (58.3 - Rpeb)**2 and R2 < (96 + Rpeb)**2:
        pebbles_a3.write(line.replace("1000000", "1000003"))
    if R2 > (96 - Rpeb)**2 and R2 < 105**2:
        pebbles_a4.write(line.replace("1000000", "1000004"))
    if R2 < 35**2 or R2 > 105**2:
        print("Pebble out of bounds at radius", np.sqrt(R2), "cm")
        print(line)
        N_out += 1

print(N_out, "pebbles out of bounds out of", N_pebbles)
