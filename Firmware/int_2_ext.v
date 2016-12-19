
`timescale 1ns / 1ps
/////////////////////////////////////////////////
/////////////////////////////////////////////////
/*
	This module maps the 256 channels of the DCD emulator on the
	DHP 64 input channels and wise versa.
	
	a) The 256 channels of the DCD emulator is serialized and put on 
		64 channels (8 by 8 blocks, i.e. DO0[7:0], DO1[7:0], ..., DO7[7:0]) 
		as the input of the DHP.
	b) The 16 channels of the offset data from the DHP is deserialized 
		and put on 64 channels (8 by 8 blocks, i.e. DI0_i[7:0], DI1_i[7:0], ..., DI7_i[7:0]) 
	c) The 4 switcher signal are deserialized (SW_DES[15:0])
	
	the postfix "_i" marks the internal used data (referning to the DCD emulator). 

*/
/////////////////////////////////////////////////
/////////////////////////////////////////////////
module external_to_internal_data( 

    // DHP signals
     output wire  [7:0] DO0,
     output wire    [7:0] DO1,
     output wire    [7:0] DO2,
     output wire    [7:0] DO3,
     output wire    [7:0] DO4,
     output wire    [7:0] DO5,
     output wire    [7:0] DO6,
     output wire    [7:0] DO7,
     input wire     [1:0] DI0,
     input wire     [1:0] DI1,
     input wire     [1:0] DI2,
     input wire     [1:0] DI3,
     input wire     [1:0] DI4,
     input wire     [1:0] DI5,
     input wire     [1:0] DI6,
     input wire     [1:0] DI7,

     // core signals
     input wire      [31:0] DO0_i,
     input wire      [31:0] DO1_i,
     input wire      [31:0] DO2_i,
     input wire      [31:0] DO3_i,
     input wire      [31:0] DO4_i,
     input wire      [31:0] DO5_i,
     input wire      [31:0] DO6_i,
     input wire      [31:0] DO7_i,
     output wire     [7:0] DI0_i,
     output wire     [7:0] DI1_i,
     output wire     [7:0] DI2_i,
     output wire     [7:0] DI3_i,
     output wire     [7:0] DI4_i,
     output wire     [7:0] DI5_i,
     output wire     [7:0] DI6_i,
     output wire     [7:0] DI7_i,
     
     input wire     [63:0] DISABLE_DO, 
 
     //clock
     input wire     CLK_320,
     input wire     CLK_80,
     input wire     LOCKED,
     
     //switcher
     input wire     SW_CLEAR_P,
     input wire     SW_CLEAR_N,
     input wire     SW_CLK_P,
     input wire     SW_CLK_N,
     input wire     SW_FRAME_P,
     input wire     SW_FRAME_N,
     input wire     SW_GATE_P,
     input wire     SW_GATE_N,
  
     output wire  [15:0] SW_DES,
	  
	  //reset signals
	  input wire   DCD_R2S,
	  output wire  [3:0]	R2S_DES,
	  output wire DCD_R2S_BUFF,
	  
	  input wire   DCD_FSYNC,
	  output wire  [3:0]	FSYNC_DES,
	  output wire DCD_FSYNC_BUFF
 
 );

////////////////////////// BANK0 //////////////////////////
///////////////////////////////////////////////////////////
//Signal assignments to pins of bank 0 
///////////////////////////////////////////////////////////
wire SERDESSTROBE_B0;
wire IOCLK_B0;
BUFPLL
 #(.DIVIDE        (4))
 bufpll_inst_B0
	(
	//Outputs
	 .IOCLK        (IOCLK_B0),
	 .LOCK         (),
	 .SERDESSTROBE (SERDESSTROBE_B0),
	//Inputs	
	 .GCLK         (CLK_80), // GCLK must be driven by BUFG
	 .LOCKED       (LOCKED),
	 .PLLIN        (CLK_320));

serializer_4_2_1#(
  .sys_w(12), 
  .dev_w(12*4)
) u_serializer_B0(
  ////////////////////////////////////////////////////////////////
  ////////////////////////// Inputs //////////////////////////////
  // Mapping: DOX[Y] -> DOX_i[Y*4+3:Y*4]
  // Mapping: DOX[Y:Z] -> DOX_i[Y*4+3:Z*4]
  .DATA_OUT_FROM_DEVICE({DO0_i[7:0],DO0_i[23:16],DO5_i[3:0],DO5_i[19:16],DO6_i[3:0],DO6_i[23:20],DO7_i[7:0],DO7_i[23:16]}),
  .CLK_DIV_IN(CLK_80),
  .IO_RESET(!LOCKED),
  .IOCLK(IOCLK_B0),
  .SERDESSTROBE(SERDESSTROBE_B0),
  ////////////////////////////////////////////////////////////////
  ////////////////////////// Outputs /////////////////////////////
  // Mapping: DOX[Y] -> DISABLE_DO[X*8+Y]
  .DISABLE_IO({DISABLE_DO[1:0],DISABLE_DO[5:4],DISABLE_DO[40],DISABLE_DO[44],DISABLE_DO[48],DISABLE_DO[53],DISABLE_DO[57:56],DISABLE_DO[61:60]}),
  .DATA_OUT_TO_PINS({DO0[1:0],DO0[5:4],DO5[0],DO5[4],DO6[0],DO6[5],DO7[1:0],DO7[5:4]})
);

deserializer_1_2_4 #(
  .sys_w(4), 
  .dev_w(4*4)
) u_deserializer_B0(
  ////////////////////////////////////////////////////////////////
  ////////////////////////// Inputs //////////////////////////////
  .DATA_IN_FROM_PINS({DI0,DI5,DI6,DI7}),
  .CLK_DIV_IN(CLK_80),
  .IO_RESET(!LOCKED),
  .IOCLK(IOCLK_B0),
  .SERDESSTROBE(SERDESSTROBE_B0),
  ////////////////////////////////////////////////////////////////
  ////////////////////////// Outputs /////////////////////////////
  // Mapping: DIX[Y] -> DIX_i[Y*4+3:Y*4]
  // Mapping: DIX[Y:Z] -> DIX_i[Y*4+3:Z*4]
  .DATA_IN_TO_DEVICE({DI0_i,DI5_i,DI6_i,DI7_i})
);


////////////////////////// BANK1 //////////////////////////
///////////////////////////////////////////////////////////
//Signal assignments to pins of bank 1 
///////////////////////////////////////////////////////////
wire SERDESSTROBE_B1;
wire IOCLK_B1;
BUFPLL
 #(.DIVIDE        (4))
 bufpll_inst_B1
	(.IOCLK        (IOCLK_B1),
	 .LOCK         (),
	 .SERDESSTROBE (SERDESSTROBE_B1),
	 .GCLK         (CLK_80), // GCLK must be driven by BUFG
	 .LOCKED       (LOCKED),
	 .PLLIN        (CLK_320));

serializer_4_2_1#(
  .sys_w(23), 
  .dev_w(23*4)
) u_serializer_B1(
   ////////////////////////////////////////////////////////////////
  ////////////////////////// Inputs //////////////////////////////
  // Mapping: DOX[Y] -> DOX_i[Y*4+3:Y*4]
  // Mapping: DOX[Y:Z] -> DOX_i[Y*4+3:Z*4]
  .DATA_OUT_FROM_DEVICE({DO0_i[11:8],DO0_i[27:24],DO1_i[11:8],DO1_i[27:24],DO2_i[11:8],DO2_i[27:24],DO3_i[11:4],DO3_i[27:20],DO4_i[11:4],DO4_i[27:20],DO5_i[11:4],DO5_i[27:20],DO6_i[11:4],DO6_i[27:24],DO7_i[11:8],DO7_i[27:24]}),
  .CLK_DIV_IN(CLK_80),
  .IO_RESET(!LOCKED),
  .IOCLK(IOCLK_B1),
  .SERDESSTROBE(SERDESSTROBE_B1),
  ////////////////////////////////////////////////////////////////
  ////////////////////////// Outputs /////////////////////////////
  // Mapping: DOX[Y] -> DISABLE_DO[X*8+Y]
  .DISABLE_IO({DISABLE_DO[2],DISABLE_DO[6],DISABLE_DO[10],DISABLE_DO[14],DISABLE_DO[18],DISABLE_DO[22],DISABLE_DO[26:25],DISABLE_DO[30:29],DISABLE_DO[34:33],DISABLE_DO[38:37],DISABLE_DO[42:41],DISABLE_DO[46:45],DISABLE_DO[50:49],DISABLE_DO[54],DISABLE_DO[58],DISABLE_DO[62]}),
  .DATA_OUT_TO_PINS({DO0[2],DO0[6],DO1[2],DO1[6],DO2[2],DO2[6],DO3[2:1],DO3[6:5],DO4[2:1],DO4[6:5],DO5[2:1],DO5[6:5],DO6[2:1],DO6[6],DO7[2],DO7[6]})
);

////////////////////////// BANK2 //////////////////////////
///////////////////////////////////////////////////////////
//Signal assignments to pins of bank 2 
///////////////////////////////////////////////////////////
wire SERDESSTROBE_B2;
wire IOCLK_B2;
BUFPLL
 #(.DIVIDE        (4))
 bufpll_inst_B2
	(.IOCLK        (IOCLK_B2),
	 .LOCK         (),
	 .SERDESSTROBE (SERDESSTROBE_B2),
	 .GCLK         (CLK_80), // GCLK must be driven by BUFG
	 .LOCKED       (LOCKED),
	 .PLLIN        (CLK_320));


serializer_4_2_1#(
  .sys_w(18), 
  .dev_w(18*4)
) u_serializer_B2(
   ////////////////////////////////////////////////////////////////
  ////////////////////////// Inputs //////////////////////////////
  // Mapping: DOX[Y] -> DOX_i[Y*4+3:Y*4]
  // Mapping: DOX[Y:Z] -> DOX_i[Y*4+3:Z*4]
  .DATA_OUT_FROM_DEVICE({DO1_i[7:0],DO1_i[23:16],DO2_i[7:0],DO2_i[23:12],DO2_i[31:28],DO3_i[3:0],DO3_i[19:12],DO3_i[31:28],DO4_i[3:0],DO4_i[19:12],DO4_i[31:28]}),
  .CLK_DIV_IN(CLK_80),
  .IO_RESET(!LOCKED),
  .IOCLK(IOCLK_B2),
  .SERDESSTROBE(SERDESSTROBE_B2),
  ////////////////////////////////////////////////////////////////
  ////////////////////////// Outputs /////////////////////////////
  // Mapping: DOX[Y] -> DISABLE_DO[X*8+Y]
  .DISABLE_IO({DISABLE_DO[9:8],DISABLE_DO[13:12],DISABLE_DO[17:16],DISABLE_DO[21:19],DISABLE_DO[23],DISABLE_DO[24],DISABLE_DO[28:27],DISABLE_DO[31],DISABLE_DO[32],DISABLE_DO[36:35],DISABLE_DO[39]}),
  .DATA_OUT_TO_PINS({DO1[1:0],DO1[5:4],DO2[1:0],DO2[5:3],DO2[7],DO3[0],DO3[4:3],DO3[7],DO4[0],DO4[4:3],DO4[7]})
);



deserializer_1_2_4 #(
  .sys_w(8), 
  .dev_w(8*4)
) u_deserializer_B2(
  ////////////////////////////////////////////////////////////////
  ////////////////////////// Inputs //////////////////////////////
  .DATA_IN_FROM_PINS({DI1,DI2,DI3,DI4}),
  .CLK_DIV_IN(CLK_80),
  .IO_RESET(!LOCKED),
  .IOCLK(IOCLK_B2),
  .SERDESSTROBE(SERDESSTROBE_B2),
   ////////////////////////////////////////////////////////////////
  ////////////////////////// Outputs /////////////////////////////
  // Mapping: DIX[Y] -> DIX_i[Y*4+3:Y*4]
  // Mapping: DIX[Y:Z] -> DIX_i[Y*4+3:Z*4]
  .DATA_IN_TO_DEVICE({DI1_i,DI2_i,DI3_i,DI4_i})
);


////////////////////////// BANK3 //////////////////////////
///////////////////////////////////////////////////////////
//Signal assignments to pins of bank 3 
///////////////////////////////////////////////////////////
wire SERDESSTROBE_B3;
wire IOCLK_B3;
BUFPLL
 #(.DIVIDE        (4))
 bufpll_inst_B3
	(.IOCLK        (IOCLK_B3),
	 .LOCK         (),
	 .SERDESSTROBE (SERDESSTROBE_B3),
	 .GCLK         (CLK_80), // GCLK must be driven by BUFG
	 .LOCKED       (LOCKED),
	 .PLLIN        (CLK_320));


serializer_4_2_1#(
  .sys_w(11), 
  .dev_w(11*4)
) u_serializer_B3(
  ////////////////////////////////////////////////////////////////
  ////////////////////////// Inputs //////////////////////////////
  // Mapping: DOX[Y] -> DOX_i[Y*4+3:Y*4]
  // Mapping: DOX[Y:Z] -> DOX_i[Y*4+3:Z*4]
  .DATA_OUT_FROM_DEVICE({DO0_i[15:12],DO0_i[31:28],DO1_i[15:12],DO1_i[31:28],DO5_i[15:12],DO5_i[31:28],DO6_i[19:12],DO6_i[31:28],DO7_i[15:12],DO7_i[31:28]}),
  .CLK_DIV_IN(CLK_80),
  .IO_RESET(!LOCKED),
  .IOCLK(IOCLK_B3),
  .SERDESSTROBE(SERDESSTROBE_B3),
 ////////////////////////////////////////////////////////////////
  ////////////////////////// Outputs /////////////////////////////
  // Mapping: DOX[Y] -> DISABLE_DO[X*8+Y]
  .DISABLE_IO({DISABLE_DO[63:62]}),
  .DATA_OUT_TO_PINS({DO0[3],DO0[7],DO1[3],DO1[7],DO5[3],DO5[7],DO6[4:3],DO6[7],DO7[3],DO7[7]})
);

wire SW_GATE;
wire SW_CLEAR;
wire SW_FRAME;
wire SW_CLK;

deserializer_1_2_4 #(
  .sys_w(2), 
  .dev_w(2*4)
) u_deserializer_B3(
////////////////////////////////////////////////////////////////
  ////////////////////////// Inputs //////////////////////////////
  .DATA_IN_FROM_PINS({DCD_FSYNC,DCD_R2S}),
  .CLK_DIV_IN(CLK_80),
  .IO_RESET(!LOCKED),
  .IOCLK(IOCLK_B3),
  .SERDESSTROBE(SERDESSTROBE_B3),
  ////////////////////////////////////////////////////////////////
  ////////////////////////// Outputs /////////////////////////////
  .DATA_IN_TO_DEVICE({FSYNC_DES,R2S_DES}),
  .BUFFED_OUT({DCD_FSYNC_BUFF,DCD_R2S_BUFF})
);


//For switcher sequence
deserializer_1_2_4 #(
  .sys_w(4), 
  .dev_w(4*4), .NOIBUF(1)
) u_deserializer_SW(
   ////////////////////////////////////////////////////////////////
  ////////////////////////// Inputs //////////////////////////////
  .DATA_IN_FROM_PINS({SW_GATE,SW_CLEAR,SW_FRAME,SW_CLK}),
  .CLK_DIV_IN(CLK_80),
  .IO_RESET(!LOCKED),
  .IOCLK(IOCLK_B3),
  .SERDESSTROBE(SERDESSTROBE_B3),
  ////////////////////////////////////////////////////////////////
  ////////////////////////// Outputs //////////////////////////////
  .DATA_IN_TO_DEVICE(SW_DES[15:0])
);


// LVDS RX
   IBUFDS #(
      .DIFF_TERM("TRUE"),   // Differential Termination
      .IOSTANDARD("DEFAULT") // Specify the input I/O standard
   ) IBUFDS_SW_CLEAR (
      .O(SW_CLEAR),  // Buffer output
      .I(SW_CLEAR_P),  // Diff_p buffer input (connect directly to top-level port)
      .IB(SW_CLEAR_N) // Diff_n buffer input (connect directly to top-level port)
   );   
  
  IBUFDS #(
      .DIFF_TERM("TRUE"),   // Differential Termination
      .IOSTANDARD("DEFAULT") // Specify the input I/O standard
   ) IBUFDS_SW_CLK (
      .O(SW_CLK),  // Buffer output
      .I(SW_CLK_P),  // Diff_p buffer input (connect directly to top-level port)
      .IB(SW_CLK_N) // Diff_n buffer input (connect directly to top-level port)
   );   
  
  IBUFDS #(
      .DIFF_TERM("TRUE"),   // Differential Termination
      .IOSTANDARD("DEFAULT") // Specify the input I/O standard
   ) IBUFDS_SW_FRAME (
      .O(SW_FRAME),  // Buffer output
      .I(SW_FRAME_P),  // Diff_p buffer input (connect directly to top-level port)
      .IB(SW_FRAME_N) // Diff_n buffer input (connect directly to top-level port)
   );   
  
  IBUFDS #(
      .DIFF_TERM("TRUE"),   // Differential Termination
      .IOSTANDARD("DEFAULT") // Specify the input I/O standard
   ) IBUFDS_SW_GATE (
      .O(SW_GATE),  // Buffer output
      .I(SW_GATE_P),  // Diff_p buffer input (connect directly to top-level port)
      .IB(SW_GATE_N) // Diff_n buffer input (connect directly to top-level port)
   );

      
endmodule 
   
