/**********************************************************************************
*                                                                                 *
*  JTAG Instruction Register                                                      *
*                                                                                 *
**********************************************************************************/


module  jtag_ir #(parameter IR_LENGTH = 4) (
  input wire tck, 					// JTAG pads
  input wire trst, 
  input wire tdi,
  input wire state_shift_ir,				// TAP states
  input wire state_capture_ir,
  input wire state_update_ir,
  output reg serout,				// Select signals for boundary scan or mbist
  output reg [IR_LENGTH-1:0]  latched_jtag_ir
); 

localparam  IDCODE          = 4'b0010;
localparam  INIT_IR_VALUE   = 4'b0101;

  
reg [IR_LENGTH-1:0]  jtag_ir;			// Instruction register.

always @ (posedge tck or posedge trst)
begin
  if (trst) begin
    jtag_ir[IR_LENGTH-1:0] 	<= {IR_LENGTH{1'b0}}; // Why not set to IDCODE ??? TODO
    latched_jtag_ir 		<= IDCODE;   // IDCODE selected after reset
  end else if (state_capture_ir)
    jtag_ir <= INIT_IR_VALUE;			// This value is fixed for easier fault detection ??? TODO Move to defines!!!		--Already moved   
  else if (state_shift_ir)
    jtag_ir[IR_LENGTH-1:0] <= {tdi, jtag_ir[IR_LENGTH-1:1]};
  else if (state_update_ir)
    latched_jtag_ir <= jtag_ir;
end

always @ (negedge tck)
begin
  serout <= jtag_ir[0];
end

endmodule