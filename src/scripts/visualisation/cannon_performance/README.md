## visualision/cannon_performance

The scripts in this directory are used to extract data from the JSON files produced when the Cannon
is run using the script `test_cannon/cannon_test.py`.

#### label_tabulator.py

A simple starting point is the script `label_tabulator.py`. This produces an ASCII table of the Cannon's
estimates for the parameters being fitted, together with their target values (taken from the metadata
associated with each spectrum). It also tabulates the formal uncertainty in the Cannon's estimates; note that
these are invariably much smaller than the true error.

The command line syntax for `label_tabulator.py` is:

```
python2.7 label_tabulator --cannon-output "../output_data/cannon/my_cannon_run.json" \
                          --labels "Teff,logg,[Fe/H]" \
                          --output-stub /tmp/my_cannon_data
```

The output from this script can be plotted in many plotting programs. I usually use Pyxplot, but that's only
because I happen to have written it :-).

The first line of the output tells you the names of each of the columns of data.

A separate ASCII file is produced containing spectra at every SNR found within the Cannon run. The option
`--labels` may be omitted, in which case a table is produced listing all the parameters the Cannon tried to
estimate.

#### plot_everything.sh

The other scripts in this directory automatically produce many of the types of plot we have used within IWG7.
The highest degree of automation is offered by the script `plot_everything.sh`, which automatically scans the
directory `../output_data/cannon`, sees what Cannon tests you've run, and plots some standard charts for each one.

This script also produces a few comparison plots which will only work if you've run specific sets of tests. It
will produce warning messages if it can't find the Cannon output from these specific tests, but you can safely
ignore these warnings.

Details of the particular plots we frequently produce are summarised below, together with the python scripts used
to generate them.

#### mean_performance_vs_labels.py

If you have run the Cannon on spectra at multiple SNRs, use this script to produce a plot of the RMS offset
in the Cannon's label estimates as a function of SNR. In its simplest form, the command line syntax is:

```
python2.7 mean_performance_vs_label.py --cannon-output "../../output_data/my_cannon_run.json" \
      --output-file "../../output_plots/cannon_performance/performance_vs_label/my_cannon_run"
```

It also supports plotting several Cannon runs side-by-side, as in:

```
python2.7 mean_performance_vs_label.py \
      --cannon-output "../../output_data/cannon/run_A.json" --dataset-label "Data A" --dataset-colour "green" \
      --cannon-output "../../output_data/cannon/run_B.json" --dataset-label "Data B" --dataset-colour "red" \
      --output-file "../../output_plots/cannon_performance/performance_vs_label/my_cannon_runs"
```

You can use the `--dataset-filter` command line option to filter the stars to plot. If you want to filter one
Cannon output, you must specify a filter for every Cannon-output, but they are allowed to be blank:

```
python2.7 mean_performance_vs_label.py \
              --cannon-output "../../output_data/cannon/lrs.json" --dataset-filter "logg<3.25;0<[Fe/H]<1" --dataset-label "Giants; [Fe/H]\$>0\$" --dataset-colour "purple" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/lrs.json" --dataset-filter "logg>3.25;0<[Fe/H]<1" --dataset-label "Dwarfs; [Fe/H]\$>0\$" --dataset-colour "pink" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/lrs.json" --dataset-filter "logg<3.25;-0.5<[Fe/H]<0" --dataset-label "Giants; \$-0.5<\$[Fe/H]\$<0\$" --dataset-colour "blue" --dataset-linetype 1 \
              --cannon-output "../../output_data/cannon/lrs.json" --dataset-filter "logg>3.25;-0.5<[Fe/H]<0" --dataset-label "Dwarfs; \$-0.5<\$[Fe/H]\$<0\$" --dataset-colour "red" --dataset-linetype 1 \
              --abundances-over-fe \
              --output-file "../../output_plots/cannon_performance/performance_vs_label/my_plots"
```

This example also demonstrates the use of the `--abundances-over-fe` option, to plot the precision
of abundances over Fe, rather than H.

To see all the commandline options available, type `python2.7 mean_performance_vs_label.py --help`.

#### scatter_plot_coloured.py

This produces a coloured scatter plot of the offsets in the Cannon's estimates of some particular label.

Take the following example:

```
python2.7 scatter_plot_coloured.py --label "Teff{7000:3400}" --label "logg{5:0}" \
          --label-axis-latex "Teff" --label-axis-latex "log(g)" \
          --label-axis-latex "[Fe/H]" \
          --colour-by-label "[Fe/H]{:}" \
          --colour-range-min " -0.3" \
          --colour-range-max " 0.3" \
          --cannon-output "../../output_data/cannon/lrs.json" \
          --output-stub "../../output_plots/cannon_performance/label_offsets/my_plots"
```

The chart produced has Teff and log(g) on its horizontal and vertical axes respectively - these two parameters
being specified using the `--label` command line option. The positions of the points on the scatter plot
are the true values of these parameters.

The points are colour coded according to the error in the Cannon's estimates of [Fe/H], with colours representing
offsets from -0.3 to 0.3.

#### scatter_plot_snr_required.py

This produces a coloured scatter plot of the minimum SNR required for the Cannon to meet some precision target
on some particular label.

Take the following example:

```
python2.7 scatter_plot_snr_required.py --label "Teff{7000:3400}" --label "logg{5:0}" \
  --label-axis-latex "Teff" --label-axis-latex "log(g)" \
  --label-axis-latex "[Fe/H]" \
  --colour-by-label "[Fe/H]" \
  --target-accuracy "0.1" \
  --colour-range-min 30 --colour-range-max 120 \
  --cannon-output "../../output_data/cannon/lrs.json" \
  --accuracy-unit "dex" \
  --output-stub "../../output_plots/cannon_performance/required_snrA/my_plots"
```

The chart produced has Teff and log(g) on its horizontal and vertical axes respectively - these two parameters
being specified using the `--label` command line option. The positions of the points on the scatter plot
are the true values of these parameters.

The points are colour coded according to the SNR required to match [Fe/H] to within a precision of 0.1 dex. SNR
values between 30 and 120 are represented by a colour scale.
