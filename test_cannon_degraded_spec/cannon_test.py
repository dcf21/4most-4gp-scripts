
# Construct and train a model.
model = tc.L1RegularizedCannonModel(training_set, training_flux, training_ivar,
    dispersion=common_dispersion, threads=-1)

model.s2 = 0
model.regularization = 0
model.vectorizer = tc.vectorizer.NormalizedPolynomialVectorizer(
    training_set, tc.vectorizer.polynomial.terminator(label_names, 2))

model.train()
model._set_s2_by_hogg_heuristic()
model.save(output_model_path, overwrite=True)

# Test the model.
test_files = glob("{}/star*_SNR*.txt".format(test_set_dirname))
N = len(test_files)
results = []
for i, filename in enumerate(test_files):
    print("Testing {}/{}: {}".format(i, N - 1, filename))

    dispersion, normalized_flux, normalized_flux_err = np.loadtxt(filename).T
    normalized_ivar = normalized_flux_err**(-2)

    # Ignore bad pixels.
    bad = (normalized_flux_err < 0) + (~np.isfinite(normalized_ivar * normalized_flux))
    normalized_ivar[bad] = 0
    normalized_flux[bad] = np.nan

    labels, cov, meta = model.fit(normalized_flux, normalized_ivar,
        full_output=True)

    # Identify which star it is, etc.
    basename = os.path.basename(filename)
    star = basename.split("_")[0].lstrip("star")
    snr = int(basename.split("_")[1].split(".")[0].lstrip("SNR"))

    err_labels = np.sqrt(np.diag(cov[0]))

    result = dict(zip(label_names, labels[0]))
    result.update(dict(zip(
        ["E_{}".format(label_name) for label_name in label_names], err_labels)))
    result.update({"star": star, "snr": snr})
    print(result)
    results.append(result)

# Show results.
with open("{}.json".format(output_path), "w") as f:
    f.write(json.dumps(results))

results = Table(rows=results)
results.write("{}.fits".format(output_path))

