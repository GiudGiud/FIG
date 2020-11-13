import numpy as np

# Fuel volume considerations
N_fuel = 470000
rad_fuel = 0.015
pf = 0.6
vol_fuel = N_fuel * 4/3 * np.pi * rad_fuel ** 3 / pf
print("Check volume fuel", vol_fuel, 10.4)
vol_fuel = 10.4

# Geometrical dimensions
R_co = 0.8
R_ci = 0.71
R_o = 1.05
R_i = 0.35
z_chute = 5.3125 - 4.5125
z_cone = 4.5125 - 3.889
a1 = (R_o - R_co) / z_cone
a2 = (R_ci - R_i) / z_cone

# Volume of each part
v_chute = np.pi * (R_co**2 - R_ci **2)  * z_chute
v_cone1 = np.pi * (R_i**2 * z_cone + R_i * a1 * z_cone**2 + a1**2 * z_cone**3 / 3)
v_cone2 = np.pi * (R_co**2 * z_cone + R_co * a2 * z_cone**2 + a2**2 * z_cone**3 / 3)
v_cone = v_cone2 - v_cone1
print("volumes", v_chute, v_cone)
area_shell = np.pi * (R_o**2 - R_i **2)

height_cylinder_shell = (vol_fuel - v_chute - v_cone) / area_shell
max_height = 3.889 - 1.389
print("Cyl shell", height_cylinder_shell, "max", max_height)

v_rest = vol_fuel  - v_cone - max_height * area_shell
# Chute is not counted in active region

# Filling the bottom cones
z_contraction_1 = 1.389
z_fueling_1 = 0.709
z_cone3 = z_contraction_1 - z_fueling_1
R_e1 = 0.7541
a3 = (R_o - R_e1) / z_cone3
z_contraction_2 = 1.0322
z_fueling_2 = 0.859
z_cone4 = z_contraction_2 - z_fueling_2
R_e2 = 0.45
a4 = (R_e2 - R_i) / z_cone4
v_cone3 = np.pi * (R_e1**2 * z_cone3 + R_e1 * a3 * z_cone3**2 + a3**2 * z_cone3**3 / 3)
v_cone4 = np.pi * (R_e2**2 * z_cone4 + R_e2 * a4 * z_cone4**2 + a4**2 * z_cone4**3 / 3)
v_inner = (z_fueling_2 - z_fueling_1) * np.pi * (R_e2)**2

print("Volume to fill", v_rest)
print("Volume in of bottom area", v_cone3 - v_cone4 - v_inner)

# First expansion part completely filled
z_cone5 = z_contraction_1 - z_contraction_2 - 0.055
v_cone5 = np.pi * (R_o**2 * z_cone5 - R_o * a3 * z_cone5**2 + a3**2 * z_cone5**3 / 3)
print("Volume first part", v_cone5)

# Second expansion part only partially filled
z_cone6 = z_contraction_1 - z_fueling_2
v_cone6 = np.pi * (R_e1**2 * z_cone6 + R_e1 * a3 * z_cone6**2 + a3**2 * z_cone6**3 / 3)
print("Volume first + second part", v_cone6 - v_cone4)

# Find partial filling height by solving the polynomial system
coeffs = np.array([0,0,0,0])
coeffs[0] = - (v_rest - v_cone5) / np.pi
coeffs[1] = R_e1**2 - R_e2**2
coeffs[2] = R_e1 * a3 - R_e2 * a4
coeffs[3] = (a3**2 - a4**2) / 3
coeffs = coeffs * np.pi

roots = np.roots(np.flipud(coeffs))
print(roots)
