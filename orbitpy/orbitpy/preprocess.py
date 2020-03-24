""" 
.. module:: preprocess

:synopsis: *Module to handle pre-processing of user inputs.*

.. note::  - Lat must be in the range -pi/2 to pi/2, while lon must be in the range -pi to pi

"""
import numpy as np
import os
import subprocess
import json
import shutil
import warnings
from .util import EnumEntity, PropagationCoverageParameters, FileUtilityFunctions, Constants
from instrupy.public_library import Instrument

class ConstellationType(EnumEntity):
    """Enumeration of recognized constellation types"""
    CUSTOM = "CUSTOM",
    WALKERDELTA = "WALKERDELTA"

class FOVGeometry(EnumEntity):
    """Enumeration of recognized instrument sensor geometries."""
    CONICAL = "CONICAL",
    RECTANGULAR = "RECTANGULAR",
    CUSTOM = "CUSTOM"

class OrbitParameters():
    """ Data structure to hold orbit parameters """
    def __init__(self, id=None, sma=None, ecc=None, inc=None, raan=None, aop=None, ta=None):
        self.id = id
        self.sma = sma
        self.ecc = ecc
        self.inc = inc
        self.raan = raan
        self.aop = aop
        self.ta = ta

class InstrumentCoverageParameters():
    """ Data structure to hold instrument coverage related parameters 
        (field-of-view and orientation) 
    """
    def __init__(self, fov_geom=None, fov_cone=None, fov_clock=None, fov_at = None, fov_ct = None, 
                 orien_eu_seq1=None, orien_eu_seq2=None, orien_eu_seq3=None, 
                 orien_eu_ang1=None, orien_eu_ang2=None, orien_eu_ang3=None):
        
        try:
            self.fov_geom = FOVGeometry.get(fov_geom)
            self.fov_cone = [float(i) for i in fov_cone]
            self.fov_clock = [float(i) for i in fov_clock] if fov_clock is not None else None # clock can be "None" if Conical Sensor
            if(self.fov_clock is None):
                if(self.fov_geom=='CONICAL'):
                    self.fov_clock = [0]
                else:
                    print("Missing clock angles from instrument coverage specifications for non-conical sensor fov.")
                    raise Exception()
            self.fov_at = float(fov_at)
            self.fov_ct = float(fov_ct)
            self.orien_eu_seq1 = int(orien_eu_seq1)
            self.orien_eu_seq2 = int(orien_eu_seq2)
            self.orien_eu_seq3 = int(orien_eu_seq3)
            self.orien_eu_ang1 = float(orien_eu_ang1)
            self.orien_eu_ang2 = float(orien_eu_ang2)
            self.orien_eu_ang3 = float(orien_eu_ang3)
        except:
            raise

class PreProcess(): 
    """ Class to handle pre-processing of user inputs.
    
    :ivar epoch: Mission epoch in Gregorian UTC format
    :vartype epoch: str
    
    :ivar covGridFn: Coverage grid filename (output file)
    :vartype covGridFn: str
    
    """
    def __init__(self, specs=dict(), user_dir=None):
        
        try:

            try:
                self.user_dir = str(user_dir)
            except ValueError:
                print('Invalid user_dir')
                raise            
            try:
                self.state_dir = self.user_dir + 'state/'
                if os.path.exists(self.state_dir):
                    shutil.rmtree(self.state_dir)
                os.makedirs(self.state_dir) 
                self.access_dir = self.user_dir + 'access/'
                if os.path.exists(self.access_dir):
                    shutil.rmtree(self.access_dir)
                os.makedirs(self.access_dir)  
                self.comm_dir = self.user_dir + 'comm/'
                if os.path.exists(self.comm_dir):
                   shutil.rmtree(self.comm_dir)
                os.makedirs(self.comm_dir) 
                self.gndstn_dir = self.user_dir + 'gndStn/'
                if os.path.exists(self.gndstn_dir):
                    shutil.rmtree(self.gndstn_dir)
                os.makedirs(self.gndstn_dir) 
            except:
                print('Error in removing and/or creating state, access, comm and gndstn directories.')
                raise
            try:
                self.epoch = str(specs['epoch'])
            except ValueError:
                print('Valid epoch, please')
                raise
            try:
                self.duration = float(specs['duration'])
            except ValueError:
                print('Valid duration, please')
                raise
            try:
                self.orbits = PreProcess.enumerate_orbits(specs['constellation'])
            except:
                print('Error in enumerating orbits')
                raise
            try:
                o = Instrument.from_json(specs["instrument"])
                [self.instru, self.sen_type, self.sen_orien, self.sen_clock, self.sen_cone] = \
                    PreProcess.process_instru_cov_specs(FileUtilityFunctions.from_json(o.get_coverage_specs()))     
            except:
                print('Error in obtaining instrument specifications')
                raise 
            try:
                _time_step = PreProcess.compute_time_step(self.orbits, self.instru, Constants.time_res_fac)
                if 'customTimeStep' in specs['settings']:                    
                    self.time_step = float(specs['settings']['customTimeStep'])
                    if(_time_step < self.time_step ):
                        warnings.warn("Custom time-step larger than computed time-step")
                        print("Custom time-step [s]: ", self.time_step)
                        print("Computed time-step [s]: ", _time_step)
                else:
                    self.time_step = _time_step
            except:
                print('Error in processing time step')
                raise            
            try:
                if 'customGridRes' in specs['settings']:
                    self.grid_res = float(specs['settings']['customGridRes'])
                else:
                    self.grid_res = PreProcess.compute_grid_res(self.orbits, self.instru, Constants.grid_res_fac)
            except:
                print('Error in processing grid resolution')
                raise
            try:
                self.cov_grid_fl = PreProcess.process_cov_grid(self.user_dir, specs['grid'], self.grid_res)
            except:
                print('Error in processessing coverage grid')
                raise    
            try:
                self.gnd_stn_fl = self.user_dir + str(specs['groundStations']['gndStnFn'])
            except ValueError:
                print('Invalid ground station file name')
                raise              
        except:
            raise Exception("Error in processing user JSON input file.")

    
    @staticmethod
    def process_instru_cov_specs(ics = dict()):

        try:
            m = InstrumentCoverageParameters(ics["fieldOfView"]["geometry"], 
                                            ics["fieldOfView"]["coneAnglesVector"], ics["fieldOfView"]["clockAnglesVector"],
                                            ics["fieldOfView"]["AlongTrackFov"], ics["fieldOfView"]["CrossTrackFov"],
                                            ics["Orientation"]["eulerSeq1"], ics["Orientation"]["eulerSeq2"], ics["Orientation"]["eulerSeq3"],
                                            ics["Orientation"]["eulerAngle1"], ics["Orientation"]["eulerAngle2"], ics["Orientation"]["eulerAngle3"]
                                            )
        except:
            print("Error in obtaining instrument coverage specifications. Perhaps required dict field missing.")
            raise       

        # Return the instrument converage specifications in format required for 
        # calling the orbitpropcov (C++) script.
        sen_type = m.fov_geom.name
        sen_orien = str(m.orien_eu_seq1) + ',' + str(m.orien_eu_seq2) + ',' + str(m.orien_eu_seq3) + ',' + \
                    str(m.orien_eu_ang1) + ',' + str(m.orien_eu_ang2) + ',' + str(m.orien_eu_ang3)       
        sen_clock = [str(i) for i in m.fov_clock]        
        sen_clock = ','.join(sen_clock)        
        sen_cone = [str(i) for i in m.fov_cone]        
        sen_cone = ','.join(sen_cone)        

        return [m, sen_type, sen_orien, sen_clock, sen_cone]


    @staticmethod
    def enumerate_orbits(constel=dict()):
        """ Enumerate all the orbits (corresponding to unique satellites) in the constellation.
        
            :param constel: Constellation specifications (Custom or Walker Delta)
            :paramtype constel: dict

            :returns: Orbits (parameters) in the constellation 
            :rtype: list, :class:`orbitpy.preprocess.OrbitParameters`

        
        """
        
        constel_type = ConstellationType.get(constel['type'])        
        
        if(constel_type is None):
            raise Exception("Invalid constellation type.")

        elif(constel_type == 'CUSTOM'):
            # read in the list of orbits
             if isinstance(constel['orbits'], list) and len(constel['orbits']) > 1:
                 orbits = PreProcess.custom_orbits(constel['orbits'])

        elif(constel_type == 'WALKERDELTA'):
            orbits = PreProcess.walker_orbits(constel)
        
        else:
            raise Exception(("Unknown error in PreProcess.enumerate_orbits"))        


        return orbits

    @staticmethod
    def custom_orbits(data):
        num_of_orbs = len(data)
        orbits = []
        for orb_i in range(0,num_of_orbs):
            _orb = data[orb_i]
            orbits.append(OrbitParameters(_orb['id'], _orb['sma'], _orb['ecc'], _orb['inc'],
                                          _orb['raan'], _orb['aop'], _orb['ta']))                   
        return orbits


    @staticmethod
    def walker_orbits(data):
        
        try:
            num_sats = data['numberSatellites']
            num_planes = data['numberPlanes']
            rel_spc = data['relativeSpacing']
            sma = Constants.radiusOfEarthInKM + data['alt']
            ecc = data['ecc']
            inc = data['inc']
            aop = data['aop']
        except:
            print("Error in parsing Walker Delta constellation specs. Perhaps missing entry?")
            raise

        num_sats_pp = num_sats/num_planes
        if(not num_sats_pp.is_integer()):
            print("Ratio of number of satellites to number of planes must be an integer.")
            raise Exception()
        else:
            num_sats_pp = int(num_sats_pp)

        orbits = []
        for pl_i in range(0,num_planes):
            raan = pl_i * 360.0/num_planes
            ta_ref = pl_i * rel_spc * 360.0/num_sats
            for sat_i in range(0,num_sats_pp):
                orb_id = str(pl_i) + str(sat_i)
                ta = (ta_ref + sat_i * 360.0/num_sats_pp)%360
                orbits.append(OrbitParameters(orb_id, sma, ecc, inc,
                                          raan, aop, ta)) 
                print(orb_id, sma, ecc, inc, raan, aop, ta)

        return orbits
        #raise Exception("Sorry! Walker Delta constellation type not yet supported!")


    def generate_prop_cov_param(self):
        ''' Generate propagation and coverage parameters. Each enumerated orbit (in the constellation) 
            corresponds to one set of propagation and coverage parameters. 
        '''              
        # For each orbit, create and separate PropagationCoverageParameters object and append to a list.
        prop_cov_param = []
        for orb_indx in range(0,len(self.orbits)):       
            orb = self.orbits[orb_indx]            
            sat_state_fl = self.state_dir +'sat'+str(orb.id)
            sat_acc_fl = self.access_dir +'sat'+str(orb.id)+'_accessInfo'
            pcp = PropagationCoverageParameters(sat_id=orb.id, epoch=self.epoch, sma=orb.sma, ecc=orb.ecc, inc=orb.inc, 
                     raan=orb.raan, aop=orb.aop, ta=orb.ta, duration=self.duration, cov_grid_fl=self.cov_grid_fl, 
                     sen_type=self.sen_type, sen_orien=self.sen_orien, sen_clock=self.sen_clock, sen_cone=self.sen_cone, 
                     step_size=self.time_step, sat_state_fl = sat_state_fl, sat_acc_fl = sat_acc_fl)

            prop_cov_param.append(pcp)
            
        return prop_cov_param

    @staticmethod
    def process_cov_grid(user_dir, grid, grid_res):
        """ Process coverage grid (auto or custom) and return the filename with path
            containing the grid info.
        """               
        # get path to *this* file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        prc_args = [os.path.join(dir_path, '..', 'oci', 'bin', 'genCovGrid')]
        
        if "autoGrid" in grid:
            # Generate grid based on user input lat, lon bounds
            autoGrid = grid["autoGrid"]
            try:
                cov_grid_fl = user_dir + autoGrid["covGridFn"] # coverage grid file path   
            except:
                raise RuntimeError('Grid filename must be specified under the field "covGridFn"')        
            prc_args.append(cov_grid_fl)
            #reg = [cov_grid_fl] # list of string arguments to be given to the 'genCovGrid' process

            try:
                regions = autoGrid["regions"]            
                # process the dictionary entries of (possibly) multiple regions into strings
                # Format: 'region_id, lat_upper, lat_lower, lon_upper, lon_lower, grid_res' 
                for reg_indx in range(0,len(regions)):
                    _reg = regions[reg_indx]
                    prc_args.append(str(_reg["id"])+','+str(_reg["latUpper"])+','+str(_reg["latLower"])+
                                    ','+str(_reg["lonUpper"])+','+str(_reg["lonLower"])+','+str(grid_res)
                                    )
            except:
                print('Error in processing regions within the "autoGrid" option') 
                raise

            try:
                result = subprocess.run(prc_args, check= True)
            except:
                print('Error executing "genCovGrid" OC script')
                raise
        
        elif "customGrid" in grid:
            try:
                cov_grid_fl = user_dir + grid["customGrid"]["covGridFn"] # coverage grid file path  
            except:
                print('Error in processing "customGrid" option. Make sure "covGridFn" is specified.')
                raise

        else:
            raise RuntimeError('Error in processing grid. Unknown option, only "autoGrid" \
                                and "customGrid" options are supported.')

        return cov_grid_fl

    @staticmethod
    def compute_time_step(orbits, instru, time_res_fac):
        """ Compute time step to be used for orbit propagation based on 
            the satelllite orbit and sensor specs.
        """
        RE = Constants.radiusOfEarthInKM
        GMe = Constants.GMe
        fov_at = instru.fov_at

        # find the minimum sma of all the orbits
        min_sma = orbits[0].sma
        for indx in range(1,len(orbits)):
            if(orbits[indx].sma < min_sma):
                min_sma = orbits[indx].sma 
        min_alt = min_sma - RE # minimum latitude in km

        f = RE/(RE+min_alt)
        satVel = np.sqrt(GMe/(RE+min_alt))
        satGVel = f * satVel
        sinRho = RE/(RE+min_alt)
        hfov_deg = fov_at/2
        elev_deg = np.rad2deg(np.arccos(np.sin(np.deg2rad(hfov_deg))/sinRho))
        lambda_deg = 90 - hfov_deg - elev_deg # half-earth centric angle 
        eca_deg = lambda_deg*2 # total earth centric angle

        AT_FP_len = RE * np.deg2rad(eca_deg)

        t_AT_FP = AT_FP_len / satGVel # find time taken by satellite to go over the along-track length
        tstep = time_res_fac * t_AT_FP

        return tstep

    @staticmethod
    def compute_grid_res(orbits, instru, grid_res_fac):
        """ Compute grid resolution to be used for coverage grid generation.
            See SMAD 3rd ed Pg 113. Fig 8-13.
        """
        RE = Constants.radiusOfEarthInKM
        # find the minimum sma of all the orbits
        min_sma = orbits[0].sma
        for indx in range(1,len(orbits)):
            if(orbits[indx].sma < min_sma):
                min_sma = orbits[indx].sma 
        
        min_alt = min_sma - RE # minimum latitude in km
        fov_ct = instru.fov_ct # instrument cross-tracj fov in degrees

        sinRho = RE/(RE+min_alt)
        hfov_deg = 0.5*fov_ct
        elev_deg = np.rad2deg(np.arccos(np.sin(np.deg2rad(hfov_deg))/sinRho))
        lambda_deg = 90 - hfov_deg - elev_deg # half-earth centric angle 
        eca_deg = lambda_deg*2 # total earth centric angle
        grid_res_deg = eca_deg*grid_res_fac # factor 0.9 can be debated

        return grid_res_deg



