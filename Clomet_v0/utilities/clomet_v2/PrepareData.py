from inspect import isclass
import numpy as np
import os
import shutil
from tqdm import tqdm

from random import randrange
from utilities.clomet_v2.ManageErrors import ManageErrors 

class PrepareData:

    def __init__(self, errorManager: ManageErrors):
        self.errormanager = errorManager

class MetaboAnalyst(PrepareData):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Prepares imported data for the MA format.
    """
    def prepareMetaboAnalyst(self, A, axis, data, naxis, ndata):
        print("Preparing data...")
        for key, value in tqdm(A.items()):

            B = []
            for item in range(len(A[key][axis])):
                B.append(str("Bin.") + str(A[key][axis][item]))

            A[key][naxis] = ["Sample"] + ["Class"] +  B

            rnd = randrange(2)

            #print( type([key]) )
            #print( type(["patient"]) )
            #print( type(A[key][data]) )

            if (rnd == 0):
                if isinstance(A[key][data], list):
                    A[key][ndata] = [key] + ["patient"] + A[key][data]
                else:
                    A[key][ndata] = [key] + ["patient"] + A[key][data].tolist()
            else:
                if isinstance(A[key][data], list):
                    A[key][ndata] = [key] + ["control"] + A[key][data]
                else:
                    A[key][ndata] = [key] + ["control"] + A[key][data].tolist()
        print("End of data preparation.")
        return A

class Workflow4Metabolomics(PrepareData):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Prepares imported data for the W4M format.
    """
    def prepareMetaboAnalyst(self, A, axis, data):
        B = self.createDataMatrixGA(A, axis, data)
        C = self.createSampleMetadataGA(A)
        D = self.createVariableMetadataGA(A, axis)
        return {"DM": B, "SM": C, "VM": D}

    """
    Creates Data Matrix.
    """
    def createDataMatrixGA(self, A, axis, data):
    
        newdata =[[]]
        newaxis = ["Data"]

        first = True
        for key, value in A.items():
            if first:

                if isinstance(A[key][data], list):
                    newdata[0] = ["Data"] + A[key][axis]
                else:
                    newdata[0] = ["Data"] + A[key][axis].tolist()

                #newdata[0] = ["Data"] + A[key][axis]
                first = False

            if isinstance(A[key][data], list):
                data2append = [key] + A[key][data]
            else:
                data2append = [key] + A[key][data].tolist()

            #data2append = [key] + A[key][data]
            newdata.append(data2append)
            newaxis = np.append(newaxis, [key])

        newdata_transpose = self.transpose(newdata)

        return newdata_transpose

    """
    Transposes Matrix.
    """
    def transpose(self, l1):
        l2 = []
        for i in range(len(l1[0])):
            row =[]
            for item in range(len(l1)):
                if ( len(l1[item]) > i ):
                    row.append(l1[item][i])
                else:
                    row.append(0)
            l2.append(row)
        return l2

    """
    Creates Sample Metadata Matrix.
    """
    def createSampleMetadataGA(self, A):

        samples = ["Sample"]
        order = ["SampleOrder"]

        counter = 1
        for key, value in A.items():
            samples = samples + [key]
            order = order + [counter]
            counter = counter + 1

        matrix = [[],[]]
        matrix[0] = samples
        matrix[1] = order

        matrix_transposed = self.transpose(matrix)

        return matrix_transposed

    """
    Creates Variable Metadata Matrix.
    """
    def createVariableMetadataGA(self, A, axis):

        samples = ["Data"]
        order = ["VariableOrder"]

        for key, value in A.items():

            if isinstance(A[key][axis], list):
                samples = samples + A[key][axis]
            else:
                samples = samples + A[key][axis].tolist()

            #samples = samples + A[key][axis]
            order = order + list(range(1, len(A[key][axis])))
            break

        matrix = [[],[]]
        matrix[0] = samples
        matrix[1] = order

        matrix_transposed = self.transpose(matrix)

        return matrix_transposed

    """
    Creates Galaxy directory.
    """
    def galaxyDirectory(self, id):
    
        origpath = "media/" + id + "_custom"
        destpath = "media/" + id + "_galaxy"

        # Check it exists
        if ( os.path.exists(origpath) == False ):
            self.errormanager.addError("ERROR: original directory doesn't exist.")
            print("ERROR: original directory doesn't exist.")
            return False
        if ( os.path.exists(destpath) ):
            return True

        # Create destination directory ("_GA")

        try:
            os.mkdir(destpath)
        except OSError:
            print ("Creation of the directory %s failed" % destpath)
            self.errormanager.addError("ERROR: Creation of the directory %s failed" % destpath)
            
        destpath = destpath + "/" + id + "_galaxy"
        
        try:
            os.mkdir(destpath)
        except OSError:
            print ("Creation of the directory %s failed" % destpath)
            self.errormanager.addError("ERROR: Creation of the directory %s failed" % destpath)

        # Enter directory
        dirs = os.listdir(origpath)

        # Iterate through folders.
        for dir in dirs:
            subpath = origpath + "/" + dir
            if (os.path.isdir(subpath)):
                l2subpath = subpath + "/" + dir
                if (os.path.isdir(l2subpath)):
                    shutil.copytree(l2subpath, destpath + "/" + dir)
            else:
                shutil.copy(subpath, destpath + "/" + dir)

        # zip directory
        destpath = "media/" + id + "_galaxy"
        shutil.make_archive(destpath, 'zip', destpath)

        return True

