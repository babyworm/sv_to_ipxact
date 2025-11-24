module ambiguity_test (
    input wire clk,
    input wire rst_n,

    // This interface matches both Dummy and Ambiguous protocols
    output wire [31:0] amb_data,
    output wire amb_valid,
    input wire amb_ready
);
endmodule
