module ibex_soc_tb #(
    parameter RAM_FPATH = "",
    parameter bit FAULT = 1'b1, 
    parameter bit FAULT_REPEAT = 1'b0, 
    parameter byte FAULT_PC_COUNT = 8'd8, 
    parameter int unsigned FAULT_INSTRUCTION = 32'hfe0407a3,
    parameter int unsigned FAULT_PC = 32'h000027dc
  ); 
   
  logic clk, rst;
  logic rx, tx;

  ibex_soc #(
    .RAM_FPATH  ( RAM_FPATH ),
    .FAULT(FAULT),
    .FAULT_REPEAT ( FAULT_REPEAT ),
    .FAULT_PC_COUNT(FAULT_PC_COUNT),
    .FAULT_INSTRUCTION (FAULT_INSTRUCTION),
    .FAULT_PC (FAULT_PC)
    )i_ibex_soc (
     .sys_clk_i  ( clk       ),
     .sys_rst_ni ( ~rst      ),
     .uart_rx_i  ( rx        ),
     .uart_tx_o  ( tx        )
    );

  initial
  begin
    rst = 1'b1;
    #20
     rst = 1'b0;
  end

  always
  begin
    clk = 1'b0;
    #5;
    clk = 1'b1;
    #5;
  end

  // Backup timeout for safety
  initial
  begin
    #500000000;  // Longer timeout for AES computation
    $display("Simulation timeout reached - AES is probably done!");
    $finish;
  end

endmodule
