"""Generate sample customer churn data."""

import numpy as np
import pandas as pd
from pathlib import Path

def generate_customer_data(n_samples=10000, seed=42):
    """Generate synthetic customer churn data."""
    np.random.seed(seed)

    data = {
        "customer_id": [f"CUST{i:06d}" for i in range(n_samples)],
        "age": np.random.randint(18, 80, n_samples),
        "gender": np.random.choice(["Male", "Female"], n_samples),
        "tenure": np.random.randint(0, 72, n_samples),
        "monthly_charges": np.random.uniform(20, 150, n_samples),
        "total_charges": None,  # Will calculate
        "contract_type": np.random.choice(
            ["Month-to-month", "One year", "Two year"],
            n_samples,
            p=[0.5, 0.3, 0.2]
        ),
        "payment_method": np.random.choice(
            ["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
            n_samples
        ),
        "internet_service": np.random.choice(
            ["DSL", "Fiber optic", "No"],
            n_samples,
            p=[0.3, 0.5, 0.2]
        ),
        "online_security": np.random.choice(["Yes", "No"], n_samples),
        "tech_support": np.random.choice(["Yes", "No"], n_samples),
    }

    df = pd.DataFrame(data)

    # Calculate total charges
    df["total_charges"] = df["monthly_charges"] * df["tenure"]
    df.loc[df["tenure"] == 0, "total_charges"] = 0

    # Generate churn labels (based on realistic patterns)
    churn_prob = (
        0.1  # Base rate
        + (df["tenure"] < 12) * 0.3  # New customers more likely to churn
        + (df["contract_type"] == "Month-to-month") * 0.25
        + (df["monthly_charges"] > 80) * 0.15
        + (df["payment_method"] == "Electronic check") * 0.1
        - (df["online_security"] == "Yes") * 0.1
        - (df["tech_support"] == "Yes") * 0.1
    )

    churn_prob = np.clip(churn_prob, 0, 1)
    df["churn"] = (np.random.random(n_samples) < churn_prob).astype(int)

    return df

def main():
    """Generate and save sample data."""
    # Create data directory
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Generate training data
    print("Generating training data (10,000 samples)...")
    train_df = generate_customer_data(n_samples=10000, seed=42)
    train_df.to_csv(data_dir / "customer_churn_train.csv", index=False)
    print(f"Saved to {data_dir / 'customer_churn_train.csv'}")
    print(f"Churn rate: {train_df['churn'].mean():.2%}")

    # Generate test data
    print("\nGenerating test data (2,000 samples)...")
    test_df = generate_customer_data(n_samples=2000, seed=123)
    test_df.to_csv(data_dir / "customer_churn_test.csv", index=False)
    print(f"Saved to {data_dir / 'customer_churn_test.csv'}")
    print(f"Churn rate: {test_df['churn'].mean():.2%}")

    print("\nData generation complete!")

if __name__ == "__main__":
    main()
