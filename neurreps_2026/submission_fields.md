# NeurReps 2026 submission fields

## Title

Determinants of hyperparameter robustness in connectome reservoir computing

## Abstract

Reservoir computing provides a controlled setting for studying how recurrent network architecture shapes computation: input signals are projected into a high-dimensional state space by a fixed nonlinear dynamical system, and only the readout is trained. However, reservoir performance can be strongly dependent on hyperparameters; this paper asks which recurrent network features support robustness to those parameter changes. We characterize computational performance using memory capacity (MC), truncated single-delay information-processing capacity (IPC), and kernel rank (KR). Generalization across input histories is measured using generalization rank (GR), while hyperparameter robustness is quantified using the coefficient of variation (CV) of each metric across sweeps of target spectral radius, input scaling, leak rate, and neuron bias.

To examine the architectural determinants of robustness, we construct controlled perturbations that alter connectivity topology, excitatory/inhibitory sign structure, weight magnitudes, and weight placement while preserving complementary properties. Across these experiments, the *C. elegans* connectome consistently occupies a relatively low-variance regime.

The central result is a performance--robustness tradeoff: architecture variants with higher task-agnostic performance also tend to exhibit greater hyperparameter sensitivity and poorer generalization across input histories. Across the E/I edge balance sweeps and shuffle controls, this tradeoff is closely associated with the raw spectral radius before normalization. Because every perturbed matrix is subsequently rescaled to the same target radius, matrices with lower raw spectral radius receive greater global amplification of their recurrent weights. The observed differences among architectures therefore characterize the joint effects of structural variation and architecture-specific global rescaling under spectral-radius normalization.

## TL;DR

The *C. elegans* connectome occupies a low-variance reservoir regime; higher task-agnostic performance coincides with greater hyperparameter sensitivity and poorer generalization.

## NeurReps relevance

The rank analysis connects recurrent architecture to representation structure. Kernel rank measures effective dimensionality available to separate distinct input histories, whereas generalization rank measures dimensions attributable to earlier history after streams share a recent signal. The results show that higher-dimensional, more separable states need not be more invariant or hyperparameter-robust: their geometry depends jointly on connectome topology, sign and weight placement, and the operating regime imposed by spectral-radius normalization. This provides a connectome-level account of recurrent separation and generalization without task-specific recurrent training.

## Keywords

reservoir computing; connectomics; representational geometry; recurrent neural networks; hyperparameter robustness

## Submission notes

- Select the **Extended Abstract Track**.
- Upload `paper.pdf`; its scientific content occupies pages 1--4 and references begin on page 5.
- The review PDF contains no authors, affiliations, acknowledgements, or identifying code links.
- Enter authors and affiliations only in the private submission-system fields during double-blind review.
- Recheck the live submission form and deadline before uploading.
