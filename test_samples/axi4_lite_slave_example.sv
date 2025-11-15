// Example AXI4-Lite Slave Interface Module
// Created for testing IP-XACT conversion
// See test_samples/LICENSE.md for license information

module axi4_lite_slave_example (
    input  wire        aclk,
    input  wire        aresetn,

    // AXI4-Lite Slave Write Address Channel
    input  wire [31:0] S_AXI_AWADDR,
    input  wire [2:0]  S_AXI_AWPROT,
    input  wire        S_AXI_AWVALID,
    output wire        S_AXI_AWREADY,

    // AXI4-Lite Slave Write Data Channel
    input  wire [31:0] S_AXI_WDATA,
    input  wire [3:0]  S_AXI_WSTRB,
    input  wire        S_AXI_WVALID,
    output wire        S_AXI_WREADY,

    // AXI4-Lite Slave Write Response Channel
    output wire [1:0]  S_AXI_BRESP,
    output wire        S_AXI_BVALID,
    input  wire        S_AXI_BREADY,

    // AXI4-Lite Slave Read Address Channel
    input  wire [31:0] S_AXI_ARADDR,
    input  wire [2:0]  S_AXI_ARPROT,
    input  wire        S_AXI_ARVALID,
    output wire        S_AXI_ARREADY,

    // AXI4-Lite Slave Read Data Channel
    output wire [31:0] S_AXI_RDATA,
    output wire [1:0]  S_AXI_RRESP,
    output wire        S_AXI_RVALID,
    input  wire        S_AXI_RREADY
);

    // Simple AXI4-Lite slave implementation
    // This is just a placeholder for testing

endmodule
