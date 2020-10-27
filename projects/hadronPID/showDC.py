#!/usr/bin/env python 
import argparse 
import numpy as np
import math
# Trick for docker install to run headless
# and never use plt.show() 
# dont use matplotlib while running this code on the batch farm
#import matplotlib
#matplotlib.use('agg')
#import matplotlib.pyplot as plt 

################################################################
## note - this is used for analyzing the RAD elastic events
## that includes both ISR and FSR. First half is ISR CTOF

from array import array 
from collections import OrderedDict 
from ROOT import (TH1F, TH2F, TF1, TFile, TCanvas, TLegend,
                  gPad, gStyle, TLatex, TGraphErrors,
                  TLine, kRed, kBlack, kBlue, kWhite, kGreen,  kTRUE, gROOT)

from ROOT import( RooRealVar, RooArgSet, RooArgList, RooDataHist,
                  RooGaussian, RooFit, RooAddPdf, RooPolynomial, RooFormulaVar, RooLinkedList)

gROOT.SetBatch(kTRUE)

default_histo = TH1F('default', '', 100, 0, 1)
default_histo2d = TH2F('default', '', 100, 0, 1, 100, 0, 1)
global_dump = []

def load_histos(file):
    ''' Use the ROOT file structure to load a dictionary of histograms. '''
    h = {}
    for k in file.GetListOfKeys():
        h[k.GetName()] = file.Get(k.GetName())
    return h

def setup_global_options():
    gStyle.SetOptTitle(0)
    gStyle.SetOptStat(0)
    gStyle.SetPalette(57)


maxparams = [
    [[[-35.1716, 25.102, -0.750281, 5.34679e-05],
      [-39.1633, 28.5551, -1.13429, 0.00419047],
      [-33.7705, 24.8068, -0.811239, 0.00138345]],
     [[-36.2389, 26.7979, -1.08147, 0.0050898],
      [-43.643, 31.6783, -1.49203, 0.00872922],
      [-54.4042, 40.6516, -2.52393, 0.0205649]],
     [[-38.3238, 26.1667, -0.777077, 0.000264835],
      [-34.2011, 24.2843, -0.696392, 3.75866e-12],
      [-36.4636, 25.8712, -0.786592, 2.24421e-10]],
     [[-31.8019, 23.154, -0.653992, 2.69968e-05],
      [-34.6637, 24.6043, -0.714901, 2.02675e-10],
      [-36.7209, 26.2469, -0.828638, 0.000340435]],
     [[-33.4016, 24.6901, -0.779889, 0.000430557],
      [-35.4583, 24.7491, -0.707953, 2.18559e-10],
      [-37.7335, 28.1547, -1.1986, 0.00582395]],
     [[-34.7808, 24.6988, -0.719936, 5.73299e-10],
      [-54.5797, 40.9138, -2.57493, 0.0213354],
      [-38.4972, 28.3142, -1.21741, 0.00640373]]],
    [[[-2.25358e-08, 12.631, -0.767619, 0.00739811],
      [-8.09501, 15.9098, -0.844083, 0.00667995],
      [-1.48113e-06, 12.2061, -0.73167, 0.0074309]],
     [[-2.10872e-07, 12.6689, -0.765156, 0.00720044],
      [-4.88862, 14.0376, -0.687202, 0.00506307],
      [-4.59793e-06, 11.5553, -0.591469, 0.00536957]],
     [[-1.13504e-08, 12.6011, -0.746025, 0.00687498],
      [-6.97884, 15.1788, -0.765889, 0.00570532],
      [-1.29468, 12.3844, -0.667561, 0.00619226]],
     [[-2.91953e-09, 13.883, -0.999624, 0.0104257],
      [-4.9855, 13.8864, -0.661348, 0.0048371],
      [-2.29438e-08, 11.8341, -0.668486, 0.00669247]],
     [[-2.02824e-08, 13.3855, -0.91158, 0.00926769],
      [-3.29092e-08, 10.8294, -0.382323, 0.00178367],
      [-4.59027e-06, 11.9414, -0.663872, 0.00625769]],
     [[-3.73322e-09, 12.6126, -0.723548, 0.0062217],
      [-4.56248, 14.1574, -0.727805, 0.00560108],
      [-2.39381e-08, 12.0663, -0.6651, 0.00602544]]],
    [[[-1.45923e-08, 13.0297, -0.828302, 0.00795271],
      [-5.41905, 13.2753, -0.503236, 0.00255607],
      [-3.67719, 12.1358, -0.462905, 0.00308219]],
     [[-9.953e-10, 11.549, -0.52816, 0.00378771],
      [-8.47154, 15.9863, -0.826166, 0.0062936],
      [-6.43715, 13.9081, -0.618535, 0.0046102]],
     [[-4.68458e-08, 12.9481, -0.781613, 0.00689754],
      [-3.46617, 12.2786, -0.440121, 0.00205448],
      [-4.43519, 10.9372, -0.210059, 3.69283e-10]],
     [[-4.18414e-07, 13.1542, -0.811251, 0.00714402],
      [-4.63166, 13.7769, -0.657207, 0.0047586],
      [-1.99278e-05, 11.3993, -0.575232, 0.00532141]],
     [[-7.07189e-10, 13.2814, -0.88476, 0.00874389],
      [-5.08373, 14.4384, -0.750795, 0.00586116],
      [-6.9642e-05, 9.50651, -0.189316, 3.07274e-06]],
     [[-5.85515e-08, 12.5116, -0.688741, 0.00557297],
      [-1.86306, 11.985, -0.482567, 0.00279836],
      [-4.94295e-07, 10.1342, -0.316715, 0.00176254]]],
    [[[-0.0157256, 11.1508, -0.415185, 0.00186904],
      [-13.6561, 19.4418, -1.15773, 0.00989432],
      [-6.24969e-07, 10.5776, -0.329325, 0.00103488]],
     [[-2.5686e-08, 11.4797, -0.476772, 0.00264288],
      [-0.0475099, 10.1207, -0.244786, 3.13032e-06],
      [-4.6875e-07, 12.019, -0.63598, 0.00543214]],
     [[-0.00702545, 11.1294, -0.407207, 0.00171263],
      [-7.27687, 15.5, -0.807858, 0.0062086],
      [-5.15078, 12.6368, -0.348584, 9.2687e-12]],
     [[-8.14106e-08, 13.28, -0.818164, 0.00703758],
      [-7.60722, 14.4871, -0.588662, 0.00326244],
      [-1.70764e-06, 12.0413, -0.63961, 0.00541784]],
     [[-1.09281, 11.5573, -0.41311, 0.00155228],
      [-3.71599, 12.8335, -0.521472, 0.00296792],
      [-0.000410815, 12.4833, -0.72999, 0.0066601]],
     [[-0.652641, 12.2766, -0.554202, 0.00314615],
      [-8.42824, 15.5087, -0.710609, 0.00447051],
      [-14.9692, 21.5885, -1.47528, 0.0136615]]],
    [[[-5.58945, 17.4004, -1.34516, 0.0142099],
      [-14.9585, 20.4538, -1.25118, 0.0106617],
      [-12.0069, 16.4545, -0.727162, 0.00495418]],
     [[-7.03048, 17.3519, -1.1831, 0.0111308],
      [-7.30641, 15.8503, -0.850952, 0.00648446],
      [-10.2549, 15.6139, -0.648352, 0.00380506]],
     [[-9.73111e-09, 13.498, -0.932479, 0.00939708],
      [-8.38053, 15.5588, -0.711323, 0.00433827],
      [-12.3097, 16.6403, -0.741362, 0.0050708]],
     [[-7.38905, 17.2652, -1.15517, 0.0109165],
      [-1.11835e-07, 10.4637, -0.301972, 0.000612754],
      [-12.2182, 17.4958, -0.919555, 0.00747512]],
     [[-0.492676, 14.4148, -1.0959, 0.0116708],
      [-5.34309, 14.3258, -0.691954, 0.00480109],
      [-12.5443, 16.1047, -0.59594, 0.00280171]],
     [[-4.08375e-07, 12.2846, -0.655278, 0.00525956],
      [-8.93101, 16.4266, -0.861853, 0.00644623],
      [-11.8406, 17.0417, -0.826301, 0.00596028]]],
    [[[-9.29415, 16.5566, -0.831923, 0.00562504],
      [-0.954483, 10.5813, -0.265766, 3.24615e-05],
      [-6.87423, 14.892, -0.76495, 0.00639603]],
     [[-18.8913, 19.3123, -0.711917, 0.00227889],
      [-13.9788, 18.5678, -0.940183, 0.00664397],
      [-11.7696, 18.3415, -1.04368, 0.0083506]],
     [[-3.82873, 12.7727, -0.425968, 0.000789835],
      [-9.81221, 14.6531, -0.471092, 0.00131406],
      [-14.2392, 15.9895, -0.430525, 2.20712e-12]],
     [[-1.76975e-07, 11.4006, -0.420134, 0.00141302],
      [-3.11764, 10.9707, -0.245823, 2.23044e-12],
      [-17.6005, 22.2881, -1.39992, 0.0117791]],
     [[-0.767518, 11.6824, -0.456275, 0.00214005],
      [-5.28047, 12.65, -0.350658, 9.80081e-05],
      [-0.0888832, 11.508, -0.49197, 0.00301269]],
     [[-4.72388, 15.8507, -1.00574, 0.00876768],
      [-2.80649, 11.4056, -0.301812, 0.000190262],
      [-13.0484, 18.665, -1.08614, 0.00960977]]]]



minparams = [
    [[[37.289, -27.5201, 1.12866, -0.00526111],
      [45.3103, -33.5226, 1.72923, -0.0114495],
      [61.5709, -47.6158, 3.4295, -0.0316429]],
     [[36.6259, -27.4064, 1.16617, -0.00604629],
      [50.3751, -37.5848, 2.19621, -0.0169241],
      [35.1563, -26.514, 1.09795, -0.00545864]],
     [[27.2367, -20.3068, 0.517752, -0.000335432],
      [39.0489, -28.6903, 1.24306, -0.0065226],
      [41.0208, -30.0339, 1.30776, -0.00626721]],
     [[29.261, -21.7041, 0.613556, -0.000774652],
      [39.5304, -29.1388, 1.34116, -0.00823818],
      [44.5313, -33.4056, 1.77581, -0.0123965]],
     [[36.5659, -25.119, 0.714074, -2.65397e-11],
      [31.6524, -22.6934, 0.613977, -5.46634e-10],
      [34.7312, -24.9901, 0.749061, -1.22922e-09]],
     [[33.154, -23.8803, 0.685794, -1.13236e-10],
      [42.6731, -31.0799, 1.40425, -0.00730816],
      [46.4732, -35.6988, 2.10144, -0.0164771]]],
    [[[2.40451, -15.0848, 1.05504, -0.0103356],
      [8.93825, -16.5995, 0.925874, -0.00767902],
      [7.23439e-08, -12.5963, 0.814574, -0.00864749]],
     [[6.2953e-07, -12.6365, 0.732206, -0.00639165],
      [12.6866, -18.7831, 1.0952, -0.00923029],
      [3.12805e-07, -12.5395, 0.795535, -0.00828991]],
     [[2.69495, -14.8778, 1.00751, -0.00975373],
      [6.05446, -14.6778, 0.767457, -0.00636729],
      [3.94741e-07, -11.1038, 0.524109, -0.00471514]],
     [[2.31558e-07, -11.5073, 0.494316, -0.00303611],
      [5.66995, -14.5948, 0.740956, -0.00561851],
      [4.40475e-06, -9.57062, 0.20354, -0.000213213]],
     [[2.74277e-08, -13.3573, 0.886651, -0.00857992],
      [9.98849e-05, -11.524, 0.531486, -0.00391441],
      [8.50811e-07, -9.72224, 0.240264, -0.000781498]],
     [[6.9021e-08, -11.8859, 0.53864, -0.00325092],
      [10.0169, -16.9153, 0.921593, -0.00752414],
      [9.90518e-07, -11.9578, 0.697029, -0.00717645]]],
    [[[6.87966e-10, -12.8497, 0.757379, -0.00651612],
      [16.2087, -19.3776, 0.951508, -0.00645029],
      [14.513, -18.8625, 1.05542, -0.00918985]],
     [[1.07197e-07, -12.5469, 0.703086, -0.00585238],
      [0.0871522, -9.22628, 0.159628, -0.000343326],
      [12.1181, -17.5575, 0.940249, -0.00788125]],
     [[2.10191e-09, -12.2782, 0.661926, -0.00555279],
      [12.5105, -17.9998, 0.951807, -0.00732845],
      [12.8043, -17.8322, 0.972401, -0.00841528]],
     [[8.11926e-10, -12.7225, 0.737941, -0.00647355],
      [7.50649, -15.987, 0.889398, -0.00729282],
      [0.174541, -10.0266, 0.306882, -0.00186093]],
     [[3.81202e-09, -12.0926, 0.598943, -0.00430458],
      [8.72368, -17.2511, 1.06348, -0.00953327],
      [1.5205, -9.86713, 0.183806, -6.40377e-12]],
     [[0.000000137378, -12.9247, 0.769722, -0.00664936],
      [8.53877, -16.6167, 0.946138, -0.00788745],
      [8.47417, -14.3897, 0.581492, -0.00387111]]],
    [[[2.50079e-07, -12.5209, 0.678491, -0.00528954],
      [12.6171, -18.4205, 1.01802, -0.00807702],
      [10.4903, -18.0981, 1.10546, -0.00971519]],
     [[5.87069e-07, -12.0075, 0.585538, -0.00416654],
      [11.1348, -17.5468, 0.943652, -0.00729083],
      [0.949201, -10.5869, 0.267536, -6.04802e-05]],
     [[1.14857, -11.1478, 0.345528, -0.000841836],
      [10.9482, -17.1647, 0.909605, -0.00722404],
      [8.7569e-08, -10.4446, 0.316302, -0.00101964]],
     [[1.09759e-06, -11.5019, 0.48435, -0.00277852],
      [0.637937, -10.7065, 0.316211, -0.000801127],
      [5.67144e-07, -12.88, 0.831252, -0.00835441]],
     [[1.68853, -11.2582, 0.308152, -7.81686e-12],
      [9.44238, -17.1892, 1.00561, -0.00864837],
      [1.20713e-07, -12.2246, 0.669321, -0.0057622]],
     [[0.00217558, -10.8858, 0.347928, -0.000790679],
      [11.8583, -17.6423, 0.923581, -0.00703041],
      [3.24078, -13.4024, 0.668777, -0.00504175]]],
    [[[6.04158, -16.8155, 1.13335, -0.0105359],
      [8.24786, -17.0204, 1.05097, -0.00941875],
      [11.7617, -17.202, 0.864472, -0.00649032]],
     [[3.70947, -13.0663, 0.513818, -0.00222627],
      [16.7022, -21.9618, 1.42869, -0.012705],
      [6.8993, -14.8192, 0.740813, -0.00585407]],
     [[2.18472e-06, -11.9461, 0.583354, -0.00423414],
      [6.51489e-07, -10.5669, 0.353028, -0.00166977],
      [12.5113, -16.5038, 0.709888, -0.00471964]],
     [[0.812719, -11.3245, 0.390183, -0.00134086],
      [2.97251, -11.9374, 0.338592, -4.36096e-13],
      [13.8844, -17.5707, 0.818446, -0.00581811]],
     [[1.55496, -14.4569, 0.949497, -0.00857237],
      [0.34359, -10.5041, 0.286497, -0.000346977],
      [14.4141, -18.7457, 1.01652, -0.00845189]],
     [[1.26317e-08, -11.1424, 0.434251, -0.00236267],
      [6.58119, -15.8546, 0.930324, -0.00801288],
      [4.41865, -11.1991, 0.234652, -7.43723e-10]]],
    [[[6.87926, -12.8949, 0.334733, -6.38494e-06],
      [35.2336, -32.2007, 2.21489, -0.020555],
      [6.80949, -16.8945, 1.19056, -0.0127558]],
     [[0.95782, -12.4625, 0.599979, -0.00405342],
      [20.4051, -23.1936, 1.42408, -0.0120792],
      [10.277, -16.1457, 0.785186, -0.00612069]],
     [[0.236196, -11.6165, 0.458613, -0.002018],
      [12.8771, -19.6785, 1.26163, -0.0115917],
      [5.21194e-08, -12.551, 0.78718, -0.00794713]],
     [[8.40778, -14.9001, 0.534967, -0.00147246],
      [15.9376, -20.9945, 1.2908, -0.0110556],
      [10.4773, -16.2238, 0.783386, -0.00593478]],
     [[3.21187, -12.1221, 0.348938, -8.70415e-14],
      [13.8983, -19.1128, 1.04727, -0.00797426],
      [11.6342, -18.8428, 1.18853, -0.0107619]],
     [[3.7311, -12.4292, 0.419345, -0.00134704],
      [6.92884, -13.2494, 0.391862, -0.000767396],
      [5.5939, -14.4175, 0.729195, -0.00568477]]]]





    
if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-i',
        '--input_file',
        required=True
    )
    ap.add_argument(
        '-o',
        '--output_prefix',
        required=True
    )
    args = ap.parse_args()

    input_rootfile = args.input_file 
    output_pdfname = args.output_prefix + '.pdf'
    rootfile = TFile(input_rootfile)
    histos = load_histos(rootfile)

    # uncomment to view all histograms in file
    #for k,v in histos.items():
    #    print(k, v)
    hadron=OrderedDict()
    hadron[2212] = 1
    hadron[211] = 2
    hadron[-211] = 3
    hadron[321] = 4
    hadron[-321] = 5

    had_color=[kRed, kBlack, kBlue, kGreen, kRed]

    setup_global_options() 

    can = TCanvas('can', 'can', 800, 1100)
    can.SetBatch(kTRUE)

    lab = TLatex()
    lab.SetNDC()
    lab.SetTextFont(42)
    lab.SetTextSize(0.05)
    lab.SetTextColor(1)

    fiducial_cuts = []
    for particle, pid in hadron.items():
        #print(' getting fits for {}'.format(particle))
        temp_p = []
        fiducial_cuts.append(temp_p)
        #print('pid {}'.format(pid))
        #print('fid cuts list lvl 1 {}, size {}'.format(fiducial_cuts[pid-1], len(fiducial_cuts[pid-1])))
        for ss in range(0,6):
            #print('--> sector {}'.format( ss) )
            temp_s=[]
            fiducial_cuts[pid-1].append(temp_s)
            #print('fid cuts list lvl 2 {}, size {}'.format(fiducial_cuts[pid-1][ss], len(fiducial_cuts[pid-1][ss])))
            
            for rr in range(0,3):
                temp_r  = []
                
                #print('----> region {}'.format(rr) )
                a_min = minparams[pid][ss][rr][0]
                b_min = minparams[pid][ss][rr][1]
                c_min = minparams[pid][ss][rr][2]
                d_min = minparams[pid][ss][rr][3]

                a_max = maxparams[pid][ss][rr][0]
                b_max = maxparams[pid][ss][rr][1]
                c_max = maxparams[pid][ss][rr][2]
                d_max = maxparams[pid][ss][rr][3]

                cut_min = TF1("cut_min","[0] + [1]*log(x) + [2]*x + [3]*x*x", 5, 50)
                cut_max = TF1("cut_max","[0] + [1]*log(x) + [2]*x + [3]*x*x", 5, 50)
    
                cut_min.SetParameter(0, a_min)
                cut_min.SetParameter(1, b_min)
                cut_min.SetParameter(2, c_min)
                cut_min.SetParameter(3, d_min)
                
                cut_max.SetParameter(0, a_max)
                cut_max.SetParameter(1, b_max)
                cut_max.SetParameter(2, c_max)
                cut_max.SetParameter(3, d_max)
                                
                cut_min.SetLineColor(had_color[pid-1])
                cut_min.SetLineWidth(2)
                cut_max.SetLineColor(had_color[pid-1])
                cut_max.SetLineWidth(2)
                temp_cuts = [cut_min, cut_max]
                #print(fiducial_cuts)

                fiducial_cuts[pid-1][ss].append(temp_r)
                fiducial_cuts[pid-1][ss][rr] = temp_cuts
                #print('fid cuts list lvl 3 {}, size {}'.format(fiducial_cuts, len(fiducial_cuts[pid-1][ss][rr])))

    garb=[]
    
    can.Print('{}['.format(output_pdfname))    
    can.Divide(2,3)
    for ss in range(0,6):
        can.cd(ss+1)   
    
        histos.get('local_hit_rotated_dcr1_s{}_FTOF_pass_pos'.format(ss+1)).Reset()
        histos.get('local_hit_rotated_dcr1_s{}_FTOF_pass_pos'.format(ss+1)).Draw("colz")
        # proton
        fiducial_cuts[0][ss][0][0].Draw("same")
        fiducial_cuts[0][ss][0][1].Draw("same")

        # pip
        fiducial_cuts[1][ss][0][0].Draw("same")
        fiducial_cuts[1][ss][0][1].Draw("same")

        #kp
        fiducial_cuts[3][ss][0][0].Draw("same")
        fiducial_cuts[3][ss][0][1].Draw("same")

        leg1 = TLegend(0.7,0.7,0.9,0.9)    
        leg1.AddEntry(fiducial_cuts[0][ss][0][0],'Proton')
        leg1.AddEntry(fiducial_cuts[1][ss][0][0],'#pi^{+}')
        leg1.AddEntry(fiducial_cuts[3][ss][0][0],'K^{+}')

        leg1.Draw("same")
        garb.append(leg1)

        lab.DrawLatex(0.1, 0.925, 'DC R1 Positive, Local #Phi vs #Theta S{}'.format(ss+1))
        lab.DrawLatex(0.6, 0.015, 'Local #Theta (deg)')
        lab.SetTextAngle(90)
        lab.DrawLatex(0.035, 0.5, 'Local #Phi (deg)')
        lab.SetTextAngle(0)

    can.Print(output_pdfname)

    for ss in range(0,6):
        can.cd(ss+1)   
    
        #histos.get('local_hit_rotated_dcr2_s{}_FTOF_pass_pos'.format(ss+1)).Draw("colz")
        # proton
        fiducial_cuts[0][ss][1][0].Draw("same")
        fiducial_cuts[0][ss][1][1].Draw("same")

        # pip
        fiducial_cuts[1][ss][1][0].Draw("same")
        fiducial_cuts[1][ss][1][1].Draw("same")

        #kp
        fiducial_cuts[3][ss][1][0].Draw("same")
        fiducial_cuts[3][ss][1][1].Draw("same")
        
        leg1 = TLegend(0.7,0.7,0.9,0.9)    
        leg1.AddEntry(fiducial_cuts[0][ss][0][0],'Proton')
        leg1.AddEntry(fiducial_cuts[1][ss][0][0],'#pi^{+}')
        leg1.AddEntry(fiducial_cuts[3][ss][0][0],'K^{+}')

        leg1.Draw("same")
        garb.append(leg1)


        lab.DrawLatex(0.1, 0.925, 'DC R2 Positive, Local #Phi vs #Theta S{}'.format(ss+1))
        lab.DrawLatex(0.6, 0.015, 'Local #Theta (deg)')
        lab.SetTextAngle(90)
        lab.DrawLatex(0.035, 0.5, 'Local #Phi (deg)')
        lab.SetTextAngle(0)


    can.Print(output_pdfname)

    for ss in range(0,6):
        can.cd(ss+1)   
    
        histos.get('local_hit_rotated_dcr3_s{}_FTOF_pass_pos'.format(ss+1)).Reset()
        histos.get('local_hit_rotated_dcr3_s{}_FTOF_pass_pos'.format(ss+1)).Draw("colz")
        # proton
        fiducial_cuts[0][ss][2][0].Draw("same")
        fiducial_cuts[0][ss][2][1].Draw("same")

        # pip
        fiducial_cuts[1][ss][2][0].Draw("same")
        fiducial_cuts[1][ss][2][1].Draw("same")

        #kp
        fiducial_cuts[3][ss][2][0].Draw("same")
        fiducial_cuts[3][ss][2][1].Draw("same")
        
        leg1 = TLegend(0.7,0.7,0.9,0.9)    
        leg1.AddEntry(fiducial_cuts[0][ss][0][0],'Proton')
        leg1.AddEntry(fiducial_cuts[1][ss][0][0],'#pi^{+}')
        leg1.AddEntry(fiducial_cuts[3][ss][0][0],'K^{+}')

        leg1.Draw("same")
        garb.append(leg1)


        lab.DrawLatex(0.1, 0.925, 'DC R3 Positive, Local #Phi vs #Theta S{}'.format(ss+1))
        lab.DrawLatex(0.6, 0.015, 'Local #Theta (deg)')
        lab.SetTextAngle(90)
        lab.DrawLatex(0.035, 0.5, 'Local #Phi (deg)')
        lab.SetTextAngle(0)
    
    can.Print(output_pdfname)


    ################################
    ## now check fiducial position of negative tracks
    for ss in range(0,6):
        can.cd(ss+1)   
    
        histos.get('local_hit_rotated_dcr1_s{}_FTOF_pass_neg'.format(ss+1)).Reset()
        histos.get('local_hit_rotated_dcr1_s{}_FTOF_pass_neg'.format(ss+1)).Draw("colz")
        # pim
        fiducial_cuts[2][ss][0][0].Draw("same")
        fiducial_cuts[2][ss][0][1].Draw("same")

        #km
        fiducial_cuts[4][ss][0][0].Draw("same")
        fiducial_cuts[4][ss][0][1].Draw("same")

        leg1 = TLegend(0.7,0.7,0.9,0.9)    
        leg1.AddEntry(fiducial_cuts[2][ss][0][0],'#pi^{-}')
        leg1.AddEntry(fiducial_cuts[4][ss][0][0],'K^{-}')

        leg1.Draw("same")
        garb.append(leg1)

        lab.DrawLatex(0.1, 0.925, 'DC R1 Negatives, Local #Phi vs #Theta S{}'.format(ss+1))
        lab.DrawLatex(0.6, 0.015, 'Local #Theta (deg)')
        lab.SetTextAngle(90)
        lab.DrawLatex(0.035, 0.5, 'Local #Phi (deg)')
        lab.SetTextAngle(0)

    can.Print(output_pdfname)

    for ss in range(0,6):
        can.cd(ss+1)   
    
        histos.get('local_hit_rotated_dcr2_s{}_FTOF_pass_neg'.format(ss+1)).Reset()
        histos.get('local_hit_rotated_dcr2_s{}_FTOF_pass_neg'.format(ss+1)).Draw("colz")

        # pim
        fiducial_cuts[2][ss][1][0].Draw("same")
        fiducial_cuts[2][ss][1][1].Draw("same")

        #km
        fiducial_cuts[4][ss][1][0].Draw("same")
        fiducial_cuts[4][ss][1][1].Draw("same")
        
        leg1 = TLegend(0.7,0.7,0.9,0.9)    
        leg1.AddEntry(fiducial_cuts[2][ss][0][0],'#pi^{-}')
        leg1.AddEntry(fiducial_cuts[4][ss][0][0],'K^{-}')

        leg1.Draw("same")
        garb.append(leg1)


        lab.DrawLatex(0.1, 0.925, 'DC R2 Negatives, Local #Phi vs #Theta S{}'.format(ss+1))
        lab.DrawLatex(0.6, 0.015, 'Local #Theta (deg)')
        lab.SetTextAngle(90)
        lab.DrawLatex(0.035, 0.5, 'Local #Phi (deg)')
        lab.SetTextAngle(0)


    can.Print(output_pdfname)

    for ss in range(0,6):
        can.cd(ss+1)   
    
        histos.get('local_hit_rotated_dcr3_s{}_FTOF_pass_neg'.format(ss+1)).Reset()
        histos.get('local_hit_rotated_dcr3_s{}_FTOF_pass_neg'.format(ss+1)).Draw("colz")
        
        # pip
        fiducial_cuts[2][ss][2][0].Draw("same")
        fiducial_cuts[2][ss][2][1].Draw("same")

        #kp
        fiducial_cuts[4][ss][2][0].Draw("same")
        fiducial_cuts[4][ss][2][1].Draw("same")
        
        leg1 = TLegend(0.7,0.7,0.9,0.9)    
        leg1.AddEntry(fiducial_cuts[2][ss][0][0],'#pi^{-}')
        leg1.AddEntry(fiducial_cuts[4][ss][0][0],'K^{-}')

        leg1.Draw("same")
        garb.append(leg1)

        lab.DrawLatex(0.1, 0.925, 'DC R3 Negatives, Local #Phi vs #Theta S{}'.format(ss+1))
        lab.DrawLatex(0.6, 0.015, 'Local #Theta (deg)')
        lab.SetTextAngle(90)
        lab.DrawLatex(0.035, 0.5, 'Local #Phi (deg)')
        lab.SetTextAngle(0)
    
    can.Print(output_pdfname)




    can.Print('{}]'.format(output_pdfname))
















'''
cut_min.SetParameter(0,0.000000137378)
cut_min.SetParameter(1,-12.9247)
cut_min.SetParameter(2,0.769722)
cut_min.SetParameter(3,-0.00664936)

cut_max.SetParameter(0,-0.0000000585515)
cut_max.SetParameter(1,12.5116)
cut_max.SetParameter(2,-0.688741)
cut_max.SetParameter(3,0.00557297)
'''
