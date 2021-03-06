#!/usr/bin/python
from FIG import triso
from FIG import pbed
from FIG import pb
from FIG import mat
from FIG.pb_gen import FuelPbGen
from FIG.serp_concept import Cell, Universe, Surface
from more_itertools import unique_everseen
from util.mkdir import mkdir
import config
import shutil
import numpy as np


def create_a_fuel_pebble(fuel_temps, coating_temps, cgt, sht, pbname, burnup, pb_comp_dir, gen_dir_name):
    '''
    create a fuel pebble, assuming all the triso particles in the pebble have the
    same temperature configurations(can have different temp in different triso
    layers though)
    fuel_temps: a list that contains temperature for each fuel
    layer in the triso, 1d array of length 1 or 3
    coating_temps: a list that contains temp for each of the non-fuel layers in triso
    cgt: central graphite temperature
    sht: shell temperature
    burnup: used to choose the fuel mat composition file in pb_comp_dir
    '''
    assert fuel_temps.shape == (1,) or fuel_temps.shape == (3,), 'wrong fuel temp shape:%r' %(fuel_temps.shape)
    assert coating_temps.shape == (1,) or coating_temps.shape == (5,), 'wrong coating temp shape:%r' %(fuel_temps.shape)

    # create fuel materials
    fuels = []
    for i, temp in enumerate(fuel_temps):
        fuel_name = 'fuel%d%s' % (i+1, pbname)
        fuel_input = '%s/fuel_mat%d' % (pb_comp_dir, burnup)
        fuels.append(mat.Fuel(temp, fuel_name, fuel_input))
    
    # create triso particle
    if coating_temps.shape == (1,):
        tr = triso.Triso(coating_temps,
                         fuels, 
                         dr_config='homogenized',
                         dir_name=gen_dir_name)
    else:
        tr = triso.Triso(coating_temps,
                         fuels, 
                         dr_config=None,
                         dir_name=gen_dir_name)
    return pb.FPb(tr, cgt, sht, dir_name=gen_dir_name)


def create_a_pb_list(fuel_temps, coating_temps, cgt, sht, uc_name, burnups, pb_comp_dir, gen_dir_name):
    '''
    fuel_temps: temperature list for unique pebbles in the unit cell
    a matrix of unique pebbles x n layers of fuel in a triso
    coating_temps: a list that contains temp for each of the non-fuel layers in triso, e.g. 4x5
    cgt: central graphite temperature
    sht: shell temperature
    '''
    fpb_list = []
    unique_fpb_list = {}
    unique_burnups = list(unique_everseen(burnups))

    unique_burnup_nb = len(unique_burnups)
    assert fuel_temps.shape[0] == unique_burnup_nb, 'wrong dimension %s' %str(fuel_temps.shape)
    assert coating_temps.shape[0] == unique_burnup_nb, 'wrong dimension' 
    # create a list of unique pebbles
    for i, bu in enumerate(unique_burnups):
        pb_name = 'pb%s%d' % (uc_name, bu)
        unique_fpb_list[bu] = create_a_fuel_pebble(fuel_temps[bu-1, :], 
                                                   coating_temps[unique_burnups[i]-1, :],
                                                   cgt, sht,
                                                   pb_name,
                                                   unique_burnups[i], 
                                                   pb_comp_dir, 
                                                   gen_dir_name)
    # create a list of all the 14 fuel pebbles, some of them are exactly the same
    for bu in burnups:
        fpb_list.append(unique_fpb_list[bu])
    return fpb_list


def create_the_unit_cell(fuel_temps,
                    triso_temps,
                    burnups,
                    pb_comp_dir,
                    gen_dir_name):
    '''
    fuel_temps: a list of temperatures used to define fuel layers 
    triso_temps: a list of temperatures used to define  layers
    '''

    pb_list = create_a_pb_list(fuel_temps, triso_temps, 900, 900, '', burnups, pb_comp_dir, gen_dir_name)
    from pbed import FuelUnitCell
    unit_cell = FuelUnitCell(pb_list, 900, packing_fraction=0.6, dir_name=gen_dir_name)
    mkdir(gen_dir_name)
    f = open(''.join([gen_dir_name, 'unit_cell']), 'w+')
    text = unit_cell.generate_output()
    f.write(text)
    f.close


if __name__ == "__main__":
    pb_burnups = np.array([1, 1, 1, 1, 2, 2, 2, 2, 3, 4, 5, 6, 7, 8])

    sample_nb = 20
    fuel_nb = 3 
    coating_nb = 5 
    burnup_nb = len(list(unique_everseen(pb_burnups)))
    temps = np.ones((burnup_nb, 8))*900 

    # generating a set of input files for serpent
    # to generat cross sections for different temperatures
    # each of the 3 fuel layers in triso particles
    # each of the 4 or 8 burnups
    Cell.id = 1
    Universe.id = 1
    Surface.id = 1
    FuelPbGen.wrote_surf = False

    tempsf = temps[:, 0:fuel_nb]
    tempst = temps[:, fuel_nb:fuel_nb+coating_nb]

    output_dir_name = 'res/'
    fuel_comp_folder = config.FLUX_ALL_AVE_FOLDER

    create_the_unit_cell(tempsf, 
                    tempst,
                    pb_burnups,
                    fuel_comp_folder,
                    output_dir_name)
