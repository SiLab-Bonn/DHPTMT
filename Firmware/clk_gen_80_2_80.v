/**
 * ------------------------------------------------------------
 * Copyright (c) All rights reserved 
 * SiLab, Institute of Physics, University of Bonn
 * ------------------------------------------------------------
 *
 * SVN revision information:
 *  $Rev::                       $:
 *  $Author::                    $:
 *  $Date::                      $:
 */
 
//----------------------------------------------------------------------------
// "Output    Output      Phase     Duty      Pk-to-Pk        Phase"
// "Clock    Freq (MHz) (degrees) Cycle (%) Jitter (ps)  Error (ps)"
//----------------------------------------------------------------------------
// CLK_OUT1___320.000______0.000______50.0______120.482____189.366
// CLK_OUT2____80.000______0.000______50.0______158.645____189.366
//
//----------------------------------------------------------------------------
// "Input Clock   Freq (MHz)    Input Jitter (UI)"
//----------------------------------------------------------------------------
// __primary_________320.000____________0.01

`timescale 1ps/1ps 


module clk_gen_80_2_80(
      input wire        CLK_IN_80,
      // Clock out ports
      output wire       CLK_OUT_80,
      // Status and control signals
      output wire        LOCKED
);

   wire clkin1;
	wire clkout0;
	wire clkout1;

     // Input buffering
  //------------------------------------
  BUFG clkin1_buf
   (.O (clkin1),
    .I (CLK_IN_80));


  // Clocking primitive
  //------------------------------------
  // Instantiation of the PLL primitive
  //    * Unused inputs are tied off
  //    * Unused outputs are labeled unused
  wire [15:0] do_unused;
  wire        drdy_unused;
  wire        clkfbout;
//  wire        clkout2_unused;
//  wire        clkout3_unused;
//  wire        clkout4_unused;
//  wire        clkout5_unused;
  wire CLKFB_IN;
  
  PLL_BASE
  #(.BANDWIDTH              ("OPTIMIZED"),
    .CLK_FEEDBACK           ("CLKFBOUT"),
    .COMPENSATION           ("SYSTEM_SYNCHRONOUS"),
    .DIVCLK_DIVIDE          (1),
    .CLKFBOUT_MULT          (2),
    .CLKFBOUT_PHASE         (0.000),
    .CLKOUT0_DIVIDE         (2),
    .CLKOUT0_PHASE          (0.000),
    .CLKOUT0_DUTY_CYCLE     (0.500),
    .CLKOUT1_DIVIDE         (1),
    .CLKOUT1_PHASE          (0.000),
    .CLKOUT1_DUTY_CYCLE     (0.500),
	 .CLKOUT2_DIVIDE         (),
    .CLKOUT2_PHASE          (),
    .CLKOUT2_DUTY_CYCLE     (),
    .CLKIN_PERIOD           (3.125*4),
    .REF_JITTER             (0.010))
  pll_base_inst
    // Output clocks
   (.CLKFBOUT              (clkfbout),
    .CLKOUT0               (clkout0),
    .CLKOUT1               (clkout1),
    .CLKOUT2               (),
    .CLKOUT3               (),
    .CLKOUT4               (),
    .CLKOUT5               (),
    // Status and control signals
    .LOCKED                (LOCKED),
    .RST                   (1'b0),
     // Input clock control
    .CLKFBIN               (CLKFB_IN),
    .CLKIN                 (clkin1));

  // Output buffering
  //-----------------------------------
  
  BUFG clkf_buf
   (.O (CLKFB_IN),
    .I (clkfbout));


  BUFG clkout1_buf
   (.O   (CLK_OUT_80),
    .I   (clkout1));
   
	assign CLK_OUT_80 = clkout0;
	//assign CLK_OUT_160 = clkout2;
  //BUFG clkout0_buf
  // (.O   (CLK_OUT_320),
  //  .I   (clkout0));
    
    /*BUFG clkout2_buf
   (.O   (CLK_OUT_160),
    .I   (clkout2));*/

endmodule
