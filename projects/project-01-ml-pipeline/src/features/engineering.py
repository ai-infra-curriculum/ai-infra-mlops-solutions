"""Feature engineering pipeline with 50+ features."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

from src.utils.logger import get_logger
from src.utils.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class FeatureEngineer:
    """Feature engineering for customer churn prediction."""

    def __init__(self, save_encoders: bool = True):
        """Initialize feature engineer.

        Args:
            save_encoders: Whether to save label encoders for inference
        """
        self.save_encoders = save_encoders
        self.encoders: Dict[str, LabelEncoder] = {}
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = []

        logger.info("Initialized FeatureEngineer")

    def engineer_features(
        self,
        df: pd.DataFrame,
        fit: bool = True,
    ) -> pd.DataFrame:
        """Engineer all features from raw data.

        Args:
            df: Input DataFrame
            fit: Whether to fit encoders/scalers (True for training, False for inference)

        Returns:
            DataFrame with engineered features
        """
        start_time = datetime.now()
        logger.info(f"Engineering features for {len(df)} records (fit={fit})")

        df = df.copy()

        # 1. Basic features
        df = self._create_basic_features(df)

        # 2. Tenure-based features
        df = self._create_tenure_features(df)

        # 3. Charge-based features
        df = self._create_charge_features(df)

        # 4. Service features
        df = self._create_service_features(df)

        # 5. Contract & payment features
        df = self._create_contract_features(df)

        # 6. Interaction features
        df = self._create_interaction_features(df)

        # 7. Aggregate features
        df = self._create_aggregate_features(df)

        # 8. Encode categorical features
        df = self._encode_categorical_features(df, fit=fit)

        # 9. Scale numerical features
        df = self._scale_features(df, fit=fit)

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Feature engineering complete: {len(df.columns)} features in {duration:.2f}s"
        )

        if fit:
            self.feature_names = [col for col in df.columns if col not in ["customer_id", "churn"]]

        return df

    def _create_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create basic derived features (8 features)."""
        # Age groups
        df["age_group"] = pd.cut(
            df["age"],
            bins=[0, 25, 35, 45, 55, 65, 100],
            labels=["18-25", "26-35", "36-45", "46-55", "56-65", "65+"],
        )

        # Senior citizen flag
        df["is_senior"] = (df["age"] >= 65).astype(int)

        # Gender binary
        df["gender_binary"] = (df["gender"] == "Male").astype(int)

        # Has phone service
        df["has_phone"] = df.get("phone_service", "Yes").apply(
            lambda x: 1 if x == "Yes" else 0
        )

        # Has internet
        df["has_internet"] = (df["internet_service"] != "No").astype(int)

        # Multiple lines
        df["has_multiple_lines"] = df.get("multiple_lines", "No").apply(
            lambda x: 1 if x == "Yes" else 0
        )

        # Paperless billing
        df["paperless_billing"] = df.get("paperless_billing", "No").apply(
            lambda x: 1 if x == "Yes" else 0
        )

        # Partner & dependents
        df["has_partner"] = df.get("partner", "No").apply(lambda x: 1 if x == "Yes" else 0)
        df["has_dependents"] = df.get("dependents", "No").apply(
            lambda x: 1 if x == "Yes" else 0
        )

        return df

    def _create_tenure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create tenure-based features (6 features)."""
        # Tenure groups
        df["tenure_group"] = pd.cut(
            df["tenure"],
            bins=[-1, 12, 24, 36, 48, 60, 100],
            labels=["0-1yr", "1-2yr", "2-3yr", "3-4yr", "4-5yr", "5+yr"],
        )

        # New customer flag
        df["is_new_customer"] = (df["tenure"] <= 6).astype(int)

        # Long-term customer
        df["is_long_term"] = (df["tenure"] >= 36).astype(int)

        # Tenure in years
        df["tenure_years"] = df["tenure"] / 12

        # Tenure squared (non-linear relationship)
        df["tenure_squared"] = df["tenure"] ** 2

        # Tenure log (for skewed distribution)
        df["tenure_log"] = np.log1p(df["tenure"])

        return df

    def _create_charge_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create charge-based features (10 features)."""
        # Handle missing total_charges
        df["total_charges"] = df["total_charges"].fillna(df["monthly_charges"])

        # Monthly charges groups
        df["monthly_charges_group"] = pd.cut(
            df["monthly_charges"],
            bins=[0, 30, 60, 90, 120, 1000],
            labels=["0-30", "30-60", "60-90", "90-120", "120+"],
        )

        # High/low charges
        df["is_high_charges"] = (df["monthly_charges"] > df["monthly_charges"].median()).astype(
            int
        )

        # Charge per tenure month
        df["charge_per_tenure"] = df["total_charges"] / (df["tenure"] + 1)

        # Average monthly charge (from total)
        df["avg_monthly_charge"] = df["total_charges"] / (df["tenure"] + 1)

        # Charge increase rate
        df["charge_increase_rate"] = (
            df["monthly_charges"] - df["avg_monthly_charge"]
        ) / (df["avg_monthly_charge"] + 1)

        # Total charges log
        df["total_charges_log"] = np.log1p(df["total_charges"])

        # Monthly charges log
        df["monthly_charges_log"] = np.log1p(df["monthly_charges"])

        # Charge ratio
        df["monthly_to_total_ratio"] = df["monthly_charges"] / (df["total_charges"] + 1)

        # Charge volatility
        df["charge_volatility"] = abs(df["monthly_charges"] - df["avg_monthly_charge"])

        return df

    def _create_service_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create service-based features (12 features)."""
        # Service columns
        service_cols = [
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies",
        ]

        # Count total services
        service_count = 0
        for col in service_cols:
            if col in df.columns:
                df[f"has_{col}"] = df[col].apply(lambda x: 1 if x == "Yes" else 0)
                service_count += df[f"has_{col}"]

        df["total_services"] = service_count

        # No services flag
        df["has_no_services"] = (df["total_services"] == 0).astype(int)

        # Premium services (security + backup)
        df["has_premium_services"] = (
            (df.get("has_online_security", 0) == 1) & (df.get("has_online_backup", 0) == 1)
        ).astype(int)

        # Streaming services
        df["has_streaming"] = (
            (df.get("has_streaming_tv", 0) == 1) | (df.get("has_streaming_movies", 0) == 1)
        ).astype(int)

        # Protection services
        df["has_protection"] = (
            (df.get("has_device_protection", 0) == 1) | (df.get("has_online_security", 0) == 1)
        ).astype(int)

        # Service to charge ratio
        df["services_per_dollar"] = df["total_services"] / (df["monthly_charges"] + 1)

        # Internet service type
        df["is_fiber"] = (df["internet_service"] == "Fiber optic").astype(int)
        df["is_dsl"] = (df["internet_service"] == "DSL").astype(int)

        return df

    def _create_contract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create contract and payment features (8 features)."""
        # Contract type flags
        df["is_month_to_month"] = (df["contract_type"] == "Month-to-month").astype(int)
        df["is_one_year"] = (df["contract_type"] == "One year").astype(int)
        df["is_two_year"] = (df["contract_type"] == "Two year").astype(int)

        # Contract stability score
        contract_score = {"Month-to-month": 0, "One year": 1, "Two year": 2}
        df["contract_stability"] = df["contract_type"].map(contract_score)

        # Payment method flags
        df["is_electronic_check"] = (df["payment_method"] == "Electronic check").astype(int)
        df["is_auto_payment"] = (
            df["payment_method"].isin(["Bank transfer", "Credit card"])
        ).astype(int)

        # Risk score (month-to-month + electronic check)
        df["high_risk_profile"] = (
            (df["is_month_to_month"] == 1) & (df["is_electronic_check"] == 1)
        ).astype(int)

        # Loyalty indicator (long tenure + long contract)
        df["loyalty_score"] = df["contract_stability"] * (df["tenure"] / 12)

        return df

    def _create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features (10 features)."""
        # Tenure × charges
        df["tenure_x_monthly"] = df["tenure"] * df["monthly_charges"]
        df["tenure_x_total"] = df["tenure"] * df["total_charges"]

        # Age × tenure
        df["age_x_tenure"] = df["age"] * df["tenure"]

        # Services × charges
        df["services_x_charges"] = df["total_services"] * df["monthly_charges"]

        # Contract × tenure
        df["contract_x_tenure"] = df["contract_stability"] * df["tenure"]

        # Family size (partner + dependents)
        df["family_size"] = df["has_partner"] + df["has_dependents"]

        # Family × charges
        df["family_x_charges"] = df["family_size"] * df["monthly_charges"]

        # Internet × services
        df["internet_x_services"] = df["has_internet"] * df["total_services"]

        # Senior × charges
        df["senior_x_charges"] = df["is_senior"] * df["monthly_charges"]

        # Risk × charges
        df["risk_x_charges"] = df["high_risk_profile"] * df["monthly_charges"]

        return df

    def _create_aggregate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create aggregate/statistical features (6 features)."""
        # Revenue potential
        df["revenue_potential"] = df["monthly_charges"] * (100 - df["tenure"])

        # Customer lifetime value estimate
        df["estimated_clv"] = df["total_charges"] + (df["monthly_charges"] * 12)

        # Value per service
        df["value_per_service"] = df["total_charges"] / (df["total_services"] + 1)

        # Engagement score
        df["engagement_score"] = (
            df["total_services"] * 0.3
            + df["tenure"] * 0.3
            + df["has_auto_payment"] * 0.2
            + df["contract_stability"] * 0.2
        )

        # Risk score (composite)
        df["churn_risk_score"] = (
            df["is_month_to_month"] * 0.3
            + df["is_electronic_check"] * 0.2
            + (df["tenure"] < 12).astype(int) * 0.3
            + (df["monthly_charges"] > 80).astype(int) * 0.2
        )

        # Satisfaction proxy (more services + longer tenure = higher satisfaction)
        df["satisfaction_proxy"] = (
            (df["total_services"] / 6) * 0.4 + (df["tenure"] / 72) * 0.6
        )

        return df

    def _encode_categorical_features(
        self, df: pd.DataFrame, fit: bool = True
    ) -> pd.DataFrame:
        """Encode categorical features."""
        categorical_cols = [
            "age_group",
            "tenure_group",
            "monthly_charges_group",
            "contract_type",
            "payment_method",
            "internet_service",
        ]

        for col in categorical_cols:
            if col not in df.columns:
                continue

            if fit:
                self.encoders[col] = LabelEncoder()
                df[f"{col}_encoded"] = self.encoders[col].fit_transform(df[col].astype(str))
            else:
                if col in self.encoders:
                    # Handle unseen categories
                    known_categories = set(self.encoders[col].classes_)
                    df[col] = df[col].apply(
                        lambda x: x if x in known_categories else self.encoders[col].classes_[0]
                    )
                    df[f"{col}_encoded"] = self.encoders[col].transform(df[col].astype(str))

        # Drop original categorical columns
        df = df.drop(columns=categorical_cols, errors="ignore")

        return df

    def _scale_features(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Scale numerical features."""
        # Select numerical columns (exclude IDs, target, and already encoded)
        exclude_cols = ["customer_id", "churn"]
        numerical_cols = [
            col
            for col in df.select_dtypes(include=[np.number]).columns
            if col not in exclude_cols
        ]

        if fit:
            self.scaler = StandardScaler()
            df[numerical_cols] = self.scaler.fit_transform(df[numerical_cols])
        else:
            if self.scaler:
                df[numerical_cols] = self.scaler.transform(df[numerical_cols])

        return df

    def get_feature_names(self) -> List[str]:
        """Get list of engineered feature names.

        Returns:
            List of feature names
        """
        return self.feature_names

    def get_feature_importance_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze feature statistics.

        Args:
            df: DataFrame with engineered features

        Returns:
            DataFrame with feature statistics
        """
        stats = []

        for col in self.feature_names:
            if col in df.columns:
                col_stats = {
                    "feature": col,
                    "mean": df[col].mean(),
                    "std": df[col].std(),
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "missing_pct": (df[col].isna().sum() / len(df)) * 100,
                }
                stats.append(col_stats)

        return pd.DataFrame(stats)

    def save_artifacts(self, output_dir: str) -> None:
        """Save encoders and scalers to disk.

        Args:
            output_dir: Output directory path
        """
        import pickle
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save encoders
        if self.encoders:
            with open(output_path / "label_encoders.pkl", "wb") as f:
                pickle.dump(self.encoders, f)
            logger.info(f"Saved {len(self.encoders)} label encoders")

        # Save scaler
        if self.scaler:
            with open(output_path / "scaler.pkl", "wb") as f:
                pickle.dump(self.scaler, f)
            logger.info("Saved feature scaler")

        # Save feature names
        if self.feature_names:
            with open(output_path / "feature_names.txt", "w") as f:
                f.write("\n".join(self.feature_names))
            logger.info(f"Saved {len(self.feature_names)} feature names")

    def load_artifacts(self, input_dir: str) -> None:
        """Load encoders and scalers from disk.

        Args:
            input_dir: Input directory path
        """
        import pickle
        from pathlib import Path

        input_path = Path(input_dir)

        # Load encoders
        encoders_file = input_path / "label_encoders.pkl"
        if encoders_file.exists():
            with open(encoders_file, "rb") as f:
                self.encoders = pickle.load(f)
            logger.info(f"Loaded {len(self.encoders)} label encoders")

        # Load scaler
        scaler_file = input_path / "scaler.pkl"
        if scaler_file.exists():
            with open(scaler_file, "rb") as f:
                self.scaler = pickle.load(f)
            logger.info("Loaded feature scaler")

        # Load feature names
        feature_names_file = input_path / "feature_names.txt"
        if feature_names_file.exists():
            with open(feature_names_file, "r") as f:
                self.feature_names = [line.strip() for line in f]
            logger.info(f"Loaded {len(self.feature_names)} feature names")

    def __repr__(self) -> str:
        """String representation."""
        return f"FeatureEngineer(features={len(self.feature_names)}, encoders={len(self.encoders)})"
