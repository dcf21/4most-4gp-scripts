The text on this page is a brief introduction to `4most-4gp-scripts`. For a
more complete tutorial, please visit the
[Wiki](https://github.com/dcf21/4most-4gp-scripts/wiki).

# 4most-4gp-scripts

The python scripts in this repository can be used to manipulate spectra in
various ways, including running all of the 4MOST IWG7 tests. These scripts
depend on the libraries in the [4most-4gp](https://github.com/dcf21/4most-4gp)
repository, which you must install first.

If you want to create your own tests, you can find pages in the sidebar on the
right which explain how to do various tasks. You may also want to read about
the [code layout](https://github.com/dcf21/4most-4gp-scripts/wiki/structure)
within this repository.

The rest of this page explains how to get started reproducing Dominic Ford's
4MOST IWG7 tests.

Firstly, you need some spectra to work with.

Create a directory called `workspace` inside the `4most-4gp-scripts` directory.
This is the default location where scripts will expect to find spectra. You can
change this if you really want to, but you'll have to pass a command line
argument to every script telling it your alternative location for your spectra.

Next, download our standard libraries of spectra, as [described
here](https://github.com/dcf21/4most-4gp-scripts/wiki/spectra). You should
expand these archives into the `workspace` directory.

To run the Cannon on these spectra, you should do the following:

```
cd 4most-4gp-scripts/src/scripts/test_cannon
 
mkdir -p ../../../output_data/cannon

python3 cannon_test.py --train "galah_training_sample_4fs_hrs[SNR=250]" \
                       --test "galah_test_sample_4fs_hrs" \
                       --description "4MOST HRS - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_hrs_10label"
python3 cannon_test.py --train "galah_training_sample_4fs_lrs[SNR=250]" \
                       --test "galah_test_sample_4fs_lrs" \
                       --description "4MOST LRS - 10 labels - Train on 0.25 GALAH. Test on 0.75 GALAH." \
                       --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                       --assume-scaled-solar \
                       --output-file "../../../output_data/cannon/cannon_galah_lrs_10label"

```

The output will get put in the `output_data/cannon` directory. The file `cannon_galah_hrs_10label.full.json.gz` will
contain the results of testing the Cannon, in gzipped JSON format. The file
`cannon_galah_hrs_10label.summary.json.gz` contains a subset of the information in the larger JSON file, describing
the parameters used in the run, but without the large table of results. The file `cannon_galah_hrs_10label.cannon`
is a binary file which contains the internal state of the trained Cannon.

To plot your results, [see here](https://github.com/dcf21/4most-4gp-scripts/wiki/visualisation).

