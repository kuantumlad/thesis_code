#!/usr/bin/python

import sys, ROOT

def getObjects(directory, objs={}):
  for kk in directory.GetListOfKeys():
    obj = kk.ReadObj()
    try:
      getObjects(obj, objs)
    except:
      path = directory.GetPath().split(':')[-1].strip('/')
      objs[path+'/'+kk.GetName()] = obj
  return objs


ff = ROOT.TFile(sys.argv[1])
c1 = ROOT.TCanvas("c1","c1",1100,800)
pdfname = sys.argv[1].split('/')[-1]+'.pdf'
c1.Print(pdfname+'[')
objs = getObjects(ff)
for kk in sorted(objs):
  
  #if 'pass_all_cuts_ftof' not in objs[kk].GetTitle(): continue
  opt = ''
  if 'TH2' in objs[kk].__class__.__name__:
    opt = 'colz'
  if 'TGraph' in objs[kk].__class__.__name__:
    opt = 'AP'
  objs[kk].Draw(opt)
  c1.Print(pdfname)
c1.Print(pdfname+']')
  
