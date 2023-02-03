import os

from utilities.clomet_v2.ManageErrors import ManageErrors

class Parameters:

    def __init__(self, errorManager: ManageErrors):
        self.errormanager = errorManager

    """
    Reads procno from file system.
    """
    def readProcno(self, id):

        returndict = []
        path="media/" + id + "_custom"
        dirs = os.listdir( path )

        for subdir in dirs:
            subpath = path + "/" + subdir
            if ( os.path.isdir(subpath) ):
                subpath = subpath + "/" + subdir
                subpaths = os.listdir(subpath)
                
                count = 1
                for subprocno in subpaths:
                    filepath = subpath + "/" + subprocno + "/acqu"
                    if ( os.path.isfile(filepath) ):
                        returndict = self.appendProcno(filepath, subpath, subprocno, returndict)

                    elif ( os.path.isfile(subpath + "/" + subprocno + "/acqus") ):
                        filepath = subpath + "/" + subprocno + "/acqus"
                        returndict = self.appendProcno(filepath, subpath, subprocno, returndict)
                        
                    else:       # Acqu does not exist
                        self.errormanager.addError("ERROR: Acqu(s) does not exist. Can't select pulprog.")
                        print("ERROR: Acqu(s) does not exist. Can't select pulprog.")

                return returndict

        return returndict

    """
    Appends procno from file system.
    """
    def appendProcno(self, filepath, subpath, subprocno, returndict):
        file = open(filepath, 'r')
        Lines = file.readlines()

        for line in Lines:
            
            if ( line.find("PULPROG=") != -1 ):
                pulprog = line.split("<",1)[1]
                pulprog = pulprog.split(">",1)[0]
                if (self.requiredFiles( subpath + "/" + subprocno ) == True):
                    returndict.append(pulprog + " (" + subprocno + ")")
                    #self.errormanager.addInfo('Available PULPROG: ' + pulprog)
                else:
                    print('Invalid PULPROG: ' + pulprog + " in path " + subpath + "/" + subprocno)
                    self.errormanager.addError('Invalid PULPROG: ' + pulprog)

        return returndict

    """
    Checks if required files exist.
    """  
    def requiredFiles(self, path):
        
        if ( os.path.exists(path + "/pdata") == False ):
            return False
        
        if ( os.path.exists(path + "/pdata/1/1r") == False ):
            return False
        
        if ( os.path.exists(path + "/pdata/1/procs") == False and os.path.exists(path + "/pdata/1/proc") == False):
            return False
                    
        return True


