import batch_utils
import batch_analysis
import matplotlib.pyplot as plt
from netpyne import sim
from itertools import product
plt.ion()

batchdatadir = "data"


def analyze_batch(batchLabel, batchdatadir=batchdatadir):

    params, data = batch_utils.load_batch(batchLabel, batchdatadir=batchdatadir)
    batch = (batchLabel, params, data)

    batch_analysis.plot_batch_raster(batch, timeRange=[100, 1000], markerSize=0.5, orderInverse=False)
    batch_analysis.plot_vtraces(batch, timerange=[100, 1000])
    batch_analysis.plot_batch_conn(batch)


#analyze_batch('v01_batch03')
#analyze_batch('v01_batch04')
#analyze_batch('v01_batch05')
#analyze_batch('v01_batch06')


# Individual plots

def plot_batch_ind_conn(batchLabel, batchdatadir='data', includePre = ['all'], includePost = ['all'], feature = 'strength', orderBy = 'gid', figSize = (10,10), groupBy = 'pop', groupByIntervalPre = None, groupByIntervalPost = None, graphType = 'matrix', synOrConn = 'syn', synMech = None, connsFile = None, tagsFile = None, clim = None, fontSize = 12, saveData = None, saveFig = True, showFig = True, save=True, outputdir="batch_figs", filename=None, **kwargs):
    """Plots individual connectivity plots for each parameter combination."""

    from netpyne import specs

    if type(batchLabel) == str:
        params, data = batch_utils.load_batch(batchLabel, batchdatadir=batchdatadir)
    elif type(batchLabel) == tuple:
        batchLabel, params, data = batchLabel
    else:
        raise Exception()

    simLabels = data.keys()

    for simLabel in simLabels:

        print('Plotting sim: ' + simLabel)

        datum = data[simLabel]

        if saveFig:
            saveFig = batchdatadir + '/' + batchLabel + '/' + 'connFig_' + simLabel + '.png'

        cfg = specs.SimConfig(datum['simConfig'])
        cfg.createNEURONObj = False

        sim.initialize()  # create network object and set cfg and net params
        sim.loadAll('', data=datum, instantiate=False)
        sim.setSimCfg(cfg)
        try:
            print('Cells created: ' + str(len(sim.net.allCells)))
        except:
            print('Alternate sim loading...')
            sim.net.createPops()     
            sim.net.createCells()
            sim.setupRecording()
            sim.gatherData() 

        sim.allSimData = datum['simData']

        sim.analysis.plotConn(includePre=includePre, includePost=includePost, feature=feature, orderBy=orderBy, figSize=figSize, groupBy=groupBy, groupByIntervalPre=groupByIntervalPre, groupByIntervalPost=groupByIntervalPost, graphType=graphType, synOrConn=synOrConn, synMech=synMech, connsFile=connsFile, tagsFile=tagsFile, clim=clim, fontSize=fontSize, saveData=saveData, saveFig=saveFig, showFig=showFig)


batchLabel = 'v01_batch06'
params, data = batch_utils.load_batch(batchLabel, batchdatadir=batchdatadir)
batchData = (batchLabel, params, data)

plot_batch_ind_conn(batchData)



#batchLabel = "v01_batch03"
#params, data = batch_utils.load_batch(batchLabel, batchdatadir=batchdatadir)
#batch = (batchLabel, params, data)
#include = ['PT5_1', 'PT5_2', 'PT5_3', 'PT5_4', 'PV5']
#plot_batch_ind_conn(batch, includePre=include, includePost=include, saveFig=True)

#include = ['PT5_1', 'PT5_2', 'PT5_3', 'PT5_4', 'PV5']
#plot_batch_ind_conn("v01_batch15") #, includePre=include, includePost=include, saveFig=True)
#plot_batch_ind_conn("v01_batch15", includePre=include, includePost=include, saveFig=True)
#plot_batch_ind_conn("v01_batch16", includePre=include, includePost=include, saveFig=True)


# sim.load(batchdatadir + '/' + batchLabel + '/' + batchLabel + curSim + '.json', instantiate=False)

# fig1 = sim.analysis.plotTraces()
# fig2 = sim.analysis.plotRaster(orderInverse=True)
# fig3 = sim.analysis.plotSpikeHist()
# fig4 = sim.analysis.plotSpikeStats()
# fig5 = sim.analysis.plotConn()
# fig6 = sim.analysis.plotRatePSD()
# fig7 = sim.analysis.plot2Dnet()



# vtraces = batch_analysis.get_vtraces(params, data)
# fig = batch_analysis.plot_relation(**vtraces)

# batch = (batchLabel, params, data)
# batch_analysis.plot_vtraces(batch, timerange=[100, 1000])

# batch_analysis.plot_num_spikes(batchLabel)

plt.show()

