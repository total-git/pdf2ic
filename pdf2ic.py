from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import XMLConverter
from pdfminer.layout import LAParams

import sys, getopt

#import xml.etree.cElementTree as ET
#import elementtree.ElementTree as ET
from lxml import etree

from article import *


def main(argv):
    infile  = ''
    outfile = ''
    password = ''
    language = ''
    try:
        opts, args = getopt.gnu_getopt(argv, "i:o:p:l:", ["infile=","outfile=", "password=","language="])
    except getopt.GetoptError:
        print 'pdf2ic.py [-i] <infile> [-o <outfile>] [-p <password>] [-l <language>]'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--infile"):
            infile = arg
        elif opt in ("-o", "--outfile"):
            outfile = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-l", "--language"):
            language = arg
        if opt not in ("-o", "--outfile") and infile: # default to pdfname.csv if no output file is given
            outfile = '.'.join(infile.split('.')[:-1] + ['csv'])
    if not infile: # infile given without -i switch
        infile = argv[0]
        if not outfile:
            outfile = '.'.join(infile.split('.')[:-1] + ['csv'])

    # convert the pdf to an xml file
    xmlfilename = '.'.join(infile.split('.')[:-1] + ['xml'])
    """
    with open(xmlfilename, "w") as xmlfd1:
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = XMLConverter(rsrcmgr, xmlfd1)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        with open(infile, "rb") as pdffd:
            for page in PDFPage.get_pages(pdffd):
                # page.rotate = (page.rotate+rotation) % 360
                interpreter.process_page(page)
    """
    # parse the xml file
    #tree = ET.parse(xmlfilename)
    tree = etree.parse(xmlfilename)
    doc = tree.getroot()
    context = etree.iterparse(xmlfilename, tag='text')
    fontsize = 0
    for action, elem in context:
        if elem.text:
            print elem.text,
            if elem.attrib['size'] != fontsize:
                fontsize = elem.attrib['size']
                print "\n"
        #print elem.attrib['font'] + " " + elem.attrib['size'] + elem.text


    """
    a = article("head","by","text")
    print a
    a.export_csv()
    """


if __name__ == "__main__":
    main(sys.argv[1:])
