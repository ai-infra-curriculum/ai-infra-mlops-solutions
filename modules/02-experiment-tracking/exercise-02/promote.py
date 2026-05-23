"""Quality-gated promotion to Staging / Production."""
import argparse
import sys

from mlflow.tracking import MlflowClient


GATE = -0.005   # may not drop more than 0.5pp vs current Production


def _metric(client, name, version, key):
    run_id = client.get_model_version(name, version).run_id
    return client.get_run(run_id).data.metrics.get(key)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("version")
    p.add_argument("--to", choices=["staging", "production"], required=True)
    args = p.parse_args()

    c = MlflowClient()
    cand = _metric(c, args.name, args.version, "accuracy")
    prod_vers = c.get_latest_versions(args.name, stages=["Production"])
    if prod_vers:
        prod_acc = _metric(c, args.name, prod_vers[0].version, "accuracy")
        delta = cand - prod_acc
        print(f"candidate={cand:.4f}  prod={prod_acc:.4f}  delta={delta:+.4f}")
        if delta < GATE:
            print("GATE FAILED")
            sys.exit(1)

    c.transition_model_version_stage(
        name=args.name, version=args.version,
        stage=args.to.capitalize(),
        archive_existing_versions=(args.to == "production"),
    )
    print(f"promoted {args.name} v{args.version} → {args.to}")


if __name__ == "__main__":
    main()
