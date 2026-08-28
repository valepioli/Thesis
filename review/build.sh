#!/usr/bin/env bash
# Ricompila i due PDF tracciati partendo pulito.
#
# Perche' esiste: latexmk rilegge .lof, .tdo e .cco del giro precedente. Se una
# compilazione e' fallita a meta', quei file restano corrotti e la compilazione
# successiva segnala errori che NON sono nel sorgente. E' successo due volte, e
# la seconda ha portato a inseguire un baco inesistente per parecchio tempo.
# Qui si cancellano sempre prima di ricompilare.
#
#   bash review/build.sh            # entrambi i PDF
#   bash review/build.sh thesis     # solo la tesi completa
#   bash review/build.sh chapter    # solo il capitolo 1
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="Master-Thesis-main"
TARGET="${1:-all}"
rc=0

build () {          # $1 = directory, $2 = jobname
  local dir="$1" job="$2"
  ( cd "$dir" || exit 1
    rm -f "$job".{aux,lof,lot,toc,out,tdo,cco,fdb_latexmk,bcf,run.xml}
    latexmk -pdf -interaction=nonstopmode "$job".tex >/dev/null 2>&1
    local err
    err=$(grep -c '^! ' "$job".log 2>/dev/null); err=${err:-0}
    if [ "$err" -eq 0 ]; then
      printf '  %-34s ok\n' "$job.pdf"
    else
      printf '  %-34s %s errori\n' "$job.pdf" "$err"
      grep -n '^! ' -A3 "$job".log | head -12 | sed 's/^/      /'
      exit 1
    fi )
}

echo "Ricompilazione (i file di lista vengono azzerati prima)"
if [ "$TARGET" = all ] || [ "$TARGET" = thesis ];  then build "$ROOT" thesis_main || rc=1; fi
if [ "$TARGET" = all ] || [ "$TARGET" = chapter ]; then build "$ROOT/chapters/Chapter_1" chapter_1_main || rc=1; fi
exit $rc
