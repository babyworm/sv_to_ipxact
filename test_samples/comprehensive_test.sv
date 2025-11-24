module comprehensive_test #(
    parameter ADDR_WIDTH = 32,
    parameter DATA_WIDTH = 32,
    parameter C_M_AXI_DATA_WIDTH = 64,
    parameter S_AXI_ID_WIDTH = 4
) (
    // Clock and Reset
    input wire clk,
    input wire rst_n,

    // Dummy Master (should match Dummy protocol)
    output wire [31:0] dummy_m_data,
    output wire dummy_m_valid,
    input wire dummy_m_ready,

    // Dummy Slave (should match Dummy protocol and mirror signals)
    // Master defines DATA as OUT, so Slave should have DATA as IN.
    input wire [31:0] dummy_s_data,
    input wire dummy_s_valid,
    output wire dummy_s_ready,

    // AXI4-Lite Master (Address Space test)
    output wire [ADDR_WIDTH-1:0] m_axi_awaddr,
    output wire m_axi_awvalid,
    input wire m_axi_awready,
    output wire [DATA_WIDTH-1:0] m_axi_wdata,
    output wire m_axi_wvalid,
    input wire m_axi_wready,
    input wire [1:0] m_axi_bresp,
    input wire m_axi_bvalid,
    output wire m_axi_bready,
    output wire [ADDR_WIDTH-1:0] m_axi_araddr,
    output wire m_axi_arvalid,
    input wire m_axi_arready,
    input wire [DATA_WIDTH-1:0] m_axi_rdata,
    input wire [1:0] m_axi_rresp,
    input wire m_axi_rvalid,
    output wire m_axi_rready,

    // AXI4-Lite Slave (Memory Map test)
    input wire [ADDR_WIDTH-1:0] s_axi_awaddr,
    input wire s_axi_awvalid,
    output wire s_axi_awready,
    input wire [DATA_WIDTH-1:0] s_axi_wdata,
    input wire s_axi_wvalid,
    output wire s_axi_wready,
    output wire [1:0] s_axi_bresp,
    output wire s_axi_bvalid,
    input wire s_axi_bready,
    input wire [ADDR_WIDTH-1:0] s_axi_araddr,
    input wire s_axi_arvalid,
    output wire s_axi_arready,
    output wire [DATA_WIDTH-1:0] s_axi_rdata,
    output wire [1:0] s_axi_rresp,
    output wire s_axi_rvalid,
    input wire s_axi_rready
);
endmodule
