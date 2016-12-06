import smtplib
import logging
import os.path
from tempfile import mkstemp
from shutil import move
import time
import array
import yaml
import subprocess

import sys
import numpy as np
from struct import unpack, unpack_from, pack
from email.mime.text import MIMEText
from theano.compile.io import Out
from tornado.process import Subprocess

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

def initiate_logger(outputDirectory, testRevision, dhptVersion ,write2file=False):
    if not os.path.exists(outputDirectory):
        os.makedirs(outputDirectory)
    
    dhpt = "DHPTX.X"
    if dhptVersion == 1.0:
        dhpt = "DHPT1.0"
    elif dhptVersion == 1.1:
        dhpt = "DHPT1.1"
    else: 
        logging.error("DHPT VERSION %s IS UNKNOWN!!", dhpt)

    logger = logging.getLogger("DHPT Probe software")
    logger.setLevel(logging.DEBUG)
    
    dhptID = open("/home/user/NeedleCardTest/Data/" + dhpt + "/dhptID.id", "rw")
    chipID = dhptID.read()
    logging.info("SOFTWARE REVISION %s - (%s/%s by Leonard Germic, SiLab/Uni Bonn)"%(testRevision, time.localtime().tm_year, time.localtime().tm_mon))
    
    '''
    Output to the console
    '''
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s\t %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    '''
    Output to the LogFile
    '''
    if write2file:
        handler = logging.FileHandler(os.path.join(outputDirectory, "chip_%s.log"%chipID), 'w', encoding=None, delay="true")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        logger.info("CHIP ID %s",chipID)
        replace("/home/user/NeedleCardTest/Data/dhptID.id", chipID, "%d"%(int(chipID)+1))
        
    return logger
    
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
    #print currActivePort.stdout.read()
    
    stream = open(filename,'r')
    dictObj = yaml.load(stream)
    tmp = currActivePort.stdout.read()
    if "\n" in tmp:
        tmp = tmp[:-1]
    dictObj['transfer_layer'][0]['init']['port'] = tmp
    
    with open(filename, 'w') as yaml_file:
        yaml_file.write(yaml.dump(dictObj, default_flow_style=True))
    
