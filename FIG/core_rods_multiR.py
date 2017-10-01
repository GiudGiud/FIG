#!/usr/bin/python
'''
This is a core class, contains a FHR core with coolant
channels inside the center and outer reflectors
# all dimensions in cm
# all temperatures in K
'''

from core_gen import CoreGen
from comp import *
import math
from centerref import CenterRef, CRCC, CRCC_Cool, CRCC_liner, CRCC_axial_segment, CRCC_gr, Control_rod
# from control_rod import Control_rod
from outerref import OuterRef, OuterRef_CoolantChannel
from vessel import Vessel
from downcomer import Downcomer
from corebarrel import Corebarrel
from blanket import Blanket
from fuel import Fuel
from fuel import Fuel_wall, Fuel_act

class Core(Comp):

    def __init__(
            self,
            fpb_list_w,
            fpb_list_a,
            temp_CR,
            temp_rod_CRCC,
            temp_cool_CRCC,
            temp_OR,
            temp_g_ORCC,
            temp_cool_ORCC,
            temp_cool_F,
            temp_Blanket,
            temp_cool_B,
            temp_Corebarrel,
            temp_Downcomer,
            temp_Vessel,
            dir_name='res/serp_input/'):

        assert(len(fpb_list_w) == 14), 'pb_list length is wrong, expected 14 pbs, got %d' % len(
            fpb_list_w)
        assert(len(fpb_list_a) == 14), 'pb_list length is wrong, expected 14 pbs, got %d' % len(
            fpb_list_a)

        self.comp_dict = {}

        self.CR = CenterRef(temp_CR)
        self.CRCC = CRCC(temp_rod_CRCC, temp_cool_CRCC, temp_CR)
        self.OR = OuterRef(temp_OR)
        self.ORCC = OuterRef_CoolantChannel(temp_g_ORCC, temp_cool_ORCC)
        self.FuelW = Fuel_wall(fpb_list_w, temp_cool_F, dir_name)
        self.FuelA = Fuel_act(fpb_list_a, temp_cool_F, dir_name)
        self.Blanket = Blanket(temp_Blanket, temp_cool_B, dir_name)
        self.Vessel = Vessel(temp_Vessel)
        self.Downcomer = Downcomer(temp_Downcomer)
        self.Corebarrel = Corebarrel(temp_Corebarrel)


        self.define_CR(self.CR.temp, self.CR.name, liner=True)
        self.define_OR(self.OR.temp, self.OR.name)
        self.define_ORCC(self.ORCC.temp, self.ORCC.name)
        self.define_FuelW(self.FuelW.temp, self.FuelW.name)
        self.define_FuelA(self.FuelA.temp, self.FuelA.name)
        self.define_Blanket(self.Blanket.temp, self.Blanket.name)
        self.define_Vessel(self.Vessel.temp, self.Vessel.name)
        self.define_Downcomer(self.Downcomer.temp, self.Downcomer.name)
        self.define_Corebarrel(self.Corebarrel.temp, self.Corebarrel.name)

        self.comp_dict = {
            'CR': self.CR,
            'CRCC':self.CRCC,
            'OR': self.OR,
            'ORCC': self.ORCC,
            'FuelW': self.FuelW,
            'FuelA': self.FuelA,
            'Blanket': self.Blanket,
            'Vessel': self.Vessel,
            'Downcomer': self.Downcomer,
            'Corebarrel': self.Corebarrel}

        self.whole_core = CylComp(fpb_list_w[0].temp,
                                  'whole_core',
                                  self.FuelA.act.mat_list,
                                  41.6,
                                  572.85,
                                  176.8,
                                  fill=self.FuelA.act)
        # contains not only self.Fuel but other three component, but they are
        # in the same universe, only need it to get the univ id
        name = 'FullCore'
        mat_list = self.collect_mat()
        Comp.__init__(self, fpb_list_w[0].temp,
                      name, mat_list, CoreGen(dir_name))

    # def adding_CRCC_to_CR(self):
    #   for key in self.CRCC.comp_dict:
    #       name = 'cc%s'%key
    #       self.CR.comp_dict[name] = self.CRCC.comp_dict[key]

    def define_CR(self, temp, name, liner):
        '''
        liner
        '''
        self.CR.comp_dict = {}
        # ---------------------------------------------------------
        # center reflector
        # entrance zone
        self.CR.zb_ent = 41.6  # in the design, CR starts at 15.7cm
        self.CR.zt_ent = 127.5
        self.CR.r_ent = 35+10
        self.CR.ent = CylComp(temp, name,
                              self.CR.mat_list, self.CR.zb_ent,
                              self.CR.zt_ent, self.CR.r_ent,
                              fill=self.CR.fill)
        self.CR.comp_dict['ent'] = EmbeddedComp(self.CR.ent,
                                                self.CRCC.comp_dict)

        # diverging
        self.CR.zb_div = self.CR.zt_ent
        self.CR.zt_div = 144.82
        self.CR.r_div = self.CR.r_ent
        self.CR.a_div = 60.0/180*math.pi
        self.CR.h_cone_div = self.CR.r_div * math.tan(self.CR.a_div)
        self.CR.div = TruncConeComp(
            temp, name,
            self.CR.mat_list,
            self.CR.zb_div,
            self.CR.zt_div,
            self.CR.zb_div,
            self.CR.h_cone_div,
            self.CR.r_div,
            fill=self.CR.fill)
        self.CR.comp_dict['div'] = EmbeddedComp(self.CR.div,
                                                self.CRCC.comp_dict)
        # active zone
        self.CR.zb_act = self.CR.zt_div
        self.CR.zt_act = 430.50
        self.CR.r_act = 35
        self.CR.act = CylComp(temp, name, 
                              self.CR.mat_list, self.CR.zb_act,
                              self.CR.zt_act, self.CR.r_act,
                              fill=self.CR.fill)
        self.CR.comp_dict['act'] = EmbeddedComp(self.CR.act,
                                                self.CRCC.comp_dict)

        # Converging
        self.CR.zb_conv = self.CR.zt_act
        self.CR.zt_conv = 492.85
        self.CR.r_conv = 61+10
        self.CR.a_conv = 60.0/180*math.pi
        self.CR.h_cone_conv = -self.CR.r_conv * math.tan(self.CR.a_conv)
        # negative h means direction to -z
        self.CR.conv = TruncConeComp(temp, name,
                                     self.CR.mat_list,
                                     self.CR.zb_conv,
                                     self.CR.zt_conv,
                                     self.CR.zt_conv,
                                     self.CR.h_cone_conv,
                                     self.CR.r_conv,
                                     fill=self.CR.fill)
        self.CR.comp_dict['conv'] = EmbeddedComp(self.CR.conv,
                                                 self.CRCC.comp_dict)

        # defueling
        self.CR.r_defuel = self.CR.r_conv
        self.CR.zb_defuel = self.CR.zt_conv
        self.CR.zt_defuel = self.CR.zb_defuel + 80
        self.CR.defuel = CylComp(temp, name,
                                 self.CR.mat_list,
                                 self.CR.zb_defuel,
                                 self.CR.zt_defuel,
                                 self.CR.r_defuel,
                                 fill=self.CR.fill)
        self.CR.comp_dict['defuel'] = EmbeddedComp(self.CR.defuel,
                                                   self.CRCC.comp_dict)

        # substract CRCC's from CR
        #self.comp_dict['CR'] = CenterRefWithoutCC(self.CR, self.CRCC)

#        self.CRCC.zb_act = 41.6
#        self.CRCC.zt_act = self.CR.zt_conv+80
#        self.CRCC.ri_act = self.CR.r_act
#        self.CRCC.ro_act = self.CR.r_act + 10
#
#        self.CRCC.act = AnnuCylComp(temp, name,
#                                    self.CRCC.mat_list,
#                                    self.CRCC.ri_act,
#                                    self.CRCC.ro_act,
#                                    self.CRCC.zb_act,
#                                    self.CRCC.zt_act)
#
#        self.CRCC.comp_dict['act'] = self.CRCC.act
# ---------------------------------------------------------
# center reflector
# entrance zone
# self.CRCC.zb_ent = 41.6  # in the design, CR starts at 15.7cm
#        self.CRCC.zt_ent = 127.5
#        self.CRCC.ri_ent = self.CR.r_ent
#        self.CRCC.ro_ent = 45
#
#        self.CRCC.ent = AnnuCylComp(temp, name,
#                                    self.CRCC.mat_list,
#                                    self.CRCC.ri_ent,
#                                    self.CRCC.ro_ent,
#                                    self.CRCC.zb_ent,
#                                    self.CRCC.zt_ent)
#
#        self.CRCC.comp_dict['ent'] = self.CRCC.ent
#
# diverging
#        self.CRCC.zb_div = self.CRCC.zt_ent
#        self.CRCC.zt_div = self.CR.zt_div
#        self.CRCC.ri_cone_div = self.CRCC.ri_ent
#        self.CRCC.ro_cone_div = self.CRCC.ro_ent
#        self.CRCC.ai_div = 60.0/180*math.pi
#        self.CRCC.ao_div = 60.0/180*math.pi
#        self.CRCC.hi_cone_div = self.CRCC.ri_cone_div * \
#            math.tan(self.CRCC.ai_div)
#        self.CRCC.ho_cone_div = self.CRCC.ro_cone_div * \
#            math.tan(self.CRCC.ao_div)
#
#        self.CRCC.div = AnnuConeConeComp(temp, name,
#                                         self.CRCC.mat_list,
#                                         self.CRCC.ri_cone_div,
#                                         self.CRCC.hi_cone_div,
#                                         self.CRCC.zb_div,
#                                         self.CRCC.ro_cone_div,
#                                         self.CRCC.ho_cone_div,
#                                         self.CRCC.zb_div,
#                                         self.CRCC.zb_div,
#                                         self.CRCC.zt_div)
#
#        self.CRCC.comp_dict['div'] = self.CRCC.div
#
# active zone
#        self.CRCC.zb_act = self.CRCC.zt_div
#        self.CRCC.zt_act = self.CR.zt_act
#        self.CRCC.ri_act = self.CR.r_act
#        self.CRCC.ro_act = self.CR.r_act + 10
#
#        self.CRCC.act = AnnuCylComp(temp, name,
#                                    self.CRCC.mat_list,
#                                    self.CRCC.ri_act,
#                                    self.CRCC.ro_act,
#                                    self.CRCC.zb_act,
#                                    self.CRCC.zt_act)
#
#        self.CRCC.comp_dict['act'] = self.CRCC.act
#
# Converging
#        self.CRCC.zb_conv = self.CRCC.zt_act
#        self.CRCC.zt_conv = self.CR.zt_conv
#        self.CRCC.ri_conv = self.CR.r_conv
#        self.CRCC.ro_conv = self.CR.r_conv + 10
#        self.CRCC.ai_conv = 60.0/180*math.pi
#        self.CRCC.ao_conv = 60.0/180*math.pi
#        self.CRCC.hi_cone_conv = -self.CRCC.ri_conv * \
#            math.tan(self.CRCC.ai_conv)
#        self.CRCC.ho_cone_conv = -self.CRCC.ro_conv * \
#            math.tan(self.CRCC.ao_conv)
# negative h means direction to -z
#
#        self.CRCC.conv = AnnuConeConeComp(temp, name,
#                                          self.CRCC.mat_list,
#                                          self.CRCC.ri_conv,
#                                          self.CRCC.hi_cone_conv,
#                                          self.CRCC.zt_conv,
#                                          self.CRCC.ro_conv,
#                                          self.CRCC.ho_cone_conv,
#                                          self.CRCC.zt_conv,
#                                          self.CRCC.zb_conv,
#                                          self.CRCC.zt_conv)
#
#        self.CRCC.comp_dict['conv'] = self.CRCC.conv
#
# defueling
#        self.CRCC.ri_defuel = self.CRCC.ri_conv
#        self.CRCC.ro_defuel = self.CRCC.ro_conv
#        self.CRCC.zb_defuel = self.CRCC.zt_conv
#        self.CRCC.zt_defuel = self.CRCC.zb_defuel + 80
#        self.CRCC.defuel = AnnuCylComp(temp, name,
#                                       self.CRCC.mat_list,
#                                       self.CRCC.ri_defuel,
#                                       self.CRCC.ro_defuel,
#                                       self.CRCC.zb_defuel,
#                                       self.CRCC.zt_defuel)
#        self.CRCC.comp_dict['defuel'] = self.CRCC.defuel
#
    def define_OR(self, temp, name):
        # --------------------------------------------------------
        # Outer reflector
        self.OR.r_outer = 165   # outer radius for the whole o_ref
        self.OR.comp_dict = {}

        # entrance zone
        self.OR.zb_ent = 41.6
        self.OR.zt_ent = 112.5
        self.OR.r_ent = 85.74
        self.OR.ent = AnnuCylComp(temp, name,
                                  self.OR.mat_list,
                                  self.OR.r_ent,
                                  self.OR.r_outer,
                                  self.OR.zb_ent,
                                  self.OR.zt_ent,
                                  fill=self.OR.fill)
        self.OR.comp_dict['ent'] = self.OR.ent

        # diverging  zone
        self.OR.a_div = math.pi*60.0/180
        self.OR.zb_div = 112.5
        self.OR.zt_div = 180.5
        self.OR.r_cone_div = 125   # self.OR.r_ent + \
            # (self.OR.zt_div - self.OR.zb_div)/math.tan(self.OR.a_div)
        self.OR.h_cone_div = -self.OR.r_cone_div*math.tan(self.OR.a_div)
        #  negative sign means direction -z
        self.OR.div = AnnuCylConeComp(
                temp, name,
                self.OR.mat_list,
                self.OR.r_cone_div,
                self.OR.h_cone_div,
                self.OR.zt_div,
                self.OR.r_outer,
                self.OR.zb_div,
                self.OR.zt_div,
                fill=self.OR.fill)

        self.OR.comp_dict['div'] = self.OR.div

        # active zone
        self.OR.r_act = 125 + 10
        self.OR.zb_act = self.OR.zt_div
        self.OR.zt_act = self.CR.zt_defuel
        self.OR.act = AnnuCylComp(temp, name,
                                  self.OR.mat_list,
                                  self.OR.r_act,
                                  self.OR.r_outer,
                                  self.OR.zb_act,
                                  self.OR.zt_act,
                                  fill=self.OR.fill)

        self.OR.comp_dict['act'] = self.OR.act


    def define_ORCC(self, temp, name):
        # --------------------------------------------------------
        # Outer reflector with coolant channel
        self.ORCC.comp_dict = {}

        # entrance zone
        #self.ORCC.zb_ent = self.OR.zb_ent
        #self.ORCC.zt_ent = self.OR.zt_ent
        #self.ORCC.ri_ent = self.OR.r_ent - 10
        #self.ORCC.ro_ent = self.OR.r_ent
        #self.ORCC.ent = AnnuCylComp(temp, name,
        #                            self.ORCC.mat_list,
        #                            self.ORCC.ri_ent,
        #                            self.ORCC.ro_ent,
        #                            self.ORCC.zb_ent,
        #                            self.ORCC.zt_ent)
        #self.ORCC.comp_dict['ent'] = self.ORCC.ent

        # diverging  zone
        #self.ORCC.ai_div = math.pi*60.0/180
        #self.ORCC.ao_div = math.pi*60.0/180
        #self.ORCC.zb_div = 112.5
        #self.ORCC.zt_div = 180.5
        #self.ORCC.ri_cone_div = 125
        #self.ORCC.hi_cone_div = -self.ORCC.ri_cone_div * \
        #    math.tan(self.ORCC.ai_div)
        #self.ORCC.ro_cone_div = self.OR.r_cone_div
        #self.ORCC.ho_cone_div = -self.ORCC.ro_cone_div * \
        #    math.tan(self.ORCC.ao_div)
        ##  negative sign means direction -z

        #self.ORCC.div = AnnuConeConeComp(temp, name,
        #                                 self.ORCC.mat_list,
        #                                 self.ORCC.ri_cone_div,
        #                                 self.ORCC.hi_cone_div,
        #                                 self.ORCC.zt_div,
        #                                 self.ORCC.ro_cone_div,
        #                                 self.ORCC.ho_cone_div,
        #                                 self.ORCC.zt_div,
        #                                 self.ORCC.zb_div,
        #                                 self.ORCC.zt_div)

        #self.ORCC.comp_dict['div'] = self.ORCC.div

        # active zone
        self.ORCC.ri_act = self.OR.r_act - 10
        self.ORCC.ro_act = self.OR.r_act
        self.ORCC.zb_act = 180.5
        self.ORCC.zt_act = 430.5
        self.ORCC.act = AnnuCylComp(temp, name,
                                    self.ORCC.mat_list,
                                    self.ORCC.ri_act,
                                    self.ORCC.ro_act,
                                    self.ORCC.zb_act,
                                    self.ORCC.zt_act,
                                    fill=self.ORCC.fill)

        self.ORCC.comp_dict['act'] = self.ORCC.act

        # convergeing zone
        self.ORCC.ri_cone_conv = self.ORCC.ri_act
        self.ORCC.ro_conv = self.ORCC.ro_act
        self.ORCC.ai_conv = 60.0 * math.pi/180
        #self.ORCC.ao_conv = 60.0 * math.pi/180
        self.ORCC.hi_cone_conv = self.ORCC.ri_cone_conv *\
            math.tan(self.ORCC.ai_conv)
        #self.ORCC.ho_cone_conv = self.ORCC.ro_cone_conv *\
        #    math.tan(self.ORCC.ao_conv)
        self.ORCC.zb_conv = self.ORCC.zt_act
        self.ORCC.zt_conv = self.CR.zb_defuel

        self.ORCC.conv = AnnuCylConeComp(temp, name,
                                        self.ORCC.mat_list,
                                        self.ORCC.ri_cone_conv,
                                        self.ORCC.hi_cone_conv,
                                        self.ORCC.zb_conv,
                                        self.ORCC.ro_conv,
                                        self.ORCC.zb_conv,
                                        self.ORCC.zt_conv,
                                        fill=self.ORCC.fill)

        self.ORCC.comp_dict['conv'] = self.ORCC.conv

        # defueling zone
        self.ORCC.zb_defuel = self.ORCC.zt_conv
        self.ORCC.zt_defuel = self.CR.zt_defuel
        self.ORCC.a_conv = math.pi*60/180.0
        self.ORCC.ri_defuel = self.ORCC.ri_cone_conv -\
            (self.ORCC.zt_conv-self.ORCC.zb_conv)/math.tan(self.ORCC.a_conv)
        self.ORCC.ro_defuel = self.ORCC.ro_act

        self.ORCC.defuel = AnnuCylComp(temp, name,
                                       self.ORCC.mat_list,
                                       self.ORCC.ri_defuel,
                                       self.ORCC.ro_defuel,
                                       self.ORCC.zb_defuel,
                                       self.ORCC.zt_defuel,
                                       fill=self.ORCC.fill)

        self.ORCC.comp_dict['defuel'] = self.ORCC.defuel

    def define_FuelW(self, temp, name):
        # ---------------------------------------------------------
        # fuel zone
        # --------------------------------------------------------
        self.FuelW.comp_dict = {}
        # entrance zone
        self.FuelW.zb_ent = 41.6  # in design report fuel pb starts at 41.6cm
        self.FuelW.zt_ent = self.OR.zt_ent
        self.FuelW.ri_ent = self.CR.r_ent
        self.FuelW.ro_ent = 75.41
        self.FuelW.ent = AnnuCylComp(temp, name,
                                    self.FuelW.mat_list,
                                    self.FuelW.ri_ent,
                                    self.FuelW.ro_ent,
                                    self.FuelW.zb_ent,
                                    self.FuelW.zt_ent,
                                    fill=self.FuelW.fill)
        self.FuelW.comp_dict['ent'] = self.FuelW.ent
        # diverging  zone 1
        self.FuelW.ro_div = 105
        self.FuelW.a_div1 = math.atan((self.OR.zt_div-self.OR.zb_div) /
                                     (self.FuelW.ro_div-self.FuelW.ro_ent))
        self.FuelW.zb_div1 = self.OR.zt_ent
        self.FuelW.zt_div1 = self.CR.zb_div
        self.FuelW.r_cone_div1 = self.FuelW.ro_div
        self.FuelW.h_cone_div1 = -self.FuelW.r_cone_div1 * \
            math.tan(self.FuelW.a_div1)
        self.FuelW.z_cone_div1 = self.OR.zt_div
        #  negative sign means direction -z
        self.FuelW.ri_div1 = self.FuelW.ri_ent
        self.FuelW.div1 = AnnuConeCylComp(temp, name,
                                         self.FuelW.mat_list,
                                         self.FuelW.r_cone_div1,
                                         self.FuelW.h_cone_div1,
                                         self.FuelW.z_cone_div1,
                                         self.FuelW.ri_div1,
                                         self.FuelW.zb_div1,
                                         self.FuelW.zt_div1,
                                         fill=self.FuelW.fill)
        self.FuelW.comp_dict['div1'] = self.FuelW.div1

        # diverging  zone 2
        self.FuelW.ao_div2 = self.FuelW.a_div1
        self.FuelW.ai_div2 = math.pi * 60.0/180.0
        self.FuelW.zb_div2 = self.FuelW.zt_div1
        self.FuelW.zt_div2 = self.CR.zt_div
        self.FuelW.ri_div2 = self.FuelW.ri_ent
        self.FuelW.h_cone_i_div2 = self.FuelW.ri_div2 * \
            math.tan(self.FuelW.ai_div2)
        self.FuelW.ro_cone_div2 = self.FuelW.r_cone_div1
        self.FuelW.ho_cone_div2 = self.FuelW.h_cone_div1
        self.FuelW.zo_cone_div2 = self.OR.zt_div
        self.FuelW.div2 = AnnuConeConeComp(temp, name,
                                          self.FuelW.mat_list,
                                          self.FuelW.ri_div2,
                                          self.FuelW.h_cone_i_div2,
                                          self.FuelW.zb_div2,
                                          self.FuelW.ro_cone_div2,
                                          self.FuelW.ho_cone_div2,
                                          self.FuelW.zo_cone_div2,
                                          self.FuelW.zb_div2,
                                          self.FuelW.zt_div2,
                                          fill=self.FuelW.fill)
        self.FuelW.comp_dict['div2'] = self.FuelW.div2

        # diverging  zone 3
        self.FuelW.a_div3 = self.FuelW.a_div1
        self.FuelW.zb_div3 = self.FuelW.zt_div2
        self.FuelW.zt_div3 = self.OR.zt_div
        self.FuelW.r_i_div3 = self.CR.r_act
        self.FuelW.r_cone_div3 = self.FuelW.ro_cone_div2
        self.FuelW.h_cone_div3 = self.FuelW.ho_cone_div2
        self.FuelW.div3 = AnnuConeCylComp(temp, name,
                                         self.FuelW.mat_list,
                                         self.FuelW.r_cone_div3,
                                         self.FuelW.h_cone_div3,
                                         self.FuelW.zt_div3,
                                         self.FuelW.r_i_div3,
                                         self.FuelW.zb_div3,
                                         self.FuelW.zt_div3,
                                         fill=self.FuelW.fill)
        self.FuelW.comp_dict['div3'] = self.FuelW.div3

        # active zone
        self.FuelW.zb_act = self.FuelW.zt_div3
        self.FuelW.zt_act = self.CR.zt_act
        self.FuelW.ro_act = 46.1
        self.FuelW.act = AnnuCylComp(temp, name,
                                    self.FuelW.mat_list,
                                    self.CR.r_act,
                                    self.FuelW.ro_act,
                                    self.FuelW.zb_act,
                                    self.FuelW.zt_act,
                                    fill=self.FuelW.fill)
        self.FuelW.comp_dict['act'] = self.FuelW.act
        # convergeing zone
        self.FuelW.zb_conv = self.FuelW.zt_act
        self.FuelW.zt_conv = self.CR.zt_conv
        self.FuelW.ri_conv = self.CR.r_conv
        self.FuelW.ai_conv = 60.0 * math.pi/180
        self.FuelW.hi_conv = -1.0*self.FuelW.ri_conv*math.tan(self.FuelW.ai_conv)
        self.FuelW.ro_conv = self.FuelW.ro_div
        self.FuelW.ao_conv = math.atan((self.FuelW.zt_conv - self.FuelW.zb_conv) /
                                      (self.FuelW.ro_div - 80))
        self.FuelW.ho_conv = self.FuelW.ro_conv*math.tan(self.FuelW.ao_conv)
        self.FuelW.conv = AnnuConeConeComp(temp, name,
                                          self.FuelW.mat_list,
                                          self.FuelW.ri_conv,
                                          self.FuelW.hi_conv,
                                          self.FuelW.zt_conv,
                                          self.FuelW.ro_conv,
                                          self.FuelW.ho_conv,
                                          self.FuelW.zb_conv,
                                          self.FuelW.zb_conv,
                                          self.FuelW.zt_conv,
                                          fill=self.FuelW.fill)
        self.FuelW.comp_dict['conv'] = self.FuelW.conv

        # defueling zone
        self.FuelW.zb_defuel = self.FuelW.zt_conv
        self.FuelW.zt_defuel = self.ORCC.zt_defuel
        self.FuelW.ri_defuel = self.CR.r_defuel
        self.FuelW.ro_defuel = self.FuelW.ro_div -\
            (self.FuelW.zt_conv - self.FuelW.zb_conv)/math.tan(self.FuelW.ao_conv)
        self.FuelW.defuel = AnnuCylComp(temp, name,
                                       self.FuelW.mat_list,
                                       self.FuelW.ri_defuel,
                                       self.FuelW.ro_defuel,
                                       self.FuelW.zb_defuel,
                                       self.FuelW.zt_defuel,
                                       fill=self.FuelW.fill)
        self.FuelW.comp_dict['defuel'] = self.FuelW.defuel

    def define_FuelA(self, temp, name):
        # ---------------------------------------------------------
        # fuel zone
        # --------------------------------------------------------
        self.FuelA.comp_dict = {}
        # active zone
        self.FuelA.zb_act = self.FuelW.zt_div3
        self.FuelA.zt_act = self.CR.zt_act
        self.FuelA.ro_act = self.FuelW.ro_div
        self.FuelA.act = AnnuCylComp(temp, name,
                                    self.FuelA.mat_list,
                                    self.FuelW.ro_act,
                                    self.FuelA.ro_act,
                                    self.FuelA.zb_act,
                                    self.FuelA.zt_act,
                                    fill=self.FuelA.fill)
        self.FuelA.comp_dict['act'] = self.FuelA.act

    def define_Blanket(self, temp, name):
        # -------------------------------------------------------------
        # Blanket
        # ------------------------------------------------------------
        self.Blanket.comp_dict = {}
        # entrance zone
        self.Blanket.zb_ent = 41.6  # in design report 41.6
        self.Blanket.zt_ent = self.OR.zt_ent
        self.Blanket.ri_ent = self.FuelW.ro_ent
        self.Blanket.ro_ent = self.OR.r_ent
        self.Blanket.ent = AnnuCylComp(temp, name,
                                       self.Blanket.mat_list,
                                       self.Blanket.ri_ent,
                                       self.Blanket.ro_ent,
                                       self.Blanket.zb_ent,
                                       self.Blanket.zt_ent,
                                       fill=self.Blanket.fill)
        self.Blanket.comp_dict['ent'] = self.Blanket.ent

        # diverging  zone
        self.Blanket.ai_div = self.FuelW.a_div1
        self.Blanket.zb_div = self.Blanket.zt_ent
        self.Blanket.zt_div = self.OR.zt_div
        self.Blanket.ri_div = self.FuelW.div3.ro
        self.Blanket.h_cone_i_div = -1.0 * self.Blanket.ri_div * \
            math.tan(self.Blanket.ai_div)
        self.Blanket.ao_div = math.pi*60.0/180
        self.Blanket.ro_div = self.OR.div.ri
        self.Blanket.h_cone_o_div = -1.0*self.Blanket.ro_div * \
            math.tan(self.Blanket.ao_div)
        self.Blanket.div = AnnuConeConeComp(temp, name,
                                            self.Blanket.mat_list,
                                            self.Blanket.ri_div,
                                            self.Blanket.h_cone_i_div,
                                            self.Blanket.zt_div,
                                            self.Blanket.ro_div,
                                            self.Blanket.h_cone_o_div,
                                            self.Blanket.zt_div,
                                            self.Blanket.zb_div,
                                            self.Blanket.zt_div,
                                            fill=self.Blanket.fill)
        self.Blanket.comp_dict['div'] = self.Blanket.div

        # active zone
        self.Blanket.ri_act = self.FuelA.act.ro
        self.Blanket.ro_act = self.ORCC.ri_act
        self.Blanket.zb_act = self.Blanket.zt_div
        self.Blanket.zt_act = self.CR.zt_act
        self.Blanket.act = AnnuCylComp(temp, name,
                                       self.Blanket.mat_list,
                                       self.Blanket.ri_act,
                                       self.Blanket.ro_act,
                                       self.Blanket.zb_act,
                                       self.Blanket.zt_act,
                                       fill=self.Blanket.fill)
        self.Blanket.comp_dict['act'] = self.Blanket.act

        # convergeing zone
        self.Blanket.ri_conv = self.FuelW.ro_conv
        self.Blanket.ai_conv = self.FuelW.ao_conv
        self.Blanket.hi_conv = self.Blanket.ri_conv * \
            math.tan(self.Blanket.ai_conv)
        self.Blanket.ro_conv = self.Blanket.ro_act
        self.Blanket.ao_conv = 60.0 * math.pi/180
        self.Blanket.ho_conv = self.Blanket.ro_conv * \
            math.tan(self.Blanket.ao_conv)
        self.Blanket.zb_conv = self.Blanket.zt_act
        self.Blanket.zt_conv = self.CR.zt_conv
        self.Blanket.conv = AnnuConeConeComp(temp, name,
                                             self.Blanket.mat_list,
                                             self.Blanket.ri_conv,
                                             self.Blanket.hi_conv,
                                             self.Blanket.zb_conv,
                                             self.Blanket.ro_conv,
                                             self.Blanket.ho_conv,
                                             self.Blanket.zb_conv,
                                             self.Blanket.zb_conv,
                                             self.Blanket.zt_conv,
                                             fill=self.Blanket.fill)
        self.Blanket.comp_dict['conv'] = self.Blanket.conv

        # defueling zone
        self.Blanket.ri_defuel = self.FuelW.ro_defuel
        self.Blanket.ro_defuel = self.ORCC.ri_defuel
        self.Blanket.defuel = AnnuCylComp(temp, name,
                                          self.Blanket.mat_list,
                                          self.Blanket.ri_defuel,
                                          self.Blanket.ro_defuel,
                                          self.CR.zb_defuel,
                                          self.CR.zt_defuel,
                                          fill=self.Blanket.fill)
        self.Blanket.comp_dict['defuel'] = self.Blanket.defuel

    def define_Corebarrel(self, temp, name):
        self.Corebarrel.ri = 165
        self.Corebarrel.ro = 168
        self.Corebarrel.act = AnnuCylComp(temp, name,
                                          self.Corebarrel.mat_list,
                                          self.Corebarrel.ri,
                                          self.Corebarrel.ro,
                                          self.CR.zb_ent,
                                          self.CR.zt_defuel,
                                          fill=self.Corebarrel.fill)
        self.Corebarrel.comp_dict = {}
        self.Corebarrel.comp_dict['act'] = self.Corebarrel.act

    def define_Downcomer(self, temp, name):
        self.Downcomer.ri = 168
        self.Downcomer.ro = 170.8
        self.Downcomer.act = AnnuCylComp(temp, name,
                                         self.Downcomer.mat_list,
                                         self.Downcomer.ri,
                                         self.Downcomer.ro,
                                         self.CR.zb_ent,
                                         self.CR.zt_defuel,
                                         fill=self.Downcomer.fill)
        self.Downcomer.comp_dict = {}
        self.Downcomer.comp_dict['act'] = self.Downcomer.act

    def define_Vessel(self, temp, name):
        self.Vessel.ri = 170.8
        self.Vessel.ro = 176.8
        self.Vessel.act = AnnuCylComp(temp, name,
                                      self.Vessel.mat_list,
                                      self.Vessel.ri,
                                      self.Vessel.ro,
                                      self.CR.zb_ent,
                                      self.CR.zt_defuel,
                                      fill=self.Vessel.fill
                                      )
        self.Vessel.comp_dict = {}
        self.Vessel.comp_dict['act'] = self.Vessel.act

    def collect_mat(self):
        mat_list = []
        for comp in self.comp_dict:
            for mat in self.comp_dict[comp].mat_list:
                if mat not in mat_list:
                    mat_list.append(mat)
        return mat_list

