# -*- coding: utf-8 -*-

from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import XMLConverter
from pdfminer.layout import LAParams

import sys, getopt
import re
import codecs

#import xml.etree.cElementTree as ET
#import elementtree.ElementTree as ET
from lxml import etree

from article import *
from locale import *

def most_common(lst):
    return max(set(lst), key=lst.count)

def main(argv):
    # command line options
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

    # build the basename of the xml file (foo.pdf -> foo.xml)
    xml_filename = '.'.join(infile.split('.')[:-1] + ['xml'])

    # convert the pdf to an xml file
    '''
    with open(xml_filename, 'w') as xmlfd1:
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = XMLConverter(rsrcmgr, xmlfd1)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        with open(infile, 'rb') as pdffd:
            for page in PDFPage.get_pages(pdffd):
                # page.rotate = (page.rotate+rotation) % 360
                interpreter.process_page(page)

    # for some reason, xmlconverter forgets the closing </pages> tag
    with open(xml_filename, 'a') as xmlfd:
        xmlfd.write('</pages>')
    '''

    # will store the dates; the most commom one will be assumed to be the publishing date of the paper
    dates = []
    weekday = u''
    day = u''
    month = u''
    year = u''

    current_text = [] # String list because otherwise python will copy the string each time we concatenate something to it
    articles = []

    first_letter = u''

    fontsizes = {} # a dictionary for the used font sizes; will be sorted to give the most common font size
    fontnames = {} # a dictionary for the used fonts
    prev_fontsize = 0
    prev_fontname = u''

    complete_text = [] # List of tuples containing the text and its size

    # parse the xml file
    tree = etree.parse(xml_filename)
    doc = tree.getroot()
    context = etree.iterparse(xml_filename, tag=u'text')
    for action, elem in context:
        if elem.text:
            if elem.attrib[u'size'] in fontsizes:
                fontsizes[elem.attrib[u'size']] += 1
                fontnames[elem.attrib[u'font']] += 1
            else:
                fontsizes[elem.attrib[u'size']] = 1
                fontnames[elem.attrib[u'font']] = 1
    article_fontsize = sorted(fontsizes, key=fontsizes.__getitem__)[-1] # the most common font size is probably the one for the article text
    '''
    print sorted(fontsizes, key=fontsizes.__getitem__)
    print fontsizes
    for i in sorted(fontsizes, key=fontsizes.__getitem__):
        print i, fontsizes[i]
    for i in sorted(fontnames, key=fontnames.__getitem__):
        print i, fontnames[i]
    '''
    root = context.root
    context = etree.iterwalk(root, tag=u'text') # iterwalk does the same as iterparse, but uses the in-memory tree

    # write all text snippets that have the same font size to the text list (together with their font size)
    for action, elem in context:
        if elem.text:
            if elem.attrib[u'size'] == prev_fontsize and elem.attrib[u'font'] == prev_fontname:
                current_text.append(elem.text)
            else:
                complete_text.append((u''.join(current_text), elem.attrib[u'size'], elem.attrib[u'font']))
                current_text = [elem.text]
            prev_fontsize = elem.attrib[u'size']
            prev_fontname = elem.attrib[u'font']
    # iterate over the text segments
    for text, size, font in complete_text:
        # find out the date
        tmpdate = text.split()
        tmp = re.findall(u'(?<=\s)\d{4}(?=\s)', text)
        if tmp:
            year = tmp[0]
        tmp = re.findall(u'(?<=\s)\d{2}(?=\s)', text)
        if tmp:
            day = tmp[0]
        for i in tmpdate:
            if i.lower() in loc.weekdays:
                weekday = loc.weekdays[i.lower()]
            if i.lower() in loc.months:
                month = loc.months[i.lower()]
        dates.append(year+u'-'+month+u'-'+day+u'-'+weekday) # append it to the date list

        # find out the current category
        if text.lower() in loc.categories:
            category = text

        # find 1-Letter strings (first letter of an article is commonly in a larger font)
        if len(text) <= 2:
            first_letter = text # if what follows is an article starting with a lowercase letter, append it to the beginning

        
        if float(size) == article_size:
            print codecs.encode(text, 'utf-8')
            #if text:
                #print text
                #if text[0].islower():
                    #article_text = first_letter + text
                    #print article_text

    # use the most common date
    date = most_common(dates)

    '''
    a = article('head','by','text')
    print a
    a.export_csv()
    '''


if __name__ == '__main__':
    main(sys.argv[1:])


# TODO
'''
replace ﬁ with fi (and reconcatenate the words like "ﬁ n")
potentially the same problem with
ﬀ -> ff
ﬂ -> fl
ﬃ -> ffi
ﬄ -> ffl

line endings

hebrew weekdays, months and categories

potentially other languages

append the first letter of an article (because it is in another font size)

delete xml file afterwards
'''
