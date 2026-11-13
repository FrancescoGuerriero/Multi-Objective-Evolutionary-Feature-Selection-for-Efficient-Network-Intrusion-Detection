# Experiment protocol

## Dataset and target

- Dataset: UNSW-NB15.
- Binary target: `label`.
- Drop `id` and `attack_cat` for binary classification.
- 42 raw predictors remain.
- Preserve the official test partition from all search and tuning decisions.

## Split protocol

For each seed (`42, 101, 202, 303, 404`):

1. Split the official training partition into training and validation data with stratification.
2. Fit preprocessing after raw-column selection.
3. Perform feature search only on training-derived data.
4. Select the candidate subset using validation information only.
5. Recombine the official train/validation rows, retrain the selected model, and evaluate once on the official test partition.

## Baselines

- Dummy Classifier (most frequent class)
- Logistic Regression
- Random Forest
- XGBoost

## Feature-selection methods

- GA
- BPSO
- PSO
- NSGA-II

GA/BPSO/PSO optimise the scalar objective:

`Macro-F1 - 0.05 * (selected_count / 42)`

NSGA-II optimises two separate objectives:

- maximise validation Macro-F1;
- minimise selected-feature ratio.

## Fairness control

The main search comparison uses exactly **300 unique expensive classifier evaluations per method per seed**. Cached duplicate masks consume no additional evaluation budget.

## Metrics

Primary:

- Macro-F1

Secondary:

- balanced accuracy;
- false-positive rate;
- selected feature count;
- feature reduction;
- optimisation runtime;
- inference latency;
- Jaccard feature-selection stability.

## Statistical interpretation

Five matched stochastic seeds are used. Friedman and pairwise Wilcoxon analyses are interpreted conservatively because `n=5` provides limited statistical power. Descriptive differences, seed wins, variance, and effect sizes should be reported alongside p-values.
