#!/usr/bin/env python
import csv
pdfname = 'foo'
class article(object):
    def __init__(self, headline='N/A', byline='N/A', text='N/A', author='N/A', source='N/A', date='N/A', section='N/A'):
        self.headline = headline
        self.byline = byline
        self.text = text
        self.author = author
        self.source = source
        self.date = date
        self.section = section
        return
    def __repr__(self):
        return ('%s \n %s \n %s \n -- %s \n %s \n %s \n %s' % (self.headline, self.byline, self.text, self.author, self.sources, self.date, self.section))
    def export_csv(self):
        with open(pdfname + '.csv', 'a') as csvfile: # append to an existing file
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='\"', quoting=QUOTE_ALL)
            #csvwriter.writerow(['HEADLINE', 'BYLINE', 'TEXT', 'AUTHOR', 'SOURCE', 'DATE', 'SECTION'])
            csvwriter.writerow([self.headline, self.byline, self.text, self.author, self.source, self.date, self.section])
        return
