# Procedura di annotazione della tesi

Il presente documento descrive il sistema di revisione multi-revisore adottato
per questa tesi. Il sistema consente di apporre annotazioni a margine senza
modificare il testo dell'autrice e senza interferenze fra i revisori.

L'autrice non opera su questi rami: consulta il PDF annotato e prosegue la
stesura su `main`. Ne consegue che lo stato delle annotazioni non viene
dichiarato manualmente, ma determinato per confronto con `main`, secondo quanto
descritto nella Sezione 9.

---

## 1. Registrazione di un revisore

E' sufficiente una dichiarazione in `Master-Thesis-main/preamble.tex`, nella
sezione *REGISTRO DEI REVISORI*:

```latex
\DeclareReviewer{GS}{blue!15}
```

Il primo argomento e' la sigla del revisore, costituita da due lettere
maiuscole; il secondo e' il colore associato. I colori gia' assegnati sono
`teal` per CC; la colonna sinistra e' riservata a MD. Si raccomanda di
selezionare una tinta chiara e agevolmente distinguibile, quale `blue!15`,
`violet!15`, `green!20` o `yellow!25`.

La dichiarazione rende disponibile la macro `\GS`, dotata di numerazione ed
elenco autonomi.

---

## 2. Redazione di un'annotazione

```latex
\GS{categoria}{testo della tesi cui l'annotazione si riferisce}{osservazione}
```

- **Primo argomento**: la categoria, espressa da un singolo termine. Si
  utilizzino le categorie ritenute opportune, quali `errore`, `nota`, `forma`,
  `riferimenti`, `domanda`.
- **Secondo argomento**: un estratto **letterale** del testo della tesi, detto
  ancora. Viene evidenziato con sottolineatura tratteggiata e contrassegnato da
  `[GS 1]`, `[GS 2]` e successivi. Deve essere riprodotto esattamente ed e'
  preferibile che sia breve e privo di formule.
- **Terzo argomento**: l'osservazione, riportata nel riquadro a destra e
  nell'elenco *Note dei revisori*.

Esempio:

```latex
\GS{errore}{The measured waist agrees with the specified MFD}{Con
$w_{0x}=5.67\pm0.10~\mu$m contro un valore nominale di $5.2~\mu$m lo scarto e'
di $4.7\sigma$: o il dato di targa e' affetto da una tolleranza, che va
esplicitata, oppure la discrepanza va discussa.}
```

Il contrassegno `[GS 1]` compare sia nel testo sia sul riquadro e costituisce
l'unico legame fra i due quando i riquadri vengono spostati verso il basso
dalla composizione. Non va rimosso.

### Annotazioni di ambito generale

Per le osservazioni riferite a un intero capitolo o a un'intera sezione, prive
pertanto di una frase cui ancorarsi -- quali disomogeneita' di notazione,
sezioni scollegate dal resto, squilibri di trattazione o di apparato
bibliografico -- si utilizzi:

```latex
\CCgen{ambito}{titolo breve}{testo}
```

L'annotazione non e' ancorata al testo: in luogo dell'ancora compare un
contrassegno a numerazione autonoma, `[CC G1]`, `[CC G2]` e successivi, e il
riquadro assume colore giallo. Confluisce in un elenco dedicato, *Note
generali*, oltre che negli elenchi per stato.

### Annotazioni riferite all'intera tesi

Di livello superiore rispetto alle precedenti: osservazioni che non riguardano
un capitolo bensi' il documento nel suo complesso, quali l'equilibrio fra le
parti, l'assenza di elenchi, materiale non incluso o l'interruzione di un filo
argomentativo.

```latex
\CCthesis{titolo breve}{testo}
```

Numerazione `[CC T1]`, colore azzurro, elenco dedicato. Si mantengono distinte
dalle annotazioni generali in quanto destinate a una lettura in momento
diverso: non durante la revisione di un capitolo, bensi' in sede di valutazione
della struttura complessiva.

Il parametro `ambito` di `\CCgen` ne indica l'estensione: `capitolo 1`,
`sezione 1.3`, `sezioni 1.2 e 1.4`. Poiche' l'estensione e' dichiarata
nell'annotazione stessa, la collocazione nel file e' libera: si raccomanda di
inserirla **all'interno del primo capoverso** dell'area cui si riferisce, mai
immediatamente dopo un titolo, in quanto in tal caso il `\marginpar` viene
elaborato in modo verticale e LaTeX perde gli oggetti flottanti della pagina.
Qualora una pagina risulti eccessivamente affollata, l'annotazione puo' essere
spostata piu' avanti nella medesima sezione senza perdita di significato.

Per ottenere un PDF contenente le annotazioni di un solo revisore si dichiari
in preambolo:

```latex
\hidereviewer{CC}     % disattiva un livello: contrassegni, riquadri ed elenco
```

---

## 3. Norme operative

1. **Il testo della tesi non va modificato.** Qualora una frase risulti errata,
   se ne dia conto in un'annotazione. Unica eccezione ammessa sono i comandi di
   impaginazione contenuti in `preamble.tex`.
2. **Le annotazioni altrui non vanno commentate**, ne' per correggerle ne' per
   confermarle. Qualora un'annotazione altrui appaia errata, la propria si
   ancori al testo della tesi e verta su di esso, senza richiamare
   l'annotazione altrui. Le annotazioni di MD sono verificate byte per byte
   rispetto al commit `f2f3af8`.
3. **Le annotazioni recepite non vanno eliminate.** Quando l'autrice da'
   seguito a un'annotazione, questa assume colore verde, riceve il contrassegno
   `[SOLVED]` e viene integrata con l'indicazione delle modalita' con cui e'
   stata recepita, cosi' da conservare memoria di quanto richiesto e di quanto
   effettuato. Le macro relative sono `\MDnsolved{ancora}{testo
   originale}{modalita'}` e le analoghe `\MDssolved`, `\MDqsolved`,
   `\MDtsolved`, oltre a `\CCsolved{categoria}{ancora}{testo}{modalita'}`. Il
   testo originale dell'annotazione va conservato immutato nell'argomento che
   lo ospita.
4. **Categoria e ancora vanno mantenute concise.** Un'ancora estesa su piu'
   righe produce un riquadro di dimensioni eccessive e rende il legame con la
   frase meno determinato.
5. **Un'annotazione eccessivamente estesa non viene letta.** Oltre le 900
   battute circa se ne raccomanda la suddivisione in due annotazioni riferite a
   frasi distinte.
6. **Entrambi i PDF vanno ricompilati prima di ogni commit**, in quanto
   tracciati: `thesis_main.pdf` e `chapters/Chapter_1/chapter_1_main.pdf`.

---

## 4. Inserimento assistito: `addnote.py`

L'inserimento manuale delle annotazioni ha dato luogo, in piu' occasioni, a
documenti non compilabili e, in un caso, alla cancellazione di sei frasi
dell'autrice. In tutti i casi il difetto non risiedeva nel contenuto
dell'annotazione bensi' nel punto di inserimento. Si raccomanda pertanto di
effettuare gli inserimenti esclusivamente per il tramite del modulo
`review/addnote.py`:

```python
import sys; sys.path.insert(0, "review")
from addnote import place
place(percorso, [(frase, annotazione, "etichetta")])
```

Il modulo respinge l'inserimento qualora l'ancora risulti assente, ambigua,
piu' breve di quattro caratteri, contenuta in una `\caption`, in modo
matematico o gia' compresa in un'altra annotazione; qualora il corpo
dell'annotazione contenga una riga vuota, poiche' un `\par` nell'argomento
compromette la scrittura degli elenchi; e qualora il testo fornito non
contenga l'ancora, condizione che comporterebbe la cancellazione del testo
dell'autrice. Nessuna scrittura viene effettuata se anche un solo inserimento
non e' ammissibile, cosi' da non lasciare il file in stato intermedio. Le
protezioni sono verificate automaticamente su testo di prova a ogni esecuzione
di `check.py`.

Si segnala inoltre che le annotazioni vanno composte per concatenazione e non
mediante interpolazione di stringhe: i corpi contengono frequentemente il
carattere `%` in forma protetta, che interferisce con la formattazione.

---

## 5. Limitazioni note di LaTeX

- **Le annotazioni non vanno inserite in `\section{}` o `\subsection{}`.** Si
  tratta di un argomento mobile: il testo dell'annotazione verrebbe riprodotto
  nell'indice, hyperref segnalerebbe un errore e l'annotazione verrebbe
  elaborata due volte. La si collochi nella riga successiva al titolo.
- **`\ref` e `\cite` non vanno impiegati all'interno di un'annotazione**, in
  quanto comandi fragili e in quanto l'elenco viene scritto su file. Si citi
  l'etichetta come testo: `\texttt{eq:dipole\_force}`.
- **Le macro di MD (`\MD*`) non operano correttamente in un capoverso
  rimodellato da `wrapfig`**: il pacchetto `soul` interrompe l'elaborazione con
  il messaggio *"Reconstruction failed"*. Le macro dei revisori impiegano
  `ulem` e non presentano tale limitazione; qualora il problema interessi
  un'annotazione di MD, e' sufficiente spostarla di una frase.
- **L'ancora deve comparire una sola volta nel file**, in difetto di che
  l'occorrenza cui l'annotazione si riferisce risulta indeterminata.
- **Le ancore devono avere estensione di almeno alcune parole.** Un'ancora di
  uno o due caratteri si aggancia alla prima occorrenza disponibile, che puo'
  trovarsi nel corpo di un'altra annotazione o in una didascalia, con
  conseguente impossibilita' di compilazione del documento.
- Successivamente a ogni riposizionamento si esegua il controllo strutturale:

```bash
python3 review/status.py --lint
```

---

## 6. Organizzazione dei rami

```
main                      autrice, non va modificato
revisione-Michelangelo    MD (e CC)
revisione-<sigla>         revisore
revisione-integrata       unione di tutti i rami, PDF trasmesso all'autrice
```

Inizializzazione:

```bash
git fetch origin
git checkout -b revisione-GS origin/main
# dichiarare \DeclareReviewer{GS}{blue!15} in preamble.tex e redigere le note
```

Produzione del PDF integrato:

```bash
git checkout revisione-integrata
git merge revisione-Michelangelo
git merge revisione-GS
cd Master-Thesis-main && latexmk -pdf thesis_main.tex
```

Si verificano conflitti sostanziali soltanto qualora due revisori annotino il
medesimo capoverso; la ripartizione dei capitoli fra i revisori li rende
pressoche' inesistenti.

---

## 7. Procedura di aggiornamento

Da eseguirsi a ogni pubblicazione dell'autrice su `main`:

```bash
git fetch origin
python3 review/resolved.py                    # 1. annotazioni da rileggere
git merge origin/main                         # 2. acquisizione del nuovo testo
python3 review/reanchor.py                    #    esecuzione in sola lettura
python3 review/reanchor.py --apply            # 3. riancoraggio delle annotazioni
bash review/build.sh                          # 4. ricompilazione dei due PDF
python3 review/check.py                       # 5. verifica finale
```

**1. `resolved.py`.** Da eseguirsi prima del merge, quando il confronto fra la
versione precedentemente revisionata e quella nuova e' ancora possibile.
Individua le annotazioni tuttora aperte il cui contesto sia stato modificato
dall'autrice. Se ne veda la motivazione nella Sezione 9.

**2. Il merge.** I due PDF danno luogo a conflitto in quanto file binari; si
adotti la propria versione e si proceda alla ricompilazione.

```bash
git checkout --ours Master-Thesis-main/thesis_main.pdf \
                    Master-Thesis-main/chapters/Chapter_1/chapter_1_main.pdf
```

**3. `reanchor.py`.** Il ramo dell'autrice non contiene annotazioni; ogni
conflitto oppone pertanto il testo nuovo privo di annotazioni al testo
precedente che le contiene. Lo strumento conserva in ogni caso il testo
dell'autrice e riancora le annotazioni. Non effettua inserimenti in una
`\caption` ne' negli argomenti di un'altra annotazione, e respinge le ancore di
estensione inferiore a quattro caratteri. Le annotazioni prive di ancora
utilizzabile vengono riancorate al contesto che le precedeva. Le annotazioni la
cui ancora non risulti piu' reperibile sono elencate come **orfane** e
corrispondono ai passaggi effettivamente riscritti: vanno rilette singolarmente
e, qualora l'autrice abbia dato seguito all'osservazione, contrassegnate come
recepite secondo la norma 3.

**4. `build.sh`.** Rimuove `.lof`, `.tdo`, `.cco` e `.aux` prima di ogni
compilazione. La rimozione e' necessaria in quanto latexmk rilegge tali file e,
qualora una compilazione precedente si sia interrotta, segnala errori non
presenti nel sorgente.

**5. `check.py`.** Esegue ventuno controlli secondo il criterio per cui **la
verifica va condotta sul PDF e non sul sorgente**: una compilazione priva di
errori non fornisce alcuna informazione sulla corretta collocazione delle
annotazioni. Verifica che tutte le annotazioni siano presenti nel PDF, che
contrassegno e riquadro compaiano sulla medesima pagina, che nulla risulti
troncato ai margini, che il blocco di testo della tesi sia rimasto invariato
(702.78 pt), che le annotazioni di MD siano integralmente presenti e non
alterate, che non siano state commentate annotazioni altrui e che non
sussistano annotazioni annidate o collocate in didascalie. Restituisce codice
di uscita diverso da zero in caso di esito negativo ed e' pertanto impiegabile
in un hook.

---

## 8. Elenchi delle annotazioni

In apertura del documento, e in apertura del PDF del solo Capitolo 1, sono
riportati un prospetto riepilogativo e sei elenchi, corrispondenti al medesimo
insieme di annotazioni ordinato secondo due criteri distinti.

| elenco | contenuto |
|---|---|
| **Todo list** | annotazioni di MD, elenco `todonotes` |
| **Note dei revisori** | annotazioni di CC e degli altri revisori |
| **Note generali** | annotazioni riferite a un capitolo o a una sezione |
| **Note sulla tesi** | annotazioni riferite al documento nel suo complesso |
| **Note aperte** | annotazioni non ancora recepite, di qualunque revisore |
| **Note risolte** | annotazioni recepite, con indicazione delle modalita' |

I primi due elenchi ordinano per LIVELLO, ossia per autore; gli ultimi due per
STATO. Ogni annotazione compare pertanto in due elenchi. Il prospetto in
apertura riporta i totali, desunti dal file `.aux` e quindi corretti a partire
dalla seconda compilazione.

L'aggiunta di un ulteriore elenco richiede due sole dichiarazioni: una macro
che scriva mediante `\notelistentry{<estensione>}{...}` e un
`\@starttoc{<estensione>}`.

---

## 9. Determinazione dello stato delle annotazioni

```bash
python3 review/status.py             # confronto con origin/main
python3 review/status.py a3a1f66     # confronto con una revisione determinata
python3 review/status.py --verbose   # comprensivo delle annotazioni aperte
python3 review/status.py --lint      # soli controlli strutturali
python3 review/resolved.py           # annotazioni aperte su testo modificato
```

`status.py` verifica, per ciascuna annotazione, la persistenza nel testo
dell'autrice della frase cui essa e' ancorata:

- **aperta** — il passaggio non e' stato modificato e l'osservazione conserva
  validita';
- **testo modificato** — il passaggio e' stato riscritto e l'annotazione va
  riletta ed eventualmente chiusa;
- **non ancorata** — annotazioni prive di ancora, non confrontabili.

Tale verifica presenta una limitazione rilevante, documentata da un caso
concreto: qualora l'autrice recepisca un'osservazione **senza modificare la
frase ancorata** -- ad esempio integrando una sigla immediatamente dopo
l'ancora, oppure inserendo altrove un rimando a figura -- l'ancora sopravvive e
l'annotazione risulta tuttora aperta pur essendo stata recepita. In una singola
occasione otto annotazioni si sono trovate in tale condizione.

A tale limitazione supplisce `resolved.py`, che confronta il **contesto**
anziche' l'ancora: per ciascuna annotazione aperta individua la frase nel testo
di riferimento e in quello nuovo e ne raffronta il seguito immediato. Le
annotazioni per le quali il seguito risulti modificato vanno rilette. Lo
strumento va eseguito dopo il fetch e prima del merge; a merge avvenuto il
confronto non e' piu' significativo.

---

## 10. Misurazione preliminare dei dati numerici

Un'annotazione che riporti un dato numerico -- quale il numero di parole di un
capitolo o il numero di sigle distinte -- va redatta sulla base di una
misurazione condotta sul testo dell'**autrice** e non sui file annotati.

```bash
python3 review/measure.py              # su origin/main
python3 review/measure.py c977f7c      # a una revisione determinata
python3 review/measure.py --acronyms   # con l'elenco delle sigle
```

La misurazione condotta sui file annotati includerebbe le annotazioni stesse;
la loro rimozione mediante espressione regolare non e' praticabile, in quanto i
corpi contengono parentesi graffe annidate ed espressioni matematiche.
L'inconveniente si e' verificato: nove dati numerici in altrettante annotazioni
sono risultati errati, con conteggi di parole sovrastimati fino al cinquanta
per cento nelle sezioni brevi e un conteggio di sigle falsato dall'inclusione
della piu' frequente nell'elenco delle esclusioni. Lo strumento acquisisce i
file da git alla revisione dell'autrice, ove le annotazioni non sono presenti.

Si raccomanda infine di ripetere la misurazione a ogni pubblicazione
dell'autrice: i dati numerici riportati nelle annotazioni aperte decadono a
ogni modifica del testo, e un'annotazione che riporti un dato non piu'
corrispondente compromette la credibilita' delle rimanenti.
