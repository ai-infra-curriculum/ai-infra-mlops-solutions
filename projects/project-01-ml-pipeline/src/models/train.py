"""Model training with hyperparameter optimization."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import lightgbm as lgb
import mlflow
import mlflow.sklearn
import numpy as np
import optuna
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from src.utils.config import get_config
from src.utils.logger import get_logger
from src.utils.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()
config = get_config()


class ModelTrainer:
    """Model trainer with hyperparameter optimization using Optuna."""

    def __init__(
        self,
        experiment_name: str = "customer_churn",
        tracking_uri: Optional[str] = None,
        random_state: int = 42,
    ):
        """Initialize model trainer.

        Args:
            experiment_name: MLflow experiment name
            tracking_uri: MLflow tracking URI
            random_state: Random seed for reproducibility
        """
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri or config.mlflow_tracking_uri
        self.random_state = random_state

        # Set up MLflow
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment(self.experiment_name)

        # Best models
        self.best_models: Dict[str, Any] = {}
        self.best_params: Dict[str, Dict] = {}
        self.best_scores: Dict[str, float] = {}

        logger.info(
            f"Initialized ModelTrainer (experiment='{experiment_name}', "
            f"tracking_uri='{self.tracking_uri}')"
        )

    def prepare_data(
        self,
        df: pd.DataFrame,
        target_column: str = "churn",
        test_size: float = 0.2,
        val_size: float = 0.1,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
        """Prepare train/val/test splits.

        Args:
            df: Input DataFrame
            target_column: Target column name
            test_size: Test set size
            val_size: Validation set size (from train set)

        Returns:
            Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        logger.info(f"Preparing data splits (test={test_size}, val={val_size})")

        # Separate features and target
        X = df.drop(columns=[target_column, "customer_id"], errors="ignore")
        y = df[target_column]

        # Convert target to binary if string
        if y.dtype == "object":
            y = (y == "Yes").astype(int)

        # Train/test split
        X_train_full, X_test, y_train_full, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state, stratify=y
        )

        # Train/val split
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_full,
            y_train_full,
            test_size=val_size,
            random_state=self.random_state,
            stratify=y_train_full,
        )

        logger.info(
            f"Data splits: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}"
        )

        return X_train, X_val, X_test, y_train, y_val, y_test

    def train_logistic_regression(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Any, Dict[str, float]]:
        """Train Logistic Regression model.

        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
            params: Model parameters

        Returns:
            Tuple of (model, metrics)
        """
        logger.info("Training Logistic Regression")

        params = params or {
            "C": 1.0,
            "max_iter": 1000,
            "solver": "lbfgs",
            "random_state": self.random_state,
        }

        with mlflow.start_run(run_name="logistic_regression"):
            # Train model
            model = LogisticRegression(**params)
            model.fit(X_train, y_train)

            # Evaluate
            metrics_dict = self._evaluate_model(model, X_val, y_val)

            # Log to MLflow
            mlflow.log_params(params)
            mlflow.log_metrics(metrics_dict)
            mlflow.sklearn.log_model(model, "model")

            logger.info(f"Logistic Regression - ROC AUC: {metrics_dict['roc_auc']:.4f}")

        return model, metrics_dict

    def train_random_forest(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Any, Dict[str, float]]:
        """Train Random Forest model.

        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
            params: Model parameters

        Returns:
            Tuple of (model, metrics)
        """
        logger.info("Training Random Forest")

        params = params or {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "random_state": self.random_state,
            "n_jobs": -1,
        }

        with mlflow.start_run(run_name="random_forest"):
            # Train model
            model = RandomForestClassifier(**params)
            model.fit(X_train, y_train)

            # Evaluate
            metrics_dict = self._evaluate_model(model, X_val, y_val)

            # Log to MLflow
            mlflow.log_params(params)
            mlflow.log_metrics(metrics_dict)
            mlflow.sklearn.log_model(model, "model")

            logger.info(f"Random Forest - ROC AUC: {metrics_dict['roc_auc']:.4f}")

        return model, metrics_dict

    def train_xgboost(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Any, Dict[str, float]]:
        """Train XGBoost model.

        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
            params: Model parameters

        Returns:
            Tuple of (model, metrics)
        """
        logger.info("Training XGBoost")

        params = params or {
            "n_estimators": 100,
            "max_depth": 6,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": self.random_state,
        }

        with mlflow.start_run(run_name="xgboost"):
            # Train model
            model = xgb.XGBClassifier(**params)
            model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

            # Evaluate
            metrics_dict = self._evaluate_model(model, X_val, y_val)

            # Log to MLflow
            mlflow.log_params(params)
            mlflow.log_metrics(metrics_dict)
            mlflow.xgboost.log_model(model, "model")

            logger.info(f"XGBoost - ROC AUC: {metrics_dict['roc_auc']:.4f}")

        return model, metrics_dict

    def train_lightgbm(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Any, Dict[str, float]]:
        """Train LightGBM model.

        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
            params: Model parameters

        Returns:
            Tuple of (model, metrics)
        """
        logger.info("Training LightGBM")

        params = params or {
            "n_estimators": 100,
            "max_depth": 6,
            "learning_rate": 0.1,
            "num_leaves": 31,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": self.random_state,
        }

        with mlflow.start_run(run_name="lightgbm"):
            # Train model
            model = lgb.LGBMClassifier(**params)
            model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

            # Evaluate
            metrics_dict = self._evaluate_model(model, X_val, y_val)

            # Log to MLflow
            mlflow.log_params(params)
            mlflow.log_metrics(metrics_dict)
            mlflow.lightgbm.log_model(model, "model")

            logger.info(f"LightGBM - ROC AUC: {metrics_dict['roc_auc']:.4f}")

        return model, metrics_dict

    def optimize_hyperparameters(
        self,
        model_type: str,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        n_trials: int = 100,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Optimize hyperparameters using Optuna.

        Args:
            model_type: Model type (logistic, random_forest, xgboost, lightgbm)
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
            n_trials: Number of optimization trials
            timeout: Optimization timeout in seconds

        Returns:
            Best parameters dictionary
        """
        logger.info(
            f"Optimizing hyperparameters for {model_type} (n_trials={n_trials})"
        )

        def objective(trial):
            if model_type == "logistic":
                params = {
                    "C": trial.suggest_float("C", 0.001, 10.0, log=True),
                    "max_iter": 1000,
                    "solver": trial.suggest_categorical("solver", ["lbfgs", "liblinear"]),
                    "random_state": self.random_state,
                }
                model = LogisticRegression(**params)

            elif model_type == "random_forest":
                params = {
                    "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                    "max_depth": trial.suggest_int("max_depth", 3, 20),
                    "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
                    "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
                    "random_state": self.random_state,
                    "n_jobs": -1,
                }
                model = RandomForestClassifier(**params)

            elif model_type == "xgboost":
                params = {
                    "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                    "max_depth": trial.suggest_int("max_depth", 3, 12),
                    "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
                    "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                    "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
                    "random_state": self.random_state,
                }
                model = xgb.XGBClassifier(**params)

            elif model_type == "lightgbm":
                params = {
                    "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                    "max_depth": trial.suggest_int("max_depth", 3, 12),
                    "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
                    "num_leaves": trial.suggest_int("num_leaves", 20, 100),
                    "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                    "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
                    "random_state": self.random_state,
                }
                model = lgb.LGBMClassifier(**params)

            else:
                raise ValueError(f"Unknown model type: {model_type}")

            # Train and evaluate
            model.fit(X_train, y_train)
            y_pred_proba = model.predict_proba(X_val)[:, 1]
            roc_auc = roc_auc_score(y_val, y_pred_proba)

            return roc_auc

        # Run optimization
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials, timeout=timeout, show_progress_bar=True)

        best_params = study.best_params
        best_score = study.best_value

        logger.info(
            f"Optimization complete - Best ROC AUC: {best_score:.4f}, "
            f"Best params: {best_params}"
        )

        self.best_params[model_type] = best_params
        self.best_scores[model_type] = best_score

        return best_params

    def train_all_models(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        optimize: bool = False,
        n_trials: int = 50,
    ) -> Dict[str, Tuple[Any, Dict[str, float]]]:
        """Train all models and return results.

        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
            optimize: Whether to optimize hyperparameters
            n_trials: Number of optimization trials

        Returns:
            Dictionary mapping model names to (model, metrics) tuples
        """
        logger.info(f"Training all models (optimize={optimize})")

        results = {}

        # Train Logistic Regression
        if optimize:
            params = self.optimize_hyperparameters(
                "logistic", X_train, y_train, X_val, y_val, n_trials
            )
        else:
            params = None
        model, metrics_dict = self.train_logistic_regression(
            X_train, y_train, X_val, y_val, params
        )
        results["logistic_regression"] = (model, metrics_dict)

        # Train Random Forest
        if optimize:
            params = self.optimize_hyperparameters(
                "random_forest", X_train, y_train, X_val, y_val, n_trials
            )
        else:
            params = None
        model, metrics_dict = self.train_random_forest(
            X_train, y_train, X_val, y_val, params
        )
        results["random_forest"] = (model, metrics_dict)

        # Train XGBoost
        if optimize:
            params = self.optimize_hyperparameters(
                "xgboost", X_train, y_train, X_val, y_val, n_trials
            )
        else:
            params = None
        model, metrics_dict = self.train_xgboost(X_train, y_train, X_val, y_val, params)
        results["xgboost"] = (model, metrics_dict)

        # Train LightGBM
        if optimize:
            params = self.optimize_hyperparameters(
                "lightgbm", X_train, y_train, X_val, y_val, n_trials
            )
        else:
            params = None
        model, metrics_dict = self.train_lightgbm(X_train, y_train, X_val, y_val, params)
        results["lightgbm"] = (model, metrics_dict)

        # Select best model
        best_model_name = max(results, key=lambda k: results[k][1]["roc_auc"])
        self.best_models["champion"] = results[best_model_name][0]

        logger.info(
            f"Best model: {best_model_name} with ROC AUC "
            f"{results[best_model_name][1]['roc_auc']:.4f}"
        )

        return results

    def _evaluate_model(
        self, model: Any, X_val: pd.DataFrame, y_val: pd.Series
    ) -> Dict[str, float]:
        """Evaluate model and return metrics.

        Args:
            model: Trained model
            X_val: Validation features
            y_val: Validation target

        Returns:
            Dictionary of metrics
        """
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1]

        metrics_dict = {
            "accuracy": accuracy_score(y_val, y_pred),
            "precision": precision_score(y_val, y_pred),
            "recall": recall_score(y_val, y_pred),
            "f1": f1_score(y_val, y_pred),
            "roc_auc": roc_auc_score(y_val, y_pred_proba),
        }

        return metrics_dict

    def evaluate_on_test_set(
        self,
        model: Any,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        model_name: str = "model",
    ) -> Dict[str, float]:
        """Evaluate model on test set and log to MLflow.

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test target
            model_name: Model name for logging

        Returns:
            Dictionary of test metrics
        """
        logger.info(f"Evaluating {model_name} on test set")

        with mlflow.start_run(run_name=f"{model_name}_test"):
            metrics_dict = self._evaluate_model(model, X_test, y_test)

            # Log test metrics
            test_metrics = {f"test_{k}": v for k, v in metrics_dict.items()}
            mlflow.log_metrics(test_metrics)

            logger.info(f"Test ROC AUC: {metrics_dict['roc_auc']:.4f}")

        return metrics_dict

    def __repr__(self) -> str:
        """String representation."""
        return f"ModelTrainer(experiment='{self.experiment_name}')"
