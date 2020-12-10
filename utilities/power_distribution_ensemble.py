import numpy as np
import matplotlib.pyplot as plt
import csv

np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
np.set_printoptions(precision=3)

N_x = 20
N_y = 20
N_2 = N_x * N_y

###################################################
# LOAD ALL FILES

rr_mean_plot = np.zeros((N_x, N_y))
rr_all = np.zeros((N_x, N_y, 9))

for ii in range(1, 10):
    # Read file
    from oct2py import octave as oct
    oct.addpath("res/RANDOM_single_region/500_2000_5000_"+str(ii))
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

    # Keep running sum
    rr_mean_plot += rr_ref_plot
    rr_all[:,:,ii - 1] = rr_ref_plot

# Average results
rr_mean_plot /= 9

# Fission
plt.figure()
plt.imshow(rr_mean_plot)
plt.colorbar()
plt.savefig("serp_fission_rates_ref")
plt.show()

# Now get the standard deviation
for i in range(9):
    rr_all[:,:,i] /= rr_mean_plot
rr_std_plot = np.std(rr_all, 2)

plt.figure()
plt.imshow(rr_std_plot[1:16, 3:13] * 100)
plt.colorbar()
plt.savefig("serp_fission_real_unc")
plt.show()

print(np.mean(rr_std_plot))
