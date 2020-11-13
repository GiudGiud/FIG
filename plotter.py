import numpy as np
import matplotlib.pyplot as plt
import csv

N_x = 20
N_y = 20
N_2 = N_x * N_y

# Read file
from oct2py import octave as oct
oct.eval("res/reference_no_xe/random_res/serp_full_core_det0")
oct.eval("save -v7 saved_rates.mat")

from scipy.io import loadmat
dict = loadmat("saved_rates.mat")

# Plot reaction rates on 2D RZ plane
rr = dict['DET1'][:, -2][:100].reshape((N_2 // 2, 1))
rr_plot = rr
rr_plot = rr_plot.reshape(N, N)

plt.figure()
plt.imshow(rr_plot)
plt.savefig("serp_fission")
# plt.show()

# Normalize
rr /= np.sum(rr)

# Dump as txt file
ref = open("ref.txt", 'w')
ref.write(str(rr))
ref.close()

# Print coordinates
r_vec = dict['DET1R'][:,-1].reshape((N,1))
z_vec = dict['DET1Z'][:,-1].reshape((N,1))
r_vec /= 100
z_vec /= 100
print(r_vec.reshape(N), z_vec.reshape(N))
print(rr.reshape(N_2))

# Concatenate and dump as CSV file
r_vec_0 = r_vec
z_vec_0 = z_vec
for i in range(N_2 // N - 1):
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
