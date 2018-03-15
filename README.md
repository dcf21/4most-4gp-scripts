# 4most-4gp-scripts

The python scripts in this repository can be used to manipulate spectra in various ways, including running
all of the 4MOST IWG7 tests. These scripts depend on the libraries in the
[4most-4gp](https://github.com/dcf21/4most-4gp)
repository, which you must install first.

If you want to create your own tests, you can find pages in the sidebar on the right which explain how to do
various tasks. You may also want to read about the 
[code layout](structure)
within this repository.

The rest of this page explains how to get started reproducing Dominic Ford's 4MOST IWG7 tests.

Firstly, you need some spectra to work with.

Create a directory called `workspace` inside the `4most-4gp-scripts` directory. This is the default location where
scripts will expect to find spectra. You can change this if you really want to, but you'll have to pass a
command line argument to every script telling it your alternative location for your spectra.

Next, download our standard libraries of spectra, as [described here](spectra). You should expand these archives
into the `workspace` directory.

To run the Cannon on these spectra, you should do the following:

```
cd 4most-4gp-scripts/test_cannon
 
mkdir -p ../output_data/cannon
 
python2.7 cannon_test.py --train "4fs_ahm2017_sample_hrs[SNR=250,continuum_normalised=1]" \
                         --test "4fs_ahm2017_perturbed_hrs[continuum_normalised=1]" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST HRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_hrs_10label"
                         
python2.7 cannon_test.py --train "4fs_ahm2017_sample_lrs[SNR=250,continuum_normalised=1]" \
                         --test "4fs_ahm2017_perturbed_lrs[continuum_normalised=1]" \
                         --censor "line_list_filter_2016MNRAS.461.2174R.txt" \
                         --description "4MOST LRS (censored) - 10 labels - Train on GES UVES AHM2017. Test on perturbed version." \
                         --labels "Teff,logg,[Fe/H],[Ca/H],[Mg/H],[Ti/H],[Si/H],[Na/H],[Ni/H],[Cr/H]" \
                         --assume-scaled-solar \
                         --output-file "../output_data/cannon/cannon_ahm2017_perturbed_censored_lrs_10label"
```

The output will get put in the `output_data/cannon` directory. The file `cannon_ahm2017_perturbed_censored_hrs_10label.json`
will contain the results of testing the Cannon. The file `cannon_ahm2017_perturbed_censored_hrs_10label.cannon` is a binary
file which contains the internal state of the trained Cannon.


To plot your results, [see here](visualisation).
