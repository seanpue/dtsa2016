import copy
import networkx as nx
import custom_meter_graph as cmg
import pandas as pd
import re

def get_hindi_scanner(count=None):
        hindi_scanner = copy.copy(get_hindi_scanner.orig_hindi_scanner)
        hindi_scanner.count = count
        return hindi_scanner
    

hindi_dg = nx.read_yaml('data/hindi_meter.yaml')    
hindi_scanner = cmg.CustomMeterGraph()
hindi_scanner.DG = hindi_dg
get_hindi_scanner.orig_hindi_scanner = hindi_scanner

#scanner = cmg.CustomMeterGraph()

def get_all_matra_counts(x, separator='\n'):
    return separator.join([str(cmg.get_matra_count(z)) for z in x.split(separator)])

def get_poss_scans(x,scanner=None):
    def splitup(x):
        return ','.join(sorted(set(x.split('\n'))))
    return splitup(get_all_matra_counts(scanner.get_all_scans_as_string(x)))

def get_line_scans(m, lines,scanner): # also needs scanner
    ''' takes a multiline match and extracts line-level scans'''
    tokens = []
    for line_id, line in enumerate(lines):
        for pos, token in enumerate(scanner.pp.tokenize(line)):
            token = {'pos':pos, 'line': line_id,'token':token}
            tokens.append(token)
    gls = pd.DataFrame(tokens)
    match_df = pd.DataFrame( (tuple(x) for x in m[0].matches), columns = m[0].matches[0]._fields)
    match_df['line'] = match_df.token_i.map(lambda x: gls.loc[x,'line'])
    line_scans = [''.join(match_df[match_df.line==l]['node_type'].values) for l in range(len(lines))]
    return line_scans



def get_hindi_count(x):
    hindi_re = 'hindi\s*(?:\[([0-9,]+)\])?'
    m = re.match(hindi_re,x)
    assert m
    if m.group(1):
        count = [int (x) for x in m.group(1).split(',')]
        return count
    return None


def get_scanner(meter):
    orig_meter = meter
    if meter==None:
        return None
    meter = meter.lower()
    meter = meter.strip()
    meter = meter.replace(' ','')
    meter = meter.replace('/','')
    assert type(meter) in [str,unicode]#==str
    if meter.startswith('hindi'):
        count = get_hindi_count(meter)
        return get_hindi_scanner(count=count)
    else:
        x = cmg.CustomMeterGraph(meter)
        if not x:
            print 'could not scan',meter
        return x

def scan_poet(poets,poet):
    
    x=poets[poet]# metadata = poets[poet]['metadata']
    metadata =  pd.DataFrame.from_csv(x['file_name_meta'],encoding='utf-16')#poets['miraji']['metadata']
    metadata.meter = metadata.meter.fillna('')
    wrangled = poets[poet]['wrangled']
    poems = metadata#[metadata.meter.str.startswith('Hindi')]
    titles_to_get = poems
    out = pd.DataFrame(columns=['poem','clean_transliteration','scan','matras','has_count'])
    for i, meta in titles_to_get.iterrows():
        poem = wrangled[wrangled.title==meta.urdu]
        scanner = get_scanner(meta.meter)
        print 'scanning ',i, meta
        if scanner:
            enjambment = meta.enjambment
            if enjambment: print enjambment
            scan_df = scan_to_df(i,poem,scanner,poss_scans=True, enjambment=enjambment)
            out = out.append(scan_df)
    out.scan = out.scan.map(lambda x: ' '+x)
    out = out[['poem','clean_transliteration','scan','matras','has_count','poss_scans']]
    return out


def scan_to_df(i,rows,scanner,show_all=False,poss_scans=False,enjambment=False, separator='\n'):

    def get_first_bad_cluster():
        clusters = []
        num_found = 0

        for i in range(i_start, len(check)):
            v = check[i]
            if (v == True):
                if num_found == 0:
                    start = i
                num_found+=1
                if i == len(check)-1:
                    clusters.append(range(start,len(check)))
                    return clusters[0]
            if (v == False):

                if num_found>0:
                    clusters.append(range(start,i))
                    return clusters[0]
                    num_found = 0
        return None

    def bad_cluster_generator():
        while True:
            bad_cluster = get_first_bad_cluster()
            if bad_cluster:
                yield bad_cluster
            else:
                raise StopIteration
    
    
        
    for i,row in rows.iterrows():
        clean_transliteration = row['clean_transliteration'].split('|')
        num_lines = len(clean_transliteration)
        poem = row['title']# * num_lines
        indexes = [str(i)+'.'+ str(x) for x in range(num_lines)]
        df = pd.DataFrame({'poem':poem,'clean_transliteration':clean_transliteration})#'urdu':row['urdu'],'clean_transliteration':clean_transliteration},columns=['poem','clean_transliteration'])#'transcription':transcription})#,index=indexes)#, columns=['clean_transliteration','transcription'])
        if show_all==False:
            df['scan'] = df['clean_transliteration'].map(scanner.get_scan_as_string)
            df['matras'] = df['scan'].map(cmg.get_matra_count)
        else:
            df['scan'] = df['clean_transliteration'].map(scanner.get_all_scans_as_string)
            df['matras'] = df['scan'].map(get_all_matra_counts)
        if poss_scans:
           df['poss_scans'] = df['clean_transliteration'].map(lambda x: get_poss_scans(x,scanner=scanner))
        
        df['has_count'] = str(scanner.count)
        df.index=indexes
        
        basic_df = df

        no_match = basic_df.scan==''
        
        if enjambment and len(no_match > 0):
            
            check = basic_df.scan==''

            i_start=0 # start of bad cluster checker

            for bad_cluster in bad_cluster_generator():

                cluster = bad_cluster
                to_try = []
                cluster_0 = cluster[0]
                # append next line

                # with next
                if cluster[-1]+1 < len(check):
                    cluster.append(cluster[-1]+1) #ma

                # without prev
                if len(cluster)>1:
                    for z in cluster[1:]:
                        to_try.append(range(cluster_0, z+1))
                # with prev
                if cluster_0 >0:
                    prev = cluster_0-1
                    for z in cluster:
                        to_try.append(range(prev,z+1))


                matched=False
                while matched==False and len(to_try)>0:
                    x = to_try.pop()
                    lines = basic_df.iloc[x]['clean_transliteration'].values

                    phrase = ''.join(lines)#basic_df.iloc[x]['clean_transliteration'].values)
                    m = scanner.graph_scan(phrase)
                    if m:
                        basic_df.ix[x, 'scan'] = get_line_scans(m,lines,scanner)
                        i_start = x[-1]

                i_start+=1
                
    df['has_count'] = str(scanner.count)
    df.index=indexes
    return df
