// -------------------------------------------------------------
// 
// File Name: hdlsrc\sd_filter_tb\node_4.v
// Created: 2022-12-05 10:44:11
// 
// Generated by MATLAB 9.13 and HDL Coder 4.0
// 
// -------------------------------------------------------------


// -------------------------------------------------------------
// 
// Module: node_4
// Source Path: sd_filter_tb/SD 2nd Order Modulator/SD Filter/node_4
// Hierarchy Level: 2
// 
// -------------------------------------------------------------

`timescale 1 ns / 1 ns

module node_4
          (clk,
           reset,
           enb,
           input_rsvd,
           node_in,
           feedback,
           node_out);


  input   clk;
  input   reset;
  input   enb;
  input   input_rsvd;
  input   signed [24:0] node_in;  // sfix25
  input   feedback;
  output  signed [32:0] node_out;  // sfix33_En8


  wire signed [20:0] SD_Mux5_out1;  // sfix21_En8
  wire signed [49:0] Gain_out1;  // sfix50_En34
  wire signed [20:0] Sum1_stage2_add_cast;  // sfix21_En8
  wire signed [20:0] Sum1_stage2_add_temp;  // sfix21_En8
  wire signed [50:0] Sum1_op_stage1;  // sfix51_En34
  wire signed [32:0] Constant_out1;  // sfix33_En8
  wire signed [20:0] SD_Mux1_out1;  // sfix21_En8
  wire signed [20:0] Sum1_stage3_sub_cast;  // sfix21_En8
  wire signed [20:0] Sum1_out1;  // sfix21_En8
  wire signed [32:0] Sum2_stage2_add_cast;  // sfix33_En8
  wire signed [32:0] Sum2_stage2_add_temp;  // sfix33_En8
  wire signed [33:0] Sum2_op_stage1;  // sfix34_En8
  reg signed [32:0] Unit_Delay1_out1;  // sfix33_En8
  wire signed [32:0] Sum2_stage3_add_cast;  // sfix33_En8
  wire signed [32:0] Sum2_out1;  // sfix33_En8


  SD_Mux5_block1 u_SD_Mux5 (.in1(input_rsvd),
                            .out1(SD_Mux5_out1)  // sfix21_En8
                            );

  assign Gain_out1 = {{2{node_in[24]}}, {node_in, 23'b00000000000000000000000}};



  assign Sum1_stage2_add_cast = Gain_out1[46:26];
  assign Sum1_stage2_add_temp = SD_Mux5_out1 + Sum1_stage2_add_cast;
  assign Sum1_op_stage1 = {{4{Sum1_stage2_add_temp[20]}}, {Sum1_stage2_add_temp, 26'b00000000000000000000000000}};



  assign Constant_out1 = 33'sh000000000;



  SD_Mux1_block1 u_SD_Mux1 (.in1(feedback),
                            .out1(SD_Mux1_out1)  // sfix21_En8
                            );

  assign Sum1_stage3_sub_cast = Sum1_op_stage1[46:26];
  assign Sum1_out1 = Sum1_stage3_sub_cast - SD_Mux1_out1;



  assign Sum2_stage2_add_cast = {{12{Sum1_out1[20]}}, Sum1_out1};
  assign Sum2_stage2_add_temp = Constant_out1 + Sum2_stage2_add_cast;
  assign Sum2_op_stage1 = {Sum2_stage2_add_temp[32], Sum2_stage2_add_temp};



  assign Sum2_stage3_add_cast = Sum2_op_stage1[32:0];
  assign Sum2_out1 = Sum2_stage3_add_cast + Unit_Delay1_out1;



  always @(posedge clk or posedge reset)
    begin : Unit_Delay1_process
      if (reset == 1'b1) begin
        Unit_Delay1_out1 <= 33'sh000000000;
      end
      else begin
        if (enb) begin
          Unit_Delay1_out1 <= Sum2_out1;
        end
      end
    end



  assign node_out = Unit_Delay1_out1;

endmodule  // node_4

