#!/usr/bin/env python
import csv
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
        return ('HEADLINE: %s \n BYLINE: %s \n TEXT: %s \n AUTHOR: %s \n SOURCE: %s \n DATE: %s \n SECTION: %s' % (self.headline, self.byline, self.text, self.author, self.source, self.date, self.section))
    '''
    def export_csv(self):
        with open('foo.csv', 'a') as csvfile: # append to an existing file
            #csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=QUOTE_ALL)
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|')

            #csvwriter.writerow(['HEADLINE', 'BYLINE', 'TEXT', 'AUTHOR', 'SOURCE', 'DATE', 'SECTION'])
            csvwriter.writerow([self.headline, self.byline, self.text, self.author, self.source, self.date, self.section])
        return
    '''
