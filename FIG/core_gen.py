#!/usr/bin/python
from gen import Gen
from serp_concept import Cell, Universe, Detector, Surface
from FIG.pb_gen import FuelPbGen
from FIG.pbed_gen import FCCGen


class CoreGen(Gen):

    def parse(self, a_core, type):
        if type == 's':
            self.generate_sbatch_file(self.dir_name)

            str_list = []
            # define title and library path
            str_list.append('''%%---Cross section data library path\n''')
            str_list.append('set title "FHR core"\n')# +
                            #'set acelib "/hpc-common/data/serpent/xsdata/endfb7u"\n')
                            # use SERPENT_DATA and SERPENT_ACELIB variables instead

            univ_id_dict = {}
            if True: #a_core.purpose == 'XS_gen':

                # Give ids to each region
                univ_id_dict['CR'] = 100000
                univ_id_dict['CRCC'] = 100001

                multi_region = True
                if multi_region:
                    univ_id_dict['FuelW'] = 100002
                    univ_id_dict['FuelA1'] = 100003
                    univ_id_dict['FuelA2'] = 100004
                    univ_id_dict['FuelA3'] = 100005
                    univ_id_dict['FuelA4'] = 100006
                else:
                    univ_id_dict['FuelW'] = 100002
                    univ_id_dict['FuelA1'] = 100002
                    univ_id_dict['FuelA2'] = 100002
                    univ_id_dict['FuelA3'] = 100002
                    univ_id_dict['FuelA4'] = 100002

                univ_id_dict['Blanket'] = 100007

                univ_id_dict['OR'] = 100008
                univ_id_dict['ORCC'] = 100008

                univ_id_dict['Corebarrel'] = 100009
                univ_id_dict['Downcomer'] = 100009
                univ_id_dict['Vessel'] = 100009
            N_univ = 10
            surface_strings = {100000+i:'(' for i in range(N_univ)}

            # define geometry, cells, universe in the core in different files
            univ = Universe()
            for key1 in a_core.comp_dict:

                filename = '%s' % key1
                comp_str = []
                comp_str.append('\n%%---%s\n' % key1)

                univ_id = univ_id_dict[key1]

                for key2 in a_core.comp_dict[key1].comp_dict:
                    comp_str.append('%%---%s\n' % key2)
                    a_core.comp_dict[key1].comp_dict[key2].gen.set_univId(univ_id)
                    output_string = a_core.comp_dict[key1].comp_dict[key2].generate_output()

                    comp_str.append(output_string)

                    # Parse output string to get surfaces
                    surface_string = ''
                    for line in output_string.split('\n'):
                        surface_string = ''

                        # Skip all surf lines in case surf_id == univ_id
                        # solved by offsetting surface id

                        for surface_list in line.split(str(univ_id))[1:]:
                            for surface in surface_list.split(' ')[3:]:
                                surface_string += surface + ' '
                        if surface_string != '':
                            surface_strings[univ_id] += surface_string + '):('
                    # print(surface_strings[univ_id])

                comp_str.append(a_core.comp_dict[key1].generate_output())
                open(self.dir_name+filename, 'w+').write(''.join(comp_str))
                str_list.append('include "%s"\n' %filename)

            # define the whole core as universe 0, and cell 'outside'
            a_core.whole_core.gen.set_univId(0)
            whole_core_output = ('\n%%---Core as a whole, universe 0\n' +
                            a_core.whole_core.generate_output()).replace(str(univ_id_dict['FuelA1']), '200000')
            str_list.append(whole_core_output)
            str_list.append(
                '\n%%---Outside\ncell %d 0 outside %d\n' %
                (Cell().id, a_core.whole_core.surf_list[1].id))

            # Add all universes to cells contained in universe 0
            for i in range(N_univ):
                if 100000+i in univ_id_dict.values():
                    str_list.append('cell c'+str(i)+' 200000 fill '+str(100000+i)+
                                    ' '+surface_strings[100000+i][:-2]+'\n')

            # Material
            filename = 'coreMaterials'
            str_list.append('include "%s"' %filename)
            mat_str = []
            for mat in a_core.mat_list:
                if self.verbose:
                  print('create material %r' % mat)
                mat_str.append(mat.generate_output())
            open(self.dir_name+filename, 'w+').write(''.join(mat_str))

            # define neutron source and BC
            str_list.append('\n%%---Neutron source and BC\n')
            str_list.append('\n%%---set pop neutron-per-cycle cycles skip-cycles\n')
            str_list.append('set pop 100000 500 500\n')
            str_list.append('set bc 1\n')
            str_list.append('set ures 1\n')
            str_list.append('set power 2.36E8\n')

            # 8g but adjusted to match CASMO-70
            str_list.append('\nene \"8g_0\" 1 0 5.8e-8 1.9e-7 5e-7 4e-6 4.8e-5 2.5e-2 1.4 20\n')
            # str_list.append('\nene \"8g_1\" 1 1e-11 5.8e-8 1.8e-7 5e-7 4e-6 4.8052e-5 2.478e-2 1.353 20\n')
            # str_list.append('\nene \"10g\" 1 1E-11 2E-08 5E-08 8E-08 2E-07 6.5E-07 8.32E-06'
            # 	'1.301E-04	3.355E-03	1.11E-01	4E+01')  #10G option

            # From Development of a Reactor Physics Analysis Procedure for the Plank-Based
            # and Liquid Salt-Cooled Advanced High Temperature Reactors
            # Included in intermediate group structure though?
            # 4G also in ORNL presentation
            # str_list.append('\nene \"4g\"  1 0 7.3000E‐07 2.9023E‐05 9.1188E‐03 20\n')
            # str_list.append('\nene \"13g\" 1 0 1.2396E‐08 3.5500E‐08 5.6922E‐08 8.1968E‐08 1.1157E‐07'
            #                 '1.4572E‐07 1.8443E‐07 2.2769E‐07 2.5103E‐07 2.9074E‐07 4.5E-7 1.4739E‐04 20\n')

            # From http://publications.rwth-aachen.de/record/766688/files/766688.pdf (HTR 10)
            # str_list.append('\nene \"6g\" 1 0 1.2e-7 4.5e-7 3.059e-6 1.30073e-4 6.73795e-2 20\n')

            # From https://etda.libraries.psu.edu/files/final_submissions/3001
            # str_list.append('\nene \"10g\" 1 0 4E-08 4.3E-7 1.6E-6 2.38E-6 3.93E-6 2.04E-3 9.12E-3 5.25E-2 8.21E-1 20\n')

            # From Spectral zone selection methodology for pebble bed reactors
            # str_list.append('\nene \"8g\" 1 1.2E-7 4.07E-7 5.285E-7 1.046E-6 2.38E-6 7.102E-3 8.21E-1 20\n')

            # Add group cross section tallies per universe
            str_univ = ''
            if multi_region:
                for i in range(N_univ):
                    str_univ += str(100000+i) + ' '
            else:
                str_univ = '100000 100001 100002 100007 100008 100009'
            str_list.append('set gcu '+str_univ+'\n')
            str_list.append('set nfg 8g_0\n')
            str_list.append('set opti 1\n')

            # Add some reaction rate maps
            str_list.append('\n %% detectors\n')
            detnb = 1
            str_list.append('\n %% detector for reaction rates distributions\n')
            str_list.append('det 1 dn 1 0 175 20 0 360 1 0 500 20 dr -80 void\n') # power
            # str_list.append('det 2 dn 1 0 175 20 0 360 1 0 500 20 dr  18 void\n')  # fission
            # str_list.append('det 3 dn 1 0 175 20 0 360 1 0 500 20 dr  27 void de 8g_0\n')  # absorption
            detnb += 3

	        # str_list.append('\n %% detector for different burnup zones\n')
            # for i in range(8):
            #   str_list.append('det %d dn 1 35 105 10 0 360 1 103.22 388.9 10 dm fuel1pbw%d dr 18 fuel1pbw%d\n' %(detnb, i+1, i+1))
            #   str_list.append('det %d dn 1 35 105 10 0 360 1 103.22 388.9 10 dm fuel2pbw%d dr 18 fuel2pbw%d\n' %(detnb+1, i+1, i+1))
            #   str_list.append('det %d dn 1 35 105 10 0 360 1 103.22 388.9 10 dm fuel3pbw%d dr 18 fuel3pbw%d\n' %(detnb+2, i+1, i+1))
            #   detnb += 3

            # for i in range(8):
            #    str_list.append('det %d  dm fuel1pba1%d dr -8 fuel1pba1%d\n' %(detnb, i+1, i+1))
            #    str_list.append('det %d  dm fuel2pba1%d dr -8 fuel2pba1%d\n' %(detnb+1, i+1, i+1))
            #    str_list.append('det %d  dm fuel3pba1%d dr -8 fuel3pba1%d\n' %(detnb+2, i+1, i+1))
            #    detnb = detnb + 1

            # str_list.append('%% detector for power\n')
            # str_list.append('%det <name> dn 1 <rmin> <rmax> <nr>  <amin> <amax> <na> <zmin> <zmax> <nz>\n')
            # str_list.append('det %d dr -8 void dn 1 0  175 35 0 360 1 41 573 38\n' %detnb)
            # detnb = detnb + 1
            #
            # str_list.append('%% detector for thermal neutron flux\n')
            # str_list.append('ene 1 1 1E-11 0.625E-6\n')
            # str_list.append('det %d de 1 dn 1 0  175 35 0 360 1 41 573 38\n' %detnb)
            # detnb = detnb + 1
            #
            # str_list.append('%% detector for fast neutron flux\n')
            # str_list.append('ene 2 1 0.625E-6 200\n')
            # str_list.append('det %d de 2 dn 1 0  175 35 0 360 1 41 573 38\n' %detnb)
            # detnb = detnb + 1

            # str_list.append('%% detector for fast neutron flux in matrix for thermal conductivity correlation\n')
            # str_list.append('ene 2 1 0.1 200\n')
            # str_list.append('det %d de 2 dm matrix\n' %detnb)
            # detnb = detnb + 1

            if a_core.purpose != 'XS_gen':
                str_list.append('\n%%---Plot the geometry\n')
                str_list.append('plot 1 775 1591 0 0 175 0 531 %% yz cross plane at x=0\n')
                str_list.append('plot 2 775 1591 0 0 175 0 531 %% xz cross plane at y=0\n')
                str_list.append('plot 2 500 500 0 45 50 210 215 %% xz cross plane at y=0\n')

                for i in range(10):
                    z_slice = str(300+20*i)
                    str_list.append('plot 3 800 800 '+z_slice+' -150 150 -150 150 %% xy cross plane at z='+str(300+20*i)+'\n')

            return ''.join(str_list)

    def generate_sbatch_file(self, dir_name):
        with open('submit_templates/run_sss.pbs', 'r') as rf:
            text = rf.read()
            with open(''.join([dir_name, 'run_sss.pbs']), 'w') as f:
                f.write(text)
