#!/usr/bin/python
from sets import Set


class mat_parser:

    '''
    convert material composition files from one format to another
    '''

    # isotopes not defined in serpent library
    not_in_serpent_lib = Set(
        ['43107', '55144', '57143', '46116', '45117', '88228', '94245',
         '83210', '92230', '86222', '91234', '92231', '86220', '84210',
         '37082', '28078', '37088', '41109', '34090', '43117', '32083',
         '56148', '52141', '62163', '33086', '36098', '28076', '31080',
         '60155', '62156', '55138', '44107', '63159', '57150', '49127',
         '55143', '35084', '58145', '37095', '62159', '43108', '65164',
         '58151', '45122', '36093', '40097', '47124', '53138', '35090',
         '34081', '47116', '45112', '63162', '29076', '42109', '44111',
         '48123', '59153', '27074', '49120', '48128', '41107', '51134',
         '69169', '40102', '36081', '48119', '44120', '39100', '31075',
         '50136', '35092', '52139', '38095', '44116', '30076', '82210',
         '37092', '49129', '59154', '54145', '47108', '43113', '46112',
         '43103', '32087', '51130', '64164', '40105', '30073', '56144',
         '48115', '46119', '33082', '35085', '55147', '70171', '57146',
         '31084', '57154', '48125', '59148', '43104', '36097', '61156',
         '52142', '37091', '58155', '41110', '51133', '36087', '66166',
         '49117', '60152', '49121', '33083', '48117', '33081', '33080',
         '33087', '33085', '33084', '33089', '33088', '48118', '41103',
         '47123', '47122', '47121', '47120', '47126', '49124', '47125',
         '47128', '63158', '39104', '39105', '39107', '39101', '39102',
         '39103', '59151', '59150', '59152', '59155', '59157', '59156',
         '59159', '59158', '31076', '54138', '54139', '54137', '43112',
         '43110', '43111', '43116', '43114', '43115', '52136', '52137',
         '52134', '52135', '52133', '52131', '52138', '31078', '45119',
         '30075', '30074', '53140', '53141', '53142', '53143', '45110',
         '45111', '31072', '31073', '31074', '45115', '30079', '31077',
         '50127', '33076', '33077', '50121', '33078', '33079', '50129',
         '50128', '55150', '29080', '29081', '63165', '63164', '63161',
         '63160', '63163', '37090', '37093', '37094', '37096', '37097',
         '37098', '37099', '62162', '62160', '62161', '62164', '62165',
         '49134', '49132', '49133', '49130', '49131', '60160', '60161',
         '38104', '38103', '38102', '38101', '38100', '29066', '53137',
         '57153', '57152', '57151', '66165', '53139', '45121', '45120',
         '45123', '44118', '65163', '65162', '65161', '44110', '44117',
         '65165', '44114', '58149', '58148', '58147', '58146', '41097',
         '41096', '41099', '41098', '42115', '42114', '42111', '42110',
         '42113', '42112', '44115', '59146', '59147', '59144', '59145',
         '59149', '46120', '46121', '46122', '46123', '46124', '46126',
         '56139', '54141', '54140', '54143', '54142', '54144', '54147',
         '54146', '47115', '64161', '64162', '64163', '64165', '60154',
         '60157', '60156', '60151', '60153', '60159', '60158', '53133',
         '38094', '38097', '53132', '38091', '53134', '38093', '38092',
         '30068', '38099', '38098', '30066', '53136', '30067', '50130',
         '50131', '50132', '50133', '50134', '50135', '55148', '55146',
         '55145', '55142', '55140', '55141', '56149', '56143', '56142',
         '56141', '56147', '56146', '56145', '48131', '48130', '48132',
         '53144', '61152', '40109', '61150', '61157', '61154', '61155',
         '40100', '40101', '61158', '61159', '40104', '40106', '40107',
         '62157', '60149', '38096', '62158', '46111', '46113', '46115',
         '46114', '46117', '46118', '34091', '34092', '69170', '57148',
         '57149', '64159', '57141', '57142', '57144', '57145', '57147',
         '69171', '27075', '27073', '27072', '52140', '28072', '58156',
         '58157', '58154', '58152', '58153', '58150', '28073', '42106',
         '42107', '42104', '42105', '42102', '42103', '42101', '42108',
         '41102', '41101', '41100', '41106', '41105', '41104', '41108',
         '30077', '44108', '44109', '32079', '32078', '32075', '32077',
         '32084', '32085', '51131', '51137', '51136', '51135', '51139',
         '51138', '32088', '62155', '36096', '36095', '36094', '36092',
         '36091', '36090', '53128', '35089', '35088', '35080', '35083',
         '35082', '35087', '35086', '45118', '31079', '44113', '44112',
         '30072', '47117', '47114', '48129', '47112', '47113', '47110',
         '48122', '48120', '48121', '48126', '48127', '47118', '47119',
         '45113', '45114', '4010', '45116', '30078', '61162', '61161',
         '61160', '40098', '40099', '40108', '67166', '46109', '56150',
         '56152', '6014', '34083', '40103', '34086', '34087', '34084',
         '34085', '30082', '34088', '34089', '29078', '43109', '37100',
         '43101', '43100', '43102', '43105', '43106', '52127', '52129',
         '70172', '61153', '70170', '55139', '49114', '49116', '45109',
         '45108', '45107', '45106', '45104', '49118', '49119', '31081',
         '31083', '31082', '39098', '39099', '39096', '39097', '39094',
         '39095', '39092', '39093', '68171', '41111', '51132', '32086',
         '48124', '32080', '37089', '32081', '32082', '51128', '51129',
         '51127', '51122', '49128', '49125', '49126', '49123', '49122',
         '36088', '36089', '29075', '29074', '29077', '29073', '29072',
         '28077', '28074', '28075', '29079', '30083', '30080', '30081',
         '35093', '35091', '35096', '35094', '35095', '48109', '61548',
         '95642'])
            # above are isotopes from origen results but not in serpent library

    def __init__(self, inp, outp):
        self.inp = inp
        self.outp = outp

    def beau2serp(self):
        '''
        convert fuel material composition files from 
	BEAU depletion calculation results to serpent syntax
        '''
        with open(self.outp, 'w+') as f:
            with open(self.inp, 'r+') as input:
                lines = input.readlines()
                for line in lines:
                    if len(line) < 20:
                        pass
                    elif line[7] != str(0) and line[7] != str(1):
                        if not line[8:18] == '0.0000E+00' \
                                and line[2:6] not in mat_parser.not_in_serpent_lib:
                            f.write(line[2: 6])
                            f.write(' ')
                            f.write(line[8: 18])
                            f.write('\n')
                        else:
                            print 'isotope %s fraction =0 or not in serp lib'
                    else:
                        if not line[9:19] == '0.0000E+00' and\
                                line[2:7] not in mat_parser.not_in_serpent_lib:
                            f.write(line[2: 7])
                            f.write(' ')
                            f.write(line[9: 19])
                            f.write('\n')
                        else:
                            print 'isotope %s fraction =0 or not in serp lib' %line[2:7]
        f.close
        input.close


    def mcnp_2_serp(self):
        mat_dict = {}
        text = []
        with open(self.inp, 'r+') as f:
            for line in f:
                isotope = line.split()[0].split('.')[0]
                fraction = line.split()[1]
                if isotope not in mat_parser.not_in_serpent_lib:
                    mat_dict[isotope] = fraction
                    text.append(isotope + ' '+fraction+'\n')
                else:
                    print 'isotope %s fraction =0 or not in serp lib' %isotope
            with open(self.outp, 'w+') as of:
                of.write(''.join(text))
        of.close()
        f.close()
