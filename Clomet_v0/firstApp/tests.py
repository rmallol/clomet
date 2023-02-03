from django.test import TestCase

import os
import shutil
import csv
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


from utilities.clomet_v2.ImportData import ImportData
from utilities.clomet_v2.LoadDataset import Metabolights, MetabolomicsWorkbench
from utilities.clomet_v2.DetectFormat import DetectFormat, MetabolomicsWorkbenchFormat
from utilities.clomet_v2.ConvertFormat import Format1, Format2, Format3, Format4, Format5, Format6
from utilities.clomet_v2.ManageErrors import ManageErrors
from utilities.clomet_v2.Parameters import Parameters
from utilities.clomet_v2.PrepareData import Workflow4Metabolomics, MetaboAnalyst
from utilities.clomet_v2.ReduceData import Binning
from utilities.clomet_v2.ConvertOutput import CSV,TSV
from utilities.clomet_v2.Others import Others
from utilities.clomet_v2.Dataset import Dataset


# MTBLS103 --> fids
# MTBLS147 --> One of them does not contain enough info (ignored and solved)
# MTBLS1518 --> weird
# MTBLS174 --> No pulprog
# MTBLS249 --> No pulprog
# MTBLS356 --> Empty data


class VisualTests(TestCase):

    globalMean = {}
    cpmgMean = {}

    def init_all(self, id):

        print(id)

        self.errormanager = ManageErrors()
        self.dataset = Dataset()
        self.parameters = Parameters(self.errormanager)
        self.importdata = ImportData(self.errormanager)
        self.bindata = Binning(self.errormanager)
        self.csv = CSV(self.errormanager)
        self.tsv = TSV(self.errormanager)
        self.metaboanalyst = MetaboAnalyst(self.errormanager)
        self.w4m = Workflow4Metabolomics(self.errormanager)
        self.others = Others(self.errormanager)

        urlrequested = ""
        self.errormanager.setTitle(id)

        if ( id.find("MTBLS") != -1 ):
            #MTBLS case
            urlrequested = "https://www.ebi.ac.uk/metabolights/" + str(id) + "/files"
            self.loader = Metabolights(self.errormanager)
            self.formatdetect = DetectFormat(self.errormanager)
            self.errormanager.addInfo("Metabolights dataset")
        elif ( id.find("ST") != -1 ):
            #WB case
            urlrequested = "https://www.metabolomicsworkbench.org/studydownload/" + id + ".zip"
            self.loader = MetabolomicsWorkbench(self.errormanager)
            self.formatdetect = MetabolomicsWorkbenchFormat(self.errormanager)
            self.errormanager.addInfo("Metabolomics workbench dataset")
        else:
            print("URL does not exist")
            self.errormanager.addError("ERROR: Id does not belong to any database")
            self.errormanager.temporal()
            print("Id does not belong to any database")
            return {"errors": "Id does not belong to any database"}

        if ( self.loader.checkURL(urlrequested) == False ):
            self.errormanager.addError("ERROR: URL does not exist")
            self.errormanager.temporal()
            print("URL does not exist")
            return {"errors": "URL does not exist"}

        overwrite = "No"
        
        if (self.loader.performWebScrappingURL(id, overwrite) == False):
            self.errormanager.addError("ERROR: Webscrapping error")
            self.errormanager.temporal()
            print("Webscrapping error")
            return {"errors": "Webscrapping error"}

        formatType = self.formatdetect.detectFormat(id)

        #print(formatType)
        if(formatType==1):
            self.formatconvert = Format1(self.errormanager)
        elif(formatType==2):
            self.formatconvert = Format2(self.errormanager)
        elif(formatType==3):
            self.formatconvert = Format3(self.errormanager)
        elif(formatType==4):
            self.formatconvert = Format4(self.errormanager)
        elif(formatType==5):
            self.formatconvert = Format5(self.errormanager)
        elif(formatType==6):
            self.formatconvert = Format6(self.errormanager)
        else:
            self.errormanager.addError("ERROR: Format type does not exist")
            self.errormanager.temporal()
            print("Format type does not exist")
            return {"errors": "Format type does not exist"}

        if ( id.find("ST") != -1 ):
            id = id + "_data"

        if (self.formatconvert.convert("media/" + str(id), overwrite) == False):
            self.errormanager.addError("ERROR: Format convert error")
            self.errormanager.temporal()
            print("Format convert error")
            return {"errors": "Format convert error"}

        if (self.w4m.galaxyDirectory(id) == False):
            self.errormanager.addError("ERROR: Format convert error")
            self.errormanager.temporal()
            print("Format convert error")
            return {"errors": "Format convert error"}

        procnos = self.parameters.readProcno(id)

        #print(procnos)

        pulstr = "Valid pulprogs:"
        for pulprog in procnos:
            pulstr = pulstr + " " + pulprog
        self.errormanager.addInfo(pulstr)

        if (len(procnos) == 0):
            self.errormanager.addError("ERROR: No available 1D PULPROG found")
            self.errormanager.temporal()
            procnos = ["No available 1D PULPROG found"]

        links = []
        if (os.path.exists("media/" + id + ".zip") == True):
            links.append(["RawData.zip", "media/" + id + ".zip"])
        if (os.path.exists("media/" + id + "_data.zip") == True):
            links.append(["RawData.zip", "media/" + id + "_data.zip"])
        if (os.path.exists("media/" + id + "_custom.zip") == True):
            links.append(["CustomData.zip", "media/" + id + "_custom.zip"])
        if (os.path.exists("media/" + id + "_galaxy.zip") == True):
            links.append(["W4MData.zip", "media/" + id + "_galaxy.zip"])


        # ----------------  second view ------------------------------------------------

        for procnofull in procnos:

            print(procnofull)        

            name = procnofull.split(" (", 1)[0]
            num = procnofull.split(" (", 1)[1]
            num = num.split(")", 1)[0]
            
            procno = {}
            procno['num'] = num
            procno['name'] = name

            A = self.importdata.dataImportManager(id, procno)

            if (A["errors"] != "None"):
                #return {"errors": {"title": "Missing files", "message": A["errors"]} }
                print("ERROR: Missing files but no return")
            else:
                A.pop("errors")

                data = 'Data'
                counter = 0
                header = []
                aux = []
                
                for key, value in A.items():

                    if counter == 0:
                        #print( len(value['XAxis']) )
                        #print( len(value[data]) )
                        header = value['XAxis']
                        aux = [0 for col in range(len(header))]
                        aux = self.toInt(value[data])
                    else:
                        ret = self.toInt(value[data])
                        if len(aux) != len(ret):
                            print("ERROR: different lengths in addition")
                            counter = counter - 1
                        else:
                            aux = [aux[i] + ret[i] for i in range(len(aux))]

                    counter = counter + 1

                aux = [aux[i]/counter for i in range(len(aux))]

                path = "ResumVisual/" + str(id) + "_output"

                path = self.csv.dirCheck(path, procno)

                plt.figure()
                self.plotMean(id, header, aux, path + '/' + id + "_" + procno["name"] + "_" + "Mean" + '.png')
                plt.close()
                plt.figure()
                self.plotData(A, id, path + '/' + id + "_" + procno["name"] + "_" + "Complete" + '.png')
                plt.close()
                plt.figure()
                self.plotSection(A, id, path + '/' + id + "_" + procno["name"] + "_" + "Section" + '.png')
                plt.close()
                
                writeCSV = [[]]
                writeCSV[0] = header
                writeCSV.append(aux)

                try:
                    VisualTests.globalMean[id] = [header, aux]
                except NameError:
                    VisualTests.globalMean = {}
                    VisualTests.globalMean[id] = [header, aux]
                except AttributeError: 
                    VisualTests.globalMean = {}
                    VisualTests.globalMean[id] = [header, aux]

                if (procno["name"].find("cpmg") != -1):
                    try:
                        VisualTests.cpmgMean[id] = [header, aux]
                    except NameError:
                        VisualTests.cpmgMean = {}
                        VisualTests.cpmgMean[id] = [header, aux]
                    except AttributeError: 
                        VisualTests.cpmgMean = {}
                        VisualTests.cpmgMean[id] = [header, aux]

                with open( path + '/' + id + "_" + procno["name"] + "_" + "Visual"  + '.csv', 'w', newline='') as file:
                    mywriter = csv.writer(file, delimiter=',')
                    mywriter.writerows(writeCSV)

    def plotMean(self, key, axis, data, path):

        plt.rcParams['figure.figsize'] = [100, 50]
        plt.rcParams['font.size'] = '16'
        
        mpl.rcParams['agg.path.chunksize'] = 100000

        sectionStart = -0.5
        sectionEnd = 9

        count = 0
        while (axis[count] > sectionEnd):
            count = count + 1
        start = count
        while(axis[count] > sectionStart and count < (len(axis)-1)):
            count = count + 1
        end = count

        plt.plot(axis[start:end], data[start:end], label=key)

        plt.plot()

        plt.xlabel("¹H chemical shift, ppm", fontsize=16)
        plt.ylabel("intensity, au", fontsize=16)
        plt.title(str(key) + " mean")
        plt.legend(loc='upper right')
        plt.show()
        plt.savefig(path)

    def plotData(self, A, id, path):

        sectionStart = -0.5
        sectionEnd = 9

        x = []

        plt.rcParams['figure.figsize'] = [100, 50]
        plt.rcParams['font.size'] = '16'
        
        mpl.rcParams['agg.path.chunksize'] = 100000

        #for key, value in A.items():

        #    if x == []:
        #        x = value['XAxis']
        #        if len(x) == 0 :
        #            return

        #    y = self.toInt(value['Data'])

        #    plt.plot( x,y, label=str(key))

        start = 0
        end = len(x)

        for key, value in A.items():

            x = value['XAxis']
            print(min(x))
            if len(x) == 0:
                print("ERROR: NULL X axis")
                return 

            count = 0
            while (x[count] > sectionEnd):
                count = count + 1
            start = count
            while(x[count] > sectionStart and count < (len(x)-1)):
                count = count + 1
            end = count

            x = x[start:end]

            y = self.toInt(value['Data'])
            y = y[start:end]

            plt.plot( x,y, label=str(key))

        plt.plot()

        plt.xlabel("¹H chemical shift, ppm", fontsize=16)
        plt.ylabel("intensity, au", fontsize=16)
        plt.title(str(key) + " data")
        #plt.legend(loc='upper right')
        plt.show()
        plt.savefig(path)
 
    def plotSection(self, A, id, path):

        sectionStart = 0.5
        sectionEnd = 1.4
        #1.31-1.35
        x = []
        counter = 0

        plt.rcParams['figure.figsize'] = [100, 50]
        plt.rcParams['font.size'] = '16'
        
        mpl.rcParams['agg.path.chunksize'] = 100000

        start = 0
        end = len(x)

        for key, value in A.items():

            if x == []:
                x = value['XAxis']

                if len(x) == 0:
                    print("ERROR: NULL X axis")
                    return 

                count = 0
                while (x[count] > sectionEnd):
                    count = count + 1
                start = count
                while(x[count] > sectionStart):
                    count = count + 1
                end = count

                x = x[start:end]
                print(len(x))
                print(x[0])
                print(x[len(x)-1])

            y = self.toInt(value['Data'])
            y = y[start:end]
            
            #aux = [y[i]/1e18 for i in range(len(y))]
            #print(aux)

            plt.plot( x,y, label=str(key))
                
            counter = counter + 1

        plt.plot()

        plt.xlabel("¹H chemical shift, ppm", fontsize=16)
        plt.ylabel("intensity, au", fontsize=16)
        plt.title(str(key) + " data")
        #plt.legend(loc='upper right')
        plt.show()
        plt.savefig(path)

    def toInt(self, value):
        aux = []
        for val in value:
            if isinstance(val, float):
                aux.append( abs(val) )
            elif isinstance(val, str):
                aux.append( abs(float(val)) )
            elif isinstance(val, int):
                aux.append( abs(val) )
            #elif val[0] <= 0.0:
            #    aux.append(0)
            elif isinstance(val, np.int32):
                aux.append( abs(val.item()) )
            else:
                #aux.append(val[0])
                #print("Unknown type: " + str(type(val)))
                aux.append( abs(val) )
        return aux

    def plotMeanSection(self, path, A):

        sectionStart = 0.5
        sectionEnd = 1.4

        x = []

        plt.rcParams['figure.figsize'] = [100, 50]
        plt.rcParams['font.size'] = '16'
        
        mpl.rcParams['agg.path.chunksize'] = 100000

        start = 0
        end = len(x)

        for key, value in A.items():

            x = value[0]
            if len(x) == 0:
                print("ERROR: NULL X axis")
                return 

            count = 0
            while (x[count] > sectionEnd):
                count = count + 1
            start = count
            while(x[count] > sectionStart):
                count = count + 1
            end = count

            x = x[start:end]

            y = self.toInt(value[1])
            y = y[start:end]

            plt.plot( x,y, label=str(key))

        plt.plot()

        plt.xlabel("¹H chemical shift, ppm", fontsize=16)
        plt.ylabel("intensity, au", fontsize=16)
        plt.title("Study data")
        #plt.legend(loc='upper right')
        plt.show()
        plt.savefig(path)

    def plotMeanComplete(self, path, A):

        sectionStart = -0.5
        sectionEnd = 9

        x = []

        plt.rcParams['figure.figsize'] = [100, 50]
        plt.rcParams['font.size'] = '16'
        
        mpl.rcParams['agg.path.chunksize'] = 100000

        #for key, value in A.items():

        #    x = value[0]

        #    if len(x) == 0:
        #        print("ERROR: NULL X axis")
        #        return

        #    y = self.toInt(value[1])

        #    plt.plot( x,y, label=str(key))

        start = 0
        end = len(x)

        for key, value in A.items():

            x = value[0]
            if len(x) == 0:
                print("ERROR: NULL X axis")
                return 

            count = 0
            while (x[count] > sectionEnd):
                count = count + 1
            start = count
            while(x[count] > sectionStart and count < (len(x)-1)):
                count = count + 1
            end = count

            x = x[start:end]

            y = self.toInt(value[1])
            y = y[start:end]

            plt.plot( x,y, label=str(key))

        plt.plot()

        plt.xlabel("¹H chemical shift, ppm", fontsize=16)
        plt.ylabel("intensity, au", fontsize=16)
        plt.title("Study data")
        #plt.legend(loc='upper right')
        plt.show()
        plt.savefig(path)

    def test_ZGlobalMean(self):
        plt.figure()
        self.plotMeanSection("ResumVisual/MeanSectionGraph", self.globalMean)
        plt.close()
        plt.figure()
        self.plotMeanComplete("ResumVisual/MeanCompleteGraph", self.globalMean)
        plt.close()
        plt.figure()
        self.plotMeanSection("ResumVisual/CpmgMeanSectionGraph", self.cpmgMean)
        plt.close()
        plt.figure()
        self.plotMeanComplete("ResumVisual/CpmgMeanCompleteGraph", self.cpmgMean)
        plt.close()
        
    def test_MTBLS2967(self):
        self.init_all("MTBLS2967")

    def test_MTBLS1357(self):
        self.init_all("MTBLS1357")

    def test_MTBLS981(self):
        self.init_all("MTBLS981")

    def test_MTBLS1497(self):
        self.init_all("MTBLS1497")

    #def test_MTBLS1518(self):
    #    self.init_all("MTBLS1518")

    def test_MTBLS563(self):
        self.init_all("MTBLS563")

    def test_MTBLS798(self):
        self.init_all("MTBLS798")

    def test_MTBLS974(self):
        self.init_all("MTBLS974")

    def test_MTBLS395(self):
        self.init_all("MTBLS395")

    def test_MTBLS470(self):
        self.init_all("MTBLS470")

    def test_MTBLS356(self):
        self.init_all("MTBLS356")

    def test_MTBLS326(self):
        self.init_all("MTBLS326")

    #def test_MTBLS249(self):
    #    self.init_all("MTBLS249")

    def test_MTBLS374(self):
        self.init_all("MTBLS374")

    def test_MTBLS424(self):
        self.init_all("MTBLS424")
        #self.test_ZGlobalMean()

    def test_MTBLS242(self):
        self.init_all("MTBLS242")

    def test_MTBLS200(self):
        self.init_all("MTBLS200")

    #def test_MTBLS174(self):
    #    self.init_all("MTBLS174")

    def test_MTBLS172(self):
        self.init_all("MTBLS172")

    #def test_MTBLS540(self):
    #    self.init_all("MTBLS540")

    def test_MTBLS161(self):
        self.init_all("MTBLS161")

    #def test_MTBLS103(self):
    #    self.init_all("MTBLS103")

    def test_MTBLS46(self):
        self.init_all("MTBLS46")

    #def test_MTBLS147(self):
    #    self.init_all("MTBLS147")

    def test_MTBLS678(self):
        self.init_all("MTBLS678")

    def test_ST000020(self):
        self.init_all("ST000020")

    def test_ST000022(self):
        self.init_all("ST000022")

    def test_ST000050(self):
        self.init_all("ST000050")

    def test_ST000051(self):
        self.init_all("ST000051")

    def test_ST000104(self):
        self.init_all("ST000104")

    def test_ST000223(self):
        self.init_all("ST000223")

    def test_ST000256(self):
        self.init_all("ST000256")

    def test_ST000306(self):
        self.init_all("ST000306")

    def test_ST000315(self):
        self.init_all("ST000315")

    def test_ST000364(self):
        self.init_all("ST000364")

    def test_ST000366(self):
        self.init_all("ST000366")

    def test_ST000438(self):
        self.init_all("ST000438")

    def test_ST000439(self):
        self.init_all("ST000439")

    def test_ST000407(self):
        self.init_all("ST000407")

    def test_ST000440(self):
        self.init_all("ST000440")

    def test_ST000442(self):
        self.init_all("ST000442")

    def test_ST000454(self):
        self.init_all("ST000454")

    def test_ST000455(self):
        self.init_all("ST000455")

    def test_ST000464(self):
        self.init_all("ST000464")

    def test_ST000605(self):
        self.init_all("ST000605")

    def test_ST000785(self):
        self.init_all("ST000785")

    def test_ST000826(self):
        self.init_all("ST000826")

    def test_ST000891(self):
        self.init_all("ST000891")

    def test_ST000892(self):
        self.init_all("ST000892")

    def test_ST000939(self):
        self.init_all("ST000939")

    def test_ST001038(self):
        self.init_all("ST001038")

    def test_ST001054(self):
        self.init_all("ST001054")

    def test_ST001129(self):
        self.init_all("ST001129")

    def test_ST001138(self):
        self.init_all("ST001138")

    def test_ST001139(self):
        self.init_all("ST001139")

    def test_ST001284(self):
        self.init_all("ST001284")

    def test_ST001294(self):
        self.init_all("ST001294")

    def test_ST001295(self):
        self.init_all("ST001295")

    def test_ST001319(self):
        self.init_all("ST001319")

    def test_ST001354(self):
        self.init_all("ST001354")

    def test_ST001375(self):
        self.init_all("ST001375")

    def test_ST001476(self):
        self.init_all("ST001476")

    def test_ST001615(self):
        self.init_all("ST001615")

    def test_ST001616(self):
        self.init_all("ST001616")

    def test_ST001706(self):
        self.init_all("ST001706")

    def test_ST001813(self):
        self.init_all("ST001813")


class FinalTests(TestCase):

    def init_all(self, id):
        self.errormanager = ManageErrors()
        self.dataset = Dataset()
        self.parameters = Parameters(self.errormanager)
        self.importdata = ImportData(self.errormanager)
        self.bindata = Binning(self.errormanager)
        self.csv = CSV(self.errormanager)
        self.tsv = TSV(self.errormanager)
        self.metaboanalyst = MetaboAnalyst(self.errormanager)
        self.w4m = Workflow4Metabolomics(self.errormanager)
        self.others = Others(self.errormanager)

        urlrequested = ""
        self.errormanager.setTitle(id)

        if ( id.find("MTBLS") != -1 ):
            #MTBLS case
            urlrequested = "https://www.ebi.ac.uk/metabolights/" + str(id) + "/files"
            self.loader = Metabolights(self.errormanager)
            self.formatdetect = DetectFormat(self.errormanager)
            self.errormanager.addInfo("Metabolights dataset")
        elif ( id.find("ST") != -1 ):
            #WB case
            urlrequested = "https://www.metabolomicsworkbench.org/studydownload/" + id + ".zip"
            self.loader = MetabolomicsWorkbench(self.errormanager)
            self.formatdetect = MetabolomicsWorkbenchFormat(self.errormanager)
            self.errormanager.addInfo("Metabolomics workbench dataset")
        else:
            print("URL does not exist")
            self.errormanager.addError("ERROR: Id does not belong to any database")
            self.errormanager.temporal()
            print("Id does not belong to any database")
            return {"errors": "Id does not belong to any database"}

        if ( self.loader.checkURL(urlrequested) == False ):
            self.errormanager.addError("ERROR: URL does not exist")
            self.errormanager.temporal()
            print("URL does not exist")
            return {"errors": "URL does not exist"}

        overwrite = "No"
        
        if (self.loader.performWebScrappingURL(id, overwrite) == False):
            self.errormanager.addError("ERROR: Webscrapping error")
            self.errormanager.temporal()
            print("Webscrapping error")
            return {"errors": "Webscrapping error"}

        formatType = self.formatdetect.detectFormat(id)

        print(formatType)
        if(formatType==1):
            self.formatconvert = Format1(self.errormanager)
        elif(formatType==2):
            self.formatconvert = Format2(self.errormanager)
        elif(formatType==3):
            self.formatconvert = Format3(self.errormanager)
        elif(formatType==4):
            self.formatconvert = Format4(self.errormanager)
        elif(formatType==5):
            self.formatconvert = Format5(self.errormanager)
        elif(formatType==6):
            self.formatconvert = Format6(self.errormanager)
        else:
            self.errormanager.addError("ERROR: Format type does not exist")
            self.errormanager.temporal()
            print("Format type does not exist")
            return {"errors": "Format type does not exist"}

        if ( id.find("ST") != -1 ):
            id = id + "_data"

        print("test")

        if (self.formatconvert.convert("media/" + str(id), overwrite) == False):
            self.errormanager.addError("ERROR: Format convert error")
            self.errormanager.temporal()
            print("Format convert error")
            return {"errors": "Format convert error"}

        if (self.w4m.galaxyDirectory(id) == False):
            self.errormanager.addError("ERROR: Format convert error")
            self.errormanager.temporal()
            print("Format convert error")
            return {"errors": "Format convert error"}

        procnos = self.parameters.readProcno(id)

        print(procnos)

        pulstr = "Valid pulprogs:"
        for pulprog in procnos:
            pulstr = pulstr + " " + pulprog
        self.errormanager.addInfo(pulstr)

        if (len(procnos) == 0):
            self.errormanager.addError("ERROR: No available 1D PULPROG found")
            self.errormanager.temporal()
            procnos = ["No available 1D PULPROG found"]

        links = []
        if (os.path.exists("media/" + id + ".zip") == True):
            links.append(["RawData.zip", "media/" + id + ".zip"])
        if (os.path.exists("media/" + id + "_data.zip") == True):
            links.append(["RawData.zip", "media/" + id + "_data.zip"])
        if (os.path.exists("media/" + id + "_custom.zip") == True):
            links.append(["CustomData.zip", "media/" + id + "_custom.zip"])
        if (os.path.exists("media/" + id + "_galaxy.zip") == True):
            links.append(["W4MData.zip", "media/" + id + "_galaxy.zip"])


        # ----------------  second view ------------------------------------------------
        procnofull = procnos[0]

        print(procnofull)        

        name = procnofull.split(" (", 1)[0]
        num = procnofull.split(" (", 1)[1]
        num = num.split(")", 1)[0]
        
        procno = {}
        procno['num'] = num
        procno['name'] = name

        if ( id.find("ST") != -1 ):
            id = id + "_data"

        A = self.importdata.dataImportManager(id, procno)

        if (A["errors"] != "None"):
            return {"errors": {"title": "Missing files", "message": A["errors"]} }
        else:
            A.pop("errors")

        basedir = ""
        for dir in A:
            basedir = dir
            break

        self.errormanager.addData("Chosen pulprog: " + procno['name'])
        self.errormanager.addData("Number of samples: " + str(len(A)))
        self.errormanager.addData("Initial size: " + str(len(A[basedir]["XAxis"])))

        #A = self.metaboanalyst.prepareMetaboAnalyst(A, "XAxis", "Data", 'MAAxis', 'MAData')
        #A = self.bindata.applyBinning(A, "XAxis", "Data")
        #A = self.metaboanalyst.prepareMetaboAnalyst(A, "BinningX", "Binning", 'MAAxisBinning', 'MADataBinning')
        self.csv.toCSV(A, 'XAxis', 'Data', id, "DataImport", procno)
        #self.csv.toCSV(A, 'MAAxis', 'MAData', id, "DataImportMA", procno)
        #self.csv.toCSV(A, 'MAAxisBinning', 'MADataBinning', id, "BinningMA", procno)

        #self.errormanager.addData("Binning size: " + str(len(A[basedir]["MAAxisBinning"])))

        #B = self.w4m.prepareMetaboAnalyst(A, "XAxis", "Data")

        #name = id + "_" + procno["name"] + "_" + "RawW4M"
        #self.tsv.toTSV(B["DM"], id, "DataImportGADM", procno, name)
        #self.tsv.toTSV(B["SM"], id, "DataImportGASM", procno, name)
        #self.tsv.toTSV(B["VM"], id, "DataImportGAVM", procno, name)

        #path = "media/" + str(id) + "_output" + "/" + str(procno["num"]) + "/" + name
        #shutil.make_archive(path, 'zip', path)
        
        #B = self.w4m.prepareMetaboAnalyst(A, "BinningX", "Binning")

        #name = id + "_" + procno["name"] + "_" + "BinW4M"
        #self.tsv.toTSV(B["DM"], id, "BinningGADM", procno, name)
        #self.tsv.toTSV(B["SM"], id, "BinningGASM", procno, name)
        #self.tsv.toTSV(B["VM"], id, "BinningGAVM", procno, name)

        #path = "media/" + str(id) + "_output" + "/" + str(procno["num"]) + "/" + name
        #shutil.make_archive(path, 'zip', path)

        #self.errormanager.temporal()
        #files = self.dataset.filelist(id, procno["num"])
        #data = self.dataset.filelist2(id, procno["num"])
        #extras = self.dataset.extras(id)


    def test_MTBLS2967(self):
        self.init_all("MTBLS2967")

    def test_MTBLS1357(self):
        self.init_all("MTBLS1357")

    def test_MTBLS981(self):
        self.init_all("MTBLS981")

    def test_MTBLS1497(self):
        self.init_all("MTBLS1497")

    def test_MTBLS1518(self):
        self.init_all("MTBLS1518")

    def test_MTBLS563(self):
        self.init_all("MTBLS563")

    def test_MTBLS798(self):
        self.init_all("MTBLS798")

    def test_MTBLS974(self):
        self.init_all("MTBLS974")

    def test_MTBLS395(self):
        self.init_all("MTBLS395")

    def test_MTBLS470(self):
        self.init_all("MTBLS470")

    def test_MTBLS356(self):
        self.init_all("MTBLS356")

    def test_MTBLS326(self):
        self.init_all("MTBLS326")

    def test_MTBLS249(self):
        self.init_all("MTBLS249")

    def test_MTBLS374(self):
        self.init_all("MTBLS374")

    def test_MTBLS424(self):
        self.init_all("MTBLS424")

    def test_MTBLS242(self):
        self.init_all("MTBLS242")

    def test_MTBLS200(self):
        self.init_all("MTBLS200")

    def test_MTBLS174(self):
        self.init_all("MTBLS174")

    def test_MTBLS172(self):
        self.init_all("MTBLS172")

    #def test_MTBLS540(self):
    #    self.init_all("MTBLS540")

    def test_MTBLS161(self):
        self.init_all("MTBLS161")

    def test_MTBLS103(self):
        self.init_all("MTBLS103")

    def test_MTBLS46(self):
        self.init_all("MTBLS46")

    def test_MTBLS147(self):
        self.init_all("MTBLS147")

    def test_MTBLS678(self):
        self.init_all("MTBLS678")


class FinalTestsMW(TestCase):

    def init_all(self, id):
        self.errormanager = ManageErrors()
        self.dataset = Dataset()
        self.parameters = Parameters(self.errormanager)
        self.importdata = ImportData(self.errormanager)
        self.bindata = Binning(self.errormanager)
        self.csv = CSV(self.errormanager)
        self.tsv = TSV(self.errormanager)
        self.metaboanalyst = MetaboAnalyst(self.errormanager)
        self.w4m = Workflow4Metabolomics(self.errormanager)
        self.others = Others(self.errormanager)

        urlrequested = ""
        self.errormanager.setTitle(id)

        if ( id.find("MTBLS") != -1 ):
            #MTBLS case
            urlrequested = "https://www.ebi.ac.uk/metabolights/" + str(id) + "/files"
            self.loader = Metabolights(self.errormanager)
            self.formatdetect = DetectFormat(self.errormanager)
            self.errormanager.addInfo("Metabolights dataset")
        elif ( id.find("ST") != -1 ):
            #WB case
            urlrequested = "https://www.metabolomicsworkbench.org/studydownload/" + id + ".zip"
            self.loader = MetabolomicsWorkbench(self.errormanager)
            self.formatdetect = MetabolomicsWorkbenchFormat(self.errormanager)
            self.errormanager.addInfo("Metabolomics workbench dataset")
        else:
            print("URL does not exist")
            self.errormanager.addError("ERROR: Id does not belong to any database")
            self.errormanager.temporal()
            print("Id does not belong to any database")
            return {"errors": "Id does not belong to any database"}

        if ( self.loader.checkURL(urlrequested) == False ):
            self.errormanager.addError("ERROR: URL does not exist")
            self.errormanager.temporal()
            print("URL does not exist")
            return {"errors": "URL does not exist"}

        overwrite = "No"
        
        if (self.loader.performWebScrappingURL(id, overwrite) == False):
            self.errormanager.addError("ERROR: Webscrapping error")
            self.errormanager.temporal()
            print("Webscrapping error")
            return {"errors": "Webscrapping error"}

        formatType = self.formatdetect.detectFormat(id)

        if(formatType==1):
            self.formatconvert = Format1(self.errormanager)
        elif(formatType==2):
            self.formatconvert = Format2(self.errormanager)
        elif(formatType==3):
            self.formatconvert = Format3(self.errormanager)
        elif(formatType==4):
            self.formatconvert = Format4(self.errormanager)
        elif(formatType==5):
            self.formatconvert = Format5(self.errormanager)
        elif(formatType==6):
            self.formatconvert = Format6(self.errormanager)
        else:
            self.errormanager.addError("ERROR: Format type does not exist")
            self.errormanager.temporal()
            print("Format type does not exist")
            return {"errors": "Format type does not exist"}

        if ( id.find("ST") != -1 ):
            id = id + "_data"

        if (self.formatconvert.convert("media/" + str(id), overwrite) == False):
            self.errormanager.addError("ERROR: Format convert error")
            self.errormanager.temporal()
            print("Format convert error")
            return {"errors": "Format convert error"}

        if (self.w4m.galaxyDirectory(id) == False):
            self.errormanager.addError("ERROR: Format convert error")
            self.errormanager.temporal()
            print("Format convert error")
            return {"errors": "Format convert error"}

        procnos = self.parameters.readProcno(id)

        print(procnos)

        pulstr = "Valid pulprogs:"
        for pulprog in procnos:
            pulstr = pulstr + " " + pulprog
        self.errormanager.addInfo(pulstr)

        if (len(procnos) == 0):
            self.errormanager.addError("ERROR: No available 1D PULPROG found")
            self.errormanager.temporal()
            procnos = ["No available 1D PULPROG found"]

        links = []
        if (os.path.exists("media/" + id + ".zip") == True):
            links.append(["RawData.zip", "media/" + id + ".zip"])
        if (os.path.exists("media/" + id + "_data.zip") == True):
            links.append(["RawData.zip", "media/" + id + "_data.zip"])
        if (os.path.exists("media/" + id + "_custom.zip") == True):
            links.append(["CustomData.zip", "media/" + id + "_custom.zip"])
        if (os.path.exists("media/" + id + "_galaxy.zip") == True):
            links.append(["W4MData.zip", "media/" + id + "_galaxy.zip"])


        # ----------------  second view ------------------------------------------------
        procnofull = procnos[0]

        print(procnofull)        

        name = procnofull.split(" (", 1)[0]
        num = procnofull.split(" (", 1)[1]
        num = num.split(")", 1)[0]
        
        procno = {}
        procno['num'] = num
        procno['name'] = name

        A = self.importdata.dataImportManager(id, procno)

        if (A["errors"] != "None"):
            return {"errors": {"title": "Missing files", "message": A["errors"]} }
        else:
            A.pop("errors")

        basedir = ""
        for dir in A:
            basedir = dir
            break

        self.errormanager.addData("Chosen pulprog: " + procno['name'])
        self.errormanager.addData("Number of samples: " + str(len(A)))
        self.errormanager.addData("Initial size: " + str(len(A[basedir]["XAxis"])))

        #A = self.metaboanalyst.prepareMetaboAnalyst(A, "XAxis", "Data", 'MAAxis', 'MAData')
        #A = self.bindata.applyBinning(A, "XAxis", "Data")
        #A = self.metaboanalyst.prepareMetaboAnalyst(A, "BinningX", "Binning", 'MAAxisBinning', 'MADataBinning')
        self.csv.toCSV(A, 'XAxis', 'Data', id, "DataImport", procno)
        #self.csv.toCSV(A, 'MAAxis', 'MAData', id, "DataImportMA", procno)
        #self.csv.toCSV(A, 'MAAxisBinning', 'MADataBinning', id, "BinningMA", procno)

        #self.errormanager.addData("Binning size: " + str(len(A[basedir]["MAAxisBinning"])))

        #B = self.w4m.prepareMetaboAnalyst(A, "XAxis", "Data")

        #name = id + "_" + procno["name"] + "_" + "RawW4M"
        #self.tsv.toTSV(B["DM"], id, "DataImportGADM", procno, name)
        #self.tsv.toTSV(B["SM"], id, "DataImportGASM", procno, name)
        #self.tsv.toTSV(B["VM"], id, "DataImportGAVM", procno, name)

        #path = "media/" + str(id) + "_output" + "/" + str(procno["num"]) + "/" + name
        #shutil.make_archive(path, 'zip', path)
        
        #B = self.w4m.prepareMetaboAnalyst(A, "BinningX", "Binning")

        #name = id + "_" + procno["name"] + "_" + "BinW4M"
        #self.tsv.toTSV(B["DM"], id, "BinningGADM", procno, name)
        #self.tsv.toTSV(B["SM"], id, "BinningGASM", procno, name)
        #self.tsv.toTSV(B["VM"], id, "BinningGAVM", procno, name)

        #path = "media/" + str(id) + "_output" + "/" + str(procno["num"]) + "/" + name
        #shutil.make_archive(path, 'zip', path)

        #self.errormanager.temporal()
        #files = self.dataset.filelist(id, procno["num"])
        #data = self.dataset.filelist2(id, procno["num"])
        #extras = self.dataset.extras(id)

    def test_ST000020(self):
        self.init_all("ST000020")

    def test_ST000022(self):
        self.init_all("ST000022")

    def test_ST000050(self):
        self.init_all("ST000050")

    def test_ST000051(self):
        self.init_all("ST000051")

    def test_ST000104(self):
        self.init_all("ST000104")

    def test_ST000223(self):
        self.init_all("ST000223")

    def test_ST000256(self):
        self.init_all("ST000256")

    def test_ST000306(self):
        self.init_all("ST000306")

    def test_ST000315(self):
        self.init_all("ST000315")

    def test_ST000364(self):
        self.init_all("ST000364")

    def test_ST000366(self):
        self.init_all("ST000366")

    def test_ST000438(self):
        self.init_all("ST000438")

    def test_ST000439(self):
        self.init_all("ST000439")

    def test_ST000407(self):
        self.init_all("ST000407")

    def test_ST000440(self):
        self.init_all("ST000440")

    def test_ST000442(self):
        self.init_all("ST000442")

    def test_ST000454(self):
        self.init_all("ST000454")

    def test_ST000455(self):
        self.init_all("ST000455")

    def test_ST000464(self):
        self.init_all("ST000464")

    def test_ST000605(self):
        self.init_all("ST000605")

    def test_ST000785(self):
        self.init_all("ST000785")

    def test_ST000826(self):
        self.init_all("ST000826")

    def test_ST000891(self):
        self.init_all("ST000891")

    def test_ST000892(self):
        self.init_all("ST000892")

    def test_ST000939(self):
        self.init_all("ST000939")

    def test_ST001038(self):
        self.init_all("ST001038")

    def test_ST001054(self):
        self.init_all("ST001054")

    def test_ST001129(self):
        self.init_all("ST001129")

    def test_ST001138(self):
        self.init_all("ST001138")

    def test_ST001139(self):
        self.init_all("ST001139")

    def test_ST001284(self):
        self.init_all("ST001284")

    def test_ST001294(self):
        self.init_all("ST001294")

    def test_ST001295(self):
        self.init_all("ST001295")

    def test_ST001319(self):
        self.init_all("ST001319")

    def test_ST001354(self):
        self.init_all("ST001354")

    def test_ST001375(self):
        self.init_all("ST001375")

    def test_ST001476(self):
        self.init_all("ST001476")

    def test_ST001615(self):
        self.init_all("ST001615")

    def test_ST001616(self):
        self.init_all("ST001616")

    def test_ST001706(self):
        self.init_all("ST001706")

    def test_ST001813(self):
        self.init_all("ST001813")


class ClometToolTests(TestCase):

    def test_aWebScrapping(self):

        self.errorManager = ManageErrors()

        pdfpath = "media/testaWS.pdf"
        self.errorManager.createPDF(pdfpath)

        self.loader = Metabolights(self.errorManager)

        url = "MTBLS46"
        overwrite = "No"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)

        url = "MTBLS326"
        overwrite = "Yes"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        
        url = "MTBLS678"
        overwrite = "Yes"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)

        url = "MTBLS46C"
        overwrite = "No"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)

        url = "MTBLS470"
        overwrite = "No"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)

        url = "MTBLS174"
        overwrite = "No"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)

        url = "MTBLS374"
        overwrite = "No"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)

        url = "MTBLS1497"
        overwrite = "No"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)

        self.loader = MetabolomicsWorkbench(self.errorManager)

        id = "ST000050"
        overwrite = "No"
        self.assertIs(self.loader.performWebScrappingURL(id, overwrite), True)

        id = "ST000315"
        overwrite = "Yes"
        self.assertIs(self.loader.performWebScrappingURL(id, overwrite), True)

    def test_bDetectFormat(self):

        self.errorManager = ManageErrors()
        pdfpath = "media/testbDF.pdf"
        self.errorManager.createPDF(pdfpath)

        self.formatdetect = DetectFormat(self.errorManager)

        id = "MTBLS46"
        self.assertIs(self.formatdetect.detectFormat(id), 1)

        id = "MTBLS470"
        self.assertIs(self.formatdetect.detectFormat(id), 2)

        id = "MTBLS174"
        self.assertIs(self.formatdetect.detectFormat(id), 3)

        id = "MTBLS374"
        self.assertIs(self.formatdetect.detectFormat(id), 3)

        id = "MTBLS326"
        self.assertIs(self.formatdetect.detectFormat(id), 4)

        id = "MTBLS46C"
        self.assertIs(self.formatdetect.detectFormat(id), 5)

        id = "MTBLS678"
        self.assertIs(self.formatdetect.detectFormat(id), 6)

        id = "MTBLS1497"
        self.assertIs(self.formatdetect.detectFormat(id), 7)

        self.formatdetect = MetabolomicsWorkbenchFormat(self.errorManager)

        id = "ST000050"
        self.assertIs(self.formatdetect.detectFormat(id), 3)

        id = "ST000315"
        self.assertIs(self.formatdetect.detectFormat(id), 3)

    def test_cConvertFormat(self):

        self.errorManager = ManageErrors()
        pdfpath = "media/testcCF.pdf"
        self.errorManager.createPDF(pdfpath)

        self.formatconvert = Format1(self.errorManager)
        id = "MTBLS46"
        overwrite = "No"
        self.assertIs(self.formatconvert.convert("media/" + id, overwrite), True)

        self.formatconvert = Format2(self.errorManager)
        id = "MTBLS470"
        overwrite = "Yes"
        self.assertIs(self.formatconvert.convert("media/" + id, overwrite), True)

        self.formatconvert = Format3(self.errorManager)
        id = "MTBLS174"
        overwrite = "No"
        self.assertIs(self.formatconvert.convert("media/" + id, overwrite), True)

        self.formatconvert = Format3(self.errorManager)
        id = "MTBLS374"
        overwrite = "Yes"
        self.assertIs(self.formatconvert.convert("media/" + id, overwrite), True)

        self.formatconvert = Format4(self.errorManager)
        id = "MTBLS326"
        overwrite = "Yes"
        self.assertIs(self.formatconvert.convert("media/" + id, overwrite), True)

        self.formatconvert = Format5(self.errorManager)
        id = "MTBLS46C"
        overwrite = "No"
        self.assertIs(self.formatconvert.convert("media/" + id, overwrite), True)

        self.formatconvert = Format3(self.errorManager)
        id = "MTBLS678"
        overwrite = "No"
        self.assertIs(self.formatconvert.convert("media/" + id, overwrite), True)

        self.formatconvert = Format3(self.errorManager)
        id = "ST000050"
        overwrite = "Yes"
        self.assertIs(self.formatconvert.convert("media/" + id, overwrite), True)

        self.formatconvert = Format6(self.errorManager)
        id = "ST000315"
        overwrite = "No"
        self.assertIs(self.formatconvert.convert("media/" + id, overwrite), True)

    def test_dW4MDirectory(self):

        self.errorManager = ManageErrors()
        pdfpath = "media/testdW4M.pdf"
        self.errorManager.createPDF(pdfpath)

        self.w4m = Workflow4Metabolomics(self.errorManager)
        id="MTBLS326"
        self.assertIs(self.w4m.galaxyDirectory(id), True)

    def test_eReadProcno(self):

        self.errorManager = ManageErrors()
        pdfpath = "media/testeRP.pdf"
        self.errorManager.createPDF(pdfpath)
        self.parameters = Parameters(self.errorManager)

        id="MTBLS326"
        self.assertEqual(self.parameters.readProcno(id), ['cpmgpr1d (1)'])

        id = "MTBLS678"
        self.assertEqual(self.parameters.readProcno(id), ['noesypr1d (11)'])

        id = "MTBLS470"
        self.assertEqual(self.parameters.readProcno(id), ['noesygppr1d (1)'])

        id = "ST000050_data"
        self.assertEqual(self.parameters.readProcno(id), ['noesypr1d (1)'])

    def test_fImportData(self):

        self.errorManager = ManageErrors()
        pdfpath = "media/testfID.pdf"
        self.errorManager.createPDF(pdfpath)
        self.importdata = ImportData(self.errorManager)

        id="MTBLS326"
        procno = {}
        procno["name"] = "cpmgpr1d"
        procno["num"] = "1"
        self.assertIsNotNone(self.importdata.dataImportManager(id, procno))

        id = "MTBLS678"
        procno = {}
        procno["name"] = "noesypr1d"
        procno["num"] = "11"
        self.assertIsNotNone(self.importdata.dataImportManager(id, procno), not None)

        id = "MTBLS470"
        procno = {}
        procno["name"] = "noesygppr1d"
        procno["num"] = "1"
        self.assertIsNotNone(self.importdata.dataImportManager(id, procno), not None)

        id = "ST000050"
        procno = {}
        procno["name"] = "noesypr1d"
        procno["num"] = "1"
        self.assertIsNotNone(self.importdata.dataImportManager(id, procno), not None)

    def test_gWebScrapping(self):
        self.errorManager = ManageErrors()

        pdfpath = "media/testgWS.pdf"
        self.errorManager.createPDF(pdfpath)

        self.loader = MetabolomicsWorkbench(self.errorManager)

        overwrite = "No"

        url = "ST000020"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000022"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000050"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000051"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000104"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000223"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000256"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000306"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000315"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000364"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)

        url = "ST000366"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000438"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000439"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000407"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000440"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000442"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000454"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000455"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000464"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000605"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000785"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)

        url = "ST000826"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000891"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000892"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST000939"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001038"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001129"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001138"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001139"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001284"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001294"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)

        url = "ST001319"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001354"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001375"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001476"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001615"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001616"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001706"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)
        url = "ST001813"
        self.assertIs(self.loader.performWebScrappingURL(url, overwrite), True)

    def test_hGraph(self):
        self.errorManager = ManageErrors()

        self.errorManager.test()

    def test_iDetectFormat(self):   
        self.errorManager = ManageErrors()
        pdfpath = "media/testbDF.pdf"
        self.errorManager.createPDF(pdfpath)

        self.formatdetect = MetabolomicsWorkbenchFormat(self.errorManager)

        overwrite = "Yes"

        url = "ST000020"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000022"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000050"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000051"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000104"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000223"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000256"
        print( url + ": " + str(self.formatdetect.detectFormat(url)) )      # False
        url = "ST000306"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000315"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000364"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)

        url = "ST000366"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000438"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000439"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000407"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000440"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000442"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000454"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000455"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000464"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000605"
        print( url + ": " + str(self.formatdetect.detectFormat(url)) )      # False
        url = "ST000785"
        print( url + ": " + str(self.formatdetect.detectFormat(url)) )      # False

        url = "ST000826"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000891"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000892"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST000939"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST001038"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST001129"
        print( url + ": " + str(self.formatdetect.detectFormat(url)) )      # False
        url = "ST001138"
        print( url + ": " + str(self.formatdetect.detectFormat(url)) )      # False
        url = "ST001139"
        print( url + ": " + str(self.formatdetect.detectFormat(url)) )      # False
        url = "ST001284"
        print( url + ": " + str(self.formatdetect.detectFormat(url)) )      # False
        url = "ST001294"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)

        url = "ST001319"
        print( url + ": " + str(self.formatdetect.detectFormat(url)) )      # False
        url = "ST001354"
        print( url + ": " + str(self.formatdetect.detectFormat(url)) )      # False
        url = "ST001375"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST001476"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST001615"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST001616"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST001706"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        url = "ST001813"
        formatType = self.formatdetect.detectFormat(url)
        self.createFormat(formatType)
        self.assertIs(self.formatconvert.convert("media/" + url + "_data", overwrite), True)
        print( url + ": " + str(self.formatdetect.detectFormat(url)) )

    def createFormat(self, formatType):
        if(formatType==1):
            self.formatconvert = Format1(self.errorManager)
        elif(formatType==2):
            self.formatconvert = Format2(self.errorManager)
        elif(formatType==3):
            self.formatconvert = Format3(self.errorManager)
        elif(formatType==4):
            self.formatconvert = Format4(self.errorManager)
        elif(formatType==5):
            self.formatconvert = Format5(self.errorManager)
        elif(formatType==6):
            self.formatconvert = Format6(self.errorManager)
        else:
            print("Format type " + str(formatType))
            self.errorManager.addDataToPDF("ERROR: Format type does not exist")
            return {"errors": "Format type does not exist"}

    def test_jProcnos(self):
        self.errorManager = ManageErrors()
        pdfpath = "media/testeRP.pdf"
        self.errorManager.createPDF(pdfpath)
        self.parameters = Parameters(self.errorManager)

        url = "ST000020_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000022_data"    
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000050_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000051_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000104_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000223_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000256_data"
        print(url + ": ")
        #print(self.parameters.readProcno(url))
        url = "ST000306_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000315_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000364_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))

        url = "ST000366_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000438_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000439_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000407_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000440_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000442_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000454_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000455_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000464_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000605_data"
        print(url + ": ")
        #print(self.parameters.readProcno(url))
        url = "ST000785_data"
        print(url + ": ")
        #print(self.parameters.readProcno(url))

        url = "ST000826_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000891_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000892_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST000939_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST001038_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST001129_data"
        print(url + ": ")
        #print(self.parameters.readProcno(url))
        url = "ST001138_data"
        print(url + ": ")
        #print(self.parameters.readProcno(url))
        url = "ST001139_data"
        print(url + ": ")
        #print(self.parameters.readProcno(url))
        url = "ST001284_data"
        print(url + ": ")
        #print(self.parameters.readProcno(url))
        url = "ST001294_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))

        url = "ST001319_data"
        print(url + ": ")
        #print(self.parameters.readProcno(url))
        url = "ST001354_data"
        print(url + ": ")
        #print(self.parameters.readProcno(url))
        url = "ST001375_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST001476_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST001615_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST001616_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST001706_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
        url = "ST001813_data"
        print(url + ": ")
        print(self.parameters.readProcno(url))
