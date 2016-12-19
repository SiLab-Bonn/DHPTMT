/**********************************************************************************
*                                                                                 *
*	  Output Cell:                                                            *
*                                                                                 *
*	  FromCore: Value that comes from on-chip logic	and goes to pin           *
*	  FromPreviousBSCell: Value from previous boundary scan cell              *
*	  ToNextBSCell: Value for next boundary scan cell                         *
*	  CaptureDR, ShiftDR, UpdateDR: TAP states                                *
*	  extest: Instruction Register Command                                    *
*	  TCK: Test Clock                                                         *
*	  TristatedPin: Signal from core is connected to this output pin via BS   *
*	  FromOutputEnable: This pin comes from core or ControlCell               *
*                                                                                 *
*	  Signal that is connected to TristatedPin comes from core or BS chain.   *
*	  Tristate control is generated in core or BS chain (ControlCell).        *
*                                                                                 *
**********************************************************************************/
// This is not a top module 
module jtag_OutputCell( 
		  input  wire FromCore,
		  input  wire FromPreviousBSCell,
		  input  wire CaptureDR,
		  input  wire ShiftDR,
		  input  wire UpdateDR,
		  input  wire extest,
		  input  wire TCK,
		  //input  FromOutputEnable,
		  output wire Pin,
		  output reg ToNextBSCell
		  );
reg Latch;
reg ShiftedControl;

wire SelectedInput = CaptureDR? FromCore : FromPreviousBSCell;//FromPin : FromPreviousBSCell
wire MuxedSignal = extest? ShiftedControl : FromCore;
//assign TristatedPin = FromOutputEnable? MuxedSignal : 1'bz;
assign Pin = MuxedSignal;

always @ (posedge TCK)
begin
	if(CaptureDR | ShiftDR)
		/*Latch*/ToNextBSCell<=SelectedInput;
end

always @ (negedge TCK)
begin
	//ToNextBSCell<=Latch;
	if(UpdateDR)
		ShiftedControl<=ToNextBSCell;
end

endmodule	// OutputCell