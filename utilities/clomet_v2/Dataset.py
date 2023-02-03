import os
from posixpath import split
import shutil

from utilities.clomet_v2.ImportData import ImportData
from utilities.clomet_v2.DetectFormat import DetectFormat, MetabolomicsWorkbenchFormat
from utilities.clomet_v2.LoadDataset import LocalUpload, Metabolights, MetabolomicsWorkbench
from utilities.clomet_v2.ManageErrors import ManageErrors
from utilities.clomet_v2.Others import Others
from utilities.clomet_v2.Parameters import Parameters
from utilities.clomet_v2.ConvertFormat import Format1, Format2, Format3, Format4, Format5, Format6
from utilities.clomet_v2.PrepareData import Workflow4Metabolomics, MetaboAnalyst
from utilities.clomet_v2.ReduceData import Binning
from utilities.clomet_v2.ConvertOutput import CSV,TSV

class Dataset:

    def __init__(self):
        self.errormanager = ManageErrors()
        self.parameters = Parameters(self.errormanager)
        self.importdata = ImportData(self.errormanager)
        self.bindata = Binning(self.errormanager)
        self.csv = CSV(self.errormanager)
        self.tsv = TSV(self.errormanager)
        self.metaboanalyst = MetaboAnalyst(self.errormanager)
        self.w4m = Workflow4Metabolomics(self.errormanager)
        self.others = Others(self.errormanager)

    """
    First CloMet view, where the ID is inserted.
    """
    def firstView(self, id):

        urlrequested = ""
        #pdfpath = "media/" + id + ".pdf"

        #self.errormanager.createPDF(pdfpath)
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
            print("ID format does not belong to MetaboLights or Metabolomics Workbench.")
            self.errormanager.addError("ERROR: Id does not belong to any database")
            self.errormanager.temporal()
            return {"errors": {"title": "Wrong ID", "message": "ID format does not belong to MetaboLights or Metabolomics Workbench."} }

        if ( self.loader.checkURL(urlrequested) == False ):
            self.errormanager.addError("ERROR: URL does not exist")
            self.errormanager.temporal()
            return {"errors": {"title": "Wrong URL", "message": "URL belonging to this study does not exist. Please, check the ID."} }

        overwrite = "No"
        
        if (self.loader.performWebScrappingURL(id, overwrite) == False):
            self.errormanager.addError("ERROR: Webscrapping error")
            self.errormanager.temporal()
            return {"errors": {"title": "Webscrapping error", "message": "Could not connect to on-line data repository."} }

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
            print("ERROR: Format type is not supported by CloMet")
            self.errormanager.addError("ERROR: Format type does not exist")
            self.errormanager.temporal()
            return {"errors": {"title": "Format error", "message": "Data format type is not supported by CloMet."} }

        if ( id.find("ST") != -1 ):
            id = id + "_data"

        if (self.formatconvert.convert("media/" + str(id), overwrite) == False):
            self.errormanager.addError("ERROR: Format convert error")
            self.errormanager.temporal()
            return {"errors": {"title": "Conversion error", "message": "An error ocurring while converting the data set. Please, retry."} }

        if (self.w4m.galaxyDirectory(id) == False):
            self.errormanager.addError("ERROR: Format convert error")
            self.errormanager.temporal()
            return {"errors": {"title": "Conversion error", "message": "An error ocurring while converting the data set. Please, retry."} }

        procnos = self.parameters.readProcno(id)

        pulstr = "Valid pulprogs:"
        for pulprog in procnos:
            pulstr = pulstr + " " + pulprog
        self.errormanager.addInfo(pulstr)

        if (len(procnos) == 0):
            self.errormanager.addError("ERROR: No available 1D PULPROG found")
            self.errormanager.temporal()
            procnos = ["No available 1D PULPROG found"]
            return {"errors": {"title": "Invalid PULPROG", "message": "No available 1D PULPROG found."} }

        links = []
        if (os.path.exists("media/" + id + ".zip") == True):
            links.append(["RawData.zip", "media/" + id + ".zip"])
        if (os.path.exists("media/" + id + "_data.zip") == True):
            links.append(["RawData.zip", "media/" + id + "_data.zip"])
        if (os.path.exists("media/" + id + "_custom.zip") == True):
            links.append(["CustomData.zip", "media/" + id + "_custom.zip"])
        if (os.path.exists("media/" + id + "_galaxy.zip") == True):
            links.append(["W4MData.zip", "media/" + id + "_galaxy.zip"])

        return {"errors": {"title": "No", "message": "No"}, "links": links, "procnos": procnos}

    """
    First Local view, where the study is uploaded.
    """
    def firstViewLocal(self, id):

        self.loader = LocalUpload(self.errormanager)
        self.formatdetect = MetabolomicsWorkbenchFormat(self.errormanager)

        sid = str(id)
        sid = sid.replace(' ', '_')

        with open("media/" + sid, 'wb+') as destination:
            for chunk in id.chunks():
                destination.write(chunk)

        format = sid.split(".", 1) [1]
        sid = sid.split(".", 1)[0]

        if (format.find("zip") == -1):
            self.errormanager.addError("ERROR: Webscrapping format error")
            self.errormanager.temporal()
            return {"errors": {"title": "Upload format error", "message": "Please upload data in a zip format."} }

        overwrite = "Yes"

        if (self.loader.performWebScrappingURL(sid, overwrite) == False):
            self.errormanager.addError("ERROR: Webscrapping function error")
            self.errormanager.temporal()
            return {"errors": {"title": "Upload error", "message": "Error while uploading the data. Please, retry."} }

        formatType = self.formatdetect.detectFormat(sid)

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
            return {"errors": {"title": "Format error", "message": "Data format type is not supported by CloMet."} }


        if (self.formatconvert.convert("media/" + str(sid) + "_data", overwrite) == False):
            self.errormanager.addError("ERROR: Format convert error")
            self.errormanager.temporal()
            return {"errors": {"title": "Conversion error", "message": "An error ocurring while converting the data set. Please, retry."} }

        if (self.w4m.galaxyDirectory( str(sid) + "_data" ) == False):
            self.errormanager.addError("ERROR: Format convert error")
            self.errormanager.temporal()
            return {"errors": {"title": "Conversion error", "message": "An error ocurring while converting the data set. Please, retry."} }

        procnos = self.parameters.readProcno( str(sid) + "_data" )

        pulstr = "Valid pulprogs:"
        for pulprog in procnos:
            pulstr = pulstr + " " + pulprog
        self.errormanager.addInfo(pulstr)

        if (len(procnos) == 0):
            self.errormanager.addError("ERROR: No available 1D PULPROG found")
            self.errormanager.temporal()
            procnos = ["No available 1D PULPROG found"]
            return {"errors": {"title": "Invalid PULPROG", "message": "No available 1D PULPROG found."} }
        links = []
        if (os.path.exists("media/" + sid + ".zip") == True):
            links.append(["FullData.zip", "media/" + sid + ".zip"])
        if (os.path.exists("media/" + sid + "_data.zip") == True):
            links.append(["RawData.zip", "media/" + sid + "_data.zip"])
        if (os.path.exists("media/" + sid + "_custom.zip") == True):
            links.append(["CustomData.zip", "media/" + sid + "_custom.zip"])
        if (os.path.exists("media/" + sid + "_galaxy.zip") == True):
            links.append(["W4MData.zip", "media/" + sid + "_galaxy.zip"])

        return {"errors": {"title": "No", "message": "No"}, "links": links, "procnos": procnos}

    """
    Second CloMet and Local view, where data is extracted, transformed, and the output is obtained and shown.
    """
    def secondView(self, procnofull, id):
        name = procnofull.split(" (", 1)[0]
        num = procnofull.split(" (", 1)[1]
        num = num.split(")", 1)[0]
        
        procno = {}
        procno['num'] = num
        procno['name'] = name

        id = id.replace(' ', '_')

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
        print("*****************************ESTER HERE")
        A = self.metaboanalyst.prepareMetaboAnalyst(A, "XAxis", "Data", 'MAAxis', 'MAData')

        A = self.bindata.applyBinning(A, "XAxis", "Data")
        if A == False:
            return {"errors": {"title": "Bining error", "message": "Error ocurred while applying binning."} }

        A = self.metaboanalyst.prepareMetaboAnalyst(A, "BinningX", "Binning", 'MAAxisBinning', 'MADataBinning')
        self.csv.toCSV(A, 'XAxis', 'Data', id, "DataImport", procno)
        self.csv.toCSV(A, 'MAAxis', 'MAData', id, "DataImportMA", procno)
        self.csv.toCSV(A, 'MAAxisBinning', 'MADataBinning', id, "BinningMA", procno)

        self.errormanager.addData("Binning size: " + str(len(A[basedir]["MAAxisBinning"])))

        B = self.w4m.prepareMetaboAnalyst(A, "XAxis", "Data")

        name = id + "_" + procno["name"] + "_" + "RawW4M"
        self.tsv.toTSV(B["DM"], id, "DataImportGADM", procno, name)
        self.tsv.toTSV(B["SM"], id, "DataImportGASM", procno, name)
        self.tsv.toTSV(B["VM"], id, "DataImportGAVM", procno, name)

        path = "media/" + str(id) + "_output" + "/" + str(procno["num"]) + "/" + name
        shutil.make_archive(path, 'zip', path)
        B = self.w4m.prepareMetaboAnalyst(A, "BinningX", "Binning")

        name = id + "_" + procno["name"] + "_" + "BinW4M"
        self.tsv.toTSV(B["DM"], id, "BinningGADM", procno, name)
        self.tsv.toTSV(B["SM"], id, "BinningGASM", procno, name)
        self.tsv.toTSV(B["VM"], id, "BinningGAVM", procno, name)

        path = "media/" + str(id) + "_output" + "/" + str(procno["num"]) + "/" + name
        shutil.make_archive(path, 'zip', path)

        self.errormanager.temporal()
        files = self.filelist(id, procno["num"])
        data = self.filelist2(id, procno["num"])
        extras = self.extras(id)

        return {"files": files, "data": data, "extras": extras, "errors": {"title": "No", "message": "No"}}

    """
    About view.
    """
    def about(self):
        return

    """
    Tutorials view.
    """
    def tutorials(self):
        datasets = self.others.localDatasets()
        rawdata = self.others.localRawData()
        mas = self.others.localMA()
        w4ms = self.others.localW4M()
        return{"datasets": datasets, "rawdata": rawdata, "mas": mas, "w4ms": w4ms}

    """
    List of files needed for the second view page.
    """
    def filelist(self, id, procno):
        files = [[1,2,3],[1, 2, 3],[1,2,3],[1]]
        path = "media/" + str(id) + "_output/" + str(procno)
        dirlist = os.listdir(path)

        for dir in dirlist:

            if ( dir.find("DataImport.csv") != -1 ):
                files[0][0] = ("RawData.csv", path + "/" + dir)
            elif ( dir.find("DataImportMA.csv") != -1 ):
                files[0][1] = ("RawDataMA.csv", path + "/" + dir)
            elif ( dir.find("BinningMA.csv") != -1 ):
                files[0][2] = ("BinningMA.csv", path + "/" + dir)

            elif ( dir.find("DataImportGADM.tabular") != -1 ):
                files[1][0] = ("DataMatrix.tab", path + "/" + dir) 
            elif ( dir.find("DataImportGASM.tabular") != -1 ):
                files[1][1] = ("SampleMeta.tab", path + "/" + dir)
            elif ( dir.find("DataImportGAVM.tabular") != -1 ):
                files[1][2] = ("VariableMeta.tab", path + "/" + dir) 

            elif ( dir.find("BinningGADM.tabular") != -1 ):
                files[2][0] = ("DataMatrixBin.tab", path + "/" + dir)
            elif ( dir.find("BinningGASM.tabular") != -1 ):
                files[2][1] = ("SampleMetaBin.tab", path + "/" + dir)
            elif ( dir.find("BinningGAVM.tabular") != -1 ):
                files[2][2] = ("VariableMetaBin.tab", path + "/" + dir)

        files[3][0] = ("Report.pdf", "media/Report.pdf")

        return files

    """
    List of files needed for the second view page.
    """
    def filelist2(self, id, procno):
        files = [1,2,3,4]
        path = "media/" + str(id) + "_output/" + str(procno)
        dirlist = os.listdir(path)

        for dir in dirlist:

            if ( dir.find("DataImportMA.csv") != -1 ):
                files[0] = ( id + "RawMA.csv", path + "/" + dir)
            elif ( dir.find("BinningMA.csv") != -1 ):
                files[1] = ( id + "BinMA.csv", path + "/" + dir)
            elif ( dir.find("RawW4M.zip") != -1 ):
                files[2] = ( id + "RawW4M.zip", path + "/" + dir)
            elif ( dir.find("BinW4M.zip") != -1 ):
                files[3] = ( id + "BinW4M.zip", path + "/" + dir)

        return files

    """
    List of files needed for the second view page.
    """
    def extras(self, id):

        links = []
        if (os.path.exists("media/" + id + ".zip") == True):
            links.append(["RawData.zip", "media/" + id + ".zip"])
        if (os.path.exists("media/" + id + "_data.zip") == True):
            links.append(["RawData.zip", "media/" + id + "_data.zip"])
        if (os.path.exists("media/" + id + "_custom.zip") == True):
            links.append(["CustomData.zip", "media/" + id + "_custom.zip"])
        if (os.path.exists("media/" + id + "_galaxy.zip") == True):
            links.append(["W4MData.zip", "media/" + id + "_galaxy.zip"])

        return links