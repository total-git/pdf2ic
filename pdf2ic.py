#!/usr/bin/python2
# -*- coding: utf-8 -*-

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
from locale import *

def main(argv):
    infile  = ''
    outfile = ''
    password = ''
    language = 'english' # default value
    try:
        opts, args = getopt.gnu_getopt(argv, 'i:o:p:l:', ['infile=','outfile=', 'password=','language='])
    except getopt.GetoptError:
        print 'pdf2ic.py [-i] <infile> [-o <outfile>] [-p <password>] [-l <language> (defaults to english)]'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-i', '--infile'):
            infile = arg
        elif opt in ('-o', '--outfile'):
            outfile = arg
        elif opt in ('-p', '--password'):
            password = arg
        elif opt in ('-l', '--language'):
            language = arg
        if opt not in ('-o', '--outfile') and infile: # default to pdfname.csv if no output file is given
            outfile = '.'.join(infile.split('.')[:-1] + ['csv'])
    if not args:
        print 'pdf2ic.py [-i] <infile> [-o <outfile>] [-p <password>] [-l <language>]'
        sys.exit(2)
    if not infile: # infile given without -i switch
        infile = args[0]
        if not outfile:
            outfile = '.'.join(infile.split('.')[:-1] + ['csv'])
    # set up a locale object from the language
    loc = locale(language)

    # convert the pdf to an xml file
    xmlfilename = '.'.join(infile.split('.')[:-1] + ['xml'])
    '''
    with open(xmlfilename, 'w') as xmlfd1:
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = XMLConverter(rsrcmgr, xmlfd1)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        with open(infile, 'rb') as pdffd:
            for page in PDFPage.get_pages(pdffd):
                # page.rotate = (page.rotate+rotation) % 360
                interpreter.process_page(page)
    # for some reason, xmlconverter forgets the closing </pages> tag
    with open(xmlfilename, 'a') as xmlfd:
        xmlfd.write('</pages>')
    '''

    # parse the xml file
    tree = etree.parse(xmlfilename)
    doc = tree.getroot()
    context = etree.iterparse(xmlfilename, tag='text')
    fontsizes = {}
    articles = []
    # date = ''
    currenttext = [] # String list because otherwise python will copy the string each time we concatenate something to it
    prevfontsize = 0
    prevfontname = ""
    completetext = [] # List of tuples containing the text and its size
    for action, elem in context:
        if elem.text:
            if elem.attrib['size'] in fontsizes:
                fontsizes[elem.attrib['size']] += 1
            else:
                fontsizes[elem.attrib['size']] = 1
    textsize = sorted(fontsizes, key=fontsizes.__getitem__)[-1] # the most common font size is probably the one for the article text
    root = context.root
    context = etree.iterwalk(root, tag='text')
    # write all text snippets that have the same font size to the text list together with their font size
    for action, elem in context:
        if elem.text:
            if elem.attrib['size'] == prevfontsize and elem.attrib['font'] == prevfontname:
                currenttext.append(elem.text)
            else:
                completetext.append((''.join(currenttext), elem.attrib['size'], elem.attrib['font']))
                currenttext = [elem.text]
            prevfontsize = elem.attrib['size']
            prevfontname = elem.attrib['font']
    for text, size, font in completetext:
        # find out the date
        #if text in dateformats:
        # find out the current category
        if text.lower() in loc.categories:
            category = text

    '''
    a = article('head','by','text')
    print a
    a.export_csv()
    '''


if __name__ == '__main__':
    main(sys.argv[1:])
