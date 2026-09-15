#!/usr/bin/env bash

set -u

job_id=${1:?usage: monitor.sh JOB_ID}
run_root=$(cd "$(dirname "$0")" && pwd)
log_file="$run_root/logs/monitor.log"
mail_marker="$run_root/logs/monitor-failure-mail.sent"

while true; do
  now=$(date --iso-8601=seconds)
  state=$(squeue -h -j "$job_id" -o '%T' | head -1)
  exit_code=-
  if [[ -z $state ]]; then
    record=$(sacct -X -n -P -j "$job_id" -o JobIDRaw,State,ExitCode |
      awk -F '|' -v id="$job_id" '$1 == id { print $2 "|" $3; exit }')
    state=${record%%|*}
    if [[ $record == *'|'* ]]; then
      exit_code=${record#*|}
    fi
  fi
  state=${state:-UNKNOWN}

  amrex_latest=$(find "$run_root/raw/amrex" -maxdepth 1 -type d -name 'chk*' \
    -printf '%f\n' 2>/dev/null | sort | tail -1)
  unstruct_latest=$(find "$run_root/raw/unstruct" -maxdepth 1 -type d \
    -name 'checkpoint*' -printf '%f\n' 2>/dev/null | sort | tail -1)
  printf '%s job=%s state=%s exit=%s amrex=%s unstruct=%s\n' \
    "$now" "$job_id" "$state" "$exit_code" \
    "${amrex_latest:-none}" "${unstruct_latest:-none}" >> "$log_file"

  case $state in
    COMPLETED*)
      exit 0
      ;;
    FAILED*|CANCELLED*|TIMEOUT*|NODE_FAIL*|OUT_OF_MEMORY*|BOOT_FAIL*|DEADLINE*)
      if [[ ! -e $mail_marker ]] && command -v mail >/dev/null 2>&1; then
        {
          printf 'NACA0012 SST job %s entered state %s with exit %s.\n\n' \
            "$job_id" "$state" "$exit_code"
          tail -80 "$run_root/logs/slurm-$job_id.err" 2>/dev/null || true
        } | mail -s "OverlapHarness job $job_id failed: $state" \
          thenwhowon@gmail.com
        : > "$mail_marker"
      fi
      exit 1
      ;;
  esac

  sleep 3600
done
