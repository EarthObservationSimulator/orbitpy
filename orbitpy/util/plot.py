import numpy as np
import matplotlib.pyplot as plt
import argparse

def orbitpyStateArray(sat_state_fl):
    
    data = np.genfromtxt(sat_state_fl, delimiter=",",skip_header=5)
    return data

def gmatStateArray(sat_state_fl):
        
    data = np.genfromtxt(sat_state_fl, skip_header = 1)
    return data    

def setPlotStyle(program='Orbitpy'):
    
    if program == 'OrbitPy':
        plt.title('ECI Data (OrbitPy)')
    elif program == 'GMAT':
        plt.title('ECI Data (GMAT)')

def plotX(data,program='OrbitPy'):
    t = data[:,0]
    x = data[:,1]
    
    plt.figure()
    lines = plt.plot(t,x)
    
    setPlotStyle(program)
    plt.setp(lines,color = 'r')
    plt.xlabel('time (s)')
    plt.ylabel('X (km)')

def plotY(data,program='OrbitPy'):
    t = data[:,0]
    x = data[:,2]
    
    plt.figure()
    lines = plt.plot(t,x)
    
    plt.setp(lines,color = 'b')
    plt.xlabel('time (s)')
    plt.ylabel('Y (km)')

    if program == 'OrbitPy':
        plt.title('ECI Data (OrbitPy)')
    elif program == 'GMAT':
        plt.title('ECI Data (GMAT)')


def plotZ(data,program='OrbitPy'):
    t = data[:,0]
    x = data[:,3]
    
    plt.figure()
    lines = plt.plot(t,x)
    
    setPlotStyle(program)
    plt.setp(lines,color = 'g')
    plt.xlabel('time (s)')
    plt.ylabel('Z (km)')
    
    
def plotDx(data,program='OrbitPy'):
    t = data[:,0]
    x = data[:,1]
    
    plt.figure()
    lines = plt.plot(t,x)
    
    plt.title("X Difference Between States")
    plt.setp(lines,color = 'r')
    plt.xlabel('time(s)')
    plt.ylabel('X Diff (km)')

def plotDy(data,program='OrbitPy'):
    t = data[:,0]
    x = data[:,2]
    
    plt.figure()
    lines = plt.plot(t,x)
    
    plt.title("Y Difference Between States")
    plt.setp(lines,color = 'b')
    plt.xlabel('time (s)')
    plt.ylabel('Y Diff (km)')


def plotDz(data,program='OrbitPy'):
    t = data[:,0]
    x = data[:,3]
    
    plt.figure()
    lines = plt.plot(t,x)
    
    plt.title("Z Difference Between States")
    plt.setp(lines,color = 'g')
    plt.xlabel('time (s)')
    plt.ylabel('Z Diff (km)')
    
    
def detectHeader(sat_state_fl):
    
    file = open(sat_state_fl,'r')
    
    line = file.readline()
    lineCount = 0
    
    while any((c.isalpha() and c != 'e') for c in line):
        lineCount = lineCount + 1
        line = file.readline()
    
    file.close()
    return lineCount

def equalizeData(data1,data2):
    
    size1 = len(data1[:,0])
    size2 = len(data2[:,0])
    diff = size1 - size2
    
    if diff != 0:
        print("WARNING: numCols not equal! Removed " + str(diff) + "rows from input 1.")
        if size1 > size2:
            data1 = data1[0:-diff,:]
        else:
            data2 = data2[0:diff,:]
            
    return data1,data2
            
        

# Begin command line parser execution
msg = "A simple command line utility to plot orbit state data associated with GMAT and orbitPy. \
The orbit states of a single file can be plotted, or the states of two files compared. The file \
source will be determined automatically based on the size of the header."

parser = argparse.ArgumentParser(description=msg)

parser.add_argument('path', metavar='F', nargs='+',type=str, help = 'Relative path to a text file containing orbit state data. A max of two files can be specified.')
parser.add_argument('-x', action='store_true',help='Plot the x position of the orbit/s as a function of time.')
parser.add_argument('-y', action='store_true',help='Plot the y position of the orbit/s as a function of time.')
parser.add_argument('-z', action='store_true',help='Plot the z position of the orbit/s as a function of time.')
parser.add_argument('-dx',action='store_true',help='Plot the difference between the x positions of the two inputs as a function of time.')
parser.add_argument('-dy',action='store_true',help='Plot the difference between the y positions of the two inputs as a function of time.')
parser.add_argument('-dz',action='store_true',help='Plot the difference between the z positions of the two inputs as a function of time.')

args = parser.parse_args()

## Begin program execution

# define header sizes
GMAT_SIZE = 1
ORBITPY_SIZE = 5

numHeaderLines = []
data = []
program = []

# Loop through all (max 2) input files to generate numpy arrays
for i in range(len(args.path)):
    ## Generate and identify numpy arrays
    numHeaderLines.append(detectHeader(args.path[i]))

    # if OrbitPy
    if numHeaderLines[i] == ORBITPY_SIZE:
        print("INPUT: OrbitPy detected")
        data.append(orbitpyStateArray(args.path[i]))
        program.append('OrbitPy')
    # elif GMAT
    elif numHeaderLines[i] == GMAT_SIZE:
        print("INPUT: GMAT detected")
        data.append(gmatStateArray(args.path[i]))
        program.append('GMAT')
    else:
        msg = "INPUT: Header count of " + str(numHeaderLines[i]) + " doesn't match GMAT or OrbitPy."
        print(msg)
# Plot positions as requested
for i in range(len(args.path)):
    if args.x == True:
        plotX(data[i],program[i])
    
    if args.y == True:
        plotY(data[i],program[i])
        
    if args.z == True:
        plotZ(data[i],program[i])

if len(args.path) > 1:
    
    data[0],data[1] = equalizeData(data[0],data[1])
    diffData = data[0]
    diffData[:,1:5] = data[0][:,1:5] - data[1][:,1:5]
    
    # Plot differences as requested
    if args.dx == True:
        plotDx(diffData)
    if args.dy == True:
        plotDy(diffData)
    if args.dz == True:
        plotDz(diffData)
    
plt.show()