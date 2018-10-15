from netpyne import specs
from netpyne import sim
from neuron import h
import numpy as np
import random
import os
import sys

netParams = specs.NetParams()  # object of class NetParams to store the network parameters

try:
    from __main__ import cfg  # import SimConfig object with params from parent module
except:
    from cfg import cfg

try: 
    import batch_utils
except:
    curpath = os.getcwd()
    while os.path.split(curpath)[1] != "sim":
        curpath = os.path.split(curpath)[0]
    sys.path.append(curpath)
    import batch_utils

# Find path to cells directory
curpath = os.getcwd()
while os.path.split(curpath)[1] != "sim":
    oldpath = curpath
    curpath = os.path.split(curpath)[0]
    if oldpath == curpath:
        raise Exception("Couldn't find cells directory. Try running from within eee/sim file tree.")
cellpath = os.path.join(curpath, "cells")

eeeS_path = os.path.join(cellpath, 'eeeS.py')
PV_path   = os.path.join(cellpath, 'FS3.hoc')

#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# General network parameters
#------------------------------------------------------------------------------
netParams.scale = cfg.scale # Scale factor for number of cells
netParams.sizeX = cfg.sizeX # x-dimension (horizontal length) size in um
netParams.sizeY = cfg.sizeY # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = cfg.sizeZ # z-dimension (horizontal depth) size in um
netParams.shape = 'cylinder' # cylindrical (column-like) volume

#------------------------------------------------------------------------------
# General connectivity parameters
#------------------------------------------------------------------------------
#netParams.scaleConnWeight = 1.0 # Connection weight scale factor (default if no model specified)
#netParams.scaleConnWeightNetStims = 1.0 #0.5  # scale conn weight factor for NetStims
netParams.defaultThreshold = -20.0 # spike threshold, 10 mV is NetCon default, lower it for all cells
netParams.defaultDelay = 2.0 # default conn delay (ms)
netParams.propVelocity = 100.0 # propagation velocity (um/ms)
netParams.probLengthConst = 150.0 # length constant for conn probability (um)


#------------------------------------------------------------------------------
# Cell parameters
#------------------------------------------------------------------------------

layer = {'5':[0.2,0.623],'long':[0.7,1.0]} #yRange in column

cellParamLabels = ['PT5_1', 'PT5_2', 'PT5_3', 'PT5_4'] 

reducedSecList = {  # section Lists for reduced cell model
    'alldend':  ['Adend1', 'Adend2', 'Adend3','Bdend1','Bdend2','Bdend3'], 
    'spiny':  ['Adend1', 'Adend2', 'Adend3', 'Bdend1','Bdend2'],
    'apicdend': ['Adend1', 'Adend2', 'Adend3'],
    'perisom':  ['soma_0'],
    'basaldend': ['Bdend1','Bdend2', 'Bdend3']}

###
#import and modify PT5 cell
###
if 'PT5_1' in cellParamLabels:

    cellRule = netParams.importCellParams(label='PT5_1', conds={'cellType': 'PT5_1', 'cellModel': 'HH_reduced'}, fileName=eeeS_path, cellName='MakeCell')

    sec = 'soma_2'
    if cfg.noise:
        
        netParams.cellParams['PT5_1']['secs'][sec]['pointps']= {'noise': {'mod'  : 'Gfluctp', 
                                                                         'loc': 0.5,
                                                                          'std_e': 0.012*cfg.exc_noise_amp,
                                                                          'g_e0' : 0.0121, 
                                                                          'tau_i': 10.49*cfg.noise_tau, 
                                                                          'tau_e': 2.728*cfg.noise_tau, 
                                                                          'std_i': 0.0264*cfg.inh_noise_amp, 
                                                                          'g_i0' : 0.0573, 
                                                                          'E_e'  : cfg.e_exc_noise, 
                                                                          'E_i'  : cfg.e_inh_noise, 
                                                                          'seed1': 'gid', 'seed2': sim.id32('gfluctp'), 'seed3': cfg.seeds['stim']}}
          
sec = 'soma_2'
for k,label in enumerate(cellParamLabels):    
    if not k == 0: 
        import copy
        cellRule = copy.deepcopy(netParams.cellParams['PT5_1'].todict())
        cellRule['conds']['cellType'] = [label]
        netParams.cellParams[label] = cellRule
        if cfg.noise:

            netParams.cellParams[label]['secs'][sec]['pointps'] = {}     
        
            netParams.cellParams[label]['secs'][sec]['pointps']= {'noise': {'mod'  : 'Gfluctp', 
                                                                            'loc': 0.5, 
                                                                            'std_e': 0.012*cfg.exc_noise_amp,
                                                                            'g_e0' : 0.0121, 
                                                                            'tau_i': 10.49*cfg.noise_tau, 
                                                                            'tau_e': 2.728*cfg.noise_tau, 
                                                                            'std_i': 0.0264*cfg.inh_noise_amp,
                                                                            'g_i0' : 0.0573, 
                                                                            'E_e'  : cfg.e_exc_noise, 
                                                                            'E_i'  : cfg.e_inh_noise, 
                                                                            'seed1': 'gid', 'seed2': sim.id32('gfluctp'), 'seed3': cfg.seeds['stim']}}

for cell_label, cell_params in netParams.cellParams.iteritems():
  if  cell_label in cellParamLabels:          
    for secName,sec in cell_params['secs'].iteritems():         
        sec['vinit'] = cfg.vinit_PT5 #-80.0 #-88.12656642859307   # set vinit for all secs
        
        #if hasattr(cfg, 'vinit_PT5'):
        if 'pas' in sec['mechs']:

            if sec['mechs']['pas']['e'] != cfg.vinit_PT5:
            
                print(cell_label)
                print(secName)
                print("e_pas orig:")
                print(sec['mechs']['pas']['e'])
                sec['mechs']['pas']['e'] = cfg.vinit_PT5
                print("e_pas new:")
                print(sec['mechs']['pas']['e'])
                print

        if hasattr(cfg, 'allNaScale') or hasattr(cfg, 'dendNaScale'):
                if 'na' in sec['mechs']:
                    orig_na = sec['mechs']['na']['gbar']
                    if hasattr(cfg, 'dendNaScale') and (("basal" in secName) or ("axon" in secName)) and (cfg.dendNaScale != 1.0):
                        sec['mechs']['na']['gbar'] = list(np.array(orig_na, ndmin=1) * cfg.dendNaScale) 
                    if hasattr(cfg, 'allNaScale') and (cfg.allNaScale != 1.0):
                        sec['mechs']['na']['gbar'] = list(np.array(orig_na, ndmin=1) * cfg.allNaScale)
            
        if hasattr(cfg, 'allKScale') or hasattr(cfg, 'dendKScale'):
                
                if 'kv' in sec['mechs']:
                    orig_kv = sec['mechs']['kv']['gbar']
                    if hasattr(cfg, 'dendKScale') and (("basal" in secName)  or ("axon" in secName)) and (cfg.dendKScale != 1.0):
                        sec['mechs']['kv']['gbar'] = list(np.array(orig_kv, ndmin=1) * cfg.dendKScale)
                    if hasattr(cfg, 'allKScale') and (cfg.allKScale != 1.0):
                        sec['mechs']['kv']['gbar'] = list(np.array(orig_kv, ndmin=1) * cfg.allKScale)

                if 'kap' in sec['mechs']:
                    orig_kap = sec['mechs']['kap']['gkabar']
                    if hasattr(cfg, 'dendKScale') and (("basal" in secName) or ("axon" in secName)) and (cfg.dendKScale != 1.0):
                        sec['mechs']['kap']['gkabar'] = list(np.array(orig_kap, ndmin=1) * cfg.dendKScale)
                    if hasattr(cfg, 'allKScale') and (cfg.allKScale != 1.0):
                        sec['mechs']['kap']['gkabar'] = list(np.array(orig_kap, ndmin=1) * cfg.allKScale)

                if 'kad' in sec['mechs']:
                    orig_kad = sec['mechs']['kad']['gkabar']
                    if hasattr(cfg, 'dendKScale') and (("basal" in secName) or ("axon" in secName)) and (cfg.dendKScale != 1.0):
                        sec['mechs']['kad']['gkabar'] = list(np.array(orig_kad, ndmin=1) * cfg.dendKScale)
                    if hasattr(cfg, 'allKScale') and (cfg.allKScale != 1.0):
                        sec['mechs']['kad']['gkabar'] = list(np.array(orig_kad, ndmin=1) * cfg.allKScale)

                if 'kBK' in sec['mechs']:
                    orig_kBK = sec['mechs']['kBK']['gpeak']
                    if hasattr(cfg, 'dendKScale') and (("basal" in secName) or ("axon" in secName)) and (cfg.dendKScale != 1.0):
                        sec['mechs']['kBK']['gpeak'] = list(np.array(orig_kBK, ndmin=1) * cfg.dendKScale)
                    if hasattr(cfg, 'allKScale') and (cfg.allKScale != 1.0):
                        sec['mechs']['kBK']['gpeak'] = list(np.array(orig_kBK, ndmin=1) * cfg.allKScale)

        if hasattr(cfg, 'allCaScale') or hasattr(cfg, 'dendCaScale'):

                if 'ca' in sec['mechs']:
                    orig_ca = sec['mechs']['ca']['gbar']
                    if hasattr(cfg, 'dendCaScale') and (("basal" in secName) or ("axon" in secName)) and (cfg.dendCaScale != 1.0):
                        sec['mechs']['ca']['gbar'] = list(np.array(orig_ca, ndmin=1) * cfg.dendCaScale)
                    if hasattr(cfg, 'allCaScale') and (cfg.allCaScale != 1.0):
                        sec['mechs']['ca']['gbar'] = list(np.array(orig_ca, ndmin=1) * cfg.allCaScale)

                if 'it' in sec['mechs']:
                    orig_it = sec['mechs']['it']['gbar']
                    if hasattr(cfg, 'dendCaScale') and (("basal" in secName) or ("axon" in secName)) and (cfg.dendCaScale != 1.0):
                        sec['mechs']['it']['gbar'] = list(np.array(orig_it, ndmin=1) * cfg.dendCaScale)
                    if hasattr(cfg, 'allCaScale') and (cfg.allCaScale != 1.0):
                        sec['mechs']['it']['gbar'] = list(np.array(orig_it, ndmin=1) * cfg.allCaScale)

        if hasattr(cfg, 'ihScale'):
                if 'ih' in sec['mechs']:
                    sec['mechs']['ih']['gbar'] = cfg.ihScale * sec['mechs']['ih']['gbar']

        if hasattr(cfg, 'RmScale'):
            if type(sec['mechs']['pas']['g']) == list:
                sec['mechs']['pas']['g'] = list((1.0/cfg.RmScale) * np.array(sec['mechs']['pas']['g']))
            elif type(sec['mechs']['pas']['g']) == float:
                sec['mechs']['pas']['g'] = (1.0/cfg.RmScale) * sec['mechs']['pas']['g']
            else:
                raise Exception("Error occurred adjusting RmScale in " + cell_label + ", " + secName)

        if hasattr(cfg, 'RaScale'):
            orig_ra = sec['geom']['Ra']
            sec['geom']['Ra'] = cfg.RaScale * sec['geom']['Ra']



#import PV5 cell

cellRule = netParams.importCellParams(label='PV5', conds={'cellType':'PV', 'cellModel':'HH_simple'}, fileName=PV_path, cellName='FScell1', cellInstance = True)

for cell_label, cell_params in netParams.cellParams.iteritems():
  if  cell_label == 'PV5':          
    for secName,sec in cell_params['secs'].iteritems():         
        sec['vinit'] = cfg.vinit_PV5

        if 'pas' in sec['mechs']:

            if sec['mechs']['pas']['e'] != cfg.vinit_PV5:
            
                print(cell_label)
                print(secName)
                print("e_pas orig:")
                print(sec['mechs']['pas']['e'])
                sec['mechs']['pas']['e'] = cfg.vinit_PV5
                print("e_pas new:")
                print(sec['mechs']['pas']['e'])

        if hasattr(cfg, 'RmScale_PV5'):
            if type(sec['mechs']['pas']['g']) == list:
                sec['mechs']['pas']['g'] = list((1.0/cfg.RmScale_PV5) * np.array(sec['mechs']['pas']['g']))
            elif type(sec['mechs']['pas']['g']) == float:
                sec['mechs']['pas']['g'] = (1.0/cfg.RmScale_PV5) * sec['mechs']['pas']['g']
            else:
                raise Exception("Error occurred adjusting RmScale in " + cell_label + ", " + secName)

        if hasattr(cfg, 'RaScale'):
            orig_ra = sec['geom']['Ra']
            sec['geom']['Ra'] = cfg.RaScale_PV5 * sec['geom']['Ra']


if cfg.noise_PV5:
        
        netParams.cellParams['PV5']['secs']['soma']['pointps']= {'noise': {'mod'  : 'Gfluctp', 
                                                                           'loc': 0.5, 
                                                                           'std_e': 0.012*cfg.exc_noise_amp_icells,
                                                                           'g_e0' : 0.0121, 
                                                                           'tau_i': 10.49*cfg.noise_tau, 
                                                                           'tau_e': 2.728*cfg.noise_tau, 
                                                                           'std_i': 0.0264*cfg.inh_noise_amp_icells, 
                                                                           'g_i0' : 0.0573, 
                                                                           'E_e'  : cfg.e_exc_noise_icells, 
                                                                           'E_i'  : cfg.e_inh_noise_icells,
                                                                           'seed1': 'gid', 'seed2': sim.id32('gfluctp'), 'seed3': cfg.seeds['stim']}}

#------------------------------------------------------------------------------
# Population parameters
#------------------------------------------------------------------------------

columnA = [50, 350] #xrange

#'Gabbott97a': [118193, 41283, 116193] Densities L2,L5,L6
PFC = {
    'VIP': [6817.0, 3976.0, 3172.0],
    'I'  : [24347.757999999998, 14201.351999999999, 11328.817500000001],
    'PV' : [9983.0, 5823.0, 4645.0],
    'SOM': [7548.0, 4402.0, 3512.0],
    'E'  : [93845.242, 27081.648, 104864.1825]
      }

#number of cells per column L2,L5,L6
num = {
    'E'  : [3111, 851, 3135],
    'PV' : [330, 183, 138],
    'SOM': [250, 138, 105],
    'VIP': [225, 125, 94]
      }


#numcellsPT5_0 = 200
numcellsPT5 = 250 #80
numcellsPV5 = int((numcellsPT5*4)/2.0)

for k,label in enumerate(cellParamLabels):
    netParams.popParams[label]  = {'cellModel': 'HH_reduced', 'cellType': label,  'xRange': columnA, 'yRange': layer['5'], 'numCells': numcellsPT5} #'gridSpacing':10}# int(p*1.0*num['E'][1])}


netParams.popParams['PV5']  = {'cellModel': 'HH_simple',  'cellType': 'PV','xRange': columnA, 'yRange': layer['5'], 'numCells': numcellsPV5} #'gridSpacing': 10}#int(p*2.43*num['PV'][1])}


if cfg.singleCellPops:
    for pop in netParams.popParams.values(): pop['numCells'] = 1


#------------------------------------------------------------------------------
# Synaptic mechanism parameters
#------------------------------------------------------------------------------
#### MyExp2syn synaptic mechanisms
netParams.synMechParams['GABAAfast'] = {'mod':'MyExp2SynBB','tau1':0.07,'tau2':18.2,'e': cfg.GABAAfast_e}
netParams.synMechParams['GABAAslow'] = {'mod': 'MyExp2SynBB','tau1': 10, 'tau2': 200, 'e': cfg.GABAAslow_e}

#### DMS synaptic mechanisms 
netParams.synMechParams['NMDA'] = {'mod': 'NMDAeee', 'Cdur': cfg.CdurNMDAScale * 1.0, 'Alpha': cfg.NMDAAlphaScale * 4.0, 'Beta': cfg.NMDABetaScale * 0.0015, 'gmax': cfg.NMDAgmax, 'e': cfg.eNMDA}
netParams.synMechParams['AMPA'] = {'mod': 'AMPA', 'gmax': cfg.ratioAMPANMDA * cfg.NMDAgmax}

ESynMech = ['AMPA','NMDA']
ISynMech = ['GABAAfast','GABAAslow']


#------------------------------------------------------------------------------
# Current clamps (IClamp)
#------------------------------------------------------------------------------
if cfg.addIClamp:
    for key in [k for k in dir(cfg) if k.startswith('IClamp')]:
        params = getattr(cfg, key, None)
        
        for i in range(numcellsPV5):
          # add stim source
          netParams.stimSourceParams[str(key)+'_'+str(i)] = {
            'type': 'IClamp',
            'del': i/64.0,
            'dur': params['dur'],
            'amp': params['amp']}    

          # connect stim source to target
          netParams.stimTargetParams[str(key)+'_'+str(i)+'_'+params['pop']] =  {
            'source': str(key)+'_'+str(i),
            'conds': {'pop': params['pop'], 'cellList': [i]},
            'sec': params['sec'],
            'loc': params['loc']}

#------------------------------------------------------------------------------
# Synaptic noise to PT5_0 pop
#------------------------------------------------------------------------------

if cfg.noise_ptps:  

    for i in range(numcellsPT5):
        netParams.stimSourceParams['noise_fluct'] = {'type': 'Gfluctp','std_e': 0.012*cfg.exc_noise_amp, 'g_e0': 0.0121, 'tau_i': 10.49*cfg.noise_tau, 'tau_e': 2.728*cfg.noise_tau, 'std_i': 0.0264*cfg.inh_noise_amp, 'g_i0': 0.0573, 'E_e': cfg.e_exc_noise, 'E_i': cfg.e_inh_noise} #'seed': i+100} 
        netParams.stimTargetParams['noise_fluct'+'_'+'PT5_1'] =  {
            'source': 'noise_fluct',
            'conds': {'pop':'PT5_1','cellList': [i]},
            'sec': 'soma_2',
            'loc': 0.5,
            }  

    for k,label in enumerate(cellParamLabels):    
        if not k == 0: 
            for i in range(numcellsPT5):
                netParams.stimSourceParams['noise_fluct'] = {'type': 'Gfluctp','std_e': 0.012*cfg.exc_noise_amp, 'g_e0': 0.0121, 'tau_i': 10.49*cfg.noise_tau, 'tau_e': 2.728*cfg.noise_tau, 'std_i': 0.0264*cfg.inh_noise_amp, 'g_i0': 0.0573, 'E_e': cfg.e_exc_noise, 'E_i': cfg.e_inh_noise} #'seed': i+100} 
                netParams.stimTargetParams['noise_fluct'+'_'+label] =  {
                    'source': 'noise_fluct',
                    'conds': {'pop':label,'cellList': [i]},
                    'sec': 'soma_2',
                    'loc': 0.5,
                    }



#------------------------------------------------------------------------------
# Long range input pulses
#------------------------------------------------------------------------------
## Long-range input populations (VecStims)
if cfg.addLongConn:
  
    if cfg.longConnPV5 == 1:
        numCells = cfg.numCellsLong
        noise = cfg.noiseLong
        start = cfg.startLong
              

        longPops = ['dTC']
        ## create populations with fixed 
        for longPop in longPops:
            netParams.popParams[longPop] = {'cellModel': 'VecStim', 
                            'numCells': numCells, 
                            'rate': cfg.ratesLong[longPop], 
                            'noise': noise, 
                            'start': start, 
                            'pulses': [],#pulses 
                            'yRange': layer['long']
                            #'spkTimes': spkTimes
                            }

#------------------------------------------------------------------------------
# NetStim inputs
#------------------------------------------------------------------------------

L5 = cellParamLabels
L5.append('PV5')
plateau = [v for v in cellParamLabels]# if not v=='PT5_0']
cfg.analysis['plotRaster']['include'].append(L5)
cfg.analysis['plotTraces']['include'].append((('PT5_1'),0))
cfg.analysis['plotTraces']['include'].append((('PT5_1'),5))
cfg.analysis['plotTraces']['include'].append((('PT5_1'),126))
#cfg.analysis['plotTraces']['include'].append((('PT5_1'),125))
#cfg.analysis['plotTraces']['include'].append((('PT5_2'),0))
#cfg.analysis['plotTraces']['include'].append((('PT5_2'),125))
#cfg.analysis['plotTraces']['include'].append((('PV5'),0))
#cfg.analysis['plotTraces']['include'].append((('PV5'),1))

ns_list =[]

connList3 = [[0,i] for i in range(int(250.0/2.0))]

if cfg.addNetStim == 1:

    for nslabel in [k for k in dir(cfg) if k.startswith('NetStim')]:
        ns = getattr(cfg, nslabel, None)        
          
        branch_length = netParams.cellParams['PT5_1']['secs'][ns['sec']]['geom']['L']
                  
        if "ExSyn" in nslabel:
            cur_locs = np.linspace(cfg.synLocMiddle-cfg.synLocRadius, cfg.synLocMiddle+cfg.synLocRadius, cfg.numExSyns)
            cur_dists = branch_length * np.abs(cur_locs - cfg.synLocMiddle)
            cur_weights = (cfg.glutAmp * cfg.glutAmpExSynScale) * (1 - cur_dists * cfg.glutAmpDecay/100)
            cur_weights = [weight if weight > 0.0 else 0.0 for weight in cur_weights]
            cur_delays = cfg.initDelay + (cfg.exSynDelay * cur_dists)
                  
              
        elif "Syn" in nslabel:
            cur_locs = np.linspace(cfg.synLocMiddle-cfg.synLocRadius, cfg.synLocMiddle+cfg.synLocRadius, cfg.numSyns)
            cur_dists = branch_length * np.abs(cur_locs - cfg.synLocMiddle)
            cur_weights = cfg.glutAmp * (1 - cur_dists * cfg.glutAmpDecay/100)
            cur_weights = [weight if weight > 0.0 else 0.0 for weight in cur_weights]
            cur_delays = cfg.initDelay + (cfg.synDelay * cur_dists)                
              
        else:
            raise Exception("NetStim must have Syn or ExSyn in name")
          
        spkTimes = list(np.linspace(ns['start'],ns['start']+(ns['interval']*(ns['number']-1)), num= ns['number']))  

        netParams.popParams['plateau_stim'] = {'cellModel': 'VecStim',
                            'numCells': 40, 
                            'noise': ns['noise'], 
                            'yRange': layer['long'], 
                            'spkTimes': spkTimes}
        
        ns_list.append('plateau_stim')                   

        # add stim source
        netParams.stimSourceParams[nslabel] = {'type': 'NetStim', 'start': ns['start'], 'interval': ns['interval'], 'noise': ns['noise'], 'number': ns['number']}  

        # connect stim source to target
        for cur_pop in plateau:#enumerate(cellParamLabels):    
            if not cur_pop == 'PV5': 
                for i in range(len(ns['synMech'])):
                    netParams.stimTargetParams[nslabel+'_'+cur_pop+'_'+ns['synMech'][i]] = \
                        {'source': nslabel, 'conds': {'pop': cur_pop, 'cellList': range(0,125)}, 'sec': ns['sec'], 'synsPerConn': cfg.numSyns, 'loc': list(cur_locs), 'synMech': ns['synMech'][i], 'weight': list(cur_weights), 'delay': list(cur_delays)}
          
    for nslabel1 in [k for k in dir(cfg) if k.startswith('Stim')]:
        ns1 = getattr(cfg, nslabel1, None)   

        ns_list.append(nslabel1)  

        cfg.analysis['plotRaster']['include'].append(ns_list)

        spkTimes1 = list(np.linspace(ns1['start'],ns1['start']+(ns1['interval']*(ns1['number']-1)), num= ns1['number']))
        netParams.popParams[nslabel1] = {'cellModel': 'VecStim', 
                      'numCells': 40, 
                      'noise': ns1['noise'],
                      'yRange': layer['long'],
                      'spkTimes': spkTimes1,
                      }
    
#------------------------------------------------------------------------------
# Local connectivity parameters
#------------------------------------------------------------------------------
if cfg.addConns:
    
    excL5 = cellParamLabels #['PT5_0','PT5_1', 'PT5_2', 'PT5_3', 'PT5_4', 'PT5_5','PT5_6','PT5_7','PT5_8','PT5_9','PT5_10']
    inhL5 = ['PV5']
  
    # (Exc) to  Exc L5
  
    for prePop in excL5:
        for postPop in excL5:
            ruleLabel = prePop+'->'+postPop
            netParams.connParams[ruleLabel] = {
                'preConds': {'pop': prePop},
                'postConds': {'pop': postPop},
                'synMech': ESynMech, 
                'weight': 1.0*cfg.EEgain, 
                'synMechWeightFactor': cfg.ratiobdend,
                'delay': 'defaultDelay+dist_3D/propVelocity',
                'convergence': cfg.EEconv,#5,#3,
                'loc': 0.3,
                'sec': 'basal_8'}
  
    #exc to inh

    for prePop in excL5:
        for postPop in inhL5:
            ruleLabel = prePop+'->'+postPop
            netParams.connParams[ruleLabel] = {
                'preConds': {'pop': prePop},
                'postConds': {'pop': postPop},
                'synMech': 'AMPA',
                'weight': 2.0*cfg.EIgain, 
                'delay': 'defaultDelay+dist_3D/propVelocity',
                'convergence': 3,
                'loc': 0.5,
                'sec': 'soma'}

  
    #inh to exc 
    for prePop in inhL5:
        for postPop in excL5:
            ruleLabel = prePop+'->'+postPop
            netParams.connParams[ruleLabel] = {
                'preConds': {'pop': prePop},
                'postConds': {'pop': postPop},
                'synMech': ISynMech, 
                'weight': 0.001*cfg.IEgain, 
                'synMechWeightFactor': [0.7,0.3],
                'delay': 'defaultDelay+dist_3D/propVelocity',
                'convergence': 4,
                'loc': 0.5,
                'sec': 'soma_2'}
  
    #inh to inh
    for prePop in inhL5:
        for postPop in inhL5:
            ruleLabel = prePop+'->'+postPop
            netParams.connParams[ruleLabel] = {
                'preConds': {'pop': prePop},
                'postConds': {'pop': postPop},
                'synMech': 'GABAAfast',
                'weight': 0.002*cfg.IIgain, 
                'delay': cfg.IIdelay, #'defaultDelay+dist_3D/propVelocity',
                'convergence': cfg.IIconv,
                'loc': 0.5,
                'sec': 'soma'}
  
###########


if cfg.addLongConn:
  
    longPops = ['dTC']
    excL5 = cellParamLabels
    plateau = [v for v in cellParamLabels  if  not v=='PV5']
    PV5 = ['PV5']  
  
    cellnumber = numcellsPT5*10
    cellnumber2 = int(numcellsPV5*1.0)
    
    connList = [[0,i] for i in range(numcellsPT5)]
    connList2 = [[i,i] for i in range(cellnumber2)]
    connList3 = [[0,i] for i in range(int(numcellsPT5/2.0))]
    connList4 = [[(i+500),i] for i in range(numcellsPT5)]
    
    if cfg.longConnPT5:
        for prePop in longPops:
            for postPop in excL5:
                ruleLabel = prePop+'->'+postPop
                netParams.connParams[ruleLabel] = {
                    'preConds': {'pop': prePop},
                    'postConds': {'pop': postPop},
                    'synMech': ESynMech,
                    'weight': cfg.weightLong, 
                    'synMechWeightFactor':  cfg.ratioapical,
                    'delay': 1, 
                    'connList': connList4,
                    'loc': 0.5,
                    'sec': 'soma'}   

    if cfg.longConnPV5:
        for prePop in longPops:
            for postPop in PV5:
                ruleLabel = prePop+'->'+postPop
                netParams.connParams[ruleLabel] = {
                    'preConds': {'pop': prePop},
                    'postConds': {'pop': postPop},
                    'synMech': 'AMPA',
                    'weight': cfg.weightLongInh,
                    'delay': 1, 
                    'connList': connList2,
                    'loc': 0.5,
                    'sec': 'dend'}  

    if cfg.addNetStim:   
                      
        for nslabel1 in [k for k in dir(cfg) if k.startswith('Stim')]:
            ns1 = getattr(cfg, nslabel1, None) 
            for postPop in plateau:             
                ruleLabel = nslabel1+'->'+postPop
                netParams.connParams[ruleLabel] = {
                    'preConds': {'pop': nslabel1},
                    'postConds': {'pop': postPop},
                    'synMech': ESynMech,                   
                    'weight': ns1['weight'], #cfg.glutAmp3,
                    'synMechWeightFactor':  cfg.ratioapical, 
                    'delay': 1, 
                    'synsPerConn': 2,#numActiveSpines,  
                    'connList': connList,
                    'loc': ns1['loc'], 
                    'sec': ns1['sec']}

                  
