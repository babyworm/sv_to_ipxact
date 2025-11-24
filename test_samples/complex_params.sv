module complex_params #(
    parameter type T = int,
    parameter int unsigned COUNT = 10,
    parameter logic [31:0] VAL = 32'hFFFF_FFFF,
    parameter real P = 3.14,
    parameter string S = "hello"
) (
    input wire clk,
    input wire rst_n
);
    // Localparams should be ignored by IP-XACT usually, or mapped to internal parameters
    localparam int INTERNAL = 0;
endmodule
