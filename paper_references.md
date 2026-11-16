

for hyperparameter selection (unsupervised DL):
https://www.mdpi.com/1424-8220/22/1/291?
Latent dimensions between 2 and 10.
Dropout between 0 and 0.3.
Different network depths.
Batch sizes of 32 and 64.
Their optimised models used latent dimensions of 6 and 7 for the conventional and variational autoencoders on one of their datasets, respectively. They also investigated dropout values of approximately 0.03 and 0.10.


https://pmc.ncbi.nlm.nih.gov/articles/PMC9030796/?
Batch size of 128.
Learning rate of 0.001.
Intermediate dimensions of 32 and 64 in their smaller architectures.
Latent dimensions of 16 and 32.
The authors also investigated the effect of changing the latent and intermediate dimensions on anomaly detection performance.
This supports your choice of batch size 128 and provides an industrial anomaly-detection precedent for investigating different latent and hidden-layer dimensions. Note that their architecture is an LSTM variational autoencoder, rather than your fully connected autoencoder

example:

### Autoencoder hyperparameter selection

Hyperparameter selection was performed to identify a suitable autoencoder architecture for representing battery-cycle behaviour and identifying potential anomalies. The principal hyperparameters considered were the latent dimension, hidden-layer dimension, dropout rate and learning rate.

An initial search space containing 160 possible hyperparameter combinations was identified. However, evaluating every combination was considered unnecessarily computationally expensive. Instead, a reduced and structured search strategy was adopted to investigate the most influential architectural and training parameters.

The latent dimension was selected as a primary hyperparameter because it determines the degree of compression applied to the input features. Three values (4, 8 and 16) were considered to investigate the effect of different levels of dimensionality reduction on reconstruction performance and the quality of the learned latent representations. These values were informed by previous research into autoencoder-based anomaly detection, including Jakubowski et al. (2022), who investigated latent dimensions between 2 and 10 when modelling industrial asset degradation.

The hidden-layer dimension was investigated using values of 32 and 64 neurons. These configurations were selected to compare a relatively compact network with one offering greater representational capacity. This was also informed by previous industrial time-series anomaly-detection research, such as Fährmann et al. (2022), which investigated intermediate network dimensions of 32 and 64.

The learning rate was investigated using values of 0.001 and 0.0001. These values were selected to compare a conventional initial learning rate for Adam optimisation with a smaller learning rate, which may provide more gradual weight updates during training. A batch size of 128 was retained throughout the experiments, providing consistency between configurations and aligning with batch sizes used in related industrial anomaly-detection research (Fährmann et al., 2022).

Dropout was initially fixed at zero to isolate the effects of architectural capacity and learning rate. Following the initial experiments, a dropout rate of 0.15 was considered for selected configurations to investigate whether additional regularisation improved generalisation and reduced overfitting. This value was within the range investigated in previous autoencoder-based degradation research (Jakubowski et al., 2022).

The maximum number of training epochs was set to 100, with early stopping using a patience of 10 epochs. This allowed sufficient training time while limiting unnecessary computation when validation performance ceased to improve.

The resulting initial search consisted of 12 configurations, followed by additional regularisation experiments on selected architectures. This staged approach reduced computational requirements while retaining the ability to investigate the influence of the principal hyperparameters. The use of a targeted search rather than exhaustive grid search is also consistent with the findings of Bergstra and Bengio (2012), who demonstrated the computational advantages of more selective hyperparameter-search strategies.

Model selection was based on validation performance, considering reconstruction error and the suitability of the learned representations for subsequent anomaly detection. The final configuration was selected based on its observed performance rather than assuming that the lowest reconstruction error alone necessarily represented the best anomaly-detection model.