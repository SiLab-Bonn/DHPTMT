from DHPTMT import DHPTMT

#GLOBAL DEFINES
DHPTVERSION = "1.2b"

SOFTWAREVERSION = 1.0
DHE = "PXD:H1031:"

if __name__ == "__main__":
    configFileName = "Probecard.yaml"
    outputPath = "/home/user/NeedleCardTest/Data/DHPT%s"%DHPTVERSION
    mp = DHPTMT(configFileName, outputPath, SOFTWAREVERSION, DHPTVERSION, DHE)
    mp.disable_voltages()
    mp.init_voltages()

    '''
    CHECK:    POWER CONSUMPTION
    '''

    is_power_oK, msg = mp.test_power_consumption()
    if not is_power_oK:
        print msg
    mp.set_dcd_ref_voltage(voltage=0.9, unit="V")
    mp.dhp.regs.set_default_value_for_dhp_registers()

    '''
    CHECK:    JTAG 
    '''
    jtag_n1_is_ok, msg = mp.test_jtag_n1()
    if not jtag_n1_is_ok:
        print msg

    jtag_n2_is_ok, msg = mp.test_jtag_n2()
    if not jtag_n2_is_ok:
        print msg

    '''
    CHECK:    Memories
    '''
    mem_ped_is_ok, msg = mp.test_pedestal_memory()
    if not mem_ped_is_ok:
        print msg

    mem_offset_is_ok, msg = mp.test_offset_memory()
    if not mem_offset_is_ok:
        print msg

    mem_sw_is_ok, msg = mp.test_switcher_memory()
    if not mem_sw_is_ok:
        print msg

    '''
    CHECK:    I/O streams
    '''
    data_is_ok, msg = mp.test_dcd_to_dhp_data(mp.dhp.regs['last_row'])
    if not data_is_ok:
        print msg

    offset_is_ok, msg = mp.test_dhp_to_dcd_offset_data(mp.dhp.regs['last_row'])
    if not offset_is_ok:
        print msg

    sw_is_ok, msg = mp.test_dhp_to_switcher_data_normal_and_gated_mode(mp.dhp.regs['last_row'])
    if not sw_is_ok:
        print msg


    '''
    CHECK:    HS link 
    '''
    hs_link_ok, msg = mp.test_high_speed_link(configpath='/home/daq/lab_framework/calibrations')

    '''
    CHECK:    ZS 
    '''
    zs_ok, msg = mp.test_zero_suppressed_data()

