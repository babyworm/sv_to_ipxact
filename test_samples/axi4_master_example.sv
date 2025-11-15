// Example AXI4 Master Interface Module
// Created for testing IP-XACT conversion
// See test_samples/LICENSE.md for license information

module axi4_master_example (
    input  wire        clk,
    input  wire        rst_n,

    // AXI4 Master Write Address Channel
    output wire [31:0] M_AXI_AWADDR,
    output wire [7:0]  M_AXI_AWLEN,
    output wire [2:0]  M_AXI_AWSIZE,
    output wire [1:0]  M_AXI_AWBURST,
    output wire        M_AXI_AWLOCK,
    output wire [3:0]  M_AXI_AWCACHE,
    output wire [2:0]  M_AXI_AWPROT,
    output wire [3:0]  M_AXI_AWQOS,
    output wire        M_AXI_AWVALID,
    input  wire        M_AXI_AWREADY,
    output wire [3:0]  M_AXI_AWID,
    output wire [3:0]  M_AXI_AWREGION,

    // AXI4 Master Write Data Channel
    output wire [31:0] M_AXI_WDATA,
    output wire [3:0]  M_AXI_WSTRB,
    output wire        M_AXI_WLAST,
    output wire        M_AXI_WVALID,
    input  wire        M_AXI_WREADY,
    output wire [3:0]  M_AXI_WID,

    // AXI4 Master Write Response Channel
    input  wire [1:0]  M_AXI_BRESP,
    input  wire        M_AXI_BVALID,
    output wire        M_AXI_BREADY,
    input  wire [3:0]  M_AXI_BID,

    // AXI4 Master Read Address Channel
    output wire [31:0] M_AXI_ARADDR,
    output wire [7:0]  M_AXI_ARLEN,
    output wire [2:0]  M_AXI_ARSIZE,
    output wire [1:0]  M_AXI_ARBURST,
    output wire        M_AXI_ARLOCK,
    output wire [3:0]  M_AXI_ARCACHE,
    output wire [2:0]  M_AXI_ARPROT,
    output wire [3:0]  M_AXI_ARQOS,
    output wire        M_AXI_ARVALID,
    input  wire        M_AXI_ARREADY,
    output wire [3:0]  M_AXI_ARID,
    output wire [3:0]  M_AXI_ARREGION,

    // AXI4 Master Read Data Channel
    input  wire [31:0] M_AXI_RDATA,
    input  wire [1:0]  M_AXI_RRESP,
    input  wire        M_AXI_RLAST,
    input  wire        M_AXI_RVALID,
    output wire        M_AXI_RREADY,
    input  wire [3:0]  M_AXI_RID
);

    // Simple AXI4 master implementation
    // This is just a placeholder for testing

endmodule
