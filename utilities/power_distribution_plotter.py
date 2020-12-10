import numpy as np
import matplotlib.pyplot as plt
import csv

np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
np.set_printoptions(precision=3)

N_x = 20
N_y = 20
N_2 = N_x * N_y

# Read file
from oct2py import octave as oct
oct.addpath("res/RANDOM_single_region")
oct.eval("serp_full_core_det0")
oct.eval("save -v7 saved_rates.mat")

from scipy.io import loadmat
dict = loadmat("saved_rates.mat")

# Plot reaction rates on 2D RZ plane
rr = dict['DET1'][:, -2][:N_2].reshape((N_2, 1))
rr_plot = rr
rr_plot = rr_plot.reshape(N_x, N_y)
rr_unc = dict['DET1'][:, -1][:N_2].reshape((N_2, 1))
rr_unc_plot = rr_unc
rr_unc_plot = rr_unc_plot.reshape(N_x, N_y)

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
plt.imshow(rr_plot)
plt.colorbar()
plt.savefig("serp_fission_rates")
# plt.show()

fig,ax = plt.subplots(2)
ax[0].imshow(rr_plot)
ax[1].imshow(rr_plot * volumes)
fig.savefig("serp_fission_volumes")
# fig.show()

# Uncertainty
plt.figure()
plt.imshow(rr_unc_plot * 100)
plt.colorbar()
plt.savefig("serp_fission_unc")
plt.title("Uncertainty (%)")
plt.show()

plt.figure()
plt.imshow(rr_unc_plot[1:16, 3:13] * 100)
plt.colorbar()
plt.savefig("serp_fission_unc_restricted")
plt.title("Uncertainty (%)")
plt.show()

print("On restricted region", np.mean(rr_unc_plot[2:14, 4:12]), np.max(rr_unc_plot[2:14, 4:12]))

# Normalize
rr /= np.sum(rr)

# Dump as txt file
ref = open("ref.txt", 'w')
ref.write(str(rr))
ref.close()

print("Sum volumes", np.sum(volumes), 2 * np.pi * r_vec[-1]**2)
print("Sum power density", np.sum(rr_plot), "sum power", np.sum(rr_plot * volumes))
print(np.flip(rr_plot, 0).reshape((1,N_2)))

# Concatenate and dump as CSV file
r_vec_0 = r_vec
z_vec_0 = z_vec
for i in range(N_2 // N_x - 1):
    r_vec = np.concatenate((r_vec, r_vec_0), axis=0)
    z_vec = np.concatenate((z_vec, z_vec_0), axis=1)
r_vec = r_vec.reshape((N_2, 1))
z_vec = z_vec.reshape((N_2, 1))
null_vec = np.zeros((N_2, 1))

rr = np.concatenate((r_vec, z_vec, null_vec, rr), axis=1)

with open('fission_rates.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for i in range(N_2):
        # print(rr[i, :])
        writer.writerow(rr[i, :])
