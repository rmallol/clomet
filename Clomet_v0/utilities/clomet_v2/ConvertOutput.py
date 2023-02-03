import csv
import os
import numpy as np

from numpy import isin

from utilities.clomet_v2.ManageErrors import ManageErrors

class ConvertOutput:

    def __init__(self, errorManager: ManageErrors):
        self.errormanager = errorManager

class CSV(ConvertOutput):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Creates a CSV file from the received data.
    """
    def toCSV(self, A, axis, data, id, step, procno):
        path = "media/" + str(id) + "_output"
        #path = "ResumVisual/" + str(id) + "_output"
        path = self.dirCheck(path, procno)
        
        writeCSV = [[]]
        header = False
        counter = 1
        for key, value in A.items():
            if header == False:
                writeCSV[0] = value[axis]
                header = True

            aux = []
            for val in value[data]:
                if isinstance(val, float):
                    aux.append(val)
                elif isinstance(val, str):
                    aux.append(val)
                elif isinstance(val, int):
                    aux.append(val)
                #elif val[0] <= 0.0:
                #    aux.append(0)
                elif isinstance(val, np.int32):
                    aux.append( abs(val.item()) )
                else:
                    #aux.append(val[0])
                    #print("Unknown type: " + str(type(val)))
                    aux.append( abs(val) )

            writeCSV.append(aux)
            counter = counter + 1

        if ( len(writeCSV[0]) == 0 ):
            self.errormanager.addError("ERROR: nothing to be appended to csv")
            print("ERROR: nothing to be appended to csv")
            #addErrorReport("Nothing to be appended to csv")
            with open( path + '/' + id + "_" + procno["name"] + "_" + step  + '.csv', 'w', newline='') as file:
                mywriter = csv.writer(file, delimiter=',')
                mywriter.writerows("ERROR: No data to be inserted")
            return False
        else:
            with open( path + '/' + id + "_" + procno["name"] + "_" + step  + '.csv', 'w', newline='') as file:
                mywriter = csv.writer(file, delimiter=',')
                mywriter.writerows(writeCSV)

        return True

    """
    Checks if a particular path exists.
    """
    def dirCheck(self, path, procno):
        if (os.path.exists(path) == False):
            try:
                os.mkdir(path)
            except OSError:
                self.errormanager.addError("Creation of the directory %s failed" % path)
                print ("Creation of the directory %s failed" % path)

        path = path + "/" + str(procno["num"])
        if (os.path.exists(path) == False):
            try:
                os.mkdir(path)
            except OSError:
                self.errormanager.addError("Creation of the directory %s failed" % path)
                print ("Creation of the directory %s failed" % path)

        return path

class TSV(ConvertOutput):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Creates a TABULAR file from the received data.
    """
    def toTSV(self, A, id, step, procno, extra):
        path = "media/" + str(id) + "_output"

        path = self.dirCheck(path, procno, extra)
        
        values = False
        writeCSV = []
        for key in range(len(A)):
            writeCSV.append(A[key])
            values = True

        if ( values == False ):
            print("ERROR: nothing to be appended to tabular")
            self.errormanager.addError("ERROR: nothing to be appended to tabular")
            with open( path + '/' + id + "_" + procno["name"] + "_" + step  + '.tabular', 'w', newline='') as file:
                mywriter = csv.writer(file, delimiter='\t')
                mywriter.writerows("ERROR: No data to be inserted")
            return False
        else:
            with open( path + '/' + id + "_" + procno["name"] + "_" + step  + '.tabular', 'w', newline='') as file:
                mywriter = csv.writer(file, delimiter='\t')
                mywriter.writerows(writeCSV)

        return True

    """
    Checks if a particular path exists.
    """
    def dirCheck(self, path, procno, extra):
        if (os.path.exists(path) == False):
            try:
                os.mkdir(path)
            except OSError:
                self.errormanager.addError("Creation of the directory %s failed" % path)
                print ("Creation of the directory %s failed" % path)

        path = path + "/" + str(procno["num"])
        if (os.path.exists(path) == False):
            try:
                os.mkdir(path)
            except OSError:
                self.errormanager.addError("Creation of the directory %s failed" % path)
                print ("Creation of the directory %s failed" % path)

        path = path + "/" + extra
        if (os.path.exists(path) == False):
            try:
                os.mkdir(path)
            except OSError:
                self.errormanager.addError("Creation of the directory %s failed" % path)
                print ("Creation of the directory %s failed" % path)

        return path
