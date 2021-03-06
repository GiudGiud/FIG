
'''
generate Latin Hypercube sampling for T_fuel from a uniform distribution Unif(600, 1200)
'''
from pyDOE import *
from scipy.stats import uniform
from more_itertools import unique_everseen
import math
import numpy as np


def sample_temperature(burnup_nb, fuel_nb, coating_nb, sample_nb):
  '''
  the 'main' function in this file
  '''
  temp_nb = fuel_nb +  2
  # assuming all the coatings have the same temperature
  LHSamp = LHS(burnup_nb, temp_nb, sample_nb)
  reshapeSamp = reshape(LHSamp, burnup_nb, fuel_nb, coating_nb, sample_nb)
  return reshapeSamp

def LHS(burnup_nb, layer_nb, sample_nb):
  '''
  return tsample: a (burnup_nb x layernb) x sample_nb matrix of randomly sampled temperatures between 600 and 1200 K 
  '''
  range = [800, 1500]  # range of the temperatures in K
  np.random.seed(3)
  sample = lhs(burnup_nb*layer_nb+1, samples = sample_nb)
  tsample = uniform(loc=range[0], scale=(range[1]-range[0])).ppf(sample)
  temps = tsample.reshape((sample_nb, burnup_nb*layer_nb+1))
  sol_temp = np.vectorize(math.floor)(temps[:, :-1].reshape(sample_nb, burnup_nb, layer_nb))
  liq_temp = np.vectorize(math.floor)(temps[:, -1])
  tsample = {'sol':sol_temp, 'liq':liq_temp}
  np.save('sample', tsample)
  return tsample

def reshape(temps, burnup_nb, fuel_nb, coating_nb, sample_nb):
  '''
  reshape the result from sampling_temp to a matrix that can be used for creating the
  FCC unit cell
  '''
  mat = temps['sol']
  reshaped_temp ={'sol':np.append(mat[:, :, 0:fuel_nb], 
                      mat[:,:, fuel_nb].reshape(sample_nb, burnup_nb, 1)*np.ones((sample_nb, burnup_nb, coating_nb)), axis=2),
                  'liq':temps['liq']}
  return reshaped_temp 
