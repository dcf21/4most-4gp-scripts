#!../../../../../virtualenv/bin/python3
# -*- coding: utf-8 -*-

# NB: The shebang line above assumes you've installed a python virtual environment alongside your working copy of the
# <4most-4gp-scripts> git repository. It also only works if you invoke this python script from the directory where it
# is located. If these two assumptions are incorrect (e.g. you're using Conda), you can still use this script by typing
# <python label_tabulator.py>, but <./label_tabulator.py> will not work.

"""
Take a load of plots listed on the command line, and compile them into a single gallery.
"""

import os
import sys


def multiplot_make(plot_list, columns=3, margin=1, width=20, aspect=1.618034, dpi=120):
    pyxplot_script = """
set output '/tmp/gallery.pdf'
set term pdf
set term dpi {dpi}

set multiplot
set nodisplay
    """.format(dpi=dpi)

    columns = int(columns)
    for index, item in enumerate(plot_list):
        column_number = (index % columns)
        x_pos = column_number * (width + margin)

        row_number = int(index / columns)
        y_pos = -row_number * (width / aspect + margin)

        command = "eps" if item.endswith("eps") else "image"

        pyxplot_script += """
{command} {image} width {width} at {x_pos}, {y_pos}
        """.format(command=command, image=item, width=width, x_pos=x_pos, y_pos=y_pos)

    pyxplot_script += """
set display
refresh

set output '/tmp/gallery.png'
set term png
refresh
    """

    # Run pyxplot script to make multiplot
    p = os.popen("pyxplot", "w")
    p.write(pyxplot_script)
    p.close()


# If we're invoked as a script, read input parameters from the command line
if __name__ == "__main__":
    # Read input parameters
    plot_list = sys.argv[1:]
    multiplot_make(plot_list=plot_list, aspect=1.8)
