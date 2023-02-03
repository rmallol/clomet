import os
import shutil

from distutils.dir_util import copy_tree
from utilities.clomet_v2.ManageErrors import ManageErrors

class DetectFormat:

    def __init__(self, errorManager: ManageErrors):
        self.errormanager = errorManager

    """
    Detects the format from the received MTBLS study ID.
    """
    def detectFormat(self, id):
    
        path = "media/" + id

        if (os.path.exists(path)):
            ret = self.detectFormatRecursive(path, 0)
            if ret == 3:
                if (self.equalNames(path) == True):
                    return 1
                else:
                    return 5    # No case existing for now
            elif ret == 2:
                if (self.equalNames(path) == True):
                    return 2
                else:
                    if(self.singleDirectory(path)):
                        return 4
                    else:
                        return 6
            elif ret==1:
                return 3
            else:
                return 7
        else:
            self.errormanager.addError("ERROR: Detect format path does not exist")
            print("The path does not exist in Detect Format: " + path)
            return 7

    def detectFormatRecursive(self, directoryURL, level):

        dirs = os.listdir( directoryURL )
        maxDepth = 0

        for subdir in dirs:
            subpath = directoryURL + "/" + subdir
            if ( os.path.isfile(subpath)  ):
                
                if (subpath.find('fid') != -1):
                    return level
            elif ( os.path.isdir(subpath) ):
                ret = self.detectFormatRecursive( subpath, level+1 )
                if (ret > maxDepth):
                    maxDepth = ret
        
        return maxDepth

    def equalNames(self, path):
        dirs = os.listdir( path )

        for subdir in dirs:
            subpath = path + "/" + subdir
            if ( os.path.isdir(subpath)  ):
                if ( os.path.isdir(subpath + "/" + subdir)  ):
                    return True
                else:
                    return False

    def singleDirectory(self, path):
        dirs = os.listdir( path )

        for subdir in dirs:
            subpath = path + "/" + subdir
            if ( os.path.isdir(subpath)  ):
                subdirs = os.listdir( subpath )
                
                count = 0
                for procdirs in subdirs:
                    count = count + 1

                if ( count == 1 ):
                    return True
                else:
                    return False

class MetabolomicsWorkbenchFormat(DetectFormat):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Detects the format from the received MW study ID.
    """
    def detectFormat(self, id):
        if (self.findRawData(id) == False):
            return False
        return super().detectFormat(id + "_data")

    """
    Finds the raw data directory inside the study received.
    """
    def findRawData(self, id):
        path = "media/" + id
        path = self.findRawDataRecursive(path)

        if isinstance(path, str) == False:
            return False

        path = self.finalDirectory(path + "/")

        if (path != False and os.path.exists("media/" + id + "_data") == False):
            try:
                os.mkdir("media/" + id + "_data")
            except OSError:
                self.errormanager.addError("ERROR: Creation of the directory %s failed" % ("media/" + id + "_data"))
                print ("Creation of the directory %s failed" % ("media/" + id + "_data"))
            copy_tree(path, "media/" + id + "_data" )
        elif (path == False):
            return False

        if (os.path.exists("media/" + id + "_data") == True and os.path.exists("media/" + id + "_data.zip") == False):
            shutil.make_archive("media/" + id + "_data", 'zip', "media/" + id + "_data")

        return True

    def findRawDataRecursive(self, path):
        dirs = os.listdir( path )

        found = -1

        for subdir in dirs:
            subpath = path + "/" + subdir
            if (os.path.isdir(subpath) and subpath.lower().find("pdata")!=-1):
                if(self.checkFiles(subpath) == True):
                    return 0
            if ( os.path.isdir(subpath) and subpath.lower().find("mac")==-1):
                result = self.findRawDataRecursive(subpath)
                if isinstance(result, str):
                    print(subpath + " returns " + str(result))
                    return result
                elif result == 1:
                    print(subpath + " returns " + str(result))
                    return path
                elif result > found:
                    found = result
                elif found == result and found != -1:
                    print(subpath + " returns " + str(result))
                    return found +1

        if found == -1:
            return found
        else:
            return found + 1

    def findRawDataRecursive2(self, path):
        dirs = os.listdir( path )

        found = False

        for subdir in dirs:
            subpath = path + "/" + subdir
            if (os.path.isdir(subpath) and subpath.lower().find("pdata")!=-1):
                if(self.checkFiles(subpath) == True):
                    print("END: " + subpath)
                    return True
            if ( os.path.isdir(subpath) and subpath.lower().find("mac")==-1):
                result = self.findRawDataRecursive2(subpath)
                if isinstance(result, str):
                    return result
                elif found == False and result == True:
                    found = True
                elif found == True and result == True:
                    return path

        return found

    def checkFiles(self, path):
        dirs = os.listdir( path )
        for subdir in dirs:
            subpath = path + "/" + subdir
            if ( os.path.isdir(subpath) and os.path.exists(subpath + "/1r") == True 
                        and (os.path.exists(subpath + "/proc") == True or os.path.exists(subpath + "/proc") == True) ):
                return True
            elif ( os.path.isdir(subpath) ):
                if self.checkFiles(subpath) == True:
                    return True
        return False

    """
    Creates the final directory.
    """
    def finalDirectory(self, path):
        dirs = os.listdir( path )

        if(len(dirs) == 1):
            for dir in dirs:
                return path + dir
        else:
            return path