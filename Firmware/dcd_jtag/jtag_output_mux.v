/**********************************************************************************
*                                                                                 *
*   JTAg Output Multiplexer                                                       *
*                                                                                 *
**********************************************************************************/


module jtag_output_mux #(parameter IR_LENGTH = 4) (	  
  input wire tck,			// JTAG pads
  input wire trst,  
  input wire tdi,  	    
  input wire state_shift_ir,		// TAP states, reuqired for tristate enable 
  input wire state_shift_dr,
  input wire state_pause_dr,
  input wire state_exit1_ir,
  input wire instruction_tdo,
  input wire idcode_tdo,
  input wire global_sr_tdo,
  input wire pixel_sr_tdo,
  input wire bs_chain_tdi_i,
  input wire [IR_LENGTH-1:0] latched_jtag_ir,
  output reg tdo_pad_o,     
  output reg tdo_padoe_o
);

localparam  EXTEST          = 4'b0000;
localparam  SAMPLE_PRELOAD  = 4'b0001;
localparam  IDCODE          = 4'b0010;
localparam  BYPASS          = 4'b1111;
localparam  SEL_GLOBAL_SR   = 4'b0100;
localparam  SEL_PIXEL_SR    = 4'b1000;

reg shift_ir_neg;			// Delay registers (Latches) ??? TODO
reg [IR_LENGTH-1:0] latched_jtag_ir_neg;
reg bypass_reg; 			// Bypass registers
reg bypassed_tdo;

always @ (posedge tck or posedge trst) // Bypass
begin
  if (trst)
    bypass_reg<= 1'b0;
  else if(state_shift_dr)
    bypass_reg<= tdi;
end

always @ (negedge tck)
begin
  bypassed_tdo <= bypass_reg;
end

//always @ (shift_ir_neg or state_exit1_ir or instruction_tdo or latched_jtag_ir_neg or idcode_tdo or bs_chain_tdi_i or bypassed_tdo)
always @(*)
begin
  if(shift_ir_neg)
    tdo_pad_o = instruction_tdo;
  else
    begin
      case(latched_jtag_ir_neg)    // synthesis parallel_case
        IDCODE:            tdo_pad_o = idcode_tdo;       // Reading ID code
        SAMPLE_PRELOAD:    tdo_pad_o = bs_chain_tdi_i;   // Sampling/Preloading
        EXTEST:            tdo_pad_o = bs_chain_tdi_i;   // External test
        SEL_GLOBAL_SR:     tdo_pad_o = global_sr_tdo;
        SEL_PIXEL_SR:      tdo_pad_o = pixel_sr_tdo;
        default:            tdo_pad_o = bypassed_tdo;     // BYPASS instruction
      endcase
    end
end

always @ (negedge tck) // Tristate control for tdo_pad_o pin
begin
  tdo_padoe_o <= state_shift_ir | state_shift_dr | (state_pause_dr/* & debug_select*/);
  shift_ir_neg <= state_shift_ir; // delay registers (Latches) ??? TODO
  latched_jtag_ir_neg <= latched_jtag_ir;
end

endmodule
