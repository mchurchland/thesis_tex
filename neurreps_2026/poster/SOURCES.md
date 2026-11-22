# Poster sources — MC200 sketch revision

The poster remains **61 × 85 cm, portrait**, with the two-pane methods band and
three-column result rows requested in the four November 22 camera sketches.
The sketches guide layout only; their photographs do not appear on the poster.
The previous poster is preserved under `archive/before_sketch_mc200_2026-11-22/`.
Original data, analyses, earlier poster archives and papers are unchanged.

## Sources and estimands

All new figure inputs come from
`analysis/mc200_recompute/mc200_274500/`. `build_figures.py` checks each CSV
against that analysis manifest before plotting; hashes and exact selections are
recorded in `poster_sources.json`. The source experiment is MC200 run 274500
(100 paired realizations, 11 E/I fractions, 24 settings). NARMA10 is joined from
the archived architecture 271871, WS 272279 and ER-distribution 274402 runs.

MC200 sums held-out squared correlations for delays 1–200. Its test segment is
5,000 samples; the NARMA10 segment remains 500 samples and was not rerun.
Both tasks retain 500 washout, 1,500 train and 500 validation samples. The ridge
penalty is chosen on validation. Recurrent weights are fixed during each task.
All nodes receive scalar input through a shared projection per realization.

All principal result panels use **own-radius scaling**. The critics' corner
compares paired performance gaps across own-radius, fixed-reference and
shared-CE-multiplier scaling. Shared CE scaling applies CE's current multiplier
to every comparison model; it still varies across E/I fractions.

Performance AUC integrates the mean score across the observed E/I fractions
and divides by the observed span. Grid settings receive equal weight; trapezoid
integration gives half endpoint weights. MC keeps capacity units, and NARMA
keeps NMSE units. No win-fraction AUC is plotted. Intervals are the existing
1,000 whole-paired-realization bootstrap percentile intervals (seed 20261122),
with no multiplicity adjustment. Hyperparameter settings are a fixed design,
not independent biological samples.

## Panel-by-panel

- **Methods and sweep:** 297 nodes and 3,604 chemical edges, checked directly
  from `Connectome/ce_adj.npy` (1,740 known-sign edges) plus
  `Connectome/ce_unknown_sign_weights.npy` (1,864 other chemical edges).
  Contact counts provide magnitude proxies. Radius {0.6, 0.95, 1.05}, leak
  {0.6, 1.0}, input {0.01, 0.1, 0.5, 1.5}, bias zero.
- **Edge-sign illustration:** one fixed five-node, ten-edge directed
  schematic in a NetworkX Kamada–Kawai layout. This is explicitly not a
  CE subgraph or a ring. Gray nodes stay neutral. Red denotes negative edges;
  blue denotes positive edges. One random permutation is drawn with the
  production `rng_for(seed, 'CE nested sign order')`; the first floor(pM)
  edges become negative at p=0, 0.2 and 0.5 (0, 2 and 5 of 10 edges).
  Positions, connectivity and order stay fixed across the panels. The actual
  experiment draws a different order for each realization, while fractions
  within it are nested. This follows `raw_networks` in
  `network_stats/architecture_sweep.py`. The figure never implies inhibitory
  neuron classes, independently redrawn signs at every fraction, or a biologically
  inferred E/I balance. `poster_data/edge_sign_schematic.json` retains all
  coordinates, edges, order and masks.
  `poster_data/sign_nesting_audit.json` additionally checks the archived source
  snapshot and cached 20%/50% matrices for CE empirical, ER binary and WS-like
  empirical weights over all 100 realizations (300 comparisons). Every
  inhibitory edge at 20% remains inhibitory at 50%; none are moved or reverted.
- **MC input-drive panel:** `architecture/mean_performance.csv`; empirical CE
  versus binary ER at the selected input scales 0.01 and 0.5. Each curve averages six
  radius/leak settings. One plot distinguishes the two inputs by color,
  with CE solid and ER dashed.
  A linear vertical axis (7.5–39.5) retains every displayed mean;
  fill highlights CE-leading regions. The top-right inset uses normal
  `architecture/performance_auc.csv` within each displayed input (six radius/leak settings).
  The callout explicitly reports the aggregate over all 24 settings, including
  input strengths 0.1 and 1.5, which are omitted from this illustration.
- **Structural MC AUC:** three groups distinguish empirical CE weight
  placement, topology with binary weights, and magnitude distribution on ER.
  The exact source is `architecture/performance_auc.csv`, metric MC_200,
  normalization own_radius, input ALL. The placement group retains original versus shuffled empirical magnitudes;
  shuffling preserves the signed multiset within sign classes. The topology
  group instead uses CE binary, ER binary and WS-like binary, avoiding a
  change in the raw magnitude distribution. Own-radius scaling still changes
  effective units between matrices. The critics' corner shows the complementary
  common-multiplier check for the same binary controls.
- **ER weight MC AUC:** `er/performance_auc.csv`, all ten distributions,
  MC_200 / own_radius / ALL. Caps at Q99, Q95, Q90 restore mean magnitude.
  Gamma/lognormal fixed mid-quantile vectors match realized mean and population
  variance, with rank-based placement and paired tie-breaking. They are not
  iid draws or maximum-likelihood fits. Compression uses w'=mu+a(w-mu).
  The gamma gain is +0.319769 MC AUC [0.296132, 0.344778], or 1.9394%.
  Lognormal and compression worsen the aggregate; all caps improve MC200.
  This does not isolate one tail statistic, norm or eigenmode as the mechanism.
- **NARMA replication:** architecture and ER normal error AUCs for seven
  selected models, plus one CE/binary-ER plot averaged equally over all 24
  input/radius/leak settings. The two curves use the stored ALL summaries and
  their whole-realization bootstrap intervals, not averages of interval endpoints.
  Their integrated means match the AUCs above. Gamma reduces error AUC by 0.001351915 [0.000850659, 0.002110294],
  or 0.8927%. The bottom row therefore does not silently reuse MC numbers.
- **Critics' corner:** paired ER-binary/WS-binary-minus-CE-binary MC AUC
  gaps, recomputed from `architecture/performance_auc_per_realization.csv`
  with the same whole-realization bootstrap (1,000 draws, seed 20261122).
  A shared CE multiplier reverses CE versus ER binary in the aggregate,
  while WS-like binary retains an advantage. Peak rankings come from
  `descriptive_peak_MC200.csv`: own-radius maxima of seed-mean test scores
  across the fixed grid. They are descriptive, test-selected maxima, not
  independently validated hyperparameter tuning or AUC rankings. The poster
  displays the top three models plus original CE (rank 11). The full
  twelve-model ordering is retained in `poster_data/peak_mc200_ordering.csv`.

The script saves each selected table under `poster_data/` so the plotted points
and printed effect sizes can be reviewed without loading the full runs.

## Claims and limits

The poster emphasizes that CE's advantage over **binary ER** is concentrated
under weak drive and E/I imbalance; this does not imply exclusivity to those
conditions or superiority to better-matched controls. Magnitude shuffling and
replacing CE wiring improve average MC in this protocol. Empirical CE magnitudes
are useful on ER relative to binary/half-normal, but do not maximize peak MC
and are not uniformly best across all architectures. Gamma is a modest
improvement, not evidence that every moment-matched distribution helps.

The topology statements explicitly refer to own-radius scaling. The final
takeaway emphasizes identifying which features of a biological substrate
provide a computational advantage; the distributional mechanism behind the
gamma gain remains unresolved.

Own-radius mean MC AUC: CE 11.3943, ER binary 14.9266, ER with CE weights
16.4880, WS-like with CE weights 17.8617. WS half-normal's mean AUC is slightly
higher (17.9071), but the paired difference from WS empirical is uncertain
[−0.0584, 0.1512]. No claim of a uniquely optimal distribution on WS is made.

There are no electrical synapses, Dale neuron-class signs, trained recurrent
weights, or claims about natural worm memory. The removed-edge CE control
retains only 1,740 chemical edges and is not density-matched to full CE/ER.
WS denotes the repository's directed WS-like control, not a replacement model.
The retained author list, affiliations and references match the previous poster:
Fenyves et al. (2020), PLOS Computational Biology 16:e1007974;
Jaeger (2002), GMD Technical Report 152. Compute acknowledgement: Orca, PSU.
