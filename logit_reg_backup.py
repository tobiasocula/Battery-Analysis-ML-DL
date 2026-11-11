    

def run_for_features(use_features, label):

    print('--- RUNNING FOR LABEL', label, '---')

    preprocess = Pipeline([
        ("scaler", StandardScaler()),
        ("variance", VarianceThreshold(threshold=0.0))
    ])

    optimize_metric = "ARI" # ARI, NMI, accuracy, macro_F1

    alpha_values = [1, 2, 3, 0.5, 0.25]

    X_train = preprocess.fit_transform(train[use_features])
    X_val = preprocess.transform(val[use_features])
    y_train = train["degradation_status"].to_numpy()
    y_val = val["degradation_status"].to_numpy()

    alpha_idx_mapping = {alpha_values[i]:i for i in range(len(alpha_values))}

    metrics_df = []

    val_pred_structs = np.empty((2, len(alpha_values)), dtype=object)

    for i,alpha in enumerate(alpha_values):

        metrics_L2, predicted_L2 = perform_logistic_regression(X_train, X_val, y_train, y_val, "l2", alpha)
        metrics_L1, predicted_L1 = perform_logistic_regression(X_train, X_val, y_train, y_val, "l1", alpha)
        metrics_L1["penalty"] = "l1"
        metrics_L2["penalty"] = "l2"
        metrics_df.append(metrics_L1)
        metrics_df.append(metrics_L2)
        val_pred_structs[0, i] = predicted_L1
        val_pred_structs[1, i] = predicted_L2

    metrics_df = pd.DataFrame(metrics_df).sort_values(optimize_metric, ascending=False)
    print('metrics df:', metrics_df)

    best_alpha = metrics_df["alpha"].values[0]
    best_L1_L2_idx = 0 if metrics_df["penalty"].values[0] == "l1" else 1

    val_predictions_best = val_pred_structs[best_L1_L2_idx, alpha_idx_mapping[best_alpha]]

    confusion_df = pd.DataFrame(
        confusion_matrix(
            val_predictions_best,
            y_val,
            labels=class_names
        ),
        index=[f"Actual {label}" for label in class_names],
        columns=[f"Predicted {label}" for label in class_names]
        )

    print("\nValidation confusion matrix:")
    print(confusion_df)

    print("\nValidation classification report:")
    print(classification_report(
        y_val,
        val_predictions_best,
        labels=class_names,
        zero_division=0
    ))

for label, feature in zip(labels, features):
    run_for_features(feature, label_names)