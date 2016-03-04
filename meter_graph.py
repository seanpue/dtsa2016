import networkx as nx
import matplotlib.pyplot as plt 
import settings
from graphparser import GraphParser

# create digraph of meters (DG) using networkx
# each node has a type (=,-, and 0 [for the first one])
# the node at the end of each meter has a meter_type and meter_full_description attribute

from collections import namedtuple

ScanResult = namedtuple('ScanResult',["scan","matches", "meter_type"]) # used for completed scans
NodeMatch  = namedtuple('NodeMatch', ["node_type",       # = or -
                                      "matched_tokens",  # tokens matched at node
                                      "node_id",         # id of node in graph
                                      "orig_tokens",     # original tokens that were matched
                                      "found",      # production of parser 
                                      "token_i"])        # used for matches at nodes in graph
 
class MeterGraph:
    
    def __init__(self):

        self.DG = self.create_graph()
        self.pp = GraphParser('settings/urdu-meter.yaml',blank=' ')
        self.lp = GraphParser('settings/long.yaml',blank='b')
        self.sp = GraphParser('settings/short.yaml',blank='b')

    def create_graph(self):
        DG=nx.DiGraph()
        
        DG.add_node(0,type='0') # this is the start
        
        for meter in settings.meters_with_feet:
            
            meter_type = settings.meters_with_feet[meter]
            meter_full_description = meter
            
            meter = meter.replace('/','') # ignore feet denominator for now
            
            node_id = 0
            
            curr_node = 0
            
            
            for i,c in enumerate(meter):
        
                found_it = False
        
                for n in DG.successors(curr_node):
        
                    node = DG.node[n]
        
                    if node['type']==c:
                        curr_node = n
                        found_it = True
                        break
        
                if found_it==False:
                    new_node = len(DG.nodes())            
                    DG.add_node(new_node, type=c)            
                    DG.add_edge(curr_node,new_node)
                    
                    # now add restraints to edge, this is a 'bad_combo' attribute 
                  #  print DG.node[curr_node]['type']
                    old_c = DG.node[curr_node]['type']
                    if (old_c,c) in settings.bad_types:
                        DG[curr_node][new_node]['bad_combos'] = settings.bad_types[(old_c, c)]
               #         print 'yes found ',old_c,c, bad_types[(old_c,c)]
                    curr_node = new_node
                if i==len(meter)-1: # store some metrical data at the last node
                    DG.node[curr_node]['meter_type'] = meter_type
                    DG.node[curr_node]['meter_full_description'] = meter_full_description
        return DG

# this is the graph scan.
     
    def graph_scan(self, in_string): 

        completed_scans = [] # holds complete scans
        
        #from collections import namedtuple
        
        # this is the scan of the input string to bcv, etc.
    #    scan = pp.parse(in_string)
        parse = self.pp.parse(in_string) # holds output, matches
        #pd = pp.parse_details # details on the matched tokens, rules, etc.
        
        # this generates scan_tokens from the scan of the input string, e.g. ['b','c','v'], using the long parser (lp)
        scan_tokens = self.lp.tokenize(parse.output)
       # print scan_tokens
     #   print 'scan_tokens are ',scan_tokens
        # This is a check to see that the short and long parsers match
        # TODO: remove later
        
    #    import collections
    #    assert collections.Counter(scan_tokens) == collections.Counter(lp.tokenize(scan))
        
        # this function descends into node (node_id), passing current token_i, matches, and a string represent
        def descend_node(node_id, token_i, matches, matched_so_far):
      
            for successor_id in self.DG.successors(node_id):
       #         print "  in successor ",successor_id, DG.node[successor_id]
    #            print scan_tokens
    #            print "\nDESCENDED INTO node, ", node_id, DG.node[node_id], "token_i ",token_i
    #            print "  So far ",matched_so_far
                node_type = self.DG.node[successor_id]['type']
                assert node_type in ('=','-')
                
                if node_type=='=': 
        #            print 'using lp'
                    parser = self.lp
                else:
         #           print 'using sp'
                    parser = self.sp
                
    #            print "  TRYING ",node_type, " from node ", node_id
                # for each match m at token_i of scan_tokens 
                # m contains ['tokens', 'start', 'rule_id', 'rule']
                # m['rule'] contain ['tokens', 'production']
                # TODO: declunkify.
        #       print ".. here , at ", token_i," of ", scan_tokens, "parser finds: ",parser.match_all_at(scan_tokens, token_i)
                for m in parser.match_all_at(scan_tokens, token_i):
    #                print '   matched ', m.tokens, m.production
                    # next, check to make sure that this is not a bad combination
                    # do so by looking for constraints on the edge
                    # note: this could be added as a constraint to match_all_at() as not_starting_with ...

                    if len(matches)>0: # if already matched something
                        a = matches[-1].found # details of previous match
                        b = m.production#**['rule']['production']   # details of current match 
                        if 'bad_combos' in self.DG[node_id][successor_id]: # if 'bad_combos' in the a,b's edge
   #                         print ' WARNING! BAD COMBO',a,b
   #                         print ' matches are ... '
    #                        print matches
                          #  print 'checking bad combos at ',node_id, successor_id
                          #  print 'trying ',(a,b,'in ',self.DG[node_id][successor_id]['bad_combos']

                            if (a,b) in self.DG[node_id][successor_id]['bad_combos']: # if it's bad
            
                          #      print '   aborting! found ',a,b
                                continue # abort! bad combination

                    # determine orig_tokens
                    # meaning, what is matched from original input and parsed to b,c,s, etc.
        
                    orig_tokens =[]
                    for i in range(token_i, token_i+len(m.tokens)):#['tokens'])):
                        #parse = pp.parse(in_string)
                        #print type(parse.matches[i].tokens)
                        orig_tokens.append(parse.matches[i].tokens)
    #                    orig_tokens.append(pd[i]['rule']['tokens'])  ## parser details here
                        # this will break if 'rule' is None
                        
    #                    except TypeError:
    #                        print 'error','i=',i
    #                        print 'pd[]i]',pd[i]
    #                        print 'error',m['tokens'], 'i',i
    #                        rule','tokens',"\n",m
     
                    # advance token index based on length of match tokens
                    
                    

                    
                    
                    
                    # generate match data
                    
                    matched_tokens = m.tokens
    #                print "   accepting ",matched_tokens
                    match_data = NodeMatch(node_type=node_type,
                                           matched_tokens = matched_tokens,
                                           node_id=node_id,
                                           orig_tokens=orig_tokens,
                                           found=m.production,
                                           token_i=token_i)
    #                print matches
    #                print match_data
        #            print match_data
                    # advance token_i 
                    
                    new_token_i = token_i + len(matched_tokens)
                    
                 ##   matches.append(match_data)
                    
                    so_far=matched_so_far + node_type
                    
                    #print ' so far',so_far
     
                    # if we're at the end
                    curr_matches = list(matches)
                    #print "curr = ",matches
                    curr_matches.append(match_data)
                    #print "~~~~\n",curr_matches
                    
                   # print curr_matches
                    if new_token_i == len(scan_tokens) and 'meter_type' in self.DG.node[successor_id]:
                        #and 'meter_type' in DG.node[s]:# and len(DG.successors(s))==0:
                        #print 'made it!', successor_id, DG.successors(successor_id),DG.node[successor_id], so_far
                        completed_scans.append(ScanResult(scan=so_far, matches=curr_matches, meter_type=self.DG.node[successor_id]['meter_type']))
                        #,"matches"]) # used for completed scans

                   #     for x in matches:
                   #         print x

                        match_node = successor_id
                        #print DG.node(match_node,data=True)#[match_node]
                    else:                  
                        descend_node(successor_id, new_token_i,curr_matches,so_far)
        # start descent into node 0 of the graph, at token_i 0, with no matches       
        descend_node(0, 0, [], '')

        return completed_scans

    def draw_graph(self):

        g = self.DG

        pos=nx.spring_layout(g)
    
        plt.figure(figsize=(15,15))

        labels=dict((n,d['type']) for n,d in g.nodes(data=True)) # need to change labels for 0,1,etc.

        nx.draw(g,labels=labels,node_color='#A0CBE2',node_size=200)

if __name__ == '__main__':
    gp = MeterGraph()
    gp.draw_graph()
    s=' dost ;gam-;xvaarii me;n merii sa((y farmaave;nge kyaa'#daa;g garm-e koshish-e iijaad-e daa;g-e taazah thaa'#dost ;gam-;xvaarii me;n merii sa((ii farmaave;nge kyaa'#hai ;xabar garm un ke aane kii'#;haq to yuu;n hai kih ;haq adaa nah hu))aa'# ja;zbah-e be-i;xtiyaar-e shauq dekhaa chaahiye'
    print(gp.pp.parse(s))
    print(s)
    translations = gp.graph_scan(s)
    for t in translations:
        print(t.scan,t.meter_type)
        for m in t.matches: print(m)

    import pprint
    print(settings.bad_types)
