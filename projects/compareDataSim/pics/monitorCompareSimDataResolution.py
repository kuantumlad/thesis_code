from ROOT import TCanvas, TPad, TFormula, TF1, TPaveLabel, TH1F, TFile, TLine
from ROOT import TGraphErrors, TBox
from ROOT import gROOT, gBenchmark, gStyle, gPad
from ROOT import kRed
from array import array
import math
import sys

def fit_slices(histo, x_range, x_bin_step):

    x_start = histo.GetXaxis().FindBin(x_range[0])
    x_stop =  histo.GetXaxis().FindBin(x_range[1])

    x_values = array('d')
    slices = []
    fits = []
    histo.RebinY(2)
    
    for i, x_bin in enumerate(range(x_start, x_stop + 1, x_bin_step)):
        projec = histo.ProjectionY(histo.GetTitle() + '_proj{}'.format(i) , x_bin, x_bin + x_bin_step)
        fit = TF1(histo.GetTitle()+'_fit{}'.format(i), 'gaus')

        fit_max = projec.GetMean() + 4.0*projec.GetRMS()
        fit_min = projec.GetMean() - 4.0*projec.GetRMS()

        
        projec.Fit(fit,'R','',fit_min,fit_max)

        slices.append(projec)
        fits.append(fit)

        x_low = histo.GetXaxis().GetBinCenter(x_bin)
        x_high = histo.GetXaxis().GetBinCenter(x_bin + x_bin_step)
        x_values.append(0.5 * (x_high + x_low))

    means = array('d')
    means_err = array('d')
    stds = array('d')
    stds_err = array('d')
    zeros = array('d')

    for f in fits:
        means.append(f.GetParameter(1))
        means_err.append(f.GetParError(1))
        stds.append(f.GetParameter(2))
        stds_err.append(f.GetParError(2))
        zeros.append(0.0)

    graph = TGraphErrors(len(x_values), x_values, means, zeros, stds)
    graph.SetName('g_' + histo.GetName())

    return graph, slices, fits

def rebinXY(hist,rebinfactorX, rebinfactorY):
    hist.RebinY(4)
    hist.RebinX(4)
    

def make_plots(can, fname, hists, x_ranges, rebinx, min_y, max_y):
    can.Clear()
    can.Divide(3,1)
    cc=1
    root_is_dumb = []
    for hh in hists:
        can.cd(cc)
        g_fit, sl_fit, f_fit  = fit_slices(hh,x_ranges[cc-1],rebinx)
        g_fit.SetTitle(hh.GetTitle()+'_slices')
        g_fit.SetMarkerStyle(21)
        g_fit.SetMarkerSize(1)
        g_fit.Draw('AP')
        g_fit.GetHistogram().SetMaximum(max_y)
        g_fit.GetHistogram().SetMinimum(min_y)
        g_fit.Draw('AP')
        root_is_dumb.append(g_fit)
        cc+=1
    can.Print(fname)

def make_slice_plots(incan, fname, hist, ranges, can_x, can_y, rebinx ):
    
    sl_container=[]
        
    grph, slices, fits = fit_slices(hist, ranges, rebinx)
    incan.Clear()
    incan.Divide(4,4)

    ss=1
    for sl in slices:
        incan.cd(ss)
        sl.SetTitle(sl.GetTitle()+'slice'+str(ss))
        sl.Draw()
        sl_container.append(sl)
        ss+=1
    incan.Print(fname)


def define2DHist(htemp, nameX, nameY):
    htemp.SetTitleX(nameX)
    htemp.SetTitleY(nameY)
    
fin = TFile(sys.argv[1])
fin_data = TFile(sys.argv[2])
tag = sys.argv[3]

my_pdf_name='mc_data_res_phi_'+tag+'.pdf'
my_pdf_fits='mc_data_res_fits_phi_'+tag+'.pdf'
my_pdf_slices='mc_data_res_phi_slices_'+tag+'.pdf'

hhs = {}
for kk in fin.GetListOfKeys():
    obj = kk.ReadObj()    
    hhs[obj.GetName()] = obj

hhs_data = {}
for kk in fin_data.GetListOfKeys():
    obj = kk.ReadObj()    
    hhs_data[obj.GetName()] = obj


can =TCanvas('can','can',1200,1200)

rebinHist=True
phi_mass = 1.019
pr_mass = 0.938
kaon_mass = 0.497


#open pdf file 
can.Print('{}['.format(my_pdf_name))
can.Divide(2,2)
can.cd(1)
hhs['epX_vs_theta_pr'].SetTitle('SIM. epX MM2 vs Proton #theta')
if rebinHist:
    hhs['epX_vs_theta_pr'].RebinY(4)
    hhs['epX_vs_theta_pr'].RebinX(4)
hhs['epX_vs_theta_pr'].Draw('colz')

phiLine1 = TLine(0.0, phi_mass, hhs['epX_vs_theta_pr'].GetXaxis().GetXmax(), phi_mass)
phiLine1.SetLineColor(kRed)
phiLine1.SetLineWidth(2)
phiLine1.Draw('same')

can.cd(2)
hhs['epX_vs_p_pr'].SetTitle('SIM. epX MM2 vs Proton Mntm')
if rebinHist:
    hhs['epX_vs_p_pr'].RebinY(4)
    hhs['epX_vs_p_pr'].RebinX(4)
hhs['epX_vs_p_pr'].Draw('colz')
phiLine2 = TLine(0.0, phi_mass, hhs['epX_vs_p_pr'].GetXaxis().GetXmax(), phi_mass)
phiLine2.SetLineColor(kRed)
phiLine2.SetLineWidth(2)
phiLine2.Draw('same')
can.cd(3)
hhs_data['epX_vs_theta_pr'].SetTitle('DATA epX MM2 vs Proton #theta')
if rebinHist:
    hhs_data['epX_vs_theta_pr'].RebinY(4)
    hhs_data['epX_vs_theta_pr'].RebinX(4)
hhs_data['epX_vs_theta_pr'].Draw('colz')
phiLine3 = TLine(0.0, phi_mass, hhs_data['epX_vs_theta_pr'].GetXaxis().GetXmax(), phi_mass)
phiLine3.SetLineColor(kRed)
phiLine3.SetLineWidth(2)
phiLine3.Draw('same')
can.cd(4)
hhs_data['epX_vs_p_pr'].SetTitle('DATA epX MM2 vs Proton Mntm')
if rebinHist:
    hhs_data['epX_vs_p_pr'].RebinY(4)
    hhs_data['epX_vs_p_pr'].RebinX(4)
hhs_data['epX_vs_p_pr'].Draw('colz')
phiLine4 = TLine(0.0, phi_mass, hhs_data['epX_vs_theta_pr'].GetXaxis().GetXmax(), phi_mass)
phiLine4.SetLineColor(kRed)
phiLine4.SetLineWidth(2)
phiLine4.Draw('same')

can.Print(my_pdf_name)
can.Clear()

can.Divide(2,2)
can.cd(1)
hhs['epkpX_vs_theta_km'].SetTitle('SIM. epkpX MM2 vs KM #theta')
if rebinHist:
    hhs['epkpX_vs_theta_km'].RebinY(4)
    hhs['epkpX_vs_theta_km'].RebinX(4)
hhs['epkpX_vs_theta_km'].Draw('colz')
kaonLine = TLine(0.0, (kaon_mass**2),  hhs['epkpX_vs_theta_km'].GetXaxis().GetXmax(), kaon_mass**2)
kaonLine.SetLineColor(kRed)
kaonLine.SetLineWidth(2)
kaonLine.Draw('same')
can.cd(2)
hhs['epkpX_vs_p_km'].SetTitle('SIM. epkpX MM2 vs KM Mntm')
if rebinHist:
    hhs['epkpX_vs_p_km'].RebinY(4)
    hhs['epkpX_vs_p_km'].RebinX(4)
hhs['epkpX_vs_p_km'].Draw('colz')
kaonLine2 = TLine(0.0, (kaon_mass**2),  hhs['epkpX_vs_p_km'].GetXaxis().GetXmax(), kaon_mass**2)
kaonLine2.SetLineColor(kRed)
kaonLine2.SetLineWidth(2)
kaonLine2.Draw('same')
can.cd(3)
hhs_data['epkpX_vs_theta_km'].SetTitle('DATA epkpX MM2 vs KM #theta')
if rebinHist:
    hhs_data['epkpX_vs_theta_km'].RebinY(4)
    hhs_data['epkpX_vs_theta_km'].RebinX(4)
hhs_data['epkpX_vs_theta_km'].Draw('colz')
kaonLine3 = TLine(0.0, (kaon_mass**2),  hhs_data['epkpX_vs_theta_km'].GetXaxis().GetXmax(), kaon_mass**2)
kaonLine3.SetLineColor(kRed)
kaonLine3.SetLineWidth(2)
kaonLine3.Draw('same')
can.cd(4)
hhs_data['epkpX_vs_p_km'].SetTitle('DATA epkpX MM2 vs KM Mntm')
if rebinHist:
    hhs_data['epkpX_vs_p_km'].RebinY(4)
    hhs_data['epkpX_vs_p_km'].RebinX(4)
hhs_data['epkpX_vs_p_km'].Draw('colz')
kaonLine4 = TLine(0.0, (kaon_mass**2),  hhs_data['epkpX_vs_p_km'].GetXaxis().GetXmax(), kaon_mass**2)
kaonLine4.SetLineColor(kRed)
kaonLine4.SetLineWidth(2)
kaonLine4.Draw('same')
can.Print(my_pdf_name)
can.Clear()

can.Divide(2,2)
can.cd(1)
hhs['epkmX_vs_theta_kp'].SetTitle('SIM. epkmX MM2 vs KP #theta')
if rebinHist:
    hhs['epkmX_vs_theta_kp'].RebinY(4)
    hhs['epkmX_vs_theta_kp'].RebinX(4)
hhs['epkmX_vs_theta_kp'].Draw('colz')
kaonPLine1 = TLine(0.0, (kaon_mass**2),  hhs['epkmX_vs_theta_kp'].GetXaxis().GetXmax(), kaon_mass**2)
kaonPLine1.SetLineColor(kRed)
kaonPLine1.SetLineWidth(2)
kaonPLine1.Draw('same')
can.cd(2)
hhs['epkmX_vs_p_kp'].SetTitle('SIM. epkmX MM2 vs KP Mntm')
if rebinHist:
    hhs['epkmX_vs_p_kp'].RebinY(4)
    hhs['epkmX_vs_p_kp'].RebinX(4)
hhs['epkmX_vs_p_kp'].Draw('colz')
kaonPLine2 = TLine(0.0, (kaon_mass**2),  hhs['epkmX_vs_p_kp'].GetXaxis().GetXmax(), kaon_mass**2)
kaonPLine2.SetLineColor(kRed)
kaonPLine2.SetLineWidth(2)
kaonPLine2.Draw('same')
can.cd(3)
hhs_data['epkmX_vs_theta_kp'].SetTitle('DATA epkmX MM2 vs KP #theta')
if rebinHist:
    hhs_data['epkmX_vs_theta_kp'].RebinY(4)
    hhs_data['epkmX_vs_theta_kp'].RebinX(4)
hhs_data['epkmX_vs_theta_kp'].Draw('colz')
kaonPLine3 = TLine(0.0, (kaon_mass**2),  hhs_data['epkmX_vs_theta_kp'].GetXaxis().GetXmax(), kaon_mass**2)
kaonPLine3.SetLineColor(kRed)
kaonPLine3.SetLineWidth(2)
kaonPLine3.Draw('same')
can.cd(4)
hhs_data['epkmX_vs_p_kp'].SetTitle('DATA epkmX MM2 vs KP Mntm')
if rebinHist:
    hhs_data['epkmX_vs_p_kp'].RebinY(4)
    hhs_data['epkmX_vs_p_kp'].RebinX(4)
hhs_data['epkmX_vs_p_kp'].Draw('colz')
kaonPLine4 = TLine(0.0, (kaon_mass**2),  hhs_data['epkmX_vs_p_kp'].GetXaxis().GetXmax(), kaon_mass**2)
kaonPLine4.SetLineColor(kRed)
kaonPLine4.SetLineWidth(2)
kaonPLine4.Draw('same')
can.Print(my_pdf_name)
can.Clear()

can.Divide(2,2)
can.cd(1)
hhs['ekpkmX_vs_theta_pr'].SetTitle('SIM. ekpkmX MM2 vs Pr. #theta')
if rebinHist:
    hhs['ekpkmX_vs_theta_pr'].RebinY(4)
    hhs['ekpkmX_vs_theta_pr'].RebinX(4)
hhs['ekpkmX_vs_theta_pr'].Draw('colz')
prLine1 = TLine(0.0, (pr_mass**2),  hhs_data['ekpkmX_vs_theta_pr'].GetXaxis().GetXmax(), pr_mass**2)
prLine1.SetLineColor(kRed)
prLine1.SetLineWidth(2)
prLine1.Draw('same')
can.cd(2)
hhs['ekpkmX_vs_p_pr'].SetTitle('SIM. ekpkmX MM2 vs Pr. Mntm')
if rebinHist:
    hhs['ekpkmX_vs_p_pr'].RebinY(4)
    hhs['ekpkmX_vs_p_pr'].RebinX(4)
hhs['ekpkmX_vs_p_pr'].Draw('colz')
prLine2 = TLine(0.0, (pr_mass**2),  hhs_data['ekpkmX_vs_p_pr'].GetXaxis().GetXmax(), pr_mass**2)
prLine2.SetLineColor(kRed)
prLine2.SetLineWidth(2)
prLine2.Draw('same')

can.cd(3)
hhs_data['ekpkmX_vs_theta_pr'].SetTitle('DATA ekpkmX MM2 vs Pr. #theta')
if rebinHist:
    hhs_data['ekpkmX_vs_theta_pr'].RebinY(4)
    hhs_data['ekpkmX_vs_theta_pr'].RebinX(4)
hhs_data['ekpkmX_vs_theta_pr'].Draw('colz')
prLine1.Draw('same')
can.cd(4)
hhs_data['ekpkmX_vs_p_pr'].SetTitle('DATA ekpkmX MM2 vs Pr. Mntm')
if rebinHist:
    hhs_data['ekpkmX_vs_p_pr'].RebinY(4)
    hhs_data['ekpkmX_vs_p_pr'].RebinX(4)
hhs_data['ekpkmX_vs_p_pr'].Draw('colz')
prLine2.Draw('same')
can.Print(my_pdf_name)
can.Clear()

#mntm lines
pLine = TLine(0.0, 0.0, hhs['delta_theta_vs_p_pr'].GetXaxis().GetXmax(), 0.0)
pLine.SetLineColor(kRed)
pLine.SetLineWidth(2)

#theta lines
tLine = TLine(0.0, 0.0, hhs['delta_theta_vs_theta_pr'].GetXaxis().GetXmax(), 0.0)
tLine.SetLineColor(kRed)
tLine.SetLineWidth(2)

#deltas
can.SetCanvasSize(1600,800)
can.Divide(4,2)
can.cd(1)
hhs['delta_theta_vs_theta_pr'].SetTitle('Sim. #Delta #theta vs #theta_{Pr}; #theta_{Pr} (deg); #Delta #theta (deg)')
if rebinHist:
    rebinXY(hhs['delta_theta_vs_theta_pr'],4,4)
hhs['delta_theta_vs_theta_pr'].Draw('colz')
tLine.Draw('same')
can.cd(2)
hhs['delta_theta_vs_p_pr'].SetTitle('Sim. #Delta #theta vs Pr. Mntm; Mntm (GeV); #Delta #theta (deg)')
if rebinHist:
    rebinXY(hhs['delta_theta_vs_p_pr'],4,4)
hhs['delta_theta_vs_p_pr'].Draw('colz')
pLine.Draw('same')
can.cd(3)
hhs['delta_p_vs_theta_pr'].SetTitle('Sim. #Delta P vs #theta_{Pr}; #theta (deg) ; #Delta P (GeV)')
if rebinHist:
    rebinXY(hhs['delta_p_vs_theta_pr'],4,4)
hhs['delta_p_vs_theta_pr'].Draw('colz')
tLine.Draw('same')
can.cd(4)
hhs['delta_p_vs_p_pr'].SetTitle('Sim. #Delta P vs Pr. Mntm; Mntm (GeV); #Delta P (GeV)')
if rebinHist:
    rebinXY(hhs['delta_p_vs_p_pr'],4,4)
hhs['delta_p_vs_p_pr'].Draw('colz')
pLine.Draw('same')
can.cd(5)
hhs_data['delta_theta_vs_theta_pr'].SetTitle('DATA #Delta #theta vs #theta_{Pr}; #theta_{Pr} (deg); #Delta #theta (deg)')
if rebinHist:
    rebinXY(hhs_data['delta_theta_vs_theta_pr'],4,4)
hhs_data['delta_theta_vs_theta_pr'].Draw('colz')
tLine.Draw('same')
can.cd(6)
hhs_data['delta_theta_vs_p_pr'].SetTitle('DATA #Delta #theta vs Pr. Mntm; Mntm (GeV); #Delta #theta (deg)')
if rebinHist:
    rebinXY(hhs_data['delta_theta_vs_p_pr'],4,4)
hhs_data['delta_theta_vs_p_pr'].Draw('colz')
pLine.Draw('same')
can.cd(7)
hhs_data['delta_p_vs_theta_pr'].SetTitle('DATA #Delta P vs #theta_{Pr}; #theta (deg) ; #Delta P (GeV)')
if rebinHist:
    rebinXY(hhs_data['delta_p_vs_theta_pr'],4,4)
hhs_data['delta_p_vs_theta_pr'].Draw('colz')
tLine.Draw('same')
can.cd(8)
hhs_data['delta_p_vs_p_pr'].SetTitle('DATA #Delta P vs Pr. Mntm; Mntm (GeV); #Delta P (GeV)')
if rebinHist:
    rebinXY(hhs_data['delta_p_vs_p_pr'],4,4)
hhs_data['delta_p_vs_p_pr'].Draw('colz')
pLine.Draw('same')
can.Print(my_pdf_name)
can.Clear()

can.Divide(4,2)
can.cd(1)
hhs['delta_theta_vs_theta_kp'].SetTitle('SIM #Delta #theta vs #theta_{KP}; #theta_{Kp} (deg); #Delta #theta (deg)')
if rebinHist:
    rebinXY(hhs['delta_theta_vs_theta_kp'],4,4)
hhs['delta_theta_vs_theta_kp'].Draw('colz')
tLine.Draw('same')
can.cd(2)
hhs['delta_theta_vs_p_kp'].SetTitle('SIM. #Delta #theta vs Kp Mntm; Mntm (GeV); #Delta #theta (deg)')
if rebinHist:
    rebinXY(hhs['delta_theta_vs_p_kp'],4,4)
hhs['delta_theta_vs_p_kp'].Draw('colz')
pLine.Draw('same')
can.cd(3)
hhs['delta_p_vs_theta_kp'].SetTitle('SIM. #Delta P vs #theta_{Kp}; #theta (deg) ; #Delta P (GeV)')
if rebinHist:
    rebinXY(hhs['delta_p_vs_theta_kp'],4,4)
hhs['delta_p_vs_theta_kp'].Draw('colz')
tLine.Draw('same')
can.cd(4)
hhs['delta_p_vs_p_kp'].SetTitle('SIM. #Delta P vs Kp Mntm; Mntm (GeV); #Delta P (GeV)')
if rebinHist:
    rebinXY(hhs['delta_p_vs_p_kp'],4,4)
hhs['delta_p_vs_p_kp'].Draw('colz')
pLine.Draw('same')
can.cd(5)
hhs_data['delta_theta_vs_theta_kp'].SetTitle('DATA #Delta #theta vs #theta_{KP}; #theta_{Kp} (deg); #Delta #theta (deg)')
if rebinHist:
    rebinXY(hhs_data['delta_theta_vs_theta_kp'],4,4)
hhs_data['delta_theta_vs_theta_kp'].Draw('colz')
tLine.Draw('same')
can.cd(6)
hhs_data['delta_theta_vs_p_kp'].SetTitle('DATA #Delta #theta vs Kp Mntm; Mntm (GeV); #Delta #theta (deg)')
if rebinHist:
    rebinXY(hhs_data['delta_theta_vs_p_kp'],4,4)
hhs_data['delta_theta_vs_p_kp'].Draw('colz')
pLine.Draw('same')
can.cd(7)
hhs_data['delta_p_vs_theta_kp'].SetTitle('DATA #Delta P vs #theta_{Kp}; #theta (deg) ; #Delta P (GeV)')
if rebinHist:
    rebinXY(hhs_data['delta_p_vs_theta_kp'],4,4)
hhs_data['delta_p_vs_theta_kp'].Draw('colz')
tLine.Draw('same')
can.cd(8)
hhs_data['delta_p_vs_p_kp'].SetTitle('DATA #Delta P vs Kp Mntm; Mntm (GeV); #Delta P (GeV)')
if rebinHist:
    rebinXY(hhs_data['delta_p_vs_p_kp'],4,4)
hhs_data['delta_p_vs_p_kp'].Draw('colz')
pLine.Draw('same')
can.Print(my_pdf_name)
can.Clear()

can.Divide(4,2)
can.cd(1)
hhs['delta_theta_vs_theta_km'].SetTitle('SIM. #Delta #theta vs #theta_{Km}; #theta_{Km} (deg); #Delta #theta (deg)')
if rebinHist:
    rebinXY(hhs['delta_theta_vs_theta_km'],4,4)
hhs['delta_theta_vs_theta_km'].Draw('colz')
tLine.Draw('same')
can.cd(2)
hhs['delta_theta_vs_p_km'].SetTitle('SIM. #Delta #theta vs Km Mntm; Mntm (GeV); #Delta #theta (deg)')
if rebinHist:
    rebinXY(hhs['delta_theta_vs_p_km'],4,4)
hhs['delta_theta_vs_p_km'].Draw('colz')
pLine.Draw('same')
can.cd(3)
hhs['delta_p_vs_theta_km'].SetTitle('SIM. #Delta P vs #theta_{Km}; #theta (deg) ; #Delta P (GeV)')
if rebinHist:
    rebinXY(hhs['delta_p_vs_theta_km'],4,4)
hhs['delta_p_vs_theta_km'].Draw('colz')
tLine.Draw('same')
can.cd(4)
hhs['delta_p_vs_p_km'].SetTitle('SIM. #Delta P vs Km Mntm; Mntm (GeV); #Delta P (GeV)')
if rebinHist:
    rebinXY(hhs['delta_p_vs_p_km'],4,4)
hhs['delta_p_vs_p_km'].Draw('colz')
pLine.Draw('same')
can.cd(5)
hhs_data['delta_theta_vs_theta_km'].SetTitle('DATA #Delta #theta vs #theta_{Km}; #theta_{Km} (deg); #Delta #theta (deg)')
if rebinHist:
    rebinXY(hhs_data['delta_theta_vs_theta_km'],4,4)
hhs_data['delta_theta_vs_theta_km'].Draw('colz')
tLine.Draw('same')
can.cd(6)
hhs_data['delta_theta_vs_p_km'].SetTitle('DATA #Delta #theta vs Km Mntm; Mntm (GeV); #Delta #theta (deg)')
if rebinHist:
    rebinXY(hhs_data['delta_theta_vs_p_km'],4,4)
hhs_data['delta_theta_vs_p_km'].Draw('colz')
pLine.Draw('same')
can.cd(7)
hhs_data['delta_p_vs_theta_km'].SetTitle('DATA #Delta P vs #theta_{Km}; #theta (deg) ; #Delta P (GeV)')
if rebinHist:
    rebinXY(hhs_data['delta_p_vs_theta_km'],4,4)
hhs_data['delta_p_vs_theta_km'].Draw('colz')
tLine.Draw('same')
can.cd(8)
hhs_data['delta_p_vs_p_km'].SetTitle('DATA  #Delta P vs Km Mntm; Mntm (GeV); #Delta P (GeV)')
if rebinHist:
    rebinXY(hhs_data['delta_p_vs_p_km'],4,4)
pLine.Draw('same')
hhs_data['delta_p_vs_p_km'].Draw('colz')
pLine.Draw('same')
can.Print(my_pdf_name)
can.Clear()


#close the pdf file
can.Print('{}]'.format(my_pdf_name))


#######################
## plot the fit means
rebinx=2
canfits = TCanvas('canfits','canfits',1000,1200)
canfits.Print('{}['.format(my_pdf_fits))
canfits.Divide(2,1)
canfits.cd(1)
g_epXthetapr, sl_epXthetapr, f_epXthetapr = fit_slices(hhs['epX_vs_theta_pr'], [22,38], rebinx)
g_epXthetapr.SetMarkerStyle(21)
g_epXthetapr.SetMarkerSize(1)
g_epXthetapr.Draw('AP')
g_epXthetapr.GetHistogram().SetMaximum(3.00)
g_epXthetapr.GetHistogram().SetMinimum(0.00)
g_epXthetapr.Draw('AP')
canfits.cd(2)
g_epXmntmpr, sl_epXmntmpr, f_epXmntmpr = fit_slices(hhs['epX_vs_p_pr'], [0.5,1.5], rebinx)
g_epXmntmpr.SetMarkerStyle(21)
g_epXmntmpr.SetMarkerSize(1)
g_epXmntmpr.Draw('AP')
g_epXmntmpr.GetHistogram().SetMaximum(3.00)
g_epXmntmpr.GetHistogram().SetMinimum(0.00)
g_epXmntmpr.Draw('AP')
canfits.Print(my_pdf_fits)
canfits.Clear()

canfits.Divide(2,1)
canfits.cd(1)
g_epkpXthetakm, sl_epkpXthetakm, f_epkpXthetakm = fit_slices(hhs['epkpX_vs_theta_km'], [12,20], rebinx)
g_epkpXthetakm.SetMarkerStyle(21)
g_epkpXthetakm.SetMarkerSize(1)
g_epkpXthetakm.Draw('AP')
g_epkpXthetakm.GetHistogram().SetMaximum(0.40)
g_epkpXthetakm.GetHistogram().SetMinimum(0.00)
g_epkpXthetakm.Draw('AP')
canfits.cd(2)
g_epkpXmntmkm, sl_epkpXmntmkm, f_epkpXmntmkm = fit_slices(hhs['epkpX_vs_p_km'], [0.85,3.0], rebinx)
g_epkpXmntmkm.SetMarkerStyle(21)
g_epkpXmntmkm.SetMarkerSize(1)
g_epkpXmntmkm.Draw('AP')
g_epkpXmntmkm.GetHistogram().SetMaximum(0.40)
g_epkpXmntmkm.GetHistogram().SetMinimum(0.00)
g_epkpXmntmkm.Draw('AP')
canfits.Print(my_pdf_fits)
canfits.Clear()


canfits.Divide(2,1)
canfits.cd(1)
g_epkmXthetakp, sl_epkmXthetakp, f_epkmXthetakp = fit_slices(hhs['epkmX_vs_theta_kp'], [9,20], rebinx)
g_epkmXthetakp.SetMarkerStyle(21)
g_epkmXthetakp.SetMarkerSize(1)
g_epkmXthetakp.Draw('AP')
g_epkmXthetakp.GetHistogram().SetMaximum(0.40)
g_epkmXthetakp.GetHistogram().SetMinimum(0.00)
g_epkmXthetakp.Draw('AP')
canfits.cd(2)
g_epkmXmntmkp, sl_epkmXmntmkp, f_epkmXmntmkp = fit_slices(hhs['epkmX_vs_p_kp'], [0.85,3.0], rebinx)
g_epkmXmntmkp.SetMarkerStyle(21)
g_epkmXmntmkp.SetMarkerSize(1)
g_epkmXmntmkp.Draw('AP')
g_epkmXmntmkp.GetHistogram().SetMaximum(0.40)
g_epkmXmntmkp.GetHistogram().SetMinimum(0.00)
g_epkmXmntmkp.Draw('AP')
canfits.Print(my_pdf_fits)
canfits.Clear()

canfits.Divide(2,1)
canfits.cd(1)
g_ekpkmXthetapr, sl_epkmXthetakp, f_epkmXthetakp = fit_slices(hhs['ekpkmX_vs_theta_pr'], [21,38], rebinx)
g_ekpkmXthetapr.SetMarkerStyle(21)
g_ekpkmXthetapr.SetMarkerSize(1)
g_ekpkmXthetapr.Draw('AP')
g_ekpkmXthetapr.GetHistogram().SetMaximum(1.10)
g_ekpkmXthetapr.GetHistogram().SetMinimum(0.70)
g_ekpkmXthetapr.Draw('AP')
canfits.cd(2)
g_ekpkmXmntmpr, sl_ekpkmXmntmpr, f_ekpkmXmntmpt = fit_slices(hhs['ekpkmX_vs_p_pr'], [0.44,1.3], rebinx)
g_ekpkmXmntmpr.SetMarkerStyle(21)
g_ekpkmXmntmpr.SetMarkerSize(1)
g_ekpkmXmntmpr.Draw('AP')
g_ekpkmXmntmpr.GetHistogram().SetMaximum(1.10)
g_ekpkmXmntmpr.GetHistogram().SetMinimum(0.70)
g_ekpkmXmntmpr.Draw('AP')
canfits.Print(my_pdf_fits)
canfits.Clear()

delta_theta_vs_theta_plots = [hhs['delta_theta_vs_theta_pr'], 
                              hhs['delta_theta_vs_theta_kp'],
                              hhs['delta_theta_vs_theta_km']]

delta_theta_vs_p_plots = [hhs['delta_theta_vs_p_pr'], 
                          hhs['delta_theta_vs_p_kp'],
                          hhs['delta_theta_vs_p_km']]

delta_p_vs_theta_plots = [hhs['delta_p_vs_theta_pr'], 
                          hhs['delta_p_vs_theta_kp'],
                          hhs['delta_p_vs_theta_km']]

delta_p_vs_p_plots = [hhs['delta_p_vs_p_pr'], 
                      hhs['delta_p_vs_p_kp'],
                      hhs['delta_p_vs_p_km']]

delta_theta_vs_theta_ranges = [ [20,38], [9,22], [9,22]]
delta_theta_vs_p_ranges = [ [0.5,1.75],[1.02,2.75], [1.02,2.75]]
delta_p_vs_theta_ranges = [ [20,38], [9,22],[9,22] ]
delta_p_vs_p_ranges = [ [0.5,1.75], [0.8, 2.75], [0.8, 2.75]]


rebinx=2
canfits.SetCanvasSize(900,300);
make_plots(canfits, my_pdf_fits, delta_theta_vs_theta_plots, delta_theta_vs_theta_ranges ,rebinx,-3,3)

make_plots(canfits, my_pdf_fits, delta_theta_vs_p_plots, delta_theta_vs_p_ranges ,rebinx,-3.0, 3.0)

make_plots(canfits, my_pdf_fits, delta_p_vs_theta_plots, delta_p_vs_theta_ranges ,rebinx,-1.3, 1.3)

make_plots(canfits, my_pdf_fits, delta_p_vs_p_plots, delta_p_vs_p_ranges ,rebinx, -1.3, 1.3)

can.Print('{}]'.format(my_pdf_fits))

    
canslices = TCanvas('canslices','canslices',900,900)
canslices.Print('{}['.format(my_pdf_slices))

hh_counter=0
for hh in delta_theta_vs_theta_plots:
    make_slice_plots(canslices, my_pdf_slices, hh, delta_theta_vs_theta_ranges[hh_counter], 3, 3, rebinx) 
    hh_counter+=1

hh_counter=0
for hh in delta_theta_vs_p_plots:
    make_slice_plots(canslices, my_pdf_slices, hh, delta_theta_vs_p_ranges[hh_counter], 3, 3, rebinx) 
    hh_counter+=1

hh_counter=0
for hh in delta_p_vs_theta_plots:
    make_slice_plots(canslices, my_pdf_slices, hh, delta_p_vs_theta_ranges[hh_counter], 3, 3, rebinx) 
    hh_counter+=1

hh_counter=0
for hh in delta_p_vs_p_plots:
    make_slice_plots(canslices, my_pdf_slices, hh, delta_p_vs_p_ranges[hh_counter], 3, 3, rebinx) 
    hh_counter+=1


canslices.Print('{}]'.format(my_pdf_slices))

    
