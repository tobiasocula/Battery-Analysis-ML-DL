# cycle_autoencoder_keras.py
#
# Simple unsupervised deep-learning baseline for battery charge-discharge cycles.
#
# Input: one row = one battery cycle.
# Output:
#   - Reconstruction error per cycle (anomaly/degradation score)
#   - 8-dimensional latent embedding for clustering / visualization
#
# The model does not use degradation_status during training.

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


# ---------------------------------------------------------------------------
# Your existing setup
# ---------------------------------------------------------------------------

df = pd.read_csv("battery_observations.csv", index_col=0)
meta = pd.read_csv("battery_metadata.csv", index_col=0)

df2 = df.join(meta[["climate_zone", "chemistry"]])
df2 = df2.sort_values(["battery_id", "cycle_index"])
df2 = df2.reset_index()
meta = meta.reset_index()

g = lambda x: int(x.split("-")[-1])
df2["battery_id"] = df2["battery_id"].apply(g)
meta["battery_id"] = meta["battery_id"].apply(g)

battery_ids = list(set(df2["battery_id"]))
materials = list(set(meta["chemistry"]))
climate_zones = list(set(meta["climate_zone"]))
labels = list(set(df2["degradation_status"]))

train_labels = pd.read_csv("train_batteries.csv")["battery_id"].apply(g)
val_labels = pd.read_csv("validation_batteries.csv")["battery_id"].apply(g)

train = df2[df2["battery_id"].isin(train_labels)]
val = df2[df2["battery_id"].isin(val_labels)]


# ---------------------------------------------------------------------------
# Feature selection
# ---------------------------------------------------------------------------

# Never use these as model inputs: they are labels or direct health/RUL measures.
LABEL_COLUMNS = [
    "degradation_status",
    "eol_reached",
    "remaining_useful_cycles",
    "remaining_useful_efc",
    "state_of_health_pct",
]

# Not useful as numeric model inputs.
ID_COLUMNS = [
    "battery_id",
    "timestamp",
    "cycle_index",
]

# Optional metadata columns. They can be included later, but chemistry and
# climate zone are categorical and would require one-hot encoding.
META_COLUMNS = [
    "climate_zone",
    "chemistry",
]

# Features used by the first simple autoencoder.
FEATURE_COLUMNS = [
    "battery_age_days",
    "time_since_previous_cycle_hours",
    "equivalent_full_cycles",
    "soc_start_pct",
    "soc_end_pct",
    "depth_of_discharge_pct",
    "high_soc_exposure_fraction",
    "low_soc_exposure_fraction",
    "charge_c_rate",
    "discharge_c_rate",
    "charge_current_a",
    "discharge_current_a",
    "charge_duration_min",
    "discharge_duration_min",
    "energy_discharged_kwh",
    "ambient_temp_c",
    "pack_temp_c",
    "cumulative_high_temp_hours",
    "cooling_active",
    "pack_voltage_mean_v",
    "pack_voltage_charge_v",
    "pack_voltage_discharge_v",
    "internal_resistance_mOhm",
]


def make_feature_matrix(dataframe, feature_columns=FEATURE_COLUMNS):
    """
    Extracts the numeric feature matrix used by the autoencoder.

    Returns
    -------
    X : np.ndarray, shape (n_cycles, n_features)
    feature_names : list[str]
    """
    missing = [c for c in feature_columns if c not in dataframe.columns]
    if missing:
        raise ValueError(f"Missing expected feature columns: {missing}")

    X = dataframe[feature_columns].copy()

    # Simple missing-value handling. Median imputation is robust for a baseline.
    X = X.fillna(X.median(numeric_only=True))

    # Convert booleans such as cooling_active to numeric values.
    X = X.astype(np.float32)

    return X.to_numpy(), feature_columns


X_train_raw, feature_names = make_feature_matrix(train)
X_val_raw, _ = make_feature_matrix(val, feature_names)

# Standardize using training statistics only.
feature_mean = X_train_raw.mean(axis=0)
feature_std = X_train_raw.std(axis=0)
feature_std[feature_std == 0] = 1.0

X_train = ((X_train_raw - feature_mean) / feature_std).astype(np.float32)
X_val = ((X_val_raw - feature_mean) / feature_std).astype(np.float32)

n_features = X_train.shape[1]
print(f"Training cycles: {X_train.shape[0]}")
print(f"Validation cycles: {X_val.shape[0]}")
print(f"Number of features: {n_features}")


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

LATENT_DIM = 8
HIDDEN_DIM = 32
DROPOUT = 0.0
LEARNING_RATE = 1e-3


def build_autoencoder(
    n_features,
    hidden_dim=HIDDEN_DIM,
    latent_dim=LATENT_DIM,
    dropout=DROPOUT,
):
    """
    Plain fully connected autoencoder.

    Architecture:
        n_features -> hidden_dim -> latent_dim -> hidden_dim -> n_features

    The narrow bottleneck forces the network to learn a compact representation
    rather than simply copying the input.
    """
    inputs = keras.Input(shape=(n_features,), name="cycle_features")

    # Encoder
    x = layers.Dense(hidden_dim, activation="relu", name="encoder_dense_1")(inputs)
    x = layers.Dropout(dropout, name="encoder_dropout")(x)
    latent = layers.Dense(latent_dim, activation="linear", name="latent_embedding")(x)

    # Decoder
    x = layers.Dense(hidden_dim, activation="relu", name="decoder_dense_1")(latent)
    reconstruction = layers.Dense(n_features, activation="linear", name="reconstruction")(x)

    model = keras.Model(
        inputs=inputs,
        outputs=[latent, reconstruction],
        name="battery_cycle_autoencoder",
    )

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss={"reconstruction": "mse"},
        loss_weights={"reconstruction": 1.0},
    )

    return model


autoencoder = build_autoencoder(n_features)
autoencoder.summary()


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

BATCH_SIZE = 128
EPOCHS = 100
PATIENCE = 10
MODEL_PATH = "cycle_autoencoder.keras"

# For an autoencoder, the target is the same standardized feature vector.
# Keras requires targets for every named output, even though the latent output
# is not directly supervised.
train_targets = {
    "latent_embedding": np.zeros((len(X_train), LATENT_DIM), dtype=np.float32),
    "reconstruction": X_train,
}

val_targets = {
    "latent_embedding": np.zeros((len(X_val), LATENT_DIM), dtype=np.float32),
    "reconstruction": X_val,
}

callbacks = [
    keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=PATIENCE,
        restore_best_weights=True,
        verbose=1,
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=max(1, PATIENCE // 2),
        min_lr=1e-5,
        verbose=1,
    ),
    keras.callbacks.ModelCheckpoint(
        filepath=MODEL_PATH,
        monitor="val_loss",
        save_best_only=True,
        verbose=0,
    ),
]

history = autoencoder.fit(
    x=X_train,
    y=train_targets,
    validation_data=(X_val, val_targets),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    shuffle=True,
    callbacks=callbacks,
    verbose=1,
)


# ---------------------------------------------------------------------------
# Training curves
# ---------------------------------------------------------------------------

plt.figure(figsize=(7, 4))
plt.plot(history.history["loss"], label="Training loss")
plt.plot(history.history["val_loss"], label="Validation loss")
plt.xlabel("Epoch")
plt.ylabel("Reconstruction MSE")
plt.title("Autoencoder reconstruction loss")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# ---------------------------------------------------------------------------
# Scoring: reconstruction error and latent embedding
# ---------------------------------------------------------------------------

def score_cycles(model, X, batch_size=256):
    """
    Computes reconstruction error and latent embeddings for each cycle.

    Parameters
    ----------
    model : keras.Model
    X : np.ndarray
        Standardized cycle-feature matrix.
    batch_size : int

    Returns
    -------
    errors : np.ndarray, shape (n_cycles,)
        Mean squared reconstruction error per cycle.
    latent : np.ndarray, shape (n_cycles, latent_dim)
        Latent representation per cycle.
    """
    errors = []
    latent_vectors = []

    for start in range(0, len(X), batch_size):
        x_batch = X[start:start + batch_size]
        x_tensor = tf.convert_to_tensor(x_batch, dtype=tf.float32)

        latent, reconstruction = model(x_tensor, training=False)

        squared_error = tf.square(x_tensor - reconstruction)
        per_cycle_error = tf.reduce_mean(squared_error, axis=1)

        errors.append(per_cycle_error.numpy())
        latent_vectors.append(latent.numpy())

    return np.concatenate(errors), np.concatenate(latent_vectors)


val_errors, val_latent = score_cycles(autoencoder, X_val)

print("\nReconstruction-error summary:")
print(f"mean: {val_errors.mean():.6f}")
print(f"median: {np.median(val_errors):.6f}")
print(f"90th percentile: {np.percentile(val_errors, 90):.6f}")
print(f"99th percentile: {np.percentile(val_errors, 99):.6f}")
print(f"Latent embedding shape: {val_latent.shape}")


# ---------------------------------------------------------------------------
# Attach scores back to the validation dataframe
# ---------------------------------------------------------------------------

# Important: preserve the original row order when attaching scores.
val = val.copy()
val["reconstruction_error"] = val_errors

# Optional: store the latent dimensions as separate columns.
for i in range(val_latent.shape[1]):
    val[f"latent_{i}"] = val_latent[:, i]


# Compare reconstruction error across degradation-status labels.
# This is evaluation only; degradation_status was never used during training.
error_by_status = (
    val.groupby("degradation_status")["reconstruction_error"]
    .agg(["mean", "median", "std", "count"])
    .sort_values("mean", ascending=False)
)

print("\nReconstruction error by degradation status:")
print(error_by_status)


# ---------------------------------------------------------------------------
# Inspect the most anomalous validation cycles
# ---------------------------------------------------------------------------

n_inspect = 20
most_anomalous_idx = np.argsort(val_errors)[::-1][:n_inspect]

print(f"\nTop {n_inspect} most anomalous validation cycles:")
print(
    val.iloc[most_anomalous_idx][
        [
            "battery_id",
            "cycle_index",
            "degradation_status",
            "reconstruction_error",
            "pack_temp_c",
            "depth_of_discharge_pct",
            "charge_c_rate",
            "discharge_c_rate",
            "internal_resistance_mOhm",
        ]
    ]
)


# ---------------------------------------------------------------------------
# Visualize reconstruction error by status
# ---------------------------------------------------------------------------

plt.figure(figsize=(8, 4))
statuses = sorted(val["degradation_status"].unique())

data_to_plot = [
    val.loc[val["degradation_status"] == status, "reconstruction_error"]
    for status in statuses
]

plt.boxplot(data_to_plot, labels=statuses, showfliers=False)
plt.ylabel("Reconstruction error")
plt.title("Reconstruction error by degradation status")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()