// Example module with multiple AXI interfaces
// Created for testing IP-XACT conversion
// See test_samples/LICENSE.md for license information

module dual_axi_interfaces (
    input  wire        clk,
    input  wire        rst_n,

    // AXI4 Master Interface
    output wire [31:0] M_AXI_AWADDR,
    output wire        M_AXI_AWVALID,
    input  wire        M_AXI_AWREADY,
    output wire [31:0] M_AXI_WDATA,
    output wire        M_AXI_WVALID,
    input  wire        M_AXI_WREADY,
    input  wire [1:0]  M_AXI_BRESP,
    input  wire        M_AXI_BVALID,
    output wire        M_AXI_BREADY,
    output wire [31:0] M_AXI_ARADDR,
    output wire        M_AXI_ARVALID,
    input  wire        M_AXI_ARREADY,
    input  wire [31:0] M_AXI_RDATA,
    input  wire [1:0]  M_AXI_RRESP,
    input  wire        M_AXI_RVALID,
    output wire        M_AXI_RREADY,

    // AXI4-Lite Slave Interface
    input  wire [31:0] S_AXI_LITE_AWADDR,
    input  wire        S_AXI_LITE_AWVALID,
    output wire        S_AXI_LITE_AWREADY,
    input  wire [31:0] S_AXI_LITE_WDATA,
    input  wire        S_AXI_LITE_WVALID,
    output wire        S_AXI_LITE_WREADY,
    output wire [1:0]  S_AXI_LITE_BRESP,
    output wire        S_AXI_LITE_BVALID,
    input  wire        S_AXI_LITE_BREADY,
    input  wire [31:0] S_AXI_LITE_ARADDR,
    input  wire        S_AXI_LITE_ARVALID,
    output wire        S_AXI_LITE_ARREADY,
    output wire [31:0] S_AXI_LITE_RDATA,
    output wire [1:0]  S_AXI_LITE_RRESP,
    output wire        S_AXI_LITE_RVALID,
    input  wire        S_AXI_LITE_RREADY
);

    // Module with both master and slave AXI interfaces
    // This is just a placeholder for testing

endmodule
