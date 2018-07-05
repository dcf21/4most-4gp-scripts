# -*- coding: utf-8 -*-

"""
Take a list of eps files, and turn them into a Pyxplot multiplot.
"""

import os
from math import floor


def make_multiplot(eps_files, output_filename, aspect = 5./8):
    item_width = 8
    item_height = item_width * aspect

    # Start building a Pyxplot script
    ppl_script = """
    
    set nodisplay
    set multiplot
    
    """

    # Insert each eps file in turn
    for index, eps in enumerate(eps_files):
        ppl_script += """
        
        eps "{}" at {},{} width {}
        
        """.format(eps,
                   (item_width + 0.5) * (index % 2),
                   item_height * floor(index / 2),
                   item_width
                   )

    # Tell Pyxplot to produce some output
    ppl_script += """

set term eps ; set output "{0}.eps" ; set display ; refresh
set term png ; set output "{0}.png" ; set display ; refresh
set term pdf ; set output "{0}.pdf" ; set display ; refresh

""".format(output_filename)

    # Run pyxplot
    p = os.popen("pyxplot", "w")
    p.write(ppl_script)
    p.close()
