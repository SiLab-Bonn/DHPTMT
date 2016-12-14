import logging

from basil.dut import Dut
#from dhptclasses import SW_SIGNALS_4X_TIME_MULTIPLEXED
#from dhptclasses import OFFSET_4X_TIME_MULTIPLEXED
#from dhptclasses import SW_SIGNALS_SEQUENCE
#from dhptclasses import OFFSET_SIGNALS_SEQUENCE
import time
import numpy as np
from sys import exit


''' Function list
    <send_test_frame>       sends DCDpp test pattern to DOX[7:0] 
    <mem_test>              performs a memory test of the SEQ_GEN
    <get_DI>   returns the 32byte send by the DHPT [128'b0, 44'b0, 4'b<row2sync>, 16'b<sw_signals>, 64'b<DI_bits>]           
    <get_offset_bits>       picks the <DI_bits> from the returned 32byte word
    <get_sw_bits>           picks the <sw_signals> from the returned 32byte word
    <get_r2s_bits>          picks the <row2sync> from the returned 32byte word
    <io_enable_all>         enabled via GPIO all 64 bits of DOX[7:0]
    <io_disable_all>        disabled via GPIO all 64 bits of DOX[7:0]
    <io_enable_channel>     enabled via GPIO all 8 bits of DO<channel>[7:0]
    <io_disable_channel>    disabled via GPIO all 8 bits of DO<channel>[7:0]
    <dcd_ref_voltage>       sets the 8bit DAC via i2c to <voltage>
'''
        

class PROBECARD(Dut):

    '''
    A class for Communication between DHPT 1.0 and DCD emulator
    '''
    
    '''
    General functions for modules
    '''
    def __init__(self, cnfg):
        Dut.__init__(self, cnfg)
        self.is_seq_rec_configured = False 

    def reset_all_modules(self):
        logging.info("%s\tModule Reset",__name__)
        self['SEQ_REC'].reset()
        self['SEQ_GEN'].reset()
        self['I2C'].reset()
        self['GPIO'].reset()
        self['PULSER_GEN'].reset()
        self['PULSER_REC'].reset()
        self['PULSER_R2S'].reset()

    def setup_to_idle(self):
        logging.info("%s\tSetting up the ProbeCard",__name__)
        self.dcd_ref_voltage()
        self.io_disable_all()

    '''
    GPIO
    '''
        
    def io_keep_enabled(self):
        '''
        Checks if IO channels are still enabled (BUGFIX needed)
        '''
        logging.info("%s\tKeeps channels DOX enabled", __name__)
        while True:
            curr = self["GPIO"].get_data()
            self["GPIO"].set_data(curr)
            sleep(100)
        
    def io_disable_all(self):
        '''
        Disabled the 8channels (64) outputs of the DCD emulator
        to the DHPT 1.0
        '''
        logging.info("%s\tDisabled all channels DOX", __name__)
        self["GPIO"].set_data([0xFF for i in range(8)])

    def io_enable_all(self):
        '''
        Enabled the 8 channel outputs of the DCD emulator
        to the DHPT 1.0
        '''
        logging.info("%s\tEnabled all channels DOX", __name__)
        self["GPIO"].set_data([0x00 for i in range(8)])

    def io_disable_channel(self, i_chan):
        '''
        Disabled the ith channel output of the DCD emulator
        to the DHPT 1.0
        '''
        curr = self["GPIO"].get_data()
        if isinstance(i_chan, list):
            for ch in i_chan:
                logging.info("%s\tDisable channel DO%s", __name__, ch)
                curr[7-ch] = 0xFF 
                self["GPIO"].set_data(curr)
        else:
            logging.info("%s\tDisable channel DO%s", __name__, i_chan)
            curr[7-i_chan] = 0xFF
            self["GPIO"].set_data(curr)

    def io_enable_channel(self, i_chan):
        '''
        Enabled the ith channel output of the DCD emulator
        to the DHPT 1.0
        '''
        curr = self["GPIO"].get_data()
        if isinstance(i_chan, list):
            for ch in i_chan:
                logging.info("%s\tEnable channel DO%s", __name__, ch)
                curr[7-ch] = 0x00
                self["GPIO"].set_data(curr)
        else:
            logging.info("%s\tEnable channel DO%s", __name__, i_chan)
            curr[7-i_chan] = 0x00
            self["GPIO"].set_data(curr)

    '''
    PULSE_GEN functions for pulse generators, i.e. PULER_GEN and PULSER_REC 
    '''
    def set_pulserRec_repeat(self, rep=1):
        self['PULSER_REC'].set_repeat(rep)
        
    def set_pulserGen_repeat(self, rep=1):
        self['PULSER_GEN'].set_repeat(rep)       
    
    def set_pulserR2S_repeat(self, rep=1):
        self['PULSER_R2S'].set_repeat(rep)       
           
    '''
    SEQ_GEN and SEQ_REC funtions for recording and generating data
    '''       
    def conf_seqRec_size(self, GCK_count):
        self['SEQ_REC'].set_size(GCK_count)
        
    def conf_seqGen_size(self, GCK_count):
        self['SEQ_GEN'].set_size(GCK_count)    
    
    def conf_seqRec(self, pulse_delay=0, pulse_width=2):
        logging.info("%s\tConfigure Sequence Recorder",__name__)
        self['SEQ_REC'].set_en_ext_start(True)
        self['PULSER_REC'].set_delay(pulse_delay)
        self['PULSER_REC'].set_width(pulse_width)

    def conf_seqGen(self, pulse_delay=0, pulse_width=5):
        logging.info("%s\tConfigure Sequence Generator",__name__)
        self['PULSER_R2S'].set_en(True)
        self['SEQ_GEN'].set_en_ext_start(True)
        self['PULSER_R2S'].set_delay(pulse_delay)
        self['PULSER_R2S'].set_width(pulse_width)
        
    def mem_test(self):
        '''
        Performs a self memory test by writing multiple
        random bit patterns in the memory space of the
        DCD emulator
        '''
        done = False

        test_pattern = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        test_addr = 0
        num_of_bytes = 6
        self['SEQ_GEN'].set_data(test_pattern, test_addr)
        #self['SEQ_GEN'].set_size(num_of_bytes)
        #self['SEQ_GEN'].start()

        print(test_pattern, num_of_bytes)
        rb = self['SEQ_GEN'].get_data(num_of_bytes, test_addr)
        print (test_pattern, rb)
        if rb == test_pattern:
            done = True

        return done 
        
    def send_testFrame(self):
        '''
        Generates the test pattern according to the DCDpipeline
        and enables the data at the output of the DCD emulator
        '''
        pass
    
    def get_dcd42_testpattern(self):
        return np.array([0x55, 0x22, 0x11, 0x00, 0x88,
                         0x44, 0xAA, 0x55, 0xAA, 0x55,
                         0xAA, 0xDD, 0xEE, 0xFF, 0x77,
                         0xBB, 0x55, 0xAA, 0x55, 0xFF,
                         0x00, 0xFF, 0x00, 0xFF, 0xFF,
                         0x00, 0x00, 0x7F, 0xFF, 0x40,
                         0x00, 0xAA], dtype=np.uint8)
    
    def get_dcd_random_pattern(self):
        return np.zeros([np.random.randint(0,256) for i in range(32)], dtype=np.uint8) 
    
    def get_seq_rec_off_data(self, seq_rec_row):
        total_num_bytes = 8*seq_rec_row
        d = self['SEQ_REC_OFF'].get_data(total_num_bytes)
        return [d[i*8:(i+1)*8] for i in range(seq_rec_row)] 

    def get_seq_rec_sw_data(self, seq_rec_row):
        total_num_bytes = 2*seq_rec_row
        d = self['SEQ_REC_SW'].get_data(total_num_bytes)
        return [d[i*2:(i+1)*2] for i in range(seq_rec_row)] 

    def get_offsetBits(self):
        seq_rec_row = last_row*8 
        if not self.is_seq_rec_configured:
            self.conf_seqRec_size(seq_rec_row)
            self.is_seq_rec_configured = True
                  
        data = self.get_seq_rec_off_data(seq_rec_row)
        retData = []
        
        block3210 = np.zeros(4, dtype=np.uint32)
        for blk in range(0, len(data), 2):
            block3210[3] = np.uint32(
                (
                    (
                        ((data[blk,0] & 0x20) << 26) | ((data[blk,0] & 0x02) << 29) |
                        ((data[blk,1] & 0x20) << 24) | ((data[blk,1] & 0x02) << 27) |
                        ((data[blk,2] & 0x20) << 22) | ((data[blk,2] & 0x02) << 25) |
                        ((data[blk,3] & 0x20) << 20) | ((data[blk,3] & 0x02) << 23) |
                        ((data[blk,4] & 0x20) << 18) | ((data[blk,4] & 0x02) << 21) |
                        ((data[blk,5] & 0x20) << 16) | ((data[blk,5] & 0x02) << 19) |
                        ((data[blk,6] & 0x20) << 14) | ((data[blk,6] & 0x02) << 17) | 
                        ((data[blk,7] & 0x20) << 12) | ((data[blk,7] & 0x02) << 15)
                    ) >> 16 
                 )
                      |
                (
                    (
                        ((data[blk,0] & 0x10) << 11)| ((data[blk,0] & 0x01) << 14) |
                        ((data[blk,1] & 0x10) << 9) | ((data[blk,1] & 0x01) << 12) |
                        ((data[blk,2] & 0x10) << 7) | ((data[blk,2] & 0x01) << 10) |
                        ((data[blk,3] & 0x10) << 5) | ((data[blk,3] & 0x01) << 8) |
                        ((data[blk,4] & 0x10) << 3) | ((data[blk,4] & 0x01) << 6) |
                        ((data[blk,5] & 0x10) << 1) | ((data[blk,5] & 0x01) << 4) |
                        ((data[blk,6] & 0x10) >> 1) | ((data[blk,6] & 0x01) << 2) | 
                        ((data[blk,7] & 0x10) >> 3) | ( data[blk,7] & 0x01)
                    ) << 16
                )
            )
            
            block3210[2] = np.uint32(
                (
                    (
                        ((data[blk,0] & 0x80) << 26) | ((data[blk,0] & 0x08) << 29) |
                        ((data[blk,1] & 0x80) << 24) | ((data[blk,1] & 0x08) << 27) |
                        ((data[blk,2] & 0x80) << 22) | ((data[blk,2] & 0x08) << 25) |
                        ((data[blk,3] & 0x80) << 20) | ((data[blk,3] & 0x08) << 23) |
                        ((data[blk,4] & 0x80) << 18) | ((data[blk,4] & 0x08) << 21) |
                        ((data[blk,5] & 0x80) << 16) | ((data[blk,5] & 0x08) << 19) |
                        ((data[blk,6] & 0x80) << 14) | ((data[blk,6] & 0x08) << 17) | 
                        ((data[blk,7] & 0x80) << 12) | ((data[blk,7] & 0x08) << 15)
                    ) >> 16 
                 )
                      |
                (
                    (
                        ((data[blk,0] & 0x40) << 11)| ((data[blk,0] & 0x04) << 14) |
                        ((data[blk,1] & 0x40) << 9) | ((data[blk,1] & 0x04) << 12) |
                        ((data[blk,2] & 0x40) << 7) | ((data[blk,2] & 0x04) << 10) |
                        ((data[blk,3] & 0x40) << 5) | ((data[blk,3] & 0x04) << 8) |
                        ((data[blk,4] & 0x40) << 3) | ((data[blk,4] & 0x04) << 6) |
                        ((data[blk,5] & 0x40) << 1) | ((data[blk,5] & 0x04) << 4) |
                        ((data[blk,6] & 0x40) >> 1) | ((data[blk,6] & 0x04) << 2) | 
                        ((data[blk,7] & 0x40) >> 3) | ( data[blk,7] & 0x04)
                    ) << 16
                )
            )
            block3210[1] = np.uint32(
                (
                    (
                        ((data[blk+1,0] & 0x20) << 26) | ((data[blk+1,0] & 0x02) << 29) |
                        ((data[blk+1,1] & 0x20) << 24) | ((data[blk+1,1] & 0x02) << 27) |
                        ((data[blk+1,2] & 0x20) << 22) | ((data[blk+1,2] & 0x02) << 25) |
                        ((data[blk+1,3] & 0x20) << 20) | ((data[blk+1,3] & 0x02) << 23) |
                        ((data[blk+1,4] & 0x20) << 18) | ((data[blk+1,4] & 0x02) << 21) |
                        ((data[blk+1,5] & 0x20) << 16) | ((data[blk+1,5] & 0x02) << 19) |
                        ((data[blk+1,6] & 0x20) << 14) | ((data[blk+1,6] & 0x02) << 17) | 
                        ((data[blk+1,7] & 0x20) << 12) | ((data[blk+1,7] & 0x02) << 15)
                    ) >> 16 
                 )
                      |
                (
                    (
                        ((data[blk+1,0] & 0x10) << 11)| ((data[blk+1,0] & 0x01) << 14) |
                        ((data[blk+1,1] & 0x10) << 9) | ((data[blk+1,1] & 0x01) << 12) |
                        ((data[blk+1,2] & 0x10) << 7) | ((data[blk+1,2] & 0x01) << 10) |
                        ((data[blk+1,3] & 0x10) << 5) | ((data[blk+1,3] & 0x01) << 8) |
                        ((data[blk+1,4] & 0x10) << 3) | ((data[blk+1,4] & 0x01) << 6) |
                        ((data[blk+1,5] & 0x10) << 1) | ((data[blk+1,5] & 0x01) << 4) |
                        ((data[blk+1,6] & 0x10) >> 1) | ((data[blk+1,6] & 0x01) << 2) | 
                        ((data[blk+1,7] & 0x10) >> 3) | ( data[blk+1,7] & 0x01)
                    ) << 16          
                )                    
            )                        
                                     
            block3210[0] = np.uint32(
                (                    
                    (                
                        ((data[blk+1,0] & 0x80) << 26) | ((data[blk,0] & 0x08) << 29) |
                        ((data[blk+1,1] & 0x80) << 24) | ((data[blk,1] & 0x08) << 27) |
                        ((data[blk+1,2] & 0x80) << 22) | ((data[blk,2] & 0x08) << 25) |
                        ((data[blk+1,3] & 0x80) << 20) | ((data[blk,3] & 0x08) << 23) |
                        ((data[blk+1,4] & 0x80) << 18) | ((data[blk,4] & 0x08) << 21) |
                        ((data[blk+1,5] & 0x80) << 16) | ((data[blk,5] & 0x08) << 19) |
                        ((data[blk+1,6] & 0x80) << 14) | ((data[blk,6] & 0x08) << 17) | 
                        ((data[blk+1,7] & 0x80) << 12) | ((data[blk,7] & 0x08) << 15)
                    ) >> 16 
                 )
                      |
                (
                    (
                        ((data[blk+1,0] & 0x40) << 11)| ((data[blk+1,0] & 0x04) << 14) |
                        ((data[blk+1,1] & 0x40) << 9) | ((data[blk+1,1] & 0x04) << 12) |
                        ((data[blk+1,2] & 0x40) << 7) | ((data[blk+1,2] & 0x04) << 10) |
                        ((data[blk+1,3] & 0x40) << 5) | ((data[blk+1,3] & 0x04) << 8) |
                        ((data[blk+1,4] & 0x40) << 3) | ((data[blk+1,4] & 0x04) << 6) |
                        ((data[blk+1,5] & 0x40) << 1) | ((data[blk+1,5] & 0x04) << 4) |
                        ((data[blk+1,6] & 0x40) >> 1) | ((data[blk+1,6] & 0x04) << 2) | 
                        ((data[blk+1,7] & 0x40) >> 3) | ( data[blk+1,7] & 0x04)
                    ) << 16
                )
            )
                          
        return block3210

    def get_offsetSequence(self, GCK_count, new_conf):
        data = self.get_offsetBits(GCK_count, new_conf)
        #print "Sampled Offset data successfully"
        DI0_0 = []
        DI0_1 = []
        DI1_0 = []
        DI1_1 = []
        DI2_0 = []
        DI2_1 = []
        DI3_0 = []
        DI3_1 = []
      
        DI4_0 = []
        DI4_1 = []
        DI5_0 = []
        DI5_1 = []
        DI6_0 = []
        DI6_1 = []
        DI7_0 = []
        DI7_1 = []
      
        for d in data:
            offset_4x_t = d.get_data()
     
            #sort DI0 
            DI0_0.apped([offset_4x_t.DI0 & 0x01])
            DI0_0.apped([offset_4x_t.DI0 & 0x04])  
            DI0_0.apped([offset_4x_t.DI0 & 0x10])
            DI0_0.apped([offset_4x_t.DI0 & 0x40])
           
            DI0_1.apped([offset_4x_t.DI0 & 0x02])
            DI0_1.apped([offset_4x_t.DI0 & 0x08])
            DI0_1.apped([offset_4x_t.DI0 & 0x20])
            DI0_1.apped([offset_4x_t.DI0 & 0x80])
            
            #sort DI1 
            DI1_0.apped([offset_4x_t.DI1 & 0x01])
            DI1_0.apped([offset_4x_t.DI1 & 0x04])  
            DI1_0.apped([offset_4x_t.DI1 & 0x10])
            DI1_0.apped([offset_4x_t.DI1 & 0x40])
        
            DI1_1.apped([offset_4x_t.DI1 & 0x02])
            DI1_1.apped([offset_4x_t.DI1 & 0x08])
            DI1_1.apped([offset_4x_t.DI1 & 0x20])
            DI1_1.apped([offset_4x_t.DI1 & 0x80])
            
            #sort DI2
            DI2_0.apped([offset_4x_t.DI2 & 0x01])
            DI2_0.apped([offset_4x_t.DI2 & 0x04])  
            DI2_0.apped([offset_4x_t.DI2 & 0x10])
            DI2_0.apped([offset_4x_t.DI2 & 0x40])
           
            DI2_1.apped([offset_4x_t.DI2 & 0x02])
            DI2_1.apped([offset_4x_t.DI2 & 0x08])
            DI2_1.apped([offset_4x_t.DI2 & 0x20])
            DI2_1.apped([offset_4x_t.DI2 & 0x80])
                
            #sort DI3
            DI3_0.apped([offset_4x_t.DI3 & 0x01])
            DI3_0.apped([offset_4x_t.DI3 & 0x04])  
            DI3_0.apped([offset_4x_t.DI3 & 0x10])
            DI3_0.apped([offset_4x_t.DI3 & 0x40])
           
            DI3_1.apped([offset_4x_t.DI3 & 0x02])
            DI3_1.apped([offset_4x_t.DI3 & 0x08])
            DI3_1.apped([offset_4x_t.DI3 & 0x20])
            DI3_1.apped([offset_4x_t.DI3 & 0x80])    
                
            #sort DI4 
            DI4_0.apped([offset_4x_t.DI4 & 0x01])
            DI4_0.apped([offset_4x_t.DI4 & 0x04])  
            DI4_0.apped([offset_4x_t.DI4 & 0x10])
            DI4_0.apped([offset_4x_t.DI4 & 0x40])
        
            DI4_1.apped([offset_4x_t.DI4 & 0x02])
            DI4_1.apped([offset_4x_t.DI4 & 0x08])
            DI4_1.apped([offset_4x_t.DI4 & 0x20])
            DI4_1.apped([offset_4x_t.DI4 & 0x80])    
            
            #sort DI5
            DI5_0.apped([offset_4x_t.DI5 & 0x01])
            DI5_0.apped([offset_4x_t.DI5 & 0x04])  
            DI5_0.apped([offset_4x_t.DI5 & 0x10])
            DI5_0.apped([offset_4x_t.DI5 & 0x40])
           
            DI5_1.apped([offset_4x_t.DI5 & 0x02])
            DI5_1.apped([offset_4x_t.DI5 & 0x08])
            DI5_1.apped([offset_4x_t.DI5 & 0x20])
            DI5_1.apped([offset_4x_t.DI5 & 0x80])
            
            #sort DI6 
            DI6_0.apped([offset_4x_t.DI6 & 0x01])
            DI6_0.apped([offset_4x_t.DI6 & 0x04])  
            DI6_0.apped([offset_4x_t.DI6 & 0x10])
            DI6_0.apped([offset_4x_t.DI6 & 0x40])
           
            DI6_1.apped([offset_4x_t.DI6 & 0x02])
            DI6_1.apped([offset_4x_t.DI6 & 0x08])
            DI6_1.apped([offset_4x_t.DI6 & 0x20])
            DI6_1.apped([offset_4x_t.DI6 & 0x80])
            
            #sort DI7
            DI7_0.apped([offset_4x_t.DI7 & 0x01])
            DI7_0.apped([offset_4x_t.DI7 & 0x04])  
            DI7_0.apped([offset_4x_t.DI7 & 0x10])
            DI7_0.apped([offset_4x_t.DI7 & 0x40])
        
            DI7_1.apped([offset_4x_t.DI7 & 0x02])
            DI7_1.apped([offset_4x_t.DI7 & 0x08])
            DI7_1.apped([offset_4x_t.DI7 & 0x20])
            DI7_1.apped([offset_4x_t.DI7 & 0x80])
        return OFFSET_SIGNALS_SEQUENCE(GCK_count, [DI7_0 , DI7_1], [DI6_0 , DI6_1], [DI5_0 , DI5_1], [DI4_0 , DI4_1], 
                                       [DI3_0 , DI3_1], [DI2_0 , DI2_1], [DI1_0 , DI1_1], [DI0_0 , DI0_1])

    def get_switcherBits(self, last_row):
        '''
        Reads switcher bytes of the DI
        '''
        seq_rec_row = last_row*8 
        if not self.is_seq_rec_configured:
            self.conf_seqRec_size(seq_rec_row)
            self.is_seq_rec_configured = True
                  
        data = self.get_seq_rec_sw_data(seq_rec_row)
        
        #block3 clk, block2 gate, block1 clear, block0 serIn
        block3210 = np.zeros(4, dtype=np.uint32)
        for block_id in range(0, len(data), 8):
            clk   = []
            gate  = []
            clear = []
            serIn = []
            for i in range(8):
                clk.append(  (data[block_id+i  , 0] & 0xf0) >> 4)
                gate.append(  data[block_id+i  , 0] & 0x0f)
                clear.append((data[block_id+i  , 1]  & 0xf0) >> 4)
                serIn.append( data[block_id+i  , 1]  & 0xf0)
            block3210[3] = (clk[7]   << 28) | (clk[6]   << 24) | (clk[5]   << 20) | (clk[4]   << 16) | (clk[3]   << 12) | (clk[2]   << 8) | (clk[1]   << 4) | clk[0]
            block3210[2] = (gate[7]  << 28) | (gate[6]  << 24) | (gate[5]  << 20) | (gate[4]  << 16) | (gate[3]  << 12) | (gate[2]  << 8) | (gate[1]  << 4) | gate[0]
            block3210[1] = (clear[7] << 28) | (clear[6] << 24) | (clear[5] << 20) | (clear[4] << 16) | (clear[3] << 12) | (clear[2] << 8) | (clear[1] << 4) | clear[0]
            block3210[0] = (serIn[7] << 28) | (serIn[6] << 24) | (serIn[5] << 20) | (serIn[4] << 16) | (serIn[3] << 12) | (serIn[2] << 8) | (serIn[1] << 4) | serIn[0]
            
        return block3210 
        #return [SW_SIGNALS_4X_TIME_MULTIPLEXED(int((d[32 - 10] & 0xf0) >> 4), int(d[32 - 10] & 0x0f), int((d[32 - 9] & 0xf0) >> 4), int(d[32 - 9] & 0x0f)) for d in data]

    def get_swSequence(self, GCK_count=512, new_conf=False):
        data = self.get_swBits(GCK_count, new_conf)
        #print "Sampled SW data successfully"
        clk   = []
        gate  = []
        clear = []
        frame = []

        frame_id = 3
        clear_id = 2
        gate_id  = 1
        clk_id   = 0

        for d in data:
            sw_4x_t = d.get_data()
            
            clk     = clk   + [(sw_4x_t[clk_id]   & 0x08) >> 3, (sw_4x_t[clk_id]   & 0x04) >> 2, (sw_4x_t[clk_id]   & 0x02) >> 1, (sw_4x_t[clk_id]   & 0x01)]
            gate    = gate  + [(sw_4x_t[gate_id]  & 0x08) >> 3, (sw_4x_t[gate_id]  & 0x04) >> 2, (sw_4x_t[gate_id]  & 0x02) >> 1, (sw_4x_t[gate_id]  & 0x01)]
            clear   = clear + [(sw_4x_t[clear_id] & 0x08) >> 3, (sw_4x_t[clear_id] & 0x04) >> 2, (sw_4x_t[clear_id] & 0x02) >> 1, (sw_4x_t[clear_id] & 0x01)]
            frame   = frame + [(sw_4x_t[frame_id] & 0x08) >> 3, (sw_4x_t[frame_id] & 0x04) >> 2, (sw_4x_t[frame_id] & 0x02) >> 1, (sw_4x_t[frame_id] & 0x01)]
        
        return SW_SIGNALS_SEQUENCE(GCK_count, clk, gate, clear, frame)

    def get_r2s_bits(self, GCK_count=512, new_conf=False):
        '''
        Reads switcher bytes of the DI
        '''
        if new_conf == False and self.conf_cnt == 0:
            self.conf_seqRec_size(GCK_count)
            self.conf_cnt = self.conf_cnt + 1
        else:
            if new_conf == True:
                self.conf_seqRec_size(GCK_count)
                  
        data = self.get_seq_rec_data(GCK_count)
        return [int(d[32-1-8-2] & 0x0F) for d in data]

    def set_dcd_ref_voltage(self, address=0x60, voltage=1.125, unit = "V"):
        LSB = 7.8 #in mV!!!!!
        if voltage > 2.0 and unit == "V" or voltage > 2000 and unit == "mV":
            logging.info("%s\tVoltage set to high!\t V=%s %s",__name__,voltage, unit)
        else:
            if unit == "V":
                val = int(voltage/LSB*1000)
            else:
                if unit == "mV":
                    val = int(voltage/LSB)
            logging.info("%s\tDCD_REF_VOLTAGE set to %s %s (%s)",__name__,voltage, unit, val)
            # reset i2c module

            # Address in *.yaml config file
            # MAX5380 8bit DAC - VREF 2V -> LSB = 7.8125mV
            # Address 0x0060 = 96
            # Data    0x0090 = 144 (=1.125V = VREF = LSB * num)
            self['I2C'].set_addr(address)
            self['I2C'].set_data(val)
            self['I2C'].clk_reset()
            self['I2C'].start()
        
    def get_dcd_ref_voltage(self):
        return self['I2C'].get_data()
    '''
    Generating data for DHPT
    '''
    def get_r2s_shift_to_80MHz(self):
        logging.info("%s\tGet shift of testpattern and row 2 sync",__name__)
        self.conf_seqRec()
        self.set_pulserR2S_repeat()
        r2s = self.get_r2s_bits(512)
        r2s_idx = np.where(np.array(r2s)!=0)
        
        if len(r2s_idx[0])==0:
            logging.error("%s\tFailed. No row2sync signal present.",__name__)
            exit(-1)
        #    print r2s, r2s_idx[0][0]
        return int(4.0-np.log2(r2s[r2s_idx[0][0]]))
        
    def send_data_to_dhpt(self, data, seqSizeInWords, fillFullMemory = False, rep=0, channel=[3,5]):
        logging.info("%s\tData send from FPGA to dhpt",__name__)
        self.conf_seqGen()
        
        self["SEQ_GEN"].set_size(seqSizeInWords)
        gotSize = self["SEQ_GEN"].get_size()
        if gotSize == seqSizeInWords:
            logging.info("%s\tSet number of words to send to %s",__name__,gotSize)
        else:
            logging.error("%s\tSet number of words failed",__name__)
        sentData = []
        self.io_disable_all()
        if len(data)<256:
            chunkSize = 32
            sleepTime = 0.1 
        else: 
            chunkSize = 128 #in bytes
            sleepTime = 0.2
        '''
        if fillFullMemory:
            data = [data += data for i in range(16*1024/len(data))]
        '''
        if isinstance(data, list):
            pass
        elif isinstance(data, str):
            data = data.tolist()
        
        if fillFullMemory:
            for cnt in range(16*1024/len(data)):
                for row in range(len(data)/chunkSize):
                    err = 0
                    start = chunkSize*row
                    stop = chunkSize*(row+1)-1
                    self['SEQ_GEN'].set_data(data[start:stop],start+len(data)*cnt)
                    sleep(sleepTime)
                #sleep(2)
                    rb = self['SEQ_GEN'].get_data(chunkSize,start+len(data)*cnt)
                    sentData += rb
                    for k in range(chunkSize-1):
                        if data[start:stop][k] != rb[k]:
                            err = err + 1
                    if err != 0:
                        logging.error("%s\tRead back not equal sent pattern! %s errors counted",__name__,err)   
                    else:
                        logging.info("%s\tCorrect read back!",__name__)
        else:
            for start in range(0,len(data),chunkSize):
                err = 0
                stop = chunkSize+start-1
                self['SEQ_GEN'].set_data(data[start:stop],start)
                sleep(sleepTime)
            #sleep(2)
                rb = self['SEQ_GEN'].get_data(chunkSize,start)
                sentData += rb
                for k in range(chunkSize-1):
                    if data[start:stop][k] != rb[k]:
                        err = err + 1
                if err != 0:
                    logging.error("%s\tRead back not equal sent pattern! %s errors counted",__name__,err)   
                else:
                    logging.info("%s\tCorrect read back!",__name__)
        self.io_enable_channel(channel)
        #self.set_pulserGen_repeat()
        #self.set_pulserR2S_repeat()
        self["SEQ_GEN"].set_repeat(rep)
        
        #self["PULSER_GEN"].start()
        logging.info("%s\tSend data.",__name__)
        return sentData
    
    def deserializer_1_2_4(self, d0, d1, d2, d3):
        d0 = np.uint8(d0)
        d1 = np.uint8(d1)
        d2 = np.uint8(d2)
        d3 = np.uint8(d3)
        return np.uint32(((d3 & 0x80) << 24) | ((d2 & 0x80) << 23) | ((d1 & 0x80) << 22) | ((d0 & 0x80) << 21) |
            ((d3 & 0x40) << 21) | ((d2 & 0x40) << 20) | ((d1 & 0x40) << 19) | ((d0 & 0x40) << 18) |
            ((d3 & 0x20) << 18) | ((d2 & 0x20) << 17) | ((d1 & 0x20) << 16) | ((d0 & 0x20) << 15) |
            ((d3 & 0x10) << 15) | ((d2 & 0x10) << 14) | ((d1 & 0x10) << 13) | ((d0 & 0x10) << 12) |
            ((d3 & 0x08) << 12) | ((d2 & 0x08) << 11) | ((d1 & 0x08) << 10) | ((d0 & 0x08) << 9) |
            ((d3 & 0x04) << 9) | ((d2 & 0x04) << 8) | ((d1 & 0x04) << 7)  | ((d0 & 0x04) << 6)  |
            ((d3 & 0x02) << 6)  | ((d2 & 0x02) << 5)  | ((d1 & 0x02) << 4)  | ((d0 & 0x02) << 3)  |
            ((d3 & 0x01) << 3)  | ((d2 & 0x01) << 2)  | ((d1 & 0x01) << 1)  | d0 & 0x01)
    
    def send_testpattern_to_dhpt(self):
        logging.info("%s\tData send from FPGA to dhpt",__name__)
        testData = get_dcd42_testpattern()
    
        self.conf_seqGen()
        
        self["SEQ_GEN"].set_size(8)
        gotSize = self["SEQ_GEN"].get_size()
        if gotSize == seqSizeInWords:
            logging.info("%s\tSet number of words to send to %s",__name__,gotSize)
        else:
            logging.error("%s\tSet number of words failed",__name__)
            
        self.io_disable_all()
        
        #data = [L7_3, L7_2, L7_1, L7_0, L6_3, L6_2,...]
        for blk in range(8):      
            d = self.deserializer_1_2_4(testData[blk*4], testData[blk*4+1], testData[blk*4+2], testData[blk*4+3])
            self['SEQ_GEN'].set_data(d, 4*blk)
            #d = [testData[blk*4+3], testData[blk*4+2], testData[blk*4+1], testData[blk*4]]*8
            #self['SEQ_GEN'].set_data(d, blk)
            time.sleep(sleepTime)
            rb = self['SEQ_GEN'].get_data(blk)
            if np.array(d) != np.array(rb): 
                logging.error("%s\tRead back not equal sent pattern! %s errors counted",__name__,err)   
            else:
                logging.info("%s\tCorrect read back!",__name__)
    
        self.io_enable_channel(channel)
        #self.set_pulserGen_repeat()
        #self.set_pulserR2S_repeat()
        self["SEQ_GEN"].set_repeat(0)
        
        #self["PULSER_GEN"].start()
        logging.info("%s\tSend data.",__name__)
        return testData
    
    def send_random_pattern_to_dhpt(self):
        logging.info("%s\tData send from FPGA to dhpt",__name__)
        testData = get_dcd_random_pattern()
    
        self.conf_seqGen()
        self["SEQ_GEN"].set_size(8)
        gotSize = self["SEQ_GEN"].get_size()
        if gotSize == seqSizeInWords:
            logging.info("%s\tSet number of words to send to %s",__name__,gotSize)
        else:
            logging.error("%s\tSet number of words failed",__name__)
            
        self.io_disable_all()
        
        #data = [L7_3, L7_2, L7_1, L7_0, L6_3, L6_2,...]
        for blk in range(8):      
            d = self.deserializer_1_2_4(testData[blk*4], testData[blk*4+1], testData[blk*4+2], testData[blk*4+3])
            self['SEQ_GEN'].set_data(d, 4*blk)
            #d = [testData[0, blk*4+3], testData[0, blk*4+2], testData[0, blk*4+1], testData[0, blk*4]]*8
            #self['SEQ_GEN'].set_data(d, blk)
            time.sleep(sleepTime)
            rb = self['SEQ_GEN'].get_data(blk)
            if np.array(d) != np.array(rb): 
                logging.error("%s\tRead back not equal sent pattern! %s errors counted",__name__,err)   
            else:
                logging.info("%s\tCorrect read back!",__name__)
    
        self.io_enable_channel(channel)
        #self.set_pulserGen_repeat()
        #self.set_pulserR2S_repeat()
        self["SEQ_GEN"].set_repeat(0)
        
        #self["PULSER_GEN"].start()
        logging.info("%s\tSend data.",__name__)
        return testData    
    