// Test file for IP-XACT conversion
// See test_samples/LICENSE.md for license information


module test_prefix_postfix (
    input  wire        clk,
    input  wire        rst_n,

    // Standard pattern: M_AXI_AWADDR
    output wire [31:0] M_AXI_AWADDR,
    output wire        M_AXI_AWVALID,
    input  wire        M_AXI_AWREADY,

    // Lowercase prefix: m_axi_awaddr
    output wire [31:0] m_axi_araddr,
    output wire        m_axi_arvalid,
    input  wire        m_axi_arready,

    // With instance number: M_AXI0_AWADDR
    output wire [31:0] M_AXI0_AWADDR,
    output wire        M_AXI0_AWVALID,
    input  wire        M_AXI0_AWREADY,

    // With instance number lowercase: m_axi1_awaddr
    output wire [31:0] m_axi1_araddr,
    output wire        m_axi1_arvalid,
    input  wire        m_axi1_arready,

    // With postfix: M_AXI_AWADDR_i, M_AXI_AWADDR_o
    output wire [31:0] M_AXI_AWADDR_o,
    output wire        M_AXI_AWVALID_o,
    input  wire        M_AXI_AWREADY_i,

    // With postfix lowercase: m_axi_awaddr_i
    output wire [31:0] m_axi_awaddr_o,
    output wire        m_axi_awvalid_o,
    input  wire        m_axi_awready_i,

    // With both prefix and postfix: M_AXI_AWADDR_0
    output wire [31:0] M_AXI_AWADDR_0,
    output wire        M_AXI_AWVALID_0,
    input  wire        M_AXI_AWREADY_0,

    // Different prefix style: AXI_M_AWADDR
    output wire [31:0] AXI_M_AWADDR,
    output wire        AXI_M_AWVALID,
    input  wire        AXI_M_AWREADY,

    // CamelCase: M_AxiAwAddr
    output wire [31:0] M_AxiAwAddr,
    output wire        M_AxiAwValid,
    input  wire        M_AxiAwReady,

    // Mixed case: M_AXI_awaddr
    output wire [31:0] M_AXI_awaddr,
    output wire        M_AXI_awvalid,
    input  wire        M_AXI_awready,

    // Long prefix: MASTER_AXI4_AWADDR
    output wire [31:0] MASTER_AXI4_AWADDR,
    output wire        MASTER_AXI4_AWVALID,
    input  wire        MASTER_AXI4_AWREADY,

    // With suffix number: M_AXI_AWADDR0
    output wire [31:0] M_AXI_AWADDR0,
    output wire        M_AXI_AWVALID0,
    input  wire        M_AXI_AWREADY0
);

endmodule
