import numpy as np
import matplotlib.pyplot as plt
import csv

np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
np.set_printoptions(precision=3)

N_x = 20
N_y = 20
N_2 = N_x * N_y

###################################################
# LOAD REFERENCE

# Read file
from oct2py import octave as oct
oct.addpath("res/RANDOM_single_region/500_2000_250000")  #REFERENCE
oct.eval("serp_full_core_det0")
oct.eval("save -v7 saved_rates.mat")

from scipy.io import loadmat
dict = loadmat("saved_rates.mat")

# Plot reaction rates on 2D RZ plane
rr_ref = dict['DET1'][:, -2][:N_2].reshape((N_2, 1))
rr_ref_plot = rr_ref
rr_ref_plot = rr_ref_plot.reshape(N_x, N_y)

# Print coordinates
r_vec = dict['DET1R'][:,-1].reshape((N_x,1))
z_vec = dict['DET1Z'][:,-1].reshape((N_y,1))
r_vec /= 100
z_vec /= 100
print("r (=x)", r_vec.reshape(N_x))
print("z realigned (=y)", np.flipud(z_vec.reshape(N_y)) - 0.416)

# Normalize by volume
volumes = np.zeros((N_x, N_y))
for i in range(1, N_x):
    for j in range(N_y):
        volumes[i,j] = (5.3 / N_y) * (r_vec[i]**2 - r_vec[i-1] ** 2) * 2*np.pi
for j in range(N_y):
    volumes[0, j] = (5.3 / N_y) * (r_vec[0]**2) * 2*np.pi
volumes = np.transpose(volumes)

rr_ref_plot /= volumes

# Fission
plt.figure()
plt.imshow(rr_ref_plot)
plt.colorbar()
plt.savefig("serp_fission_rates_ref")
# plt.show()

###################################################
# LOAD COMPARED

# Read file
from oct2py import octave as oct1
oct1.addpath("res/RANDOM_single_region/500_2000_50000")
oct1.eval("serp_full_core_det0")
oct1.eval("save -v7 saved_rates.mat")

from scipy.io import loadmat
dict = loadmat("saved_rates.mat")

# Plot reaction rates on 2D RZ plane
rr = dict['DET1'][:, -2][:N_2].reshape((N_2, 1))
rr_plot = rr
rr_plot = rr_plot.reshape(N_x, N_y)

# Print coordinates
r_vec = dict['DET1R'][:,-1].reshape((N_x,1))
z_vec = dict['DET1Z'][:,-1].reshape((N_y,1))
r_vec /= 100
z_vec /= 100
print("r (=x)", r_vec.reshape(N_x))
print("z realigned (=y)", np.flipud(z_vec.reshape(N_y)) - 0.416)

# Normalize by volume
volumes = np.zeros((N_x, N_y))
for i in range(1, N_x):
    for j in range(N_y):
        volumes[i,j] = (5.3 / N_y) * (r_vec[i]**2 - r_vec[i-1] ** 2) * 2*np.pi
for j in range(N_y):
    volumes[0, j] = (5.3 / N_y) * (r_vec[0]**2) * 2*np.pi
volumes = np.transpose(volumes)

rr_plot /= volumes

# Fission
plt.figure()
plt.imshow((rr_plot - rr_ref_plot) / rr_ref_plot * 100)
plt.colorbar()
plt.savefig("serp_fission_rates_error")
plt.figure()
plt.imshow((rr_plot[2:14, 4:12] - rr_ref_plot[2:14, 4:12]) / rr_ref_plot[2:14, 4:12] * 100)
plt.colorbar()
plt.savefig("serp_fission_rates_error_zoom")
plt.show()

# Get statistics
ref = rr_ref_plot[2:14, 4:12]
com = rr_plot[2:14, 4:12]
rel = (com - ref) / ref * 100
print("RMS", np.sqrt(np.sum(rel * rel) / np.size(rel)) , "%")
print("MAX", np.max(np.abs(rel)), "%")
