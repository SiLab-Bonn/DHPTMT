#################################################
#################################################
#################################################
#################################################

#       Slow Control:                           #
#       pyEpics related classes and methods     #

#################################################
#################################################
#################################################
from epics import PV

from time import sleep
from matplotlib.backends.backend_pdf import Stream
from _struct import unpack, pack
import numpy as np

import time
from misc import query_dict
import logging

class REGISTER():
    def __init__(self, name, size=1, value=0):
        self._name      = name
        self._size      = size
        
    @property
    def name(self):
        return self._name
    
    @property
    def size(self):
        return self._size
        
        
class PROCESS_VAR_JTAG():
    #jtag_reg_name (e.g. corereg, gobalreg, etc.)
    #functional_reg (e.g. sw_gate_sdly, dcd_jtag_en_out, etc.)
    def __init__(self, dhpt_id, functional_reg, isPv=True):
        self._func_reg_name  = functional_reg.name 
        self._func_reg_size  = functional_reg.size
        self._id = dhpt_id
        #print "PXD:H1031:D" + str(dhpt_id) + ":" + self._func_reg_name + ":VALUE:set"
        if isPv:
            if self._func_reg_name == "chip_id":
                self._setVal     = PV("PXD:H1032:D" + str(dhpt_id) + ":" + self._func_reg_name + ":ID:set")       #Value to be
                self._getVal     = PV("PXD:H1032:D" + str(dhpt_id) + ":" + self._func_reg_name + ":ID:cur")       #Value as is    
            else:
                if self._func_reg_size == 1:
                    self._setVal     = PV("PXD:H1032:D" + str(dhpt_id) + ":" + self._func_reg_name + ":S:set")       #Value to be
                    self._getVal     = PV("PXD:H1032:D" + str(dhpt_id) + ":" + self._func_reg_name + ":S:cur")       #Value as is    
                else:
                    self._setVal     = PV("PXD:H1032:D" + str(dhpt_id) + ":" + self._func_reg_name + ":VALUE:set")       #Value to be
                    self._getVal     = PV("PXD:H1032:D" + str(dhpt_id) + ":" + self._func_reg_name + ":VALUE:cur")       #Value as is    
        else:
            self._setVal     = PV("PXD:H1032:D" + str(dhpt_id) + ":" + self._func_reg_name + ":trg:set")       #Value to be
            self._getVal     = PV("PXD:H1032:D" + str(dhpt_id) + ":" + self._func_reg_name + "_dispatch:trg:cur")       #Value as is   
            
    #set and get pv value        
    ############################
    def set_value(self, val=0):
        self.pvSet.put(val)
        
    def get_value(self):
        self.pvGet.get()
    ############################
        
    @property
    def name(self):
        return self._func_reg_name
    
    @property
    def size(self):
        return self._func_reg_size
    
    @property
    def pvSet(self):
        return self._setVal
    
    @property
    def pvGet(self):
        return self._getVal
     
    
class JTAG_REGS():
    def __init__(self, dhpt_id=1):
        self.MEMORY_REGISTERS = {
                                "PEDESTAL" : { 
                                    "pv" : {
                                              "addr" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memaddr",-1)),
                                              "mem0" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memdata0", 32)),
                                              "mem1" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memdata1", 32)),
                                              "mem2" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memdata2", 32)),
                                              "mem3" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memdata3", 32))
                                              },
                                    "dispatch"  :   PROCESS_VAR_JTAG(dhpt_id , REGISTER("memdata",16), False),
                                            },
                                
                                "OFFSET" : { 
                                    "pv" : {
                                              "addr" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memoffsetaddr",-1)),
                                              "mem0" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memoffsetdata0", 32)),
                                              "mem1" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memoffsetdata1", 32)),
                                              "mem2" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memoffsetdata2", 32)),
                                              "mem3" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memoffsetdata3", 32))
                                              },
                                    "dispatch" :   PROCESS_VAR_JTAG(dhpt_id , REGISTER("memoffsetdata",8), False),
                                            },
                                 
                                "SWITCHER" : { 
                                    "pv" : {
                                              "addr" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memswaddr",-1)),
                                              "mem0" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memswdata0", 32)),
                                              "mem1" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memswdata1", 32)),
                                              "mem2" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memswdata2", 32)),
                                              "mem3" :      PROCESS_VAR_JTAG(dhpt_id , REGISTER("memswdata3", 32))
                                              },
                                    "dispatch" :   PROCESS_VAR_JTAG(dhpt_id , REGISTER("memswdata",-1), False)
                                            }
                                 }
        
        self.JTAG_REGISTERS =  {    
                                "GLOBAL" : {
                                    "pv" : {                                        
                                            #"clk_dly"                   : PROCESS_VAR_JTAG(dhpt_id , REGISTER("clk_dly",                    5)),
                                            #"frame_sync_dly"            : PROCESS_VAR_JTAG(dhpt_id , REGISTER("frame_sync_dly",             5)),
                                            #"row2_sync_dly"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("row2_sync_dly")),
                                            
                                            #NOT USED IN DHPT 1.0
                                            #"offset_dly"                : (("LINK_%s"%lnk : ("DLY_%s"%dly : PROCESS_VAR_JTAG(dhpt_id , "globalreg" , REGISTER("offset_dly",5))) for dly in range(2)) for lnk in range(8)) 
                                            #"offset_dly"                : 8*[2*[PROCESS_VAR_JTAG(dhpt_id , "globalreg" , REGISTER("offset_dly",           5))]],
                                            #"sw_clk_dly"                : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_clk_dly",                 5)),
                                            #"sw_clear_dly"              : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_clear_dly",               5)),
                                            #"sw_gate_dly"               : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_gate_dly",                5)),
                                            #"sw_new_frame_dly"          : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_new_frame_dly",           5)),
                                            #"pll_out_sel"               : PROCESS_VAR_JTAG(dhpt_id , REGISTER("pll_out_sel",                4)),
                                            #"tx_sel_clk"                : PROCESS_VAR_JTAG(dhpt_id , REGISTER("tx_sel_clk")),
                                            "pll_en_out"                : PROCESS_VAR_JTAG(dhpt_id , REGISTER("pll_en_out")),
                                            "top_ub_en_out"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("top_ub_en_out")),
                                            "offset_en_out"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("offset_en_out")),
                                            "sw_en_out"                 : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_en_out")),
                                            
                                            
                                            "sw_tx_set06"               : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_tx_set06")),
                                            "sw_tx_set12"               : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_tx_set12")),
                                            "sw_tx_set30"               : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_tx_set30")),
                                            
                                            "sw_clear_sdly"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_clear_sdly",              4)),
                                            "sw_gate_sdly"              : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_gate_sdly",               4)),
                                            "sw_clk_sdly"               : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_clk_sdly",                4)),
                                            "sw_frame_sdly"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_frame_sdly",              4)),   
                                            
                                            "tdo_tx_set06"              : PROCESS_VAR_JTAG(dhpt_id , REGISTER("tdo_tx_set06")),
                                            "tdo_tx_set12"              : PROCESS_VAR_JTAG(dhpt_id , REGISTER("tdo_tx_set12")),
                                            "tdo_tx_set30"              : PROCESS_VAR_JTAG(dhpt_id , REGISTER("tdo_tx_set30")),
                                            "tdo_sdly"                  : PROCESS_VAR_JTAG(dhpt_id , REGISTER("tdo_sdly",                   4)),
                                            "dcd_jtag_en_out"           : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_jtag_en_out")),
                                            
                                             #logic dcd_sync_en_out
                                            "dcd_sync_en_clk"           : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_sync_en_clk")),
                                            "dcd_sync_en_diff_clk"      : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_sync_en_diff_clk")),
                                            "dcd_sync_en_row_sync"      : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_sync_en_row_sync")),
                                            "dcd_sync_en_frame_sync"    : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_sync_en_frame_sync")),
                                            
                                            "dcd_invert_TRST_polarity"  : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_sync_en_frame_sync")),
                                            "dcd_invert_TCK_polarity"   : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_invert_TRST_polarity")),
                                           
                                            "dcd_cmos_clk_dly"          : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_invert_TCK_polarity",    4)),
                                            "dcd_row2_syn_dly"          : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_row2_syn_dly",           4)),
                                            "frame_sync_dcd_dly"        : PROCESS_VAR_JTAG(dhpt_id , REGISTER("frame_sync_dcd_dly",         4)),
                                            
                                           
                                            "dcd_clk_set06"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_clk_set06")),
                                            "dcd_clk_set12"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_clk_set12")),
                                            "dcd_clk_set30"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_clk_set30")),      
                                            "dcd_clk_sdly"              : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_clk_sdly",               4)),
                                            
                                            "dcd_rx_sdly"               : dict(("LINK_%02d"%lnk, PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_rx_sdly_%02d"%lnk,4))) for lnk in range(64)), 
                                            #"dcd_rx_sdly"               : 64*[PROCESS_VAR_JTAG(dhpt_id , REGISTER("dcd_rx_sdly",            4))],
                                            "offset_dcd_dly"            : dict(("LINK_%02d"%lnk, PROCESS_VAR_JTAG(dhpt_id , REGISTER("offset_dcd_dly_%02d"%lnk,4))) for lnk in range(16)), 
                                            #"offset_dcd_dly"            : 16*[PROCESS_VAR_JTAG(dhpt_id , REGISTER("offset_dcd_dly",         4))],
                                            
                                            "pll_ser_clk_dly"           : PROCESS_VAR_JTAG(dhpt_id , REGISTER("pll_ser_clk_dly",            4)),
                                            "pll_ser_clk_sel"           : PROCESS_VAR_JTAG(dhpt_id , REGISTER("pll_ser_clk_sel")),
                                            "pll_des_clk_sel"           : PROCESS_VAR_JTAG(dhpt_id , REGISTER("pll_des_clk_sel",            2)),
                                            "pll_cml_out_sel"           : PROCESS_VAR_JTAG(dhpt_id , REGISTER("pll_cml_out_sel",            2)),
                                            "pll_cml_dly_sel"           : PROCESS_VAR_JTAG(dhpt_id , REGISTER("pll_cml_dly_sel",            2)),
                                            "ser_lfsr_rb"               : PROCESS_VAR_JTAG(dhpt_id , REGISTER("ser_lfsr_rb")),
                                            
                                            "IDAC_CML_TX_BIAS"          : PROCESS_VAR_JTAG(dhpt_id , REGISTER("idac_cml_tx_bias",           8)),
                                            "IDAC_CML_TX_BIASD"         : PROCESS_VAR_JTAG(dhpt_id , REGISTER("idac_cml_tx_biasd",          8)),
                                            "IDAC_CML_TX_IBIASDELAY"    : PROCESS_VAR_JTAG(dhpt_id , REGISTER("idac_cml_tx_ibiasdelay",     8)),
                                            "IDAC_DCD_RX_IREF"          : PROCESS_VAR_JTAG(dhpt_id , REGISTER("idac_dcd_rx_iref",           8)),
                                            "IDAC_DIODE"                : PROCESS_VAR_JTAG(dhpt_id , REGISTER("idac_diode",                 8)),
                                            "IDAC_LVDS_RX_IREF"         : PROCESS_VAR_JTAG(dhpt_id , REGISTER("idac_lvds_rx_iref",          8)),
                                            "IDAC_LVDS_TX_IREF"         : PROCESS_VAR_JTAG(dhpt_id , REGISTER("idac_lvds_tx_iref",          8)),
                                            "IDAC_PLL_I50U"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("idac_pll_i50u",              8)),
                                            "IDAC_PLL_ICP"              : PROCESS_VAR_JTAG(dhpt_id , REGISTER("idac_pll_icp",               8)),
                                            "IDAC_PLL_IVCO"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("idac_pll_ivco",              8)),
                                            "IDAC_TEST"                 : PROCESS_VAR_JTAG(dhpt_id , REGISTER("idac_test",                  8)),
                                            "IREF_TRIMMING"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("iref_trimming",              4))
                                            }, 
                                    "dispatch" : PROCESS_VAR_JTAG(dhpt_id , REGISTER("globalreg",-1), False)},
        
                                "CORE" : {   
                                    "pv" : {
                                            "chip_id"                       : PROCESS_VAR_JTAG(dhpt_id , REGISTER("chip_id",                        8)),
                                            "latency"                       : PROCESS_VAR_JTAG(dhpt_id , REGISTER("latency",                       10)),
                                            "last_row"                      : PROCESS_VAR_JTAG(dhpt_id , REGISTER("last_row",                      10)),
                                            "last_row_dump"                 : PROCESS_VAR_JTAG(dhpt_id , REGISTER("last_row_dump",                 10)),
                                    
                                            #signal management
                                            "frame_sync_proc_dly"           : PROCESS_VAR_JTAG(dhpt_id , REGISTER("frame_sync_proc_dly",           13)),
                                            "row2_sync_dcd_clk_dly"         : PROCESS_VAR_JTAG(dhpt_id , REGISTER("row2_sync_dcd_clk_dly",          7)),
                                            "sw_last_row"                   : PROCESS_VAR_JTAG(dhpt_id , REGISTER("sw_last_row",                    8)),
                                            
                                            #input stage
                                            "invert_input_values"           : PROCESS_VAR_JTAG(dhpt_id , REGISTER("invert_input_values")),
                                            "disable_memory"                : PROCESS_VAR_JTAG(dhpt_id , REGISTER("disable_memory",                4)),
                                            "pedestal_subtraction"          : PROCESS_VAR_JTAG(dhpt_id , REGISTER("pedestal_subtraction")),
                                            "pedestal_offset"               : PROCESS_VAR_JTAG(dhpt_id , REGISTER("pedestal_offset",                8)),
                                            "active_ped_mem"                : PROCESS_VAR_JTAG(dhpt_id , REGISTER("active_ped_mem")),        
                                            "test_mode_en"                  : PROCESS_VAR_JTAG(dhpt_id , REGISTER("test_mode_en")),        
                                            
                                            #common mode correction related
                                            "cm_correction_en"     : PROCESS_VAR_JTAG(dhpt_id , REGISTER("cm_correction_en")),
                                            "cm_use_dcd_chan_mask" : PROCESS_VAR_JTAG(dhpt_id , REGISTER("cm_use_dcd_chan_mask")),
                                            "cm_use_overflow_bit"  : PROCESS_VAR_JTAG(dhpt_id , REGISTER("cm_use_overflow_bit")),
                                            "cm_offset"                     : PROCESS_VAR_JTAG(dhpt_id , REGISTER("cm_offset",                      8)),
                                            "threshold"                      : PROCESS_VAR_JTAG(dhpt_id , REGISTER("threshold",                       8)),        
                                            
                                            #dcd offest correction related
                                            "offset_mem_disable"            : PROCESS_VAR_JTAG(dhpt_id , REGISTER("offset_mem_disable",                   2)),        
                                            "offset_frame_sync_dly"         : PROCESS_VAR_JTAG(dhpt_id , REGISTER("offset_frame_sync_dly",         11)),
                                            "offset_des_dly"                : PROCESS_VAR_JTAG(dhpt_id , REGISTER("offset_des_dly",                 4)),
                                            "offset_mem_active"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("offset_mem_active")),
                                            "rand_gen_on_out_fifo"          : PROCESS_VAR_JTAG(dhpt_id , REGISTER("rand_gen_on_out_fifo")),
                                            "trig_cont_en"                  : PROCESS_VAR_JTAG(dhpt_id , REGISTER("trig_cont_en"))
                                            }, 
                                    "dispatch" : PROCESS_VAR_JTAG(dhpt_id , REGISTER("corereg",-1), False)},
        
                                "CORE READBACK" : {   
                                    "pv" : {
                                            "eoc_lost"            : PROCESS_VAR_JTAG(dhpt_id , REGISTER("eoc_lost",            32)),        
                                            "mem_errors"          : dict(("NUM_%s"%lnk, PROCESS_VAR_JTAG(dhpt_id , REGISTER("mem_errors_%02d"%lnk,8))) for lnk in range(32)),
                                            #"mem_errors"          : 32*[PROCESS_VAR_JTAG(dhpt_id , REGISTER("mem_errors",       8))],
                                            "offset_mem_errors"   : dict(("NUM_%s"%lnk, PROCESS_VAR_JTAG(dhpt_id , REGISTER("offset_mem_errors_%d"%lnk,8))) for lnk in range(4)),
                                            #"offset_mem_errors"   : 4*[PROCESS_VAR_JTAG(dhpt_id , REGISTER("offset_mem_errors", 8))],                 
                                            "seq_mem_errors"      : dict(("NUM_%s"%lnk, PROCESS_VAR_JTAG(dhpt_id , REGISTER("seq_mem_errors_%d"%lnk,8))) for lnk in range(2)),
                                            #"seq_mem_errors"      : 2*[PROCESS_VAR_JTAG(dhpt_id , REGISTER("seq_mem_errors",    8))]
                                            }, 
                                    "dispatch" : PROCESS_VAR_JTAG(dhpt_id , REGISTER("corerbreg",-1), False)},
        
                                "ADC" : {   
                                    "pv" : {
                                            "refClk"        : PROCESS_VAR_JTAG(dhpt_id , REGISTER("refClk",            10)),        
                                            "enableClkDiv"  : PROCESS_VAR_JTAG(dhpt_id , REGISTER("enableClkDiv")),
                                            "loadClkDiv"    : PROCESS_VAR_JTAG(dhpt_id , REGISTER("loadClkDiv")),
                                            "dataValid"     : PROCESS_VAR_JTAG(dhpt_id , REGISTER("dataValid")),
                                            "loadData"      : PROCESS_VAR_JTAG(dhpt_id , REGISTER("loadData")),
                                            "rst_n"         : PROCESS_VAR_JTAG(dhpt_id , REGISTER("rst_n")),
                                            "start"         : PROCESS_VAR_JTAG(dhpt_id , REGISTER("start")),
                                            "downValue"     : PROCESS_VAR_JTAG(dhpt_id , REGISTER("downValue",         16)),
                                            "upValue"       : PROCESS_VAR_JTAG(dhpt_id , REGISTER("upValue",           16)),
                                            "loadRatio"     : PROCESS_VAR_JTAG(dhpt_id , REGISTER("loadRatio")),
                                            "rRatio"        : PROCESS_VAR_JTAG(dhpt_id , REGISTER("rRatio",             3)),                        
                                            "pRatio"        : PROCESS_VAR_JTAG(dhpt_id , REGISTER("pRatio",             2)),                        
                                            "vb"            : PROCESS_VAR_JTAG(dhpt_id , REGISTER("vb",                 6)),                        
                                            "vrp"           : PROCESS_VAR_JTAG(dhpt_id , REGISTER("vrp",                3)),                        
                                            "nbits"         : PROCESS_VAR_JTAG(dhpt_id , REGISTER("nbits",             4)),                        
                                            "gain"          : PROCESS_VAR_JTAG(dhpt_id , REGISTER("gain",              20)),                        
                                            "vcm"           : PROCESS_VAR_JTAG(dhpt_id , REGISTER("vcm",                8))
                                            }, 
                                    "dispatch" : PROCESS_VAR_JTAG(dhpt_id , REGISTER("jtagadcreg",-1), False)},
        
       
                                "OUT CONFIGURE" : {   
                                    "pv" : {
                                            "rand_gen_on"       : PROCESS_VAR_JTAG(dhpt_id , REGISTER("rand_gen_on")),                        
                                            "do_cc"             : PROCESS_VAR_JTAG(dhpt_id , REGISTER("do_cc")),                        
                                            "how_long_align"    : PROCESS_VAR_JTAG(dhpt_id , REGISTER("how_long_align", 10)),                        
                                            "double_out_bits"   : PROCESS_VAR_JTAG(dhpt_id , REGISTER("double_out_bits")),                        
                                            "reverse_bit_order" : PROCESS_VAR_JTAG(dhpt_id , REGISTER("reverse_bit_order")),
                                            },
                                    #DHH side -> belongs to corereg  
                                    "dispatch" : PROCESS_VAR_JTAG(dhpt_id , REGISTER("corereg",-1), False)     
                                }
            }
    def set_default(self):
        logging.info("JTAG; Load default settings")
        nested_dicts = ["dcd_rx_sdly","offset_dcd_dly","mem_errors","offset_mem_errors","seq_mem_errors"]
        excludedRegs = ["tdo_tx_set06, tdo_tx_set12, tdo_tx_set30", "pll_des_clk_sel", 
                        "IDAC_CML_TX_BIAS", "IDAC_CML_TX_BIASD", "IDAC_CML_TX_IBIASDELAY",
                        "IDAC_DCD_RX_IREF", "IDAC_LVDS_RX_IREF", "IDAC_LVDS_TX_IREF",
                        "IDAC_PLL_I50U", "IDAC_PLL_ICP", "IDAC_PLL_IVCO", "IREF_TRIMMING",
                        "chip_id", "last_row", "last_row_dump", "do_cc", "how_long_align",
                        "double_out_bts"]
        excludedBlocks = ["ADC", "CORE READBACK"]
        
        #GLOBAL_REG
        if self.JTAG_REGISTERS['GLOBAL']['pv']["tdo_tx_set06"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["tdo_tx_set06"].set_value(0)
        if self.JTAG_REGISTERS['GLOBAL']['pv']["tdo_tx_set12"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["tdo_tx_set12"].set_value(0)
        if self.JTAG_REGISTERS['GLOBAL']['pv']["tdo_tx_set30"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["tdo_tx_set30"].set_value(0)
           
        if self.JTAG_REGISTERS['GLOBAL']['pv']["pll_des_clk_sel"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["pll_des_clk_sel"].set_value(1)
        
        if self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_CML_TX_BIAS"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_CML_TX_BIAS"].set_value(255)
        if self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_CML_TX_BIASD"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_CML_TX_BIASD"].set_value(128)
        if self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_CML_TX_IBIASDELAY"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_CML_TX_IBIASDELAY"].set_value(50)
       
        if self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_DCD_RX_IREF"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_DCD_RX_IREF"].set_value(100)
       
        if self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_LVDS_RX_IREF"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_LVDS_RX_IREF"].set_value(100)
        if self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_LVDS_TX_IREF"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_LVDS_TX_IREF"].set_value(150)
       
        if self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_PLL_I50U"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_PLL_I50U"].set_value(40)
        if self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_PLL_ICP"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_PLL_ICP"].set_value(10)
        if self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_PLL_IVCO"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["IDAC_PLL_IVCO"].set_value(96)
        
        if self.JTAG_REGISTERS['GLOBAL']['pv']["IREF_TRIMMING"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["IREF_TRIMMING"].set_value(8)
        
        if self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_jtag_en_out"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_jtag_en_out"].set_value(0)
        
        if self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_sync_en_clk"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_sync_en_clk"].set_value(0)
            
        if self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_sync_en_diff_clk"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_sync_en_diff_clk"].set_value(0)    
        
        if self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_sync_en_frame_sync"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_sync_en_frame_sync"].set_value(0)
            
        if self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_sync_en_row_sync"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_sync_en_row_sync"].set_value(0)    
        
        if self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_clk_set06"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_clk_set06"].set_value(1)  
        
        if self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_clk_set12"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_clk_set12"].set_value(1)    
        
        if self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_clk_set30"].pvSet.connected:
            self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_clk_set30"].set_value(1)    
        
        #CORE_REG
        if self.JTAG_REGISTERS['CORE']['pv']["chip_id"].pvSet.connected:
            self.JTAG_REGISTERS['CORE']['pv']["chip_id"].set_value(0)
        if self.JTAG_REGISTERS['CORE']['pv']["last_row"].pvSet.connected:
            self.JTAG_REGISTERS['CORE']['pv']["last_row"].set_value(255)
        if self.JTAG_REGISTERS['CORE']['pv']["last_row_dump"].pvSet.connected:
            self.JTAG_REGISTERS['CORE']['pv']["last_row_dump"].set_value(255)
        if self.JTAG_REGISTERS['CORE']['pv']["frame_sync_proc_dly"].pvSet.connected:
            self.JTAG_REGISTERS['CORE']['pv']["frame_sync_proc_dly"].set_value(17)
        if self.JTAG_REGISTERS['CORE']['pv']["row2_sync_dcd_clk_dly"].pvSet.connected:
            self.JTAG_REGISTERS['CORE']['pv']["row2_sync_dcd_clk_dly"].set_value(4)
        if self.JTAG_REGISTERS['CORE']['pv']["sw_last_row"].pvSet.connected:
            self.JTAG_REGISTERS['CORE']['pv']["sw_last_row"].set_value(191)
        #FIXME Since do_cc breaks the link of the DHPT 1.1 -> never use it!!!!!!!
        #if self.JTAG_REGISTERS['OUT CONFIGURE']['pv']["do_cc"].pvSet.connected:
        #    self.JTAG_REGISTERS['OUT CONFIGURE']['pv']["do_cc"].set_value(1)
        if self.JTAG_REGISTERS['OUT CONFIGURE']['pv']["how_long_align"].pvSet.connected:
            self.JTAG_REGISTERS['OUT CONFIGURE']['pv']["how_long_align"].set_value(400)
        if self.JTAG_REGISTERS['OUT CONFIGURE']['pv']["double_out_bits"].pvSet.connected:
            self.JTAG_REGISTERS['OUT CONFIGURE']['pv']["double_out_bits"].set_value(0)
        
        for key in self.JTAG_REGISTERS:
            if key not in excludedBlocks:
                for pvname in self.JTAG_REGISTERS[key]['pv']:
                    pv = self.JTAG_REGISTERS[key]['pv'][pvname]    
                    if pvname in nested_dicts:
                        for v in query_dict(pv):
                            if v not in excludedRegs and v.pvSet.connected:
                                v.set_value(0)
                                time.sleep(0.01)
                                
        self.JTAG_REGISTERS['CORE']['dispatch'].set_value()
        self.JTAG_REGISTERS['GLOBAL']['dispatch'].set_value()   
        self.JTAG_REGISTERS['OUT CONFIGURE']['dispatch'].set_value()
        
    def dcd_delay(self,channel=0,dly=[0]*8):
        link_start = channel*8
        for lnk in range(8):
            self.JTAG_REGISTERS['GLOBAL']['pv']["dcd_rx_sdly"]["LINK_%02d"%(link_start+lnk)].set_value(dly[lnk])
        self.JTAG_REGISTERS['GLOBAL']['dispatch'].set_value() 
    
    def offset_delay(self,channel=0,dly=[0]*8):
        link_start = channel*8
        for lnk in range(8):
            self.JTAG_REGISTERS['GLOBAL']['pv']["offset_dcd_dly"]["LINK_%02d"%(link_start+lnk)].set_value(dly[lnk])
        self.JTAG_REGISTERS['GLOBAL']['dispatch'].set_value()     
        
        
class OFFSET_DAC_MAPPING():
    def __init__(self):
        self._intern_blk0_word_128bit = []
        self._intern_blk1_word_128bit = []
        #self._dac_dict = dict( ("Link%s"%ln : dict(("Bit%s"%ch : 0) for ch in range(32))) for ln in range(8))
    
    def load_yaml(self, yamlstr):
        self._dac_dict = yamlstr         
        
    def map_extern_dcd(self):
        self._intern_blk0_word_128bit = []
        self._intern_blk1_word_128bit = []
        for ch in range(32):
            for ln in range(8):
                self._intern_blk0_word_128bit.append(self._dac_dict["Link%s"%ln]["Bit%s"%ch] & 0x01)
                self._intern_blk1_word_128bit.append((self._dac_dict["Link%s"%ln]["Bit%s"%ch] & 0x02) >> 1)
        self._intern_blk0_word_128bit.reverse()
        self._intern_blk1_word_128bit.reverse()
        
    def get_mapping(self):
        return [self._intern_blk0_word_128bit,self._intern_blk1_word_128bit]
    
    def get_mapping_str(self):
        return ["".join(str(v) for v in self._intern_blk0_word_128bit), "".join(str(v) for v in self._intern_blk1_word_128bit)]  
    
    def map_2_16byte_word(self):
        self._intern_16byte_word = []
        for ch in range(32):
            for ln in range(8):
                self._intern_16byte_word.append(bin(self._dac_dict["Link%s"%ln]["Bit%s"%ch]))
        self._intern_16byte_word.reverse()
  
        
        
        packed_data = [self.bin_2_dec(self._intern_16byte_word[16*i:16*(i+1)]) for i in range(0,16)]
        return packed_data
    
    def bin_2_dec(self, lsBin16):
        val = 0
        if len(lsBin16) == 16:
            for i in range(0,16):
                val += lsBin16[i]*pow(2, 16-i-1)
        else: pass
        return val
        
    
        
        
