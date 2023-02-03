
import os
import shutil
import time
import requests
import urllib.request
import patoolib
import py7zr
from tqdm import tqdm

from abc import abstractmethod
from shutil import rmtree
from bs4 import BeautifulSoup
from zipfile import ZipFile
from os import chdir
from pyunpack import Archive
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.error import HTTPError, URLError

from utilities.clomet_v2.ManageErrors import ManageErrors

class LoadDataset:

    def __init__(self, errorManager: ManageErrors):
        self.errormanager = errorManager

    """
    Checks if a URL exists.
    """
    def checkURL(self, url):
        try:
            urllib.request.urlopen(url)
        except HTTPError as e:
            self.errormanager.addError("ERROR: The inserted url does not exist")
            return False
        except URLError as e:
            self.errormanager.addError("ERROR: The inserted url does not exist")
            return False
        return True

    """
    Performs web scrapping techniques on a particular URL.
    """
    @abstractmethod
    def performWebScrappingURL(self, obtainedURL, overwrite):
        pass

class Metabolights(LoadDataset):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Performs web scrapping techniques on a particular MTBLS URL.
    """
    def performWebScrappingURL(self, id, overwrite):
        
        obtainedURL = "https://www.ebi.ac.uk/metabolights/" + str(id) + "/files"
        
        mediaurl = "media/" + id + "/"
        
        if (os.path.exists(mediaurl) == True and overwrite == "Yes"):
            rmtree(mediaurl)
            if (os.path.exists("media/" + id + ".zip") == True):
                os.remove("media/" + id + ".zip")
        elif (os.path.exists(mediaurl) == True and overwrite == "No"):
            if (os.path.exists("media/" + id + ".zip") == False):
                shutil.make_archive("media/" + id, 'zip', "media/" + id)
            return True
        #else means that checkdir is false, therefore download

        tries = 0
        sleepTime = 4
        links = []
        while (tries < 5 and len(links)<=0):

            #print("Chrome setup")

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

            prefs = {"download.default_directory" : "archivos_comprimidos"}
            chrome_options.add_experimental_option("prefs",prefs)

            d = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
            d.get('https://www.google.nl/')

            e = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
            e.get('https://www.google.nl/')

            f = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
            f.get('https://www.google.nl/')

            #print("Get MTBLS files")

            d.get(obtainedURL)

            #print("Get html content")
            time.sleep(sleepTime)
            html_source = d.page_source
            soup = BeautifulSoup(html_source,'lxml')

            # Create list of links of all the links of the dataset (ending in .zip or .rar)

            #print("Create link list")
            
            for a in soup.find_all('a', href=True):
                #if (a['href'].find('/download/')!=-1 and a['href'].find(' ')==-1):
                if (a['href'].find('/download/')!=-1):

                    convert = a['href']
                    convert = convert.replace(" ", "%20")
                    links.append(convert)

            if ( len(links) <= 0 ):
                self.errormanager.addError("ERROR: No links available on the web")
                print("ERROR: No links available")
                tries = tries + 1
                sleepTime = sleepTime * 2

        if tries >= 5 and len(links) <= 0:
            return False
        
        try:
            os.mkdir(mediaurl)
        except OSError:
            self.errormanager.addError("ERROR: Creation of the directory %s failed" % mediaurl)
            print ("Creation of the directory %s failed" % mediaurl)

        print("--------------- DOWNLOAD -------------------------")

        for downloadurl in tqdm(links):    
            folder =  downloadurl.split("file=", 1)[1]


            if ( folder.find('.') == -1 ):        # It is a folder
                #print("No download: " + mediaurl + folder)
                pass
            else:
                if (self.checkURL(downloadurl) == True):

                    time.sleep(0)

                    zip_file = requests.get(downloadurl, stream=True).content

                    count = 0
                    while ( os.path.exists(mediaurl + folder) == False and count < 4):
                        try:
                            with open(mediaurl + folder, 'wb') as out_file:
                                out_file.write(zip_file)
                            time.sleep(1)
                        except Exception as error:
                            count = count + 1
                            print( "EXCEPTION " + id + ": {" + os.getcwd() + "}/" + mediaurl + folder )
                            time.sleep(3)

                    time.sleep(0)
                
        print("------------------ END DOWNLOAD -----------------------")
        print("Please wait...")
        #time.sleep(30)
        time.sleep(3)
        print("Waiting done.")


        dirs = os.listdir(mediaurl)
        for folder in dirs:

            if ( folder.find('.zip') != -1 ):
                while ( os.path.isdir(mediaurl + folder) == False and os.path.isfile(mediaurl + folder) == False):
                    print("Zip wait " + folder)
                    time.sleep(3)

                ufolder = folder.split(".zi", 1)[0]

                with ZipFile(mediaurl + folder, 'r') as zipObj:
                    zipObj.extractall(mediaurl + ufolder)

                if (os.path.exists( mediaurl + folder ) ):
                    os.remove(mediaurl + folder)
                else:
                    self.errormanager.addError("ERROR: The folder %s doesn't exist" % (mediaurl + folder))
                    print ("The folder %s doesn't exist" % (mediaurl + folder) )
                    
            elif (folder.find('.rar') != -1):
                while ( os.path.isdir(mediaurl + folder) == False and os.path.isfile(mediaurl + folder) == False):
                    print("RAR wait " + folder)
                    time.sleep(3)

                ufolder = folder.split(".ra", 1)[0]
                patoolib.extract_archive(mediaurl + folder, outdir=mediaurl)
                if (os.path.exists( mediaurl + folder ) ):
                    os.remove(mediaurl + folder)
                else:
                    self.errormanager.addError("ERROR: The folder %s doesn't exist" % (mediaurl + folder))
                    print ("The folder %s doesn't exist" % (mediaurl + folder) )
        
        if (os.path.exists("media/" + id) == True and os.path.exists("media/" + id + ".zip") == False):
            shutil.make_archive("media/" + id, 'zip', "media/" + id)

        return True

class MetabolomicsWorkbench(LoadDataset):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Performs web scrapping techniques on a particular MW URL.
    """
    def performWebScrappingURL(self, id, overwrite):

        mediaurl = "media/" + id
        
        if (os.path.exists(mediaurl) == True and overwrite == "Yes"):
            rmtree(mediaurl)
            if (os.path.exists("media/" + id + ".zip") == True):
                os.remove("media/" + id + ".zip")
        elif (os.path.exists(mediaurl) == True and overwrite == "No"):
            if (os.path.exists("media/" + id + ".zip") == False):
                shutil.make_archive("media/" + id, 'zip', "media/" + id)
            return True
        #else means that checkdir is false, therefore download

        obtainedURL = self.obtainURL(id)
        #obtainedURL = "https://www.metabolomicsworkbench.org/studydownload/" + id + ".zip"
        
        print (obtainedURL)
        
        if (self.checkURL(obtainedURL) == True):

            print("--------------- DOWNLOAD -------------------------")

            zip_file = requests.get(obtainedURL, stream=True).content
            #print("EndGet")

            try:
                if (obtainedURL.find(".zi")!=-1):
                    with open(mediaurl + ".zip", 'wb') as out_file:
                        out_file.write(zip_file)
                elif (obtainedURL.find(".7z")!=-1):
                    with open(mediaurl + ".7z", 'wb') as out_file:
                        out_file.write(zip_file)
                time.sleep(1)
                #print("EndZip")
            except Exception as error:
                print( "EXCEPTION " + id + ": {" + os.getcwd() + "}/" + mediaurl )
                print(error)
                time.sleep(3)
                return False

            try:
                os.mkdir(mediaurl)
            except OSError:
                #addErrorReport("The directory " + mediaurl + "could not be created.")
                self.errormanager.addError("ERROR: Creation of the directory %s failed" % mediaurl)
                print ("Creation of the directory %s failed" % mediaurl)
                return False
                    
            print("------------------ END DOWNLOAD -----------------------")

            time.sleep(30)

            if (obtainedURL.find(".zi")!=-1):
                with ZipFile(mediaurl + ".zip", 'r') as zipObj:
                    zipObj.extractall(mediaurl)

            elif (obtainedURL.find(".7z")!=-1):

                archive = py7zr.SevenZipFile(mediaurl + ".7z", mode='r')
                archive.extractall(path=(mediaurl))
                archive.close()

            print("StartUnzip")
            self.unzipall(mediaurl)

            return True

        return False

    def unzipall(self, url):

        dirs = os.listdir(url)
        for dir in dirs:
            urldir = url + "/" + dir
            if ( dir.find('.zip') != -1 ):
                ufolder = dir.split(".zi", 1)[0]
                print("urldir zip: " + urldir)
                print("urldir: " + url + "/" + ufolder)

                with ZipFile(urldir, 'r') as zipObj:
                    zipObj.extractall(url + "/" + ufolder)

                if (os.path.exists( urldir ) ):
                    os.remove(urldir)
                else:
                    self.errormanager.addError("ERROR: The folder %s doesn't exist" % (urldir))
                    print ("The folder %s doesn't exist" % (urldir) )

                self.unzipall(url + "/" + ufolder)
            elif ( dir.find('.7z') != -1 ):
                ufolder = dir.split(".7z", 1)[0]

                try:
                    os.mkdir(url + "/" + ufolder)
                except OSError:
                    self.errormanager.addError("ERROR: Creation of the directory %s failed" % (url + "/" + ufolder))
                    print ("Creation of the directory %s failed" % (url + "/" + ufolder))

                # Archive(urldir).extractall(url + "/" + ufolder)

                archive = py7zr.SevenZipFile(urldir, mode='r')
                archive.extractall(path=(url + "/" + ufolder))
                archive.close()

                #with py7zr.SevenZipFile("Archive.7z", 'r') as archive:
                #    archive.extractall(path="/tmp")

                if (os.path.exists( urldir ) ):
                    os.remove(urldir)
                else:
                    self.errormanager.addError("ERROR: The folder %s doesn't exist" % (urldir))
                    print ("The folder %s doesn't exist" % (urldir) )

                self.unzipall(url + "/" + ufolder)
            elif (os.path.isdir(urldir) and urldir.lower().find("mac")==-1):
                self.unzipall(urldir)
        
        return True

    def obtainURL(self, id):

        auxURL = "https://www.metabolomicsworkbench.org/data/DRCCStudySummary.php?Mode=SetupRawDataDownload&StudyID=" + id

        if (self.checkURL(auxURL) == True):

            zip_file = requests.get(auxURL, stream=True).content

            zip_file = zip_file.decode(encoding="utf-8")

            zip_file = zip_file.split("<")

            for item in zip_file:
                if (item.find("href")!=-1 and item.find("/studydownload/")!=-1):
                    aux = item.split('"')[1]
                    return "https://www.metabolomicsworkbench.org" + aux

        return "https://www.metabolomicsworkbench.org/studydownload/" + id + ".zip"

class LocalUpload(LoadDataset):

    def __init__(self, errorManager: ManageErrors):
        super().__init__(errorManager)

    """
    Uploads data from Local.
    """
    def performWebScrappingURL(self, id, overwrite):
        
        mediaurl = "media/" + id

        if (os.path.exists(mediaurl) == True and overwrite == "Yes"):
            rmtree(mediaurl)
            #if (os.path.exists("media/" + id + ".zip") == True):
            #    os.remove("media/" + id + ".zip")
        elif (os.path.exists(mediaurl) == True and overwrite == "No"):
            if (os.path.exists("media/" + id + ".zip") == False):
                shutil.make_archive("media/" + id, 'zip', "media/" + id)
            return True

        try:
            os.mkdir(mediaurl)
        except OSError:
            #addErrorReport("The directory " + mediaurl + "could not be created.")
            self.errormanager.addError("ERROR: Creation of the directory %s failed" % mediaurl)
            print ("Creation of the directory %s failed" % mediaurl)
            return False

        with ZipFile(mediaurl + ".zip", 'r') as zipObj:
            zipObj.extractall(mediaurl)
                
        print("StartUnzip")
        self.unzipall(mediaurl)

        if (os.path.exists("media/" + id + ".zip") == True):
            os.remove("media/" + id + ".zip")

        if (os.path.exists("media/" + id) == True and os.path.exists("media/" + id + ".zip") == False):
            shutil.make_archive("media/" + id, 'zip', "media/" + id)

        return True

    def unzipall(self, url):

        dirs = os.listdir(url)
        for dir in dirs:
            urldir = url + "/" + dir
            if ( dir.find('.zip') != -1 ):
                ufolder = dir.split(".zi", 1)[0]
                print("urldir zip: " + urldir)
                print("urldir: " + url + "/" + ufolder)

                with ZipFile(urldir, 'r') as zipObj:
                    zipObj.extractall(url + "/" + ufolder)

                if (os.path.exists( urldir ) ):
                    os.remove(urldir)
                else:
                    self.errormanager.addError("ERROR: The folder %s doesn't exist" % (urldir))
                    print ("The folder %s doesn't exist" % (urldir) )

                self.unzipall(url + "/" + ufolder)
            elif ( dir.find('.7z') != -1 ):
                ufolder = dir.split(".7z", 1)[0]

                try:
                    os.mkdir(url + "/" + ufolder)
                except OSError:
                    self.errormanager.addError("ERROR: Creation of the directory %s failed" % (url + "/" + ufolder))
                    print ("Creation of the directory %s failed" % (url + "/" + ufolder))

                # Archive(urldir).extractall(url + "/" + ufolder)

                archive = py7zr.SevenZipFile(urldir, mode='r')
                archive.extractall(path=(url + "/" + ufolder))
                archive.close()

                #with py7zr.SevenZipFile("Archive.7z", 'r') as archive:
                #    archive.extractall(path="/tmp")

                if (os.path.exists( urldir ) ):
                    os.remove(urldir)
                else:
                    self.errormanager.addError("ERROR: The folder %s doesn't exist" % (urldir))
                    print ("The folder %s doesn't exist" % (urldir) )

                self.unzipall(url + "/" + ufolder)
            elif (os.path.isdir(urldir) and urldir.lower().find("mac")==-1):
                self.unzipall(urldir)
        
        return True