import io
import time
import shutil
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import dataframe_image as dfi

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.lib.units import cm
from pathlib import Path
from fpdf import FPDF


class ManageErrors:

    def __init__(self):
        self.nextLine = 26
        self.title = ""
        self.errors = []
        self.data = []
        self.info = []

    def temporal(self):

        # Global Variables
        WIDTH = 210
        HEIGHT = 297

        # Create PDF
        pdf = PDF() # A4 (210 by 297 mm)

        # Add Page
        pdf.add_page()

        # Add lettterhead and title
        self.create_letterhead(pdf, WIDTH)
        self.create_title(self.title, pdf)

        self.create_subtitle("General information", pdf)
        for info in self.info:
            # Add some words to PDF
            self.write_to_pdf(pdf, info)
            pdf.ln(10)

        self.create_subtitle("Data information", pdf)
        for data in self.data:
            # Add some words to PDF
            self.write_to_pdf(pdf, data)
            pdf.ln(10)

        self.create_subtitle("Error log", pdf)
        for error in self.errors:
            # Add some words to PDF
            self.write_to_pdf(pdf, error)
            pdf.ln(10)

        # Generate the PDF
        pdf.output("media/Report.pdf", 'F')

    def setTitle(self, title):
        self.title = title

    def addError(self, error):
        self.errors.append(error)
    
    def addData(self, data):
        self.data.append(data)

    def addInfo(self, info):
        self.info.append(info)

    def createPDF(self, path):
        self.path = path
        canvas = Canvas(path)
        canvas.setFont("Times-Roman", 20)
        canvas.drawString(10*cm, 28*cm, "CloMet")
        canvas.save()

    def getDataFromPDF(self):
        pdf_path = (
            Path.home()
            / "creating-and-modifying-pdfs"
            / "practice_files"
            / "Pride_and_Prejudice.pdf"
        )
        pdf = PdfFileReader(str(self.path))
        print(pdf.getNumPages)
        print(pdf.documentInfo)
        print(pdf.documentInfo.title)

        for page in pdf.pages:
            print(page.extractText())

    def addDataToPDF(self, data):
        packet = io.BytesIO()
        can = Canvas(packet, pagesize=letter)
        # can.setFillColorRGB(1, 0, 0)
        can.setFont("Times-Roman", 14)
        can.drawString(2*cm, self.nextLine*cm, data)
        self.nextLine = self.nextLine - 1
        can.save()

        packet.seek(0)
        new_pdf = PdfFileReader(packet)

        existing_pdf = PdfFileReader(open(self.path, "rb"))
        output = PdfFileWriter()

        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)

        outputStream = open("media/aux.pdf", "wb")
        output.write(outputStream)
        outputStream.close()

        if (os.path.exists(self.path)):
            os.remove(self.path)
            time.sleep(1)
            shutil.copy("media/aux.pdf", self.path)
            time.sleep(1)
            os.remove("media/aux.pdf")

    def test(self):
        #df = pd.read_csv("media/SamplePDF.csv")
        
        df = pd.DataFrame({'A': [1,2,3,4], 'B':[5,3,4,5]})

        # dfi.export(df, "media/SamplePDFTable.png")
        self.generate_matplotlib_stackbars(df, 'media/SampleGraph.png')
        self.generate_matplotlib_piechart(df, 'media/SampleGraph2.png')

        # Global Variables
        WIDTH = 210
        HEIGHT = 297

        # Create PDF
        pdf = PDF() # A4 (210 by 297 mm)


        '''
        First Page of PDF
        '''
        # Add Page
        pdf.add_page()

        # Add lettterhead and title
        self.create_letterhead(pdf, WIDTH)
        self.create_title(self.title, pdf)

        # Add some words to PDF
        self.write_to_pdf(pdf, "1. The graph below illustrates something related to Metabolomics:")
        pdf.ln(15)

        # Add table
        pdf.image('media/SampleGraph.png', x=50, w=100)
        pdf.ln(10)

        # Add some words to PDF
        self.write_to_pdf(pdf, "2. The other two graphs have the same function:")

        # Add the generated visualisations to the PDF
        pdf.image('media/SampleGraph2.png', 5, 175, WIDTH/2-10)
        pdf.image('media/SampleGraph2.png', WIDTH/2, 175, WIDTH/2-10)
        pdf.ln(10)


        '''
        Second Page of PDF
        '''

        # Add Page
        pdf.add_page()

        # Add lettterhead
        self.create_letterhead(pdf, WIDTH)

        # Add some words to PDF
        pdf.ln(40)
        self.write_to_pdf(pdf, "3. In conclusion, we were able to show a couple of graphs related to metabolomics that will be changed once we have the final format.")
        pdf.ln(15)

        # Generate the PDF
        pdf.output("media/Report.pdf", 'F')

    def generate_matplotlib_stackbars(self, df, filename):
        
        # Create subplot and bar
        fig, ax = plt.subplots()
        ax.plot(df['A'].values, df['B'].values, color="#E63946", marker='D') 

        # Set Title
        ax.set_title('Heicoders Academy Annual Sales', fontweight="bold")

        # Set xticklabels
        ax.set_xticklabels(df['A'].values, rotation=90)
        plt.xticks(df['A'].values)

        # Set ylabel
        ax.set_ylabel('Total Sales (USD $)') 

        # Save the plot as a PNG
        plt.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0)
        
        plt.show()

    def generate_matplotlib_piechart(self, df, filename):
    
        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        labels = ["A", "B"]
        sales_value = df[["A", "B"]].tail(1)
        
        # Colors
        colors = ['#E63946','#F1FAEE']
        
        # Create subplot
        fig, ax = plt.subplots()
        
        # Generate pie chart
        ax.pie(sales_value, labels=labels, autopct='%1.1f%%', startangle=90, colors = colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        # Set Title
        ax.set_title('Heicoders Academy 2016 Sales Breakdown', fontweight="bold")
        
        # Save the plot as a PNG
        plt.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0)
        
        plt.show()

    def create_letterhead(self, pdf, WIDTH):
        pdf.image("media/Header.png", 0, 0, WIDTH)

    def create_title(self, title, pdf):
    
        # Add main title
        pdf.set_font('Helvetica', 'b', 20)  
        pdf.ln(20)
        pdf.write(5, title)
        pdf.ln(10)

    def create_subtitle(self, subtitle, pdf):
        # Add main title
        pdf.set_font('Helvetica', 'b', 15)
        pdf.set_text_color(r=128,g=128,b=128)  
        pdf.ln(10)
        pdf.write(5, subtitle)
        pdf.ln(10)

    def write_to_pdf(self, pdf, words):
        
        # Set text colour, font size, and font type
        pdf.set_text_color(r=0,g=0,b=0)
        pdf.set_font('Helvetica', '', 10)
        
        pdf.write(5, words)

class PDF(FPDF):

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')
