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
2. **Non si commentano le note degli altri revisori.** Ne' per correggerle ne'
   per confermarle. Se pensi che una nota altrui sia sbagliata, la tua nota si
   aggancia al TESTO DELLA TESI e parla di quello, senza citare la nota altrui.
   Le note di MD sono verificate byte per byte contro il commit `f2f3af8`.
3. **Le note risolte non si cancellano.** Quando la studentessa da' seguito a
   una nota, quella nota diventa verde, prende il tag `[SOLVED]` e guadagna una
   riga che dice COME e' stata risolta. Cosi' resta la storia di cosa e' stato
   chiesto e di cosa e' stato fatto. Le macro sono
   `\MDnsolved{ancora}{testo originale}{come}`, e analoghe `\MDssolved`,
   `\MDqsolved`, `\MDtsolved`, piu' `\CCsolved{categoria}{ancora}{testo}{come}`.
   Il testo originale della nota non si tocca: sta nell'argomento di prima.
4. **Categoria e ancora corte.** Un'ancora lunga tre righe rende il riquadro
   enorme e il legame con la frase piu' vago, non meno.
5. **Nota lunga = nota che verra' saltata.** Sopra le ~900 battute conviene
   spezzarla in due note su due frasi diverse.
6. **Ricompilare entrambi i PDF prima di committare**, perche' sono tracciati:
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
- **Ancore lunghe almeno qualche parola.** Un'ancora di uno o due caratteri (una
  virgola) si aggancia alla prima occorrenza che trova, che puo' benissimo
  essere dentro il corpo di un'altra nota o dentro una didascalia. E' gia'
  successo, e il risultato e' un documento che non compila piu'.
- Dopo ogni riposizionamento delle note, far girare il controllo strutturale:

```bash
python3 review/status.py --lint     # note annidate, note dentro \caption, ancore troppo corte
```

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

## 6. Il giro di lavoro, in quattro comandi

Ogni volta che la studentessa pubblica qualcosa su `main`:

```bash
git fetch origin && git merge origin/main     # 1. porta dentro il suo testo
python3 review/reanchor.py                    #    prova a vuoto: dice cosa farebbe
python3 review/reanchor.py --apply            # 2. riattacca le note alla sua prosa
bash review/build.sh                          # 3. ricompila i due PDF, da pulito
python3 review/check.py                       # 4. verifica che sia tutto a posto
```

**1. Il merge.** I due PDF vanno sempre in conflitto come binari: si prende il
proprio e si ricompila dopo, non serve risolverli a mano.

```bash
git checkout --ours Master-Thesis-main/thesis_main.pdf \
                    Master-Thesis-main/chapters/Chapter_1/chapter_1_main.pdf
```

**2. `reanchor.py`.** Il suo ramo non contiene le note, quindi ogni conflitto e'
``la sua prosa nuova'' contro ``la nostra prosa vecchia con le note''. Lo script
tiene sempre la SUA prosa e riattacca le note. Ha tre protezioni, tutte nate da
errori veri: non inserisce mai dentro una `\caption`, mai dentro gli argomenti
di un'altra nota, e rifiuta le ancore di meno di quattro caratteri.
Le note la cui ancora non esiste piu' vengono elencate come **orfane**: sono i
punti in cui lei e' intervenuta. Vanno rilette una per una e, se ha dato seguito
alla nota, rimesse in verde con il tag `[SOLVED]` (vedi la regola 3).

**3. `build.sh`.** Cancella sempre `.lof`, `.tdo`, `.cco` e `.aux` prima di
compilare. Non e' pedanteria: latexmk rilegge quei file, e se una compilazione
e' fallita a meta' quella dopo segnala errori che nel sorgente non ci sono.

**4. `check.py`.** Quattordici controlli, e il criterio e' che **si misura il
PDF, non il sorgente**: una compilazione pulita non dice nulla su quante note
siano finite nella pagina giusta. Verifica che tutte le note siano nel PDF, che
marcatore e riquadro stiano sulla stessa pagina, che niente sia tagliato ai
bordi, che il blocco di testo della tesi sia rimasto quello originale
(702.78 pt), che le note di MD siano tutte presenti e non alterate, che nessuno
abbia commentato le note altrui, e che non ci siano note annidate o dentro le
didascalie. Esce diverso da zero se qualcosa non va, quindi si puo' mettere in
un hook.

---

## 7. Gli elenchi delle note

In testa al documento (e in testa al PDF del solo capitolo 1) ci sono un
riepilogo e **quattro elenchi**, che sono lo stesso insieme di note guardato in
due modi diversi.

| elenco | cosa contiene |
|---|---|
| **Todo list** | le note di MD, elenco di `todonotes`, com'e' sempre stato |
| **Note dei revisori** | le note di CC e degli altri revisori |
| **Note aperte** | tutte le note ancora da lavorare, di chiunque |
| **Note risolte** | tutte quelle chiuse, con la descrizione di come |

I primi due dividono per LIVELLO (chi ha scritto), gli altri due per STATO.
Ogni nota compare quindi in due elenchi: uno per livello e uno per stato.
Il riquadro in cima riporta i totali, che vengono dall'`.aux` e sono quindi
aggiornati dalla seconda compilazione in poi (latexmk ne fa comunque piu' di una).

Per aggiungere un elenco proprio bastano due righe: una macro che scrive con
`\notelistentry{<estensione>}{...}` e un `\@starttoc{<estensione>}`.

---

## 8. Stato delle note

```bash
python3 review/status.py             # confronto con origin/main
python3 review/status.py a3a1f66     # confronto con un commit preciso
python3 review/status.py --verbose   # elenca anche le note ancora aperte
python3 review/status.py --lint      # solo i controlli strutturali
```

Per ogni nota controlla se la frase a cui e' agganciata esiste ancora nel testo
della studentessa:

- **aperta** — quel passaggio non e' stato toccato, la nota vale ancora;
- **testo cambiato** — ha riscritto li', la nota va riletta e forse chiusa;
- **non ancorata** — note che non si agganciano a una frase, non confrontabili.

Attenzione a un limite: se lei risolve una nota **senza toccare la frase
ancorata** (per esempio aggiungendo altrove il rimando a una figura), lo
strumento la vede ancora ``aperta''. Lo stato automatico e' un aiuto, non un
sostituto della rilettura.
