"""A class for viewing and processing STK and OrbitPy coverage output, and switching between the two formats.

TODO: Update to the latest version of the OrbitPy output.  (Probably this file is no longer needed, check)

"""
import numpy as np
from math import ceil,floor
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm

class Coverage:
    
    def __init__(self,coverage,region,lat,lon,r=6378.137,days = 1,accesses = None, program = 'OrbitPy'):
        
        self.coverage = coverage
        self.region = region
        self.lat = lat
        self.lon = lon
        self.r = r
        self.days = days
        self.program = program
        
        if accesses == None:
            self.computeAccesses()
        else:
            self.accesses = accesses
        self.sphericalToCartesian()
    
    @classmethod
    def OrbitPyCoverage_Deprecated(cls,accPath,gridPath,days = 1):
        """Factory method. Instantiates the class using OrbitPy grid access file and grid file. Deprecated access format."""
        coverage = np.genfromtxt(accPath, delimiter=",",skip_header = 5,filling_values = 0)
        grid = np.genfromtxt(gridPath, delimiter=",", skip_header = 1)
        
        # Number of grid points
        numPts = grid.shape[0];    
        
        numSecs = days * 86401 
        
        timeArray = np.linspace(0,numSecs-1,numSecs,dtype=int)
        
        with open(accPath) as f:
            lines = f.readlines()[5:]
            coverage = np.zeros([numSecs,numPts],dtype=int)
            
            for line in lines:
                row = np.fromstring(line,dtype = float,sep=',')
                accessTimeIndex = int(row[0])
                gpi = int(row[2])
                coverage[accessTimeIndex,gpi] = 1
                
            
        # Add time steps to first column of coverage array, to match orbitpy     
        coverage = np.insert(coverage,0,timeArray,axis=1)
        
        # Remove rows with no accesses
        coverage = coverage[~np.all(coverage[:,1:]==0,axis = 1)]
        

        region = grid[:,0]
        lat = grid[:,2]
        lon = grid[:,3]
        
        return cls(coverage,region,lat,lon,program = 'OrbitPy Coverage')
    
    @classmethod
    def OrbitPyCoverage(cls,accPath,gridPath,days = 1):
        """Factory method. Instantiates the class using OrbitPy grid access file and grid file."""
        coverage = np.genfromtxt(accPath, delimiter=",",skip_header = 5,filling_values = 0)
        grid = np.genfromtxt(gridPath, delimiter=",", skip_header = 1)
        
        # Number of grid points
        numPts = grid.shape[0];    
        
        numSecs = days * 86401 
        
        timeArray = np.linspace(0,numSecs-1,numSecs,dtype=int)
        
        with open(accPath) as f:
            lines = f.readlines()[5:]
            coverage = np.zeros([numSecs,numPts],dtype=int)
            
            for line in lines:
                row = np.fromstring(line,dtype = float,sep=',')
                accessTimeIndex = int(row[0])
                gpi = int(row[1])
                coverage[accessTimeIndex,gpi] = 1
                
            
        # Add time steps to first column of coverage array, to match orbitpy     
        coverage = np.insert(coverage,0,timeArray,axis=1)
        
        # Remove rows with no accesses
        coverage = coverage[~np.all(coverage[:,1:]==0,axis = 1)]
        

        region = grid[:,0]
        lat = grid[:,2]
        lon = grid[:,3]
        
        return cls(coverage,region,lat,lon,program = 'OrbitPy Coverage')
    
    @classmethod
    def STKCoverage(cls,path,days = 1):
        """Factory method. Instantiates the class using an STK .cvaa access file."""     
        with open(path,'r') as file:
            lines = file.readlines()
            
            # Still not as efficient as possible
            numPts = 0
            for line in lines:
                if "NumberOfRegions" in line:
                    numRegions = int(line.split()[1])
                if "NumPtsInRegion" in line:
                    numPts = numPts + int(line.split()[1])
                
            numSecs = days * 86400 
            timeArray = np.linspace(0,numSecs-1,numSecs,dtype=int)
            coverageArray = np.zeros([numSecs,numPts],dtype=int)
            accessesArray = np.zeros(numPts)
            latArray = np.zeros(numPts)
            lonArray = np.zeros(numPts)
            regionArray = np.zeros(numPts)
            
            accesses = 0
            recorded = 0
            for line in lines:
                if "RegionNumber" in line:          
                    region = float(line.split()[1])          
                if "RegionName" in line:            
                    region = 999                 
                if "PointNumber" in line:               
                    index = int(float((line.split()[1])))
                    regionArray[index] = region                    
                if "NumberOfAccesses" in line:
                    accesses = int(float((line.split()[1])))
                    recorded = 0
                    accessesArray[index] = accesses
                    continue          
                if "Lat" in line:
                    lat = float(line.split()[1])
                    lat = np.degrees(lat)
                    
                    # Match orbitpy angle definition, -90 to 90 
                    if lat > 90:
                        lat = lat - 180
                    elif lat <  -90:
                        lat = lat + 180
                    
                    latArray[index] = lat
                if "Lon" in line:
                    lon = float(line.split()[1])
                    lon = np.degrees(lon)
                    
                    # Match orbitpy angle definition, -180 to 180
                    if lon > 180:
                        lon = lon - 360
                    elif lon <  -180:
                        lon = lon + 360
                    
                    lonArray[index] = lon
                
                # Save accessed steps
                if accesses != recorded and accesses != 0:
                    cols = line.split()
                    start = ceil(float(cols[1]))
                    stop = floor(float(cols[2]))
                    coverageArray[start:stop,index] = 1
                    
                    recorded = recorded + 1    
        
        # Add time steps to first column of coverage array, to match orbitpy     
        coverageArray = np.insert(coverageArray,0,timeArray,axis=1)
        
        # Remove rows with no accesses
        coverageArray = coverageArray[~np.all(coverageArray[:,1:]==0,axis = 1)]
        
        return cls(coverageArray,regionArray,latArray,lonArray,program = 'STK Coverage')
    
    def sphericalToCartesian(self):
        """Generates the grid in cartesian coordinates for plotting."""
        
        lat = np.radians(self.lat)
        lon = np.radians(self.lon)
        
    
        self.x = self.r * np.cos(lon) * np.cos(lat)
        self.y = self.r * np.cos(lat) * np.sin(lon)
        self.z = self.r * np.sin(lat)
        
    def computeAccesses(self):
        """For each grid point, finds number of accesses, access intervals, and total time accessed."""
        
        accesses = np.zeros(len(self.lat))
        
        # Create list of access interval lists
        accessIntervals = []
        timeAccessed = np.zeros(len(self.lat))
        
        for i in range(len(self.lat)):
            accessIntervals.append([])
        
        flag = 0
        for j in range(0,self.coverage.shape[1]-1):
            for i in range(self.coverage.shape[0]):
                
                if self.coverage[i,j+1] == 1 and flag == 1:
                    timeAccessed[j] += 1
                    continue
                elif self.coverage[i,j+1] == 1 and flag == 0:
                    timeAccessed[j] += 1
                    accesses[j] += 1
                    flag = 1
                    startTime = self.coverage[i,0]
                elif self.coverage[i,j+1] == 0 and flag == 1:
                    flag = 0
                    stopTime = self.coverage[i-1,0]
                    accessIntervals[j].append((startTime,stopTime))
                    
        self.accesses = accesses
        self.accessIntervals = accessIntervals
        self.timeAccessed = timeAccessed
    
    def plotAccesses(self, hide_background = True):
        """Plot the access grid."""
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        
        vmax = max(self.accesses)
        if vmax == 0:
            vmax = 1
        
        norm = colors.Normalize(vmin=.01,vmax=vmax)
        palette = cm.get_cmap('cividis', int(vmax))
        palette.set_under("red")
                
        surface = ax.scatter(self.x,self.y,self.z,c = self.accesses,cmap = palette,norm = norm, s = 30)
        surface.set_clim(0,vmax)
        
        if hide_background:
            ax.set_axis_off()
        else:
            ax.set_xlabel("X Position (ECEF)", labelpad = 10)
            ax.set_ylabel("Y Position (ECEF)", labelpad = 10)
            ax.set_zlabel("Z Position (ECEF)", labelpad = 10)
        
        
        cbar = fig.colorbar(surface,ticks = np.arange(0,vmax+1),extend = 'min')
        cbar.ax.set_ylabel("Number of Accesses", labelpad = 20)
        
        fig.suptitle(self.program,fontsize = 22)
        
        # Set initial viewing angle
        ax.view_init(azim=-105,elev = 40)    
        fig.set_size_inches(8*1.2,5*1.2)
        
        plt.show()
 
    def writeOrbitPyGrid(self,path):
        """Write a grid file compatible with orbitpy."""
        gpi = np.linspace(0,len(self.region)-1,len(self.region),dtype = int)
        
        tup = (self.region,gpi,self.lat,self.lon)
        outputArray = np.column_stack(tup)
        
        header = "regi,gpi,lat[deg],lon[deg]"
        fmt = ['%d','%d','%.17f','%.17f']
        
        np.savetxt(path,outputArray,delimiter=',',fmt=fmt,header=header)
        
    def writeOrbitPyAccess(self,path):
        """Write out an access file in a format similar to orbitpy."""
        
        fmt = '%d'
        np.savetxt(path,self.coverage,delimiter = ',', fmt = fmt)
