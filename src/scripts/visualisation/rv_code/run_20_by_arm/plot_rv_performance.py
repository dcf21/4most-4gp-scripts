#!../../../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python plot_rv_performance.py>, but <./plot_rv_performance.py> will not work.

import os
import glob

from multiplot_maker import multiplot_make

# from filters import filters

# Read index of runs
run_index = {}
run_pids = []
for line in open("data/run_index.dat"):
    line = line.strip()

    # Ignore blank lines
    if line == "" or line[0] == "#":
        continue

    words = line.split()
    run_letter = words[0]
    run_pid = words[1]
    run_description = line[14:]

    run_index[run_pid] = [run_letter, run_pid, run_description]
    run_pids.append(run_pid)

for run_pid in run_pids:
    pid = run_index[run_pid]
    print("Working on run {} -- {}".format(pid[1], pid[2]))

    pyxplot_input = """

bw=20
width=12

set width width

set xlabel 'Radial velocity error [m/s]'
set ylabel 'Stars per unit RV'

set texthalign left
set textvalign top
set label 1 "%s) %s"%("{run_letter}", "{run_description}") at page 0.5, page width/goldenRatio-0.3
set key top right

v_max = 10e3

histogram [-v_max:v_max] h0() "data/test_rv_code_HRS_0_%s.dat"%"{run_pid}" using ($9-$8)*1000 binwidth bw
histogram [-v_max:v_max] h1() "data/test_rv_code_HRS_1_%s.dat"%"{run_pid}" using ($9-$8)*1000 binwidth bw
histogram [-v_max:v_max] h2() "data/test_rv_code_HRS_2_%s.dat"%"{run_pid}" using ($9-$8)*1000 binwidth bw
histogram [-v_max:v_max] l0() "data/test_rv_code_LRS_0_%s.dat"%"{run_pid}" using ($9-$8)*1000 binwidth bw
histogram [-v_max:v_max] l1() "data/test_rv_code_LRS_1_%s.dat"%"{run_pid}" using ($9-$8)*1000 binwidth bw
histogram [-v_max:v_max] l2() "data/test_rv_code_LRS_2_%s.dat"%"{run_pid}" using ($9-$8)*1000 binwidth bw

set term eps
set output 'output/rv_performance_%s.eps'%"{run_letter}"
plot [-2000:2000] h0(x) title 'HRS blue' w histeps, h1(x) title 'HRS green' w histeps, h2(x) title 'HRS red' w histeps, l0(x) title 'LRS blue' w histeps, l1(x) title 'LRS green' w histeps, l2(x) title 'LRS red' w histeps col green

set term png
set output 'output/rv_performance_%s.png'%"{run_letter}"
refresh

foreach mode in ["HRS", "LRS"] {{
foreach arm in [0,1,2] {{

rv_range_min = {{"HRS":-800, "LRS":-3000}}[mode]
rv_range_max = {{"HRS": 800, "LRS": 3000}}[mode]

arm_name = "%s%s"%(mode,arm)
pixel_multiplicative_spacing = {{ \
   "HRS0":1.0000182856961957, \
   "HRS1":1.0000185173103215, \
   "HRS2":1.0000185719409722, \
   "LRS0":1.0000836518159060, \
   "LRS1":1.0000615715894605, \
   "LRS2":1.0000608590412805  \
}}[arm_name]

set xlabel 'Radial velocity in [m/s]'
set ylabel 'Radial velocity error [m/s]'
set nokey
set term eps
set output 'output/rv_performance_%s_%s_%s_D.eps'%(mode,arm,"{run_letter}")
set width width
set label 1 "%s) %s (%s %s)"%("{run_letter}", "{run_description}", mode, arm) at page 0.5, page width/goldenRatio-0.3
plot [][rv_range_min:rv_range_max] "data/test_rv_code_%s_%s_%s.dat"%(mode,arm,"{run_pid}") using ($8*1000) : ($9-$8)*1000 w dots ps 6

set term png
set output 'rv_performance_%s_%s_%s_D.png'%(mode,arm,"{run_letter}")
refresh

set xlabel 'Inter-pixel offset'
set ylabel 'Radial velocity error [m/s]'
set nokey
set term eps
set output 'output/rv_performance_%s_%s_%s_E.eps'%(mode,arm,"{run_letter}")
set width width
set label 1 "%s) %s (%s %s)"%("{run_letter}", "{run_description}", mode, arm) at page 0.5, page width/goldenRatio-0.3
c = 299792458.
plot [][rv_range_min:rv_range_max] "data/test_rv_code_%s_%s_%s.dat"%(mode,arm,"{run_pid}") using (log(sqrt((c-$8*1000)/(c+$8*1000)))/log(pixel_multiplicative_spacing)) % 1 : ($9-$8)*1000 w dots ps 6

set term png
set output 'output/rv_performance_%s_%s_%s_E.png'%(mode,arm,"{run_letter}")
refresh


set xlabel 'Reported radial velocity uncertainty [m/s]'
set ylabel 'Radial velocity offset [m/s]'
set nokey
set term eps
set output 'output/rv_performance_%s_%s_%s_F.eps'%(mode,arm,"{run_letter}")
set width width
set label 1 "%s) %s (%s %s)"%("{run_letter}", "{run_description}", mode, arm) at page 0.5, page width/goldenRatio-0.3
x_max = (mode == "HRS") ? 500 : 2500
y_max = (mode == "HRS") ? 300 : 2000
plot [0:x_max][-y_max:y_max] "data/test_rv_code_%s_%s_%s.dat"%(mode,arm,"{run_pid}") using ($10*1000) : ($9-$8)*1000 w dots ps 3

set term png
set output 'output/rv_performance_%s_%s_%s_F.png'%(mode,arm,"{run_letter}")
refresh


colour_range_min = (mode=="LRS") ? -1000 : -200
colour_range_max = -colour_range_min
colour_bar_width = width / goldenRatio * 0.05
colour_bar_x_pos = width + 1

col_scale_z(z) = min(max(  (z-colour_range_min) / (colour_range_max-colour_range_min)  ,0),1)
col_scale(z) = hsb(0.75 * col_scale_z(z), 1, 1)

set term eps
set output 'output/rv_performance_%s_%s_%s_A.eps'%(mode,arm,"{run_letter}")

set multiplot
set nodisplay
clear
set nokey
set width width
set xlabel 'Teff / K'
set ylabel 'log(g) / dex'
set label 1 "%s) %s (%s %s)"%("{run_letter}", "{run_description}", mode, arm) at page 0.5, page width/goldenRatio-0.3
plot [7000:3400][5:0] "data/test_rv_code_%s_%s_%s.dat"%(mode,arm,"{run_pid}") using 2:4 with dots colour col_scale(($9-$8)*1000) ps 8

unset label
set noxlabel
set xrange [0:1]
set noxtics ; set nomxtics
set axis y right
set ylabel "Offset in RV"
set yrange [colour_range_min:colour_range_max]
set c1range [colour_range_min:colour_range_max] norenormalise
set width colour_bar_width
set size ratio 1 / 0.05
set colormap col_scale(c1)
set nocolkey
set sample grid 2x200
set origin colour_bar_x_pos, 0
plot y with colourmap

set display
refresh
set term png
set output 'output/rv_performance_%s_%s_%s_A.png'%(mode,arm,"{run_letter}")
refresh
set nomultiplot
unset axis x y ; unset size ; unset origin

set term eps
set output 'output/rv_performance_%s_%s_%s_B.eps'%(mode,arm,"{run_letter}")

set multiplot
set nodisplay
clear
set nokey
set width width
set xlabel '[Fe/H]'
set ylabel 'log(g) / dex'
set label 1 "%s) %s (%s %s)"%("{run_letter}", "{run_description}", mode, arm) at page 0.5, page width/goldenRatio-0.3
plot [-2:0.5][5:0] "data/test_rv_code_%s_%s_%s.dat"%(mode,arm,"{run_pid}") using 6:4 with dots colour col_scale(($9-$8)*1000) ps 8

unset label
set noxlabel
set xrange [0:1]
set noxtics ; set nomxtics
set axis y right
set ylabel "Offset in RV"
set yrange [colour_range_min:colour_range_max]
set c1range [colour_range_min:colour_range_max] norenormalise
set width colour_bar_width
set size ratio 1 / 0.05
set colormap col_scale(c1)
set nocolkey
set sample grid 2x200
set origin colour_bar_x_pos, 0
plot y with colourmap

set display
refresh
set term png
set output 'output/rv_performance_%s_%s_%s_B.png'%(mode,arm,"{run_letter}")
refresh
set nomultiplot
unset axis x y ; unset size ; unset origin

}}
}}

""".format(run_letter=pid[0], run_pid=pid[1], run_description=pid[2])

    # Run pyxplot
    p = os.popen("pyxplot", "w")
    p.write(pyxplot_input)
    p.close()

for mode in ["HRS", "LRS"]:
    for arm in [0, 1, 2]:
        for plottype in ["A", "B", "D", "E", "F"]:
            multiplot_make(columns=2,
                           aspect=1.6,
                           plot_list=sorted(glob.glob("output/rv_performance_%s_%s_*_%s.eps" % (mode, arm, plottype)))
                           )
            os.system("mv /tmp/gallery.pdf output/gallery_%s_%s_%s.pdf" % (mode, arm, plottype))
            os.system("mv /tmp/gallery.png output/gallery_%s_%s_%s.png" % (mode, arm, plottype))

os.system("python3 multiplot_maker.py output/rv_performance_?.eps")
os.system("mv /tmp/gallery.pdf output/gallery_0.pdf")
os.system("mv /tmp/gallery.png output/gallery_0.png")
