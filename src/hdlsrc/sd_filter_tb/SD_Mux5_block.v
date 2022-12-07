// -------------------------------------------------------------
// 
// File Name: hdlsrc\sd_filter_tb\SD_Mux5_block.v
// Created: 2022-12-05 10:44:11
// 
// Generated by MATLAB 9.13 and HDL Coder 4.0
// 
// -------------------------------------------------------------


// -------------------------------------------------------------
// 
// Module: SD_Mux5_block
// Source Path: sd_filter_tb/SD 2nd Order Modulator/SD Filter/node_3/SD_Mux5
// Hierarchy Level: 3
// 
// -------------------------------------------------------------

`timescale 1 ns / 1 ns

module SD_Mux5_block
          (in1,
           out1);


  input   in1;
  output  signed [24:0] out1;  // sfix25_En8


  wire switch_compare_1;
  wire signed [24:0] Constant3_out1;  // sfix25_En8
  wire signed [24:0] Constant2_out1;  // sfix25_En8
  wire signed [24:0] Switch1_out1;  // sfix25_En8


  assign switch_compare_1 = in1 > 1'b0;



  assign Constant3_out1 = 25'sb1111111110101001000110011;



  assign Constant2_out1 = 25'sb0000000001010110111001101;



  assign Switch1_out1 = (switch_compare_1 == 1'b0 ? Constant3_out1 :
              Constant2_out1);



  assign out1 = Switch1_out1;

endmodule  // SD_Mux5_block

