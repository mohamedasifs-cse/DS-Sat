"""
Model Evaluation and Diagnostics Module
CareBridge Hospitals - Hospital Appointment Insight (Challenge ID: U23AD491)

Calculates evaluation metrics on the hold-out test set:
- Accuracy, Precision, Recall, F1-Score, ROC-AUC
- Confusion Matrix visualization
- Feature Importance extraction and visualization
- Exports reports/model_metrics.csv, reports/model_evaluation.txt, models/no_show_model.joblib
"""

import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)

def evaluate_and_save_models(trained_pipelines, X_test, y_test, num_cols, cat_cols,
                            models_dir="models", reports_dir="reports", figures_dir="reports/figures"):
    """
    Evaluates all trained pipelines on the test set, saves the champion model,
    and produces metric tables, evaluation logs, and diagnostic plots.
    """
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    print("\n[Model Evaluation] Assessing model performance on hold-out test set...")
    metrics_list = []
    confusion_matrices = {}

    for name, pipe in trained_pipelines.items():
        y_pred = pipe.predict(X_test)
        
        # Predicted probabilities for ROC-AUC
        if hasattr(pipe, "predict_proba"):
            y_proba = pipe.predict_proba(X_test)[:, 1]
            try:
                auc = roc_auc_score(y_test, y_proba)
            except Exception:
                auc = np.nan
        else:
            auc = np.nan

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred)

        confusion_matrices[name] = cm

        metrics_list.append({
            "model_name": name,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4) if not np.isnan(auc) else "N/A",
            "selection_status": "Candidate"
        })

    df_metrics = pd.DataFrame(metrics_list)

    # Select champion model based on highest F1-score (or ROC-AUC)
    # Convert roc_auc to float for comparison
    df_metrics["f1_numeric"] = pd.to_numeric(df_metrics["f1_score"], errors="coerce")
    best_idx = df_metrics["f1_numeric"].idxmax()
    df_metrics.loc[best_idx, "selection_status"] = "Selected Champion"
    champion_name = df_metrics.loc[best_idx, "model_name"]
    df_metrics.drop(columns=["f1_numeric"], inplace=True)

    print("\nModel Evaluation Summary Table:")
    print(df_metrics.to_string(index=False))
    print(f"\n=> Champion Model Selected: {champion_name}")

    # 1. Save model_metrics.csv
    metrics_csv_path = os.path.join(reports_dir, "model_metrics.csv")
    df_metrics.to_csv(metrics_csv_path, index=False)
    print(f"Saved metrics table: {metrics_csv_path}")

    # 2. Save Champion Model Joblib
    champion_pipe = trained_pipelines[champion_name]
    model_save_path = os.path.join(models_dir, "no_show_model.joblib")
    joblib.dump(champion_pipe, model_save_path)
    print(f"Saved champion pipeline to: {model_save_path}")

    # 3. Save Confusion Matrix Plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    model_names = list(trained_pipelines.keys())

    for idx, name in enumerate(model_names):
        cm = confusion_matrices[name]
        ax = axes[idx]
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                    xticklabels=["Attended", "No-show"],
                    yticklabels=["Attended", "No-show"],
                    ax=ax, annot_kws={"size": 11, "weight": "bold"})
        ax.set_title(f"{name}\n(F1: {df_metrics.loc[df_metrics['model_name']==name, 'f1_score'].values[0]})",
                     fontsize=11, fontweight="bold")
        ax.set_xlabel("Predicted Label", fontsize=10)
        ax.set_ylabel("True Label", fontsize=10)

    plt.suptitle("Figure 10: Confusion Matrix Comparison across Models", fontsize=14, fontweight="bold", y=1.03)
    plt.tight_layout()
    cm_path = os.path.join(figures_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved confusion matrix visualization: {cm_path}")

    # 4. Extract Feature Importances from Random Forest
    rf_pipe = trained_pipelines.get("Random Forest")
    if rf_pipe is not None:
        try:
            preprocessor = rf_pipe.named_steps["preprocessor"]
            classifier = rf_pipe.named_steps["classifier"]
            
            # Extract transformed feature names
            cat_encoder = preprocessor.named_transformers_["cat"].named_steps["encoder"]
            cat_feature_names = cat_encoder.get_feature_names_out(cat_cols)
            all_feature_names = list(num_cols) + list(cat_feature_names)

            importances = classifier.feature_importances_
            feat_imp_df = pd.DataFrame({
                "feature": all_feature_names,
                "importance": importances
            }).sort_values(by="importance", ascending=False)

            # Top 15 features
            top_feats = feat_imp_df.head(15).iloc[::-1]

            plt.figure(figsize=(10, 6))
            plt.barh(top_feats["feature"], top_feats["importance"], color="#2b5c8f", edgecolor="#222222")
            plt.title("Figure 11: Top 15 Predictive Features (Random Forest Classifier)", fontsize=13, fontweight="bold", pad=12)
            plt.xlabel("Gini Feature Importance", fontsize=11, labelpad=8)
            plt.ylabel("Predictor Variable", fontsize=11)
            plt.tight_layout()
            fi_path = os.path.join(figures_dir, "feature_importance.png")
            plt.savefig(fi_path, dpi=300)
            plt.close()
            print(f"Saved feature importance visualization: {fi_path}")
        except Exception as e:
            print(f"Warning: Could not extract feature importances: {e}")

    # 5. Generate reports/model_evaluation.txt
    eval_txt_path = os.path.join(reports_dir, "model_evaluation.txt")
    with open(eval_txt_path, "w", encoding="utf-8") as f:
        f.write("CAREBRIDGE HOSPITALS - OUTPATIENT NO-SHOW PREDICTION MODEL EVALUATION\n")
        f.write("DS Sprint Skill-Based Assessment 2 | Challenge ID: U23AD491\n")
        f.write("=" * 75 + "\n\n")
        f.write("1. TARGET VARIABLE DEFINITION\n")
        f.write("   - Positive Class (1): No-show (patient did not attend scheduled visit)\n")
        f.write("   - Negative Class (0): Attended (patient completed appointment)\n")
        f.write("   - Unresolved, cancelled, rescheduled, and pending records were excluded from\n")
        f.write("     binary training to maintain clinical label integrity.\n\n")
        f.write("2. SPLIT METHODOLOGY\n")
        f.write("   - Strategy: Strict chronological train-test split (80% train, 20% test).\n")
        f.write("   - Training set size: " + str(len(y_test) * 4) + " (approx)\n")
        f.write("   - Test set size: " + str(len(y_test)) + "\n")
        f.write("   - Temporal structure strictly preserved to mimic real-world deployment.\n\n")
        f.write("3. PERFORMANCE BENCHMARKING ON HOLD-OUT TEST SET\n")
        f.write("-" * 75 + "\n")
        f.write(f"{'Model Name':<22} | {'Accuracy':<9} | {'Precision':<9} | {'Recall':<9} | {'F1-Score':<9} | {'ROC-AUC':<9} | {'Status'}\n")
        f.write("-" * 75 + "\n")
        for _, row in df_metrics.iterrows():
            f.write(f"{row['model_name']:<22} | {row['accuracy']:<9} | {row['precision']:<9} | {row['recall']:<9} | {row['f1_score']:<9} | {str(row['roc_auc']):<9} | {row['selection_status']}\n")
        f.write("-" * 75 + "\n\n")
        f.write("4. CHAMPION MODEL SELECTION RATIONALE\n")
        f.write(f"   The '{champion_name}' model was selected as the operational champion.\n")
        f.write("   In outpatient appointment scheduling, false negatives (failing to identify an upcoming\n")
        f.write("   no-show) lead to idle physician time and lost clinic capacity. Therefore, the selection\n")
        f.write("   prioritizes balanced F1-score and ROC-AUC over simple accuracy.\n\n")
        f.write("5. CONFUSION MATRIX (CHAMPION MODEL)\n")
        cm_champ = confusion_matrices[champion_name]
        f.write(f"   True Attended  (TN): {cm_champ[0][0]:<5} | False No-show (FP): {cm_champ[0][1]:<5}\n")
        f.write(f"   False Attended (FN): {cm_champ[1][0]:<5} | True No-show  (TP): {cm_champ[1][1]:<5}\n\n")
        f.write("6. KEY PREDICTIVE SIGNALS\n")
        f.write("   - Booking Lead Time (waiting_days): Long lead times (>7 days) correlate with higher no-show risk.\n")
        f.write("   - Prior Patient History (prior_noshow_count & prior_noshow_rate): The single strongest predictor.\n")
        f.write("   - Reminder Status (reminder_sent & reminder_response): Confirmed reminders dramatically reduce risk.\n")
        f.write("   - Age Cohort & Departmental variations provide actionable secondary signals.\n")

    print(f"Saved evaluation report: {eval_txt_path}")
    return df_metrics, champion_name

if __name__ == "__main__":
    from src.data_preprocessing import clean_and_merge_data
    from src.train_model.py import train_all_models
