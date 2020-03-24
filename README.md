<h2>Updated the orbits for new GMAT OC module and Reduction & Metrics module.</h2>
<br/>

Boost was updated from 1.63.0 to 1.72.0 Makefiles need to be changed.

<b>Building the oc and rm:</b>


1.  Go to the top level directory 'orbits'
2.  Building all by typing '`make all`'
3.  Check no compiler errors.
4.  Run testing for verification by type '`make runtest`'
5.  Clean up those objects by typing '`make clean`'

<br/>
<b>Instruction of using Makefile for its target:</b><br/>

    make all     - Compile the entire program including install
    make install - Copy the library file(s) and executable to the lib and bin directories
    make clean   - Remove object files *.o and locally *.a (static library files)
    make bare    - Remove all executable file(s) and static library files
    make runtest - Run testing


<b>Calling the Orbit Module</b>
The orbit module takes two command line arguments:

    1.  A path to <mission_name>.json (including mission file extension)  Ex:  /...../test-mission/mission.json

    2.  A path to <architecture>.json (directory only)                    Ex:  /...../test-mission/arch-0
    

The binary file can be found in: /...../tat-c/orbits/rm/bin/reductionMetrics

When calling the Orbit Module, the "tat-c" directory must either be a parent directory or the current working directoy.

Example:  
```
- orbits
    - rm
        - bin
            - landsat8.json
            - reductionMetrics
            - arch
                - arch.json
            
bin>> ./reductionMetrics ./landsat8.json ./arch
```

<br/><br/>
<hr>
<h3>NOTE:</h3> 
Runnning the unit testing in the orbits/oc/test directory with  
<code>make runtest</code> that the file <code>SystemTest_Analysis.cpp</code> has the default value (<b>numIter=50</b>) in order to make it short for running.


If you want to run longer, go to the ./orbits/oc/test directory and  then you can edit the file <code>SystemTest_Analysis.cpp</code> to set the value of the variable <code>numIter</code> at line 71 or nearby.

```
   Integer numIter = 50; // 10000;
```

Then do <code>make bare all</code> for building the test located in that 'test' directory and <code>make runtest</code> for the verification.

<hr>

<h3>Optional Tags</h3>


<h5>Caching System</h5>

The orbig module's cache system is controlled by a boolean "useCache" key under the "settings" key in the mission.json file. 
```
   "useCache": true,
```
```
   "useCache": false,
```

A cache directory is created at the beginning of every run if no cache directory exists (even if use cache is set to false). <br>
Additionally, the "useCache" key:value pair defaults to true when not present in the mission file.


<h5>Multi-threading</h5>

Multi-threading in the orbit module is controlled by a boolean "useThreading" key under the "settings" key in the mission.json file.
```
   "useThreading": true,
```
```
   "useThreading": false,
```

The orbit module will create a thread for each satellite in an architecture "including a thread for each satellite in an existing constellation".

<h5>Limiting POIs for performance</h5>

You can limit the number of POIs the orbit module produces by editing an integer "maxGridSize" key:value pair under the "settings" key in the mission.json file. 
```
   "maxGridSize": 250,
```
The value part of this pair represents the max amount of POIs you want the orbit module to produce. If this key:value pair is missing, the max number of points will default to 10,000

<hr>

<h1>Outputs</h1>


<h4>Output Files - used by other modules </h4>
The "X" in the file names will be replaced by the satellite's ID in an architecture
* poi.csv
* satX_accessInfo.csv 
* gbl.json
* lcl.csv

*Description of file contents*

1.  `poi.csv`

    Comma delimited file.

    | Column name | Unit    | Data type | Description                |
    |-------------|---------|-----------|----------------------------|
    | `POI`       |         | integer   | Index of Point of Interest |
    | `lat[deg]`  | degrees (-90,90) | float     | Latitude of ground-point   |
    | `lon[deg]`  | degrees (-180,180) | float     | Longitude of ground-point  |   

2. `satX_accessInfo.csv` (used by instrument module)

    First four rows convey general information:
    
    For example:
    ```
    Satellite states are in Earth-Centered-Inertial equatorial plane.,,,,,,,,,,
    Epoch[JDUT1] is 2458562.344745371,,,,,,,,,,
    All time is referenced to the Epoch.
    Mission Duration [Days] is 1
    ```
    
    First and third rows are same always as above.  Second row tells the epoch (in Julian Day UT1) to which the time-series in the file is referenced. Fourth row tells in entire Mission Duration (for which the access is calculated) in # Days.

    The rest of the file contains comma delimited data.

    | Column name        | Unit                 | Data type | Description                                                                             |
    |--------------------|----------------------|-----------|-----------------------------------------------------------------------------------------|
    | `EventNum`         |                      | integer   | Event ID (unique for access events of the particular satellite)                         |
    | `POI`              |                      | integer   | Index of the accessed ground-point.                                                     |
    | `AccessFrom[Days]` | Solar Days           | float     | Start of access. Referenced to epoch.                                                   |
    | `Duration[s]`      | seconds              | float     | Duration of access.                                                                     |
    | `Time[Days]`       | Solar Days           | float     | Time at which Satellite state is recorded. Shall be close to middle of access interval. |
    | `X[km]`            | kilometer            | float     | Satellite position x-coordinate in ECI equatorial frame.                                |
    | `Y[km]`            | kilometer            | float     | Satellite position y-coordinate in ECI equatorial frame.                                |
    | `Z[km]`            | kilometer            | float     | Satellite position z-coordinate in ECI equatorial frame.                                |
    | `VX[km/s]`         | kilometer-per-second | float     | Satellite velocity x-coordinate in ECI equatorial frame.                                |
    | `VY[km/s]`         | kilometer-per-second | float     | Satellite velocity y-coordinate in ECI equatorial frame.                                |
    | `VZ[km/s]`         | kilometer-per-second | float     | Satellite velocity z-coordinate in ECI equatorial frame.                                |



3. `gbl.json`
    
    Contains global data evaluated from the architecture.

    ```
    "AccessTime" : {
      "avg" : Double,
      "max" : Double,
      "min" : Double
   },
   "Coverage" : 91.505791505791507,
   "DataLatency" : {
      "avg" : Double,
      "max" : Double,
      "min" : Double
   },
   "DownlinkTimePerPass" : {
      "avg" : Double,
      "max" : Double,
      "min" : Double
   },
   "NumGSpassesPD" : Double,
   "NumOfPOIpasses" : {
      "avg" : Double,
      "max" : Double,
      "min" : Double
   },
   "ResponseTime" : {
      "avg" : Double,
      "max" : Double,
      "min" : Double
   },
   "RevisitTime" : {
      "avg" : Double,
      "max" : Double,
      "min" : Double
   },
   "Time" : {
      "max" : Double,
      "min" : Double
   },
   "TimeToCoverage" : {
      "avg" : Double,
      "max" : Double,
      "min" : Double
   },
   "TotalDownlinkTimePD" : Double
    ```

    






