interface my_bus_if;
    logic clk;
    logic [31:0] data;
endinterface

module interface_port_test (
    input wire clk,
    input wire rst_n,
    my_bus_if.master bus_m,
    my_bus_if.slave bus_s,
    simple_if simple_port
);
endmodule
