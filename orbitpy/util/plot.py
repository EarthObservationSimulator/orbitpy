import numpy as np
import matplotlib.pyplot as plt
import argparse

def orbitpyStateArray(sat_state_fl):
    
    data = np.genfromtxt(sat_state_fl, delimiter=",",skip_header=5)
    return data

def gmatStateArray(sat_state_fl):
        
    data = np.genfromtxt(sat_state_fl, skip_header = 1)
    return data    

def setPlotStyle(program='OrbitPy'):
    
    if program == 'OrbitPy':
        plt.title('ECI Data (OrbitPy)')
    elif program == 'GMAT':
        plt.title('ECI Data (GMAT)')
        
def setPlotStyleKepler(program='OrbitPy'):
    
    if program == 'OrbitPy':
        plt.title('Keplerian Data (OrbitPy)')
    elif program == 'GMAT':
        plt.title('Keplerian Data (GMAT)')
        
def plotSMA(data,program='OrbitPy'):
    t = data[:,0]
    SMA = data[:,1]
    
    plt.figure()
    lines = plt.plot(t,SMA)
    
    setPlotStyleKepler(program)
    plt.setp(lines,color = 'r')
    plt.xlabel('time (s)')
    plt.ylabel('SMA (km)')
    
def plotECC(data,program='OrbitPy'):
    t = data[:,0]
    ECC = data[:,2]
    
    plt.figure()
    lines = plt.plot(t,ECC)
    
    setPlotStyleKepler(program)
    plt.setp(lines,color = 'b')
    plt.xlabel('time (s)')
    plt.ylabel('ECC')
    
def plotINC(data,program='OrbitPy'):
    t = data[:,0]
    INC = data[:,3]
    
    plt.figure()
    lines = plt.plot(t,INC)
    
    setPlotStyleKepler(program)
    plt.setp(lines,color = 'g')
    plt.xlabel('time (s)')
    plt.ylabel('INC (deg)')
    
def plotRAAN(data,program='OrbitPy'):
    t = data[:,0]
    RAAN = data[:,4]
    
    plt.figure()
    lines = plt.plot(t,RAAN)
    
    setPlotStyleKepler(program)
    plt.setp(lines,color = 'r')
    plt.xlabel('time (s)')
    plt.ylabel('RAAN (deg)')
    
def plotAOP(data,program='OrbitPy'):
    t = data[:,0]
    AOP = data[:,5]
    
    plt.figure()
    lines = plt.plot(t,AOP)
    
    setPlotStyleKepler(program)
    plt.setp(lines,color = 'b')
    plt.xlabel('time (s)')
    plt.ylabel('AOP (deg)')
    
def plotTA(data,program='OrbitPy'):
    t = data[:,0]
    SMA = data[:,6]
    
    plt.figure()
    lines = plt.plot(t,SMA)
    
    setPlotStyleKepler(program)
    plt.setp(lines,color = 'g')
    plt.xlabel('time (s)')
    plt.ylabel('TA (deg)')

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
    
def plotDsma(data,program='OrbitPy'):
    t = data[:,0]
    sma = data[:,1]
    
    plt.figure()
    lines = plt.plot(t,sma)
    
    plt.title("SMA Difference Between States")
    plt.setp(lines,color = 'r')
    plt.xlabel('time(s)')
    plt.ylabel('SMA Diff (km)')

def plotDecc(data,program='OrbitPy'):
    t = data[:,0]
    ecc = data[:,2]
    
    plt.figure()
    lines = plt.plot(t,ecc)
    
    plt.title("ECC Difference Between States")
    plt.setp(lines,color = 'b')
    plt.xlabel('time (s)')
    plt.ylabel('ECC Diff')


def plotDinc(data,program='OrbitPy'):
    t = data[:,0]
    inc = data[:,3]
    
    plt.figure()
    lines = plt.plot(t,inc)
    
    plt.title("INC Difference Between States")
    plt.setp(lines,color = 'g')
    plt.xlabel('time (s)')
    plt.ylabel('INC Diff (deg)')
    
def plotDraan(data,program='OrbitPy'):
    t = data[:,0]
    raan = data[:,4]
    
    plt.figure()
    lines = plt.plot(t,raan)
    
    plt.title("RAAN Difference Between States")
    plt.setp(lines,color = 'r')
    plt.xlabel('time(s)')
    plt.ylabel('RAAN Diff (deg)')

def plotDaop(data,program='OrbitPy'):
    t = data[:,0]
    aop = data[:,5]
    
    plt.figure()
    lines = plt.plot(t,aop)
    
    plt.title("AOP Difference Between States")
    plt.setp(lines,color = 'b')
    plt.xlabel('time (s)')
    plt.ylabel('AOP Diff (deg)')


def plotDta(data,program='OrbitPy'):
    t = data[:,0]
    ta = data[:,6]
    
    plt.figure()
    lines = plt.plot(t,ta)
    
    plt.title("TA Difference Between States")
    plt.setp(lines,color = 'g')
    plt.xlabel('time (s)')
    plt.ylabel('TA Diff (deg)')
    
    
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

# keplerian input
parser.add_argument('-sma', action='store_true',help='Plot the SMA of the orbit/s as a function of time.')
parser.add_argument('-ecc', action='store_true',help='Plot the ECC of the orbit/s as a function of time.')
parser.add_argument('-inc', action='store_true',help='Plot the INC of the orbit/s as a function of time.')
parser.add_argument('-raan', action='store_true',help='Plot the RAAN of the orbit/s as a function of time.')
parser.add_argument('-aop', action='store_true',help='Plot the AOP of the orbit/s as a function of time.')
parser.add_argument('-ta', action='store_true',help='Plot the TA of the orbit/s as a function of time.')

parser.add_argument('-dsma',action='store_true',help='Plot the difference between the SMA of the two inputs as a function of time.')
parser.add_argument('-decc',action='store_true',help='Plot the difference between the ECC of the two inputs as a function of time.')
parser.add_argument('-dinc',action='store_true',help='Plot the difference between the INC of the two inputs as a function of time.')
parser.add_argument('-draan',action='store_true',help='Plot the difference between the RAAN of the two inputs as a function of time.')
parser.add_argument('-daop',action='store_true',help='Plot the difference between the AOP of the two inputs as a function of time.')
parser.add_argument('-dta',action='store_true',help='Plot the difference between the TA of the two inputs as a function of time.')

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
        
    # keplerian       
    if args.sma == True:
        plotSMA(data[i],program[i])
        
    if args.ecc == True:
        plotECC(data[i],program[i])
        
    if args.inc == True:
        plotINC(data[i],program[i])
        
    if args.raan == True:
        plotRAAN(data[i],program[i])
        
    if args.aop == True:
        plotAOP(data[i],program[i])
        
    if args.ta == True:
        plotTA(data[i],program[i])

if len(args.path) > 1:
    
    data[0],data[1] = equalizeData(data[0],data[1])
    diffData = data[0]
    diffData[:,1:6] = data[0][:,1:6] - data[1][:,1:6]
    
    # Plot differences as requested
    if args.dx == True:
        plotDx(diffData)
    if args.dy == True:
        plotDy(diffData)
    if args.dz == True:
        plotDz(diffData)
        
    # keplerian
    if args.dsma == True:
        plotDsma(diffData)
        
    if args.decc == True:
        plotDecc(diffData)
        
    if args.dinc == True:
        plotDinc(diffData)
        
    if args.draan == True:
        plotDraan(diffData)
        
    if args.daop == True:
        plotDaop(diffData)
        
    if args.dta == True:
        plotDta(diffData)
    
plt.show()