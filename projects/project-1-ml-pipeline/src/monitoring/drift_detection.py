"""Data and model drift detection."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from evidently import ColumnMapping
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.report import Report
from scipy import stats

from src.utils.logger import get_logger
from src.utils.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class DriftDetector:
    """Detect data and model drift."""

    def __init__(
        self,
        reference_data: Optional[pd.DataFrame] = None,
        drift_threshold: float = 0.05,
    ):
        """Initialize drift detector.

        Args:
            reference_data: Reference dataset (training data)
            drift_threshold: P-value threshold for drift detection
        """
        self.reference_data = reference_data
        self.drift_threshold = drift_threshold
        self.drift_history: List[Dict[str, Any]] = []

        logger.info(f"Initialized DriftDetector (threshold={drift_threshold})")

    def detect_data_drift(
        self,
        current_data: pd.DataFrame,
        reference_data: Optional[pd.DataFrame] = None,
    ) -> Dict[str, Any]:
        """Detect data drift using statistical tests.

        Args:
            current_data: Current dataset
            reference_data: Reference dataset (defaults to stored reference)

        Returns:
            Dictionary with drift detection results
        """
        reference = reference_data if reference_data is not None else self.reference_data

        if reference is None:
            raise ValueError("Reference data not provided")

        logger.info(
            f"Detecting data drift: reference={len(reference)}, current={len(current_data)}"
        )

        drift_results = {
            "timestamp": datetime.now().isoformat(),
            "num_features": 0,
            "drifted_features": [],
            "drift_scores": {},
            "overall_drift": False,
        }

        # Get common numerical columns
        numerical_cols = reference.select_dtypes(include=[np.number]).columns
        common_cols = [col for col in numerical_cols if col in current_data.columns]

        drift_results["num_features"] = len(common_cols)

        # Test each feature for drift
        for col in common_cols:
            # Kolmogorov-Smirnov test
            ks_stat, ks_pvalue = stats.ks_2samp(
                reference[col].dropna(), current_data[col].dropna()
            )

            # Chi-square test for categorical (binned continuous)
            try:
                ref_hist, bins = np.histogram(reference[col].dropna(), bins=10)
                curr_hist, _ = np.histogram(current_data[col].dropna(), bins=bins)

                # Avoid division by zero
                ref_hist = ref_hist + 1
                curr_hist = curr_hist + 1

                chi2_stat, chi2_pvalue = stats.chisquare(curr_hist, ref_hist)
            except Exception:
                chi2_stat, chi2_pvalue = None, 1.0

            # Population Stability Index (PSI)
            psi_score = self._calculate_psi(
                reference[col].dropna(), current_data[col].dropna()
            )

            # Determine drift
            is_drifted = (
                ks_pvalue < self.drift_threshold or psi_score > 0.2
            )

            if is_drifted:
                drift_results["drifted_features"].append(col)

            drift_results["drift_scores"][col] = {
                "ks_statistic": float(ks_stat),
                "ks_pvalue": float(ks_pvalue),
                "chi2_statistic": float(chi2_stat) if chi2_stat else None,
                "chi2_pvalue": float(chi2_pvalue) if chi2_pvalue else None,
                "psi": float(psi_score),
                "is_drifted": is_drifted,
            }

        # Overall drift if > 20% of features drifted
        drift_results["overall_drift"] = (
            len(drift_results["drifted_features"]) / len(common_cols) > 0.2
        )

        # Log results
        logger.info(
            f"Data drift detection: {len(drift_results['drifted_features'])}/{len(common_cols)} "
            f"features drifted, overall_drift={drift_results['overall_drift']}"
        )

        # Track metrics
        metrics.record_drift_score(
            drift_type="data",
            score=len(drift_results["drifted_features"]) / len(common_cols),
        )

        self.drift_history.append(drift_results)

        return drift_results

    def _calculate_psi(
        self,
        reference: pd.Series,
        current: pd.Series,
        bins: int = 10,
    ) -> float:
        """Calculate Population Stability Index (PSI).

        Args:
            reference: Reference data series
            current: Current data series
            bins: Number of bins for discretization

        Returns:
            PSI score
        """
        try:
            # Create bins based on reference
            _, bin_edges = np.histogram(reference, bins=bins)

            # Calculate distributions
            ref_dist, _ = np.histogram(reference, bins=bin_edges)
            curr_dist, _ = np.histogram(current, bins=bin_edges)

            # Convert to percentages
            ref_pct = ref_dist / len(reference)
            curr_pct = curr_dist / len(current)

            # Avoid log(0)
            ref_pct = np.where(ref_pct == 0, 0.0001, ref_pct)
            curr_pct = np.where(curr_pct == 0, 0.0001, curr_pct)

            # Calculate PSI
            psi = np.sum((curr_pct - ref_pct) * np.log(curr_pct / ref_pct))

            return float(psi)

        except Exception as e:
            logger.warning(f"Failed to calculate PSI: {e}")
            return 0.0

    def detect_prediction_drift(
        self,
        reference_predictions: np.ndarray,
        current_predictions: np.ndarray,
    ) -> Dict[str, Any]:
        """Detect drift in model predictions.

        Args:
            reference_predictions: Reference predictions
            current_predictions: Current predictions

        Returns:
            Dictionary with prediction drift results
        """
        logger.info("Detecting prediction drift")

        # KS test on predictions
        ks_stat, ks_pvalue = stats.ks_2samp(reference_predictions, current_predictions)

        # PSI on predictions
        psi_score = self._calculate_psi(
            pd.Series(reference_predictions), pd.Series(current_predictions)
        )

        # Jensen-Shannon divergence
        js_divergence = self._calculate_js_divergence(
            reference_predictions, current_predictions
        )

        is_drifted = ks_pvalue < self.drift_threshold or psi_score > 0.2

        results = {
            "timestamp": datetime.now().isoformat(),
            "ks_statistic": float(ks_stat),
            "ks_pvalue": float(ks_pvalue),
            "psi": float(psi_score),
            "js_divergence": float(js_divergence),
            "is_drifted": is_drifted,
        }

        logger.info(f"Prediction drift: is_drifted={is_drifted}, psi={psi_score:.4f}")

        # Track metrics
        metrics.record_drift_score(drift_type="prediction", score=psi_score)

        return results

    def _calculate_js_divergence(
        self,
        reference: np.ndarray,
        current: np.ndarray,
        bins: int = 10,
    ) -> float:
        """Calculate Jensen-Shannon divergence.

        Args:
            reference: Reference data
            current: Current data
            bins: Number of bins for discretization

        Returns:
            JS divergence score
        """
        try:
            # Create distributions
            ref_hist, bin_edges = np.histogram(reference, bins=bins, density=True)
            curr_hist, _ = np.histogram(current, bins=bin_edges, density=True)

            # Normalize
            ref_dist = ref_hist / np.sum(ref_hist)
            curr_dist = curr_hist / np.sum(curr_hist)

            # Calculate JS divergence
            m = 0.5 * (ref_dist + curr_dist)
            js = 0.5 * stats.entropy(ref_dist, m) + 0.5 * stats.entropy(curr_dist, m)

            return float(js)

        except Exception as e:
            logger.warning(f"Failed to calculate JS divergence: {e}")
            return 0.0

    def generate_drift_report(
        self,
        current_data: pd.DataFrame,
        reference_data: Optional[pd.DataFrame] = None,
        output_path: Optional[str] = None,
    ) -> str:
        """Generate comprehensive drift report using Evidently.

        Args:
            current_data: Current dataset
            reference_data: Reference dataset
            output_path: Path to save HTML report

        Returns:
            Path to generated report
        """
        reference = reference_data if reference_data is not None else self.reference_data

        if reference is None:
            raise ValueError("Reference data not provided")

        logger.info("Generating drift report with Evidently")

        try:
            # Create column mapping
            column_mapping = ColumnMapping()

            # Create report
            report = Report(metrics=[DataDriftPreset(), DataQualityPreset()])

            report.run(
                reference_data=reference,
                current_data=current_data,
                column_mapping=column_mapping,
            )

            # Save report
            if output_path is None:
                output_path = f"reports/drift_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

            from pathlib import Path

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            report.save_html(output_path)

            logger.info(f"Drift report saved to {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"Failed to generate drift report: {e}")
            raise

    def get_drift_history(self) -> List[Dict[str, Any]]:
        """Get drift detection history.

        Returns:
            List of drift detection results
        """
        return self.drift_history

    def should_trigger_retraining(
        self,
        drift_results: Dict[str, Any],
        performance_degradation: Optional[float] = None,
    ) -> Tuple[bool, str]:
        """Determine if model retraining should be triggered.

        Args:
            drift_results: Drift detection results
            performance_degradation: Optional performance degradation metric

        Returns:
            Tuple of (should_retrain, reason)
        """
        reasons = []

        # Check data drift
        if drift_results.get("overall_drift", False):
            reasons.append(
                f"Data drift detected in {len(drift_results['drifted_features'])} features"
            )

        # Check performance degradation
        if performance_degradation is not None and performance_degradation > 0.1:
            reasons.append(
                f"Performance degraded by {performance_degradation:.2%}"
            )

        # Check prediction drift
        if drift_results.get("is_drifted", False):
            reasons.append(f"Prediction drift detected (PSI={drift_results.get('psi', 0):.4f})")

        should_retrain = len(reasons) > 0

        reason_str = "; ".join(reasons) if reasons else "No retraining needed"

        logger.info(f"Retraining trigger: {should_retrain} - {reason_str}")

        return should_retrain, reason_str

    def __repr__(self) -> str:
        """String representation."""
        return f"DriftDetector(threshold={self.drift_threshold}, history={len(self.drift_history)})"
