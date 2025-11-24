module param_test #(
    parameter WIDTH = 32
) (
    input wire [WIDTH-1:0] data_in,
    output wire [0:WIDTH-1] data_out_ascending
);
endmodule
