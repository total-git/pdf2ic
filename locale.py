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
}

months = {
'french' : {
    u'janvier':u'01', u'février':u'02', u'mars':u'03', u'avril':u'04', u'mai':u'05', u'juin':u'06', u'juillet':u'07', u'août':u'08', u'septembre':u'09', u'octobre':u'10', u'novembre':u'11', u'décembre':u'12'
    },
'english' : {
    u'january':u'01', u'february':u'02', u'march':u'03', u'april':u'04', u'may':u'05', u'june':u'06', u'july':u'07', u'august':u'08', u'september':u'09', u'october':u'10', u'november':u'11', u'december':u'12'
    },
'hebrew' : {
    },
}

diacritics = {
u'ﬁ ' : u'fi',
u'ﬀ ' : u'ff',
u'ﬂ ' : u'fl',
u'ﬃ ' : u'ffi',
u'ﬄ ' : u'ffl',
}

special_characters = {
u'2'   : u'²',
u'3'   : u'³',
u'er'  : u'er',
u'ère' : u'ère',
}


class locale(object):
    def __init__(self, language='english'):
        self.language = language
        self.categories = categories[self.language]
        self.weekdays = weekdays[self.language]
        self.months = months[self.language]

