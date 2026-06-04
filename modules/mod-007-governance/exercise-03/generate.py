"""Auto-fill model card template from MLflow run metadata."""
import argparse

from mlflow.tracking import MlflowClient


TEMPLATE = open("MODEL_CARD.md").read()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("version")
    args = p.parse_args()

    c = MlflowClient()
    mv = c.get_model_version(args.name, args.version)
    run = c.get_run(mv.run_id)

    # Use Jinja or simple substitution in production; this prints the template
    print(TEMPLATE)
    print("\n=== Live metadata ===")
    print(f"params: {run.data.params}")
    print(f"metrics: {run.data.metrics}")


if __name__ == "__main__":
    main()
