'''
This file is used to generate cross-sections
'''

#!/usr/bin/python
from FIG.core import Core
from FIG.pb_gen import FuelPbGen
from FIG.pbed_gen import FCCGen
from FIG.serp_concept import Cell, Universe, Surface
from util.mkdir import mkdir
import config
import shutil
import numpy as np
from more_itertools import unique_everseen

# Default ranges for salt T, fuel T and CR insertion
temps_s = [300, 600, 900, 1200, 1500] # in K
temps_f = [300, 600, 900, 1200, 1500]
temps_g = [300, 600, 900, 1200, 1500]
insertions = [[False, False, False, False],
              [True, False, False, False],
              [True, True, False, False],
              [True, True, True, False],
              [True, True, True, True]]


def create_models(sample_nb,
                  gen_dir_name, hasRods=[False, False, False, False],
                  fuel_type='eq', hasShield=False, packing_fraction=0.6):
    '''
    create a number of models with sampled temperatures to fit a cross section model
    sample_nb: number of models(data samples)
    '''
    isOneFuel = True
    isOneCoating = False

    if fuel_type == 'burned':
        fuel_comp_folder_w = config.FLUX_ALL_AVE_FOLDER
        fuel_comp_folder_a = config.FLUX_ALL_AVE_FOLDER
        burnups_w = np.array([1, 1, 1, 1, 2, 2, 2, 2, 3, 4, 5, 6, 7, 8])
        burnups_a = np.array([1, 1, 1, 1, 2, 2, 2, 2, 3, 4, 5, 6, 7, 8])
    elif fuel_type == 'fresh':
        fuel_comp_folder_w = config.FRESH_FOLDER
        fuel_comp_folder_a = config.FRESH_FOLDER
        # 14 pebbles is hardwired
        burnups_w = np.array([0 for i in range(14)])
        burnups_a = np.array([0 for i in range(14)])
        burnup_nb = 1
    else:
        print("Check fuel type", fuel_type, stop)

    random_grid = False
    fuel_nb = 3
    coating_nb = 5
    if random_grid:
        # sample fuel temperatures for each layer
        from util.sample_temperature import sample_temperature
        burnup_nb = len(list(unique_everseen(burnups_w)))
        temps_mat = sample_temperature(burnup_nb, fuel_nb, coating_nb, sample_nb)
    else:
        temps_mat = {}
        temps_mat['sol'] = [np.tile(temps_f[i//(len(temps_s) * len(temps_g)) % len(temps_f)], (burnup_nb, fuel_nb)) for i in range(sample_nb)]
        temps_mat['liq'] = []
        temps_mat['CR'] = []
    mkdir(gen_dir_name)
    np.save(gen_dir_name+'temp_mat', temps_mat)

    # Generate a set of input files for serpent to get
    # group cross sections for different temperatures
    # - each of the 3 fuel layers in triso particles (no nee)
    # - each of the 4 or 8 burnups
    # - various control rod insertions
    for case, temps in enumerate(temps_mat['sol']):
        # set the counters for incremental parameters back to 0
        Cell.id = 1
        Universe.id = 1
        Surface.id = 1
        FuelPbGen.wrote_surf = False
        FCCGen.file_id = 0

        # Fuel core temperature
        tempsf = temps[:, 0:fuel_nb]
        Tfuel = tempsf[0][0]
        tempst = np.ones((burnup_nb, coating_nb)) * Tfuel

        # Coolant with pebbles temperature
        if random_grid:
            tempst = temps[:, fuel_nb:fuel_nb+coating_nb]
            temp_cool = temps_mat['liq'][case]
        else:
            temp_cool = temps_s[case % (len(temps_s))]
            hasRods = insertions[case // (len(temps_s) * len(temps_f) * len(temps_g))]

        # Outer structures temperature
        temp_g = temps_g[case // (len(temps_s)) % len(temps_g)]

        # Check temperature
        print(temp_cool, temp_g, tempsf[0][0], np.sum(hasRods))

        output_dir_name = gen_dir_name + 'input%d/' % case
        if not random_grid:
            output_dir_name = gen_dir_name + '/' + str(temp_cool) + '_' + str(tempsf[0][0]) + '_' + str(temp_g) + '_' + str(sum(hasRods)) + '/'

        core = Core(
            (tempsf, tempst, Tfuel, Tfuel, 'w', burnups_w,  fuel_comp_folder_w),
            (tempsf, tempst, Tfuel, Tfuel, 'a1', burnups_a, fuel_comp_folder_a),
            (tempsf, tempst, Tfuel, Tfuel, 'a2', burnups_a, fuel_comp_folder_a),
            (tempsf, tempst, Tfuel, Tfuel, 'a3', burnups_a, fuel_comp_folder_a),
            (tempsf, tempst, Tfuel, Tfuel, 'a4', burnups_a, fuel_comp_folder_a),
            temp_g,  # temp_CR
            temp_g,  # temp_g_CRCC
            temp_cool,  # temp_cool_CRCC, has to be equal to temp_cool_F or temp_cool_B for now, O/W flibeMaterial will be missing
            temp_g,  # temp_OR
            temp_g,  # temp_g_ORCC
            temp_cool,  # temp_cool_ORCC
            temp_cool,  # temp_cool_Fuel
            temp_cool,  # temp_blanket
            temp_cool,  # temp_cool_Blanket
            600+273.15,  # temp_Corebarrel  #too far from the core, does not matter
            600+273.15,  # temp_Downcomer
            600+273.15,  # temp_vessel
            output_dir_name,
            hasShield=hasShield,
            hasRods=hasRods,
            packing_fraction=packing_fraction,
            purpose='XS_gen')

        # write the model down
        mkdir(output_dir_name)
        print(output_dir_name)
        f = open(''.join([output_dir_name, '/serp_full_core']), 'w+')
        text = core.generate_output()
        f.write(text)
        f.close

        #TODO Reset the universe base id to 1 (0 is root)

    # write a readme file in the folder
    rd = open(''.join([gen_dir_name, '/readme']), 'w+')
    text = []
    text.append('Has rods: %s\n' %str(hasRods))
    text.append('Packing fraction %f\n' % packing_fraction)
    text.append('Same fuel composition in multi fuel zones: %s\n' % str(isOneFuel))
    text.append('Combined triso coatings into one layer: %s\n' % str(isOneCoating))
    #text.append('Coolant temperature', str(*temps_s), '\n')
    #text.append('Fuel temperature', *temps_f, '\n')
    text.append('Fuel type %s\n' %fuel_type)
    text.append('Has shield %s\n' %str(hasShield))

    rd.write(''.join(text))
    rd.close
