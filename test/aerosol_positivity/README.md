# Aerosol positivity after state increments

`mpas_state_mod::add_incr` already applies a zero floor to hydrometeor and moisture fields. The change applies the same helper to 20 explicitly named GOCART aerosol mass-fraction fields. Chemical precursors are not included. Missing selected fields are ignored by the existing pool iterator. The SACA early-return path is unchanged.

For a controlled single-outer-loop analysis replay using identical input files, run:

```sh
python3 test/aerosol_positivity/check_analysis.py original_analysis.nc clipped_analysis.nc
```

The check requires all 20 configured aerosols to equal `max(0, reference)` exactly and all other compared fields to remain unchanged. It rejects missing aerosol fields, masked aerosol values, nonfinite aerosols, changed field sets, and unexpected changes in other fields. Use `--allow-reference-extras` only when the reference has additional workflow-appended carryover fields. Their names are explicitly reported as not compared; extra fields in the replay remain an error. This is an integration check using user-provided model files, not a self-contained CTest fixture. Multiple outer loops can change subsequent trajectories and need a different comparison.

The tested 550-nm-only analysis replay passed this check: all 20 aerosol fields matched the expected zero floor; 25 non-aerosol fields present in both files were unchanged. The completed workflow reference also contained land/carryover fields absent from the isolated replay; those were not compared. The 12-member ensemble-recentering replay also produced finite, nonnegative aerosols matching the expected clipped recentering within rounding tolerance. The recentering application invokes the same state increment operation.

Clipping is not mass conserving. It can increase the ensemble mean and reduce variance; recentering onto a central analysis is no longer exact after clipping negative members. In the tested ensemble, the unweighted sum of gridpoint variances decreased approximately 12–22% for carbonaceous aerosol fields and 12% for sulfate. These are case-specific variance changes, not universal bounds or standard-deviation changes.

A two-cycle end-to-end forecast/assimilation comparison is in progress. The replay tests do not establish behavior for every model state or justify changing observation QC, emission factors, or chemistry carryover settings.
