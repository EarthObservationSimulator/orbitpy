Miscellaneous
**************

.. _prop_time_step_determination:

Propagation time-step determination
======================================
The propagation time step is selected based on the time taken to cover the length (along-track) of the sensor footprint from it's field-of-**regard** (calculated 
at the nadir) and a time-resolution factor (:code:`time_res_fac`) which be default is set to 0.25. Smaller :code:`time_res_fac` implies higher precision
in calculation of the access interval over a grid-point. In case of conical sensors there is always a chance that a grid-point
is missed during the access calculations.

.. figure:: time_step_illus.png
    :scale: 75 %
    :align: center

    Illustration of possible inaccuracies due to a large time resolution factor (0.75 in above figure).

.. _grid_res_determination:

Grid Resolution determination
================================
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

.. note:: While the time-step is calculated from the FOV, the  grid-resolution is calculated from the FOR.

.. _corr_acc_files:

"Correction" of access files for purely side-looking instruments
==================================================================

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
   
   *Access listed below corresponds to approximate access instants at the grid-points at a (approximately) side-look target geometery. The scene scan time should be used along with the below data to get complete access information.*


.. warning:: There is a small hiccup when the propagation time step is smaller than the sensor (eg: SAR) dwell time and access is corrected as described above. 
            Since the propagation time step is small, the access over the grid point takes place over number of time-steps, while the corrected access
            files show access as taking place at only one time-step. The correction method is to be used when the dwell time is much smaller than the 
            propagation time step. The dwell time needed for the calculation of the data-metrics is calculated analytically by the :code:`instrupy` module.
            It should be OK as long as we are aware.

