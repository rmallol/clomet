import os
import utilities.clomet_v2.Constants as constants
from utilities.clomet_v2.ManageErrors import ManageErrors

class Others:

    def __init__(self, errorManager: ManageErrors):
        self.errormanager = errorManager

    """
    List of files needed for the tutorials page.
    """
    def localDatasets(self):
        files = []
        path = "media"
        dirlist = os.listdir(path)

        for dir in dirlist:
            if ( dir.find("_galaxy.zip") != -1 ):
                name = dir.split("_")[0]
                if name in constants.W4MDATASETS:
                    files.append( (dir, path + "/" + dir) )

        return files

    """
    List of files needed for the tutorials page.
    """
    def localRawData(self):
        files = []
        path = "media"
        dirlist = os.listdir(path)

        for dir in dirlist:
            if ( dir.find("_output") != -1 ):
                name = dir.split("_")[0]
                if name in constants.TUTORIALDATASETS:

                    procnos = os.listdir(path + "/" + dir)
                    for procno in procnos:
                        
                        if (os.path.isdir(path + "/" + dir + "/" + procno)):
                            filelist = os.listdir(path + "/" + dir + "/" + procno)
                            for file in filelist:
                                if ( file.find("DataImport.csv") != -1 ):
                                    name = file.split("_")[0]
                                    files.append( (file, path + "/" + dir + "/" + procno + "/" + file) )

        return files

    """
    List of files needed for the tutorials page.
    """
    def localMA(self):

        files = []
        path = "media"
        dirlist = os.listdir(path)

        for dir in dirlist:
            if ( dir.find("_output") != -1 ):
                name = dir.split("_")[0]
                if name in constants.TUTORIALDATASETS:

                    procnos = os.listdir(path + "/" + dir)
                    for procno in procnos:
                        
                        if (os.path.isdir(path + "/" + dir + "/" + procno)):
                            filelist = os.listdir(path + "/" + dir + "/" + procno)
                            for file in filelist:
                                if ( file.find("BinningMA.csv") != -1 ):
                                    name = file.split("_")[0]
                                    files.append( (file, path + "/" + dir + "/" + procno + "/" + file) )

        return files

    """
    List of files needed for the tutorials page.
    """
    def localW4M(self):

        files = []
        path = "media"
        dirlist = os.listdir(path)

        for dir in dirlist:
            if ( dir.find("_output") != -1 ):
                name = dir.split("_")[0]
                if name in constants.W4MDATASETS:

                    procnos = os.listdir(path + "/" + dir)
                    for procno in procnos:
                        
                        if (os.path.isdir(path + "/" + dir + "/" + procno)):
                            filelist = os.listdir(path + "/" + dir + "/" + procno)
                            for file in filelist:
                                if ( file.find(".zip") != -1 and file.find("BinW4M") != -1):
                                    files.append( (file, path + "/" + dir + "/" + procno + "/" + file) )

        return files

