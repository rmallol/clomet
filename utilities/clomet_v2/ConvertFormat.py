import os
import distutils
import shutil

from abc import abstractmethod
from distutils.dir_util import copy_tree
from shutil import rmtree

from utilities.clomet_v2.ManageErrors import ManageErrors


class ConvertFormat():

    def __init__(self, errorManager: ManageErrors):
        self.errormanager = errorManager

    """
    Creates the final zip in case it doesn't already exist.
    """
    def finalZip(self, path):
        if (os.path.exists(path + "_custom") == True and os.path.exists(path + "_custom.zip") == False):
            shutil.make_archive(path + "_custom", 'zip', path + "_custom")

    """
    Checks if the received path already exists and has to be deleted according to 'overwrite'.
    """
    def checkOverwrite(self, path, overwrite):
        if (os.path.exists(path + "_custom") == True and overwrite == "Yes"):
            rmtree(path + "_custom")
            if (os.path.exists(path + "_custom.zip") == True):
                os.remove(path + "_custom.zip")
            return True
        elif (os.path.exists(path + "_custom") == True and overwrite == "No"):
            if (os.path.exists(path + "_custom.zip") == False):
                self.finalZip(path + "_custom")
            return False
        else:
            return True

    """
    Converts each particular format to the standard format.
    """
    @abstractmethod
    def convert(self, path, overwrite):
        pass

class Format1(ConvertFormat):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Converts each particular format to the standard format.
    """
    def convert(self, path, overwrite):
        if (self.checkOverwrite(path, overwrite) == True):
            distutils.dir_util._path_created = {}
            copy_tree(path, path + "_custom")
            self.finalZip(path)
        return True

class Format2(ConvertFormat):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Converts each particular format to the standard format.
    """
    def convert(self, path, overwrite):
        if (self.checkOverwrite(path, overwrite) == True):
            distutils.dir_util._path_created = {}
            copy_tree(path, path + "_custom")
            result = self.convert_recursive(path + "_custom")
            self.finalZip(path)
            return result
        else:
            return True

    def convert_recursive(self, path):

        dirs = os.listdir(path)

        for subdir in dirs:
            subpath = path + "/" + subdir
            if ( os.path.isdir(subpath) and subdir!="pdata" ):
                self.convert_recursive(subpath)
            elif ( os.path.isdir(subpath) and subdir=="pdata" ):

                newpath = path + "/1"
                try:
                    os.mkdir(newpath)
                except OSError:
                    self.errormanager.addError("Creation of the directory %s failed" % newpath)
                    print ("Creation of the directory %s failed" % newpath)
                    return False

                for subdircpy in dirs:
                    shutil.move(path + "/" + subdircpy, newpath + "/" + subdircpy)

        return True

class Format3(ConvertFormat):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Converts each particular format to the standard format.
    """
    def convert(self, path, overwrite):
        if (self.checkOverwrite(path, overwrite) == True):
            distutils.dir_util._path_created = {}
            copy_tree(path, path + "_custom")
            result = self.convert_recursive(path + "_custom", 0)
            self.finalZip(path)
            return result
        else:
            return True

    def convert_recursive(self, path, level):

        dirs = os.listdir(path)

        for subdir in dirs:
            subpath = path + "/" + subdir
            if ( os.path.isdir(subpath) and subdir!="pdata" ):
                self.convert_recursive(subpath, level+1)
            elif ( os.path.isfile(subpath) and level > 0 ):

                idarray = path.split("/")
                newpath = path + "/" + idarray[ len(idarray)-1 ]
                try:
                    os.mkdir(newpath)
                except OSError:
                    self.errormanager.addError("Creation of the directory %s failed" % newpath)
                    print ("Creation of the directory %s failed" % newpath)
                    return False

                newpath = newpath + "/1"
                try:
                    os.mkdir(newpath)
                except OSError:
                    self.errormanager.addError("Creation of the directory %s failed" % newpath)
                    print ("Creation of the directory %s failed" % newpath)
                    return False

                for subdircpy in dirs:
                    shutil.move(path + "/" + subdircpy, newpath + "/" + subdircpy)
            
        return True

class Format4(ConvertFormat):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)
       
    """
    Converts each particular format to the standard format.
    """
    def convert(self, path, overwrite):
        if (self.checkOverwrite(path, overwrite) == True):
            distutils.dir_util._path_created = {}
            copy_tree(path, path + "_custom")
            result = self.rename_recursive(path + "_custom") and self.convert_recursive(path + "_custom")
            self.finalZip(path)
            return result
        else:
            return True

    def rename_recursive(self, path):

        dirs = os.listdir(path)

        for subdir in dirs:
            subpath = path + "/" + subdir

            if ( os.path.isdir(subpath) ):

                renamepath = subpath + "/" + subdir
                movedirs = os.listdir(subpath)

                try:
                    os.mkdir(renamepath)
                except OSError:
                    print ("Creation of the directory %s failed" % renamepath)
                    return False

                for subdircpy in movedirs:
                    if (os.path.isdir(subpath + "/" + subdircpy)):
                        movedirs2 = os.listdir(subpath + "/" + subdircpy)
                        for subdircpy2 in movedirs2:
                            shutil.move(subpath + "/" + subdircpy + "/" + subdircpy2, renamepath + "/" + subdircpy2)
                        rmtree(subpath + "/" + subdircpy)
        
        return True

    def convert_recursive(self, path):

        dirs = os.listdir(path)

        for subdir in dirs:
            subpath = path + "/" + subdir
            if ( os.path.isdir(subpath) and subdir!="pdata" ):
                self.convert_recursive(subpath)
            elif ( os.path.isdir(subpath) and subdir=="pdata" ):

                newpath = path + "/1"
                try:
                    os.mkdir(newpath)
                except OSError:
                    print ("Creation of the directory %s failed" % newpath)
                    return False

                for subdircpy in dirs:
                    shutil.move(path + "/" + subdircpy, newpath + "/" + subdircpy)
            
        return True

class Format5(ConvertFormat):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Converts each particular format to the standard format.
    """
    def convert(self, path, overwrite):
        if (self.checkOverwrite(path, overwrite) == True):
            distutils.dir_util._path_created = {}
            copy_tree(path, path + "_custom")
            result = self.rename_recursive(path + "_custom")
            self.finalZip(path)
            return result
        else:
            return True

    def rename_recursive(self, path):

        dirs = os.listdir(path)

        for subdir in dirs:

            subpath = path + "/" + subdir

            if ( os.path.isdir(subpath) ):

                renamepath = subpath + "/" + subdir
                movedirs = os.listdir(subpath)

                try:
                    os.mkdir(renamepath)
                except OSError:
                    print ("Creation of the directory %s failed" % renamepath)
                    self.errormanager.addError("Creation of the directory %s failed" % renamepath)
                    return False

                for subdircpy in movedirs:
                    if (os.path.isdir(subpath + "/" + subdircpy)):
                        movedirs2 = os.listdir(subpath + "/" + subdircpy)
                        for subdircpy2 in movedirs2:
                            shutil.move(subpath + "/" + subdircpy + "/" + subdircpy2, renamepath + "/" + subdircpy2)
                        rmtree(subpath + "/" + subdircpy)
            
        return True

class Format6(ConvertFormat):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Converts each particular format to the standard format.
    """
    def convert(self, path, overwrite):
        if (self.checkOverwrite(path, overwrite) == True):
            distutils.dir_util._path_created = {}
            copy_tree(path, path + "_custom")
            result = self.convert_recursive(path + "_custom")
            self.finalZip(path)
            return result
        else:
            return True

    def convert_recursive(self, path):
        dirs = os.listdir(path)

        for subdir in dirs:
            subpath = path + "/" + subdir

            if ( os.path.isdir(subpath)):

                lvl2subdir = os.listdir(subpath)
                newpath = subpath + "/" + subdir
                try:
                    os.mkdir(newpath)
                except OSError:
                    self.errormanager.addError("Creation of the directory %s failed" % newpath)
                    print ("Creation of the directory %s failed" % newpath)
                    return False

                for subdircpy in lvl2subdir:
                    shutil.move(subpath + "/" + subdircpy, newpath + "/" + subdircpy)
        return True
    