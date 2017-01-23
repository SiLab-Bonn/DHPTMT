import smtplib
import logging
import os.path
from tempfile import mkstemp
from shutil import move
import time
import array
import yaml
import os
import subprocess
import sys
import numpy as np
from struct import unpack, unpack_from, pack
from email.mime.text import MIMEText
import matplotlib.pyplot as pl
import matplotlib as mpl
import numpy as np
from argparse import ArgumentParser
import configparser
import os
import sys
import math
from matplotlib.backends.backend_pdf import PdfPages
import config_utils
import dhp_utils
import matplotlib.ticker as tick



def programFPGA():
    #os.system('source /opt/Xilinx/14.7/LabTools/settings64.sh')
    p = subprocess.Popen(['source /opt/Xilinx/14.7/LabTools/settings64.sh; impact -batch /home/user/git/DHPTMP/Software/program_probecard.cmd'], stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    ret = False
    if 'Programmed successfully' in out:
        ret = True
    return ret

def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    os.close(fh)
    #Remove original file
    os.remove(file_path)
    #Move new file
    move(abs_path, file_path)

def initiate_logger(outputDirectory, testRevision, dhptVersion):
    if not os.path.exists(outputDirectory):
        os.makedirs(outputDirectory)
    
    dhpt = "DHPTX.X"
    if dhptVersion == "1.0":
        dhpt = "DHPT1.0"
    elif dhptVersion == "1.1":
        dhpt = "DHPT1.1"
    elif dhptVersion == "1.2a":
        dhpt = "DHPT1.2a"
    elif dhptVersion == "1.2b":
        dhpt = "DHPT1.2b"
    else: 
        logger.error("DHPT VERSION %s IS UNKNOWN!!", dhpt)
        sys.exit(-1)
        
    dhptID = open("/home/user/NeedleCardTest/Data/" + dhpt + "/dhptID.id", "rw")
    chipID = dhptID.read()

    logging.basicConfig()
    formatter = logging.Formatter("%(levelname)s\t %(message)s")
    rootLogger = logging.getLogger("log")
    '''
    Output to the LogFile
    '''
    fileHandler = logging.FileHandler(os.path.join(outputDirectory, "chip_%s.log"%chipID), 'w', encoding=None, delay="true")
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    rootLogger.addHandler(fileHandler)
   
    '''
    Output to the console
    '''
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(formatter)
    rootLogger.addHandler(consoleHandler)
        
    rootLogger.info("%s\tCHIP ID %s",__name__,chipID)
    replace("/home/user/NeedleCardTest/Data/" + dhpt + "/dhptID.id", chipID, "%d"%(int(chipID)+1))
   
    rootLogger.info("%s\tSOFTWARE REVISION %s - (%s/%s by Leonard Germic, SiLab/Uni Bonn)",__name__,testRevision, time.localtime().tm_year, time.localtime().tm_mon)

def chipID(ID='DHP12B.A00W01'):
    rows = ['A','B','C','D','E','F','G','H','I','J']
    row = ID[-6]
    col = int(ID[-5]+ID[-4])
    wafer = int(ID[-2]+ID[-1])
    print 'r %s, c %s, w %s'%(row,col,wafer) 
    
    lid = list(ID)
    
    if 10 > col:
        lid[-5] = '%02d'%(col+1)[0]
        lid[-4] = '%02d'%(col+1)[1]
    else:
        lid[-5] = str(0)
        lid[-4] = str(0)
        if (rows.index(row) > len(rows)-2): 
            lid[-6] = rows.index(0)
        else:
            lid[-6] = rows(rows.index(row)+1)
            lid[-2] = '%02d'%(wafer+1)[0]
            lid[-1] = str(wafer+1)[1]
            
    return str(lid)
        
    
    
           
def query_dict(nested_dict):
    return [value for key, value in nested_dict.iteritems()]

def get_bitString(Z):
    res = ''
    if isinstance(Z, list):
        for z in Z:
            res += format(z,'#010b')[2:]
    else:
        res = format(Z,'#010b')[2:]
    return res

def generate_dcd_test_data():
    testpattern = np.array([213, 162, 145, 128, 8, 196, 42, 213,
        42, 213, 42, 93, 110, 127, 247, 59, 213,
        42, 213, 127, 128, 127, 128, 127, 127,
        128, 128, 255, 127, 192, 128, 42], dtype=np.uint8)
    
    data = np.zeros(32)
    remapped_testpattern = testpattern.reshape(8,4)[:,::-1].reshape(32)
    data = remapped_testpattern
    for i in range(6):
        data = np.concatenate((data, remapped_testpattern), axis=0)
    
    return data

def generate_test_data(adc=np.zeros((32,8),dtype=np.uint8),dcd_testpattern=False, shift_testpattern=0): 
    logging.info("%s\tGenerate testdata",__name__)
    if not dcd_testpattern:
        if adc.shape != (32,8):
            logging.error("%s\tShape of adc must be (32,8)",__name__)
            sys.exit(1)
    else:
        adc = np.zeros((32,8),dtype=np.uint8)
        #adc[0:31,:]=np.uint8(255)
        if shift_testpattern >= 0:
            logging.info("%s\tTestpattern shifted by %d dcd_clk cycles",__name__,shift_testpattern)
            adc[(0+shift_testpattern)%32,:]=np.uint8(-127) # 1000 0001
            for i in range(29):
                adc[(2+i+shift_testpattern)%32,:]=np.uint8(127) # 0111 1111
        else:
            adc[(0+32-shift_testpattern)%32,:]=np.uint8(-127) # 1000 0001
            for i in range(29):
                adc[(32+2+i-shift_testpattern)%32,:]=np.uint8(127) # 0111 1111
    #logging.info("%s\tTestdata:\n",__name__,adc)        
    '''
    TESTPATTERN
    
    -------- bit ------------
    |    ADC0    1000 0001        dcd_clk_tick 1
    |    ADC1    0000 0000        dcd_clk_tick 2
    |    ADC2    0111 1111        dcd_clk_tick 3
    a    ADC3    0111 1111
    d    ADC4    0111 1111
    c    .        .
    |    .        .
    |    .        .
    |    ADC30   0111 1111        dcd_clk_tick 30
    |    ADC31   0000 0000        dcd_clk_tick 31
    '''
    seq = []
    for byte4_group in range(8):
        '''
        As input we receive 8x32 bytes correspinding to 8bus and 32ADC values (1 byte each)
        We take now every 32ADC values and split them into groups of 4 bytes, i.e. 8x 4bytes
        First bit schould be the earliest
        
        DOX_32[:,bus] -> ADC[adc,bit]
        e.g.. 
        ADC0, ADC1, ADC2, ADC3 => 
        DOX_32[:,bus]   =  {0,1,2,3,4,5,6,7,...,24,25,26,27,28,29,30,31}
                        => {(3,2,1,0),(7,6,5,4),...,(27,26,25,24),(31,30,29,28)}
                        
        output from FPGA DOX =  (0,4, 8,12,16,20,24,28)     dcd_clk_tick 1   
                                (1,5, 9,13,17,21,25,29)     dcd_clk_tick 2
                                (2,6,10,14,18,22,26,30)     dcd_clk_tick 3
                                (3,7,11,15,19,23,27,31)     dcd_clk_tick 4     
        '''                     
        
        DOX_32 = np.zeros((32,8),dtype=str)
        DOX_32_str = ""
        word = []
        for bus in range(8):
            for bit in range(32):
                DOX_32[bit,bus] = get_bitString(adc[byte4_group*4+(3-bit%4),bus])[int(bit/4)]

            #Generate a bitstring
            for v in DOX_32[:,bus]:
                DOX_32_str += v
            
        #print DOX_32_str
        '''
        encode the 32 bit words in 4bytes 
        DOX_4bytes[:bus] = (byte3,byte2,byte1,byte0)
        '''
        DOX_4bytes = np.zeros((4,8),dtype=np.uint8)
        for bus in range(8):
            for B in range(4):
                DOX_4bytes[B,bus] = np.uint8(int(DOX_32_str[B*8:(B+1)*8],2))
                #word += np.uint8(int(DOX_32_str[B*8:(B+1)*8],2))
        #print DOX_4bytes[:,0]
        for bus in range(8):
            word += [DOX_4bytes[i,bus] for i in range(4)]
        seq += word         
    #print seq, len(seq)
    
    return seq

def import_test_data(fname):
    f = open(fname)
    ld = []
    for lines in f:
        if lines != "\n":
            ld += lines.split(",")[:len(lines)-1]
    ld1 = []
    for s in ld:
        if "\n" in s:
            ld1.append(int(s[:len(lines)-3]))
        else:
            ld1.append(int(s))
    #print ld1
    out = array.array('B',ld1) 
    return out
 
def send_to_Mr_Cookie(failedChipNumber):
    print "Sending email"
    server = smtplib.SMTP()
    server.connect('smtp.uni-bonn.de:587')
    server.ehlo()
    server.starttls()
    
    logname = "germic@physik.uni-bonn.de"
    logpwd = "!%MO71hj"
    server.login(logname, logpwd)
  
    receiver = "hemperek@physik.uni-bonn.de"
    
    message = MIMEText("Tomek! You owe me %s cookies!!!"%failedChipNumber)
    message['Subject'] = 'automatic generated report'
    message['From'] = logname
    message['To'] = receiver
    
    try:
        server.sendmail(logname, logname, message.as_string())         
        print "Successfully sent email"
        server.quit()
    except smtplib.SMTPException:
        print "Error: unable to send email"

def updatePortInYaml(filename):
    logging.info("%s\tUpdating config file",__name__)
    currActivePort = subprocess.Popen('ls /dev/ttyUSB*', stdout=subprocess.PIPE, shell=True)
    ports = currActivePort.stdout.read().split()

    stream = open(filename,'r')
    dictObj = yaml.load(stream)
    dictObj['transfer_layer'][0]['init']['port'] = ports[-1]
    
    with open(filename, 'w') as yaml_file:
        yaml_file.write(yaml.dump(dictObj, default_flow_style=True))
        
def printProgress(it, tot, prefix='Progress:', suffix='Complete', decimals=0, barLen=50):
    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100*(it/float(tot)))
    filledLen = int(round(barLen*it/float(tot)))
    bar = '|' * filledLen + '-' * (barLen-filledLen)
    sys.stdout.write('\r %s |%s| %s%s %s' % (prefix,bar,percent, '%', suffix)),
    if it==tot:
        sys.stdout.write('\n')
    sys.stdout.flush()
                  
 
################## plot Bias vs Biasd #############################
def plot_cml(pdf, data, bias, biasd):

    # label biasd axis correctly
    def tick_biasd(x, y):
        # we do not want wrong and strange values for negative values
        if x<0 or x>(len(biasd)-1):
            return
        else:
            return '%d' % (biasd[int(x)])

    # label bias axis correctly
    def tick_bias(x, y):
        if x<0 or x>(len(bias)-1):
            return
        else:
            return '%d' % (bias[int(x)])

    figure, (ax1, ax2) = pl.subplots(2, 2, sharex=False, sharey=False, figsize = (11.69, 8.27))
    figure.suptitle("IV curve VDD", fontsize=14)
    axes=ax1[0]
    axes.set_xlim([0,255])
    axes.set_xlabel("Bias DAC")
    axes.set_ylabel("IVDD [mA]")
    off = np.min(data[0,0])
    for bd in biasd:
        d = []
        for v in data[:,bd]:
            if v!=0:
                d.append(v)
        axes.plot(bias, d-off, linestyle='-', marker='x', markersize=1)
    axes.plot([0,255], [np.min(data[255,0])-off,np.min(data[255,0])-off], linestyle='-', marker='', linewidth=2)
    
    axes=ax1[1]
    axes.set_xlim([0,255])
    axes.set_xlabel("Biasd DAC")
    axes.set_ylabel("IVDD [mA]")
    for b in bias:
        d = []
        for v in data[b,:]:
            if v!=0:
                d.append(v)
        axes.plot(biasd, d-off, linestyle='-', marker='x', markersize=1)
    axes.plot([0,255], [np.min(data[0,255])-off,np.min(data[0,255])-off], linestyle='-', marker='', linewidth=2)
    
        
    axes=ax2[0]
    axes.set_xlabel("Bias DAC")
    axes.set_ylabel("Biasd DAC")
    #axes.imshow(data[:,:,int(i)-1], aspect='auto',  cmap=pl.cm.RdYlGn, interpolation='nearest', vmin=0, vmax=vmax)#,  extent=[bias_start, bias_stop, biasd_start, biasd_stop])
    cmap = mpl.cm.get_cmap("jet")
    #
    vmax = np.max(data)
    data = data.astype(int).astype(float)
    data[data==0]=np.nan
    axes.imshow(np.transpose(data[:,:])-off, aspect='auto',  cmap=cmap,interpolation='None',\
            vmin=0, vmax=vmax-off,  origin='lower')
    axes.tick_params(axis='both', which='major', labelsize=10)
    # this is stupid! it sets labels at every step
    # if you have a larger range you do not see anything!
    #axes.set_xticks(np.ndarray.tolist(np.arange(len(biasd))))
    #axes.set_xticklabels(biasd)
    #axes.set_yticks(np.ndarray.tolist(np.arange(len(bias))))
    #axes.set_yticklabels(bias)
    # we take the labels which there are and replace them smartly
    axes.xaxis.set_major_formatter(tick.FuncFormatter(tick_bias))
    axes.yaxis.set_major_formatter(tick.FuncFormatter(tick_biasd))
    #xlabel="Bias"
    #ylabel="Bias d"
    #figure.text(0.05, 0.05 + 0.9/2, ylabel, ha="left", va="center", rotation="vertical", fontsize=12)
    #figure.text(0.05 + (0.92-0.05)/2, 0.01, xlabel, ha="center", va="bottom", fontsize=12)
    # Colorbar
    axes.contour(data, [0,20], linewidths=2, cmap=cmap)    
    cb_ax = figure.add_axes([0.91, 0.05, 0.02, 0.9])
    norm = mpl.colors.Normalize(vmin=0 , vmax=vmax-off )
    cb = mpl.colorbar.ColorbarBase(cb_ax, cmap=cmap, norm=norm, orientation='vertical')
    cb.set_label("VDD current [mA]")
    # save to pdf
    
    pdf.savefig(figure)
    

################## plot Bias vs Biasd #############################
def plot_bias_biasd(pdf, path, bias, biasd, biasdly, vmax=31):
    
    import matplotlib.pyplot as pl
    import matplotlib as mpl
    import numpy as np
    from argparse import ArgumentParser
    import configparser
    import os
    import sys
    import math
    from matplotlib.backends.backend_pdf import PdfPages
    import config_utils
    import dhp_utils
    import matplotlib.ticker as tick
            
    # label biasd axis correctly
    def tick_biasd(x, y):
        # we do not want wrong and strange values for negative values
        if x<0 or x>(len(biasd)-1):
            return
        else:
            return '%d' % (biasd[int(x)])

    # label bias axis correctly
    def tick_bias(x, y):
        if x<0 or x>(len(bias)-1):
            return
        else:
            return '%d' % (bias[int(x)])

    def dhp_bug(bias_delay_item):
        """
        dhp manual:
        [3] minimum (is non zero due to propagation delay).
        [1] larger than [3]
        [2] larger than [1]
        [0] maximum
        """
        dict = {0:3, 1:2, 2:1, 3:0}
        return dict[bias_delay_item]

    figure, axs = pl.subplots(2, 2, sharex=False, sharey=False, figsize = (11.69, 8.27))
    figure.suptitle("Aurora link scan", fontsize=14)
    
    for bd in biasdly:
        filename = "pll_cml_dly_sel%d.npz" % bd
        print 'plot', filename
        loaded_data = np.load(os.path.join(path, filename))
        data=loaded_data['data']
        tmp = np.zeros( (len(bias),len(biasd),2,4) ) 
        for j in range(len(biasd)):
            tmp[:,j,:,:] = data[:,biasd[0]+j*(biasd[1]-biasd[0]),:,:]    
       
        row = int(bd/2)
        column = int(bd%2)
        axes=axs[row,column]
       
        cmap = mpl.cm.get_cmap("jet")
        axes.set_title("dly %d"%bd, fontsize=10)
        axes.imshow(get_rid_of_isolated_spots_in_data(tmp[:,:,1,0]*tmp[:,:,0,0])[1], aspect='auto',  cmap=cmap,interpolation='none',\
                vmin=0, vmax=vmax,  origin='lower')
       
        axes.tick_params(axis='both', which='major', labelsize=10)
      
        axes.xaxis.set_major_formatter(tick.FuncFormatter(tick_biasd))
        axes.yaxis.set_major_formatter(tick.FuncFormatter(tick_bias))
        xlabel="Bias d"
        ylabel="Bias"
        figure.text(0.05, 0.05 + 0.9/2, ylabel, ha="left", va="center", rotation="vertical", fontsize=12)
        figure.text(0.05 + (0.92-0.05)/2, 0.01, xlabel, ha="center", va="bottom", fontsize=12)
        # Colorbar
        cb_ax = figure.add_axes([0.91, 0.05, 0.02, 0.9])
        norm = mpl.colors.Normalize(vmin=0 , vmax=vmax )
        #axes.contour(get_rid_of_isolated_spots_in_data(tmp[:,:,0,0])[0]*get_rid_of_isolated_spots_in_data(tmp[:,:,1,0])[1], [30], linewidths=2, cmap=cmap, norm=norm)
        #axes.contour(get_rid_of_isolated_spots_in_data(tmp[:,:,0,0])[1], [0,1], linewidths=3, colors=('red'))#, cmap='gray', norm=norm)
        cb = mpl.colorbar.ColorbarBase(cb_ax, cmap=cmap, norm=norm, orientation='vertical')
        cb.set_label("Eye Diagram")
    # save to pdf
    pdf.savefig(figure)
    
def get_rid_of_isolated_spots_in_data(data):
    idxs = np.where(data==0)
    masked = data
    interpolated_data = data
    for idx in idxs:
        if not len(idx)==0:
            if idx[0]>0 and (masked.shape[0]-2)>idx[0] and idx[1]>0 and (masked.shape[1]-2)>idx[1]:
                if ((0==masked[idx[0]+1,idx[1]-1]) and (0==masked[idx[0]+1,idx[1]+1]) and (0==masked[idx[0]-1,idx[1]-1]) and (0==masked[idx[0]-1,idx[1]+1])):
                    masked[idx] = np.nan
                    interpolated_data[idx] = 0.25*(interpolated_data[idx[0]+1,idx[1]-1] + interpolated_data[idx[0]-1,idx[1]+1] + interpolated_data[idx[0]-1,idx[1]-1] + interpolated_data[idx[0]+1,idx[1]+1])
    return masked, interpolated_data
    
    
def plot_shmoo(pdf,data, testdata, volt, freq):  
    figure, axs = pl.subplots(2, 2, sharex=False, sharey=False, figsize = (11.69, 8.27))
    pl.subplots_adjust(wspace=0.5)
    figure.suptitle("IV curve VDD", fontsize=14)
    reducedVolt = range(0,len(volt),4)
    
    axes=axs[0,0]
    xlabel = "frequency"
    ylabel = "Voltage"
    cmap = mpl.cm.get_cmap("jet")
    tmp = np.transpose(data[:,:,1])#*data[:,:,0])
    tmp[tmp==0]=np.nan
    axes.imshow(tmp, aspect='auto',  cmap=cmap,interpolation='None',\
            vmin=np.min(tmp), vmax=np.max(tmp),  origin='lower')
    axes.tick_params(axis='both', which='major', labelsize=10)
    axes.set_xticks(range(len(freq)))
    axes.set_yticks(reducedVolt)
    axes.set_xticklabels(freq)
    axes.set_yticklabels([volt[i] for i in reducedVolt])
    figure.text(0.05, 0.05 + 0.9/2, ylabel, ha="left", va="center", rotation="vertical", fontsize=12)
    figure.text(0.05 + (0.92-0.05)/2, 0.01, xlabel, ha="center", va="bottom", fontsize=12)
    # Colorbar
    axes.contour(tmp, [0.9,0.99,0.999], linewidths=2, colors='white')    
    cb_ax = figure.add_axes([0.45, 0.55, 0.02, 0.35])
    norm = mpl.colors.Normalize(vmin=np.min(tmp), vmax=np.max(tmp) )
    cb = mpl.colorbar.ColorbarBase(cb_ax, cmap=cmap, norm=norm, orientation='vertical')
    cb.set_label("rel. #of correct data")

    axes=axs[0,1]
    xlabel = "frequency"
    ylabel = "Voltage"
    cmap1 = mpl.cm.get_cmap("jet")
    tmp = np.transpose(data[:,:,2])
    axes.imshow(tmp, aspect='auto',  cmap=cmap1,interpolation='None',\
            vmin=np.min(tmp), vmax=np.max(tmp),  origin='lower')
    axes.tick_params(axis='both', which='major', labelsize=10)
    axes.set_xticks(range(len(freq)))
    axes.set_yticks(reducedVolt)
    axes.set_xticklabels(freq)
    axes.set_yticklabels([volt[i] for i in reducedVolt])
    #figure.text(0.05, 0.05 + 0.9/2, ylabel, ha="left", va="center", rotation="vertical", fontsize=12)
    #figure.text(0.05 + (0.92-0.05)/2, 0.01, xlabel, ha="center", va="bottom", fontsize=12)
    # Colorbar
    #axes.contour(data, [0,20], linewidths=2, cmap=cmap)    
    cb_ax1 = figure.add_axes([0.91, 0.55, 0.02, 0.35])
    norm1 = mpl.colors.Normalize(vmin=np.min(tmp), vmax=np.max(tmp) )
    cb1 = mpl.colorbar.ColorbarBase(cb_ax1, cmap=cmap1, norm=norm1, orientation='vertical')
    cb1.set_label("IVDD+IVDDCML [mA]")
    
    axes=axs[1,0]
    xlabel = "frequency"
    ylabel = "Voltage"
    cmap3 = mpl.cm.get_cmap("jet")
    tmp = np.transpose(data[:,:,3]*200.0/31.0)
    axes.imshow(tmp, aspect='auto',  cmap=cmap1,interpolation='None',\
            vmin=np.min(tmp), vmax=np.max(tmp),  origin='lower')
    axes.tick_params(axis='both', which='major', labelsize=10)
    axes.set_xticks(range(len(freq)))
    axes.set_yticks(reducedVolt)
    axes.set_xticklabels(freq)
    axes.set_yticklabels([volt[i] for i in reducedVolt])
    #figure.text(0.05, 0.05 + 0.9/2, ylabel, ha="left", va="center", rotation="vertical", fontsize=12)
    #figure.text(0.05 + (0.92-0.05)/2, 0.01, xlabel, ha="center", va="bottom", fontsize=12)
    # Colorbar
    axes.contour(tmp, [150], linewidths=5, colors='white')    
    cb_ax3 = figure.add_axes([0.45, 0.1, 0.02, 0.35])
    norm3 = mpl.colors.Normalize(vmin=np.min(tmp), vmax=np.max(tmp) )
    cb3 = mpl.colorbar.ColorbarBase(cb_ax3, cmap=cmap3, norm=norm3, orientation='vertical')
    cb3.set_label("eye [mV]")
    
    axes=axs[1,1]
    axes.set_title('rnd test pattern')
    xlabel = "Column"
    ylabel = "row"
    tmp = np.transpose(data[:,:,4])#testdata
    axes.imshow(tmp, aspect='auto',  cmap=cmap1,interpolation='None',\
            vmin=np.min(tmp), vmax=np.max(tmp),  origin='lower')
    
    pdf.savefig(figure)
    
def readFile(filename,asicpair,frames=10):
    from pyDepfetReader.file_reader import  FileReader
    reader=FileReader(-1,1,'H1032')
    #print filename
    isgood = True
    if False==reader.open(filename):
        print "File not found: ",filename
        raise IOError
    nr_of_frames=0
    frameContainer=np.zeros((256*4,64,1),dtype=np.uint16)
    
    for data, raw in reader:
        if raw:
            #print frameContainer.shape, data.shape
            if len(frameContainer.shape) == 3:
                frameContainer = np.concatenate((frameContainer,data[...,np.newaxis]), axis=2)
            elif len(frameContainer.shape) == 2:
                frameContainer = np.concatenate((frameContainer[...,np.newaxis],data[...,np.newaxis]), axis=2)
            nr_of_frames+=1
        if nr_of_frames==frames:
            break
    if nr_of_frames==0:
        #print "No events in file",filename
        isgood = False
        #raise IOError
    return frameContainer, isgood
        
        
