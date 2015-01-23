#!/usr/bin/python2
# -*- coding: utf-8 -*-

categories = {
'french' : [
    u'politique',
    u'monde',
    u'economie',
    u'securite',
    u'culture',
    u'societe',
    u'sport',
    u'feuilleton',
    ],
'english' : [
    u'politics',
    u'world',
    u'economy',
    u'business',
    u'culture',
    u'society',
    u'feuilleton',
    u'sports',
    u'sport',
    ],
'hebrew' : [
    ],
'arabic' : [
    ],
}

weekdays = {
'french' : {
    u'lundi': u'Monday', u'mardi': u'Tuesday', u'mercredi': u'Wednesday', u'jeudi': u'Thursday', u'vendredi': u'Friday', u'samedi': u'Saturday', u'dimanche': u'Sunday'
    },
'english' : {
    u'monday': u'Monday', u'tuesday': u'Tuesday', u'wednesday': u'Wednesday', u'thursday': u'Thursday', u'friday': u'Friday', u'saturday': u'Saturday', u'sunday': u'Sunday'
    },
'hebrew' : {
    },
'arab' : {
    },
}

months = {
        'french' : {
            u'janvier':1, u'février':2, u'mars':3, u'avril':4, u'mai':5, u'juin':6, u'juillet':7, u'août':8, u'septembre':9, u'octobre':10, u'novembre':11, u'décembre':12
            },
        'english' : {
            u'january':1, u'february':2, u'march':3, u'april':4, u'may':5, u'june':6, u'july':7, u'august':8, u'september':9, u'october':10, u'november':11, u'december':12
            },
        'hebrew' : {
            },
        'arabic' : {
            },
        }


class locale(object):
    def __init__(self, language='english'):
        self.language = language
        self.categories = categories[self.language]
        self.weekdays = weekdays[self.language]
        self.months = months[self.language]

