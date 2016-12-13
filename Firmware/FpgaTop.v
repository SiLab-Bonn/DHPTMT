
`default_nettype none

module ProbeCardFpgaTop(
	output wire GPIO_1,
	input wire DCD_CLK,
	input wire GPIO_0,
	
	output wire [7:0] DO0,
	output wire [7:0] DO1,
	output wire [7:0] DO2,
	output wire [7:0] DO3,
	output wire [7:0] DO4,
	output wire [7:0] DO5,
	output wire [7:0] DO6,
	output wire [7:0] DO7,
	
	input wire [1:0] DI0,
	input wire [1:0] DI1,
	input wire [1:0] DI2,
	input wire [1:0] DI3,
	input wire [1:0] DI4,
	input wire [1:0] DI5,
	input wire [1:0] DI6,
	input wire [1:0] DI7,
	
	input wire DCD_R2S,
	input wire EN_IO,
	
	output wire DCD_TDO,
	input wire DCD_TDI,
	input wire DCD_TMS,
	input wire DCD_TCK,
	input wire DCD_TRST,
	 
	input wire SW_CLEAR_P,
	input wire SW_CLEAR_N,
	input wire SW_GATE_P,
	input wire SW_GATE_N,     
	input wire SW_CLK_P,
	input wire SW_CLK_N,     
	input wire SW_FRAME_P,
	input wire SW_FRAME_N,
	 
	output wire FPGA_TX,
	input wire FPGA_RX,
	 
	output wire SCL,
	inout wire SDA
     
);

localparam GPIO_BASEADDR        	= 32'h0000_1000;
localparam GPIO_HIGHADDR        	= 32'h0000_1fff;

localparam PULSER_R2S_BASEADDR    	= 32'h0001_0000;
localparam PULSER_R2S_HIGHADDR    	= 32'h0001_1000;

localparam PULSER_FSYNC_BASEADDR    = 32'h0001_4000;
localparam PULSER_FSYNC_HIGHADDR    = 32'h0001_5000;

localparam I2C_BASEADDR         	= 32'h0000_0000;
localparam I2C_HIGHADDR         	= 32'h0000_0008; 

localparam SEQ_GEN_BASEADDR     	= 32'h1000_0000;
localparam SEQ_GEN_HIGHADDR     	= 32'h1fff_ffff;
 
localparam SEQ_REC_BASEADDR     	= 32'h2000_0000;
localparam SEQ_REC_HIGHADDR     	= 32'h2fff_ffff;


wire main_clk, DCD_FSYNC;
//clock and reset
assign     main_clk      =  DCD_CLK; 
assign     DCD_FSYNC     =  GPIO_0;
/////////////////////////////////////////////////////////
//Synchronization signals row2sync
reg [1:0] r2s_edge;
wire r2s_strobe;
always @(posedge CLK_320) r2s_edge <= {r2s_edge[0], DCD_R2S_BUFF};
assign r2s_strobe = (r2s_edge == 2'b01);

reg [1:0] fsync_edge;
wire fsync_strobe;
always @(posedge CLK_320) fsync_edge <= {fsync_edge[0], DCD_FSYNC_BUFF};
assign fsync_strobe = (fsync_edge == 2'b01);

assign GPIO_1 = r2s_strobe; 
/////////////////////////////////////////////////////////

wire CLK_80, CLK_320, CLK_160, LOCKED;
clk_gen i_clk_gen(
	.CLK_IN_320(main_clk),
	.CLK_OUT_320(CLK_320),
	.CLK_OUT_80(CLK_80),
	.LOCKED(LOCKED)
);


wire BUS_RST, BUS_CLK;
//for main_clk = CLK_320 =  4x 77.23 MHz
// DIV = CLK_320 / Baudrate / 4
//parameter UART_CLK_DIVISOR = 335;     // BAUDRATE 230400 
parameter UART_CLK_DIVISOR = 168;     // BAUDRATE 460800 

clock_divider #(.DIVISOR(UART_CLK_DIVISOR) 
	) i_clock_divisor_uart (
	.CLK(CLK_320),
	.RESET(1'b0),
	.CE(),
	.CLOCK(BUS_CLK)
);


wire	[31:0] DO0_i;  wire [7:0] DI0_i; 
wire	[31:0] DO1_i;  wire [7:0] DI1_i; 
wire	[31:0] DO2_i;  wire [7:0] DI2_i; 
wire	[31:0] DO3_i;  wire [7:0] DI3_i; 
wire	[31:0] DO4_i;  wire [7:0] DI4_i; 
wire	[31:0] DO5_i;  wire [7:0] DI5_i; 
wire	[31:0] DO6_i;  wire [7:0] DI6_i; 
wire	[31:0] DO7_i;  wire [7:0] DI7_i; 

wire    [3:0] ROW2SYNC_DATA;
wire    [15:0] SW_DATA;
wire    [63:0] DISABLE_DO;
 
external_to_internal_data u_external_to_internal_data (
  // external
	.CLK_320(CLK_320),
	.CLK_80(CLK_80),
	.LOCKED(LOCKED),
	.DISABLE_DO(DISABLE_DO & {64{EN_IO}}),
	
	.DI0(DI0),
	.DI1(DI1),
	.DI2(DI2),
	.DI3(DI3),
	.DI4(DI4),
	.DI5(DI5),
	.DI6(DI6),
	.DI7(DI7),
	.DO0(DO0),
	.DO1(DO1),
	.DO2(DO2),
	.DO3(DO3),
	.DO4(DO4),
	.DO5(DO5),
	.DO6(DO6),
	.DO7(DO7),
	
	.SW_CLK_P(SW_CLK_P),
	.SW_CLK_N(SW_CLK_N),
	.SW_FRAME_P(SW_FRAME_P),
	.SW_FRAME_N(SW_FRAME_N),
	.SW_GATE_P(SW_GATE_P),
	.SW_GATE_N(SW_GATE_N),
	.SW_CLEAR_P(SW_CLEAR_P),
	.SW_CLEAR_N(SW_CLEAR_N),
	
	// internal
	.DO0_i(DO0_i),
	.DO1_i(DO1_i),
	.DO2_i(DO2_i),
	.DO3_i(DO3_i),
	.DO4_i(DO4_i),
	.DO5_i(DO5_i),
	.DO6_i(DO6_i),
	.DO7_i(DO7_i),
	.DI0_i(DI0_i),
	.DI1_i(DI1_i),
	.DI2_i(DI2_i),
	.DI3_i(DI3_i),
	.DI4_i(DI4_i),
	.DI5_i(DI5_i),
	.DI6_i(DI6_i),
	.DI7_i(DI7_i),
	
	.SW_DES(SW_DATA),
	
	.DCD_R2S(DCD_R2S),
	.R2S_DES(ROW2SYNC_DATA),
	.DCD_R2S_BUFF(DCD_R2S_BUFF),
	
	.DCD_FSYNC(GPIO_0),
	.FSYNC_DES(),
	.DCD_FSYNC_BUFF(DCD_FSYNC_BUFF)
  
);


reset_gen #( .CNT(4) ) i_reset_gen (.CLK(BUS_CLK), .RST(BUS_RST));

wire [7:0] BUS_DATA;
wire [31:0] BUS_ADD;
wire BUS_WR, BUS_RD;

uart_master i_uart (
    .UART_CLK_X4(BUS_CLK),
    .UART_RST(BUS_RST),
    .UART_RX(FPGA_RX),
    .UART_TX(FPGA_TX),
    .BUS_DATA(BUS_DATA),
    .BUS_ADD(BUS_ADD),
    .BUS_WR(BUS_WR),
    .BUS_RD(BUS_RD)
);

gpio #( .BASEADDR(GPIO_BASEADDR), 
        .HIGHADDR(GPIO_HIGHADDR),
        .ABUSWIDTH(32),
        .IO_WIDTH(64),
        .IO_DIRECTION(64'hffff_ffff_ffff_ffff),
        .IO_TRI(64'h0)
    ) i_gpio
(
    .BUS_CLK(BUS_CLK),
    .BUS_RST(BUS_RST),
    .BUS_ADD(BUS_ADD),
    .BUS_DATA(BUS_DATA),
    .BUS_RD(BUS_RD),
    .BUS_WR(BUS_WR),
    .IO(DISABLE_DO)
);
    
/////////////////////////////////////////////////////////
//Pulsgenerator for dcd_data sw_data
/////////////////////////////////////////////////////////    
wire switcher_pulse;
wire dcd_pulse;

// pulse width has to be at least 5x T(CLK_320)
pulse_gen #( .BASEADDR(PULSER_R2S_BASEADDR),
             .HIGHADDR(PULSER_R2S_HIGHADDR),
             .ABUSWIDTH(32)
	) i_pulser_dcd
(
    .BUS_CLK(BUS_CLK),
    .BUS_RST(BUS_RST),
    .BUS_ADD(BUS_ADD),
    .BUS_DATA(BUS_DATA),
    .BUS_RD(BUS_RD),
    .BUS_WR(BUS_WR),
    
    .PULSE_CLK(CLK_320),
    .EXT_START(r2s_strobe),
    .PULSE(dcd_pulse)
);  

pulse_gen #( .BASEADDR(PULSER_FSYNC_BASEADDR),
		     .HIGHADDR(PULSER_FSYNC_HIGHADDR),
		     .ABUSWIDTH(32)
	) i_pulser_switcher
(
    .BUS_CLK(BUS_CLK),
    .BUS_RST(BUS_RST),
    .BUS_ADD(BUS_ADD),
    .BUS_DATA(BUS_DATA),
    .BUS_RD(BUS_RD),
    .BUS_WR(BUS_WR),
    
    .PULSE_CLK(CLK_80),
    .EXT_START(fsync_strobe),
    .PULSE(switcher_pulse)
);  
 
// DCD data generator
wire [4*8*8-1:0] DO_DATA;
assign {DO7_i,DO6_i,DO5_i,DO4_i,DO3_i,DO2_i,DO1_i,DO0_i} = DO_DATA;
seq_gen #( .BASEADDR(SEQ_GEN_BASEADDR), 
		   .HIGHADDR(SEQ_GEN_HIGHADDR),
		   .ABUSWIDTH(32),
		   .MEM_BYTES(16*1024), 
		   .OUT_BITS(256) 
	) i_seq_gen
(
    .BUS_CLK(BUS_CLK),
    .BUS_RST(BUS_RST),
    .BUS_ADD(BUS_ADD),
    .BUS_DATA(BUS_DATA),
    .BUS_RD(BUS_RD),
    .BUS_WR(BUS_WR),

    .SEQ_EXT_START(dcd_pulse),
    .SEQ_CLK(CLK_80),
    .SEQ_OUT(DO_DATA)
);
/////////////////////////////////////////////////////////

// Switcher and Offset 
wire [4*8*2-1:0] DI_DATA;
assign DI_DATA = {DI7_i,DI6_i,DI5_i,DI4_i,DI3_i,DI2_i,DI1_i,DI0_i};
seq_rec #( .BASEADDR(SEQ_REC_BASEADDR), 
		   .HIGHADDR(SEQ_REC_HIGHADDR),
		   .ABUSWIDTH(32),
		   .MEM_BYTES(16*1024), 
		   .IN_BITS(256)
	) i_seq_rec
(
    .BUS_CLK(BUS_CLK),
    .BUS_RST(BUS_RST),
    .BUS_ADD(BUS_ADD),
    .BUS_DATA(BUS_DATA),
    .BUS_RD(BUS_RD),
    .BUS_WR(BUS_WR),
	 
	.SEQ_EXT_START(switcher_pulse),
    .SEQ_CLK(CLK_80),
    .SEQ_IN({128'b0, 44'b0,ROW2SYNC_DATA,SW_DATA,DI_DATA})
);

wire i2c_error;
i2c #( .BASEADDR(I2C_BASEADDR), 
	   .HIGHADDR(I2C_HIGHADDR),
	   .ABUSWIDTH(32)
	) i2c_mod
(
	.BUS_CLK(BUS_CLK),
    .BUS_RST(BUS_RST),
    .BUS_ADD(BUS_ADD),
    .BUS_DATA(BUS_DATA),
    .BUS_RD(BUS_RD),
    .BUS_WR(BUS_WR),

    .i2c_sda(SDA),
    .i2c_scl(SCL),
	.busy(),
	.error(i2c_error)
);


jtag i_dcd_jtag(
	//JTAG signals
	.tms(DCD_TMS), 
	.tck(DCD_TCK), 
	.trst(DCD_TRST), 
	.tdi(DCD_TDI),
	.tdo(DCD_TDO),
	
	//connecting the global shift register (full custom - analog block)
	.clk_gsr(),
	.data_to_gsr(),
	.load_gsr(),
	.shift_gsr(),
	.read_back_gsr(),
	.data_from_gsr(1'b1),
	
	//connecting the pixel shift register (full custom - analog block)
	.data_to_psr(),
	.clk_psr(),
	.load_psr(),
	.shift_psr(),
	.read_back_psr(),
	.data_from_psr(1'b0),  
	
	//chip's input signals with BS input cell
	//From Pad
	.clk_fromPad(1'b0),
	.sync_reset_fromPad(1'b0),
	.test_injection_en_fromPad(1'b0),
	.pedestals_in0_fromPad(2'b0),
	.pedestals_in1_fromPad(2'b0),
	.pedestals_in2_fromPad(2'b0),
	.pedestals_in3_fromPad(2'b0),
	.pedestals_in4_fromPad(2'b0),
	.pedestals_in5_fromPad(2'b0),
	.pedestals_in6_fromPad(2'b0),
	.pedestals_in7_fromPad(2'b0),
	//To Core
	.clk_toCore(),
	.sync_reset_toCore(),
	.test_injection_en_toCore(),
	.pedestals_in0_toCore(),  
	.pedestals_in1_toCore(),  
	.pedestals_in2_toCore(),  
	.pedestals_in3_toCore(),  
	.pedestals_in4_toCore(),  
	.pedestals_in5_toCore(),  
	.pedestals_in6_toCore(),  
	.pedestals_in7_toCore(),  
	
	
	//chip's output signals with BS output cell
	//To Pad:
	.return_clk_toPad(),
	.data_output_stream0_toPad(),
	.data_output_stream1_toPad(),
	.data_output_stream2_toPad(),
	.data_output_stream3_toPad(),
	.data_output_stream4_toPad(),
	.data_output_stream5_toPad(),
	.data_output_stream6_toPad(),
	.data_output_stream7_toPad(),
	//From Core:
	.return_clk_fromCore(1'b0),
	.data_output_stream0_fromCore(8'b0),
	.data_output_stream1_fromCore(8'b0),
	.data_output_stream2_fromCore(8'b0),
	.data_output_stream3_fromCore(8'b0),
	.data_output_stream4_fromCore(8'b0),
	.data_output_stream5_fromCore(8'b0),
	.data_output_stream6_fromCore(8'b0),
	.data_output_stream7_fromCore(8'b0)
);

endmodule