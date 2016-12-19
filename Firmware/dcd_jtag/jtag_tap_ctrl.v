module jtag_tap_ctrl (
		input wire tms,      	// JTAG test mode select pad
		input wire tck,      	// JTAG test clock pad
		input wire trst,     	// JTAG test reset pad
		//input tdi,      	// JTAG test data input pad
		output wire test_logic_reset,// TAP STATES
		output wire run_test_idle,
		output wire select_dr_scan,
		output wire select_ir_scan,
		output wire capture_dr, 
		output wire capture_ir,
		output wire shift_dr,
		output wire shift_ir,
		output wire exit1_dr,
		output wire exit1_ir,
		output wire pause_dr,
		output wire pause_ir,
		output wire exit2_dr,
		output wire exit2_ir,
		output wire update_dr,
		output wire update_ir//,
		//output tdo_o			// TDO signal that is connected to TDI of sub-modules.
		);

parameter TEST_LOGIC_RESET_P 	= 16'b1000000000000000;
parameter RUN_TEST_IDLE_P 	= 16'b0100000000000000;
parameter SELECT_DR_SCAN_P 	= 16'b0010000000000000;
parameter SELECT_IR_SCAN_P 	= 16'b0001000000000000;
parameter CAPTURE_DR_P 		= 16'b0000100000000000;
parameter CAPTURE_IR_P 		= 16'b0000010000000000;
parameter SHIFT_DR_P 		= 16'b0000001000000000;
parameter SHIFT_IR_P 		= 16'b0000000100000000;
parameter EXIT1_DR_P 		= 16'b0000000010000000;
parameter EXIT1_IR_P 		= 16'b0000000001000000;
parameter PAUSE_DR_P 		= 16'b0000000000100000;
parameter PAUSE_IR_P 		= 16'b0000000000010000;
parameter EXIT2_DR_P 		= 16'b0000000000001000;
parameter EXIT2_IR_P 		= 16'b0000000000000100;
parameter UPDATE_DR_P 		= 16'b0000000000000010;
parameter UPDATE_IR_P 		= 16'b0000000000000001;

reg [15:0] current_state, next_state;

//assign tdo_o = tdi;
assign {test_logic_reset, run_test_idle, select_dr_scan, select_ir_scan, capture_dr, capture_ir, shift_dr, shift_ir, exit1_dr, exit1_ir, pause_dr, pause_ir, exit2_dr, exit2_ir, update_dr, update_ir} = current_state;

always @(*) begin
  casex({tms, current_state})
    {1'b0, TEST_LOGIC_RESET_P}:   	next_state = RUN_TEST_IDLE_P;
    {1'b1, TEST_LOGIC_RESET_P}:   	next_state = TEST_LOGIC_RESET_P;
    {1'b0, RUN_TEST_IDLE_P}:   	  	next_state = RUN_TEST_IDLE_P;
    {1'b1, RUN_TEST_IDLE_P}:   	  	next_state = SELECT_DR_SCAN_P;
    {1'b1, SELECT_DR_SCAN_P}:   	next_state = SELECT_IR_SCAN_P;
    {1'b0, SELECT_DR_SCAN_P}:   	next_state = CAPTURE_DR_P;
    {1'b0, SELECT_IR_SCAN_P}:   	next_state = CAPTURE_IR_P;
    {1'b1, SELECT_IR_SCAN_P}:   	next_state = TEST_LOGIC_RESET_P;
    {1'b0, CAPTURE_DR_P}:   		next_state = SHIFT_DR_P;
    {1'b1, CAPTURE_DR_P}:   		next_state = EXIT1_DR_P;
    {1'b0, CAPTURE_IR_P}:   		next_state = SHIFT_IR_P;
    {1'b1, CAPTURE_IR_P}:   		next_state = EXIT1_IR_P;
    {1'b1, SHIFT_DR_P}:   		next_state = EXIT1_DR_P;
    {1'b0, SHIFT_DR_P}:   		next_state = SHIFT_DR_P;
    {1'b1, SHIFT_IR_P}:   		next_state = EXIT1_IR_P;
    {1'b0, SHIFT_IR_P}:   		next_state = SHIFT_IR_P;
    {1'b0, EXIT1_DR_P}:   		next_state = PAUSE_DR_P;
    {1'b1, EXIT1_DR_P}:   		next_state = UPDATE_DR_P;
    {1'b0, EXIT1_IR_P}:   		next_state = PAUSE_IR_P;
    {1'b1, EXIT1_IR_P}:   		next_state = UPDATE_IR_P;
    {1'b1, PAUSE_DR_P}:   		next_state = EXIT2_DR_P;
    {1'b0, PAUSE_DR_P}:   		next_state = PAUSE_DR_P;
    {1'b1, PAUSE_IR_P}:   		next_state = EXIT2_IR_P;
    {1'b0, PAUSE_IR_P}:   		next_state = PAUSE_IR_P;
    {1'b1, EXIT2_DR_P}:   		next_state = UPDATE_DR_P;
    {1'b0, EXIT2_DR_P}:   		next_state = SHIFT_DR_P;
    {1'b1, EXIT2_IR_P}:   		next_state = UPDATE_IR_P;
    {1'b0, EXIT2_IR_P}:   		next_state = SHIFT_IR_P;
    {1'b1, UPDATE_DR_P}:  		next_state = SELECT_DR_SCAN_P;
    {1'b0, UPDATE_DR_P}:   		next_state = RUN_TEST_IDLE_P;
    {1'b1, UPDATE_IR_P}:   		next_state = SELECT_DR_SCAN_P;
    {1'b0, UPDATE_IR_P}:   		next_state = RUN_TEST_IDLE_P;
    default:  				next_state = TEST_LOGIC_RESET_P;
  endcase
end

always @(posedge tck or posedge trst ) begin
  if (trst  == 1'b1)
    current_state <= TEST_LOGIC_RESET_P;
  else 
    current_state <= next_state;
end

endmodule
