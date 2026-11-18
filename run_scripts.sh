#!/usr/bin/env bash
set -euo pipefail

notebooks=(
    "knn.ipynb"
    "logistic_regression.ipynb"
    "decision_trees.ipynb"
    "unsupervised_DL.ipynb"
    teacher-student_DL.ipynb
)

for notebook in "${notebooks[@]}"; do
    echo "Running: $notebook"
    jupyter nbconvert \
        --to notebook \
        --execute \
        --inplace \
        "$notebook"
done

echo "All notebooks completed."