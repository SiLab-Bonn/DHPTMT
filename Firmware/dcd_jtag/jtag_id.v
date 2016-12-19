/**********************************************************************************
*                                                                                 *
*  JTAG ID Register                                                               *
*                                                                                 *
**********************************************************************************/


module jtag_id (  
  input 	wire tck,  			// JTAG pads
  input 	wire tdi,
  input 	wire trst,
  input 	wire state_shift_dr,		// TAP states
  input 	wire idcode_select,		// instruction register code
  output reg 	serout			// serial output
);

localparam  IDCODE_VALUE    = 32'h12345678;

reg [31:0] idcode_reg;			// store and shift ID in this register

always @ (posedge tck/* or posedge trst*/)			// this has no reset. Why? TODO		No cons --So it has now a reset state	
begin
 /* if (trst) 
  begin
    serout <= 1'b0;
    idcode_reg <= {31{1'b0}};
  end
  else*/ if (idcode_select && state_shift_dr)
    idcode_reg <= {tdi, idcode_reg[31:1]};	// shift ID register
  else
    idcode_reg <= IDCODE_VALUE;		// load with constant value
end

always @ (negedge tck)
begin
    serout <= idcode_reg[0];
end

endmodule