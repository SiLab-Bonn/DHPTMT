

module jtag (
  //JTAG signals
  input     wire            tms, 
  input     wire            tck, 
  input     wire            trst, 
  input     wire            tdi,
  output    wire            tdo,
  
  //connecting the global shift register (full custom - analog block)
  output    wire            data_to_gsr,
  output    wire            clk_gsr,
  output    wire            load_gsr,
  output    wire            shift_gsr,
  output    wire            read_back_gsr,
  input     wire            data_from_gsr,
  
  //connecting the pixel shift register (full custom - analog block)
  output    wire            data_to_psr,
  output    wire            clk_psr,
  output    wire            load_psr,
  output    wire            shift_psr,
  output    wire            read_back_psr,
  input     wire            data_from_psr,  
  
  //chip's input signals with BS input cell
  //From Pad
  input     wire            clk_fromPad,
  input     wire            sync_reset_fromPad,
  input     wire            test_injection_en_fromPad,
  input     wire    [1:0]   pedestals_in0_fromPad,
  input     wire    [1:0]   pedestals_in1_fromPad,
  input     wire    [1:0]   pedestals_in2_fromPad,
  input     wire    [1:0]   pedestals_in3_fromPad,
  input     wire    [1:0]   pedestals_in4_fromPad,
  input     wire    [1:0]   pedestals_in5_fromPad,
  input     wire    [1:0]   pedestals_in6_fromPad,
  input     wire    [1:0]   pedestals_in7_fromPad,
  //To Core
  output    wire            clk_toCore,
  output    wire            sync_reset_toCore,
  output    wire            test_injection_en_toCore,
  output    wire    [1:0]   pedestals_in0_toCore,  
  output    wire    [1:0]   pedestals_in1_toCore,  
  output    wire    [1:0]   pedestals_in2_toCore,  
  output    wire    [1:0]   pedestals_in3_toCore,  
  output    wire    [1:0]   pedestals_in4_toCore,  
  output    wire    [1:0]   pedestals_in5_toCore,  
  output    wire    [1:0]   pedestals_in6_toCore,  
  output    wire    [1:0]   pedestals_in7_toCore,  
  
  
  //chip's output signals with BS output cell
  //To Pad:
  output    wire            return_clk_toPad,
  output    wire    [7:0]   data_output_stream0_toPad,
  output    wire    [7:0]   data_output_stream1_toPad,
  output    wire    [7:0]   data_output_stream2_toPad,
  output    wire    [7:0]   data_output_stream3_toPad,
  output    wire    [7:0]   data_output_stream4_toPad,
  output    wire    [7:0]   data_output_stream5_toPad,
  output    wire    [7:0]   data_output_stream6_toPad,
  output    wire    [7:0]   data_output_stream7_toPad,
  //From Core:
  input     wire            return_clk_fromCore,
  input     wire    [7:0]   data_output_stream0_fromCore,
  input     wire    [7:0]   data_output_stream1_fromCore,
  input     wire    [7:0]   data_output_stream2_fromCore,
  input     wire    [7:0]   data_output_stream3_fromCore,
  input     wire    [7:0]   data_output_stream4_fromCore,
  input     wire    [7:0]   data_output_stream5_fromCore,
  input     wire    [7:0]   data_output_stream6_fromCore,
  input     wire    [7:0]   data_output_stream7_fromCore

);

localparam  IR_LENGTH       = 4;
localparam  EXTEST          = 4'b0000;
localparam  SAMPLE_PRELOAD  = 4'b0001;
localparam  IDCODE          = 4'b0010;
localparam  BYPASS          = 4'b1111;
localparam  SEL_GLOBAL_SR   = 4'b0100;
localparam  SEL_PIXEL_SR    = 4'b1000;

//JTAG wires
wire                    captureDR;
wire                    captureIR;
wire                    shiftDR;
wire                    shiftIR;
wire                    pauseDR;
wire                    updateDR;
wire                    updateIR;

wire                    instruction_tdo;
wire                    idcode_tdo;
wire    [IR_LENGTH-1:0] latched_jtag_ir;
reg                     extest_select;
reg                     sample_preload_select;
reg                     idcode_select;
reg                     bypass_select;
reg                     global_sr_select;
reg                     pixel_sr_select;

//wire to connect the boundary scan chain
wire    [82:0]          bs_chain;
wire                    bs_chain_tdo;


//Instantiations of BS cells
//Note : The order of cells in the chain is physical aware!

//Column Pair 0
jtag_OutputCell BS_output_cell_data_output_stream00( 
  .FromCore(data_output_stream0_fromCore[0]),
  .FromPreviousBSCell(tdi), //this is the first cell in the chain!
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream0_toPad[0]),
  .ToNextBSCell(bs_chain[0])
);

jtag_OutputCell BS_output_cell_data_output_stream01( 
  .FromCore(data_output_stream0_fromCore[1]),
  .FromPreviousBSCell(bs_chain[0]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream0_toPad[1]),
  .ToNextBSCell(bs_chain[1])
);

jtag_OutputCell BS_output_cell_data_output_stream02( 
  .FromCore(data_output_stream0_fromCore[2]),
  .FromPreviousBSCell(bs_chain[1]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream0_toPad[2]),
  .ToNextBSCell(bs_chain[2])
);

jtag_OutputCell BS_output_cell_data_output_stream03( 
  .FromCore(data_output_stream0_fromCore[3]),
  .FromPreviousBSCell(bs_chain[2]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream0_toPad[3]),
  .ToNextBSCell(bs_chain[3])
);

jtag_OutputCell BS_output_cell_data_output_stream04( 
  .FromCore(data_output_stream0_fromCore[4]),
  .FromPreviousBSCell(bs_chain[3]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream0_toPad[4]),
  .ToNextBSCell(bs_chain[4])
);

jtag_OutputCell BS_output_cell_data_output_stream05( 
  .FromCore(data_output_stream0_fromCore[5]),
  .FromPreviousBSCell(bs_chain[4]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream0_toPad[5]),
  .ToNextBSCell(bs_chain[5])
);

jtag_OutputCell BS_output_cell_data_output_stream06( 
  .FromCore(data_output_stream0_fromCore[6]),
  .FromPreviousBSCell(bs_chain[5]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream0_toPad[6]),
  .ToNextBSCell(bs_chain[6])
);

jtag_OutputCell BS_output_cell_data_output_stream07( 
  .FromCore(data_output_stream0_fromCore[7]),
  .FromPreviousBSCell(bs_chain[6]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream0_toPad[7]),
  .ToNextBSCell(bs_chain[7])
);

jtag_InputCell BS_input_cell_pedestals_in00_I ( 
  .InputPin(pedestals_in0_fromPad[0]),
  .FromPreviousBSCell(bs_chain[7]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[8]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in0_toCore[0])
);

jtag_InputCell BS_input_cell_pedestals_in01_I ( 
  .InputPin(pedestals_in0_fromPad[1]),
  .FromPreviousBSCell(bs_chain[8]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[9]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in0_toCore[1])
);





//Column Pair 1
jtag_OutputCell BS_output_cell_data_output_stream10( 
  .FromCore(data_output_stream1_fromCore[0]),
  .FromPreviousBSCell(bs_chain[9]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream1_toPad[0]),
  .ToNextBSCell(bs_chain[10])
);

jtag_OutputCell BS_output_cell_data_output_stream11( 
  .FromCore(data_output_stream1_fromCore[1]),
  .FromPreviousBSCell(bs_chain[10]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream1_toPad[1]),
  .ToNextBSCell(bs_chain[11])
);

jtag_OutputCell BS_output_cell_data_output_stream12( 
  .FromCore(data_output_stream1_fromCore[2]),
  .FromPreviousBSCell(bs_chain[11]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream1_toPad[2]),
  .ToNextBSCell(bs_chain[12])
);

jtag_OutputCell BS_output_cell_data_output_stream13( 
  .FromCore(data_output_stream1_fromCore[3]),
  .FromPreviousBSCell(bs_chain[12]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream1_toPad[3]),
  .ToNextBSCell(bs_chain[13])
);

jtag_OutputCell BS_output_cell_data_output_stream14( 
  .FromCore(data_output_stream1_fromCore[4]),
  .FromPreviousBSCell(bs_chain[13]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream1_toPad[4]),
  .ToNextBSCell(bs_chain[14])
);

jtag_OutputCell BS_output_cell_data_output_stream15( 
  .FromCore(data_output_stream1_fromCore[5]),
  .FromPreviousBSCell(bs_chain[14]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream1_toPad[5]),
  .ToNextBSCell(bs_chain[15])
);

jtag_OutputCell BS_output_cell_data_output_stream16( 
  .FromCore(data_output_stream1_fromCore[6]),
  .FromPreviousBSCell(bs_chain[15]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream1_toPad[6]),
  .ToNextBSCell(bs_chain[16])
);

jtag_OutputCell BS_output_cell_data_output_stream17( 
  .FromCore(data_output_stream1_fromCore[7]),
  .FromPreviousBSCell(bs_chain[16]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream1_toPad[7]),
  .ToNextBSCell(bs_chain[17])
);

jtag_InputCell BS_input_cell_pedestals_in10_I ( 
  .InputPin(pedestals_in1_fromPad[0]),
  .FromPreviousBSCell(bs_chain[17]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[18]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in1_toCore[0])
);

jtag_InputCell BS_input_cell_pedestals_in11_I ( 
  .InputPin(pedestals_in1_fromPad[1]),
  .FromPreviousBSCell(bs_chain[18]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[19]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in1_toCore[1])
);








//Column Pair 2
jtag_OutputCell BS_output_cell_data_output_stream20( 
  .FromCore(data_output_stream2_fromCore[0]),
  .FromPreviousBSCell(bs_chain[19]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream2_toPad[0]),
  .ToNextBSCell(bs_chain[20])
);

jtag_OutputCell BS_output_cell_data_output_stream21( 
  .FromCore(data_output_stream2_fromCore[1]),
  .FromPreviousBSCell(bs_chain[20]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream2_toPad[1]),
  .ToNextBSCell(bs_chain[21])
);

jtag_OutputCell BS_output_cell_data_output_stream22( 
  .FromCore(data_output_stream2_fromCore[2]),
  .FromPreviousBSCell(bs_chain[21]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream2_toPad[2]),
  .ToNextBSCell(bs_chain[22])
);

jtag_OutputCell BS_output_cell_data_output_stream23( 
  .FromCore(data_output_stream2_fromCore[3]),
  .FromPreviousBSCell(bs_chain[22]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream2_toPad[3]),
  .ToNextBSCell(bs_chain[23])
);

jtag_OutputCell BS_output_cell_data_output_stream24( 
  .FromCore(data_output_stream2_fromCore[4]),
  .FromPreviousBSCell(bs_chain[23]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream2_toPad[4]),
  .ToNextBSCell(bs_chain[24])
);

jtag_OutputCell BS_output_cell_data_output_stream25( 
  .FromCore(data_output_stream2_fromCore[5]),
  .FromPreviousBSCell(bs_chain[24]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream2_toPad[5]),
  .ToNextBSCell(bs_chain[25])
);

jtag_OutputCell BS_output_cell_data_output_stream26( 
  .FromCore(data_output_stream2_fromCore[6]),
  .FromPreviousBSCell(bs_chain[25]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream2_toPad[6]),
  .ToNextBSCell(bs_chain[26])
);

jtag_OutputCell BS_output_cell_data_output_stream27( 
  .FromCore(data_output_stream2_fromCore[7]),
  .FromPreviousBSCell(bs_chain[26]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream2_toPad[7]),
  .ToNextBSCell(bs_chain[27])
);

jtag_InputCell BS_input_cell_pedestals_in20_I ( 
  .InputPin(pedestals_in2_fromPad[0]),
  .FromPreviousBSCell(bs_chain[27]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[28]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in2_toCore[0])
);

jtag_InputCell BS_input_cell_pedestals_in21_I ( 
  .InputPin(pedestals_in2_fromPad[1]),
  .FromPreviousBSCell(bs_chain[28]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[29]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in2_toCore[1])
);






//Column Pair 3
jtag_OutputCell BS_output_cell_data_output_stream30( 
  .FromCore(data_output_stream3_fromCore[0]),
  .FromPreviousBSCell(bs_chain[29]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream3_toPad[0]),
  .ToNextBSCell(bs_chain[30])
);

jtag_OutputCell BS_output_cell_data_output_stream31( 
  .FromCore(data_output_stream3_fromCore[1]),
  .FromPreviousBSCell(bs_chain[30]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream3_toPad[1]),
  .ToNextBSCell(bs_chain[31])
);

jtag_OutputCell BS_output_cell_data_output_stream32( 
  .FromCore(data_output_stream3_fromCore[2]),
  .FromPreviousBSCell(bs_chain[31]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream3_toPad[2]),
  .ToNextBSCell(bs_chain[32])
);

jtag_OutputCell BS_output_cell_data_output_stream33( 
  .FromCore(data_output_stream3_fromCore[3]),
  .FromPreviousBSCell(bs_chain[32]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream3_toPad[3]),
  .ToNextBSCell(bs_chain[33])
);

jtag_OutputCell BS_output_cell_data_output_stream34( 
  .FromCore(data_output_stream3_fromCore[4]),
  .FromPreviousBSCell(bs_chain[33]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream3_toPad[4]),
  .ToNextBSCell(bs_chain[34])
);

jtag_OutputCell BS_output_cell_data_output_stream35( 
  .FromCore(data_output_stream3_fromCore[5]),
  .FromPreviousBSCell(bs_chain[34]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream3_toPad[5]),
  .ToNextBSCell(bs_chain[35])
);

jtag_OutputCell BS_output_cell_data_output_stream36( 
  .FromCore(data_output_stream3_fromCore[6]),
  .FromPreviousBSCell(bs_chain[35]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream3_toPad[6]),
  .ToNextBSCell(bs_chain[36])
);

jtag_OutputCell BS_output_cell_data_output_stream37( 
  .FromCore(data_output_stream3_fromCore[7]),
  .FromPreviousBSCell(bs_chain[36]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream3_toPad[7]),
  .ToNextBSCell(bs_chain[37])
);

jtag_InputCell BS_input_cell_pedestals_in30_I ( 
  .InputPin(pedestals_in3_fromPad[0]),
  .FromPreviousBSCell(bs_chain[37]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[38]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in3_toCore[0])
);

jtag_InputCell BS_input_cell_pedestals_in31_I ( 
  .InputPin(pedestals_in3_fromPad[1]),
  .FromPreviousBSCell(bs_chain[38]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[39]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in3_toCore[1])
);



assign sync_reset_toCore = sync_reset_fromPad;
assign clk_toCore = clk_fromPad;


//Infrastructure signals
jtag_InputCell BS_input_cell_sync_reset_I ( 
  .InputPin(sync_reset_fromPad),
  .FromPreviousBSCell(bs_chain[39]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[40]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore()
  //.ToCore(sync_reset_toCore)
);

jtag_InputCell BS_input_cell_clk_I ( 
  .InputPin(clk_fromPad),
  .FromPreviousBSCell(bs_chain[40]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[41]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore()
  //.ToCore(clk_toCore)
);

jtag_OutputCell BS_output_cell_return_clk( 
  .FromCore(return_clk_fromCore),
  .FromPreviousBSCell(bs_chain[41]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(return_clk_toPad),
  .ToNextBSCell(bs_chain[42])
);

jtag_InputCell BS_input_cell_test_injection_en_I ( 
  .InputPin(test_injection_en_fromPad),
  .FromPreviousBSCell(bs_chain[42]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[43]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(test_injection_en_toCore)
);






//Column Pair 4
jtag_OutputCell BS_output_cell_data_output_stream40( 
  .FromCore(data_output_stream4_fromCore[0]),
  .FromPreviousBSCell(bs_chain[43]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream4_toPad[0]),
  .ToNextBSCell(bs_chain[44])
);

jtag_OutputCell BS_output_cell_data_output_stream41( 
  .FromCore(data_output_stream4_fromCore[1]),
  .FromPreviousBSCell(bs_chain[44]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream4_toPad[1]),
  .ToNextBSCell(bs_chain[45])
);

jtag_OutputCell BS_output_cell_data_output_stream42( 
  .FromCore(data_output_stream4_fromCore[2]),
  .FromPreviousBSCell(bs_chain[45]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream4_toPad[2]),
  .ToNextBSCell(bs_chain[46])
);

jtag_OutputCell BS_output_cell_data_output_stream43( 
  .FromCore(data_output_stream4_fromCore[3]),
  .FromPreviousBSCell(bs_chain[46]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream4_toPad[3]),
  .ToNextBSCell(bs_chain[47])
);

jtag_OutputCell BS_output_cell_data_output_stream44( 
  .FromCore(data_output_stream4_fromCore[4]),
  .FromPreviousBSCell(bs_chain[47]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream4_toPad[4]),
  .ToNextBSCell(bs_chain[48])
);

jtag_OutputCell BS_output_cell_data_output_stream45( 
  .FromCore(data_output_stream4_fromCore[5]),
  .FromPreviousBSCell(bs_chain[48]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream4_toPad[5]),
  .ToNextBSCell(bs_chain[49])
);

jtag_OutputCell BS_output_cell_data_output_stream46( 
  .FromCore(data_output_stream4_fromCore[6]),
  .FromPreviousBSCell(bs_chain[49]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream4_toPad[6]),
  .ToNextBSCell(bs_chain[50])
);

jtag_OutputCell BS_output_cell_data_output_stream47( 
  .FromCore(data_output_stream4_fromCore[7]),
  .FromPreviousBSCell(bs_chain[50]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream4_toPad[7]),
  .ToNextBSCell(bs_chain[51])
);

jtag_InputCell BS_input_cell_pedestals_in40_I ( 
  .InputPin(pedestals_in4_fromPad[0]),
  .FromPreviousBSCell(bs_chain[51]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[52]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in4_toCore[0])
);

jtag_InputCell BS_input_cell_pedestals_in41_I ( 
  .InputPin(pedestals_in4_fromPad[1]),
  .FromPreviousBSCell(bs_chain[52]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[53]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in4_toCore[1])
);






//Column Pair 5
jtag_OutputCell BS_output_cell_data_output_stream50( 
  .FromCore(data_output_stream5_fromCore[0]),
  .FromPreviousBSCell(bs_chain[53]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream5_toPad[0]),
  .ToNextBSCell(bs_chain[54])
);

jtag_OutputCell BS_output_cell_data_output_stream51( 
  .FromCore(data_output_stream5_fromCore[1]),
  .FromPreviousBSCell(bs_chain[54]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream5_toPad[1]),
  .ToNextBSCell(bs_chain[55])
);

jtag_OutputCell BS_output_cell_data_output_stream52( 
  .FromCore(data_output_stream5_fromCore[2]),
  .FromPreviousBSCell(bs_chain[55]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream5_toPad[2]),
  .ToNextBSCell(bs_chain[56])
);

jtag_OutputCell BS_output_cell_data_output_stream53( 
  .FromCore(data_output_stream5_fromCore[3]),
  .FromPreviousBSCell(bs_chain[56]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream5_toPad[3]),
  .ToNextBSCell(bs_chain[57])
);

jtag_OutputCell BS_output_cell_data_output_stream54( 
  .FromCore(data_output_stream5_fromCore[4]),
  .FromPreviousBSCell(bs_chain[57]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream5_toPad[4]),
  .ToNextBSCell(bs_chain[58])
);

jtag_OutputCell BS_output_cell_data_output_stream55( 
  .FromCore(data_output_stream5_fromCore[5]),
  .FromPreviousBSCell(bs_chain[58]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream5_toPad[5]),
  .ToNextBSCell(bs_chain[59])
);

jtag_OutputCell BS_output_cell_data_output_stream56( 
  .FromCore(data_output_stream5_fromCore[6]),
  .FromPreviousBSCell(bs_chain[59]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream5_toPad[6]),
  .ToNextBSCell(bs_chain[60])
);

jtag_OutputCell BS_output_cell_data_output_stream57( 
  .FromCore(data_output_stream5_fromCore[7]),
  .FromPreviousBSCell(bs_chain[60]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream5_toPad[7]),
  .ToNextBSCell(bs_chain[61])
);

jtag_InputCell BS_input_cell_pedestals_in50_I ( 
  .InputPin(pedestals_in5_fromPad[0]),
  .FromPreviousBSCell(bs_chain[61]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[62]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in5_toCore[0])
);

jtag_InputCell BS_input_cell_pedestals_in51_I ( 
  .InputPin(pedestals_in5_fromPad[1]),
  .FromPreviousBSCell(bs_chain[62]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[63]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in5_toCore[1])
);






//Column Pair 6
jtag_OutputCell BS_output_cell_data_output_stream60( 
  .FromCore(data_output_stream6_fromCore[0]),
  .FromPreviousBSCell(bs_chain[63]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream6_toPad[0]),
  .ToNextBSCell(bs_chain[64])
);

jtag_OutputCell BS_output_cell_data_output_stream61( 
  .FromCore(data_output_stream6_fromCore[1]),
  .FromPreviousBSCell(bs_chain[64]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream6_toPad[1]),
  .ToNextBSCell(bs_chain[65])
);

jtag_OutputCell BS_output_cell_data_output_stream62( 
  .FromCore(data_output_stream6_fromCore[2]),
  .FromPreviousBSCell(bs_chain[65]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream6_toPad[2]),
  .ToNextBSCell(bs_chain[66])
);

jtag_OutputCell BS_output_cell_data_output_stream63( 
  .FromCore(data_output_stream6_fromCore[3]),
  .FromPreviousBSCell(bs_chain[66]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream6_toPad[3]),
  .ToNextBSCell(bs_chain[67])
);

jtag_OutputCell BS_output_cell_data_output_stream64( 
  .FromCore(data_output_stream6_fromCore[4]),
  .FromPreviousBSCell(bs_chain[67]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream6_toPad[4]),
  .ToNextBSCell(bs_chain[68])
);

jtag_OutputCell BS_output_cell_data_output_stream65( 
  .FromCore(data_output_stream6_fromCore[5]),
  .FromPreviousBSCell(bs_chain[68]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream6_toPad[5]),
  .ToNextBSCell(bs_chain[69])
);

jtag_OutputCell BS_output_cell_data_output_stream66( 
  .FromCore(data_output_stream6_fromCore[6]),
  .FromPreviousBSCell(bs_chain[69]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream6_toPad[6]),
  .ToNextBSCell(bs_chain[70])
);

jtag_OutputCell BS_output_cell_data_output_stream67( 
  .FromCore(data_output_stream6_fromCore[7]),
  .FromPreviousBSCell(bs_chain[70]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream6_toPad[7]),
  .ToNextBSCell(bs_chain[71])
);

jtag_InputCell BS_input_cell_pedestals_in60_I ( 
  .InputPin(pedestals_in6_fromPad[0]),
  .FromPreviousBSCell(bs_chain[71]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[72]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in6_toCore[0])
);

jtag_InputCell BS_input_cell_pedestals_in61_I ( 
  .InputPin(pedestals_in6_fromPad[1]),
  .FromPreviousBSCell(bs_chain[72]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[73]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in6_toCore[1])
);







//Colmn Pair 7
jtag_OutputCell BS_output_cell_data_output_stream70( 
  .FromCore(data_output_stream7_fromCore[0]),
  .FromPreviousBSCell(bs_chain[73]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream7_toPad[0]),
  .ToNextBSCell(bs_chain[74])
);

jtag_OutputCell BS_output_cell_data_output_stream71( 
  .FromCore(data_output_stream7_fromCore[1]),
  .FromPreviousBSCell(bs_chain[74]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream7_toPad[1]),
  .ToNextBSCell(bs_chain[75])
);

jtag_OutputCell BS_output_cell_data_output_stream72( 
  .FromCore(data_output_stream7_fromCore[2]),
  .FromPreviousBSCell(bs_chain[75]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream7_toPad[2]),
  .ToNextBSCell(bs_chain[76])
);

jtag_OutputCell BS_output_cell_data_output_stream73( 
  .FromCore(data_output_stream7_fromCore[3]),
  .FromPreviousBSCell(bs_chain[76]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream7_toPad[3]),
  .ToNextBSCell(bs_chain[77])
);

jtag_OutputCell BS_output_cell_data_output_stream74( 
  .FromCore(data_output_stream7_fromCore[4]),
  .FromPreviousBSCell(bs_chain[77]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream7_toPad[4]),
  .ToNextBSCell(bs_chain[78])
);

jtag_OutputCell BS_output_cell_data_output_stream75( 
  .FromCore(data_output_stream7_fromCore[5]),
  .FromPreviousBSCell(bs_chain[78]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream7_toPad[5]),
  .ToNextBSCell(bs_chain[79])
);

jtag_OutputCell BS_output_cell_data_output_stream76( 
  .FromCore(data_output_stream7_fromCore[6]),
  .FromPreviousBSCell(bs_chain[79]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream7_toPad[6]),
  .ToNextBSCell(bs_chain[80])
);

jtag_OutputCell BS_output_cell_data_output_stream77( 
  .FromCore(data_output_stream7_fromCore[7]),
  .FromPreviousBSCell(bs_chain[80]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .UpdateDR(updateDR),
  .extest(extest_select),
  .TCK(tck),
  .Pin(data_output_stream7_toPad[7]),
  .ToNextBSCell(bs_chain[81])
);

jtag_InputCell BS_input_cell_pedestals_in70_I ( 
  .InputPin(pedestals_in7_fromPad[0]),
  .FromPreviousBSCell(bs_chain[81]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain[82]),
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in7_toCore[0])
);

jtag_InputCell BS_input_cell_pedestals_in71_I ( 
  .InputPin(pedestals_in7_fromPad[1]),
  .FromPreviousBSCell(bs_chain[82]),
  .CaptureDR(captureDR),
  .ShiftDR(shiftDR),
  .TCK(tck),
  .ToNextBSCell(bs_chain_tdo), //This ist the last chain in the scan chain
  .UpdateDR(updateDR),
  .sample_preload(sample_preload_select),
  .ToCore(pedestals_in7_toCore[1])
);




//JTAG TAP Control (FSM)
jtag_tap_ctrl tap_ctrl_I (
  .tms(tms),          // JTAG test mode select pad
  .tck(tck),          // JTAG test clock pad
  .trst(trst),        // JTAG test reset pad
  .capture_dr(captureDR), 
  .capture_ir(captureIR),
  .shift_dr(shiftDR),
  .shift_ir(shiftIR),
  .pause_dr(pauseDR),
  .pause_ir(), //unused?
  .update_dr(updateDR),
  .update_ir(updateIR),
  
  //unused outputs
  .test_logic_reset(),
  .run_test_idle(),
  .select_dr_scan(),
  .select_ir_scan(),
  .exit1_dr(),
  .exit1_ir(),
  .exit2_dr(),
  .exit2_ir()
);

//JTAG Instruction Register
jtag_ir ir_I (
  .tck(tck),                      // JTAG pads
  .trst(trst), 
  .tdi(tdi), 
  .state_shift_ir(shiftIR),              // TAP states
  .state_capture_ir(captureIR),
  .state_update_ir(updateIR),
  .serout(instruction_tdo),               // Instruction register
  .latched_jtag_ir(latched_jtag_ir)
);

//JTAG ID Code
jtag_id id_I(
  .tck(tck),                  // JTAG pads
  .tdi(tdi), 
  .trst(trst),
  .state_shift_dr(shiftDR),                // TAP states
  .idcode_select(idcode_select),              // Instruction register
  .serout(idcode_tdo)
);

//JTAG Output Multiplexer
jtag_output_mux output_mux_I(
  .tck(tck),          // JTAG pads 
  .trst(trst), 
  .tdi(tdi), 
  .state_shift_ir(shiftIR),      // TAP states
  .state_shift_dr(shiftDR),
  .state_pause_dr(pauseDR),
  .state_exit1_ir(1'b0), //unused??
  .latched_jtag_ir(latched_jtag_ir),
  .instruction_tdo(instruction_tdo),
  .idcode_tdo(idcode_tdo),
  .global_sr_tdo(data_from_gsr),
  .pixel_sr_tdo(data_from_psr),
  .bs_chain_tdi_i(bs_chain_tdo),
  .tdo_pad_o(tdo),          // JTAG test data output pad
  .tdo_padoe_o()       //unused! There is no output that needs to be enabled.
);  



//GENERAL INFORMATION:
// The JTAG Logic is by definition very slow - or at least it's not speed that counts - so large combinatorical logic
// clouds or fairly acceptable!

//Logic for decoding the instruction
always @ (latched_jtag_ir)
begin
  extest_select           = 1'b0;
  sample_preload_select   = 1'b0;
  idcode_select           = 1'b0;
  bypass_select           = 1'b0;
  global_sr_select        = 1'b0;
  pixel_sr_select         = 1'b0;

  case(latched_jtag_ir)    /* synthesis parallel_case */ 
    EXTEST:            extest_select           = 1'b1;    // External test
    SAMPLE_PRELOAD:    sample_preload_select   = 1'b1;    // Sample preload
    IDCODE:            idcode_select           = 1'b1;    // ID Code
    BYPASS:            bypass_select           = 1'b1;    // BYPASS
    SEL_GLOBAL_SR:     global_sr_select        = 1'b1;    // Global Shift Register
    SEL_PIXEL_SR:      pixel_sr_select         = 1'b1;    // Pixel Shift Register
    default:           bypass_select           = 1'b1;    // BYPASS
  endcase
end

  
assign  data_to_gsr     = tdi; //trivial - tdi is broadcast
assign  clk_gsr         = tck;
assign  load_gsr        = updateDR && global_sr_select;
assign  shift_gsr       = shiftDR && global_sr_select;
assign  read_back_gsr   = captureDR && global_sr_select;
assign  data_to_psr     = tdi; //trivial - tdi is broadcast
assign  clk_psr         = tck;
assign  load_psr        = updateDR && pixel_sr_select;
assign  shift_psr       = shiftDR && pixel_sr_select;
assign  read_back_psr   = captureDR && pixel_sr_select;


endmodule