from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice

from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

from pdfminer_layout_scanner import layout_scanner

import sys, getopt

from article import *


def main(argv):
    infile  = ''
    outfile = ''
    password = ''
    language = ''
    try:
        opts, args = getopt.gnu_getopt(argv, "i:o:p:l:", ["ifile=","ofile=", "password=","language="])
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
        if opt not in ("-o", "--outfile"): # default to pdfname.csv if no output file is given
            outfile = '.'.join(infile.split('.')[:-1] + ['csv'])
    if not infile:
        infile = argv[0]
        if not outfile:
            outfile = '.'.join(infile.split('.')[:-1] + ['csv'])

    fp = open(infile, 'rb')
    parser = PDFParser(fp)
    # Create a PDF document object that stores the document structure (password potentially empty).
    document = PDFDocument(parser, password)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
    # Create a PDF device object.
    device = PDFDevice(rsrcmgr)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    text_content = []
    continue_article = False
    """
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        # layout=device.get_result()
        # text_content.append(parse_lt_objs(layout))
    """
    a = article("head","by","text")
    print a
    a.export_csv()


    
    '''
    # Set parameters for analysis.
    laparams = LAParams()
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    print layout_scanner.get_pages(infile)[0]
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        # receive the LTPage object for the page.
        layout = device.get_result()
    '''

if __name__ == "__main__":
    main(sys.argv[1:])


"""
def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str

print convert_pdf_to_txt("../embedded_text/sample_art.pdf")
"""
