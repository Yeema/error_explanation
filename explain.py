from collections import defaultdict
from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
import spacy
import json 

nlp = spacy.load('en')
wordnet_lemmatizer = WordNetLemmatizer()
dictWord = eval(open('GPs.txt', 'r').read())
phraseV = eval(open('phrase.txt', 'r').read())
ex_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
with open('explain_dict.json') as f:
    tmp_ex_dict = json.load(f)
for cat, ex in tmp_ex_dict.items():
    for key,wrong_key in ex.items():
        for w_key,heads in wrong_key.items():
            for headkey, explains in heads.items():
                for explain , worong_sent in explains.items():
                    ex_dict[cat][key][w_key][headkey][explain].append(worong_sent)
                    
with open('tagMap.json') as f:
    tagMap = json.load(f)
# DET PREP PART PUNCT
pos_map = {'N':'NOUN','J':'ADJ','V':'VERB'}
def printInfo(decode,correct,wrong,head):
    for key in ex_dict[decode][correct] [wrong][head].keys():
        print('[explain]: %s'%('\n'.join(key.split(';'))))
        if head in dictWord['N']:
            for pats , example , sent  in dictWord['N'][head]: 
                pat , ratio = pats.split('%')
                example = ' , '.join(example)
                print("%s%%\t%s  %s : %s -> %s"%(ratio,pat,example,sent[0],sent[1]))
        if head in dictWord['V']:
            for pats , example , sent  in dictWord['V'][head]: 
                pat , ratio = pats.split('%')
                example = ' , '.join(example)
                print("%s%%\t%s  %s : %s -> %s"%(ratio,pat,example,sent[0],sent[1]))
        if head in dictWord['ADJ']:
            for pats , example , sent  in dictWord['ADJ'][head]: 
                pat , ratio = pats.split('%')
                example = ' , '.join(example)
                print("%s%%\t%s  %s : %s -> %s"%(ratio,pat,example,sent[0],sent[1]))

def lookup(decode,wrong,correct,finding,tag):
#     if wrong in tagMap:
    if wrong!="NONE":
        wrong = wordnet_lemmatizer.lemmatize(wrong ,pos='v')
    if correct!="NONE":
        correct = wordnet_lemmatizer.lemmatize(correct ,pos='v')
    if decode[:2] == 'M:':
        decode += tag
        heads = list(ex_dict[decode][correct] [wrong].keys())
        new_decode = "R:"+tag
        m2r = ex_dict[new_decode][correct].items()
        heads.extend( [v  for key,val in ex_dict[new_decode][correct].items() for v in val])
    else:
        decode += tag
        heads = ex_dict[decode][correct] [wrong].keys()
    flag = True
    for head in heads:
        if head in correction:
            printInfo(decode,correct,wrong,head)
            flag = False
            break
    if flag:
        if delete-2<0:
            start = 0
        else:
            start = delete-2
        if delete+3>len(token_o):
            end = 0
        else:
            end = delete+2
        for f in finding:  
            for head in heads:
                if head == wordnet_lemmatizer.lemmatize(str(f) ,pos='v'):
                    printInfo(decode,correct,wrong,head)

def cal_explain(original,correction):
    token_o = word_tokenize(original)
    token_c = word_tokenize(correction)
    if '[' in token_c:
        deletes = [id for id, c in enumerate(token_c) if c == '[']
    else:
        deletes = []
    if '{' in token_c:
        adds = [id for id, c in enumerate(token_c) if c == '{']
    else:
        adds = []
    tags = pos_tag(token_o)
    tags_correction = pos_tag(token_c)
    len_d = len(deletes)
    len_a = len(adds)
    i = 0 
    j = 0 
    decodes = []
    while i<len_d and j<len_a:
        if i<=j:
            if deletes[i]+3==adds[j]:
                decodes.append(('R:',deletes[i],adds[j]))
                i+=1
                j+=1
            else:
                decodes.append(('U:',deletes[i],-1))
                i+=1
        else:
            decodes.append(('M:',-1,adds[j]))
            j+=1
    while i<len_d:
        decodes.append(('U:',deletes[i],-1))
        i+=1
    while j<len_a:
        decodes.append(('M:',-1,adds[j]))
        j+=1
    flag = True
    print(original , '\n',correction)
    original_splits = original.split()
    # if delete != 0 and add != 0: 
    for decode,delete,add in decodes:
    #     if delete ==-1:
        if decode == 'M:':
            correct = token_c[add+1][1:-1]
    #         depend on correct
            correct_string = ' '.join(token_c).replace('{ +','').replace('+ }','')
            finding = []
            doc = nlp(correct_string)
            finding.extend([anc.text for anc in list(doc[token_c.index('+'+correct+'+')-4].ancestors)])
            finding.extend([child.text for child in list(doc[token_c.index('+'+correct+'+')-4].children)])
            finding.append(correct)
            if correct in tagMap:
                lookup(decode,"NONE",correct,finding,tagMap[correct])
            elif tags_correction[add+1][1][0] in pos_map:
                lookup(decode,"NONE",correct,finding,pos_map[tags_correction[add+1][1][0]])
    #     elif add ==-1:
        elif decode == 'U:':
            wrong = token_c[delete+1][1:-1]
            correct = 'NONE'
            doc = nlp(original)
            finding = []
    #         depend on wrong
            finding.extend([anc.text for anc in list(doc[token_o.index(wrong)].ancestors)])
            finding.extend([child.text for child in list(doc[token_o.index(wrong)].children)])
            if correct in tagMap:
                lookup(decode,wrong,correct,finding,tagMap[wrong])
            elif tags_correction[delete+1][1][0] in pos_map:
                lookup(decode,wrong,correct,finding,pos_map[tags_correction[delete+1][1][0]])
    #     elif delete+3 == add:
        elif decode == 'R:':
            wrong = token_c[delete+1][1:-1]
            correct = token_c[add+1][1:-1]
    #         depend on correct
            no_wrong_token = token_c[:delete]+token_c[delete+3:]
            correct_string = ' '.join(no_wrong_token).replace('{ +','').replace('+ }','')
            finding = []
            doc = nlp(correct_string)
            finding.append(correct)
            finding.extend([anc.text for anc in list(doc[token_c.index('+'+correct+'+')-4].ancestors)])
            finding.extend([child.text for child in list(doc[token_c.index('+'+correct+'+')-4].children)])
            if correct in tagMap:
                lookup(decode,wrong,correct,finding,tagMap[wrong])
            elif tags_correction[delete+1][1][0] in pos_map:
                lookup(decode,wrong,correct,finding,pos_map[tags_correction[delete+1][1][0]])
    


if __name__ == '__main__':
    testcases = [('We discussed about the issue .','We discussed [-about-] the issue .'),\
    ("The train arrived at exactly twelve past three .","The train arrived at exactly twelve {+minutes+} past three."),\
    ("I am a honest teacher.","I am [-a-] {+an+} honest teacher."),\
    ("School finishes at five in morning .","School finishes at five in {+the+} morning .")]
    for id,(original,correction) in enumerate(testcases):
        print('case',id)
        cal_explain(original,correction)
        print()
    