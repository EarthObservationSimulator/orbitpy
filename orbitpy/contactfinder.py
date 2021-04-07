""" 
.. module:: contactfinder

:synopsis: *Module to handle line-of-sight contact opportunity finder between two entities (satellite to ground-station
            or satellite to satellite). Note that ground-station to ground-station line-of-sight contact is not supported.* 

"""

import numpy as np
import copy
import pandas as pd
import csv
from collections import namedtuple

from instrupy.util import Entity, Constants, MathUtilityFunctions, GeoUtilityFunctions
import orbitpy.util
from orbitpy.util import Spacecraft, GroundStation

ContactPairs = namedtuple("ContactPairs", ["entityA", "entityA_state_cart_fl", "entityB", "entityB_state_cart_fl"])

class ContactFinder(Entity):

    @staticmethod
    def find_all_pairs(entity, entity_state_cart_fl):
        """ Find all possible pairs of entities between which contacts can be computed.

        :param entity: List of entities of type ``Spacecraft`` or ``GroundStation``.
        :paramtype entity: list, :class:`orbitpy.util.Spacecraft` or :class:`orbitpy.util.GroundStation`

        :param entity_state_cart_fl: List of orbital state files corresponding to the Spacecraft in the input ``entity`` list. If the ``entity`` is
                                     a GroundStation, then the corresponding list entry is ``None``.
        :paramtype entity_state_cart_fl: list, str or None

        :return: List of pairs of entities and the correpsonding state files as a namedtuple in the following
                 format: ("entityA", "entityA_state_cart_fl", "entityB", "entityB_state_cart_fl")
        :rtype: list, namedtuple, (:class:`orbitpy.util.Spacecraft` or :class:`orbitpy.util.GroundStation`, str or None, :class:`orbitpy.util.Spacecraft` or :class:`orbitpy.util.GroundStation`, str or None)

        """
        res = []
        for j in range(0, len(entity)):
            for k in range(j+1, len(entity)):
                if isinstance(entity[j], GroundStation) and isinstance(entity[k], GroundStation):
                    continue
                
                res.append(ContactPairs(entity[j], entity_state_cart_fl[j], entity[k], entity_state_cart_fl[k]))
        
        return res
    
    @staticmethod
    def execute(entityA, entityB, out_dir, entityA_state_cart_fl=None, entityB_state_cart_fl=None, out_filename=None, out_type='INTERVAL', opaque_atmos_height=0):
        """ Find line-of-sight contact times between two entities (satellite to ground-station or satellite to satellite).

        The results are available in two different formats *INTERVAL* or *DETAIL* (either of which can be specified in the input argument ``out_type``).

        1. *INTERVAL*: The first line of the file indicates the entity identifiers. The second line contains the epoch in Julian Date UT1. The 
            third line contains the step-size in seconds. The later lines contain the interval data in csv format with the following column headers:

            .. csv-table:: Contact file INTERVAL data format
                    :header: Column, Data type, Units, Description
                    :widths: 10,10,10,30

                start index, int, , Contact start time-index.
                stop index, int, , Contact stop time-index.

        2. *DETAIL*: The first line of the file indicates the entity identifiers. The second line contains the epoch in Julian Date UT1. The 
            third line contains the step-size in seconds. The later lines contain the interval data in csv format with the following column headers:
            The 'elevation [deg]' column appears only for the case of satellite-to-ground-station contact finder results.

            .. csv-table:: Contact file INTERVAL data format
                    :header: Column, Data type, Units, Description
                    :widths: 10,10,10,30

                time index, int, , Contact time-index.
                access, bool, , 'T' indicating True or F indicating False.
                range [km], float, kilometer, Distance between the two entities at the corresponding time.
                elevation [deg], float, degrees, Angle between the ground-plane and the ground-station to satellite line.

        :param entityA: Satellite or Ground-station ``orbitpy.util`` objects.
        :paramtype entityA: :class:`orbitpy.util.Spacecraft` or :class:`orbitpy.util.GroundStation`

        :param entityB: Satellite or Ground-station ``orbitpy.util`` objects.
        :paramtype entityB: :class:`orbitpy.util.Spacecraft` or :class:`orbitpy.util.GroundStation`

        :param out_dir: Path to directory where the file with results is to be stored.
        :paramtype out_dir: str

        :param entityA_state_cart_fl: Relevant when the ``entityA`` input argument is a satellite. File name with path of the (input) file 
                                      in which the orbit states (of entityA) in CARTESIAN_EARTH_CENTERED_INERTIAL are available.
                                      Refer to :class:`orbitpy.propagator.J2AnalyticalPropagator.execute` for description of the file data format.
        :paramtype entityA_state_cart_fl: str or None

        :param entityB_state_cart_fl: Relevant when the ``entityA`` input argument is a satellite. File name with path of the (input) file 
                                      in which the orbit states (of entityB) in CARTESIAN_EARTH_CENTERED_INERTIAL are available.
                                      Refer to :class:`orbitpy.propagator.J2AnalyticalPropagator.execute` for description of the file data format.
                                      The time-series of the states must be in sync with the time-series states in the entityA state file.
        :paramtype entityB_state_cart_fl: str or None

        :param out_filename: Name of output file in when the results are written. If not specified, the output filename is derived from the entity names
                             in the following format: *entityAName*_to_*entityBName*_contact.csv
        :paramtype out_filename: str or None

        :param out_type: Indicates the type of output data to be saved. 'DETAIL' or 'INTERVAL' are accepted values, where 'INTERVAL' indicates that
                         the contact time-intervals are stored, while 'DETAIL' stores the range and elevation-angle information at each time-step of mission.  
                         Default is 'INTERVAL'
        :paramtype out_type: str

        :param opaque_atmos_height: Relevant in-case both the input entities are spacecrafts. Height of atmosphere (in kilometers) below which line-of-sight 
                                    communication between two satellites cannot take place. Default value is 0 km.
        :paramtype opaque_atmos_height_km: float

        :return: None. The results are written out in a file.
        :rtype: None

        .. warning:: The time-series of the states in the entityA state file and entityB state file (in case of satellite-to-satellite contact finder)
                     must be in sync, i.e. the epoch, time-step and duration must be the same.

        """
        if isinstance(entityA, GroundStation) and isinstance(entityB, GroundStation):
            raise NotImplementedError("Ground-station to Ground-station contact finder is not supported.")

        # Make entityA strictly Spacecraft for easier coding.
        if isinstance(entityA, GroundStation) and isinstance(entityB, Spacecraft):
            # swap entityA and entityB and the corresponding files
            entityB, entityA = entityA, entityB
            entityB_state_cart_fl, entityA_state_cart_fl = entityA_state_cart_fl, entityB_state_cart_fl

        entityA_df = pd.read_csv(entityA_state_cart_fl, skiprows=4)
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(entityA_state_cart_fl)

        time_indx = list(entityA_df['time index'])
        numTimeSteps = len(time_indx)
        A_pos = entityA_df
        A_x_km = list(entityA_df['x [km]'])
        A_y_km = list(entityA_df['y [km]'])
        A_z_km = list(entityA_df['z [km]'])

        if isinstance(entityB, Spacecraft):
           entityB_df = pd.read_csv(entityA_state_cart_fl, skiprows=4)
           (_epoch_JDUT1, _step_size, _duration) = orbitpy.util.extract_auxillary_info_from_state_file(entityA_state_cart_fl)
           if(_epoch_JDUT1 != epoch_JDUT1 or _step_size != step_size or _duration != duration):
               raise RuntimeError("The time-series data of entityA and entityB are not synced.")

           B_x_km = list(entityB_df['x [km]'])
           B_y_km = list(entityB_df['y [km]'])
           B_z_km = list(entityB_df['z [km]'])
        
        elif isinstance(entityB, GroundStation):
            # Find the CARTESIAN_EARTH_CENTERED_INERTIAL position coordinates of the ground-station over all the time-steps.
            ground_stn_coords = entityB.get_coords()
            opaque_atmos_height = 0 # ensure opaque atmosphere height is 0 for the case of ground-station contacts.
            B_x_km = [None] * numTimeSteps
            B_y_km = [None] * numTimeSteps
            B_z_km = [None] * numTimeSteps
            for idx, value in enumerate(time_indx):
                time_JDUT1 = epoch_JDUT1 + value*step_size*(1.0/86400.0) 
                coords_eci =GeoUtilityFunctions.geo2eci(ground_stn_coords, time_JDUT1)
                B_x_km[idx] = coords_eci[0]
                B_y_km[idx] = coords_eci[1]
                B_z_km[idx] = coords_eci[2]
        else:
            raise RuntimeError('Unknown type of EntityB.')       
        
        # construct output filepath
        if out_filename:
            out_filepath = out_dir + '/' + out_filename
        else:
            if entityA.name is not None:
                A_name = entityA.name
            else:
                A_name = entityA._id

            if entityB.name is not None:
                B_name = entityB.name
            else:
                B_name = entityB._id
            
            out_filepath = out_dir + "/" + A_name + "_to_" + B_name + ".csv" 

        # create and initialize output file
        with open(out_filepath, 'w') as out:
            out.write('Contacts between Entity1 with id {} with Entity2 with id {}\n'.format(entityA._id, entityB._id))
            out.write('Epoch [JDUT1] is {}\n'.format(epoch_JDUT1))
            out.write('Step size [s] is {}\n'.format(step_size))

        # Loop over entire mission duration        
        access_log = [None] * numTimeSteps
        range_log = [None] * numTimeSteps
        elv_log = [None] * numTimeSteps
        for idx, value in enumerate(time_indx):

            A_pos = np.array([A_x_km[idx], A_y_km[idx], A_z_km[idx]]).astype(float)
            B_pos = np.array([B_x_km[idx], B_y_km[idx], B_z_km[idx]]).astype(float)
            
            los = GeoUtilityFunctions.checkLOSavailability(A_pos, B_pos, Constants.radiusOfEarthInKM + opaque_atmos_height)
            
            if isinstance(entityB, GroundStation): # additional checks that the elevation angle should be OK
                # calculate elevation angle, i.e. angle between ground-plane and ground-station to satellite line.
                elv_angle = None                    
                # Satellite is in line-of-sight of the ground station
                if(los):
                    AB_km = B_pos - A_pos
                    ground_stn_to_sat = -1 * AB_km
                    unit_ground_stn_to_sat = MathUtilityFunctions.normalize(ground_stn_to_sat)
                    unit_ground_stn = MathUtilityFunctions.normalize(B_pos)
                    elv_angle = np.pi/2 - np.arccos(np.dot(unit_ground_stn, unit_ground_stn_to_sat))            
                    # Check if the satellite fulfills the elevation condition                     
                    if(elv_angle > np.deg2rad(entityB.minimumElevation)):
                        access_log[idx] = True
                    else:
                        access_log[idx] = False
                else:
                    access_log[idx] = False
            else: # satellite-to-satellite communication,
                access_log[idx] = los

            if out_type == 'DETAIL':
                AB_km = B_pos - A_pos # TODO repeated calc sometimes, make it more efficient.
                r_AB_km = np.sqrt(np.dot(AB_km, AB_km))
                range_log[idx] = r_AB_km

                if isinstance(entityB, GroundStation):                    
                    elv_log[idx] = np.rad2deg(elv_angle) if elv_angle else None

        if out_type == 'DETAIL':
            # Write DETAIL output file
            if isinstance(entityB, GroundStation): 
                data = pd.DataFrame(list(zip(time_indx, access_log, range_log, elv_log)), columns=['time index', 'access', 'range [km]', 'elevation [deg]'])
                data.to_csv(out_filepath, mode='a', index=False)
                
            else:                
                data = pd.DataFrame(list(zip(time_indx, access_log, range_log)), columns=['time index', 'access', 'range [km]'])
                data.to_csv(out_filepath, mode='a', index=False)
        
        elif out_type == 'INTERVAL':    
            # Post process to create intervals
            interval_boundary = [] # TODO: Having variable-sized list could slow down computation in case of large number of intervals
            flag = access_log[0]
            for indx in range(1,numTimeSteps):
                if flag!=access_log[indx]:
                    interval_boundary.append(time_indx[indx])
                    flag = access_log[indx]

            if access_log[0] is True: # Means the mission starts off with the satellite seeing each other
                if(len(interval_boundary) == 0):
                    interval_boundary.append(time_indx[numTimeSteps-1]) # There is LOS for complete mission duration
                interval_boundary = [0] + interval_boundary  # append start of LOS, which is start of mission
                
            # interval_boundary should be even, else add the end of mission time to the interval boundary
            if(len(interval_boundary)%2 != 0):
                interval_boundary.append(time_indx[numTimeSteps-1])

            # write results           
            with open(out_filepath, 'a', newline='') as csvfile:
                fwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                fwriter.writerow(['start index', 'end index'])
                indx = 0
                while indx < len(interval_boundary):
                    fwriter.writerow([interval_boundary[indx], interval_boundary[indx+1]])
                    indx = indx + 2    

        else:
            raise RuntimeError("Unknown specification of the contact finder output data format.")    
             
