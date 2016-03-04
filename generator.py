# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Ghalib Concordance Generator

# <markdowncell>

# ## Description
# 
# This notebook contains code to generate a concordance for the muravāj dīvān of Ghalib.
# 
# Verses are taken from "input/verses.csv"
# 
# The current task is to identify the proper lemma of the tokens, e.g. singular instead of plural,
# verb infinitive instead of verb root, etc. This can partially be done computationally.
# 
# Lemma that remain to be checked are in "output/tocheck.csv" The first column, if marked as 'x',
# means that entry is okay. Checked lemma can then be entered into "input/okay.csv" using the
# functions 
# 

# <codecell>

import re
from collections import *
import csv

# <headingcell level=2>

# Variables

# <codecell>

verses = {}                      # dictionary of verses, e.g. 001.01.0='naqsh faryaadii..'
tokens = {}                      # dictionary of tokens where key is verses+.xx, e.g. 001.01.0.01 = 'naqsh'
unique_tokens = Counter()        # Counter of tokens where value is their count
lemmas = defaultdict(list)       # dictionary of tokens where value is a list of their lemmas
unique_lemmas = []               # list of unique lemmas
okay_lemmas = defaultdict(list)  # dictionary of unique tokens with lists of lemma, e.

# <markdowncell>

# ##Functions

# <codecell>

# moved load_verses, moved to util.py

def load_verses(inputfile='input/verses.csv'):
    '''
    Loads verses from CSV data file
    inputfile: name of csv file
    returns: verses where verses['ggg.vv.l']=token; where ggg=ghazal #; vv=verse number;l=line number
    '''


    verses = {}
    with open(inputfile,'r') as csvfile:
        versereader = csv.reader(csvfile)
        for row in versereader:
            if len(row)<3: print row
            (verse_id, input_string, real_scan) = row # 
            if not 'x' in verse_id: # only muravvaj divan for now
                verses[verse_id] = input_string.strip() 
    return verses

def get_okay_lemmas(inputfile='input/okay.csv'):
    '''
    Loads checked lemmas from CSV data file
    inputfile: name of csv file
    returns: checked_lemmas where checked_lemmas['token'] = [lemmas]
    '''

    import csv
    okay_lemmas = {}
    with open(inputfile,'r') as csvfile:
        versereader = csv.reader(csvfile)
        for row in versereader:
#            print row
            (status, unique_token, lemmas) = row
            
            assert status in ['','x']
            if status=='x':
                okay_lemmas[unique_token]=lemmas.split('|')
    return okay_lemmas


def get_tokens(verses):
    '''
    Identifies tokens in verses
    verses: verses
    returns: tokens, where tokens['ggg.vv.l.tt']=token {tt = token # on line starting  at zero}
    '''
    tokens = {}
    token_instances=defaultdict(list)
    token_instance_count = Counter()
    for k in verses.keys():
        v_tokens = verses[k].split(' ')
        for id,t in enumerate(v_tokens):

            token_id = k+'.'+str(id).zfill(2)
            tokens[token_id] = t
            token_instances[t].append(token_id)
            token_instance_count[t]+=1
    return tokens,token_instances,token_instance_count

def locate_token(token):
    '''
    Finds locations of token
    token: string 
    Input: token (string)
    returns: a list of locations, e.g. [001.01.0.01]
    '''
    assert tokens
    return [k  for k,v in tokens.iteritems() if v==token]

def match_tokens(match_string):
    '''
    Finds tokens matching a pattern (from start)
    match_string: regular expression string (assumes ^,e.g. 'naq')
    returns: a list of tokens,e.g. ['naqsh']
    '''
    assert unique_tokens
    return [k  for k in unique_tokens.keys() if re.match(match_string,k)]

def search_tokens(match_string):
    '''
    Searches for tokens matching a pattern (anywhere in it)
    match_string: regular expression of string
    Input: regular expression string (e.g. 'naqsh'
    returns: a list of tokens, e.g. ['naqsh']
    '''
    assert unique_tokens
    return [k  for k in unique_tokens.keys() if re.search(match_string,k)]

def get_unique_tokens(tokens):
    '''
    Finds unique tokens
    tokens: a dictionary of tokens at locations, e.g. tokens['001.01.0.00']='naqsh'
    returns: a dictionary of unique tokens and their count, unique_tokens['token']=1
    '''
    unique = Counter()
#    print type(tokens)
    for k,t in tokens.iteritems():
        unique[t]+=1
    return unique


def get_lemmas(unique_tokens):
    '''
    Generate lemmas of tokens
    unique_tokens: dictionary of unique tokens
    returns: lemmas[original_token]=['lemma1','lemma2']
    '''
    lemmas = {}

    
    for t in unique_tokens.keys():
        lemma = t
        if re.search("-e$",t):
            lemma = t[:-2] # remove izaafat ending '-e'
        if re.search("[-']haa$",t): 
            lemma = t[:-4] # remove Persian plural ['-]haa ending
#            print lemma
        t_lemmas = [lemma]
        if re.search('-o-',lemma):
            nouns = lemma.split('-o-')
            t_lemmas = t_lemmas + nouns
            
        lemmas[t]=t_lemmas
    return lemmas

def get_unique_lemmas(lemmas):
    '''
    Generates unique lemma forms
    lemmas: dictionary keyed by tokens containing lists of lemma, e.g. lemmas['rang-o-buu']=['rang','buu','rang-o-buu']
    returns: unique_lemmas as unique_lemmas['lemma']=count
    '''
    unique_lemmas = set()
    for t,t_lemmas in lemmas.iteritems():
        for lemma in t_lemmas:
            unique_lemmas.add(lemma)
    return unique_lemmas


def to_check():
    '''
    Generates list of unique tokens that still need to be checked.
    '''
    out = []
    return [t for t in sorted(unique_tokens.keys()) if not t in okay_lemmas]

def print_stats():
    print "Currently there are ",len(okay_lemmas)," out of ",len(lemmas)

# <markdowncell>

# ## Set Variables

# <codecell>

verses = load_verses()
tokens,token_instances,token_instance_count = get_tokens(verses)
unique_tokens = get_unique_tokens(tokens)

lemmas = get_lemmas(unique_tokens)
unique_lemmas = get_unique_lemmas(lemmas)
okay_lemmas = get_okay_lemmas()

okay_tokens_not_in_lemmas = [ok for ok in okay_lemmas if not ok in lemmas]

if len(okay_tokens_not_in_lemmas) > 0:
    print 'the following tokens are marked as okay but are not any longer'
    print okay_tokens_not_in_lemmas

# <markdowncell>

# ## Update Files

# <codecell>

def update_to_check():
    '''
    Writes unique tokens not contained in okay_lemmas to output/tocheck.csv
    '''
    with open('output/tocheck.csv','w') as f:
        for t in sorted(unique_tokens.keys()):
            if not t in okay_lemmas: # only add unchecked ones
                line  = "," # good or bad
                line += t+"," #token
                line += '|'.join(lemmas[t]) # possible lemma of token
                line += "\n" 
                f.write(line)

def update_okay(inputfile='output/tocheck.csv'):
    '''
    Loads lemmas noted as correct from inputfile into okay_lemmas
    '''
    lemmas_to_add = get_okay_lemmas(inputfile=inputfile)
    for k,v in lemmas_to_add.iteritems():
        if k in okay_lemmas:
            print "WARNING: ",k," found in okay_lemmas. Will override."
        okay_lemmas[k] = v
    
def write_okay(outputfile='input/okay.csv'):
    '''
    Writes okay_lemmas to outputfile, as status,token,lemma1|lemma2|lemma3
    '''
    with open(outputfile,'w') as f:
        for t in sorted(okay_lemmas.keys()):
            line  = "x," # good or bad
            line += t+"," #token
            line += '|'.join(okay_lemmas[t])
            line += "\n" 
            f.write(line)

def update_files():
    '''
    Loads lemmas noted as correct from tocheck.csv, 
    Writes okay_lemmas as input/okay.csv
    Regenerates output/tocheck.csv
    '''
    update_okay() 
    write_okay()
    update_to_check()
    print_stats()

# <codecell>

update_files()

# <markdowncell>

# #Concordance Details
# 
# Generates "output/conc_details.csv" which lists lemmas and their sources.

# <codecell>

lemmas_out = defaultdict(set)


for k,v in okay_lemmas.iteritems(): # k = word; v = lemmas
    for l in v:
        lemmas_out[l].add(k)

with open('output/conc_details.csv','w') as f:
    for k,v in sorted(lemmas_out.iteritems()):
        f.write(k+','+'|'.join(v)+'\n')
        
#okay_lemmas.keys()[0:100]

# <markdowncell>

# ##Lemma Instances
# Sorted list of lemma instances.

# <codecell>

def instances_of_lemma(lemma):
    i=0
    for x in lemmas_out[lemma]:
        i+= token_instance_count[x]
    return i

lemma_instance_count = {lemma: instances_of_lemma(lemma) for lemma in lemmas_out.keys()}
#instances_of_lemma for
#zz=sorted(lemmas_out.keys(),key=instances_of_lemma)#sort_by_instances)#size_of_lemma_by_instances)
#for z in zz: print z, instances_of_lemma[zz])
with open("output/statistics/lemma-counts.csv","w") as f:
    for x in sorted(lemma_instance_count, key=lemma_instance_count.get,reverse=True):
        f.write(x+','+str(lemma_instance_count[x])+'\n')

# <markdowncell>

# #Izafats

# <markdowncell>

# I am not sure yet how we will wind up using these. Probably based on a token location range, similarly to compound verbs, etc. There may be some combos I am not grabbing properly. These will need to lemma-ed later (e.g. nasalization).

# <codecell>

izafat_verse_ids = [v_id for v_id in sorted(verses.keys()) if re.search('-e ',verses[v_id])]
izafat_verses = [verses[v_id] for v_id in izafat_verse_ids]

# <codecell>

izafat_re = re.compile('(?:[^ ]+-e )+(?:z )?[^ ]+')
izafats=Counter()
for s in izafat_verses:
    x = izafat_re.findall(s)#re.findall(m,s)
    for y in x:
        izafats[y]+=1

# <codecell>

with open('output/izafats.csv','w') as f:
    f.write('\n'.join(sorted(izafats.keys())))

# <markdowncell>

# Here also is a version of the tokens where izafat phrases are treated as individual tokens.

# <codecell>

iast=Counter() # izafats as tokens, along with tokens
iast_re = re.compile('(?:[^ ]+-e )+(?:z )?[^ ]+|[^ ]+')
for i,s in verses.iteritems():
    words = iast_re.findall(s)
    for t in words:
        iast[t]+=1

# <markdowncell>

# ##Statistics
# Word frequencies, etc.

# <codecell>

def make_csv_of_token_freq(d, filename):
    '''
    Generates a CSV file of a dictionary based on numeric value of key, reverse sorted
    d: dictionary of tokens and values(token: #)
    filename = output file name
    '''
    with open(filename,'w') as f:
        for k,v in d.most_common():
            f.write(k+','+str(v)+'\n')
            

# <codecell>

make_csv_of_token_freq(izafats, 'output/statistics/izafat-freq.csv')
make_csv_of_token_freq(unique_tokens, 'output/statistics/uniquetokens-freq.csv')
make_csv_of_token_freq(iast, 'output/statistics/izafatastokens-freq.csv')

# <codecell>

type(izafats)

# <codecell>

lemma_counts_beta=Counter()

for token, count in unique_tokens.iteritems():
    if token in okay_lemmas:
        lemma = okay_lemmas[token][0]
    else:
        lemma = token
    lemma_counts_beta[lemma]+=count
lemma_counts_beta
make_csv_of_token_freq(lemma_counts_beta,'output/statistics/lemmas-beta-freq.csv')

# <codecell>

# the following will generate the urdu versions of the statistics (a little slow)

# <codecell>

import generate_urdu

# <codecell>

#redo here
reload(generate_urdu)#generate_urdu.write_all_urdu_statistics()

# <markdowncell>

# ##Quick and Dirty Output
# 
# This generates some quick output for proofing as .md; this a bit sloppy

# <codecell>

with open('output/lemmas-by-size.txt','w') as f:
    for x in sorted(lemma_instance_count, key=lemma_instance_count.get,reverse=True):
        words=lemmas_out[x]
        words = sorted(words,key=token_instance_count.get, reverse=True)
        f.write(x+' '+str(lemma_instance_count[x])+'\n')
        for w in words:
            f.write("  - "+w+' '+str(token_instance_count[w])+'\n')

# <codecell>

import codecs
import sys
sys.path.append('./graphparser/')
import graphparser
urdup = graphparser.GraphParser('./graphparser/settings/urdu.yaml')
nagarip = graphparser.GraphParser('./graphparser/settings/devanagari.yaml')

def gen_hiur_lemmas_by_size():
    import codecs
    import sys
    sys.path.append('./graphparser/')
    import graphparser
    urdup = graphparser.GraphParser('./graphparser/settings/urdu.yaml')
    nagarip = graphparser.GraphParser('./graphparser/settings/devanagari.yaml')
    def out_hiur(w):
        return urdup.parse(w).output+' '+nagarip.parse(w).output+' '+w
    with codecs.open('output/lemmas-by-size-hiur.md','w','utf-8') as f:
        for x in sorted(lemma_instance_count, key=lemma_instance_count.get,reverse=True):
            words=lemmas_out[x]
            words = sorted(words,key=token_instance_count.get, reverse=True)

            f.write(out_hiur(x)+' '+str(lemma_instance_count[x])+'\n')
            for w in words:
                f.write("  - "+out_hiur(w)+' '+str(token_instance_count[w])+'\n')
                
def out_hiur(w):
    return urdup.parse(w).output+' '+nagarip.parse(w).output+' '+w

def out_hiur_csv(w):
    return urdup.parse(w).output+','+nagarip.parse(w).output+','+w
def html_out(w):
    return td(urdup.parse(w).output)+td(nagarip.parse(w).output)+td(w)

def td(x):
    return '<td>'+x+'</td>'

def li(x):
    return ('<li>'+x+'</li>')
def md_link(s,urdu=True):
    out =  " ["+s+"]"
    out += "("+'http://www.columbia.edu/itc/mealac/pritchett/00ghalib/'
    out += s[0:3]+'/'+s[0:3]+"_"+s[4:6]+".html"
    if urdu==True:
        out+="?urdu"
    out += ") "#
    return out
def a_link(s,urdu=False):
    out =  "<a href='http://www.columbia.edu/itc/mealac/pritchett/00ghalib/"
    out += s[0:3]+'/'+str(int(s[0:3]))+"_"+s[4:6]+".html"
    if urdu==True:
        output+="?urdu"
    out+="'>"
    out += s
    out+="</a>"
    return out

def gen_hiur_lemmas_by_size_hiur(file_name, with_verses=False, truncate=True,truncate_limit=50):

    with codecs.open(file_name,'w','utf-8') as f:
        for x in sorted(lemma_instance_count, key=lemma_instance_count.get,reverse=True):
            words=lemmas_out[x]
            words = sorted(words,key=token_instance_count.get, reverse=True)
            
            f.write(' '+out_hiur(x)+' '+str(lemma_instance_count[x])+'\n')

            for w in words:
                f.write("  - ")
                f.write("  - "+out_hiur(w)+' '+str(token_instance_count[w])+'\n')
                vi = set(x[:-5] for x in token_instances[w]) # eg001.01 from 001.01.01.0

                if with_verses==True:
                    if (truncate==False) or (truncate==True and len (vi)< truncate_limit):
    #                print list(vi)[0]
                        f.write("    - ")# nested indent
                        f.write(', '.join([md_link(v) for v in vi]))
                        f.write('\n')

def gen_hiur_lemmas_by_size_ul(file_name='output/hiur-lemmas-by-size-ul.html'):
    with codecs.open(file_name,'w','utf-8') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html lang="en-US">\n')
        f.write('<head><meta charset="utf-8"></head>\n')
        f.write('<body>\n')


        f.write('<table>\n')
        for x in sorted(lemma_instance_count, key=lemma_instance_count.get,reverse=True):
            words=lemmas_out[x]
            words = sorted(words,key=token_instance_count.get, reverse=True)
            f.write('<p><b>'+out_hiur(x)+' '+str(lemma_instance_count[x])+'</b></p>\n')
            f.write('<ul>\n')
            for w in words:
                f.write('<li>'+out_hiur(w)+' '+str(token_instance_count[w])+'</li>\n')
            f.write("</ul>")

        f.write("</body></html>")

def gen_hiur_lemmas(filename='output/hiur-lemmas.html'):
    with codecs.open(filename,'w','utf-8') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html lang="en-US">\n')
        f.write('<head><meta charset="utf-8"></head>\n')
        f.write("<body><table>")
        for l,tkns in sorted(lemmas_out.iteritems()):
            locs=[]
            for t in tkns:
                locs += [v[0:6] for v,t_x in tokens.iteritems() if t_x ==t]
            locs=sorted(list(set(sorted(locs))))
            hyperlocs = [a_link(loc,urdu=False) for loc in locs]
            f.write('<tr>'+td(l)+td(urdup.parse(l).output)+td(nagarip.parse(l).output)+td(', '.join(hyperlocs))+'</tr>\n')
#                    print l,urdup.parse(l).output,locs
        f.write("</table></body></html>")
gen_hiur_lemmas()    

# <codecell>

#gen_hiur_lemmas_by_size()
#gen_hiur_lemmas_by_size_with_verses()
#gen_hiur_lemmas_by_size_hiur('output/lemmas-by-size-w-verses-all-hiur.md', with_verses=True, truncate=False)#True,truncate_limit=50):
#gen_hiur_lemmas_by_size_hiur('output/lemmas-by-size-countsonly.md', with_verses=False)#True,truncate_limit=50):
gen_hiur_lemmas_by_size_ul()

# <codecell>

def gen_hiur_lemmas_by_size_md(file_name='output/hiur-lemmas-by-size.md'):
    with codecs.open(file_name,'w','utf-8') as f:
        f.write('# Lemmas and Tokens (Sorted by Number of Occurences)\n\n')
        for x in sorted(lemma_instance_count, key=lemma_instance_count.get,reverse=True):
            words=lemmas_out[x]
            words = sorted(words,key=token_instance_count.get, reverse=True)
            f.write('\n'+out_hiur(x)+' '+str(lemma_instance_count[x])+'\n')
            for w in words:
                f.write('* '+out_hiur(w)+' '+str(token_instance_count[w])+'\n')
                
gen_hiur_lemmas_by_size_md()

# <markdowncell>

# ##Experimenting with Lemma version of text (for topic modeling)

# <codecell>

def gen_documents(file_name = 'output/lemma_documents.txt'):
    with codecs.open(file_name,'w','utf-8') as f:
        it = iter(sorted(verses))
        for x in it:
            v_id0,v_id1 = x,next(it)
            #print v_id0,v_id1
            lemmastring = ''
            for v in [v_id0,v_id1]:
            #print v
                vtkns = [t for t in tokens if t.startswith(v)]
                for t in vtkns:
                    l = okay_lemmas[tokens[t]]
                    if len(l)>1:
                        while '-o-' in l[0]:
                            l=l[1:]
                    lemmas_out = ' '.join(l)
                    lemmastring+=' '+lemmas_out

            f.write(lemmastring+'\n')
gen_documents()

# <codecell>


# <codecell>

import PyICU
import PyICU
locale=PyICU.Locale('ur')
urdu_col = PyICU.Collator.createInstance(locale)

# <codecell>

import PyICU
locale=PyICU.Locale('ur')
urducol = PyICU.Collator.createInstance(locale)

# <codecell>

import graphparser
reload(graphparser)

urdup = graphparser.GraphParser('./graphparser/settings/urdu-diacritics.yaml')
urdudiacriticsp = graphparser.GraphParser('./graphparser/settings/urdu-diacritics.yaml')
#nagarip = graphparser.GraphParser('./graphparser/settings/devanagari.yaml')
lemmas_diacritics = {urdudiacriticsp.parse(x).output:x for x in lemmas_out }

urdu_lemmas = [urdup.parse(x).output for x in lemmas_out]
urdu_lemmas_sorted = sorted(urdu_lemmas,col.compare)

# <codecell>

col.compare('ب','ا')

# <codecell>

def gen_hiur_lemmas(filename='output/hiur-lemmas.html',sort='transliteration'):
    with codecs.open(filename,'w','utf-8') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html lang="en-US">\n')
        f.write('<head><meta charset="utf-8"></head>\n')
        f.write("<body><table>")
        assert sort in ['transliteration','urdu','devanagari']
        if sort=='transliteration':
            sorted_lemmas=sorted(lemmas_out.iteritems())
        elif sort=='urdu':
            import 
        for l,tkns in sorted(lemmas_out.iteritems()):
            locs=[]
            for t in tkns:
                locs += [v[0:6] for v,t_x in tokens.iteritems() if t_x ==t]
            locs=sorted(list(set(sorted(locs))))
            hyperlocs = [a_link(loc,urdu=False) for loc in locs]
            f.write('<tr>'+td(l)+td(urdup.parse(l).output)+td(nagarip.parse(l).output)+td(', '.join(hyperlocs))+'</tr>\n')
#                    print l,urdup.parse(l).output,locs
        f.write("</table></body></html>")
gen_hiur_lemmas()   

# <codecell>

for x in sorted(set([urdup.parse(t).output for t in tokens.values() if t.endswith('-e')] ), col.compare): print x

# <codecell>

import codecs
def gen_concordance(filename='output/concordance-urdu.html'):

    with codecs.open(filename,'w','utf-8') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html lang="ur-PK">\n')
        f.write('<head><meta charset="utf-8"></head>\n')
        f.write("<body><table>")
        for l_d in sorted(lemmas_diacritics,col.compare):
            tkns = lemmas_out[lemmas_diacritics[l_d]]
            
#        for l,tkns in sorted(lemmas_out.iteritems(),urducol.compare):
            locs=[]
            for t in tkns:
                locs += [v[0:6] for v,t_x in tokens.iteritems() if t_x ==t]
            locs=sorted(list(set(sorted(locs))))
            hyperlocs = [a_link(loc,urdu=False) for loc in locs]
            print ('<tr>'+td(l_d)+td(', '.join(hyperlocs))+'</tr>\n')
#                    print l,urdup.parse(l).output,locs
        f.write("</table></body></html>")
gen_concordance()

# <codecell>

lemmas_diacritics = {urdudiacriticsp.parse(x).output:x for x in lemmas_out }

# <codecell>

sorted(lemmas_diacritics.keys(),urducol.compare)

# <codecell>


