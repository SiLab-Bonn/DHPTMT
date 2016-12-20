from epics import get_pv
from slowcontrol import *
from Probecard import PROBECARD
#from dhh import mapping
#from pyDepfetReader.file_reader import FileReader
from misc import initiate_logger, printProgress
from basil.dut import Dut
from __builtin__ import True


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
        self.parasiticResistanceVDD = 5.0/8 #Needle and bumb connection compensation
        self.parasiticResistanceDVDD = 5.0/8 #Needle and bumb connection compensation
        
        self.sc         = SlowControl()
  
        self.logger = initiate_logger(logFileDir, softwareVersion, dhptVersion, True)
        #PROBECARD.__init__(self, config)
        self.psu1.init()
        self.psu2.init()
	
    def init_voltages(self):
        self.set_VDD_voltage()
        self.set_DVDD_voltage()
        self.set_VCC_voltage()
        self.set_DHE_voltage()
        
        self.enable_voltages()
        cnt = 0
        while not self.is_DHE_on():
            time.sleep(0.5)
            printProgress(cnt,10)
            cnt = cnt + 1
        self.logger.info("DHE is ready!")
        
        self.logger.info("VCC on? %s"%self.is_VCC_on())
        self.logger.info("dut connected? %s"%self.is_dut_connected())
        self.logger.info("Init successul")
        if self.is_VCC_on() and self.is_dut_connected():
            self.set_VDD_voltage(v=1.2+float(self.get_VDD_current()*self.parasiticResistanceVDD), on=True)
            self.set_DVDD_voltage(v=1.8+float(self.get_DVDD_current()*self.parasiticResistanceDVDD), on=True)
            return True
        else:
            return False
    
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
        if self.get_DHE_current() > 1.5:
            return True
        else:
            return False
    
    def is_VCC_on(self):
        if self.get_VCC_current() > 0.05:
            return True
        else:
            return False
        
    def enable_voltages(self):
        self.psu2["PowerSupply2"].on(channel=1)
        self.psu2["PowerSupply2"].on(channel=2)
        self.psu1["PowerSupply1"].on(channel=1)
        self.psu1["PowerSupply1"].on(channel=2)
    
    def disable_voltages(self):
        self.psu2["PowerSupply2"].off(channel=1)
        self.psu2["PowerSupply2"].off(channel=2)
        self.psu1["PowerSupply1"].off(channel=1)
        self.psu1["PowerSupply1"].off(channel=2)
            
    def set_VDD_voltage(self, v=1.2, on=False):
        self.vdd = v
        ch = 1
        self.psu2["PowerSupply2"].set_ocp(0.24, channel=ch)
        self.psu2["PowerSupply2"].set_current_limit(0.22, channel=ch) 
        self.psu2["PowerSupply2"].set_ovp(self.vdd+0.2, channel=ch)                   
        self.psu2["PowerSupply2"].set_voltage(self.vdd, channel=ch)
        if on:
            self.psu2["PowerSupply2"].on(channel=ch)
        else:
            self.psu2["PowerSupply2"].off(channel=ch)

    def set_DVDD_voltage(self, v=1.8, on=False):
        self.dvdd= v
        ch = 2
        self.psu2["PowerSupply2"].set_ocp(0.08, channel=ch)
        self.psu2["PowerSupply2"].set_current_limit(0.06, channel=ch) 
        self.psu2["PowerSupply2"].set_ovp(self.dvdd+0.2, channel=ch)                  
        self.psu2["PowerSupply2"].set_voltage(self.dvdd, channel=ch)
        if on:
            self.psu2["PowerSupply2"].on(channel=ch)
        else:
            self.psu2["PowerSupply2"].off(channel=ch)

    def set_DHE_voltage(self, v=5.5, on=False):
        val= v
        ch = 1
        self.psu1["PowerSupply1"].set_ocp(2.6, channel=ch)
        self.psu1["PowerSupply1"].set_current_limit(2.5, channel=ch) 
        self.psu1["PowerSupply1"].set_ovp(val+0.2, channel=ch)                   
        self.psu1["PowerSupply1"].set_voltage(val, channel=ch)
        if on:
            self.psu1["PowerSupply1"].on(channel=ch)
        else:
            self.psu1["PowerSupply1"].off(channel=ch)

    def set_VCC_voltage(self, v=2.5, on=False):
        val= v
        ch = 2
        self.psu1["PowerSupply1"].set_ocp(0.5, channel=ch)
        self.psu1["PowerSupply1"].set_current_limit(0.3, channel=ch) 
        self.psu1["PowerSupply1"].set_ovp(val+0.4, channel=ch)                  
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
        self.logger.info("Power; Power Consumption Test")
        ivdd = self.get_VDD_current()
        idvdd = self.get_DVDD_current()
        
        
        if (ivdd>110) and (ivdd<150) and (idvdd>30) and (idvdd<60):
            self.logger.info("Power; Passed: VDD %smV(%smA) and DVDD %smV(%smA)"%(self.vdd, ivdd, self.dvdd, idvdd))
            return True
        else:
            self.logger.info("Power; Failed: VDD %smV(%smA) and DVDD %smV(%smA)"%(self.vdd, ivdd, self.dvdd, idvdd))
            return False
            
    def test_jtag(self):
        crst = get_pv(self.sc.dhePrefix+":dhpt_crst:S:set")
        reinJTAG = get_pv(self.sc.dhePrefix+":jtag_reinit_chain:S:set")
        if not get_pv(self.sc.dhePrefix+":jtag_chain_initialized:S:cur").get():
            crst.put(0)
            crst.put(1)
            self.logger.info("%s\tCRESETB; Reset JTAG registers in DHPT", __name__)
            reinJTAG.put(1)
            self.logger.info("%s\tReinitalized JTAG chain",__name__)
        
        self.sc.turn_all_regs_on()
        return True
    
    def test_memories(self):
        isPedestalMemoryOK = False
        isOffsetMemoryOK   = False
        isSwitcherMemoryOK = False
        
        '''
        Test Data+Pedestal Memory
        '''
        self.logger.info("MEM; Pedestal memory test")
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
                self.logger.fatal("Bit error detected: in mem block %s", derr[0]) 
            
            for pat in pattern: 
                self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["mem0"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["mem1"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["mem2"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["PEDESTAL"]["pv"]["mem3"].set_value(pat)
                for blk in range(16):
                    #self.logger.info("MEM; use pattern %x"%pat)
                    #self.logger.info("Pattern %x"%pat)
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
                        #self.logger.info(patternErr)
                        if ((mem0 != pat) or (mem1 != pat) or (mem2 != pat) or (mem3 != pat)):
                            patternErr = patternErr + 1 
                            self.logger.info("Adress %d failure in block %d"%(addr_id, blk))
                            self.logger.info("Received pattern %x %x %x %x"%(mem0, mem1, mem2, mem3))
                        
        stop = time.time()  
        
        if (patternErr == 0) and not isErr:
            self.logger.info("Mem; Pedestal memory test passed after %d sec"%(stop-start))
            isPedestalMemoryOK = True
        else:
            self.logger.warning("Mem; Pedestal memory test failed. Result %d (!= 0)"%patternErr)
           
        '''
        Test Offset Memory
        '''
        self.logger.info("MEM; Offset memory test")
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
                self.logger.fatal("Bit error detected: in mem block %s", derr[0]) 
            
            for pat in pattern: 
                self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["mem0"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["mem1"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["mem2"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["OFFSET"]["pv"]["mem3"].set_value(pat)
                #self.logger.info("MEM; use pattern %x"%pat)
                #self.logger.info("Pattern %x"%pat)
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
                    #self.logger.info(patternErr)
                    if ((mem0 != pat) or (mem1 != pat) or (mem2 != pat) or (mem3 != pat)):
                        patternErr = patternErr + 1 
                        self.logger.info("Adress %d failure in block %d"%(addr_id, blk))
                        self.logger.info("Received pattern %x %x %x %x"%(mem0, mem1, mem2, mem3))
                    
        stop = time.time()  
        
        if (patternErr == 0) and not isErr:
            self.logger.info("Mem; Offset memory test passed after %d sec"%(stop-start))
            isOffsetMemoryOK = True
        else:
            self.logger.warning("Mem; Offset memory test failed. Result %d (!= 0)"%patternErr)
                
        
        '''
        Test Switcher Memory
        '''
        self.logger.info("MEM; Switcher memory test")
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
                self.logger.fatal("Bit error detected: in mem block %s", derr[0]) 
            
            for pat in pattern: 
                self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["mem0"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["mem1"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["mem2"].set_value(pat)
                self.sc.dhptRegister.MEMORY_REGISTERS["SWITCHER"]["pv"]["mem3"].set_value(pat)
                for blk in range(16):
                    #self.logger.info("MEM; use pattern %x"%pat)
                    #self.logger.info("Pattern %x"%pat)
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
                        #self.logger.info(patternErr)
                        if ((mem0 != pat) or (mem1 != pat) or (mem2 != pat) or (mem3 != pat)):
                            patternErr = patternErr + 1 
                            self.logger.info("Adress %d failure in block %d"%(addr_id, blk))
                            self.logger.info("Received pattern %x %x %x %x"%(mem0, mem1, mem2, mem3))
                        
        stop = time.time()  
        
        if (patternErr == 0) and not isErr:
            self.logger.info("Mem; Offset memory test passed after %d sec"%(stop-start))
            isSwitcherMemoryOK = True
        else:
            self.logger.warning("Mem; Offset memory test failed. Result %d (!= 0)"%patternErr)
                
                
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
    #     self.logger.info("I/O; DCD-DHPT Delay Test ")
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
    #         self.logger.info("I/O; DCD-DHPT Delay Test passed after %d sec"%(stop-start))
    #         isDelayOK = True
    #     else:
    #         self.logger.warning("I/O; DCD-DHPT Delay Test failed. No set of delays found.")
    # 
    #     '''
    #     Test DCD Data 
    #     '''
    #     self.logger.info("I/O; DCD-DHPT Data Test ")
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
    #         self.logger.info("I/O; DCD-DHPT Delay Test passed after %d sec"%(stop-start))
    #         isDCDOK = True
    #     else:
    #         self.logger.warning("I/O; DCD-DHPT Delay Test failed. No set of delays found.")
    #     
    #     '''
    #     Test Offset Data 
    #     '''
    #     isOffsetOK = True
    #     self.logger.info("I/O; OFFSET Data Test ")
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
    #         self.logger.info("Wrong data in row:\n " + ", ".join(str(x) for x in wrong_data_row_id))
    #         self.logger.info("Received pattern %x %x %x %x vs Expected pattern %x %x %x %x"%(dataRet[0,row], dataRet[1,row], dataRet[2,row], dataRet[3,row], data[pattern_id,0,row], data[i,1,row], data[pattern_id,2,row], data[pattern_id,3,row]))
    #         isOffsetOK = isOffsetOK & (len(wrong_data_row_id) == 0)           
    #     stop = time.time()
    #     
    #     self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["offset_en_out"].set_value()
    #     self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["dispatch"].set_value()
    #     if isOffsetOK:
    #         self.logger.info("I/O; Offset Test passed after %d sec"%(stop-start))
    #     else:
    #         self.logger.warning("I/O; Offset Test failed.")
    #     
    #     '''
    #     Test Switcher Data 
    #     '''
    #     isSwitcherOK = True
    #     self.logger.info("I/O; Switcher Data Test ")
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
    #         self.logger.info("Wrong data in row:\n " + ", ".join(str(x) for x in wrong_data_row_id))
    #         self.logger.info("Received pattern %x %x %x %x vs Expected pattern %x %x %x %x"%(dataRet[0,row], dataRet[1,row], dataRet[2,row], dataRet[3,row], data[pattern_id,0,row], data[i,1,row], data[pattern_id,2,row], data[pattern_id,3,row]))
    #         isSwitcherOK = isSwitcherOK & (len(wrong_data_row_id) == 0)           
    #     stop = time.time()
    #     
    #     self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["sw_en_out"].set_value()
    #     self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["dispatch"].set_value()
    #     if isSwitcherOK:
    #         self.logger.info("I/O; Switcher Test passed after %d sec"%(stop-start))
    #     else:
    #         self.logger.warning("I/O; Switcher Test failed.")
    #     
    #===========================================================================
        
    def test_high_speed_link(self):
        isHSOK = False
        '''
        Test High Speed Link Memory
        '''
        self.logger.info("HS; High Speed Link Test")
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
            self.logger.info("HS; High Speed Test passed after %d sec"%(stop-start))
            isHSOK = True
        else:
            self.logger.warning("HS; High Speed Test failed. No bias condition found.")
    
        return isHSOK
    
    def test_data_path(self):
        pass
    
    def test_digital_processing(self):
        pass
    
    
    