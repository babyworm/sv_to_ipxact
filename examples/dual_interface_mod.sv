// Example with multiple bus interfaces
module dual_interface_mod (
    input wire clk,
    input wire rst_n,

    input  wire [31:0]  si0_awaddr,
    input  wire [2:0]   si0_awprot,
    input  wire [3:0]   si0_awlen,
    input  wire [1:0]   si0_awburst,
    input  wire         si0_awvalid,
    output wire         si0_awready,

    input  wire [127:0] si0_wdata,
    input  wire [15:0]  si0_wstrb,
    input  wire         si0_wvalid,
    output wire         si0_wready,

    output wire [1:0]   si0_bresp,
    output wire         si0_bvalid,
    input  wire         si0_bready,

    input  wire [31:0]  si0_araddr,
    input  wire [2:0]   si0_arprot,
    input  wire [3:0]   si0_arlen,
    input  wire [1:0]   si0_arburst,
    input  wire         si0_arvalid,
    output wire         si0_arready,

    output wire [127:0] si0_rdata,
    output wire [1:0]   si0_rresp,
    output wire         si0_rvalid,
    input  wire         si0_rready,

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
