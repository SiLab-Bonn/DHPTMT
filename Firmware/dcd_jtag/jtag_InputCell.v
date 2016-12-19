/**********************************************************************************
*                                                                                 *
*	  Input Cell:                                                             *
*                                                                                 *
*	  InputPin: Value that comes from on-chip logic	and goes to pin           *
*	  FromPreviousBSCell: Value from previous boundary scan cell              *
*	  ToNextBSCell: Value for next boundary scan cell                         *
*	  CaptureDR, ShiftDR: TAP states                                          *
*	  TCK: Test Clock                                                         *
*                                                                                 *
**********************************************************************************/
// This is not a top module 
module jtag_InputCell( 
          input wire  InputPin,
		  input wire  FromPreviousBSCell,
		  input wire  CaptureDR,
		  input wire  ShiftDR,
          input wire  UpdateDR,
          input wire  sample_preload,
		  input wire  TCK,
          output wire ToCore,
		  output reg ToNextBSCell
);
          
reg ShiftedControl;    

wire SelectedInput = CaptureDR ? InputPin : FromPreviousBSCell;

assign ToCore = sample_preload ? ShiftedControl : InputPin;

always @ (posedge TCK)
begin
	if(CaptureDR | ShiftDR)
		ToNextBSCell<=SelectedInput;
end

always @ (negedge TCK)
begin
    if(UpdateDR)
        ShiftedControl<=ToNextBSCell;
end

endmodule	// InputCell