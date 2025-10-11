// Example SystemVerilog module with AXI4 master interface
module axi_master_example #(
    parameter ADDR_WIDTH = 32,
    parameter DATA_WIDTH = 64
) (
    // Clock and Reset
    input  wire clk,
    input  wire rst_n,

    // AXI4 Master Interface
    output wire [ADDR_WIDTH-1:0]  M_AXI_AWADDR,
    output wire [7:0]              M_AXI_AWLEN,
    output wire [2:0]              M_AXI_AWSIZE,
    output wire [1:0]              M_AXI_AWBURST,
    output wire                    M_AXI_AWLOCK,
    output wire [3:0]              M_AXI_AWCACHE,
    output wire [2:0]              M_AXI_AWPROT,
    output wire [3:0]              M_AXI_AWQOS,
    output wire                    M_AXI_AWVALID,
    input  wire                    M_AXI_AWREADY,

    output wire [DATA_WIDTH-1:0]   M_AXI_WDATA,
    output wire [DATA_WIDTH/8-1:0] M_AXI_WSTRB,
    output wire                    M_AXI_WLAST,
    output wire                    M_AXI_WVALID,
    input  wire                    M_AXI_WREADY,

    input  wire [1:0]              M_AXI_BRESP,
    input  wire                    M_AXI_BVALID,
    output wire                    M_AXI_BREADY,

    output wire [ADDR_WIDTH-1:0]   M_AXI_ARADDR,
    output wire [7:0]              M_AXI_ARLEN,
    output wire [2:0]              M_AXI_ARSIZE,
    output wire [1:0]              M_AXI_ARBURST,
    output wire                    M_AXI_ARLOCK,
    output wire [3:0]              M_AXI_ARCACHE,
    output wire [2:0]              M_AXI_ARPROT,
    output wire [3:0]              M_AXI_ARQOS,
    output wire                    M_AXI_ARVALID,
    input  wire                    M_AXI_ARREADY,

    input  wire [DATA_WIDTH-1:0]   M_AXI_RDATA,
    input  wire [1:0]              M_AXI_RRESP,
    input  wire                    M_AXI_RLAST,
    input  wire                    M_AXI_RVALID,
    output wire                    M_AXI_RREADY,

    // Control signals
    input  wire                    start,
    output wire                    done
);

    // Implementation would go here
    assign done = 1'b0;

endmodule
