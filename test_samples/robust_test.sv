`define DATA_WIDTH 32
`define ADDR_WIDTH 32

module robust_test #(
    parameter WIDTH = `DATA_WIDTH,
    parameter AW = `ADDR_WIDTH
) (
    input wire clk, // Clock signal
    input wire rst_n, /* Active low reset */

    /*
       Multi-line comment
       describing the interface
    */
    input wire [WIDTH-1:0] data_in,

    `ifdef USE_OUTPUT
    output wire [WIDTH-1:0] data_out,
    `endif

    // Comment with "input wire" inside
    output wire valid // Valid signal
);
endmodule
