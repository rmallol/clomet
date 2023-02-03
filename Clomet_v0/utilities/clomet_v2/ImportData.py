import os
import numpy as np
import struct

from pandas import Int32Dtype

from utilities.clomet_v2.ManageErrors import ManageErrors

class ImportData:

    def __init__(self, errorManager: ManageErrors):
        self.errormanager = errorManager

    """
    Calls de importData function.
    """
    def dataImportManager(self, id, procno):
        path = "media/" + id + "_custom"
        return self.importData(procno, path)

    """
    Imports data from the study to a matrix of values.
    """
    def importData(self, procno, basepath):

        dirs = os.listdir(basepath)
        A = {"errors": "None"}

        window_a = [1.340, 1.33]
        refPeak = 1.335
        refMethod = 'maxima'

        for dir in dirs:
            subpath = basepath + "/" + dir
            if ( os.path.isdir(subpath) ):
                finalpath = subpath + "/" + dir + "/" + str(procno["num"]) + "/pdata/1"
                if ( os.path.exists(finalpath) ):
                    B = self.rbnmr(finalpath)
                    if B["errors"] != "None":
                        return B
                    A[dir] = B
                    #A[dir] = self.clean(B)
                    #A[dir] = self.alignSpectra(A[dir], window_a, refPeak, refMethod)
                else:
                    print("It doesn't exist: " + finalpath)

        return A

    """
    Cleans the data importes.
    """
    def clean(self, A):

        interval = self.getRang(A, 4.5, 2)
        result = sum(interval)
        if np.sign(result) == -1:
            print("CHANGE OF SIGN")
            A['Data'] = -A['Data']

        A = self.reduceDecimals(A)

        A = self.reduceBorders(A, 0.5, 8.5)
        A = self.supressWater(A, 4.5, 5.0)

        return A

    """
    Obtains data from particular files.
    """
    def rbnmr(self, path):
        # TODO: check the data acquired is fine (split errors)

        A = {}
        A["errors"] = "None"

        if (os.path.exists(path + '/title')):
            A['title'] = self.readFile(path + '/title')
        else:
            self.errormanager.addError("ERROR: No title found")
            A['title'] = "No title found"
            #print("ERROR: " + path + '/title' + "does not exist" )

        if (os.path.exists(path + '/procs')):
            A['procs'] = self.readprocs(path, 'procs')

        elif (os.path.exists(path + '/proc')):
            A['procs'] = self.readprocs(path, 'proc')
        else:
            print("ERROR: " + path + '/procs' + "does not exist" )
            self.errormanager.addError("ERROR: No procs file found")
            A["errors"]= "Procs file not found in " + path
            return A

        start = A['procs']['OFFSET']
        stop = (A['procs']['OFFSET']-A['procs']['SW_p'])/A['procs']['SF']
        num = A['procs']['SI']
        A['XAxis'] = np.linspace(start=A['procs']['OFFSET'], stop=A['procs']['OFFSET']-A['procs']['SW_p']/A['procs']['SF'], num=A['procs']['SI'])

        #print(start)
        #print(stop)
        #print(num)
        #print("Xaxis size: " + str(len(A['XAxis'])))
        
        if A['procs']['BYTORDP'] == 0:
            endian = 'l'
        else:
            endian = 'b'

        if (os.path.exists(path + '/1r')):
            A['Data'] = self.read1r(path + '/1r', endian)
        else:
            self.errormanager.addError("ERROR: 1r does not exist")
            print("ERROR: " + path + '/1r' + " does not exist" )
            #addErrorReport("No 1r file found")
            A["errors"]= "1r file not found in " + path
            return A

        return A

    """
    Reduces spectra borders.
    """
    def reduceBorders(self, A, l, r):
    
        data = []
        axis = []

        for i in range(len(A['XAxis'])):
            if ( A['XAxis'][i] > l and A['XAxis'][i] < r ):            
                data.append(A['Data'][i][0])
                axis.append(A['XAxis'][i])

        A['Data'] = data
        A['XAxis'] = axis

        return A

    """
    Supressed water peak.
    """
    def supressWater(self, A, l, r):
        data = []
        axis = []

        for i in range(len(A['XAxis'])):
            if ( (A['XAxis'][i] < l) or (A['XAxis'][i] > r) ):
                data.append(A['Data'][i])
                axis.append(A['XAxis'][i])

        A['Data'] = data
        A['XAxis'] = axis

        return A

    """
    Reduces variables decimals for readability.
    """
    def reduceDecimals(self, A):

        axis = []

        for i in range(len(A['XAxis'])):
            axis.append( round(A['XAxis'][i], 4) )

        A['XAxis'] = axis

        return A

    """
    Gets range of values between r and l.
    """
    def getRang(self, v, r, l):

        interval = []

        for i in range(len(v['XAxis'])):
            if ( v['XAxis'][i] > l and v['XAxis'][i] < r ):
                interval.append(v['Data'][i][0])

        return interval

    """
    Gets range of values between r and l.
    """
    def getRangB(self, axis, data, r, l):

        interval = {"data": [], "axis": []}

        for i in range(len(axis)):
            if ( axis[i] > l and axis[i] < r ):
                interval['data'].append(data[i])
                interval['axis'].append(axis[i])

        return interval

    """
    Reads the procs file.
    """
    def readprocs(self, path, file):

        path = path + "/" + file
        #print("procs path: " + str(path) + "/" + str(file))
        file = open(path, 'r')
        Lines = file.readlines()

        procVars = {}
        
        for line in Lines:
            if ( line.find("BYTORDP=") != -1 ):
                procVars["BYTORDP"] = int(line.split("= ",1)[1])
            elif ( line.find("NC_proc=") != -1 ):
                procVars["NC_proc"] = int(line.split("= ",1)[1])
            elif ( line.find("OFFSET=") != -1 ):
                procVars["OFFSET"] = float(line.split("= ",1)[1])
            elif ( line.find("SI=") != -1 ):
                procVars["SI"] = int(line.split("= ",1)[1])
            elif ( line.find("SW_p=") != -1 ):
                procVars["SW_p"] = float(line.split("= ",1)[1])
            elif ( line.find("SF=") != -1 ):
                procVars["SF"] = float(line.split("= ",1)[1])
            elif ( line.find("XDIM=") != -1 ):
                procVars["XDIM"] = int(line.split("= ",1)[1])

        return procVars

    """
    Reads the 1r file.
    """
    def read1r(self, path, endian):

        with open(path,'rb') as f:
            data = np.fromfile(f, np.int32)
            return data

        Data = []

        if endian == 'l':
            blocksize = 8

            with open(path, "rb") as f:
                while True:
                    buf = f.read(blocksize)
                    if not buf:
                        break
                    value = struct.unpack('<Q', buf)
                    Data.append(value)
        #elif endian == 'b':
    # TODO big endian
        
        return Data

    def readFile(self, path):

        # TODO deal with empty spaces

        Data = []

        file = open(path, 'r')
        Lines = file.readlines()

        for line in Lines:
            Data.append(line)

        return Data

    """
    Finds a peak value.
    """
    def maxpos(self, data, max_element):
        for i in range(len(data)):
            if (data[i] == max_element):
                return i

    """
    Finds a peak position.
    """
    def refPeakpos(self, interval, refPeak):
        greater = interval['axis'][0] > refPeak
        for i in range(len(interval['axis'])):
            if (interval['axis'][i] == refPeak):
                return i
            elif (greater == True and interval['axis'][i] < refPeak):
                return i-1

    """
    Finds a peak value.
    """
    def maxelem(self, idata):
        greater = 0
        for i in range(len(idata)):
            if (idata[i] > greater):
                greater = idata[i]
        return greater

    """
    Aligns the spectra received.
    """
    def alignSpectra(self, B, window, refPeak, refMethod):
        
        xaxis = B['XAxis']
        data = B['Data']
        
        interval = self.getRangB(xaxis, data, window[0], window[1])
        
        if refMethod == 'maxima':
            max_element = self.maxelem(interval['data'])
            max_pos = self.maxpos(interval['data'], max_element)
            peak_pos = self.refPeakpos(interval, refPeak)
            desp =  max_pos - peak_pos
        
        if desp > 0:
            zeros=np.zeros(desp)
            data_i = data[desp:len(xaxis)] 
            X = np.concatenate((data_i,zeros))
        elif desp < 0:
            zeros=np.zeros(np.abs(desp))
            rang=len(xaxis)-np.abs(desp)
            data_i=data[0:rang]
            X = np.concatenate((zeros,data_i))
        else:
            zeros=np.zeros(0)
            X = np.concatenate((zeros,data))
    
        X = np.ndarray.tolist(X)
        B['Data'] = X
            
        return B

    def getRangA(self, v,ppm1,ppm2):
        x=np.where(v < ppm1)
        z=np.where(v > ppm2)
        return np.intersect1d(x[1], z[1])

    """
    Finds a min value.
    """
    def smallerThan(self, arr, val):
        aux = []
        for i in range(len(arr)):
            if (arr[i] < val):
                aux.append(arr[i])

        return aux