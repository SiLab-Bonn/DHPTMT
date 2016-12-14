// file: serializer_4_2_1.v
// (c) Copyright 2009 - 2011 Xilinx, Inc. All rights reserved.
// 
// This file contains confidential and proprietary information
// of Xilinx, Inc. and is protected under U.S. and
// international copyright and other intellectual property
// laws.
// 
// DISCLAIMER
// This disclaimer is not a license and does not grant any
// rights to the materials distributed herewith. Except as
// otherwise provided in a valid license issued to you by
// Xilinx, and to the maximum extent permitted by applicable
// law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
// WITH ALL FAULTS, AND XILINX HEREBY DISCLAIMS ALL WARRANTIES
// AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
// BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
// INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
// (2) Xilinx shall not be liable (whether in contract or tort,
// including negligence, or under any other theory of
// liability) for any loss or damage of any kind or nature
// related to, arising under or in connection with these
// materials, including for any direct, or any indirect,
// special, incidental, or consequential loss or damage
// (including loss of data, profits, goodwill, or any type of
// loss or damage suffered as a result of any action brought
// by a third party) even if such damage or loss was
// reasonably foreseeable or Xilinx had been advised of the
// possibility of the same.
// 
// CRITICAL APPLICATIONS
// Xilinx products are not designed or intended to be fail-
// safe, or for use in any application requiring fail-safe
// performance, such as life-support or safety devices or
// systems, Class III medical devices, nuclear facilities,
// applications related to the deployment of airbags, or any
// other applications that could lead to death, personal
// injury, or severe property or environmental damage
// (individually and collectively, "Critical
// Applications"). Customer assumes the sole risk and
// liability of any use of Xilinx products in Critical
// Applications, subject only to applicable laws and
// regulations governing limitations on product liability.
// 
// THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
// PART OF THIS FILE AT ALL TIMES.
//----------------------------------------------------------------------------
// User entered comments
//----------------------------------------------------------------------------
// None
//----------------------------------------------------------------------------

`timescale 1ps/1ps

(* CORE_GENERATION_INFO = "serializer_4_2_1,selectio_wiz_v4_1,{component_name=serializer_4_2_1,bus_dir=OUTPUTS,bus_sig_type=SINGLE,bus_io_std=LVCMOS25,use_serialization=true,use_phase_detector=false,serialization_factor=4,enable_bitslip=false,enable_train=false,system_data_width=1,bus_in_delay=NONE,bus_out_delay=NONE,clk_sig_type=SINGLE,clk_io_std=LVCMOS25,clk_buf=BUFPLL,active_edge=RISING,clk_delay=NONE,v6_bus_in_delay=NONE,v6_bus_out_delay=NONE,v6_clk_buf=BUFIO,v6_active_edge=NOT_APP,v6_ddr_alignment=SAME_EDGE_PIPELINED,v6_oddr_alignment=SAME_EDGE,ddr_alignment=C0,v6_interface_type=NETWORKING,interface_type=NETWORKING,v6_bus_in_tap=0,v6_bus_out_tap=0,v6_clk_io_std=LVCMOS18,v6_clk_sig_type=SINGLE}" *)

module serializer_4_2_1
   // width of the data for the system
 #(parameter sys_w = 1,
   // width of the data for the device
   parameter dev_w = 4)
 (
  // From the device out to the system
  input  wire [dev_w-1:0] DATA_OUT_FROM_DEVICE,
  output wire [sys_w-1:0] DATA_OUT_TO_PINS,
  input  wire [sys_w-1:0] DISABLE_IO,     // disable output buffers
  input  wire             CLK_DIV_IN,    // Slow clock input from PLL/MMCM
  input  wire             IO_RESET,
  input wire SERDESSTROBE,
  input wire IOCLK
  );
  localparam         num_serial_bits = dev_w/sys_w;
  // Signal declarations
  ////------------------------------
  wire               clock_enable = 1'b1;
  // Before the buffer
  wire   [sys_w-1:0] data_out_to_pins_int;
  // Between the delay and serdes
  wire   [sys_w-1:0] data_out_to_pins_predelay;
  // Array to use intermediately from the serdes to the internal
  //  devices. bus "0" is the leftmost bus
  wire [num_serial_bits-1:0]  oserdes_d[sys_w-1:0];   // fills in starting with 7
  // Create the clock logic
	
	wire [sys_w-1:0]local_disable_io;
	

  // We have multiple bits- step over every bit, instantiating the required elements
  genvar pin_count;
  genvar i,j;
  generate for (pin_count = 0; pin_count < sys_w; pin_count = pin_count + 1) begin: pins
    // Instantiate the buffers
    ////------------------------------
    // Instantiate a buffer for every bit of the data bus
    OBUFT
      #(.IOSTANDARD ("LVCMOS25"))
     obuf_inst
       (.O          (DATA_OUT_TO_PINS    [pin_count]),
        .I          (data_out_to_pins_int[pin_count]),
        .T          (local_disable_io[pin_count]));

    // Pass through the delay
    ////-------------------------------
   assign data_out_to_pins_int[pin_count]    = data_out_to_pins_predelay[pin_count];
 
     // Instantiate the serdes primitive
     ////------------------------------
     // local wire only for use in this generate loop
     wire cascade_ms_d;
     wire cascade_ms_t;
     wire cascade_sm_d;
     wire cascade_sm_t;

     // declare the oserdes
     OSERDES2
       #(.DATA_RATE_OQ   ("SDR"),
         .DATA_RATE_OT   ("SDR"),
         .TRAIN_PATTERN  (0),
         .DATA_WIDTH     (num_serial_bits),
         .SERDES_MODE    ("NONE"),
         .OUTPUT_MODE    ("SINGLE_ENDED"))
      oserdes2_master
       (.D1         (oserdes_d[pin_count][3]),
        .D2         (oserdes_d[pin_count][2]),
        .D3         (oserdes_d[pin_count][1]),
        .D4         (oserdes_d[pin_count][0]),
        .T1         (DISABLE_IO[pin_count]),
        .T2         (DISABLE_IO[pin_count]),
        .T3         (DISABLE_IO[pin_count]),
        .T4         (DISABLE_IO[pin_count]),
        .SHIFTIN1   (1'b1),
        .SHIFTIN2   (1'b1),
        .SHIFTIN3   (1'b1),
        .SHIFTIN4   (1'b1),
        .SHIFTOUT1  (),
        .SHIFTOUT2  (),
        .SHIFTOUT3  (),
        .SHIFTOUT4  (),
        .TRAIN      (1'b0),
        .OCE        (clock_enable),
        .CLK0       (IOCLK),
        .CLK1       (1'b0),
        .CLKDIV     (CLK_DIV_IN),
        .OQ         (data_out_to_pins_predelay[pin_count]),
        .TQ         (local_disable_io[pin_count]),
        .IOCE       (SERDESSTROBE),
        .TCE        (clock_enable),
        .RST        (IO_RESET));


     // Concatenate the serdes outputs together. Keep the timesliced
     //   bits together, and placing the earliest bits on the right
     //   ie, if data comes in 0, 1, 2, 3, 4, 5, 6, 7, ...
     //       the output will be 3210, 7654, ...
     ////---------------------------------------------------------
     //wire [num_serial_bits-1:0]  oserdes_d[sys_w-1:0];   // fills in starting with 7
     
     
  end
  
  	for (i=0;i<sys_w;i=i+1) begin : gen_oserdes
	  	for (j=0;j<num_serial_bits;j=j+1) begin : gen_oserdes_ass
	  		assign oserdes_d[i][j] = DATA_OUT_FROM_DEVICE[num_serial_bits*i + j];
	  	end
  	end
  
//     for (slice_count = 0; slice_count < sys_w; slice_count = slice_count + 1) begin: out_slices
//     	assign oserdes_d[slice_count] = DATA_OUT_FROM_DEVICE[(slice_count+1)*num_serial_bits-1:slice_count*num_serial_bits];
//     end
  
  
  
  endgenerate

endmodule
