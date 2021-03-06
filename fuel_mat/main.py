'''
main file to 

1) read fuel composition from Mk1.txt MCNP input

2) generate fuel composition files that can be used in FIG to 
generate serpent input files

'''
import volume
import config
import pandas as pd
from ave_fuel_mat import sum_comp, sum_comp_2_zones
import numpy as np

# the weight(volume or flux) matrices have dimension 5x4x8
volmat = np.array(volume.get_volume()).reshape((4, 5, 1))
volmat = np.swapaxes(volmat, 0, 1)
print(volmat.shape)



print('compute average fuel composition for near wall zones')

# build a flux matrix for the wall regions by setting the
# active region flux to 0 in the full core flux matrix

# read volume*flux in each zone
fluxdf = pd.read_csv(config.FLUX_CSV_PATH, header=None)
fluxmat = fluxdf.values.reshape((5, 4, 8))
print('fluxmat')
print(fluxmat)
fluxmat_wall = fluxmat
for passno in range(1, 9):
  for R in range(2, 5):
    fluxmat_wall[2][R-1][passno-1] = 0

# for each pass, compute the weighted average(flux^2) fuel
# composition and write to file
for i in range(1, 9):
    flux_ave_fuel1 = sum_comp(fluxmat_wall*fluxmat_wall, passno=i)
    outputfile1 = config.FLUX_WALL_AVE_FOLDER + 'fuel_mat%d' % i
    flux_ave_fuel1.write_mat_to_file(comp_path=outputfile1)

print('compute (weighted) average fuel composition for center zones')
# build a flux matrix for the act regions by setting the values to the
# active regions and leave others to 0
# read volume*flux in each zone
fluxdf = pd.read_csv(config.FLUX_CSV_PATH, header=None)
fluxmat = fluxdf.values.reshape((5, 4, 8))
print('fluxmat')
print(fluxmat)
fluxmat_act = np.zeros((5, 4, 8))
for passno in range(1, 9):
  for R in range(2, 5):
    print(fluxmat[2][R-1][passno-1])
    fluxmat_act[2][R-1][passno-1] = fluxmat[2][R-1][passno-1]
print('flux mat for active region is\n')
print(fluxmat_act)

# for each pass, compute the weighted average(flux^2) fuel
# composition and write to file
for i in range(1, 9):
    flux_ave_fuel2 = sum_comp(fluxmat_act*fluxmat_act, passno=i)
    outputfile2 = config.FLUX_ACT_AVE_FOLDER + 'fuel_mat%d' % i
    flux_ave_fuel2.write_mat_to_file(comp_path=outputfile2)

print('compute for wall and active zones as a whole')
buw = np.array([1, 5, 2, 6, 3, 7, 4, 8])
bua = np.array([1, 1, 2, 2, 3, 3, 4, 4])

# construct the weight matrix
weights = np.zeros((5, 4, 8))
# add active zone weights(flux)
for pbno in range(1, 9):
  for Z in range(1, 6):
    for R in range(1, 5):
        weights[Z-1][R-1][pbno-1] += fluxmat[Z-1, R-1, bua[pbno-1]-1]
        weights[Z-1][R-1][pbno-1] += fluxmat[Z-1, R-1, buw[pbno-1]-1]

print(weights)

for i in range(1, 9):
    # sum up the composition 
    flux_ave_fuel = sum_comp_2_zones(weights, passno=[buw[i-1], bua[i-1]], pbnb=i)

    # write down into files
    outputfile = config.FLUX_ALL_AVE_FOLDER + 'fuel_mat%d' % i
    flux_ave_fuel.write_mat_to_file(comp_path=outputfile)
