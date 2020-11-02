from core_models.reference import create_the_model
import numpy as np


def create_feedback_models(gen_dir_name, flag):

    # Default parameters
    packing_fraction = 0.6
    isOneFuel = True
    isOneCoating = False
    hasShield = False
    fuel_type = 'Fresh'

    if flag == 'flibe':
        #densities =np.array([1700, 1800, 1900, 2000, 2100])
        #temps_s = (2413-densities)/0.488
        temps_s = [600, 900, 1100, 1300, 1500]
        for temp in temps_s:
            create_the_model(''.join([gen_dir_name, '/', str(int(temp)), '/']),
                             temp_cool=temp, purpose='XS_gen')

    elif flag == 'fuel':
        temps_f = [300, 600, 900, 1200, 1500]
        for temp in temps_f:
            create_the_model(''.join([gen_dir_name, '/', str(int(temp)), '/']),
                             temp_fuel=temp, purpose='XS_gen')

    elif flag == 'control_rod':
        insertions = [[False, False, False, False],
                      [True, False, False, False],
                      [True, True, False, False],
                      [True, True, True, False],
                      [True, True, True, True]]
        for insertion in insertions:
            sum_i = sum(insertion)
            create_the_model(''.join([gen_dir_name, '/', str(sum_i), '/']),
                             hasRods=insertion, purpose='XS_gen')

    # write a readme file in the folder
    rd = open(''.join([gen_dir_name, '/readme']), 'w+')
    text = []
    text.append('Rod insertion: 5 steps')
    text.append('Packing fraction %f\n' % packing_fraction)
    text.append('Same fuel composition in multi fuel zones: %s\n' % str(isOneFuel))
    text.append('Combined triso coatings into one layer: %s\n' % str(isOneCoating))
    text.append('Coolant temperature', *temps_s, '\n')
    text.append('Fuel temperature', *temps_f, '\n')
    text.append('Fuel type %s\n' %fuel_type)
    text.append('Has shield %s\n' %str(hasShield))
