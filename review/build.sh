#!/usr/bin/env bash
# Ricompilazione dei due PDF tracciati a partire da uno stato pulito.
#
# La rimozione preliminare dei file ausiliari e' necessaria: latexmk rilegge
# .lof, .tdo e .cco della compilazione precedente e, qualora questa si sia
# interrotta, tali file permangono in stato incoerente e la compilazione
# successiva segnala errori non presenti nel sorgente. La circostanza si e'
# verificata in due occasioni, la seconda delle quali ha comportato la ricerca
# prolungata di un difetto inesistente.
#
#   bash review/build.sh            # entrambi i PDF
#   bash review/build.sh thesis     # sola tesi completa
#   bash review/build.sh chapter    # solo Capitolo 1
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
