// Example with multiple bus interfaces
module dual_interface (
    input wire clk,
    input wire rst_n,

    // AXI4-Lite Slave Interface
    input  wire [31:0]  S_AXI_AWADDR,
    input  wire [2:0]   S_AXI_AWPROT,
    input  wire         S_AXI_AWVALID,
    output wire         S_AXI_AWREADY,

    input  wire [31:0]  S_AXI_WDATA,
    input  wire [3:0]   S_AXI_WSTRB,
    input  wire         S_AXI_WVALID,
    output wire         S_AXI_WREADY,

    output wire [1:0]   S_AXI_BRESP,
    output wire         S_AXI_BVALID,
    input  wire         S_AXI_BREADY,

    input  wire [31:0]  S_AXI_ARADDR,
    input  wire [2:0]   S_AXI_ARPROT,
    input  wire         S_AXI_ARVALID,
    output wire         S_AXI_ARREADY,

    output wire [31:0]  S_AXI_RDATA,
    output wire [1:0]   S_AXI_RRESP,
    output wire         S_AXI_RVALID,
    input  wire         S_AXI_RREADY,

    // APB Master Interface
    output wire [31:0]  M_APB_PADDR,
    output wire         M_APB_PSEL,
    output wire         M_APB_PENABLE,
    output wire         M_APB_PWRITE,
    output wire [31:0]  M_APB_PWDATA,
    input  wire [31:0]  M_APB_PRDATA,
    input  wire         M_APB_PREADY,
    input  wire         M_APB_PSLVERR
);

    // Implementation would go here

endmodule
