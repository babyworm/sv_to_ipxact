package my_pkg;
    typedef logic [15:0] my_type_t;
endpackage

module package_import_test
    import my_pkg::*;
(
    input wire clk,
    input my_type_t data_in,
    output my_pkg::my_type_t data_out
);
endmodule
