'''
this file is used to compare papers in the referred directory and the papers listed in a txt files.
We do this to check if we have downloaded all papers listed in the txt file into the directory
'''

import os
import os.path as osp

def compactName(raw):
    paper=raw.lower()
    paper=' '.join(paper.split('_'))
    paper=''.join(paper.split(':'))
    return paper

def compareName(name):
    return ''.join(name.split(' '))

def compare(dir,compare_txt):
    with open(compare_txt,'r') as f:
        txt_papers=f.readlines()
    txt_papers=[paper  for paper in txt_papers if paper.strip()!=''] #filter blank lines
    # print(papers)
    numTxt=len(txt_papers)
    dir_papers=os.listdir(dir)
    numDir=len(dir_papers)
    print('there are a total of {} papers in the {} directory'.format(numDir,dir))
    print('there are a total of {} papers listed in the {}'.format(numTxt,compare_txt))
    papers=[paper.strip().split('.')[0].split('?')[0] for paper in txt_papers]
    # print(papers)
    dpapers=[compactName(paper.strip().split('.')[0].split('?')[0]) for paper in sorted(dir_papers)]
    cdpapers=[compareName(paper) for paper in dpapers]
    # print(dpapers)
    tpapers=[compactName(paper) for paper in sorted(papers)]
    ctpapers=[compareName(paper) for paper in tpapers]
    # print(tpapers)
    # counter=0
    dunique=[]
    for paper in cdpapers:
        if paper not in ctpapers:
            dunique.append(dpapers[cdpapers.index(paper)])
    print('-------------------------')
    print('there are {} papers unique in the {}:'.format(len(dunique),dir))
    for paper in dunique:
        print(paper)
    tunique=[]
    for paper in ctpapers:
        if paper not in cdpapers:
            tunique.append(tpapers[ctpapers.index(paper)])
    print('-------------------------')
    print('there are {} papers unique in the {}:'.format(len(tunique),compare_txt))
    for paper in tunique:
        print(paper)
    
    for i in range(len(ctpapers)):
        for j in range(len(ctpapers)):
            if i!=j and ctpapers[i]==ctpapers[j]:
                print(i,j)
                print(tpapers[i])

if __name__=='__main__':
    path='applications'
    compare_txt='applications.txt'
    compare(path,compare_txt)