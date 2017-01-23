from epics import get_pv
from slowcontrol import *
from Probecard import PROBECARD
#from dhh import mapping
#from pyDepfetReader.file_reader import FileReader
from misc import initiate_logger, printProgress, updatePortInYaml, plot_bias_biasd, plot_cml, plot_shmoo, readFile
from basil.dut import Dut
from time import sleep
from upload_utils import upload_frame_data 
import numpy as np
import daq
import dhp_utils
import os
from epics_utils import pvname
from collections import OrderedDict



class SlowControl(object):
    def __init__(self, dhePrefix="PXD:H1031"):
         self.dhptRegister = JTAG_REGS()
         self.dhePrefix    = dhePrefix
         
    def turn_all_regs_on(cycles=10):
        nested_dicts = ["dcd_rx_sdly","offset_dcd_dly","mem_errors","offset_mem_errors","seq_mem_errors"]
        result = 0
        start = time.time()
        
        excludedRegs = ["pll_out_sel", "tdo_tx_set06","tdo_tx_set12","tdo_tx_set30","tdo_sdly","IDAC_PLL_I50U","IDAC_PLL_ICP","IDAC_PLL_IVCO"]
        excludedBlocks = ["CORE READBACK"]
        
        
        for i in range(cycles):
            logging.info("Iteration number %d of %d"%(i,cycles))
            #Check with all ones
            for key in self.dhptRegister.JTAG_REGISTERS:
                if key not in excludedBlocks:
                    logging.info("Now in BLOCK %s"%key)
                    for pvname in self.dhptRegister.JTAG_REGISTERS[key]['pv']:
                        pv = jtag_reg[key]['pv'][pvname]    
                        if pvname in nested_dicts:
                            for v in query_dict(pv):
                                if v not in excludedRegs and v.pvSet.connected:
                                    max_val = pow(2,v.size)-1 
                                    v.set_value(max_val) 
                        else:   
                            if pvname not in excludedRegs and pv.pvSet.connected:
                                max_val = pow(2,pv.size)-1 
                                pv.set_value(max_val)
                            else:
                                pass
          
            self.dhptRegister.JTAG_REGISTERS['GLOBAL']['dispatch'].set_value()
            self.dhptRegister.JTAG_REGISTERS['CORE']['dispatch'].set_value()
            self.dhptRegister.JTAG_REGISTERS['OUT CONFIGURE']['dispatch'].set_value()
            time.sleep(0.5) 
            self.dhptRegister.JTAG_REGISTERS['GLOBAL']['dispatch'].get_value()
            self.dhptRegister.JTAG_REGISTERS['CORE']['dispatch'].get_value()
            self.dhptRegister.JTAG_REGISTERS['OUT CONFIGURE']['dispatch'].get_value()
             
            for key in self.dhptRegister.JTAG_REGISTERS:
                if key not in excludedBlocks:
                    logging.info("Now in BLOCK %s"%key)
                    for pvname in self.dhptRegister.JTAG_REGISTERS[key]['pv']:
                        pv = self.dhptRegister.JTAG_REGISTERS[key]['pv'][pvname]
                        if pvname in nested_dicts:
                            for v in query_dict(pv):
                                if v not in excludedRegs and v.pvSet.connected:
                                    max_val = pow(2,v.size)-1 
                                    result = result + abs(max_val - v.pvGet.get()) 
                        else:   
                            if pvname not in excludedRegs and pv.pvSet.connected:
                                max_val = pow(2,pv.size)-1 
                                result = result + abs(max_val - pv.pvGet.get())
                                #logger.info("Set max value %d"%max_val)
                            else:
                                pass         
                                    
            #Chech with all zeros
            for key in self.dhptRegister.JTAG_REGISTERS:
                if key not in excludedBlocks:
                    logging.info("Now in dict %s"%key)
                    for pvname in self.dhptRegister.JTAG_REGISTERS[key]['pv']:
                        pv = self.dhptRegister.JTAG_REGISTERS[key]['pv'][pvname]
                        if pvname in nested_dicts:
                            for v in query_dict(pv):
                                if v not in excludedRegs and v.pvSet.connected:
                                    v.set_value(0) 
                        else:   
                            if pvname not in excludedRegs and pv.pvSet.connected:
                                pv.set_value(0)
                            else:
                                pass
          
            self.dhptRegister.JTAG_REGISTERS['GLOBAL']['dispatch'].set_value()
            self.dhptRegister.JTAG_REGISTERS['CORE']['dispatch'].set_value()
            self.dhptRegister.JTAG_REGISTERS['OUT CONFIGURE']['dispatch'].set_value()
            time.sleep(0.5) 
            self.dhptRegister.JTAG_REGISTERS['GLOBAL']['dispatch'].get_value()
            self.dhptRegister.JTAG_REGISTERS['CORE']['dispatch'].get_value()
            self.dhptRegister.JTAG_REGISTERS['OUT CONFIGURE']['dispatch'].get_value()
       
            for key in self.dhptRegister.JTAG_REGISTERS:
                if key not in excludedBlocks:
                    logging.info("Now in dict %s"%key)
                    for pvname in self.dhptRegister.JTAG_REGISTERS[key]['pv']:
                        pv = self.dhptRegister.JTAG_REGISTERS[key]['pv'][pvname]
                        if pvname in nested_dicts:
                            for v in query_dict(pv):
                                if v not in excludedRegs and v.pvGet.connected:
                                    logging.info("Checking pv %s"%pvname)
                                    result = result + v.pvGet.get()
                                    #logger.info("Set max value %d"%max_val)
                        else:   
                            if pvname not in excludedRegs and pv.pvGet.connected:
                                logging.info("Checking pv %s"%pvname)
                                max_val = pow(2,pv.size)-1 
                                result = result + pv.pvGet.get()
                                #logger.info("Set max value %d"%max_val)
                            else:
                                pass                             
        stop =time.time()                    
        return result, stop-start
         
         
         
         
    def read_dhpt_data_via_hs(self, filename, numberOfFrames = 100, lastRow = 256, firstRow = 0):
        from dhh import daq
        self.dhptRegister.JTAG_REGISTERS["CORE"]["pv"]["last_row"].set_value(lastRow)
        self.dhptRegister.JTAG_REGISTERS["CORE"]["dispatch"].set_value()
        daq.record_memorydump(1, numberOfFrames, self.dhePrefix, filename)
    
    def read_dhpt_data_via_jtag(self, filename, numberOfFiles = 5, lastRow = 256, firstRow = 0):
        from jtagmemoryreader import JTagRawReader
        reader = JTagRawReader(dhpPrefix, last_row, numberOfFiles) 
        reader.readMemory()
        frames = reader.getCurrentFrames()
        np.save(filename, frames)
        
    def ped_error():
        self.dhptRegister.JTAG_REGISTERS["CORE READBACK"]["dispatch"].get_value()
        memErrs = [self.dhptRegister.JTAG_REGISTERS["CORE READBACK"]["pv"]["mem_errors"]["NUM_%s"%k].get_value() for k in range(32)]
        doubleErrs = []
        singleErrs = []
        
        for k in range(len(memErrs)):
            singleErrs.append([k,memErrs[k] & 0x1f])         #5 bit for single bit errors
            doubleErrs.append([k,(memErrs[k] & 0xe0) >> 5])  #3 bit for double bit errors
    
        return singleErrs, doubleErrs

    def offset_error():
        self.dhptRegister.JTAG_REGISTERS["CORE READBACK"]["reg"].pvGet.get()
        memErrs = [self.dhptRegister.JTAG_REGISTERS["CORE READBACK"]["pv"]["offset_mem_errors"]["NUM_%s"%k].pvGet.get() for k in range(4)]
        doubleErrs = []
        singleErrs = []
        
        for k in range(len(memErrs)):
            singleErrs.append([k,memErrs[k] & 0x1f])         #5 bit for single bit errors
            doubleErrs.append([k,(memErrs[k] & 0xe0) >> 5])  #3 bit for double bit errors
    
        return singleErrs, doubleErrs
    
    def sw_seq_error():
        memErrs = [self.dhptRegister.JTAG_REGISTERS["CORE READBACK"]["reg"]["seq_mem_errors"]["NUM_%s"%k].read() for k in range(2)]
        doubleErrs = []
        singleErrs = []
        
        for k in range(len(memErrs)):
            singleErrs.append([k,memErrs[k] & 0x1f])         #5 bit for single bit errors
            doubleErrs.append([k,(memErrs[k] & 0xe0) >> 5])  #3 bit for double bit errors
    
        return singleErrs, doubleErrs

    def fill_switcher_memory(self, data, start_addr):
        mem_reg["SWITCHER"]["pv"]["addr"].set_value(start_addr)
        time.sleep(0.05)    
        for addr_id in range(data.shape[1]):
            time.sleep(0.05)
            mem_reg["SWITCHER"]["pv"]["mem0"].set_value(data[0, start_addr])
            mem_reg["SWITCHER"]["pv"]["mem1"].set_value(data[1, start_addr])
            mem_reg["SWITCHER"]["pv"]["mem2"].set_value(data[2, start_addr])
            mem_reg["SWITCHER"]["pv"]["mem3"].set_value(data[3, start_addr])
            time.sleep(0.05)
            mem_reg["SWITCHER"]["dispatch"].set_value()
            
    def fill_offset_memory(self, data):
        mem_reg["SWITCHER"]["pv"]["addr"].set_value()
        time.sleep(0.05)    
        for addr_id in range(data.shape[1]):
            time.sleep(0.05)
            mem_reg["SWITCHER"]["pv"]["mem0"].set_value(data[0, start_addr])
            mem_reg["SWITCHER"]["pv"]["mem1"].set_value(data[1, start_addr])
            mem_reg["SWITCHER"]["pv"]["mem2"].set_value(data[2, start_addr])
            mem_reg["SWITCHER"]["pv"]["mem3"].set_value(data[3, start_addr])
            time.sleep(0.05)
            mem_reg["SWITCHER"]["dispatch"].set_value()


class DHPTMP(PROBECARD):
    def __init__(self, config, logFileDir, softwareVersion, dhptVersion):
        self.fileDir    = logFileDir
        self.psu1       = Dut("dut1_ttiql335tp_pyserial.yaml")
        self.psu2       = Dut("dut2_ttiql335tp_pyserial.yaml")

        self.vdd = 0.0  
        self.dvdd = 0.0
        self.parasiticResistanceVDD = 5.0/12 + 0.1 #Needle and bumb connection compensation
        self.parasiticResistanceDVDD = 5.0/6 + 0.2 #Needle and bumb connection compensation
        self.parasiticResistanceDHE = 0.1 #Needle and bumb connection compensation
        
        
        self.sc         = SlowControl()
  
        initiate_logger(logFileDir, softwareVersion, dhptVersion)
        self.psu2.init()
        sleep(0.5)
        self.psu1.init()
        updatePortInYaml(config)
        PROBECARD.__init__(self, config)  
    
    def shut_down_system(self):
        self.io_disable_all()
        self.disable_voltages()
    
    def init_voltages(self):
        #VDD
        self.psu2["PowerSupply2"].set_ocp(0.24, channel=1)
        self.psu2["PowerSupply2"].set_current_limit(0.22, channel=1) 
        self.psu2["PowerSupply2"].set_ovp(1.6, channel=1)
        #DVDD
        self.psu2["PowerSupply2"].set_ocp(0.1, channel=2)
        self.psu2["PowerSupply2"].set_current_limit(0.08, channel=2) 
        self.psu2["PowerSupply2"].set_ovp(2.5, channel=2)   
        #DHE
        self.psu1["PowerSupply1"].set_ocp(2.8, channel=1)
        self.psu1["PowerSupply1"].set_current_limit(2.6, channel=1) 
        self.psu1["PowerSupply1"].set_ovp(6.0, channel=1)   
        #VCC
        self.psu1["PowerSupply1"].set_ocp(0.5, channel=2)
        self.psu1["PowerSupply1"].set_current_limit(0.3, channel=2) 
        self.psu1["PowerSupply1"].set_ovp(3.6, channel=2)               
        
        self.set_DHE_voltage(on=True)
        sleep(0.5)
        self.set_DVDD_voltage(on=True)
        sleep(0.5)
        self.set_VDD_voltage(on=True)
        sleep(0.5)
        self.set_VCC_voltage(on=True)
        
        #self.enable_voltages()
        cnt = 0
        while not self.is_DHE_on():
            time.sleep(0.5)
            printProgress(cnt,10)
            cnt = cnt + 1
        logging.info("%s\tDHE is ready!", __name__)
        self.compensate_dhe_drop()
        sleep(0.5)
        logging.info("%s\tVCC on? %s", __name__,self.is_VCC_on())
        logging.info("%s\tdut connected? %s", __name__,self.is_dut_connected())
        logging.info("%s\tInit successul",__name__)
        if self.is_VCC_on() and self.is_dut_connected():
            self.compensate_vdrop()
            return True
        else:
            return False
    
    def compensate_vdd_drop(self, vdd=1.2):
        cur_ivdd = 1
        changed_ivdd = 0
        while not (0.001 > abs(changed_ivdd - cur_ivdd)):
            cur_ivdd = self.get_VDD_current() 
            self.set_VDD_voltage(v=vdd+float(cur_ivdd*self.parasiticResistanceVDD), on=True)
            changed_ivdd = self.get_VDD_current()
        
        v = dict({"IVDD" : changed_ivdd})        
        return v
    
    def compensate_dhe_drop(self, dhe=5.5):
        cur_idhe = 1
        changed_idhe = 0
        while not (0.001 > abs(changed_idhe - cur_idhe)):
            cur_idhe = self.get_DHE_current() 
            self.set_DHE_voltage(v=dhe+float(cur_idhe*self.parasiticResistanceDHE), on=True)
            changed_idhe = self.get_DHE_current()
        
        v = dict({"IDHE" : changed_idhe})        
        return v
    
    def compensate_vdrop(self, vdd=1.2, dvdd=1.8):
        cur_ivdd = 1
        changed_ivdd = 0
        changed_idvdd = 0
        cur_idvdd = 1
        while not (0.001 > abs(changed_ivdd - cur_ivdd)):
            cur_ivdd = self.get_VDD_current() 
            self.set_VDD_voltage(v=vdd+float(cur_ivdd*self.parasiticResistanceVDD), on=True)
            changed_ivdd = self.get_VDD_current()
            #print 'IVDD %s\t%s'%(cur_ivdd,changed_ivdd)
            
        while not (0.001 > abs(changed_idvdd - cur_idvdd)):
            cur_idvdd = self.get_DVDD_current() 
            self.set_DVDD_voltage(v=dvdd+float(cur_idvdd*self.parasiticResistanceDVDD), on=True)
            changed_idvdd = self.get_DVDD_current()
            #print 'IDVDD %s\t%s'%(cur_idvdd,changed_idvdd)
        
        v = dict({"IVDD" : changed_ivdd, "IDVDD" : changed_idvdd})        
        return v
    
    def is_dut_connected(self):
        if self.is_VDD_on() and self.is_DVDD_on():
            return True
        else:
            return False
    
    def is_VDD_on(self):
        if self.get_VDD_current() > 0.05:
            return True
        else:
            return False
            
    def is_DVDD_on(self):
        if self.get_DVDD_current() > 0.02:
            return True
        else:
            return False
    
    def is_DHE_on(self):
        if self.get_DHE_current() > 1.8:
            return True
        else:
            return False
    
    def is_VCC_on(self):
        if self.get_VCC_current() > 0.04:
            return True
        else:
            return False
        
    def enable_voltages(self):
        self.psu2["PowerSupply2"].on(channel=1)
        sleep(0.1)
        self.psu2["PowerSupply2"].on(channel=2)
        sleep(0.1)
        self.psu1["PowerSupply1"].on(channel=1)
        sleep(0.1)
        self.psu1["PowerSupply1"].on(channel=2)
        sleep(0.1)
    
    def disable_voltages(self):
        self.psu2["PowerSupply2"].off(channel=1)
        sleep(0.1)
        self.psu2["PowerSupply2"].off(channel=2)
        sleep(0.1)
        self.psu1["PowerSupply1"].off(channel=1)
        sleep(0.1)
        self.psu1["PowerSupply1"].off(channel=2)
            
    def set_VDD_voltage(self, v=1.2, on=False):
        self.vdd = v
        ch = 1      
        self.psu2["PowerSupply2"].set_voltage(self.vdd, channel=ch)
        if on:
            self.psu2["PowerSupply2"].on(channel=ch)
        else:
            self.psu2["PowerSupply2"].off(channel=ch)

    def set_DVDD_voltage(self, v=1.8, on=False):
        self.dvdd= v
        ch = 2               
        self.psu2["PowerSupply2"].set_voltage(self.dvdd, channel=ch)
        if on:
            self.psu2["PowerSupply2"].on(channel=ch)
        else:
            self.psu2["PowerSupply2"].off(channel=ch)

    def set_DHE_voltage(self, v=5.5, on=False):
        val= v
        ch = 1                
        self.psu1["PowerSupply1"].set_voltage(val, channel=ch)
        if on:
            self.psu1["PowerSupply1"].on(channel=ch)
        else:
            self.psu1["PowerSupply1"].off(channel=ch)

    def set_VCC_voltage(self, v=3.3, on=False):
        val= v
        ch = 2   
        self.psu1["PowerSupply1"].set_voltage(val, channel=ch)
        if on:
            self.psu1["PowerSupply1"].on(channel=ch)
        else:
            self.psu1["PowerSupply1"].off(channel=ch)

    def get_VDD_current(self):
        ch=1
        return float(self.psu2['PowerSupply2'].get_current(channel=ch)[0:-3])

    def get_DVDD_current(self):
        ch=2
        return float(self.psu2['PowerSupply2'].get_current(channel=ch)[0:-3])
        
    def get_DHE_current(self):
        ch=1
        return float(self.psu1['PowerSupply1'].get_current(channel=ch)[0:-3])
    
    def get_VCC_current(self):
        ch=2
        return float(self.psu1['PowerSupply1'].get_current(channel=ch)[0:-3])
    
    def get_VDD_voltage(self):
        ch=1
        return float(self.psu2['PowerSupply2'].get_voltage(channel=ch)[0:-3])

    def get_DVDD_voltage(self):
        ch=2
        return float(self.psu2['PowerSupply2'].get_voltage(channel=ch)[0:-3])
        
    def get_DHE_voltage(self):
        ch=1
        return float(self.psu1['PowerSupply1'].get_voltage(channel=ch)[0:-3])
    
    def get_VCC_voltage(self):
        ch=2
        return float(self.psu1['PowerSupply1'].get_voltage(channel=ch)[0:-3])

    def test_power_consumption(self):
        logging.info("%s\tPower; Power Consumption Test",__name__)
        ivdd = self.get_VDD_current()
        idvdd = self.get_DVDD_current()
        
        
        if (ivdd>0.110) and (ivdd<0.150) and (idvdd>0.030) and (idvdd<0.060):
            logging.info("%s\tPower; Passed: VDD %smV(%smA) and DVDD %smV(%smA)",__name__,self.vdd, ivdd, self.dvdd, idvdd)
            return True
        else:
            logging.info("%s\tPower; Failed: VDD %smV(%smA) and DVDD %smV(%smA)",__name__,self.vdd, ivdd, self.dvdd, idvdd)
            return False
            
    def test_jtag(self):
        crst = get_pv(self.sc.dhePrefix+":dhpt_crst:S:set")
        reinJTAG = get_pv(self.sc.dhePrefix+":jtag_reinit_chain:S:set")
        if not get_pv(self.sc.dhePrefix+":jtag_chain_initialized:S:cur").get():
            crst.put(0)
            crst.put(1)
            logging.info("%s\tCRESETB; Reset JTAG registers in DHPT", __name__)
            reinJTAG.put(1)
            logging.info("%s\tReinitalized JTAG chain",__name__)
        
        self.sc.turn_all_regs_on()
        return True
    
    def test_memories(self):
        isPedestalMemoryOK = False
        isOffsetMemoryOK   = False
        isSwitcherMemoryOK = False
        
        '''
        Test Data+Pedestal Memory
        '''
        logging.info("MEM; Pedestal memory test")
        start = time.time()
        
        rnd0 = np.random.randint(0,pow(2,32))
        rnd1 = np.random.randint(0,pow(2,32))
        pattern = [np.uint32(0xaaaaaaaa), np.uint32(0x55555555), rnd0, rnd1]
        
        isErr = False
        cnt   = 0
        
        while not isErr and (cnt<5): 
            cnt = cnt + 1
            singleErrs = []
            doubleErrs = []
            patternErr = 0
           
            singleErrs, doubleErrs = self.sc.ped_error()
         
            for derr in doubleErrs : 
                if derr[1]!=0:
                    isErr = True
            
            for serr in singleErrs : 
                if serr[1]!=0:
                    isErr = True
                    
            if isErr:
                logging.fatal("Bit error detected: in mem block %s", derr[0]) 
            
            for pat in pattern: 
                self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["mem0"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["mem1"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["mem2"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["mem3"].set_value(pat)
                for blk in range(16):
                    #logging.info("MEM; use pattern %x"%pat)
                    #logging.info("Pattern %x"%pat)
                    self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["addr"].set_value(blk << 10)
                    time.sleep(0.05)
                    for addr_id in range(1024):
                        self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["dispatch"].set_value()
                        time.sleep(0.05)
                        
                for blk in range(16):
                    self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["addr"].set_value(blk << 10)
                    time.sleep(0.05)
                    for addr_id in range(1024): 
                        self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["dispatch"].set_value() 
                        time.sleep(0.1)
                        mem0 = np.uint32(self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["mem0"].get_value())
                        mem1 = np.uint32(self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["mem1"].get_value())
                        mem2 = np.uint32(self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["mem2"].get_value())
                        mem3 = np.uint32(self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["mem3"].get_value())
                        time.sleep(0.05)
                        #logging.info(patternErr)
                        if ((mem0 != pat) or (mem1 != pat) or (mem2 != pat) or (mem3 != pat)):
                            patternErr = patternErr + 1 
                            logging.info("Adress %d failure in block %d"%(addr_id, blk))
                            logging.info("Received pattern %x %x %x %x"%(mem0, mem1, mem2, mem3))
                        
        stop = time.time()  
        
        if (patternErr == 0) and not isErr:
            logging.info("Mem; Pedestal memory test passed after %d sec"%(stop-start))
            isPedestalMemoryOK = True
        else:
            logging.warning("Mem; Pedestal memory test failed. Result %d (!= 0)"%patternErr)
           
        '''
        Test Offset Memory
        '''
        logging.info("MEM; Offset memory test")
        start = time.time()
        
        rnd0 = np.random.randint(0,pow(2,32))
        rnd1 = np.random.randint(0,pow(2,32))
        pattern = [np.uint32(0xaaaaaaaa), np.uint32(0x55555555), rnd0, rnd1]
        
        isErr = False
        cnt   = 0
        
        while not isErr and (cnt<5): 
            cnt = cnt + 1
            singleErrs = []
            doubleErrs = []
            patternErr = 0
           
            singleErrs, doubleErrs = sc.offset_error()
         
            for derr in doubleErrs : 
                if derr[1]!=0:
                    isErr = True
            
            for serr in singleErrs : 
                if serr[1]!=0:
                    isErr = True
                    
            if isErr:
                logging.fatal("Bit error detected: in mem block %s", derr[0]) 
            
            for pat in pattern: 
                self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["mem0"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["mem1"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["mem2"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["mem3"].set_value(pat)
                #logging.info("MEM; use pattern %x"%pat)
                #logging.info("Pattern %x"%pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["addr"].set_value()
                time.sleep(0.05)
                for addr_id in range(1024):
                    self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["dispatch"].set_value()
                    time.sleep(0.05)
                    
                self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["addr"].set_value()
                time.sleep(0.05)
                for addr_id in range(1024): 
                    self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["dispatch"].set_value() 
                    time.sleep(0.1)
                    mem0 = np.uint32(self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["mem0"].get_value())
                    mem1 = np.uint32(self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["mem1"].get_value())
                    mem2 = np.uint32(self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["mem2"].get_value())
                    mem3 = np.uint32(self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["mem3"].get_value())
                    time.sleep(0.05)
                    #logging.info(patternErr)
                    if ((mem0 != pat) or (mem1 != pat) or (mem2 != pat) or (mem3 != pat)):
                        patternErr = patternErr + 1 
                        logging.info("Adress %d failure in block %d"%(addr_id, blk))
                        logging.info("Received pattern %x %x %x %x"%(mem0, mem1, mem2, mem3))
                    
        stop = time.time()  
        
        if (patternErr == 0) and not isErr:
            logging.info("Mem; Offset memory test passed after %d sec"%(stop-start))
            isOffsetMemoryOK = True
        else:
            logging.warning("Mem; Offset memory test failed. Result %d (!= 0)"%patternErr)
                
        
        '''
        Test Switcher Memory
        '''
        logging.info("MEM; Switcher memory test")
        start = time.time()
        
        rnd0 = np.random.randint(0,pow(2,32))
        rnd1 = np.random.randint(0,pow(2,32))
        pattern = [np.uint32(0xaaaaaaaa), np.uint32(0x55555555), rnd0, rnd1]
        
        isErr = False
        cnt   = 0
        
        while not isErr and (cnt<5): 
            cnt = cnt + 1
            singleErrs = []
            doubleErrs = []
            patternErr = 0
           
            singleErrs, doubleErrs = sc.switcher_error()
         
            for derr in doubleErrs : 
                if derr[1]!=0:
                    isErr = True
            
            for serr in singleErrs : 
                if serr[1]!=0:
                    isErr = True
                    
            if isErr:
                logging.fatal("Bit error detected: in mem block %s", derr[0]) 
            
            for pat in pattern: 
                self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["mem0"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["mem1"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["mem2"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["mem3"].set_value(pat)
                for blk in range(16):
                    #logging.info("MEM; use pattern %x"%pat)
                    #logging.info("Pattern %x"%pat)
                    self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["addr"].set_value()
                    time.sleep(0.05)
                    for addr_id in range(1024):
                        self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["dispatch"].set_value()
                        time.sleep(0.05)
                        
                for blk in range(16):
                    self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["addr"].set_value()
                    time.sleep(0.05)
                    for addr_id in range(1024): 
                        self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["dispatch"].set_value() 
                        time.sleep(0.1)
                        mem0 = np.uint32(self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["mem0"].get_value())
                        mem1 = np.uint32(self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["mem1"].get_value())
                        mem2 = np.uint32(self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["mem2"].get_value())
                        mem3 = np.uint32(self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["mem3"].get_value())
                        time.sleep(0.05)
                        #logging.info(patternErr)
                        if ((mem0 != pat) or (mem1 != pat) or (mem2 != pat) or (mem3 != pat)):
                            patternErr = patternErr + 1 
                            logging.info("Adress %d failure in block %d"%(addr_id, blk))
                            logging.info("Received pattern %x %x %x %x"%(mem0, mem1, mem2, mem3))
                        
        stop = time.time()  
        
        if (patternErr == 0) and not isErr:
            logging.info("Mem; Offset memory test passed after %d sec"%(stop-start))
            isSwitcherMemoryOK = True
        else:
            logging.warning("Mem; Offset memory test failed. Result %d (!= 0)"%patternErr)
                
                
        return isPedestalMemoryOK and isOffsetMemoryOK and isSwitcherMemoryOK 
    
    #===========================================================================
    # def test_io_streams(self):
    #     isDelayOK    = False
    #     isDCDOK      = False
    #     isOffsetOK   = False
    #     isSwitcherOK = False
    #      
    #     '''
    #     Test DCD Delay scan
    #     '''
    #     logging.info("I/O; DCD-DHPT Delay Test ")
    #     start = time.time()
    #     PROBECARD.send_testpattern_to_dhpt()
    #     os.system("/home/lgermic/.cs-studio/analysis/delays/scan_delays.py")
    #     os.system("/home/lgermic/.cs-studio/analysis/delays/analyze_delays.py")
    #     os.system("/home/lgermic/.cs-studio/analysis/delays/find_optimal_delays.py")
    #     '''
    #     TODO: find_optimal_delays returns if optimal delays are found and optimal delays
    #     '''
    #     optDelays = True
    #     stop = time.time()
    #     
    #     if optDelays:
    #         logging.info("I/O; DCD-DHPT Delay Test passed after %d sec"%(stop-start))
    #         isDelayOK = True
    #     else:
    #         logging.warning("I/O; DCD-DHPT Delay Test failed. No set of delays found.")
    # 
    #     '''
    #     Test DCD Data 
    #     '''
    #     logging.info("I/O; DCD-DHPT Data Test ")
    #     start = time.time()
    #     testpattern = PROBECARD.send_random_pattern_to_dhpt()
    #     filename = self.fileDir+"data"
    #     self.sc.read_dhpt_data_via_hs(filename)
    #     
    #     read = FileReader(-1,1)
    #     read.set_debug_output(False)
    #     if read.open(filename):
    #         print "File not found: ",filename
    #         sys.exit(-1)
    #     data, isRaw, isGood = read.readEvent()
    #     nr_of_frames = 0
    #     wrongbits = 0
    #     while isGood:
    #         nr_of_frames += 1
    #         dataNew = mapping.matrixToDcd(data[:,:,nr_of_frames-1])
    #         wrongbits += plots.calculate_wrong_bits(dataNew, testpattern)
    #         data, isRaw, isGood = read.readEvent()
    #     
    #     isDCDOK = (wrongbits == 0) 
    #     stop = time.time()
    #     
    #     if dcdData:
    #         logging.info("I/O; DCD-DHPT Delay Test passed after %d sec"%(stop-start))
    #         isDCDOK = True
    #     else:
    #         logging.warning("I/O; DCD-DHPT Delay Test failed. No set of delays found.")
    #     
    #     '''
    #     Test Offset Data 
    #     '''
    #     isOffsetOK = True
    #     logging.info("I/O; OFFSET Data Test ")
    #     start = time.time()
    #     data = np.zeros((4,4,512), dtype=np.uint32)
    #     data[0,:,:] = np.array(4*[512*[0xAAAAAAAA]], dtype=np.uint32)    
    #     data[1,:,:] = np.array(4*[512*[0x55555555]], dtype=np.uint32)    
    #     data[2,:,:] = np.random.randint(0,np.power(2,32),(4,512))
    #     data[3,:,:] = np.random.randint(0,np.power(2,32),(4,512))
    #     
    #     self.sc.dhptRegister.JTAG_REGISTERS["CORE"]["pv"]["last_row"].set_value(255)
    #     self.sc.dhptRegister.JTAG_REGISTERS["CORE"]["dispatch"].set_value()    
    # 
    #     self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["offset_en_out"].set_value(1)
    #     self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["dispatch"].set_value()
    # 
    #     for pattern_id in range(4):
    #         self.sc.fill_offset_memory(data[pattern_id])
    #         dataRet = PROBECARD.get_offsetBits()
    #         
    #         wrong_data_row_id = []
    #         if data[i].shape == dataRet.shape:
    #             for row in range(data.shape[1]):
    #                 if (data[id,:,row] != dataRet[:,row]): 
    #                     wrong_data_row_id.append(row) 
    #         
    #         logging.info("Wrong data in row:\n " + ", ".join(str(x) for x in wrong_data_row_id))
    #         logging.info("Received pattern %x %x %x %x vs Expected pattern %x %x %x %x"%(dataRet[0,row], dataRet[1,row], dataRet[2,row], dataRet[3,row], data[pattern_id,0,row], data[i,1,row], data[pattern_id,2,row], data[pattern_id,3,row]))
    #         isOffsetOK = isOffsetOK & (len(wrong_data_row_id) == 0)           
    #     stop = time.time()
    #     
    #     self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["offset_en_out"].set_value()
    #     self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["dispatch"].set_value()
    #     if isOffsetOK:
    #         logging.info("I/O; Offset Test passed after %d sec"%(stop-start))
    #     else:
    #         logging.warning("I/O; Offset Test failed.")
    #     
    #     '''
    #     Test Switcher Data 
    #     '''
    #     isSwitcherOK = True
    #     logging.info("I/O; Switcher Data Test ")
    #     start = time.time()
    #     data = np.zeros((4,4,1024), dtype=np.uint32)
    #     data[0,:,:] = np.array(4*[1024*[0xAAAAAAAA]], dtype=np.uint32)    
    #     data[1,:,:] = np.array(4*[1024*[0x55555555]], dtype=np.uint32)    
    #     data[2,:,:] = np.random.randint(0,np.power(2,32),(4,1024))
    #     data[3,:,:] = np.random.randint(0,np.power(2,32),(4,1024))
    #     
    #     numOfGates = 256
    #     self.sc.dhptRegister.JTAG_REGISTERS["CORE"]["pv"]["last_row"].set_value(numOfGates-1)
    #     self.sc.dhptRegister.JTAG_REGISTERS["CORE"]["dispatch"].set_value()    
    #     self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["sw_en_out"].set_value(1)
    #     self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["dispatch"].set_value()
    #     
    #     for pattern_id in range(4):
    #         self.sc.fill_switcher_memory(data[pattern_id])
    #         dataRet = PROBECARD.get_switcherBits(numOfGates)
    #         
    #         wrong_data_row_id = []
    #         if dataRet.shape == numOfGates:
    #             for row in range(numOfGates):
    #                 if (data[pattern_id,:,row] != dataRet[:,row]): 
    #                     wrong_data_row_id.append(row) 
    #         
    #         logging.info("Wrong data in row:\n " + ", ".join(str(x) for x in wrong_data_row_id))
    #         logging.info("Received pattern %x %x %x %x vs Expected pattern %x %x %x %x"%(dataRet[0,row], dataRet[1,row], dataRet[2,row], dataRet[3,row], data[pattern_id,0,row], data[i,1,row], data[pattern_id,2,row], data[pattern_id,3,row]))
    #         isSwitcherOK = isSwitcherOK & (len(wrong_data_row_id) == 0)           
    #     stop = time.time()
    #     
    #     self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["sw_en_out"].set_value()
    #     self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["dispatch"].set_value()
    #     if isSwitcherOK:
    #         logging.info("I/O; Switcher Test passed after %d sec"%(stop-start))
    #     else:
    #         logging.warning("I/O; Switcher Test failed.")
    #     
    #===========================================================================
        
    def test_high_speed_link(self):
        isHSOK = False
        '''
        Test High Speed Link Memory
        '''
        logging.info("HS; High Speed Link Test")
        start = time.time()
        os.system("/home/lgermic/.cs-studio/analysis/aurora_optimization/aurora_scan.py")
        os.system("/home/lgermic/.cs-studio/analysis/aurora_optimization/aurora_analyze.py")
        '''
        TODO: aurora_analyze return if link stable and best bias parameters
        '''
        linkUp = True
        bias = [25,250,2]
        
        if linkUp:
            self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["IDAC_CML_TX_BIAS"].set_value(bias[0])
            self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["IDAC_CML_TX_BIASD"].set_value(bias[1])
            self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["pll_cml_dly_sel"].set_value(bias[2])
            self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["dispatch"].set_value()
            
        stop = time.time()
        
        if linkUp:
            logging.info("HS; High Speed Test passed after %d sec"%(stop-start))
            isHSOK = True
        else:
            logging.warning("HS; High Speed Test failed. No bias condition found.")
    
        return isHSOK
    
    def test_data_path(self):
        pass
    
    def test_digital_processing(self):
        pass
    
    def CML_iv_curve(self):
        from argparse import ArgumentParser
        import configparser
        import epics_utils
        import config_utils
        import time
        import numpy as np
        import os
        from daq import folder_for_data
        import shutil
        import matplotlib.pyplot as pl
        import matplotlib as mpl
        import sys
        from math import sqrt
        import matplotlib.ticker as tick
        from matplotlib.backends.backend_pdf import PdfPages
    
    
    
        ################ parse inifile (aurora_scan.ini) #################
        parser = ArgumentParser(description='Check Aurora HS Link')
        parser.add_argument('-c', '--filename', dest='filename', default='iv_curve.ini')
        args = parser.parse_args()
    
        filename = args.filename.decode('utf-8')
        config = configparser.ConfigParser(delimiters=("="))
        config.optionxform = str
        config.read(filename)
    
        ############### load settings from ini file (aurora_scan.ini) #################
        path = config.get("general","path")
        asicpair = map(int, config.get("general","asicpair").split(","))
        dheprefix = config.get("general", "dhe")
        bias_start = config.getint("bias","start")
        bias_step = config.getint("bias","step")
        bias_stop = config.getint("bias","stop")
        biasd_start = config.getint("biasd","start")
        biasd_step = config.getint("biasd","step")
        biasd_stop = config.getint("biasd","stop")
        timestamp = config.getboolean("general", "timestamp", fallback=True)
        loadData = config.getboolean("general", "loaddata", fallback=True)
        analysispath = config.get("plot","path")
    
        ############### get pv names of bias, biasd, biasdelay & channel_up for all asicpairs and put them to pv lists ################
        bias_pvlist = []
        biasd_pvlist = []
        write_pvlist = []
        ser_pvlist = []
        core_pll_pvlist = []
        ####### create pv lists #############
    
        
        bias = epics_utils.pvname_dhp(dheprefix, 1, "idac_cml_tx_bias:VALUE:set")
        bias_pvlist.append(bias)
        biasd = epics_utils.pvname_dhp(dheprefix, 1, "idac_cml_tx_biasd:VALUE:set")
        biasd_pvlist. append(biasd)
        ser = epics_utils.pvname_dhp(dheprefix, 1, "pll_ser_clk_sel:S:set")
        ser_pvlist.append(bias)
        core_pll = epics_utils.pvname_dhp(dheprefix, 1, "pll_des_clk_sel:VALUE:set")
        core_pll_pvlist.append(biasd)
        
        write = epics_utils.pvname_dhp(dheprefix, int(1), "globalreg:trg:set")
        write_pvlist.append(write)
        # PVs are not connected because there is no .get() nor .put() method
        #print link_pvlist_eye
        #print link_pvlist_green
    
    
        if not loadData:
            # copy setting and save to file
            print "timestamp"
            path = folder_for_data(path, timestamp)
            print "data will be saved in: %s"%path
            # copy ini file
            shutil.copy(args.filename, os.path.join(path, args.filename))
            # save configuration to disk
            #config_utils.save_settings(path, dheprefix=dheprefix, psprefix=ps)
            for item in core_pll_pvlist:
                epics_utils.get_pv(item).put(3)
            for item in ser_pvlist:    
                epics_utils.get_pv(item).put(1)
            ############ create numpy array [bias, biasd, asicpairs] of zeros ##############
            bias_length = (bias_stop + 1 - bias_start) / bias_step
            biasd_length = (biasd_stop + 1 - biasd_start) / biasd_step
            data = np.zeros( (256 , 256))
        
            for item in write_pvlist:
                epics_utils.get_pv(item).put(1)
                time.sleep(0.1)
        
            ############# step through bias ##############
            bias_index = 0
            for bias_value in range(bias_start, bias_stop +1, bias_step):
    
                ################# set the bias value for all four dhps using the pvlist ################
                for item in bias_pvlist:
                    epics_utils.get_pv(item).put(bias_value)
    
                ################ step through biasd ####################
                biasd_index = 0
                for biasd_value in range(biasd_start, biasd_stop+1, biasd_step):
    
                    ################# set the biasd value for all four dhps using the pvlist ################
                    for item in biasd_pvlist:
                        epics_utils.get_pv(item).put(biasd_value)
    
                    print
                    print "BIAS: " + str(bias_value)
                    print "BIASD: " + str(biasd_value)
                    
                    ############### write to JTAG ###################
                    for item in write_pvlist:
                        epics_utils.get_pv(item).put(1)
                        time.sleep(0.1)
                    
                    ivdd = self.compensate_vdrop()["IVDD"]*1000.0 
                    print 'IVDD: %smA\t at '%ivdd + '{:05.3f}'.format(self.get_VDD_voltage()) + 'V' 
                    print
                    data[bias_value, biasd_value] =ivdd 
                     
                ################## save numpy array to path ##################
                filename = "cml_iv_curve.npz"
                print "saving numpy array to " + path + "/" + filename
                np.savez(os.path.join(path, filename),data=data)
    
            ############# reset to default values #############
            for item in bias_pvlist:
                epics_utils.get_pv(item).put(15)
            for item in biasd_pvlist:
                epics_utils.get_pv(item).put(150)
            for item in core_pll_pvlist:
                epics_utils.get_pv(item).put(3)
            for item in ser_pvlist:    
                epics_utils.get_pv(item).put(1)
        
            for item in write_pvlist:
                epics_utils.get_pv(item).put(1)
                time.sleep(0.1)
    
            print "data has been recorded in: %s"%path
        
        savenamepdf = os.path.join(analysispath, "overview.pdf")
        print savenamepdf
        pdf = PdfPages(savenamepdf)
        
        bias = range(bias_start, bias_stop+1,bias_step)
        biasd = range(biasd_start, biasd_stop+1,biasd_step)
        filename = "cml_iv_curve.npz"
        loaded_data = np.load(os.path.join(analysispath, filename))
        data=loaded_data['data']

        plot_cml(pdf, data, bias, biasd)
        

        pdf.close()
        pl.show()
        
    def test_aurora_link(self):
        from argparse import ArgumentParser
        import configparser
        import epics_utils
        import config_utils
        import time
        import numpy as np
        import os
        from daq import folder_for_data
        import shutil
        import matplotlib.pyplot as pl
        import matplotlib as mpl
        import sys
        from math import sqrt
        from matplotlib.backends.backend_pdf import PdfPages
    
    
    
        ################ parse inifile (aurora_scan.ini) #################
        parser = ArgumentParser(description='Check Aurora HS Link')
        parser.add_argument('-c', '--filename', dest='filename', default='aurora_scan.ini')
        args = parser.parse_args()
    
        filename = args.filename.decode('utf-8')
        config = configparser.ConfigParser(delimiters=("="))
        config.optionxform = str
        config.read(filename)
    
        ############### load settings from ini file (aurora_scan.ini) #################
        path = config.get("general","path")
        asicpair = map(int, config.get("general","asicpair").split(","))
        delay = config.getfloat("general","delay")
        dheprefix = config.get("general", "dhe")
        bias_start = config.getint("bias","start")
        bias_step = config.getint("bias","step")
        bias_stop = config.getint("bias","stop")
        biasd_start = config.getint("biasd","start")
        biasd_step = config.getint("biasd","step")
        biasd_stop = config.getint("biasd","stop")
        biasdelay_start = config.getint("bias_delay","start")
        biasdelay_stop = config.getint("bias_delay","stop")
        biasdelay_step = config.getint("bias_delay","step")
        timestamp = config.getboolean("general", "timestamp", fallback=True)
        loadData = config.getboolean("general", "loaddata", fallback=True)
        analysispath = config.get("plot","path")
    
    
        ############### define plot function #########################
    
    
        ############### get pv names of bias, biasd, biasdelay & channel_up for all asicpairs and put them to pv lists ################
        bias_pvlist = []
        biasd_pvlist = []
        biasdelay_pvlist = []
        channel_up_pvlist = []
        write_pvlist = []
        link_pvlist_eye = []
        link_pvlist_green = []
    
    
    
        ####### create pv lists #############
    
        
        bias = epics_utils.pvname_dhp(dheprefix, 1, "idac_cml_tx_bias:VALUE:set")
        bias_pvlist.append(bias)
        biasd = epics_utils.pvname_dhp(dheprefix, 1, "idac_cml_tx_biasd:VALUE:set")
        biasd_pvlist. append(biasd)
        biasdelay = epics_utils.pvname_dhp(dheprefix, 1, "pll_cml_dly_sel:VALUE:set")
        biasdelay_pvlist.append(biasdelay)
        write = epics_utils.pvname_dhp(dheprefix, int(1), "globalreg:trg:set")
        write_pvlist.append(write)
        link_pvlist_green.append(epics_utils.get_pv ( epics_utils.pvname(  dheprefix,"dhp1_channel_up:S:cur" ) ))
        link_pvlist_eye.append(  epics_utils.get_pv ( epics_utils.pvname( dheprefix,"dfeeyedacmon1:AMPL:raw" ) ))
        longrst = epics_utils.get_pv( epics_utils.pvname(dheprefix, "dhp_rst_long:S:set") )
        gtxrst =  epics_utils.get_pv( epics_utils.pvname(dheprefix, "rst_gtx:S:set") )
    
        # PVs are not connected because there is no .get() nor .put() method
        #print link_pvlist_eye
        #print link_pvlist_green
        if not loadData:
            # copy setting and save to file
            print "timestamp"
            path = folder_for_data(path, timestamp)
            print "data will be saved in: %s"%path
            # copy ini file
            shutil.copy(args.filename, os.path.join(path, args.filename))
            # save configuration to disk
            #config_utils.save_settings(path, dheprefix=dheprefix, psprefix=ps)
        
        
            ############ create numpy array [bias, biasd, asicpairs] of zeros ##############
            bias_length = (bias_stop + 1 - bias_start) / bias_step
            biasd_length = (biasd_stop + 1 - biasd_start) / biasd_step
            data = np.zeros( (256 , 256,2, 4))
        
            for biasdelay_value in range(biasdelay_start, biasdelay_stop+1, biasdelay_step):
                ############ set bias delay (pll_cml_dly_sel)  #############
                for item in biasdelay_pvlist:
                    epics_utils.get_pv(item).put(biasdelay_value)
        
                ############# step through bias ##############
                bias_index = 0
                for bias_value in range(bias_start, bias_stop +1, bias_step):
        
                    ################# set the bias value for all four dhps using the pvlist ################
                    for item in bias_pvlist:
                        epics_utils.get_pv(item).put(bias_value)
        
                    ################ step through biasd ####################
                    biasd_index = 0
                    for biasd_value in range(biasd_start, biasd_stop+1, biasd_step):
        
                        ################# set the biasd value for all four dhps using the pvlist ################
                        for item in biasd_pvlist:
                            epics_utils.get_pv(item).put(biasd_value)
        
                        print
                        print "BIAS: " + str(bias_value)
                        print "BIASD: " + str(biasd_value)
                        print "BIASDELAY: " + str(biasdelay_value)
                        print
        
                        ############### write to JTAG ###################
                        for item in write_pvlist:
                            epics_utils.get_pv(item).put(1)
                            time.sleep(delay)
        
                        #################### GTX and long reset ###################
                        #gtxrst.put(1)
                        #time.sleep(delay)
                        # VERY IMPORTANT TO RESET!!!
                        #gtxrst.put(0)
                        #time.sleep(delay)
                        longrst.put(1)
                        time.sleep(delay)
                        longrst.put(1)
                        longrst.put(1)
                        time.sleep(delay)
                        longrst.put(1)
                       
                        time.sleep(4*delay)
        
        
                        #################### if link is ON record memory dump ##############
        
                        memory_dump = epics_utils.get_pv(dheprefix, 'mem_dump:S:set')
                        memory_dump.put(1)
                        time.sleep(delay*5)
                        memory_dump.put(0)
                        time.sleep(delay)
        
        
                        #################### check HS links #################
        
                        #################### check HS links eye diagramm #################
                        for i, item_eye in enumerate(link_pvlist_eye):
                            link_eye = item_eye.get()
                            print "eye: : " + str(link_eye)
                            #################### check HS links green light #################
        
                            #link_green = epics_utils.get_pv(link_pvlist_green[i]).get()
                            link_green = link_pvlist_green[i].get()
                            print "green light: " + str(link_green)
        
                            #################### multiply green light and eye value #################
        
                            self.compensate_vdrop()
                            ########## write to numpy #############
                            data[bias_value, biasd_value, 0, int(asicpair[i])-1] = link_green
                            data[bias_value, biasd_value, 1, int(asicpair[i])-1] = link_eye
        
        
        
                ################## save numpy array to path ##################
                filename = "pll_cml_dly_sel" + str(biasdelay_value) + ".npz"
                print "saving numpy array to " + path + "/" + filename
                np.savez(os.path.join(path, filename),data=data)
        
                ############## reset to default values #############
                for item in bias_pvlist:
                    epics_utils.get_pv(item).put(15)
                for item in biasd_pvlist:
                    epics_utils.get_pv(item).put(150)
                for item in biasdelay_pvlist:
                    epics_utils.get_pv(item).put(0)
                for item in write_pvlist:
                    epics_utils.get_pv(item).put(1)
        
        
                ######## call plot function #################
                #loaded_data = np.load(os.path.join(path, filename))
                #data=loaded_data['data']
        
                #plot_bias_biasd(data,bias_start, bias_stop, biasd_start,biasd_stop)
            print "data has been recorded in: %s"%path
    
        bias = range(bias_start, bias_stop+1,bias_step)
        biasd = range(biasd_start, biasd_stop+1,biasd_step)
        biasdly = range(biasdelay_start, biasdelay_stop+1, biasdelay_step)
        # save to pdf
        savenamepdf = os.path.join(path, "overview.pdf")
        print savenamepdf
        pdf = PdfPages(savenamepdf)


        plot_bias_biasd(pdf, path, bias, biasd, biasdly)

        pdf.close()
        pl.show()
    
    def shmoo_plot(self, voltages=range(800,1400,100), nrframes=10, scan=False):
        from matplotlib.backends.backend_pdf import PdfPages
        import matplotlib.pyplot as pl
        
        freq = {'0-62.5MHz':0, '1-65MHz':1, '2-67.84MHz':2, '3-71.2MHz':3, '4-76.23MHz':4}#, '5-127.21MHz':5}
        volt = {}
        for v in voltages:
            if len(str(v)) ==4:
                volt["%smV"%v] = float(v)/1000.0
            else:
                volt["0%smV"%v] = float(v)/1000.0
        freq = OrderedDict(sorted(freq.items()))
        volt = OrderedDict(sorted(volt.items(), reverse=True))
        
        path='/home/user/NeedleCardTest/Data/DHPT1.2b/shmooplot/'
        
        if scan:
            currents = np.zeros((len(freq),len(volt)),dtype=np.float)
            eye = np.zeros((len(freq),len(volt)),dtype=np.int)
            jtag = np.zeros((len(freq),len(volt)),dtype=np.int)
            
            data = np.random.randint(255, size=(1024,64), dtype=np.uint8)
            np.savez(os.path.join(path, 'random_test_pattern.npz'),data=data)
            
            self.compensate_vdd_drop()
            get_pv('config:PXD:H1032:config:VALUE:set').put('/home/user/cs-studio/dhh/inifiles/dhh_pxd_bonn.cfg')
            memdump = get_pv( pvname('PXD:H1032', "mem_dump:S:set"))
            with daq.dhh_daq(dheprefix='PXD:H1032') as writer:   
                for fname, fidx in freq.iteritems():
                    self.set_DHE_voltage(v=0.0,on=True)
                    sleep(1)
                    self.set_DHE_voltage(on=True)
                    cnt = 0
                    while not self.is_DHE_on():
                        time.sleep(0.5)
                        printProgress(cnt,10)
                        cnt = cnt + 1
                    logging.info("%s\tDHE is ready!", __name__)
                    sleep(1)
                    get_pv('config:PXD:H1032:config:trg:set').put(1)
                    sleep(1)
                    get_pv('PXD:H1032:clock_frequency:set').put(fidx)
                    sleep(1)
                    print 'Set to frequency %s'%fname
                    get_pv('PXD:H1032:dhpt_crst:S:set').put(1)
                    sleep(0.5)
                    get_pv('PXD:H1032:jtag_reinit_chain:S:set').put(1)
                    sleep(0.1)
                    get_pv('PXD:H1032:jtag_reinit_chain:S:set').put(0)
                    self.compensate_vdd_drop(vdd=1.2)
                    sleep(1)
                    upload_frame_data('PXD:H1032:', 1, data)
                    sleep(0.5)
                    vcnt = len(volt.items())-1
                    for vname, vval in volt.iteritems():   
                        print 'VDD @ %s'%vname
                        self.compensate_vdd_drop(vdd=vval)
                        sleep(0.2)
                        eye[fidx,vcnt] = get_pv('PXD:H1032:dfeeyedacmon1:AMPL:raw').get()
                        currents[fidx,vcnt] = float(self.get_VDD_current())*1000.0
                        self.sc.dhptRegister.set_default()
                        self.sc.dhptRegister.JTAG_REGISTERS['GLOBAL']['pv']['IDAC_CML_TX_BIAS'].set_value(255)
                        self.sc.dhptRegister.JTAG_REGISTERS['GLOBAL']['pv']['IDAC_CML_TX_BIASD'].set_value(100)
                        self.sc.dhptRegister.JTAG_REGISTERS['GLOBAL']['dispatch'].set_value(1)
                        self.sc.dhptRegister.JTAG_REGISTERS['CORE']['pv']['test_mode_en'].set_value(1)
                        self.sc.dhptRegister.JTAG_REGISTERS['CORE']['dispatch'].set_value(1)
                        sleep(0.5)
                        get_pv('PXD:H1032:D1:corereg:trg:cur').put(1)
                        sleep(0.5)
                        if self.sc.dhptRegister.JTAG_REGISTERS['CORE']['pv']['chip_id'].get_value()!=0:
                            jtag[fidx,vcnt] = 1
                        print "START DAQ"
                        dhp_utils.get_link(dhe='PXD:H1032',asicpair=1)
                        sleep(1)
                        try:
                            writer.set_filename(filename=path+"shmoo_freq%s_volt%s"%(fname,vname))
                            writer.start()
                            memdump.put(0)
                            sleep(0.5)
                            for i in range(nrframes):
                                memdump.put(1)
                                time.sleep(0.05)
                                memdump.put(0)
                                time.sleep(0.05)
                            sleep(0.5)
                            writer.stop()
                            sleep(0.5)
                        except IOError:
                            print 'No Link, no data...'
                        print "DAQ done"
                        vcnt = vcnt - 1
            np.savez(os.path.join(path, 'currents.npz'),data=currents)
            np.savez(os.path.join(path, 'eye.npz'),data=eye)
            np.savez(os.path.join(path, 'jtag.npz'),data=jtag)
            
        savenamepdf = os.path.join(path, "overview.pdf")
        print savenamepdf
        pdf = PdfPages(savenamepdf)
       
        
        # frequency, voltage,relNumOfRecFrames,relNumOfWrongBytes
        shmoo = np.zeros((len(freq),len(volt),5))
        
        filename = 'random_test_pattern.npz'
        loaded_data = np.load(os.path.join(path, filename))
        rndData=loaded_data['data']
        
        filename = 'currents.npz'
        loaded_data = np.load(os.path.join(path, filename))
        currents=loaded_data['data']
        shmoo[:,:,2] = currents
        
        filename = 'eye.npz'
        loaded_data = np.load(os.path.join(path, filename))
        eye=loaded_data['data']
        shmoo[:,:,3] = eye
        
        filename = 'jtag.npz'
        loaded_data = np.load(os.path.join(path, filename))
        jtag=loaded_data['data']
        shmoo[:,:,4] = jtag
        
        
        vcnt = len(volt.items())-1  
        for vname, vval in volt.iteritems():   
            for fname, fidx in freq.iteritems():      
                filename = 'shmoo_freq%s_volt%s'%(fname,vname)
                fdata, isgood = readFile(os.path.join(path, filename),asicpair=1,frames=nrframes)
                goodbytes = len(np.where((fdata==rndData[...,np.newaxis]))[0])
                shmoo[fidx,vcnt,0] = int(float(fdata.shape[2])/nrframes)
                shmoo[fidx,vcnt,1] = float(goodbytes)/(fdata.shape[0]*fdata.shape[1]*fdata.shape[2])
            vcnt = vcnt - 1
        plot_shmoo(pdf, shmoo, rndData, list(reversed(volt.keys())), freq.keys())
        pdf.close()
        pl.show()       
        
        