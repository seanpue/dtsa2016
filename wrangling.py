#poets, !/usr/bin/env python
# -*- coding: utf-8 -*-


# Random functions to clean up text.
import pandas as pd
import re
def cleanup_urdu_lines(urdu):
    ''' 
    Removes whitespaces in the hopes of matching with transliteration for side-by-side comparison
    '''
    output=[]
    punctuation=u'۔۔. '+u'\t'
    urdu_lines = urdu.split('|')
    for l in urdu_lines:
        l= l.strip()
        if len(l)==0: continue#l.i =='':continue
        if all([c in punctuation for c in l]):
            continue
        output.append(l)
        
    return u'|'.join(output)
    


def cleanup_lines(transliteration):
    output = []
    translit_lines = transliteration.split('|')
    for l in translit_lines:
#        l=l.strip()
        l= re.sub('------','',l)
        if l in ['------','----']:
            l = ''
        l=re.sub('\?',' ',l)
        l=re.sub('[:;\)"]+\s*$','',l)
        l=re.sub('[,:;)]+\s*$','',l)
        
        l=re.sub(' i;nb',' imb',l)   # fix for i;mbisaat - need to resolve; cannot be nasalized?
        l=re.sub(';o','u',l)
        l=re.sub(';e','i',l)

##        l=re.sub('\)$','',l)
        l=re.sub('\)$','',l)
        l=re.sub(',',' ',l)
        
        l=re.sub('--',' ',l)
        l=re.sub('"',' ',l)
        l=re.sub("''", ' ',l)
        l=re.sub('!',' ',l)
        l=re.sub(' : ',' ',l)
        l=re.sub(' \) ',' ',l)

        l=re.sub('; ',' ',l)
        
        l=re.sub('\s+',' ',l)
        l=re.sub('_','-',l)
#        l=re.sub('sa;nbhal','sambhal',l)
        l=re.sub('[0-9]','',l)
        l= l.strip()
        l=' '+l
        
        
        if l != ' ':
            output.append(l)
    return '|'.join(output)

def transcribe_lines(clean_transliteration):
    translit_lines = clean_transliteration.split('|')
    return '|'.join( [pp.parse(l).output for l in translit_lines])


def basic_df_from_rows(rows):
    '''
    Generates a df with index as poem.line#; 
    '''
    out = pd.DataFrame(columns=['poem','clean_transliteration'])#,'transcription'])\
    clean_transliteration = row['clean_transliteration'].split('|')

    for i,row in rows.iterrows():
        clean_transliteration = row['clean_transliteration'].split('|')
        num_lines = len(clean_transliteration)
        poems = row['title']# * num_lines
        indexes = [str(i)+'.'+ str(x) for x in range(num_lines)]
        df = pd.DataFrame({'poem':poems,'urdu':urdu,'clean_transliteration':clean_transliteration},columns=['poem','clean_transliteration'])#'transcription':transcription})#,index=indexes)#, columns=['clean_transliteration','transcription'])
        df.index=indexes
        out=pd.concat([out,df])
    return out

def number_poem_tokens(poems_data):
    '''
    returns a data based on lines rather than poems
    poem title; line number; 
    '''
    poems_data['idx']=''
    
    title_rows = poems_data[ poems_data['type']=='TITLE' ]
    
    for t_i,(t_ix, t_row) in enumerate(title_rows.iterrows()):

        title_rows_ix = title_rows.index.values

        is_last = t_ix==title_rows_ix[-1]

        if is_last:
            poem_data = poems_data[t_ix:]
        else:
            poem_data = poems_data[t_ix:title_rows_ix[t_i+1]]

        line_rows = poem_data[ poem_data['type'] == 'LINE']
        
        urdu_str = '|'.join([x for x in line_rows['urdu'].values])
        
        translit_str = ''

        for l_i,(l_ix, l_row) in enumerate(line_rows.iterrows()):

            line_rows_ix = line_rows.index.values

            is_last = l_ix==line_rows_ix[-1]

            if is_last:
                end=-1
                line_data = poem_data[l_ix:]
            else:
                line_data = poems_data[l_ix:line_rows_ix[l_i+1] ] # poems_data vs poem makes a difference here

            tokens = line_data[ line_data['type'] == 'TOKEN' ] # .astype(str) # convert to string
            poems_data.loc[tokens.index,'idx'] = [str(t_i)+'.'+str(l_i)+'.'+str(i) for i,(t_ix, t_row) in enumerate(tokens.iterrows())]# = [t_ix for ti_x, t_row in tokens.iterrows()]

    return poems_data


def basic_df_from_rows(rows):
    '''
    Generates a df with index as poem.line#; 
    '''
    out = pd.DataFrame(columns=['poem','clean_transliteration'])#,'transcription'])\
    for i,row in rows.iterrows():
        clean_transliteration = row['clean_transliteration'].split('|')
        num_lines = len(clean_transliteration)
        poems = row['title']# * num_lines
        indexes = [str(i)+'.'+ str(x) for x in range(num_lines)]
        df = pd.DataFrame({'poem':poems,'urdu':row['urdu'],'clean_transliteration':clean_transliteration},columns=['poem','clean_transliteration'])#'transcription':transcription})#,index=indexes)#, columns=['clean_transliteration','transcription'])
        df.index=indexes
        out=pd.concat([out,df])
    return out

def basic_df_from_series(rows):
    '''
    Generates a df with index as poem.line#; 
    '''
    out = pd.DataFrame(columns=['poem','clean_transliteration'])#,'transcription'])\
    for i,row in rows.iteritems():
        clean_transliteration = row['clean_transliteration'].split('|')
        num_lines = len(clean_transliteration)
        poems = row['title']# * num_lines
        indexes = [str(i)+'.'+ str(x) for x in range(num_lines)]
        df = pd.DataFrame({'poem':poems,'urdu':row['urdu'],'clean_transliteration':clean_transliteration},columns=['poem','clean_transliteration'])#'transcription':transcription})#,index=indexes)#, columns=['clean_transliteration','transcription'])
        df.index=indexes
        out=pd.concat([out,df])
    return out

def wrangle_poems(poems_data):
    '''
    returns a dataframe based on lines rather than poems
    poem title; line number; 
    '''
    poems_data.fillna('',inplace=True)
    poems = []
    title_rows = poems_data[ poems_data['type']=='TITLE' ]
    
    for t_i,(t_ix, t_row) in enumerate(title_rows.iterrows()):
        title_rows_ix = title_rows.index.values

        is_last = t_ix==title_rows_ix[-1]

        if is_last:
            poem_data = poems_data[t_ix:]
        else:
            poem_data = poems_data[t_ix:title_rows_ix[t_i+1]]


        line_rows = poem_data[ poem_data['type'] == 'LINE']
        
        urdu_str = u'|'.join([x for x in line_rows['urdu'].values])
        
        translit_str = ''

        for l_i,(l_ix, l_row) in enumerate(line_rows.iterrows()):
#            print l_i,(l_ix,l_row)
            line_rows_ix = line_rows.index.values

            is_last = l_ix==line_rows_ix[-1]

            if is_last:
                end=-1
                line_data = poem_data[l_ix:]
            else:

                line_data = poems_data[l_ix:line_rows_ix[l_i+1] ] # poems_data vs poem makes a difference here

            tokens = line_data[ line_data['type'] == 'TOKEN' ] # convert to string
            
            translit_str += u' '.join(tokens['transliteration'])+'|'

        poems.append( {'title': t_row['urdu'], 
                       'transliteration': translit_str,
                       'urdu': urdu_str}
                    )
        
    poems_df = pd.DataFrame(poems)
    poems_df['clean_transliteration'] = poems_df['transliteration'].map(cleanup_lines)
    poems_df['clean_urdu'] = poems_df['urdu'].map(cleanup_urdu_lines)
    return poems_df

def load_poets(poets,encoding='utf-16',just_poet=None):
    '''
    adds a *wrangled* and a *metadata* field to poets
    
    wrangled calls *wrangle_poems* on poets[file_name]
    
    '''
#    global poets
#    assert poets
    toload = poets
    if just_poet:
        toload = [just_poet]
    for p in toload:
        print 'loading poet ',p
        x = poets[p]
        poems_metadata = pd.DataFrame.from_csv(x['file_name_meta'],encoding=encoding)
        poems_data = pd.DataFrame.from_csv(x['file_name'],encoding=encoding)
        wrangled = wrangle_poems(poems_data)
        poets[p]['wrangled']=wrangled
        poets[p]['metadata'] = poems_metadata
    return poets


