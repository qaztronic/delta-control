#

#
+librescan
+libext+.v+.sv+.vh+.svh
-y .
--timescale-override 1ps/1ps
--top-module top

#
../../../src/sd_filter/sd_filter_pkg.sv
../../../src/sd_filter/sd_filter_node.sv
../../../src/sd_filter/scaler_mux.sv
../../../src/sd_filter/sd_filter.sv
../../../src/sd_filter/sd_modulator.sv
../../../src/sd_filter/sd_filter_top.sv

./tb_top_pkg.sv
./top.sv
