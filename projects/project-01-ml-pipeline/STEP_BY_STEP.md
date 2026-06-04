# Step-by-Step Implementation Guide

## Project: End-to-End ML Pipeline for Customer Churn Prediction

This guide walks through the complete implementation of a production-grade MLOps pipeline from scratch.

---

## Phase 1: Environment Setup (30 minutes)

### 1.1 Clone and Navigate to Project
```bash
cd project-1-ml-pipeline
```

### 1.2 Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.3 Install Dependencies
```bash
make install
# Or manually:
pip install -r requirements.txt
pip install -e .
```

### 1.4 Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `REDIS_HOST`, `REDIS_PORT`
- `MLFLOW_TRACKING_URI`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (if using S3)

### 1.5 Start Infrastructure with Docker
```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- MLflow (port 5000)
- Prometheus (port 9090)
- Grafana (port 3000)

Verify services:
```bash
docker-compose ps
```

---

## Phase 2: Data Generation and Ingestion (1 hour)

### 2.1 Generate Sample Data
```bash
python scripts/generate_sample_data.py
```

This creates:
- `data/raw/customer_churn_train.csv` (10,000 samples)
- `data/raw/customer_churn_test.csv` (2,000 samples)

### 2.2 Test Data Connectors

**CSV Connector:**
```python
from src.data import CSVConnector

connector = CSVConnector(
    name="customer_data",
    file_path="data/raw/customer_churn_train.csv"
)

connector.connect()
df = connector.read()
print(f"Loaded {len(df)} records")
connector.disconnect()
```

**Database Connector:**
```python
from src.data import DatabaseConnector

connector = DatabaseConnector(
    name="postgres_db",
    database_url="postgresql://mlops:mlops_password@localhost:5432/mlops_db"
)

connector.connect()
# Write data to database
connector.write(df, table_name="customer_churn", if_exists="replace")
# Read back
df_db = connector.read_table("customer_churn", limit=100)
connector.disconnect()
```

### 2.3 Use Data Ingestion Pipeline

```python
from src.data import DataIngestionPipeline

# Create pipeline
pipeline = DataIngestionPipeline(pipeline_name="churn_ingestion")

# Register CSV connector
pipeline.register_csv_connector(
    name="csv_source",
    file_path="data/raw/customer_churn_train.csv"
)

# Ingest data
df = pipeline.ingest("csv_source")
print(f"Ingested {len(df)} records")

# Save to database
pipeline.register_database_connector(
    name="postgres_sink",
    database_url="postgresql://mlops:mlops_password@localhost:5432/mlops_db"
)
pipeline.save_to_database(df, "postgres_sink", "customer_churn_raw")

# Save to parquet
pipeline.save_to_file(df, "data/processed/customer_churn.parquet", "parquet")
```

---

## Phase 3: Data Validation (30 minutes)

### 3.1 Create Expectation Suite

```python
from src.data.validation import DataValidator

# Initialize validator
validator = DataValidator(
    context_root_dir="data/great_expectations",
    use_in_memory=False
)

# Create customer churn expectation suite (20+ rules)
validator.create_customer_churn_suite(suite_name="customer_churn_suite")
```

### 3.2 Validate Data

```python
# Validate training data
validation_results = validator.validate(
    df=df,
    suite_name="customer_churn_suite",
    batch_id="train_batch_001"
)

print(f"Validation success: {validation_results['success']}")
print(f"Success rate: {validation_results['statistics']['success_percent']:.1f}%")

# Export report
validator.export_validation_report(
    validation_results,
    "reports/validation_report.html",
    format="html"
)
```

### 3.3 Handle Validation Failures

```python
if not validation_results['success']:
    print("Failed expectations:")
    for result in validation_results['results']:
        if not result['success']:
            print(f"  - {result['expectation_type']}")
```

---

## Phase 4: Feature Engineering (1 hour)

### 4.1 Engineer Features (50+ features)

```python
from src.features.engineering import FeatureEngineer

# Initialize feature engineer
engineer = FeatureEngineer(save_encoders=True)

# Engineer features (fit mode for training)
df_features = engineer.engineer_features(df, fit=True)

print(f"Original features: {len(df.columns)}")
print(f"Engineered features: {len(df_features.columns)}")
print(f"Feature names: {engineer.get_feature_names()}")

# Save artifacts for inference
engineer.save_artifacts("models/artifacts")
```

### 4.2 Feature Categories Created

The feature engineer creates 50+ features across categories:
1. **Basic features** (8): Age groups, senior flag, gender binary, service flags
2. **Tenure features** (6): Tenure groups, new customer flag, tenure transformations
3. **Charge features** (10): Charge groups, ratios, volatility, transformations
4. **Service features** (12): Service counts, premium/streaming flags, service efficiency
5. **Contract features** (8): Contract type flags, stability scores, risk profiles
6. **Interaction features** (10): Cross-feature products (tenure×charges, age×tenure, etc.)
7. **Aggregate features** (6): Revenue potential, CLV, engagement scores

### 4.3 Store Features in Feature Store

```python
from src.features.store import FeatureStore

# Initialize feature store
store = FeatureStore(schema="feature_store")

# Create feature set
feature_set_id = store.create_feature_set(
    feature_set_name="customer_churn_features",
    features=engineer.get_feature_names(),
    version=1,
    description="Customer churn prediction features v1",
    entity_type="customer"
)

# Write features
store.write_features(
    feature_set_id=feature_set_id,
    df=df_features,
    entity_id_column="customer_id"
)

# Read features
df_retrieved = store.read_features(
    feature_set_id=feature_set_id,
    entity_ids=["CUST000001", "CUST000002"]
)
```

---

## Phase 5: Model Training (2 hours)

### 5.1 Prepare Data Splits

```python
from src.models.train import ModelTrainer

# Initialize trainer
trainer = ModelTrainer(
    experiment_name="customer_churn",
    tracking_uri="http://localhost:5000"
)

# Prepare train/val/test splits
X_train, X_val, X_test, y_train, y_val, y_test = trainer.prepare_data(
    df=df_features,
    target_column="churn",
    test_size=0.2,
    val_size=0.1
)
```

### 5.2 Train Individual Models

```python
# Logistic Regression
model_lr, metrics_lr = trainer.train_logistic_regression(
    X_train, y_train, X_val, y_val
)

# Random Forest
model_rf, metrics_rf = trainer.train_random_forest(
    X_train, y_train, X_val, y_val
)

# XGBoost
model_xgb, metrics_xgb = trainer.train_xgboost(
    X_train, y_train, X_val, y_val
)

# LightGBM
model_lgb, metrics_lgb = trainer.train_lightgbm(
    X_train, y_train, X_val, y_val
)
```

### 5.3 Hyperparameter Optimization with Optuna

```python
# Optimize XGBoost
best_params = trainer.optimize_hyperparameters(
    model_type="xgboost",
    X_train=X_train,
    y_train=y_train,
    X_val=X_val,
    y_val=y_val,
    n_trials=100
)

# Train with optimized parameters
model_xgb_opt, metrics_xgb_opt = trainer.train_xgboost(
    X_train, y_train, X_val, y_val, params=best_params
)
```

### 5.4 Train All Models with Optimization

```python
# Train all 4 models with optimization
results = trainer.train_all_models(
    X_train, y_train, X_val, y_val,
    optimize=True,
    n_trials=50
)

# Best model is automatically selected
champion_model = trainer.best_models["champion"]

# Evaluate on test set
test_metrics = trainer.evaluate_on_test_set(
    champion_model, X_test, y_test, model_name="champion"
)

print(f"Test ROC AUC: {test_metrics['roc_auc']:.4f}")
```

### 5.5 View MLflow Experiments

```bash
# Open MLflow UI
open http://localhost:5000
```

Navigate to "customer_churn" experiment to see all runs, metrics, and models.

---

## Phase 6: Model Serving (1 hour)

### 6.1 Save Champion Model

```python
import pickle

# Save model
with open("models/champion_model.pkl", "wb") as f:
    pickle.dump(champion_model, f)

# Save feature engineer artifacts (already done in Phase 4)
```

### 6.2 Start API Server

```bash
# Start locally
python -m src.api.server

# Or with docker-compose (already running)
docker-compose up -d api
```

### 6.3 Test API Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Single Prediction:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST001",
    "age": 45,
    "gender": "Male",
    "tenure": 24,
    "monthly_charges": 75.50,
    "total_charges": 1812.00,
    "contract_type": "One year",
    "payment_method": "Credit card",
    "internet_service": "Fiber optic",
    "online_security": "Yes",
    "tech_support": "Yes"
  }'
```

**Batch Prediction:**
```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "customers": [
      {"customer_id": "CUST001", "age": 45, ...},
      {"customer_id": "CUST002", "age": 32, ...}
    ]
  }'
```

**Model Info:**
```bash
curl http://localhost:8000/model/info
```

### 6.4 Test with Python Client

```python
import requests

# Single prediction
response = requests.post(
    "http://localhost:8000/predict",
    json={
        "customer_id": "CUST001",
        "age": 45,
        "gender": "Male",
        "tenure": 24,
        "monthly_charges": 75.50,
        "total_charges": 1812.00,
        "contract_type": "One year",
        "payment_method": "Credit card",
        "internet_service": "Fiber optic",
        "online_security": "Yes",
        "tech_support": "Yes"
    }
)

result = response.json()
print(f"Churn probability: {result['churn_probability']:.2%}")
print(f"Risk level: {result['risk_level']}")
```

---

## Phase 7: Monitoring and Drift Detection (1 hour)

### 7.1 Detect Data Drift

```python
from src.monitoring.drift_detection import DriftDetector

# Initialize detector with reference data
detector = DriftDetector(
    reference_data=df_features,
    drift_threshold=0.05
)

# Simulate new data (with some drift)
df_current = df_features.sample(n=1000, replace=True)
df_current["monthly_charges"] = df_current["monthly_charges"] * 1.2  # Simulate drift

# Detect drift
drift_results = detector.detect_data_drift(
    current_data=df_current,
    reference_data=df_features
)

print(f"Overall drift: {drift_results['overall_drift']}")
print(f"Drifted features ({len(drift_results['drifted_features'])}):")
for feature in drift_results['drifted_features']:
    scores = drift_results['drift_scores'][feature]
    print(f"  - {feature}: PSI={scores['psi']:.4f}, p-value={scores['ks_pvalue']:.4f}")
```

### 7.2 Generate Drift Report

```python
# Generate comprehensive report with Evidently
report_path = detector.generate_drift_report(
    current_data=df_current,
    reference_data=df_features,
    output_path="reports/drift_report.html"
)

print(f"Report saved to {report_path}")
```

### 7.3 Check Retraining Trigger

```python
# Determine if retraining is needed
should_retrain, reason = detector.should_trigger_retraining(
    drift_results=drift_results,
    performance_degradation=0.05  # 5% performance drop
)

if should_retrain:
    print(f"⚠️  Retraining recommended: {reason}")
else:
    print("✓ No retraining needed")
```

### 7.4 View Monitoring Dashboards

**Prometheus Metrics:**
```bash
open http://localhost:9090
```

**Grafana Dashboards:**
```bash
open http://localhost:3000
# Login: admin / admin
```

---

## Phase 8: End-to-End Pipeline Execution (30 minutes)

### 8.1 Complete Pipeline Script

```python
#!/usr/bin/env python
"""Complete end-to-end ML pipeline."""

from src.data import DataIngestionPipeline
from src.data.validation import DataValidator
from src.features.engineering import FeatureEngineer
from src.features.store import FeatureStore
from src.models.train import ModelTrainer
from src.monitoring.drift_detection import DriftDetector

def main():
    # 1. Data Ingestion
    print("=== Phase 1: Data Ingestion ===")
    pipeline = DataIngestionPipeline()
    pipeline.register_csv_connector(
        name="raw_data",
        file_path="data/raw/customer_churn_train.csv"
    )
    df_raw = pipeline.ingest("raw_data")

    # 2. Data Validation
    print("=== Phase 2: Data Validation ===")
    validator = DataValidator()
    validator.create_customer_churn_suite()
    validation = validator.validate(df_raw, "customer_churn_suite")

    if not validation['success']:
        raise ValueError("Data validation failed!")

    # 3. Feature Engineering
    print("=== Phase 3: Feature Engineering ===")
    engineer = FeatureEngineer()
    df_features = engineer.engineer_features(df_raw, fit=True)
    engineer.save_artifacts("models/artifacts")

    # 4. Feature Store
    print("=== Phase 4: Feature Store ===")
    store = FeatureStore()
    feature_set_id = store.create_feature_set(
        "churn_features_v1",
        engineer.get_feature_names(),
        version=1
    )
    store.write_features(feature_set_id, df_features)

    # 5. Model Training
    print("=== Phase 5: Model Training ===")
    trainer = ModelTrainer()
    X_train, X_val, X_test, y_train, y_val, y_test = trainer.prepare_data(df_features)
    results = trainer.train_all_models(X_train, y_train, X_val, y_val, optimize=True)

    champion = trainer.best_models["champion"]
    test_metrics = trainer.evaluate_on_test_set(champion, X_test, y_test)

    print(f"Champion Model Test ROC AUC: {test_metrics['roc_auc']:.4f}")

    # 6. Save Model
    print("=== Phase 6: Model Saving ===")
    import pickle
    with open("models/champion_model.pkl", "wb") as f:
        pickle.dump(champion, f)

    # 7. Drift Detection Setup
    print("=== Phase 7: Monitoring Setup ===")
    detector = DriftDetector(reference_data=df_features)

    print("✓ Pipeline execution complete!")

if __name__ == "__main__":
    main()
```

Run the complete pipeline:
```bash
python scripts/run_pipeline.py
```

---

## Phase 9: Production Deployment (Optional)

### 9.1 Build Docker Images

```bash
# Build API image
docker build -t ml-pipeline-api:latest .

# Push to registry
docker tag ml-pipeline-api:latest your-registry/ml-pipeline-api:latest
docker push your-registry/ml-pipeline-api:latest
```

### 9.2 Deploy to Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/mlflow.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml

# Check deployment
kubectl get pods -n ml-pipeline
kubectl get services -n ml-pipeline
```

### 9.3 Set Up CI/CD

GitHub Actions workflow is in `.github/workflows/ci-cd.yml`:
- Runs tests on PR
- Builds Docker image on merge to main
- Deploys to staging/production

---

## Troubleshooting

### Common Issues

**1. Database Connection Error:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart if needed
docker-compose restart postgres
```

**2. MLflow Not Accessible:**
```bash
# Check MLflow logs
docker-compose logs mlflow

# Restart MLflow
docker-compose restart mlflow
```

**3. Model Loading Error:**
```python
# Verify model file exists
import os
print(os.path.exists("models/champion_model.pkl"))

# Load manually and debug
import pickle
with open("models/champion_model.pkl", "rb") as f:
    model = pickle.load(f)
```

**4. Feature Engineering Issues:**
```python
# Check for missing columns
required_cols = ["age", "gender", "tenure", "monthly_charges", ...]
missing = [col for col in required_cols if col not in df.columns]
print(f"Missing columns: {missing}")
```

---

## Performance Benchmarks

Expected performance on 10K training set:
- **Data Ingestion:** < 5 seconds
- **Data Validation:** < 10 seconds
- **Feature Engineering:** < 15 seconds
- **Model Training (single):** < 30 seconds
- **Hyperparameter Optimization:** 5-10 minutes (100 trials)
- **Prediction (single):** < 50ms
- **Prediction (batch 1000):** < 500ms

---

## Next Steps

1. **Add More Data Sources:** Implement Kafka/API connectors for real-time data
2. **Automated Retraining:** Set up Airflow DAG for scheduled retraining
3. **A/B Testing:** Implement champion/challenger model comparison
4. **Advanced Monitoring:** Add custom business metrics and alerting
5. **Model Explainability:** Integrate SHAP/LIME for model interpretability
6. **Security:** Add authentication, rate limiting, input validation
7. **Scaling:** Set up Kubernetes HPA for auto-scaling based on load

---

## Support

For questions or issues:
1. Check the README.md
2. Review API documentation at `/docs`
3. Check MLflow experiments at http://localhost:5000
4. Review logs in `logs/` directory

---

**Congratulations! You've implemented a production-grade MLOps pipeline!** 🎉
