#!/usr/bin/env bash
# Build COMPARE sweep RPS ladder: explicit list, or LOADS × REPEATS matrix, optional shuffle.
#
# Env:
#   COMPARE_SWEEP_RPS          — comma list (default if COMPARE_SWEEP_LOADS unset)
#   COMPARE_SWEEP_LOADS        — comma load points (e.g. 200,220,240,260,280)
#   COMPARE_SWEEP_REPEATS_PER_LOAD — repeats per load (default 1)
#   COMPARE_SWEEP_ROUNDS       — cap rounds (must be <= expanded list length)
#   COMPARE_SWEEP_SHUFFLE_ROUNDS — 1 = randomize round order (reduces drift bias)
#   COMPARE_SWEEP_SHUFFLE_SEED — optional int seed for reproducible shuffle
#
# Sets: CLEAN_RPS[], ROUND_LABELS[], ROUNDS
# shellcheck shell=bash

_expand_trim_csv_item() {
  echo "$1" | xargs
}

parse_compare_sweep_rps_matrix() {
  local default_rps="${1:-}"
  CLEAN_RPS=()
  ROUND_LABELS=()

  if [[ -n "${COMPARE_SWEEP_LOADS:-}" ]]; then
    local repeats="${COMPARE_SWEEP_REPEATS_PER_LOAD:-1}"
    if ! [[ "${repeats}" =~ ^[0-9]+$ ]] || ((repeats < 1)); then
      echo "COMPARE_SWEEP_REPEATS_PER_LOAD must be a positive integer" >&2
      return 1
    fi
    IFS=',' read -r -a _loads <<< "${COMPARE_SWEEP_LOADS}"
    for _load in "${_loads[@]}"; do
      _q="$(_expand_trim_csv_item "${_load}")"
      [[ -z "${_q}" ]] && continue
      for ((rep = 1; rep <= repeats; rep++)); do
        CLEAN_RPS+=("${_q}")
        ROUND_LABELS+=("rps=${_q}#${rep}")
      done
    done
  elif [[ -n "${COMPARE_SWEEP_RPS:-}" ]]; then
    IFS=',' read -r -a _rps <<< "${COMPARE_SWEEP_RPS}"
    for _r in "${_rps[@]}"; do
      _q="$(_expand_trim_csv_item "${_r}")"
      [[ -n "${_q}" ]] && CLEAN_RPS+=("${_q}") && ROUND_LABELS+=("rps=${_q}")
    done
  elif [[ -n "${default_rps}" ]]; then
    IFS=',' read -r -a _rps <<< "${default_rps}"
    for _r in "${_rps[@]}"; do
      _q="$(_expand_trim_csv_item "${_r}")"
      [[ -n "${_q}" ]] && CLEAN_RPS+=("${_q}") && ROUND_LABELS+=("rps=${_q}")
    done
  fi

  if ((${#CLEAN_RPS[@]} == 0)); then
    echo "COMPARE_SWEEP_RPS / COMPARE_SWEEP_LOADS produced an empty RPS list" >&2
    return 1
  fi

  if [[ "${COMPARE_SWEEP_SHUFFLE_ROUNDS:-}" == "1" ]]; then
    _shuffle_compare_sweep_rounds || return 1
  fi

  ROUNDS="${COMPARE_SWEEP_ROUNDS:-${#CLEAN_RPS[@]}}"
  if ! [[ "${ROUNDS}" =~ ^[0-9]+$ ]] || ((ROUNDS < 1)); then
    echo "COMPARE_SWEEP_ROUNDS must be a positive integer" >&2
    return 1
  fi
  if ((ROUNDS > ${#CLEAN_RPS[@]})); then
    echo "COMPARE_SWEEP_ROUNDS=${ROUNDS} exceeds ladder length ${#CLEAN_RPS[@]}" >&2
    return 1
  fi

  if ((ROUNDS < ${#CLEAN_RPS[@]})); then
    CLEAN_RPS=("${CLEAN_RPS[@]:0:ROUNDS}")
    ROUND_LABELS=("${ROUND_LABELS[@]:0:ROUNDS}")
  fi
  return 0
}

_shuffle_compare_sweep_rounds() {
  local n=${#CLEAN_RPS[@]}
  if ((n < 2)); then
    return 0
  fi
  local seed="${COMPARE_SWEEP_SHUFFLE_SEED:-}"
  local rps_csv labels_csv
  rps_csv="$(IFS=,; echo "${CLEAN_RPS[*]}")"
  labels_csv="$(IFS='|'; echo "${ROUND_LABELS[*]}")"
  read -r rps_csv labels_csv < <(
    RPS_CSV="${rps_csv}" LABELS_CSV="${labels_csv}" SEED="${seed}" python3 - <<'PY'
import os, random
rps = [x for x in os.environ.get("RPS_CSV", "").split(",") if x]
labels = [x for x in os.environ.get("LABELS_CSV", "").split("|") if x]
if len(rps) != len(labels):
    raise SystemExit("internal: rps/labels length mismatch")
seed_s = os.environ.get("SEED", "").strip()
rng = random.Random(int(seed_s) if seed_s.isdigit() else None)
order = list(range(len(rps)))
rng.shuffle(order)
print(",".join(rps[i] for i in order))
print("|".join(labels[i] for i in order))
PY
  ) || return 1
  IFS=',' read -r -a CLEAN_RPS <<< "${rps_csv}"
  IFS='|' read -r -a ROUND_LABELS <<< "${labels_csv}"
  return 0
}
