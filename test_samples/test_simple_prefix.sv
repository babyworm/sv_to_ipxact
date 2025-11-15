// Test file for IP-XACT conversion
// See test_samples/LICENSE.md for license information

module test_simple_prefix (
    input  wire        clk,
    input  wire        rst_n,

    // Standard: M_AXI_AWADDR
    output wire [31:0] M_AXI_AWADDR,
    output wire [7:0]  M_AXI_AWLEN,
    output wire [2:0]  M_AXI_AWSIZE,
    output wire [1:0]  M_AXI_AWBURST,
    output wire        M_AXI_AWVALID,
    input  wire        M_AXI_AWREADY,
    output wire [31:0] M_AXI_WDATA,
    output wire [3:0]  M_AXI_WSTRB,
    output wire        M_AXI_WLAST,
    output wire        M_AXI_WVALID,
    input  wire        M_AXI_WREADY,
    input  wire [1:0]  M_AXI_BRESP,
    input  wire        M_AXI_BVALID,
    output wire        M_AXI_BREADY,
    output wire [31:0] M_AXI_ARADDR,
    output wire [7:0]  M_AXI_ARLEN,
    output wire [2:0]  M_AXI_ARSIZE,
    output wire [1:0]  M_AXI_ARBURST,
    output wire        M_AXI_ARVALID,
    input  wire        M_AXI_ARREADY,
    input  wire [31:0] M_AXI_RDATA,
    input  wire [1:0]  M_AXI_RRESP,
    input  wire        M_AXI_RLAST,
    input  wire        M_AXI_RVALID,
    output wire        M_AXI_RREADY
);

endmodule
