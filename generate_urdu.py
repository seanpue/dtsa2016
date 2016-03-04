# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Generates Urdu versions of output
# 
# This is a bit sloppy right now. 

# <codecell>

import sys
sys.path.append('./graphparser/')
import graphparser
urdup = graphparser.GraphParser('./graphparser/settings/urdu.yaml')
nagarip = graphparser.GraphParser('./graphparser/settings/devanagari.yaml')

# <codecell>

import csv

def unicode_csv_reader(unicode_csv_data, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                             **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')
import csv, codecs, cStringIO

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds )
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# <codecell>

def write_urdu_statistics(inputfile,outputfile,nagari=False,headers=True):
    with open(outputfile,'w') as output_stream:
        csvwriter = UnicodeWriter(output_stream)
        if headers==True:
            fieldnames = ['urdu', 'transliteration','count']
            if nagari==True:
                fieldnames=['urdu', 'nagari', 'transliteration','count']
            csvwriter.writerow(fieldnames) # add headers
            
        with open(inputfile,'r') as input_stream:
            csvreader = unicode_csv_reader(input_stream) # this is likely not utf-8
            for row in csvreader:
                (token,freq)=row
                if nagari==True:
                    row = urdup.parse(token).output,nagarip.parse(token).output,token,freq
                else:
                    row = urdup.parse(token).output, token, freq
                csvwriter.writerow(row)

# <codecell>

def write_all_urdu_statistics():
#    write_urdu_statistics('output/statistics/izafat-freq.csv','output/statistics') # will contain transliteration for now
    write_urdu_statistics('output/statistics/lemmas-beta-freq.csv','output/statistics/lemmas-beta-freq-ur.csv')
    write_urdu_statistics('output/statistics/uniquetokens-freq.csv','output/statistics/uniquetokens-freq-ur.csv')
    write_urdu_statistics('output/statistics/izafatastokens-freq.csv','output/statistics/izafatastokens-freq-ur.csv')
    write_urdu_statistics('output/statistics/izafatastokens-freq.csv','output/statistics/izafatastokens-freq-hiur.csv',nagari=True)
    write_urdu_statistics('output/statistics/lemma-counts.csv', 'output/statistics/lemma-counts-ur.csv')

# <codecell>

write_all_urdu_statistics()

# <codecell>


