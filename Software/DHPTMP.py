from epics import get_pv
import slowcontrol 
from probecard import PPROBECARD
from dhh import mapping
from pyDepfetReader.file import_reader import FileReader
import logger
from basil.dut import Dut


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
                                #logging.info("Set max value %d"%max_val)
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
                                    #logging.info("Set max value %d"%max_val)
                        else:   
                            if pvname not in excludedRegs and pv.pvGet.connected:
                                logging.info("Checking pv %s"%pvname)
                                max_val = pow(2,pv.size)-1 
                                result = result + pv.pvGet.get()
                                #logging.info("Set max value %d"%max_val)
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
        self.psu1       = Dut("dut1_ttiql335tp_pyvisa.yaml")
        self.psu2       = Dut("dut2_ttiql335tp_pyvisa.yaml")
        
        self.sc         = SlowControl()
  
        logger.initiate_logger(logFileDir, softwareVersion, dhptVersion, True)
        PROBECARD.__init__(self, config)
        self.psu1.init()
        self.psu2.init()
        
    def set_VDD_voltage(self, ch=0, v=1200, u="mV"):
        val= 1200
        if (u == "mV"):
            if (v>900) and (v<1500):
                pass
            elif v<900:
                val = 900
            elif v>1500:
                val = 1500
                           
        self.psu1["PowerSupply"].set_voltage(val, unit=u, channel=ch)

    def set_DVDD_voltage(self, ch=1, v=1800, u="mV"):
        val= 1800
        if (u == "mV"):
            if (v>1600) and (v<2200):
                pass
            elif v<1600:
                val = 1600
            elif v>2200:
                val = 2200
                           
        self.psu1["PowerSupply"].set_voltage(val, unit=u, channel=ch)

    def set_VCC_voltage(self, ch=0, v=3300, u="mV"):
        val= 3300
        if (u == "mV"):
            if (v>3000) and (v<3500):
                pass
            elif v<3000:
                val = 3000
            elif v>3500:
                val = 3500
                           
        self.psu2["PowerSupply"].set_voltage(val, unit=u, channel=ch)
    
    def get_VDD_current(self, ch=0):
        self.psu1['PowerSupply'].get_current(channel=ch)

    def get_DVDD_current(self, ch=1):
        self.psu1['PowerSupply'].get_current(channel=ch)

    def test_power_consumption(self):
        logging.info("Power; Power Consumption Test")
        ivdd = get_VDD_current()
        idvdd = get_DVDD_current()
        
        
        if (ivdd>110) and (ivdd<150) and (idvvd>30) and (idvdd<60):
            logging.info("Power; Passed: VDD %smV(%smA) and DVDD %smV(%smA)"%(self.psu1.get_voltage(channel=0), ivdd, self.psu1.get_voltage(channel=1), idvdd))
            return True
        else:
            logging.info("Power; Failed: VDD %smV(%smA) and DVDD %smV(%smA)"%(self.psu1.get_voltage(channel=0), ivdd, self.psu1.get_voltage(channel=1), idvdd))
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
    
    def test_io_streams(self):
        isDelayOK    = False
        isDCDOK      = False
        isOffsetOK   = False
        isSwitcherOK = False
         
        '''
        Test DCD Delay scan
        '''
        logging.info("I/O; DCD-DHPT Delay Test ")
        start = time.time()
        PROBECARD.send_testpattern_to_dhpt()
        os.system("/home/lgermic/.cs-studio/analysis/delays/scan_delays.py")
        os.system("/home/lgermic/.cs-studio/analysis/delays/analyze_delays.py")
        os.system("/home/lgermic/.cs-studio/analysis/delays/find_optimal_delays.py")
        '''
        TODO: find_optimal_delays returns if optimal delays are found and optimal delays
        '''
        optDelays = True
        stop = time.time()
        
        if optDelays:
            logging.info("I/O; DCD-DHPT Delay Test passed after %d sec"%(stop-start))
            isDelayOK = True
        else:
            logging.warning("I/O; DCD-DHPT Delay Test failed. No set of delays found.")
    
        '''
        Test DCD Data 
        '''
        logging.info("I/O; DCD-DHPT Data Test ")
        start = time.time()
        testpattern = PROBECARD.send_random_pattern_to_dhpt()
        filename = self.fileDir+"data"
        self.sc.read_dhpt_data_via_hs(filename)
        
        read = FileReader(-1,1)
        read.set_debug_output(False)
        if read.open(filename):
            print "File not found: ",filename
            sys.exit(-1)
        data, isRaw, isGood = read.readEvent()
        nr_of_frames = 0
        wrongbits = 0
        while isGood:
            nr_of_frames += 1
            dataNew = mapping.matrixToDcd(data[:,:,nr_of_frames-1])
            wrongbits += plots.calculate_wrong_bits(dataNew, testpattern)
            data, isRaw, isGood = read.readEvent()
        
        isDCDOK = (wrongbits == 0) 
        stop = time.time()
        
        if dcdData:
            logging.info("I/O; DCD-DHPT Delay Test passed after %d sec"%(stop-start))
            isDCDOK = True
        else:
            logging.warning("I/O; DCD-DHPT Delay Test failed. No set of delays found.")
        
        '''
        Test Offset Data 
        '''
        isOffsetOK = True
        logging.info("I/O; OFFSET Data Test ")
        start = time.time()
        data = np.zeros((4,4,512), dtype=np.uint32)
        data[0,:,:] = np.array(4*[512*[0xAAAAAAAA]], dtype=np.uint32)    
        data[1,:,:] = np.array(4*[512*[0x55555555]], dtype=np.uint32)    
        data[2,:,:] = np.random.randint(0,np.power(2,32),(4,512))
        data[3,:,:] = np.random.randint(0,np.power(2,32),(4,512))
        
        self.sc.dhptRegister.JTAG_REGISTERS["CORE"]["pv"]["last_row"].set_value(255)
        self.sc.dhptRegister.JTAG_REGISTERS["CORE"]["dispatch"].set_value()    
    
        self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["offset_en_out"].set_value(1)
        self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["dispatch"].set_value()
    
        for pattern_id in range(4):
            self.sc.fill_offset_memory(data[pattern_id])
            PROBECARD.
            dataRet = PROBECARD.get_offsetBits()
            
            wrong_data_row_id = []
            if data[i].shape == dataRet.shape:
                for row in range(data.shape[1]):
                    if (data[id,:,row] != dataRet[:,row]): 
                        wrong_data_row_id.append(row) 
            
            logging.info("Wrong data in row:\n " + ", ".join(str(x) for x in wrong_data_row_id))
            logging.info("Received pattern %x %x %x %x vs Expected pattern %x %x %x %x"%(dataRet[0,row], dataRet[1,row], dataRet[2,row], dataRet[3,row], data[pattern_id,0,row], data[i,1,row], data[pattern_id,2,row], data[pattern_id,3,row]))
            isOffsetOK = isOffsetOK & (len(wrong_data_row_id) == 0)           
        stop = time.time()
        
        self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["offset_en_out"].set_value()
        self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["dispatch"].set_value()
        if isOffsetOK:
            logging.info("I/O; Offset Test passed after %d sec"%(stop-start))
        else:
            logging.warning("I/O; Offset Test failed.")
        
        '''
        Test Switcher Data 
        '''
        isSwitcherOK = True
        logging.info("I/O; Switcher Data Test ")
        start = time.time()
        data = np.zeros((4,4,1024), dtype=np.uint32)
        data[0,:,:] = np.array(4*[1024*[0xAAAAAAAA]], dtype=np.uint32)    
        data[1,:,:] = np.array(4*[1024*[0x55555555]], dtype=np.uint32)    
        data[2,:,:] = np.random.randint(0,np.power(2,32),(4,1024))
        data[3,:,:] = np.random.randint(0,np.power(2,32),(4,1024))
        
        numOfGates = 256
        self.sc.dhptRegister.JTAG_REGISTERS["CORE"]["pv"]["last_row"].set_value(numOfGates-1)
        self.sc.dhptRegister.JTAG_REGISTERS["CORE"]["dispatch"].set_value()    
        self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["sw_en_out"].set_value(1)
        self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["dispatch"].set_value()
        
        for pattern_id in range(4):
            self.sc.fill_switcher_memory(data[pattern_id])
            dataRet = PROBECARD.get_switcherBits(numOfGates)
            
            wrong_data_row_id = []
            if dataRet.shape == numOfGates:
                for row in range(numOfGates):
                    if (data[pattern_id,:,row] != dataRet[:,row]): 
                        wrong_data_row_id.append(row) 
            
            logging.info("Wrong data in row:\n " + ", ".join(str(x) for x in wrong_data_row_id))
            logging.info("Received pattern %x %x %x %x vs Expected pattern %x %x %x %x"%(dataRet[0,row], dataRet[1,row], dataRet[2,row], dataRet[3,row], data[pattern_id,0,row], data[i,1,row], data[pattern_id,2,row], data[pattern_id,3,row]))
            isSwitcherOK = isSwitcherOK & (len(wrong_data_row_id) == 0)           
        stop = time.time()
        
        self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["pv"]["sw_en_out"].set_value()
        self.sc.dhptRegister.JTAG_REGISTERS["GLOBAL"]["dispatch"].set_value()
        if isSwitcherOK:
            logging.info("I/O; Switcher Test passed after %d sec"%(stop-start))
        else:
            logging.warning("I/O; Switcher Test failed.")
        
        
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
    
    
    