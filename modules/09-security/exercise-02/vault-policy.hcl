# Minimal Vault policy for an ML serving pod (uses Vault Agent + IRSA/workload-id).
path "kv/data/ml-platform/iris-api/*" { capabilities = ["read"] }
path "kv/metadata/ml-platform/iris-api/*" { capabilities = ["list", "read"] }
path "database/creds/iris-api" { capabilities = ["read"] }   # dynamic DB creds
# No write, no list outside the iris-api prefix.
