#!/usr/bin/env bash
# Wire Nextcloud AIO integration_openai + assistant to City llama.cpp on Frank.
# Requires: col-llama-cpp on nextcloud-aio network, healthy :8081 OpenAI API.
set -euo pipefail

ENV_FILE="${1:-}"
if [[ -n "$ENV_FILE" && -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  # Values with spaces/parens must be quoted in the env file.
  source "$ENV_FILE"
  set +a
fi

URL="${NC_OPENAI_URL:-http://col-llama-cpp:8081}"
MODEL="${NC_OPENAI_MODEL:-/models/Bonsai-4B-Q1_0.gguf}"
SERVICE_NAME="${NC_OPENAI_SERVICE_NAME:-Bonsai LLM (TRL4)}"
API_KEY="${NC_OPENAI_API_KEY:-no-key-needed}"
CHAT_ENABLED="${NC_OPENAI_CHAT_ENDPOINT_ENABLED:-1}"

echo "Preflight: NC container -> $URL/health"
docker exec nextcloud-aio-nextcloud curl -sf --max-time 5 "${URL}/health" >/dev/null
echo "Preflight OK"

occ() {
  docker exec -u 33 nextcloud-aio-nextcloud php occ "$@"
}

# Ensure apps present/enabled
occ app:enable integration_openai >/dev/null || true
occ app:enable assistant >/dev/null || true

occ config:app:set integration_openai url --value="$URL"
occ config:app:set integration_openai default_completion_model_id --value="$MODEL"
occ config:app:set integration_openai service_name --value="$SERVICE_NAME"
occ config:app:set integration_openai api_key --value="$API_KEY"
occ config:app:set integration_openai chat_endpoint_enabled --value="$CHAT_ENABLED"

# Refresh model cache JSON from live backend (best-effort)
MODELS_JSON="$(docker exec nextcloud-aio-nextcloud curl -sf --max-time 10 "${URL}/v1/models" || true)"
if [[ -n "$MODELS_JSON" ]]; then
  # store via php to avoid shell escaping issues
  docker exec -i -u 33 nextcloud-aio-nextcloud php -r '
    require "/var/www/html/lib/base.php";
    $raw = stream_get_contents(STDIN);
    $j = json_decode($raw, true);
    if (!is_array($j)) { fwrite(STDERR, "invalid models json\n"); exit(1); }
    \OC::$server->getConfig()->setAppValue("integration_openai", "models", $raw);
    echo "models_cache_updated\n";
  ' <<<"$MODELS_JSON"
fi

echo "Verify:"
echo -n "  url="; occ config:app:get integration_openai url
echo -n "  model="; occ config:app:get integration_openai default_completion_model_id
echo -n "  service="; occ config:app:get integration_openai service_name
echo -n "  chat="; occ config:app:get integration_openai chat_endpoint_enabled
occ app:list 2>/dev/null | grep -iE "assistant|integration_openai" || true
echo "DONE"
