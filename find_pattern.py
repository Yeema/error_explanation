import sys
from collections import defaultdict,Counter
from pprint import pprint
from functools import partial
import sys,re
from collections import Counter, defaultdict
from itertools import groupby
import json
# from pgrules import isverbpat
pgPreps = 'under|without|around|round|in_favor_of|_|about|after|against|among|as|at|between|behind|by|for|from|in|into|of|on|upon|over|through|to|toward|off|on|across|towards|with|out'.split('|')
otherPreps ='out|off|down|up|across'.split('|')
reservedWords = 'how wh; who wh; what wh; when wh; someway someway; together together; enoguh enough; amount amount; that that'.split('; ')
pronOBJ = ['me', 'us', 'you', 'him', 'them']
collin_res=set([ 'off',  'on', 'amount', 'behind', 'into', 'towards', 'be', 'past', 'for', 'though', 'within', 'down',  'between', 'from', 'as', 'there', 'with', 'across', 'like', 'without',  'through', 'before', 'by', 'of', 'together', 'against', 'that', 'about', 'favour', 'under', 'among', 'onto', 'over', 'the', 'how', 'after', 'and', 'at', 'in', 'to'])
def isverbpat(key,pat):
    verbs = word2pat[key]['V']
    if pat == 'adv V' or pat =='adv V':
        return True
    if verbs:
        for prep in pgPreps:
            if pat.replace(prep,'prep') in verbs:
                return True
        return  pat in verbs or pat.replace('adv V','V') in verbs or pat.replace('V adv','V') in verbs or pat.replace('amount','n') in verbs 
    else:
        if len(pat.split())>1:
            ispreps = pat.split()[1:]
            cat_preps = []
            for isprep in ispreps:
                if  isprep in pgPreps:
                    cat_preps.append(isprep)
                    if word2pat[pat.split()[0]+' '+' '.join(cat_preps)]['V']:
                        pat = ' '.join([p for id , p in enumerate (pat.split()) if id>len(cat_preps) or id==0])
                        return  pat in verbs or pat.replace('adv V','V') in verbs or pat.replace('V adv','V') in verbs or pat.replace('amount','n') in verbs 
                else:
                    break
        return False
def isnounpat(key,pat):
    nouns = word2pat[key]['N']
    if nouns:
        for prep in pgPreps:
            if pat.replace(prep,'prep') in nouns:
                return True
        return  pat in nouns or pat.replace('v','be') in nouns or pat.replace('adj N','N') in nouns or pat.replace('adj N','N')=='N' or pat.replace('amount','n') in nouns or pat.replace('N of n','N') in nouns or pat.replace('N of n','N')=='N'
    else:
        return False
def isadjpat(key,pat):
    adjs = word2pat[key]['ADJ']
#     print(key,pat,adjs)
    if pat == 'ADJ n':
        return True
    if adjs:
        for prep in pgPreps:
            if pat.replace(prep,'prep') in adjs:
                return True
        return  pat in adjs or pat.replace('v','be') in adjs or pat.replace('amount','n') in adjs
    else:
        return False

maxDegree = 9

def sentence_to_ngram(words, lemmas, tags, chunks): 
    return [ (k, k+degree) for k in range(1,len(words)) for degree in range(2, min(maxDegree, len(words)-k+1)) ]

mapHead = dict( [('H-NP', 'N'), ('H-VP', 'V'), ('H-ADJP', 'ADJ'), ('H-ADVP', 'ADV'), ('H-VB', 'V')] )
mapRest = dict( [('VBG', '-ing'), ('VBD', 'V-ed'), ('VBN', 'V-ed'), ('VB', 'v'), ('NN', 'n'), ('NNS', 'n'), ('JJ', 'adj'), ('RB', 'adv'),
                    ('NP', 'n'), ('VP', 'v'), ('JP', 'adj'), ('ADJP', 'adj'), ('ADVP', 'adv'), ('SBAR', 'that')] )

mapRW = dict( [ pair.split() for pair in reservedWords ] )
mode = ''
def hasTwoObjs(tag, chunk):
    if chunk[-1] != 'H-NP': return False
    return (len(tag) > 1 and tag[0] in pronOBJ) or (len(tag) > 1 and 'DT' in tag[1:])
output = set()    
def chunk_to_element(words, lemmas, tags, chunks, i, isHead):
    if isHead:
        if len(chunks[i][-1])>3:
            # print('chunk',chunks[i][-1])
            if chunks[i][-1][2]=='V':
                return 'V'
            elif chunks[i][-1][2]=='N':
                return 'N'
            elif chunks[i][-1][2:5]=='ADJ':
                return 'ADJ'
            elif lemmas[i][-1] in pgPreps:
                return lemmas[i][-1]
    if lemmas[i][0] == 'favour' and words[i-1][-1]=='in' and words[i+1][0]=='of': return 'favour'
    if tags[i][-1] == 'RP' and tags[i-1][-1][:2] == 'VB':                return '_'
    if tags[i][0][0] in ['W','R'] and lemmas[i][-1] in mapRW:                    return mapRW[lemmas[i][-1]]
    if tags[i][0]=='CD': return 'amount'
    if hasTwoObjs(tags[i], chunks[i]):                                              return 'n n'
    if tags[i][-1] in mapRest:                            return mapRest[tags[i][-1]]
    if tags[i][-1][:2] in mapRest:                        return mapRest[tags[i][-1][:2]]
    if chunks[i][-1] in mapHead:                            return mapHead[chunks[i][-1]].lower()
    if lemmas[i][-1] in pgPreps:                                         return lemmas[i][-1]
    if lemmas[i][-1] in collin_res:
        return lemmas[i][-1]
    return lemmas[i][-1]

def simplifyPat(pat): 
    if pat == 'V ,':
        return 'V'
    elif pat =='N ,':
        return 'N'
    elif pat =='J ,':
        return 'ADJ'
    else:
        return pat.replace(' _', '').replace('_', ' ').replace('  ', ' ')

def ngram_to_pat(words, lemmas, tags, chunks, start, end):
    pat, doneHead = [], False
    for i in range(start, end):
        isHead = tags[i][-1][0] in ['V','J','N'] and not doneHead
        pat.append( chunk_to_element(words, lemmas, tags, chunks, i, isHead) )
        if isHead: doneHead = True
    pat = simplifyPat(' '.join(pat))
    tmp_pat= []
    for p in pat.split():
        if not tmp_pat:
            tmp_pat.append(p)
        else:
            if p!=tmp_pat[-1]:
                tmp_pat.append(p)
    pat = ' '.join(tmp_pat)
    if isverbpat(lemmas[start][0],pat):
        mode = 'V'
        return pat
    elif isnounpat(lemmas[start][0],pat):
        mode = 'N'
        return pat
    elif isadjpat(lemmas[start][0],pat):
        mode = 'ADJ'
        return pat
    else: ''
def get_mode():
    return mode
def ngram_to_head(words, lemmas, tags, chunks, start, end):
    for i in range(start, end):
        # if len(tags)>i+1:
        #     if tags[i][-1][0] in 'V' and tags[i+1][-1]=='RP':  
        #         return tags[i][-1][0],lemmas[i][-1].upper()+ ('_'+lemmas[i+1][-1].upper())
        if tags[i][-1][0] in ['V','N','J']:  
            return tags[i][-1][0],lemmas[i][-1].upper()
        else: return ""
        
word2pat = defaultdict(lambda: defaultdict (list))
with open('word2pattern.json',encoding = 'utf-8') as outfile:
        tmp_dict = json.load(outfile)
for head,tmp in tmp_dict.items():
    for part,grammar in tmp.items():
        word2pat[head][part]=grammar

if __name__ == "__main__":
    cor_pat = []
    lines = open('explain_cor_pat.txt','r').readlines()
    heads = open('explain_head.txt','r').readlines()
    # print('hi')
    for id,line in enumerate(lines):
        tmp_cor_pat = []
        parse = eval(line.strip())
        parse = [ [y.split() for y in x]  for x in parse ]
        for start, end in sentence_to_ngram(*parse):
            pat = ngram_to_pat(*parse, start, end)
            if pat: 
                if ngram_to_head(*parse, start, end):
                    mode,head = ngram_to_head(*parse, start, end)
                    if head.lower() in word2pat:
                        pat_short_ex = ' '.join([' '.join(x) for x in parse[0][start:end] ])
                        if pat_short_ex:
                            print(line)
                            print(heads[id], pat,'        ',pat_short_ex)
                            print()
                            if heads[id] in pat_short_ex:
                                if not any(special in pat_short_ex for special in [',','.',';',':','(',')']):
                                    tmp_cor_pat.append([mode,pat,pat_short_ex])
                                    # if head.lower()=='introduce':
                                    # print(head.lower(),mode,pat,pat_short_ex)
        cor_pat.append(tmp_cor_pat)
    with open('cor_pat.json', 'w') as outfile:
        json.dump(cor_pat, outfile) 
