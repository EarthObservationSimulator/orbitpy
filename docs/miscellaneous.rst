Miscellaneous
**************

.. _grid_pnts_cov_calc_app:

Grid-points coverage calculations approach
==========================================
This section describes the "Grid-point" approach towards coverage calculations. In this approach, the coverage calculator is given a 
set of predefined grid-points (lat, lon values). The satellite is propagated and at each time, and it is determined if a grid-point falls
within the sensor projected footprint on the Earth's surface at that time. A continuous collection of such times corresponds to 
an access interval: i.e. the time-interval over which the ground-point is visible to the satellite sensor.
The key aspects relating to this approach are described below:

.. _prop_time_step_determination:

Propagation time-step determination
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The propagation time step is selected based on the time taken to cover the length (along-track) of the sensor footprint from it's field-of-**regard** (calculated 
at the nadir) and a time-resolution factor (:code:`time_res_fac`) which be default is set to 0.25. Smaller :code:`time_res_fac` implies higher precision
in calculation of the access interval over a grid-point. In case of conical sensors there is always a chance that a grid-point
is missed during the access calculations.

.. figure:: time_step_illus.png
    :scale: 75 %
    :align: center

    Illustration of possible inaccuracies due to a large time resolution factor (0.75 in above figure).

The user may change the default :code:`time_res_fac` by setting the :code:`customTimeResFac` JSON key within the :code:`settings` JSON
object in the user-defined JSON configuration file.

.. _grid_res_determination:

Grid Resolution determination
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The grid resolution is set such that at any given arbitrary time, the sensor footprint from its field-of-**view** captures atleast one grid-point
when the satellite is within the interior of a region. This can be acheived by setting the grid resolution (spacing between
the grid points) to be less than the minimum footprint dimension. A grid resolution factor :code:`grid_res_fac` is defined 
(with default value 0.9) and the grid resolution is computed as (:code:`grid_res_fac` . minimum footprint angular dimension).
For example, in case of rectangular sensor with FOV: 5 deg x 15 deg at an altitude of 500km, the minimum footprint angular dimension 
is the Earth centric angle subtended by the 5 deg side = 0.3922 deg. This gives the grid resolution as 0.3530 deg.

.. figure:: grid_res_illus.png
    :scale: 75 %
    :align: center

    Illustration of relationship between grid resolution and sensor footprint.

.. note:: While the time-step is calculated from the FOR, the  grid-resolution is calculated from the FOV.

The user may change the default :code:`grid_res_fac` by setting the :code:`customGridResFac` JSON key within the :code:`settings` JSON
object in the user-defined JSON configuration file.

.. _corr_acc_files:

"Correction" of access files for purely side-looking instruments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In case of purely side-looking instruments (eg: SARs executing Stripmap operation mode), the access to a grid-point takes place when the grid-point
is seen with no squint angle. The orbit propagation and coverage calculations takes place for a corresponding *FOV/sceneFOV* for the instrument 
(see :code:`instrupy` package documentation). 
The generated access files are then *corrected* to a new format, to show access only at approximately the middle of the access interval. This should be 
coupled with the scene-scan time to get complete information about the access. 

For example, consider a SAR instrument pointing sideways as shown in the figure below. The along-track FOV is narrow
corresponding to narrow strips, and a scene is built from concatenated strips. A SceneFOV is associated with the SAR and is used for access 
calculation over the grid point shown in the figure. Say the propagation time-step is 1s as shown in the figure. An acccess interval between
t=100s to t=105s is registered. However as shown the actual access takes place over a small interval of time at t=103.177s. 

An approximation can be applied (i.e. correction is made) that the observaton time of the ground point is at the middle of the access
interval rounded of to the nearest propgation time as calculated using the SceneFOV, i.e. :math:`t= 100 + ((105-100)/2) % 1 = 103s`. The state 
of the spacecraft at :math:`t=103s` is utilized for the data-metrics calculation.


.. figure:: sar_access.png
    :scale: 75 %
    :align: center

The correction of the access files is handled by the :class:`orbitpy.orbitpropcov` module which requires as inputs: list of access files (to be revised). The original access files are renamed to :code:`...._old` and the corrected access files are
produced with the same name as the original access files at the same location. An additional message is displayed within the file as follows:
   
   *Access listed below corresponds to approximate access instants at the grid-points at a side-look target geometery. The scene scan time should be used along with the below data to get complete access information.*


.. warning:: There is a small hiccup when the propagation time step is smaller than the sensor (eg: SAR) dwell time and access is corrected as described above. 
            Since the propagation time step is small, the access over the grid point takes place over number of time-steps, while the corrected access
            files show access as taking place at only one time-step. The correction method is to be used when the dwell time is much smaller than the 
            propagation time step. The dwell time needed for the calculation of the data-metrics is calculated analytically by the :code:`instrupy` module.
            It should be OK as long as we are aware.

Issue #1
.........

Current implementation works well only for:
   1. Instruments whose required observation time < propagation step-size (i.e. < 1s).  For scanning type instruments 
      (like pushbroom sensors, stripmap SARs) this condition can be waived. But cannot be waived for instruments like Matrix imagers, radiometers 
      which require the entire sensor FOV to be focused on the scene. 
   2. Whose FOV << FOR.

*First one is not realistic if the minimum exposure/ dwell time of instruments 
(required in radiometers) is to be considered. Second one is not realistic assumption for 
instruments having a wide-swath.*

The access file generated by the orbit and coverage is quite naive. It indicates if the ground-point can be accessed at some instant of time.
However, what we require are the imaging opportunities, where a imaging opportunity is defined as:

*Outlier grid-points:* The area around the grid-point should be able to be observed, not just the point. Not realistic for instruments with large FOV.

.. figure:: outlier_grid_points.png
    :scale: 75 %
    :align: center

    Issue of the outlier grid-points

.. _pnt_opts_cov_calc_app:

Pointing Options coverage calculations approach
===============================================
In this coverage calculation approach, a set of pointing options is supplied in a data-file by the user. The pointing-options
are defined with respect to the Nadir-frame (see :code:`instrupy`, :code:`orientation` JSON object description). The complete set of pointing-options
represent a discretized field-of-maneuverability. Hence the :code:`maneuver` JSON object need not be specified within the  
:code:`instrument` JSON object.

The generated access file contains the locations corresponding to each pointing-option and each time accessed by the sensor. This location
is the intersection of the pointing-axis with a spherical Earth model to give geocentric latitudes and longitudes. 

The propagation time-step determination is identical to the description above in :ref:`prop_time_step_determination`. However, instead of 
field-of-regard, the field-of-**view** would be used, since the maneuver field is not included. Also, the user may set a higher
:code:`customTimeResFactor`(from the default 0.25) in the :code:`settings` JSON object.  

Pointing Options with Grid coverage calculations approach
==========================================================
The sensor is oriented to each of the pointing-options specified by the user and the coverage is calculated for taking into account the 
FOV of the sensor. 
Sensor orientation and Maneuver options if specified, are ignored since the pointing options are defined with respect to the Nadir frame.

Common issues:
==============

Issue
^^^^^^

* The area around the ground-point is not the same at each observation, especially for rectangular FOV sensors.

.. figure:: different_observation_areas.png
    :scale: 75 %
    :align: center

    Issue of the different observation areas when observation is made with footprint aligned to the ground-track.




