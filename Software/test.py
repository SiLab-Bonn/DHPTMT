from classes import DHPTMP
#GLOBAL DEFINES
DHPTVERSION = "1.2b"

SOFTWAREVERSION = 1.0

if __name__ == "__main__":

    configFileName = "probecard.yaml"
    
    outputPath = "/home/user/NeedleCardTest/Data/DHPT%s"%DHPTVERSION
    initiate_logger(outputPath, testRevision=SOFTWAREVERSION, dhptVersion=DHPTVERSION)
    
    mp = DHPTMP()
    updatePortInYaml(configFileName)
    
    '''
    CHECK:    Power Consumption
    '''
    isPowerOK = mp.test_power_consumption()
    if not isPowerOK:
        while (tester != "quit") or (tester != "ok"):
            tester = raw_input("---ERROR---ERROR---ERROR---ERROR---ERROR---ERROR---\nPower Consumption Test failed!! Please check bump connection!\nOptions:\n\t-to continue type 'ok'\n\t-to quit test type 'quit'")
            if tester == "quit":
                logging.warning("Test abort!")
                sys.exit(-1)
            elif tester == "ok":
                pass
              
    
    mp.set_dcd_ref_voltage(voltage=0.9, unit="V")
    mp.sc.dhptResgister.set_default()
    
    '''
    CHECK:    JTAG 
    '''
    isJtagOK = mp.test_jtag()
    mp.sc.set_default()
      
    '''
    CHECK:    Memories
    '''
    isMemoryOK =  test_script.test_memory_pedestals(jtag, memories) and test_script.test_memory_offset(jtag,memories) and test_script.test_memory_switcher(jtag, memories)

    '''
    CHECK:    I/O streams
    '''
    isDCDInputOK =  test_script.test_dcd_data(probe, "Test.npy")
    isSWandGatedOK = test_script.test_switcher_output_with_gated_mode(jtag, memories, probe, 10)
    isOffsetBitOK = test_script.test_offset_bits(jtag, probe) 

    '''
    CHECK:    Memories
    '''
    isLinkOK = test_mp.test_link(jtag)
    
    
    #if isPowerOK and isJtagOK and isMemoryOK and isGatedModeOK and isOffsetBitOK:
    #    print "Success!! This CHIP is great!!!!"
    #else:
    #    print "F***... dont't use this s***!!!"
    #    misc.send_to_Mr_Cookie(0)

    
