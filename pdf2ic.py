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
    date = u''
    weekday = u''
    day = u''
    month = u''
    year = u''

    category = u''

    current_text = [] # String list because otherwise python will copy the string each time we concatenate something to it
    articles = []

    fontsizes = {} # a dictionary for the used font sizes; will be sorted to give the most common font size
    fontnames = {} # a dictionary for the used fonts
    tmp_fontsize = u''
    tmp_fontname = u''
    tmp_text = u''
    prev_fontsize = u''
    prev_fontname = u''
    headline = 'N/A'
    byline = 'N/A'

    complete_text = [] # List of tuples containing the text and its size

    read_buffer = [(None, None, None),(None, None, None),(None, None, None),(None, None, None)] # FILO buffer containing the last 4 tuples (text, size, font)

    # parse the xml file
    tree = etree.parse(xml_filename)
    doc = tree.getroot()
    context = etree.iterparse(xml_filename, tag='text')
    for event, elem in context:
        if elem.text:
            tmp_fontsize = elem.attrib['size']
            tmp_fontname = elem.attrib['font']
            if tmp_fontsize in fontsizes:
                fontsizes[tmp_fontsize] += 1
                fontnames[tmp_fontname] += 1
            else:
                fontsizes[tmp_fontsize] = 1
                fontnames[tmp_fontname] = 1
    article_fontsize = sorted(fontsizes, key=fontsizes.__getitem__)[-1] # the most common font size is probably the one for the article text
    article_fontname = sorted(fontnames, key=fontnames.__getitem__)[-1] # the most common font name is probably the one for the article text
    # print fontsizes # DEBUG

    root = context.root
    context = etree.iterwalk(root, tag='text') # iterwalk does the same as iterparse, but uses the in-memory tree

    # write all text snippets that have the same font size to the text list (together with their font size)
    for event, elem in context:
        tmp_fontsize = elem.attrib['size']
        tmp_fontname = elem.attrib['font']
        if elem.text:
            if tmp_fontsize == prev_fontsize: # same as before => add it to the current text
                current_text.append(elem.text)
            else: # new font size => add the whole section to complete_text and start a new section
                tmp_text = u''.join(current_text)
                # replace the diacritics (fi, ff etc)
                for i,j in diacritics.iteritems():
                    tmp_text = tmp_text.replace(i,j)
                # remove dashes from line endings TODO better method, because sont-ils and the likes are changed; maybe a dictionary for those words?
                tmp_text = tmp_text.replace(u'-', u'')

                complete_text.append((tmp_text, prev_fontsize, prev_fontname))
                current_text = [elem.text]
            prev_fontsize = tmp_fontsize
            prev_fontname = tmp_fontname


    # iterate over the text segments
    article_text = ''
    for text, size, font in complete_text:

        # find out the date
        tmpdate = text.split()
        tmp_regex = re.findall(u'(?<=\s)\d{4}(?=\s)', text)
        if tmp_regex:
            year = tmp_regex[0]
        tmp_regex = re.findall(u'(?<=\s)\d{2}(?=\s)', text)
        if tmp_regex:
            day = tmp_regex[0]
        for i in tmpdate:
            if i.lower() in loc.weekdays:
                weekday = loc.weekdays[i.lower()]
            if i.lower() in loc.months:
                month = loc.months[i.lower()]
        dates.append(year+u'-'+month+u'-'+day+u'-'+weekday) # append it to the date list

        # find out the current category
        if text.lower() in loc.categories:
            category = text
        
        if size == article_fontsize:
            if text:
                # append strings consiting of 1 (or 2, as in «A) to the article text; the first letter of an article is commonly in a larger font and therefore in another elemnt of our list
                if text[0].lower() and len(read_buffer[3][0]) <= 2:
                    articles.append(article(headline, byline, article_text, section=category))
                    article_text = read_buffer[3][0] + text
                    # font size of previous segment is > 30 => no byline and the big segment is the headline
                    if float(read_buffer[2][1]) > 30.0:
                        headline = read_buffer[2][0]
                        byline = 'N/A'
                    # font size of the segment before that is > 30 => byline has to be in between the headline and the text
                    elif float(read_buffer[1][1]) > 30.0:
                        headline = read_buffer[1][0]
                        byline = read_buffer[2][0]
                elif float(read_buffer[3][1]) > 30.0:
                    headline = read_buffer[3][0]
                    byline = 'N/A'
                    article_text = text
                    articles.append(article(headline, byline, article_text, section=category))
                elif float(read_buffer[2][1]) > 30.0:
                    headline = read_buffer[2][0]
                    byline = read_buffer[3][0]
                    article_text = text
                    articles.append(article(headline, byline, article_text, section=category))
                elif float(read_buffer[1][1]) > 30.0:
                    headline = read_buffer[1][0]
                    byline = read_buffer[2][0]
                    article_text = read_buffer[3][0] + '\n\n' + text
                    articles.append(article(headline, byline, article_text, section=category))

                # look for small headlines inside the article (difference between the two font sizes is small)
                if float(read_buffer[3][1]) < float(size) + 1 and read_buffer[2][1] == article_fontsize:
                    article_text += '\n\n' + read_buffer[3][0] + '\n\n' + text
                '''
                print "-----------------"
                print codecs.encode('HEAD: '+headline, 'utf-8') # DEBUG
                print codecs.encode('BY: '+byline, 'utf-8') # DEBUG
                print codecs.encode(article_text, 'utf-8') # DEBUG
                '''

        # store the current text, size, font to the buffer and pop the first element
        read_buffer.append((text,size,font))
        read_buffer.pop(0)

    # use the most common date
    date = most_common(dates)

    '''
    a = article('head','by','text')
    print a
    a.export_csv()
    '''
    for i in articles:
        print '------------------'
        print codecs.encode(unicode(i), 'utf-8') # DEBUG
    '''
    print "-----------------"
    print codecs.encode('HEAD: '+headline, 'utf-8') # DEBUG
    print codecs.encode('BY: '+byline, 'utf-8') # DEBUG
    print codecs.encode(article_text, 'utf-8') # DEBUG

    a = article(headline, byline, article_text, date, section=category)
    print codecs.encode(unicode(a), 'utf-8') # DEBUG
    '''



if __name__ == '__main__':
    main(sys.argv[1:])


# TODO
'''
DONE -- replace ﬁ with fi (and reconcatenate the words like "ﬁ n")
potentially the same problem with
ﬀ -> ff
ﬂ -> fl
ﬃ -> ffi
ﬄ -> ffl

DONE -- line endings

hebrew weekdays, months and categories

potentially other languages

DONE -- append the first letter of an article (because it is in another font size)

delete xml file afterwards
'''
