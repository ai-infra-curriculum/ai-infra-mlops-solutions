"""Data validation using Great Expectations."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import great_expectations as gx
import pandas as pd
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.data_context import BaseDataContext
from great_expectations.data_context.types.base import (
    DataContextConfig,
    InMemoryStoreBackendDefaults,
)

from src.utils.config import get_config
from src.utils.logger import get_logger
from src.utils.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()
config = get_config()


class DataValidator:
    """Data validation using Great Expectations."""

    def __init__(
        self,
        context_root_dir: Optional[str] = None,
        expectations_dir: Optional[str] = None,
        use_in_memory: bool = False,
    ):
        """Initialize data validator.

        Args:
            context_root_dir: Root directory for Great Expectations context
            expectations_dir: Directory for expectation suites
            use_in_memory: Whether to use in-memory context (for testing)
        """
        self.context_root_dir = context_root_dir or str(
            Path.cwd() / "data" / "great_expectations"
        )
        self.expectations_dir = expectations_dir or str(
            Path(self.context_root_dir) / "expectations"
        )
        self.use_in_memory = use_in_memory

        # Initialize Great Expectations context
        self.context = self._initialize_context()

        # Validation history
        self._validation_history: List[Dict[str, Any]] = []

        logger.info(f"Initialized DataValidator (in_memory={use_in_memory})")

    def _initialize_context(self) -> BaseDataContext:
        """Initialize Great Expectations data context.

        Returns:
            Great Expectations data context
        """
        try:
            if self.use_in_memory:
                # Use in-memory context for testing
                context_config = DataContextConfig(
                    store_backend_defaults=InMemoryStoreBackendDefaults()
                )
                context = gx.get_context(project_config=context_config)
                logger.debug("Initialized in-memory Great Expectations context")
            else:
                # Use file-based context
                Path(self.context_root_dir).mkdir(parents=True, exist_ok=True)
                context = gx.get_context(context_root_dir=self.context_root_dir)
                logger.debug(f"Initialized Great Expectations context at {self.context_root_dir}")

            return context

        except Exception as e:
            logger.error(f"Failed to initialize Great Expectations context: {e}")
            raise

    def create_expectation_suite(
        self,
        suite_name: str,
        overwrite_existing: bool = False,
    ) -> None:
        """Create a new expectation suite.

        Args:
            suite_name: Name of the expectation suite
            overwrite_existing: Whether to overwrite if suite exists
        """
        try:
            self.context.add_expectation_suite(
                expectation_suite_name=suite_name,
                overwrite_existing=overwrite_existing,
            )
            logger.info(f"Created expectation suite: {suite_name}")

        except Exception as e:
            logger.error(f"Failed to create expectation suite '{suite_name}': {e}")
            raise

    def create_customer_churn_suite(
        self,
        suite_name: str = "customer_churn_suite",
    ) -> None:
        """Create comprehensive expectation suite for customer churn data.

        This suite includes 20+ validation rules covering:
        - Data completeness
        - Data types
        - Value ranges
        - Categorical values
        - Statistical distributions
        - Cross-column relationships
        - Data quality

        Args:
            suite_name: Name of the expectation suite
        """
        logger.info(f"Creating customer churn expectation suite: {suite_name}")

        self.create_expectation_suite(suite_name, overwrite_existing=True)
        suite = self.context.get_expectation_suite(suite_name)

        expectations = []

        # 1. Table-level expectations
        expectations.extend(
            [
                {
                    "expectation_type": "expect_table_row_count_to_be_between",
                    "kwargs": {
                        "min_value": 1,
                        "max_value": None,
                    },
                    "meta": {"description": "Table must have at least 1 row"},
                },
                {
                    "expectation_type": "expect_table_columns_to_match_set",
                    "kwargs": {
                        "column_set": [
                            "customer_id",
                            "age",
                            "gender",
                            "tenure",
                            "monthly_charges",
                            "total_charges",
                            "contract_type",
                            "payment_method",
                            "internet_service",
                            "online_security",
                            "tech_support",
                            "churn",
                        ],
                        "exact_match": False,
                    },
                    "meta": {"description": "Required columns must be present"},
                },
            ]
        )

        # 2. Customer ID expectations
        expectations.extend(
            [
                {
                    "expectation_type": "expect_column_values_to_be_unique",
                    "kwargs": {"column": "customer_id"},
                    "meta": {"description": "Customer ID must be unique"},
                },
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "customer_id"},
                    "meta": {"description": "Customer ID cannot be null"},
                },
            ]
        )

        # 3. Age expectations
        expectations.extend(
            [
                {
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {
                        "column": "age",
                        "min_value": 18,
                        "max_value": 100,
                    },
                    "meta": {"description": "Age must be between 18 and 100"},
                },
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "age"},
                    "meta": {"description": "Age cannot be null"},
                },
                {
                    "expectation_type": "expect_column_mean_to_be_between",
                    "kwargs": {
                        "column": "age",
                        "min_value": 20,
                        "max_value": 80,
                    },
                    "meta": {"description": "Average age should be reasonable"},
                },
            ]
        )

        # 4. Gender expectations
        expectations.extend(
            [
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {
                        "column": "gender",
                        "value_set": ["Male", "Female", "Other"],
                    },
                    "meta": {"description": "Gender must be valid value"},
                },
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "gender"},
                    "meta": {"description": "Gender cannot be null"},
                },
            ]
        )

        # 5. Tenure expectations
        expectations.extend(
            [
                {
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {
                        "column": "tenure",
                        "min_value": 0,
                        "max_value": 100,
                    },
                    "meta": {"description": "Tenure must be non-negative and reasonable"},
                },
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "tenure"},
                    "meta": {"description": "Tenure cannot be null"},
                },
            ]
        )

        # 6. Monthly charges expectations
        expectations.extend(
            [
                {
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {
                        "column": "monthly_charges",
                        "min_value": 0,
                        "max_value": 1000,
                    },
                    "meta": {"description": "Monthly charges must be positive and reasonable"},
                },
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "monthly_charges"},
                    "meta": {"description": "Monthly charges cannot be null"},
                },
                {
                    "expectation_type": "expect_column_mean_to_be_between",
                    "kwargs": {
                        "column": "monthly_charges",
                        "min_value": 10,
                        "max_value": 500,
                    },
                    "meta": {"description": "Average monthly charges should be reasonable"},
                },
            ]
        )

        # 7. Total charges expectations
        expectations.extend(
            [
                {
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {
                        "column": "total_charges",
                        "min_value": 0,
                        "max_value": 100000,
                    },
                    "meta": {"description": "Total charges must be non-negative"},
                },
                # Total charges can be null for new customers
            ]
        )

        # 8. Contract type expectations
        expectations.extend(
            [
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {
                        "column": "contract_type",
                        "value_set": ["Month-to-month", "One year", "Two year"],
                    },
                    "meta": {"description": "Contract type must be valid"},
                },
            ]
        )

        # 9. Payment method expectations
        expectations.extend(
            [
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {
                        "column": "payment_method",
                        "value_set": [
                            "Electronic check",
                            "Mailed check",
                            "Bank transfer",
                            "Credit card",
                        ],
                    },
                    "meta": {"description": "Payment method must be valid"},
                },
            ]
        )

        # 10. Internet service expectations
        expectations.extend(
            [
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {
                        "column": "internet_service",
                        "value_set": ["DSL", "Fiber optic", "No"],
                    },
                    "meta": {"description": "Internet service must be valid"},
                },
            ]
        )

        # 11. Boolean service expectations (online_security, tech_support, etc.)
        for column in ["online_security", "tech_support"]:
            expectations.append(
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {
                        "column": column,
                        "value_set": ["Yes", "No", "No internet service"],
                    },
                    "meta": {"description": f"{column} must be valid value"},
                }
            )

        # 12. Churn target variable expectations
        expectations.extend(
            [
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {
                        "column": "churn",
                        "value_set": [0, 1, "Yes", "No"],
                    },
                    "meta": {"description": "Churn must be binary"},
                },
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "churn"},
                    "meta": {"description": "Churn target cannot be null"},
                },
            ]
        )

        # 13. Cross-column relationships
        expectations.extend(
            [
                {
                    "expectation_type": "expect_column_pair_values_a_to_be_greater_than_b",
                    "kwargs": {
                        "column_A": "total_charges",
                        "column_B": "monthly_charges",
                        "or_equal": True,
                        "ignore_row_if": "either_value_is_missing",
                    },
                    "meta": {
                        "description": "Total charges should be >= monthly charges for active customers"
                    },
                },
            ]
        )

        # 14. Data freshness (optional - useful for production)
        # expectations.append({
        #     "expectation_type": "expect_column_max_to_be_between",
        #     "kwargs": {
        #         "column": "ingestion_timestamp",
        #         "min_value": datetime.now() - timedelta(days=7),
        #         "max_value": datetime.now(),
        #     },
        #     "meta": {"description": "Data should be fresh (within last 7 days)"},
        # })

        # Add all expectations to suite
        for expectation in expectations:
            suite.add_expectation_configuration(**expectation)

        # Save suite
        self.context.save_expectation_suite(expectation_suite=suite)

        logger.info(
            f"Created expectation suite '{suite_name}' with {len(expectations)} expectations"
        )

    def validate(
        self,
        df: pd.DataFrame,
        suite_name: str,
        batch_id: Optional[str] = None,
        save_results: bool = True,
    ) -> Dict[str, Any]:
        """Validate DataFrame against expectation suite.

        Args:
            df: DataFrame to validate
            suite_name: Name of the expectation suite
            batch_id: Optional batch identifier
            save_results: Whether to save validation results

        Returns:
            Dictionary containing validation results with keys:
                - success: Whether all expectations passed
                - statistics: Summary statistics
                - results: List of expectation results
                - evaluated_expectations: Number of expectations evaluated
                - successful_expectations: Number of successful expectations
                - unsuccessful_expectations: Number of failed expectations
                - success_percent: Percentage of successful expectations

        Raises:
            ValueError: If suite doesn't exist
        """
        start_time = datetime.now()
        batch_id = batch_id or f"batch_{start_time.strftime('%Y%m%d_%H%M%S')}"

        logger.info(
            f"Validating DataFrame ({len(df)} rows) against suite '{suite_name}' "
            f"(batch_id={batch_id})"
        )

        try:
            # Create batch request
            batch_request = RuntimeBatchRequest(
                datasource_name="pandas_datasource",
                data_connector_name="runtime_data_connector",
                data_asset_name="customer_data",
                runtime_parameters={"batch_data": df},
                batch_identifiers={"batch_id": batch_id},
            )

            # Create or get datasource
            try:
                datasource = self.context.get_datasource("pandas_datasource")
            except Exception:
                datasource_config = {
                    "name": "pandas_datasource",
                    "class_name": "Datasource",
                    "execution_engine": {
                        "class_name": "PandasExecutionEngine",
                    },
                    "data_connectors": {
                        "runtime_data_connector": {
                            "class_name": "RuntimeDataConnector",
                            "batch_identifiers": ["batch_id"],
                        },
                    },
                }
                datasource = self.context.add_datasource(**datasource_config)

            # Get expectation suite
            suite = self.context.get_expectation_suite(suite_name)

            # Create checkpoint
            checkpoint_name = f"checkpoint_{suite_name}"
            checkpoint_config = {
                "name": checkpoint_name,
                "config_version": 1,
                "class_name": "Checkpoint",
                "validations": [
                    {
                        "batch_request": batch_request,
                        "expectation_suite_name": suite_name,
                    }
                ],
            }

            # Run validation
            checkpoint = self.context.add_checkpoint(**checkpoint_config)
            results = checkpoint.run()

            # Extract results
            validation_result = results.list_validation_results()[0]
            success = validation_result.success

            # Calculate statistics
            statistics = validation_result.statistics
            evaluated = statistics.get("evaluated_expectations", 0)
            successful = statistics.get("successful_expectations", 0)
            unsuccessful = statistics.get("unsuccessful_expectations", 0)
            success_percent = (successful / evaluated * 100) if evaluated > 0 else 0

            # Build result summary
            result_summary = {
                "success": success,
                "batch_id": batch_id,
                "suite_name": suite_name,
                "validation_time": datetime.now(),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "row_count": len(df),
                "statistics": {
                    "evaluated_expectations": evaluated,
                    "successful_expectations": successful,
                    "unsuccessful_expectations": unsuccessful,
                    "success_percent": success_percent,
                },
                "results": [],
            }

            # Extract individual expectation results
            for result in validation_result.results:
                result_summary["results"].append(
                    {
                        "expectation_type": result.expectation_config.expectation_type,
                        "success": result.success,
                        "result": result.result,
                    }
                )

            # Log results
            if success:
                logger.info(
                    f"Validation PASSED: {successful}/{evaluated} expectations succeeded "
                    f"({success_percent:.1f}%)"
                )
                metrics.increment_data_validation(
                    suite=suite_name,
                    status="success",
                )
            else:
                logger.warning(
                    f"Validation FAILED: {unsuccessful}/{evaluated} expectations failed "
                    f"({100 - success_percent:.1f}%)"
                )
                metrics.increment_data_validation(
                    suite=suite_name,
                    status="failure",
                )

                # Log failed expectations
                for result in result_summary["results"]:
                    if not result["success"]:
                        logger.warning(
                            f"  - Failed: {result['expectation_type']}: {result['result']}"
                        )

            # Save to history
            self._validation_history.append(result_summary)

            return result_summary

        except Exception as e:
            logger.error(f"Validation failed with error: {e}")
            metrics.increment_data_validation(
                suite=suite_name,
                status="error",
            )
            raise

    def get_validation_history(self) -> List[Dict[str, Any]]:
        """Get validation history.

        Returns:
            List of validation result summaries
        """
        return self._validation_history

    def export_validation_report(
        self,
        validation_result: Dict[str, Any],
        output_path: str,
        format: str = "json",
    ) -> None:
        """Export validation results to file.

        Args:
            validation_result: Validation result dictionary
            output_path: Output file path
            format: Export format ('json' or 'html')
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            if format == "json":
                # Serialize datetime objects
                def serialize(obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    raise TypeError(f"Type {type(obj)} not serializable")

                with open(output_path, "w") as f:
                    json.dump(validation_result, f, indent=2, default=serialize)

                logger.info(f"Exported validation report to {output_path}")

            elif format == "html":
                # Generate HTML report (simplified)
                html_content = self._generate_html_report(validation_result)
                with open(output_path, "w") as f:
                    f.write(html_content)

                logger.info(f"Exported HTML validation report to {output_path}")

            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Failed to export validation report: {e}")
            raise

    def _generate_html_report(self, validation_result: Dict[str, Any]) -> str:
        """Generate HTML validation report.

        Args:
            validation_result: Validation result dictionary

        Returns:
            HTML content as string
        """
        stats = validation_result["statistics"]
        success = validation_result["success"]
        status_color = "green" if success else "red"
        status_text = "PASSED" if success else "FAILED"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Validation Report - {validation_result['suite_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .status {{ font-size: 24px; font-weight: bold; color: {status_color}; }}
        .stats {{ margin: 20px 0; }}
        .stat {{ display: inline-block; margin-right: 30px; }}
        .stat-label {{ font-weight: bold; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
    </style>
</head>
<body>
    <h1>Validation Report</h1>
    <div class="status">Status: {status_text}</div>

    <div class="stats">
        <div class="stat">
            <span class="stat-label">Suite:</span> {validation_result['suite_name']}
        </div>
        <div class="stat">
            <span class="stat-label">Batch ID:</span> {validation_result['batch_id']}
        </div>
        <div class="stat">
            <span class="stat-label">Rows:</span> {validation_result['row_count']}
        </div>
    </div>

    <div class="stats">
        <div class="stat">
            <span class="stat-label">Evaluated:</span> {stats['evaluated_expectations']}
        </div>
        <div class="stat">
            <span class="stat-label">Successful:</span>
            <span class="success">{stats['successful_expectations']}</span>
        </div>
        <div class="stat">
            <span class="stat-label">Failed:</span>
            <span class="failure">{stats['unsuccessful_expectations']}</span>
        </div>
        <div class="stat">
            <span class="stat-label">Success Rate:</span> {stats['success_percent']:.1f}%
        </div>
    </div>

    <h2>Expectation Results</h2>
    <table>
        <tr>
            <th>Expectation Type</th>
            <th>Status</th>
            <th>Details</th>
        </tr>
"""

        for result in validation_result["results"]:
            status_class = "success" if result["success"] else "failure"
            status_text = "✓ PASS" if result["success"] else "✗ FAIL"
            details = json.dumps(result["result"], indent=2) if result["result"] else "N/A"

            html += f"""
        <tr>
            <td>{result['expectation_type']}</td>
            <td class="{status_class}">{status_text}</td>
            <td><pre>{details}</pre></td>
        </tr>
"""

        html += """
    </table>
</body>
</html>
"""

        return html

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"DataValidator(context_root={self.context_root_dir}, "
            f"in_memory={self.use_in_memory})"
        )
