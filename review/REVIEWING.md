# Come annotare questa tesi

Sistema di revisione a piu' revisori. Serve per aggiungere note nel margine
senza toccare il testo della studentessa e senza pestarsi i piedi fra revisori.

La studentessa **non lavora su questi rami**: guarda il PDF con le note e
continua a scrivere su `main`. Di conseguenza nessuno deve marcare le note come
"risolte" a mano: lo stato si ricava confrontando le note con `main`
(vedi *Stato delle note* in fondo).

---

## 1. Aggiungersi come revisore

Una riga in `Master-Thesis-main/preamble.tex`, nella sezione
*REGISTRO DEI REVISORI*:

```latex
\DeclareReviewer{GS}{blue!15}
```

`GS` sono le tue iniziali (due lettere maiuscole), `blue!15` il tuo colore.
Colori gia' presi: **teal** = CC (Claude Code), e la colonna di sinistra e'
di MD. Scegline uno chiaro e distinguibile: `blue!15`, `violet!15`,
`green!20`, `yellow!25`.

Da quel momento esiste la macro `\GS`, con la numerazione e l'elenco tuoi.

---

## 2. Scrivere una nota

```latex
\GS{categoria}{testo della tesi a cui ti agganci}{la tua osservazione}
```

- **primo argomento**: la categoria, una parola. Usa quelle che ti servono
  (`errore`, `nota`, `forma`, `riferimenti`, `domanda`).
- **secondo argomento**: un pezzo **letterale** del testo della tesi. Viene
  sottolineato tratteggiato e marcato con `[GS 1]`, `[GS 2]`, ... Deve essere
  copiato esatto, ed e' meglio che sia breve e senza formule.
- **terzo argomento**: la nota vera e propria, che finisce nel riquadro a
  destra e nell'elenco *Reviewer notes*.

Esempio reale:

```latex
\GS{errore}{The measured waist agrees with the specified MFD}{Con
$w_{0x}=5.67\pm0.10~\mu$m contro un nominale di $5.2~\mu$m siamo a
$4.7\sigma$: o il dato di targa ha una tolleranza, e va scritta, oppure lo
scarto va commentato.}
```

Il numero `[GS 1]` compare **sia nel testo sia sul riquadro**: e' quello che
lega la nota alla frase anche quando i riquadri scivolano in basso. Non
toglierlo.

**Per un PDF con le note di un revisore solo**, in preambolo:

```latex
\hidereviewer{CC}     % spegne un layer: niente marcatori, riquadri, elenco
```

---

## 3. Regole per non fare pasticci

1. **Non si modifica il testo della tesi.** Mai. Se una frase e' sbagliata, si
   scrive una nota. L'unica eccezione sono i comandi di layout in `preamble.tex`.
2. **Non si modificano le note di un altro revisore.** Se non sei d'accordo,
   aggiungi la tua nota accanto. Le note di MD in particolare vengono
   verificate byte per byte contro il commit `f2f3af8`.
3. **Categoria e ancora corte.** Un'ancora lunga tre righe rende il riquadro
   enorme e il legame con la frase piu' vago, non meno.
4. **Nota lunga = nota che verra' saltata.** Sopra le ~900 battute conviene
   spezzarla in due note su due frasi diverse.
5. **Ricompilare entrambi i PDF prima di committare**, perche' sono tracciati:
   `thesis_main.pdf` e `chapters/Chapter_1/chapter_1_main.pdf`.

---

## 4. Trappole LaTeX, tutte gia' incontrate

- **Mai una nota dentro `\section{}` o `\subsection{}`.** E' un argomento
  mobile: il testo della nota finisce stampato nell'indice, hyperref protesta e
  la nota viene eseguita due volte. Metti la nota nella riga **dopo** il titolo.
- **Niente `\ref` o `\cite` dentro una nota.** Sono comandi fragili e l'elenco
  viene scritto su file. Cita l'etichetta come testo:
  `\texttt{eq:dipole\_force}`.
- **Le macro di MD (`\MD*`) non funzionano dentro un capoverso rimodellato da
  `wrapfig`**: `soul` si ferma con *"Reconstruction failed"*. Le macro dei
  revisori usano `ulem` e non hanno il problema; se capita a una nota di MD,
  basta spostarla di una frase.
- **L'ancora deve comparire una volta sola** nel file, altrimenti non si capisce
  a quale occorrenza ti riferisci.

---

## 5. Flusso di lavoro: un ramo per revisore

```
main                      la studentessa, non si tocca
revisione-Michelangelo    MD (+ CC)
revisione-<tuosigla>      tu
revisione-integrata       merge di tutti, e' il PDF che si manda a lei
```

**Partire:**

```bash
git fetch origin
git checkout -b revisione-GS origin/main
# aggiungi \DeclareReviewer{GS}{blue!15} in preamble.tex, scrivi le note
```

**Allineare le note al testo aggiornato della studentessa** (da rifare ogni
volta che lei pubblica su `main`):

```bash
git fetch origin && git merge origin/main
# i PDF vanno in conflitto come binari: si prende il proprio e si ricompila
git checkout --ours Master-Thesis-main/thesis_main.pdf \
                    Master-Thesis-main/chapters/Chapter_1/chapter_1_main.pdf
cd Master-Thesis-main && latexmk -pdf thesis_main.tex
```

**Produrre il PDF con le note di tutti:**

```bash
git checkout revisione-integrata
git merge revisione-Michelangelo
git merge revisione-GS
cd Master-Thesis-main && latexmk -pdf thesis_main.tex
```

I conflitti veri capitano solo dove due revisori annotano **lo stesso
capoverso**. Il modo semplice per non averne quasi mai e' dividersi i capitoli.

---

## 6. Stato delle note

```bash
python3 review/status.py             # confronto con origin/main
python3 review/status.py a3a1f66     # confronto con un commit preciso
python3 review/status.py --verbose   # elenca anche le note ancora aperte
```

Per ogni nota controlla se la frase a cui e' agganciata esiste ancora nel testo
della studentessa:

- **aperta** — quel passaggio non e' stato toccato, la nota vale ancora;
- **testo cambiato** — ha riscritto li', la nota va riletta e forse chiusa;
- **non ancorata** — note che si riferiscono ad altre note, non confrontabili.

E' l'unico "stato" che esiste, e nessuno deve aggiornarlo a mano.
