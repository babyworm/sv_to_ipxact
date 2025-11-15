// Test file for IP-XACT conversion
// See test_samples/LICENSE.md for license information

module test_postfix_only (
    input  wire        clk,
    input  wire        rst_n,

    // Full AXI4 signals with postfix _o and _i
    output wire [31:0] M_AXI_AWADDR_o,
    output wire [7:0]  M_AXI_AWLEN_o,
    output wire [2:0]  M_AXI_AWSIZE_o,
    output wire [1:0]  M_AXI_AWBURST_o,
    output wire        M_AXI_AWVALID_o,
    input  wire        M_AXI_AWREADY_i,
    output wire [31:0] M_AXI_WDATA_o,
    output wire [3:0]  M_AXI_WSTRB_o,
    output wire        M_AXI_WLAST_o,
    output wire        M_AXI_WVALID_o,
    input  wire        M_AXI_WREADY_i,
    input  wire [1:0]  M_AXI_BRESP_i,
    input  wire        M_AXI_BVALID_i,
    output wire        M_AXI_BREADY_o,
    output wire [31:0] M_AXI_ARADDR_o,
    output wire [7:0]  M_AXI_ARLEN_o,
    output wire [2:0]  M_AXI_ARSIZE_o,
    output wire [1:0]  M_AXI_ARBURST_o,
    output wire        M_AXI_ARVALID_o,
    input  wire        M_AXI_ARREADY_i,
    input  wire [31:0] M_AXI_RDATA_i,
    input  wire [1:0]  M_AXI_RRESP_i,
    input  wire        M_AXI_RLAST_i,
    input  wire        M_AXI_RVALID_i,
    output wire        M_AXI_RREADY_o
);

endmodule
