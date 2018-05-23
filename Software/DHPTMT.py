import os
import time
from collections import OrderedDict
from time import sleep

import daq
import dhp_utils
import mapping
import numpy as np
import upload_utils
from basil.dut import Dut
from epics import get_pv, pvname

from Probecard import PROBECARD
from epics_slctr import DHPregisters
from misc import initiate_logger, printProgress, updatePortInYaml, plot_bias_biasd, plot_cml, plot_shmoo, readFile


# class SlowControl(object):
#     def __init__(self, dhePrefix="PXD:H1031"):
#          self.dhp = DHPregisters()
#
#     def turn_all_regs_on(self):
#         start = time.time()
#         #Check with all ones
#         for key in self.dhp.regs.iteritems():
#             if ":S" in key:
#                 if key in ["tdo_tx_set_06:S","tdo_tx_set_12:S","tdo_tx_set_30:S","dcd_invert_TRST_polarity:S","dcd_invert_TCK_polarity:S"]:
#                     pass
#                 else:
#                     self.dhp.regs[key] = 1
#             else:
#                 if key in ["pll_des_clk_sel:VALUE","IDAC_LVDS_RX_IREF:VALUE","IDAC_LVDS_TX_IREF:VALUE","IDAC_PLL_I50U:VALUE","IDAC_PLL_ICP:VALUE", \
#                            "IDAC_PLL_IVCO:VALUE", "IREF_TRIMMING:VALUE"]:
#                     pass
#                 else:
#                     self.dhp.regs[key] = 2**16
#
#         self.dhp.write_core()
#         self.dhp.write_global()
#         stop =time.time()
#         return stop-start
#
#     def turn_all_regs_off(self):
#         start = time.time()
#         # Check with all ones
#         for key in self.dhp.regs.iteritems():
#             if ":S" in key:
#                 if key in ["tdo_tx_set_06:S", "tdo_tx_set_12:S", "tdo_tx_set_30:S", "dcd_invert_TRST_polarity:S",
#                            "dcd_invert_TCK_polarity:S"]:
#                     pass
#                 else:
#                     self.dhp.regs[key] = 0
#             else:
#                 if key in ["pll_des_clk_sel:VALUE", "IDAC_LVDS_RX_IREF:VALUE", "IDAC_LVDS_TX_IREF:VALUE",
#                            "IDAC_PLL_I50U:VALUE", "IDAC_PLL_ICP:VALUE", \
#                            "IDAC_PLL_IVCO:VALUE", "IREF_TRIMMING:VALUE"]:
#                     pass
#                 else:
#                     self.dhp.regs[key] = 0
#
#         self.dhp.write_core()
#         self.dhp.write_global()
#         stop = time.time()
#         return stop - start
#
#
#
#
#     def read_dhpt_data_via_hs(self, filename, numberOfFrames = 100, lastRow = 256, firstRow = 0):
#         from dhh import daq
#         self.dhptRegister.JTAG_REGISTERS["CORE"]["pv"]["last_row"].set_value(lastRow)
#         self.dhptRegister.JTAG_REGISTERS["CORE"]["dispatch"].set_value()
#         daq.record_memorydump(1, numberOfFrames, self.dhePrefix, filename)
#
#     def read_dhpt_data_via_jtag(self, filename, numberOfFiles = 5, lastRow = 256, firstRow = 0):
#         from jtagmemoryreader import JTagRawReader
#         reader = JTagRawReader(dhpPrefix, last_row, numberOfFiles)
#         reader.readMemory()
#         frames = reader.getCurrentFrames()
#         np.save(filename, frames)
#
#     def ped_error():
#         self.dhptRegister.JTAG_REGISTERS["CORE READBACK"]["dispatch"].get_value()
#         memErrs = [self.dhptRegister.JTAG_REGISTERS["CORE READBACK"]["pv"]["mem_errors"]["NUM_%s"%k].get_value() for k in range(32)]
#         doubleErrs = []
#         singleErrs = []
#
#         for k in range(len(memErrs)):
#             singleErrs.append([k,memErrs[k] & 0x1f])         #5 bit for single bit errors
#             doubleErrs.append([k,(memErrs[k] & 0xe0) >> 5])  #3 bit for double bit errors
#
#         return singleErrs, doubleErrs
#
#     def offset_error():
#         self.dhptRegister.JTAG_REGISTERS["CORE READBACK"]["reg"].pvGet.get()
#         memErrs = [self.dhptRegister.JTAG_REGISTERS["CORE READBACK"]["pv"]["offset_mem_errors"]["NUM_%s"%k].pvGet.get() for k in range(4)]
#         doubleErrs = []
#         singleErrs = []
#
#         for k in range(len(memErrs)):
#             singleErrs.append([k,memErrs[k] & 0x1f])         #5 bit for single bit errors
#             doubleErrs.append([k,(memErrs[k] & 0xe0) >> 5])  #3 bit for double bit errors
#
#         return singleErrs, doubleErrs
#
#     def sw_seq_error():
#         memErrs = [self.dhptRegister.JTAG_REGISTERS["CORE READBACK"]["reg"]["seq_mem_errors"]["NUM_%s"%k].read() for k in range(2)]
#         doubleErrs = []
#         singleErrs = []
#
#         for k in range(len(memErrs)):
#             singleErrs.append([k,memErrs[k] & 0x1f])         #5 bit for single bit errors
#             doubleErrs.append([k,(memErrs[k] & 0xe0) >> 5])  #3 bit for double bit errors
#
#         return singleErrs, doubleErrs
#
#     def fill_switcher_memory(self, data, start_addr):
#         mem_reg["SWITCHER"]["pv"]["addr"].set_value(start_addr)
#         time.sleep(0.05)
#         for addr_id in range(data.shape[1]):
#             time.sleep(0.05)
#             mem_reg["SWITCHER"]["pv"]["mem0"].set_value(data[0, start_addr])
#             mem_reg["SWITCHER"]["pv"]["mem1"].set_value(data[1, start_addr])
#             mem_reg["SWITCHER"]["pv"]["mem2"].set_value(data[2, start_addr])
#             mem_reg["SWITCHER"]["pv"]["mem3"].set_value(data[3, start_addr])
#             time.sleep(0.05)
#             mem_reg["SWITCHER"]["dispatch"].set_value()
#
#     def fill_offset_memory(self, data):
#         mem_reg["SWITCHER"]["pv"]["addr"].set_value()
#         time.sleep(0.05)
#         for addr_id in range(data.shape[1]):
#             time.sleep(0.05)
#             mem_reg["SWITCHER"]["pv"]["mem0"].set_value(data[0, start_addr])
#             mem_reg["SWITCHER"]["pv"]["mem1"].set_value(data[1, start_addr])
#             mem_reg["SWITCHER"]["pv"]["mem2"].set_value(data[2, start_addr])
#             mem_reg["SWITCHER"]["pv"]["mem3"].set_value(data[3, start_addr])
#             time.sleep(0.05)
#             mem_reg["SWITCHER"]["dispatch"].set_value()

class DHPTMT(PROBECARD):
    def __init__(self, config, logFileDir, softwareVersion, dhptVersion, dhe):
        self.fileDir    = logFileDir
        self.dhePrefix  = dhe
        self.psu1       = Dut("dut1_ttiql335tp_pyserial.yaml")
        self.psu2       = Dut("dut2_ttiql335tp_pyserial.yaml")

        self.vdd = 0.0  
        self.dvdd = 0.0
        self.parasiticResistanceVDD = 5.0/12 + 0.1 #Needle and bumb connection compensation
        self.parasiticResistanceDVDD = 5.0/6 + 0.2 #Needle and bumb connection compensation
        self.parasiticResistanceDHE = 0.1 #Needle and bumb connection compensation
        

        initiate_logger(logFileDir, softwareVersion, dhptVersion)

        self.psu2.init()
        sleep(0.5)
        self.psu1.init()

        updatePortInYaml(config)
        self.dhp = DHPregisters()
        PROBECARD.__init__(self, config)

    def test_jtag_n1(self):
        start = time.time()
        jtag_ok = True
        #Check with all ones
        for key in self.dhp.regs.iteritems():
            if ":S" in key:
                if key in ["tdo_tx_set_06:S","tdo_tx_set_12:S","tdo_tx_set_30:S","dcd_invert_TRST_polarity:S","dcd_invert_TCK_polarity:S"]:
                    pass
                else:
                    self.dhp.regs[key] = 1
            else:
                if key in ["pll_des_clk_sel:VALUE","IDAC_LVDS_RX_IREF:VALUE","IDAC_LVDS_TX_IREF:VALUE","IDAC_PLL_I50U:VALUE","IDAC_PLL_ICP:VALUE", \
                           "IDAC_PLL_IVCO:VALUE", "IREF_TRIMMING:VALUE"]:
                    pass
                else:
                    self.dhp.regs[key] = 2**16

        self.dhp.write_core()
        self.dhp.write_global()
        time.sleep(0.5)
        self.dhp.read_core()
        self.dhp.read_global()
        time.sleep(0.5)

        for key in self.dhp.regs.iteritems():
            if ":S" in key:
                if key in ["tdo_tx_set_06:S","tdo_tx_set_12:S","tdo_tx_set_30:S","dcd_invert_TRST_polarity:S","dcd_invert_TCK_polarity:S"]:
                    pass
                else:
                    if self.dhp.regs[key] != 1:
                        jtag_ok = False
            else:
                if key in ["pll_des_clk_sel:VALUE","IDAC_LVDS_RX_IREF:VALUE","IDAC_LVDS_TX_IREF:VALUE","IDAC_PLL_I50U:VALUE","IDAC_PLL_ICP:VALUE", \
                           "IDAC_PLL_IVCO:VALUE", "IREF_TRIMMING:VALUE"]:
                    pass
                else:
                    if "0" in bin(self.dhp.regs[key])[1:]:
                        jtag_ok = False

        stop = time.time()

        if jtag_ok:
            cmd = "JTAG - test #1 passed after %d sec" % (stop - start)
            return True, cmd
        else:
            cmd = "ERROR: JTAG - test #1 failed after %d sec" % (stop - start)
            return False, cmd

    def test_jtag_n2(self):
        start = time.time()
        jtag_ok = True
        # Check with all ones
        for key in self.dhp.regs.iteritems():
            if ":S" in key:
                if key in ["tdo_tx_set_06:S", "tdo_tx_set_12:S", "tdo_tx_set_30:S", "dcd_invert_TRST_polarity:S",
                           "dcd_invert_TCK_polarity:S"]:
                    pass
                else:
                    self.dhp.regs[key] = 0
            else:
                if key in ["pll_des_clk_sel:VALUE", "IDAC_LVDS_RX_IREF:VALUE", "IDAC_LVDS_TX_IREF:VALUE",
                           "IDAC_PLL_I50U:VALUE", "IDAC_PLL_ICP:VALUE", \
                           "IDAC_PLL_IVCO:VALUE", "IREF_TRIMMING:VALUE"]:
                    pass
                else:
                    self.dhp.regs[key] = 0

        self.dhp.write_core()
        self.dhp.write_global()
        self.dhp.write_core()
        self.dhp.write_global()
        time.sleep(0.5)
        self.dhp.read_core()
        self.dhp.read_global()
        time.sleep(0.5)

        for key in self.dhp.regs.iteritems():
            if ":S" in key:
                if key in ["tdo_tx_set_06:S","tdo_tx_set_12:S","tdo_tx_set_30:S","dcd_invert_TRST_polarity:S","dcd_invert_TCK_polarity:S"]:
                    pass
                else:
                    if self.dhp.regs[key] != 0:
                        jtag_ok = False
            else:
                if key in ["pll_des_clk_sel:VALUE","IDAC_LVDS_RX_IREF:VALUE","IDAC_LVDS_TX_IREF:VALUE","IDAC_PLL_I50U:VALUE","IDAC_PLL_ICP:VALUE", \
                           "IDAC_PLL_IVCO:VALUE", "IREF_TRIMMING:VALUE"]:
                    pass
                else:
                    if "1" in bin(self.dhp.regs[key])[1:]:
                        jtag_ok = False
        stop = time.time()

        if jtag_ok:
            cmd = "JTAG - test #2 passed after %d sec" % (stop - start)
            return True, cmd
        else:
            cmd = "ERROR: JTAG - test #2 failed after %d sec" % (stop - start)
            return False, cmd
    
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
        #logging.info("%s\tPower; Power Consumption Test",__name__)
        ivdd = self.get_VDD_current()
        idvdd = self.get_DVDD_current()
        
        
        if (ivdd>0.110) and (ivdd<0.150) and (idvdd>0.030) and (idvdd<0.060):
            return True, "Power - power test passed: VDD %smV(%smA) and DVDD %smV(%smA)"%(self.vdd, ivdd, self.dvdd, idvdd)
        else:
            return False, "ERROR: Power - power test failed: VDD %smV(%smA) and DVDD %smV(%smA)"%(self.vdd, ivdd, self.dvdd, idvdd)
            
    def test_jtag(self):
        crst = get_pv(self.dhePrefix+":dhpt_crst:S:set")
        reinJTAG = get_pv(self.dhePrefix+":jtag_reinit_chain:S:set")
        if not get_pv(self.dhePrefix+":jtag_chain_initialized:S:cur").get():
            crst.put(0)
            crst.put(1)
            logging.info("%s\tCRESETB; Reset JTAG registers in DHPT", __name__)
            reinJTAG.put(1)
            logging.info("%s\tReinitalized JTAG chain",__name__)

        return self.turn_all_regs_on() and self.turn_all_regs_off()



    def test_pedestal_memory(self):
        from struct import unpack
        number_of_gates=1024
        start = time.time()
        pedestals = np.random.randint(low=0, high=255, size=number_of_gates*256).reshape(
            (4 * number_of_gates,64))
        upload_utils.upload_frame_data(dheprefix=self.dhePrefix, asicpair=1, dataFrame=pedestals, address_offset=0, verbose=True)

        pedestals_recorded = np.zeros((4 * number_of_gates,64))
        for blk in range(16):
            get_pv(self.dhePrefix, "D1:memaddr:VALUE").put(blk << 10)
            time.sleep(0.05)
            for addr_id in range(1024):
                get_pv(self.dhePrefix, "D1:memdata_dispatch:trg:cur").put(1)
                time.sleep(0.1)
                pedestals_recorded[addr_id * 4:(addr_id + 1) * 4, blk * 4 + 0] = np.array(unpack('4B'. np.uint32(get_pv(self.dhePrefix, "D1:memdata0:VALUE").get())))
                pedestals_recorded[addr_id * 4:(addr_id + 1) * 4, blk * 4 + 1] = np.array(unpack('4B'. np.uint32(get_pv(self.dhePrefix, "D1:memdata1:VALUE").get())))
                pedestals_recorded[addr_id * 4:(addr_id + 1) * 4, blk * 4 + 2] = np.array(unpack('4B'. np.uint32(get_pv(self.dhePrefix, "D1:memdata2:VALUE").get())))
                pedestals_recorded[addr_id * 4:(addr_id + 1) * 4, blk * 4 + 3] = np.array(unpack('4B'. np.uint32(get_pv(self.dhePrefix, "D1:memdata3:VALUE").get())))


        mem_ped = pedestals_recorded == pedestals
        stop = time.time()

        if mem_ped:
            cmd = "I/O - pedestal memory test passed after %d sec" % (stop - start)
            return True, cmd
        else:
            cmd = "ERROR: I/O - pedestal memory test failed after %d sec" % (stop - start)
            return False, cmd

    def test_offset_memory(self):
        from struct import unpack
        number_of_gates=256
        start = time.time()
        offset_frame = np.random.randint(low=0, high=3, size=64 * 4 * number_of_gates).reshape(
            (64, 4 * number_of_gates))
        offset_lin = mapping.matrixToOffsetUpload(data_in=offset_frame, memIndex=0, shift=0)
        upload_utils.upload_offsets(data=offset_lin, index=1, start_address=0, asic="DHPT", dheprefix=self.dhePrefix)

        offset_recorded = np.zeros((4 * number_of_gates, 64))
        for blk in range(16):
            get_pv(self.dhePrefix, "D1:memoffsetaddr:VALUE").put(blk << 10)
            time.sleep(0.05)
            for addr_id in range(1024):
                get_pv(self.dhePrefix, "D1:memoffsetdata_dispatch:trg:cur").put(1)
                time.sleep(0.1)
                offset_recorded[addr_id * 4:(addr_id + 1) * 4, blk * 4 + 0] = np.array(unpack('4B'.np.uint32(get_pv(self.dhePrefix, "D1:memoffsetdata0:VALUE").get())))
                offset_recorded[addr_id * 4:(addr_id + 1) * 4, blk * 4 + 1] = np.array(unpack('4B'.np.uint32(get_pv(self.dhePrefix, "D1:memoffsetdata1:VALUE").get())))
                offset_recorded[addr_id * 4:(addr_id + 1) * 4, blk * 4 + 2] = np.array(unpack('4B'.np.uint32(get_pv(self.dhePrefix, "D1:memoffsetdata2:VALUE").get())))
                offset_recorded[addr_id * 4:(addr_id + 1) * 4, blk * 4 + 3] = np.array(unpack('4B'.np.uint32(get_pv(self.dhePrefix, "D1:memoffsetdata3:VALUE").get())))

        mem_ped = offset_recorded == offset_frame.T
        stop = time.time()

        if mem_off:
            cmd = "I/O - offset memory test passed after %d sec" % (stop - start)
            return True, cmd
        else:
            cmd = "ERROR: I/O - offset memory test failed after %d sec" % (stop - start)
            return False, cmd

    def test_switcher_memory(self):
        number_of_gates=256
        start = time.time()
        switcher_normal_data = np.random.randint(low=0, high=1, size=32 * 4 * number_of_gates).reshape(
            (number_of_gates, 4, 32))
        switcher_gated_data = np.random.randint(low=0, high=1, size=32 * 4 * number_of_gates).reshape(
            (number_of_gates, 4, 32))
        upload_utils.upload_switcher_sequence(dheprefix=self.dhePrefix, asicpair=1, data=switcher_normal_data,
                                              sequence="main")
        upload_utils.upload_switcher_sequence(dheprefix=self.dhePrefix, asicpair=1, data=switcher_gated_data,
                                              sequence="gated")

        # TODO: READ AND CHECK
        mem_sw = True
        stop = time.time()

        if mem_sw:
            cmd = "I/O - switcher memory test passed after %d sec" % (stop - start)
            return True, cmd
        else:
            cmd = "ERROR: I/O - switcher memory test failed after %d sec" % (stop - start)
            return False, cmd


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
                get_pv(self.dhePrefix, "D1:memdata0:VALUE").put(pat)
                get_pv(self.dhePrefix, "D1:memdata1:VALUE").put(pat)
                get_pv(self.dhePrefix, "D1:memdata2:VALUE").put(pat)
                get_pv(self.dhePrefix, "D1:memdata3:VALUE").put(pat)
                for blk in range(16):
                    #logging.info("MEM; use pattern %x"%pat)
                    #logging.info("Pattern %x"%pat)
                    get_pv(self.dhePrefix, "D1:memaddr:VALUE").put(blk << 10)
                    time.sleep(0.05)
                    for addr_id in range(1024):
                        get_pv(self.dhePrefix, "D1:memdata:trg:set").put(1)
                        time.sleep(0.05)
                        
                for blk in range(16):
                    get_pv(self.dhePrefix, "D1:memaddr:VALUE").put(blk << 10)
                    time.sleep(0.05)
                    for addr_id in range(1024):
                        get_pv(self.dhePrefix, "D1:memdata_dispatch:trg:cur").put(1)
                        time.sleep(0.1)
                        mem0 = np.uint32(get_pv(self.dhePrefix, "D1:memdata0:VALUE").get())
                        mem1 = np.uint32(get_pv(self.dhePrefix, "D1:memdata1:VALUE").get())
                        mem2 = np.uint32(get_pv(self.dhePrefix, "D1:memdata2:VALUE").get())
                        mem3 = np.uint32(get_pv(self.dhePrefix, "D1:memdata3:VALUE").get())
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
                get_pv(self.dhePrefix, "D1:memoffsetdata0:VALUE").put(pat)
                get_pv(self.dhePrefix, "D1:memoffsetdata1:VALUE").put(pat)
                get_pv(self.dhePrefix, "D1:memoffsetdata2:VALUE").put(pat)
                get_pv(self.dhePrefix, "D1:memoffsetdata3:VALUE").put(pat)
                #logging.info("MEM; use pattern %x"%pat)
                #logging.info("Pattern %x"%pat)
                get_pv(self.dhePrefix, "D1:memoffsetaddr:VALUE").put(0)
                time.sleep(0.05)
                for addr_id in range(1024):
                    get_pv(self.dhePrefix, "D1:memoffsetdata:trg:set").put(1)
                    time.sleep(0.05)

                get_pv(self.dhePrefix, "D1:memoffsetaddr:VALUE").put(0)
                time.sleep(0.05)
                for addr_id in range(1024):
                    get_pv(self.dhePrefix, "D1:memoffsetdata_dispatch:trg:cur").put(1)
                    time.sleep(0.1)
                    mem0 = np.uint32(get_pv(self.dhePrefix, "D1:memoffsetdata0:VALUE").get())
                    mem1 = np.uint32(get_pv(self.dhePrefix, "D1:memoffsetdata1:VALUE").get())
                    mem2 = np.uint32(get_pv(self.dhePrefix, "D1:memoffsetdata2:VALUE").get())
                    mem3 = np.uint32(get_pv(self.dhePrefix, "D1:memoffsetdata3:VALUE").get())
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
                get_pv(self.dhePrefix, "D1:memswdata0:VALUE").put(pat)
                get_pv(self.dhePrefix, "D1:memswdata1:VALUE").put(pat)
                get_pv(self.dhePrefix, "D1:memswdata2:VALUE").put(pat)
                get_pv(self.dhePrefix, "D1:memswdata3:VALUE").put(pat)
                for blk in range(16):
                    #logging.info("MEM; use pattern %x"%pat)
                    #logging.info("Pattern %x"%pat)
                    get_pv(self.dhePrefix, "D1:memswaddr:VALUE").put(0)
                    time.sleep(0.05)
                    for addr_id in range(1024):
                        get_pv(self.dhePrefix, "D1:memswdata:trg:set").put(1)
                        time.sleep(0.05)
                        
                for blk in range(16):
                    get_pv(self.dhePrefix, "D1:memswaddr:VALUE").put(0)
                    time.sleep(0.05)
                    for addr_id in range(1024):
                        get_pv(self.dhePrefix, "D1:memswdata_dispatch:trg:cur").put(1)
                        time.sleep(0.1)
                        mem0 = np.uint32(get_pv(self.dhePrefix, "D1:memswdata0:VALUE").get())
                        mem1 = np.uint32(get_pv(self.dhePrefix, "D1:memswdata1:VALUE").get())
                        mem2 = np.uint32(get_pv(self.dhePrefix, "D1:memswdata2:VALUE").get())
                        mem3 = np.uint32(get_pv(self.dhePrefix, "D1:memswdata3:VALUE").get())
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

    def analyze_data(self, refData, dataToAnalyze, isRaw=True):
        if isRaw:
            if np.all(refData==dataToAnalyze):
                return True

    def test_dcd_to_dhp_data(self, number_of_gates):
        start = time.time()
        # Every gate has the same 256bytes-random data
        testpattern = PROBECARD.send_random_pattern_to_dhpt(number_of_gates)
        filename = self.fileDir + "data"

        data = daq.record_memorydump(1, framenr=1, dhePrefix=self.dhePrefix)
        dcdData = self.analyze_data(testpattern, data)

        stop = time.time()

        if dcdData:
            cmd = "I/O - DCD-DHPT data test passed after %d sec" %(stop - start)
            return True, cmd
        else:
            cmd = "ERROR: I/O - DCD-DHPT data test failed after %d sec" % (stop - start)
            return False, cmd

    def test_dhp_to_dcd_offset_data(self, number_of_gates):
        start = time.time()
        offset_frame = np.random.randint(low=0, high=3, size=64 * 4 * number_of_gates).reshape(
            (64, 4 * number_of_gates))
        offset_lin = mapping.matrixToOffsetUpload(data_in=offset_frame, memIndex=0, shift=0)
        upload_utils.upload_offsets(data=offset_lin, index=1, start_address=0, asic="DHPT", dheprefix=self.dhePrefix)

        data = PROBECARD.get_offset_bits(number_of_gates)
        dcd_data = self.analyze_data(offset_frame, data)
        stop = time.time()

        if dcd_data:
            cmd = "I/O - DHP-DCD offset data test passed after %d sec" % (stop - start)
            return True, cmd
        else:
            cmd = "ERROR: I/O - DHP-DCD offset data test failed after %d sec" % (stop - start)
            return False, cmd

    def test_dhp_to_switcher_data_normal_and_gated_mode(self, number_of_gates):
        start = time.time()
        switcher_normal_data = np.random.randint(low=0, high=1, size=32 * 4 * number_of_gates).reshape(
            (number_of_gates, 4, 32))
        switcher_gated_data = np.random.randint(low=0, high=1, size=32 * 4 * number_of_gates).reshape(
            (number_of_gates, 4, 32))
        upload_utils.upload_switcher_sequence(dheprefix=self.dhePrefix, asicpair=1, data=switcher_normal_data, sequence="main")
        upload_utils.upload_switcher_sequence(dheprefix=self.dhePrefix, asicpair=1, data=switcher_gated_data, sequence="gated")
        sw_data_normal = PROBECARD.get_switcher_bits(number_of_gates)

        #TODO: ENABLE GATED MODE AND RECORD SW DATA
        sw_data_gated = PROBECARD.get_switcher_bits(number_of_gates)

        #TODO: DISABLE GATED MODE
        sw_data = self.analyze_data(switcher_normal_data, sw_data_normal) and self.analyze_data(switcher_gated_data, sw_data_gated)
        stop = time.time()

        if sw_data:
            cmd = "I/O - DHP-SW data test passed after %d sec" % (stop - start)
            return True, cmd
        else:
            cmd = "ERROR: I/O - DHP-SW data test failed after %d sec" % (stop - start)
            return False, cmd


    def test_high_speed_link(self, configpath):
        import configparser
        isHSOK = False
        '''
        Test High Speed Link Memory
        '''
        logging.info("HS; High Speed Link Test")
        start = time.time()
        os.system("/home/daq/lab_framework/calibrations/measure.py")
        os.system("/home/daq/lab_framework/calibrations/analysis.py")
        '''
        TODO: aurora_analyze return if link stable and best bias parameters
        '''
        config = configparser.ConfigParser(delimiters="=")
        config.read(os.path.join(configpath, "measure.ini"))
        user = config.get("general", "user")
        opt = np.load(os.path.join(configpath, "analysis.npy"))
        opt_dly = opt[pvname(user, self.dhePrefix, "D1", "pll_cml_dly_sel:VALUE:set")]
        opt_bias = opt[pvname(user, self.dhePrefix, "D1", "idac_cml_tx_bias:VALUE:set")]
        opt_biasd = opt[pvname(user, self.dhePrefix, "D1", "idac_cml_tx_biasd:VALUE:set")]

        #set optimal values
        self.dhp.regs['pll_cml_dly_sel:VALUE'] = opt_dly
        self.dhp.regs['idac_cml_tx_bias:VALUE'] = opt_bias
        self.dhp.regs['idac_cml_tx_biasd:VALUE'] = opt_biasd
        self.dhp.write_global()
        stop = time.time()

        if (opt_dly != 0) and (opt_bias != 0) and (opt_biasd != 0):
            cmd = "HS - CML parameter test passed after %d sec" % (stop - start)
            return True, cmd
        else:
            cmd = "ERROR: HS - CML parameter test failed after %d sec" % (stop - start)
            return False, cmd

    def test_zero_suppressed_data(self):
        from pyDepfetReader import FileReader
        from daq import dhh_daq, record_zpdata_dhe
        from tqdm import tqdm
        import operator
        from itertools import product
        from shutil import copyfile
        import os
        import errno
        import time
        start = time.time()
        def upload_pedestals(dhe, pedestals):
            for a in [1]:
                get_pv(dhe, "D%d:test_mode_en:S:set" % a).put(1)
                get_pv(dhe, "D%d:cm_correction_en:S:set" % a).put(0)
                get_pv(dhe, "D%d:pedestal_subtraction:S:set" % a).put(0)
                get_pv(dhe, "D%d:threshold:VALUE:set" % a).put(19)
                get_pv(dhe, "D%d:corereg:trg:set" % a).put(1)
                upload_utils.upload_pedestal_frame(dhe, a, pedestals, memIndex=0, verbose=True)
                upload_utils.upload_pedestal_frame(dhe, a, pedestals, memIndex=1, verbose=True)
                upload_utils.upload_data_frame(dhe, a, pedestals, memIndex=0, verbose=True)

        def checkEvent(RecEvent, dup):
            if len(dup) == 0 and len(recEvents) == 0:
                return True, None
            if len(RecEvent) == 0:
                return False, 'ERROR: Received no hits but expected some!'
            recFrameNrs = np.unique(RecEvent[:, 4])
            differenceOfFrameNumber = (RecEvent[-1, 4] - RecEvent[0, 4]) % (2 ** 16)  # - (recFrames[0]-x1)%overflow

            if differenceOfFrameNumber > 1:
                return False, 'ERROR: Difference of frame number: %d | Frame number: %s' % (
                differenceOfFrameNumber, recFrameNrs)
            else:
                assert 1 <= len(recFrameNrs) <= 2
                # Check content of frame one
                drec = {(e[1], e[0], e[2]) for e in RecEvent}
                # Check for monotonicity
                for frameNr in recFrameNrs:
                    linX = RecEvent[RecEvent[:, 4] == frameNr, 0] + 64 * RecEvent[RecEvent[:, 4] == frameNr, 1]
                    if not np.all(linX[1:] - linX[0:-1] > 0):
                        return False, 'ERROR: Received hits not in monotonic increasing order'

                # Check if doublicate hits are present
                if (len({(e[1], e[0]) for e in RecEvent}) - len(RecEvent)) != 0:
                    return False, 'ERROR: Duplicated hit in data stream!'
                # Check if all hits received
                if not drec == dup:
                    # print "got hits:",drec
                    # print "expected",dup
                    return False, 'ERROR: Missing hits or too many hits.'
                if len(recFrameNrs) == 2:
                    if RecEvent[0, 1] <= RecEvent[-1, 1]:
                        # print "strange event:"
                        # print RecEvent
                        # print RecEvent[0,1],"vs", RecEvent[-1,1]
                        return False, 'ERROR: First hit in first frame has lower row_id than the last hit of the second frame'
            return True, None

        dhe = self.dhePrefix
        path = "results"
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        print dhe

        '''
        SET UP FILEREADER
        '''
        reader = FileReader(-1, 0, dhe)
        reader.return_trigger = False
        reader.return_dhc_trigger = False
        reader.set_skip_raw(True)
        reader.set_return_subevent_number(True)
        reader.set_absolute_subevent_number(True)
        pedestals = np.zeros((64, 64), np.uint8)

        upload_pedestals(dhe=dhe, pedestals=pedestals)
        # max number of hits in a row+1, starting with the last row, Maximum: 8!
        l = [4, 3, 2, 1, 1]
        for x in l:
            assert x <= 9, "Too many hits in one row requested!"
        upper_hits_old = None
        totalErrors = 0
        notExpectedErrors = 0
        with open(os.path.join(path, "logfile.txt"), "w") as logfile:
            with dhh_daq(dheprefix=dhe, wait=0, quiet=True, connectOnly=True) as writer:
                '''
                GENERATE TESTPATTERN
                '''
                pbar = tqdm(product(*map(xrange, l)), total=reduce(operator.mul, l))
                for nr_per_row in pbar:
                    n_gates = ((len(l) - 1) / 4 + 1)
                    hits = np.zeros((n_gates * 4, 8), np.uint8)
                    hit_set = set()
                    setting_string = ",".join(map(str, nr_per_row))
                    pbar.set_description("Setting " + setting_string + " Errors:%3d" % totalErrors)
                    for row_from_last, n_row in enumerate(nr_per_row, start=1):
                        for col in range(n_row):
                            hits[-row_from_last, col] = 20 + (col * 3 + row_from_last * 7) % 200
                            hit_set.add((64 - row_from_last, 16 + col, 20 + (col * 3 + row_from_last * 7) % 200))
                    '''
                    UPLOAD TESTPATTERN
                    '''

                    if (upper_hits_old is None) or np.any(hits[:, 4:] != upper_hits_old):
                        # print "uploading other hits!", nr_per_row
                        upper_hits_old = np.copy(hits[:, 4:])
                        # print upper_hits_old
                        upload_utils.upload_memory_slice(dhe, 1, upper_hits_old, 5, start_gate=16 - n_gates, pedestal_mem=False,
                                            mem_index=0, verbose=False)
                        upload_utils.upload_memory_slice(dhe, 1, hits[:, :4], 4, start_gate=16 - n_gates, pedestal_mem=False,
                                        mem_index=0, verbose=False)
                    time.sleep(0.04)
                    '''
                    TRIGGER DATA
                    '''
                    filenm = os.path.join(path, "temp.dat")
                    record_zpdata_dhe(dhePrefix=dhe, art_trigger_freq=1000, filename=filenm, nr_art_triggers=40,
                                      daq_instance=writer, verbose=False)
                    '''
                    CHECK RECEIVED DATA
                    '''
                    reader.open(filenm)

                    for [recEvents] in reader:
                        is_ok, msg = checkEvent(recEvents, hit_set)
                        if not is_ok:
                            totalErrors += 1
                            if setting_string.split(",")[1] == 2:
                                notExpectedErrors += 1
                            newName = os.path.join(path, "bad" + setting_string + ".dat")
                            copyfile(filenm, newName)
                            logfile.write("Setting %s Bad. Reason: '%s'. File %s\n" % (setting_string, msg, newName))
                            break
                    else:
                        logfile.write("Setting %s OK\n" % (setting_string))
                    logfile.flush()

        '''
        LOG TEST
        '''
        stop = time.time()
        if notExpectedErrors == 0:
            cmd = "ZS - zero suppression test passed after %d sec" % (stop - start)
            return True, cmd
        else:
            cmd = "ERROR: ZS - zero suppression test failed after %d sec" % (stop - start)
            return False, cmd



    def CML_iv_curve(self):
        from argparse import ArgumentParser
        import configparser
        import epics_utils
        import time
        import numpy as np
        import os
        from daq import folder_for_data
        import shutil
        import matplotlib.pyplot as pl
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
        import time
        import numpy as np
        import os
        from daq import folder_for_data
        import shutil
        import matplotlib.pyplot as pl
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
        
        