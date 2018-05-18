#from epics_utils import get_pv

def get_pv(a,b):
    print a+b

class Registers(dict):
    #def __init__(self, dhe, dhp):
    #    self._dheprefix = dhe
    #    self._dhpprefix = dhp

    def __getitem__(self, key):
        #if  get_pv("PXD:H1031:", "D%d:%s:cur" %(1,key)).connected:
        #    get_pv("PXD:H1031:", "D%d:%s:cur" %(1,key))#.get()
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        #get_pv("PXD:H1031:", "D%d:%s:set" %(1,key))#.put(value)
        print "PXD:H1031:D%d:%s:set" %(1,key), "=", value

class DHPregisters(object):
    def __init__(self):
        self.regs = Registers({
            #GLOBAL REGISTER
            #START
            #TEST PINS
            "pll_en_out:S":0,
            "top_ub_en_out:S":0,
            #IOs
            "offset_en_out:S":0,
            "sw_en_out:S":0,
            #SW bias for diff TX
            "sw_tx_set06:S":0,
            "sw_tx_set12:S":0,
            "sw_tx_set30:S":0,
            #JTAG bias for diff TX
            "tdo_tx_set06:S":0,
            "tdo_tx_set12:S":0,
            "tdo_tx_set30:S":0,
            #DCD_CLK bias for diff TX
            "dcd_clk_set06:S":0,
            "dcd_clk_set12:S":0,
            "dcd_clk_set30:S":0,
            #JTAG to DCD
            "dcd_jtag_en_out:S":0,
            "dcd_sync_en_clk:S":0,
            "dcd_sync_en_diff_clk:S":0,
            "dcd_sync_en_row_sync:S":0,
            "dcd_sync_en_frame_sync:S":0,
            "dcd_invert_TRST_polarity:S":0,
            "dcd_invert_TCK_polarity:S":0,
            "ser_lfsr_rb:S":0,
            "pll_ser_clk_sel:S":0,
            #Phase delay for SW diff signals
            "sw_clear_sdly:VALUE":0,
            "sw_gate_sdly:VALUE":0,
            "sw_clk_sdly:VALUE":0,
            "sw_frame_sdly:VALUE":0,
            "tdo_sdly:VALUE":0,
            "dcd_cmos_clk_dly:VALUE":0,
            "dcd_row2_syn_dly:VALUE":0,
            "frame_sync_dcd_dly:VALUE":0,
            "dcd_clk_sdly:VALUE":0,
            "pll_ser_clk_dly:VALUE":0,
            "pll_des_clk_sel:VALUE":0,
            "pll_cml_out_sel:VALUE":0,
            #BIAS
            "IDAC_CML_TX_BIAS:VALUE":0,
            "IDAC_CML_TX_BIASD:VALUE":0,
            "IDAC_CML_TX_IBIASDELAY:VALUE":0,
            "IDAC_DCD_RX_IREF:VALUE":0,
            "IDAC_DIODE:VALUE":0,
            "IDAC_LVDS_RX_IREF:VALUE":0,
            "IDAC_LVDS_TX_IREF:VALUE":0,
            "IDAC_PLL_I50U:VALUE":0,
            "IDAC_PLL_ICP:VALUE":0,
            "IDAC_PLL_IVCO:VALUE":0,
            "IDAC_TEST:VALUE":0,
            "IREF_TRIMMING:VALUE":0,
            #Phase delay for incoming data DCD->DHP
            "dcd_rx_sdly_00:VALUE":0,
            "dcd_rx_sdly_01:VALUE":0,
            "dcd_rx_sdly_02:VALUE":0,
            "dcd_rx_sdly_03:VALUE":0,
            "dcd_rx_sdly_04:VALUE":0,
            "dcd_rx_sdly_05:VALUE":0,
            "dcd_rx_sdly_06:VALUE":0,
            "dcd_rx_sdly_07:VALUE":0,
            "dcd_rx_sdly_08:VALUE":0,
            "dcd_rx_sdly_09:VALUE":0,
            "dcd_rx_sdly_10:VALUE":0,
            "dcd_rx_sdly_11:VALUE":0,
            "dcd_rx_sdly_12:VALUE":0,
            "dcd_rx_sdly_13:VALUE":0,
            "dcd_rx_sdly_14:VALUE":0,
            "dcd_rx_sdly_15:VALUE":0,
            "dcd_rx_sdly_16:VALUE":0,
            "dcd_rx_sdly_17:VALUE":0,
            "dcd_rx_sdly_18:VALUE":0,
            "dcd_rx_sdly_19:VALUE":0,
            "dcd_rx_sdly_20:VALUE":0,
            "dcd_rx_sdly_21:VALUE":0,
            "dcd_rx_sdly_22:VALUE":0,
            "dcd_rx_sdly_23:VALUE":0,
            "dcd_rx_sdly_24:VALUE":0,
            "dcd_rx_sdly_25:VALUE":0,
            "dcd_rx_sdly_26:VALUE":0,
            "dcd_rx_sdly_27:VALUE":0,
            "dcd_rx_sdly_28:VALUE":0,
            "dcd_rx_sdly_29:VALUE":0,
            "dcd_rx_sdly_30:VALUE":0,
            "dcd_rx_sdly_31:VALUE":0,
            "dcd_rx_sdly_32:VALUE":0,
            "dcd_rx_sdly_33:VALUE":0,
            "dcd_rx_sdly_34:VALUE":0,
            "dcd_rx_sdly_35:VALUE":0,
            "dcd_rx_sdly_36:VALUE":0,
            "dcd_rx_sdly_37:VALUE":0,
            "dcd_rx_sdly_38:VALUE":0,
            "dcd_rx_sdly_39:VALUE":0,
            "dcd_rx_sdly_40:VALUE":0,
            "dcd_rx_sdly_41:VALUE":0,
            "dcd_rx_sdly_42:VALUE":0,
            "dcd_rx_sdly_43:VALUE":0,
            "dcd_rx_sdly_44:VALUE":0,
            "dcd_rx_sdly_45:VALUE":0,
            "dcd_rx_sdly_46:VALUE":0,
            "dcd_rx_sdly_47:VALUE":0,
            "dcd_rx_sdly_48:VALUE":0,
            "dcd_rx_sdly_49:VALUE":0,
            "dcd_rx_sdly_50:VALUE":0,
            "dcd_rx_sdly_51:VALUE":0,
            "dcd_rx_sdly_52:VALUE":0,
            "dcd_rx_sdly_53:VALUE":0,
            "dcd_rx_sdly_54:VALUE":0,
            "dcd_rx_sdly_55:VALUE":0,
            "dcd_rx_sdly_56:VALUE":0,
            "dcd_rx_sdly_57:VALUE":0,
            "dcd_rx_sdly_58:VALUE":0,
            "dcd_rx_sdly_59:VALUE":0,
            "dcd_rx_sdly_60:VALUE":0,
            "dcd_rx_sdly_61:VALUE":0,
            "dcd_rx_sdly_62:VALUE":0,
            "dcd_rx_sdly_63:VALUE":0,
            # Phase delay for outgoing offset data DHP->DCD
            "offset_dcd_dly_00:VALUE":0,
            "offset_dcd_dly_01:VALUE":0,
            "offset_dcd_dly_02:VALUE":0,
            "offset_dcd_dly_03:VALUE":0,
            "offset_dcd_dly_04:VALUE":0,
            "offset_dcd_dly_05:VALUE":0,
            "offset_dcd_dly_06:VALUE":0,
            "offset_dcd_dly_07:VALUE":0,
            "offset_dcd_dly_08:VALUE":0,
            "offset_dcd_dly_09:VALUE":0,
            "offset_dcd_dly_10:VALUE":0,
            "offset_dcd_dly_11:VALUE":0,
            "offset_dcd_dly_12:VALUE":0,
            "offset_dcd_dly_13:VALUE":0,
            "offset_dcd_dly_14:VALUE":0,
            "offset_dcd_dly_15:VALUE":0,
            "offset_dcd_dly_16:VALUE":0,
            "offset_dcd_dly_17:VALUE":0,
            "offset_dcd_dly_18:VALUE":0,
            "offset_dcd_dly_19:VALUE":0,
            "offset_dcd_dly_20:VALUE":0,
            "offset_dcd_dly_21:VALUE":0,
            "offset_dcd_dly_22:VALUE":0,
            "offset_dcd_dly_23:VALUE":0,
            "offset_dcd_dly_24:VALUE":0,
            "offset_dcd_dly_25:VALUE":0,
            "offset_dcd_dly_26:VALUE":0,
            "offset_dcd_dly_27:VALUE":0,
            "offset_dcd_dly_28:VALUE":0,
            "offset_dcd_dly_29:VALUE":0,
            "offset_dcd_dly_30:VALUE":0,
            "offset_dcd_dly_31:VALUE":0,
            "offset_dcd_dly_32:VALUE":0,
            "offset_dcd_dly_33:VALUE":0,
            "offset_dcd_dly_34:VALUE":0,
            "offset_dcd_dly_35:VALUE":0,
            "offset_dcd_dly_36:VALUE":0,
            "offset_dcd_dly_37:VALUE":0,
            "offset_dcd_dly_38:VALUE":0,
            "offset_dcd_dly_39:VALUE":0,
            "offset_dcd_dly_40:VALUE":0,
            "offset_dcd_dly_41:VALUE":0,
            "offset_dcd_dly_42:VALUE":0,
            "offset_dcd_dly_43:VALUE":0,
            "offset_dcd_dly_44:VALUE":0,
            "offset_dcd_dly_45:VALUE":0,
            "offset_dcd_dly_46:VALUE":0,
            "offset_dcd_dly_47:VALUE":0,
            "offset_dcd_dly_48:VALUE":0,
            "offset_dcd_dly_49:VALUE":0,
            "offset_dcd_dly_50:VALUE":0,
            "offset_dcd_dly_51:VALUE":0,
            "offset_dcd_dly_52:VALUE":0,
            "offset_dcd_dly_53:VALUE":0,
            "offset_dcd_dly_54:VALUE":0,
            "offset_dcd_dly_55:VALUE":0,
            "offset_dcd_dly_56:VALUE":0,
            "offset_dcd_dly_57:VALUE":0,
            "offset_dcd_dly_58:VALUE":0,
            "offset_dcd_dly_59:VALUE":0,
            "offset_dcd_dly_60:VALUE":0,
            "offset_dcd_dly_61:VALUE":0,
            "offset_dcd_dly_62:VALUE":0,
            "offset_dcd_dly_63:VALUE":0,
            # GLOBAL REGISTER
            # END

            # CORE REGISTER
            # START
            "invert_input_values:S":0,
            "pedestal_subtraction:S":0,
            "active_ped_mem:S":0,
            "test_mode_en:S":0,
            "cm_correction_en:S":0,
            "cm_use_dcd_chan_mask:S":0,
            "cm_use_overflow_bit:S":0,

            "chip_id:VALUE":0,
            "latency:VALUE":0,
            "last_row:VALUE":0,
            "last_row_dump:VALUE":0,
            # signal management
            "frame_sync_proc_dly:VALUE":0,
            "row2_sync_dcd_clk_dly:VALUE":0,
            "sw_last_row:VALUE":0,
            "disable_memory:VALUE":0,
            "pedestal_offset:VALUE":0,
            "cm_offset:VALUE":0,
            "threshold:VALUE":0,

            "offset_mem_disable:VALUE":0,
            "offset_frame_sync_dly:VALUE":0,
            "offset_des_dly:VALUE":0,
            "offset_mem_active:S":0,
            "rand_gen_on_out_fifo:S":0,
            "trig_cont_en:S":0
            # CORE REGISTER
            # END
        })

    def set_default_value_for_dhp_registers(self):
        # GLOBAL_REG
        self.regs["tdo_tx_set06:S"] = 0
        self.regs["tdo_tx_set12:S"] = 0
        self.regs["tdo_tx_set30:S"] = 0
        self.regs["pll_des_clk_sel:S"] = 1

        self.regs["IDAC_CML_TX_BIAS:VALUE"] = 120
        self.regs["IDAC_CML_TX_BIASD:VALUE"] = 250
        self.regs["IDAC_CML_TX_IBIASDELAY:VALUE"] = 0

        self.regs["IDAC_DCD_RX_IREF:VALUE"] = 100

        self.regs["IDAC_LVDS_RX_IREF:VALUE"] = 100
        self.regs["IDAC_LVDS_TX_IREF:VALUE"] = 150

        self.regs["IDAC_PLL_I50U:VALUE"] = 40
        self.regs["IDAC_PLL_ICP:VALUE"] = 4
        self.regs["IDAC_PLL_IVCO:VALUE"] = 96
        self.regs["IDAC_PLL_I50U:VALUE"] = 40
        self.regs["IREF_TRIMMING:VALUE"] = 8

        self.regs["dcd_jtag_en_out:S"] = 0
        self.regs["dcd_sync_en_clk:S"] = 0
        self.regs["dcd_sync_en_diff_clk:S"] = 0
        self.regs["dcd_sync_en_frame_sync:S"] = 0
        self.regs["dcd_sync_en_row_sync:S"] = 0

        self.regs["dcd_clk_set06:S"] = 0
        self.regs["dcd_clk_set12:S"] = 1
        self.regs["dcd_clk_set30:S"] = 1

        self.regs["chip_id:VALUE"] = 0
        self.regs["last_row:VALUE"] = 191
        self.regs["last_row_dump:VALUE"] = 191
        self.regs["frame_sync_proc_dly:VALUE"] = 17
        self.regs["row2_sync_dcd_clk_dly:VALUE"] = 4
        self.regs["sw_last_row:VALUE"] = 191
        self.regs["do_cc:S"] = 0
        self.regs["how_long_align:VALUE"] = 400
        self.regs["double_out_bits:S"] = 0
        self.regs["frame_sync_proc_dly:VALUE"] = 17

        for key, val in dhp.regs.iteritems():
            if "dcd_rx_sdly_" in key or "offset_dcd_dly_" in key:
                self.regs[key] = 0

    def write_core(self):
        get_pv("PXD:H1031:D1:corereg:trg:set")#.put(1)
    def read_core(self):
        get_pv("PXD:H1031:D1:corereg_dispatch:trg:cur")#.put(1)

    def write_global(self):
        get_pv("PXD:H1031:D1:globalreg:trg:set")#.put(1)
    def read_globale(self):
        get_pv("PXD:H1031:D1:globalreg_dispatch:trg:cur")#.put(1)
