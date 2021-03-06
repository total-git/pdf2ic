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

HEADLINE_THRESHOLD = 30.0
FIRST_LETTER_THRESHOLD = 20.0
TOLERABLE_FONTSIZE_DIFFERENCE = 1.0
MAX_CATEGORY_LENGTH = 15

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

    '''
    FILO (first in last out) buffer containing the last 4 tuples (text, size, font)
    '''
    read_buffer = [(None, None, None),(None, None, None),(None, None, None),(None, None, None)] 

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
    # article_fontname = sorted(fontnames, key=fontnames.__getitem__)[-1] # the most common font name is probably the one for the article text
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
                # remove dashes from line endings TODO better method, because sont-ils and the likes are changed; maybe a dictionary for those words? -vous -ils
                tmp_text = tmp_text.replace(u'-', u'')

                complete_text.append((tmp_text, prev_fontsize, prev_fontname))
                current_text = [elem.text]
            prev_fontsize = tmp_fontsize
            prev_fontname = tmp_fontname


    # iterate over the text segments
    article_text = u''
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
        if len(text) < MAX_CATEGORY_LENGTH:
            for cat in loc.categories:
                if cat in re.sub(u'[\W_]+', u'', text.lower()):
                    category = cat

        
        # search for the special box thing that is sometimes used to conclude articles
        if font == 'HLWIXK+Webdings':
            '''
            print '0:  ' + read_buffer[0][0] + read_buffer[0][1]
            print '1:  ' + read_buffer[1][0] + read_buffer[1][1]
            print '2:  ' + read_buffer[2][0] + read_buffer[2][1]
            print '3:  ' + read_buffer[3][0] + read_buffer[3][1]
            print 'text:  ' + codecs.encode(text, 'utf-8') + size # DEBUG
            print 'article_text:  ' + codecs.encode(article_text, 'utf-8')
            print 'headline:  ' + codecs.encode(headline, 'utf-8')
            print 'byline:  ' + codecs.encode(byline, 'utf-8')
            '''
            articles.append(article(headline=headline, byline=byline, text=article_text, section=category))
            article_text=u''
            headline=u'N/A'
            byline=u'N/A'

        if size == article_fontsize:
            if text:
                # append strings consisting of 1 (or 2, as in «A) to the article text; the first letter of an article is commonly in a larger font and therefore in another element of our list
                # the regex checks if the character is whitespace or a digit
                if text[0].lower() and len(read_buffer[3][0]) <= 2 and float(read_buffer[3][1]) > FIRST_LETTER_THRESHOLD and not re.search(u'\A(\s*|\d)\Z', read_buffer[3][0]):
                    # font size of previous segment is > article_fontsize and nothing before that => no byline and the big segment is the headline
                    if float(read_buffer[2][1]) > float(article_fontsize) and float(read_buffer[1][1]) <= float(article_fontsize):
                        # articles.append(article(headline=headline, byline=byline, text=article_text, section=category))
                        article_text = read_buffer[3][0] + text
                        headline = read_buffer[2][0]
                        byline = 'N/A'
                    # font size of the segment before that is > threshold: byline should be in between the headline and the text
                    elif float(read_buffer[2][1]) > float(article_fontsize) and float(read_buffer[1][1]) > float(article_fontsize):
                        # articles.append(article(headline=headline, byline=byline, text=article_text, section=category))
                        article_text = read_buffer[3][0] + text
                        headline = read_buffer[1][0]
                        byline = read_buffer[2][0]
                    else:
                        # articles.append(article(headline=headline, byline=byline, text=article_text, section=category))
                        article_text += read_buffer[3][0] + text
                elif float(read_buffer[3][1]) > HEADLINE_THRESHOLD and len(read_buffer[3][0]) > 2:
                    # articles.append(article(headline=headline, byline=byline, text=article_text, section=category))
                    headline = read_buffer[3][0]
                    byline = 'N/A'
                    article_text = text
                elif float(read_buffer[2][1]) > HEADLINE_THRESHOLD and len(read_buffer[2][0]) > 2:
                    # articles.append(article(headline=headline, byline=byline, text=article_text, section=category))
                    headline = read_buffer[2][0]
                    byline = read_buffer[3][0]
                    article_text = text
                # in interviews, the first letter doesn't seem to be in a bigger font. Also, the question is in another font. So the question will be in read_buffer[3][0]
                elif float(read_buffer[1][1]) > HEADLINE_THRESHOLD and len(read_buffer[1][0]) > 2:
                    # articles.append(article(headline=headline, byline=byline, text=article_text, section=category))
                    headline = read_buffer[1][0]
                    byline = read_buffer[2][0]
                    article_text = read_buffer[3][0] + '\n\n' + text

                # look for small headlines inside the article (difference between the two font sizes is small)
                if float(size) < float(read_buffer[3][1]) < float(size) + TOLERABLE_FONTSIZE_DIFFERENCE and read_buffer[2][1] == article_fontsize:
                    # when finding italic expressions inside the text, keep going (they normally don't end in . ? ! or :)
                    if read_buffer[3][2].lower().find(u'italic') > 0 and not re.search(u'[\.\?!:,»]\s*\Z', article_text):
                        article_text += read_buffer[3][0] + text
                    # when finding sub-headlines, add newlines
                    else:
                        article_text += '\n\n' + read_buffer[3][0] + '\n\n' + text

                # replace whitespace in wrong font sizes
                if read_buffer[2][1] == article_fontsize and re.search(u'\A\s*\Z', read_buffer[3][0]):
                    article_text += text

                # replace some special characters that appear in wrong font sizes (at the moment superscripts: exponents, 1er (premier) / 1ère (première))
                if read_buffer[2][1] == article_fontsize and read_buffer[3][0] in special_characters:
                    article_text += special_characters[read_buffer[3][0]] + text

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

    # export the list of articles to a csv file
    with open(outfile, 'a') as csvfile: # append to an existing file
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|')
        csvwriter.writerow([u'HEADLINE', u'BYLINE', u'TEXT', u'AUTHOR', u'SOURCE', u'DATE', u'SECTION'])
        for i in articles:
            i.date = date
            csvwriter.writerow([
                codecs.encode(i.headline, 'utf-8'),
                codecs.encode(i.byline, 'utf-8'),
                codecs.encode(i.text, 'utf-8'),
                codecs.encode(i.author, 'utf-8'),
                codecs.encode(i.source, 'utf-8'),
                codecs.encode(i.date, 'utf-8'),
                codecs.encode(i.section, 'utf-8')
                ])
            #print '------------------' # DEBUG
            #print codecs.encode(unicode(i), 'utf-8') # DEBUG


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

use https://github.com/paxan/python-dateutil for the date

DONE -- article export
'''
