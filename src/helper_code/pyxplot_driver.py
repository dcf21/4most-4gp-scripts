# -*- coding: utf-8 -*-

"""
A wrapper for Pyxplot which allows us to run scripts to automatically produce plots with the dimensions specified
in <plot_settings>, and in all of the requested image formats. It also allows us to produce multiplots of all the
plots we've made with a single driver instance.
"""

import os
from math import floor
import pwd
import time

import plot_settings


class PyxplotDriver:
    """
    A wrapper for Pyxplot which allows us to run scripts to automatically produce plots with the dimensions specified
    in <plot_settings>, and in all of the requested image formats. It also allows us to produce multiplots of all the
    plots we've made with a single driver instance.
    """

    def __init__(self,
                 width=plot_settings.plot_width,
                 aspect=1 / 1.618034,
                 dpi=plot_settings.output_dpi,
                 multiplot_filename=None,
                 multiplot_aspect=5. / 8):
        """
        Instantiate a pyxplot instance.

        :param width:
            The width of the plots to be produced with this plotter, in cm.
        :param aspect:
            The aspect ratio of the plots to be produced with this plotter.
        :param dpi:
            The DPI resolution to use when making PNG images of plots
        :param multiplot_filename:
            The filename to give the multiplot of all the plots made with this plotter instance
        :param multiplot_aspect:
            The aspect ratio of the box to give each plot on the multiplot canvas
        """
        self.width = width
        self.aspect = aspect
        self.dpi = dpi
        self.multiplot_filename = multiplot_filename
        self.multiplot_aspect = multiplot_aspect
        self.multiplot_eps_files = []
        self.files_to_delete_on_exit = []

        # Look up user name and the current time, so that we can label plot with who created it and when
        self.user_name = pwd.getpwuid(os.getuid()).pw_gecos.split(",")[0]
        self.plot_creator = "{}, {}".format(self.user_name, time.strftime("%d %b %Y"))

    def make_plot(self, pyxplot_script, output_filename, data_files, caption="", add_to_multiplot=True):
        """
        Use Pyxplot to produce a plot.

        :param pyxplot_script:
            The Pyxplot commands used to produce the plot. You do not need to set the output size, filename or image
            format yourself, as we automatically deal with generating this boiler plate code.
        :param output_filename:
            The filename for the plot we're going to make. Omit the file format suffix, as this gets added later.
        :param data_files:
            A list of data files which we use to make this plot, and which we may want to clean up afterwards.
        :param caption:
            Possible caption to put in the top-left corner of the plot.
        :param add_to_multiplot:
            Boolean flag indicating whether to add this plot to a multiplot of all the output from this Pyxplot
            instance.
        :return:
        """

        # Wrap the pyxplot script to make this plot with code to set the size of the plot
        pyxplot_input = """

set width {width}
set size ratio {aspect}
set term dpi {dpi}
set nodisplay

set textvalign top
set label 1 "\parbox{{{width_caption}cm}}{{ {description} }}" at page 0.5, page {description_y}

set fontsize 0.8
set textvalign bottom
text "{plot_creator}" at 0, {plot_creator_y}
unset fontsize

{pyxplot_script}

""".format(width=self.width, aspect=self.aspect, dpi=self.dpi,
           width_caption=self.width * 0.5,
           description=caption if plot_settings.include_caption else "",
           description_y=self.width * self.aspect - 0.3,
           plot_creator=self.plot_creator if plot_settings.include_author else "",
           plot_creator_y=self.width * self.aspect + 0.4,
           pyxplot_script=pyxplot_script)

        # Work out what images format we need to produce this plot in. If we're making a multiplot, we're going to need
        # an EPS file for later.
        image_formats = list(plot_settings.output_formats)

        if add_to_multiplot and 'eps' not in image_formats:
            image_formats.append('eps')

        # Create a copy of this plot in all requested image formats
        for image_format in image_formats:
            pyxplot_input += """
            
set term {format}
set output '{filename}.{format}'
set display
refresh
        
""".format(filename=output_filename, format=image_format)

        # Run pyxplot
        p = os.popen("pyxplot", "w")
        p.write(pyxplot_input)
        p.close()

        # If we are not keeping the data files, add them to the list of things for the garbage collector to delete
        if not plot_settings.keep_data_files:
            self.files_to_delete_on_exit.extend(data_files)

        # If requested, add this plot to multiplot
        if add_to_multiplot:
            self.multiplot_eps_files.append("{filename}.eps".format(filename=output_filename))

            if 'eps' not in plot_settings.output_formats:
                self.files_to_delete_on_exit.append("{filename}.eps".format(filename=output_filename))

    def _make_multiplot(self):
        # Dimensions to make each individual plot in the multiplot canvas
        item_width = 8
        item_height = item_width * self.multiplot_aspect

        # Start building a Pyxplot script
        pyxplot_input = """
        
set nodisplay
set multiplot
        
        """

        # Insert each eps file in turn
        for index, eps in enumerate(self.multiplot_eps_files):
            pyxplot_input += """
            
eps "{eps_file}" at {x_pos},{y_pos} width {width}
            
""".format(eps_file=eps, width=item_width, x_pos=(item_width + 0.5) * (index % 2), y_pos=item_height * floor(index / 2))

        # Create a copy of this plot in all requested image formats
        for image_format in plot_settings.output_formats:
            pyxplot_input += """
            
set term {format}
set output '{filename}.{format}'
set display
refresh
        
""".format(filename=self.multiplot_filename, format=image_format)

        # Run pyxplot
        p = os.popen("pyxplot", "w")
        p.write(pyxplot_input)
        p.close()

    def __del__(self):
        """
        Destructor. Clean up. Make multiplot if we still need to do that. Delete any EPS files that are no longer
        needed.

        :return:
            None
        """

        # Make multiplot, if needed
        if (self.multiplot_filename is not None) and (len(self.multiplot_eps_files) > 0):
            self._make_multiplot()

        # Clean up files we no longer need
        for filename in self.files_to_delete_on_exit:
            os.system("rm -f {}".format(filename))
