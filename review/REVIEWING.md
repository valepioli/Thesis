# Procedura di annotazione di una tesi

Questo documento descrive una procedura di revisione multi-revisore per un
elaborato composto in LaTeX e versionato con git. È stata sviluppata per una
tesi magistrale, ma non dipende da quel contenuto: si applica a qualunque
documento in cui più revisori debbano annotare un testo che l'autore continua
a modificare.

Il presupposto è la separazione dei ruoli. L'autore lavora sul proprio ramo,
dove le annotazioni non esistono; ciascun revisore lavora su un ramo distinto e
non modifica il testo. L'autore riceve un PDF annotato e prosegue la stesura.
Ne consegue che lo stato di un'annotazione non viene dichiarato manualmente da
nessuno, ma determinato per confronto fra i due rami, secondo quanto descritto
nella Sezione 8.

Il documento distingue le **norme**, la cui inosservanza produce un documento
difettoso o comporta la perdita di lavoro, dalle **raccomandazioni**, che
migliorano la leggibilità e la tenuta della revisione ma la cui inosservanza
non pregiudica il risultato.

---

## 1. Registrazione di un revisore

È sufficiente una dichiarazione nel preambolo, nella sezione *REGISTRO DEI
REVISORI*:

```latex
\DeclareReviewer{GS}{blue!15}
```

Il primo argomento è la sigla del revisore, costituita da due lettere
maiuscole; il secondo è il colore associato. Si raccomanda una tinta chiara e
agevolmente distinguibile, quale `blue!15`, `violet!15`, `green!20` o
`yellow!25`, e si verifichi che non sia già assegnata: un colore condiviso
vanifica la distinzione fra revisori, che è la ragione stessa del registro.

La dichiarazione rende disponibile la macro `\GS`, dotata di numerazione ed
elenco autonomi.

---

## 2. Redazione di un'annotazione

```latex
\GS{categoria}{testo cui l'annotazione si riferisce}{osservazione}
```

- **Primo argomento**: la categoria, espressa da un singolo termine. Si
  utilizzino le categorie ritenute opportune, quali `errore`, `nota`, `forma`,
  `riferimenti`, `domanda`.
- **Secondo argomento**: un estratto **letterale** del testo, detto ancora.
  Viene evidenziato con sottolineatura tratteggiata e contrassegnato da
  `[GS 1]`, `[GS 2]` e successivi. Deve essere riprodotto esattamente.
- **Terzo argomento**: l'osservazione, riportata nel riquadro a margine e
  nell'elenco delle annotazioni.

Esempio:

```latex
\GS{errore}{The measured waist agrees with the specified MFD}{Con
$w_{0x}=5.67\pm0.10~\mu$m contro un valore nominale di $5.2~\mu$m lo scarto è
di $4.7\sigma$: o il dato di targa è affetto da una tolleranza, che va
esplicitata, oppure la discrepanza va discussa.}
```

Il contrassegno `[GS 1]` compare sia nel testo sia sul riquadro e costituisce
l'unico legame fra i due quando la composizione sposta i riquadri verso il
basso. **Norma:** non va rimosso.

### Annotazioni di ambito generale

Per le osservazioni riferite a un intero capitolo o a un'intera sezione, prive
pertanto di una frase cui ancorarsi — disomogeneità di notazione, sezioni
scollegate dal resto, squilibri di trattazione o di apparato bibliografico:

```latex
\CCgen{ambito}{titolo breve}{testo}
```

L'annotazione non è ancorata: in luogo dell'ancora compare un contrassegno a
numerazione autonoma e il riquadro assume colore distinto. Confluisce in un
elenco dedicato, oltre che negli elenchi per stato.

Il parametro `ambito` ne indica l'estensione: `capitolo 1`, `sezione 1.3`,
`sezioni 1.2 e 1.4`. Poiché l'estensione è dichiarata nell'annotazione stessa,
la collocazione nel file è libera.

**Norma:** non va collocata immediatamente dopo un titolo, poiché in tal caso
il `\marginpar` viene elaborato in modo verticale e LaTeX perde gli oggetti
flottanti della pagina. **Raccomandazione:** la si inserisca nel primo
capoverso dell'area cui si riferisce; qualora una pagina risulti affollata, la
si sposti più avanti nella medesima sezione senza perdita di significato.

### Annotazioni riferite all'intero documento

Di livello superiore: osservazioni che non riguardano un capitolo bensì il
documento nel suo complesso, quali l'equilibrio fra le parti, l'assenza di
elenchi, materiale non incluso o l'interruzione di un filo argomentativo.

```latex
\CCthesis{titolo breve}{testo}
```

Numerazione, colore ed elenco propri. Si mantengono distinte dalle annotazioni
generali in quanto destinate a una lettura in momento diverso: non durante la
revisione di un capitolo, bensì in sede di valutazione della struttura
complessiva.

Per ottenere un PDF contenente le annotazioni di un solo revisore si dichiari
in preambolo:

```latex
\hidereviewer{CC}     % disattiva un livello: contrassegni, riquadri ed elenco
```

---

## 3. Norme

L'inosservanza di quanto segue produce un documento difettoso o comporta la
perdita di lavoro.

1. **Il testo dell'autore non va modificato.** Qualora una frase risulti
   errata, se ne dia conto in un'annotazione. Unica eccezione ammessa sono i
   comandi di impaginazione del preambolo, che appartengono all'apparato di
   revisione e non al testo.
2. **Le annotazioni recepite non vanno eliminate.** Quando l'autore dà seguito
   a un'annotazione, questa assume colore verde, riceve il contrassegno
   `[SOLVED]` e viene integrata con l'indicazione delle modalità con cui è
   stata recepita, così da conservare memoria di quanto richiesto e di quanto
   effettuato. Il testo originale dell'annotazione va conservato immutato
   nell'argomento che lo ospita. Le macro relative sono
   `\CCsolved{categoria}{ancora}{testo}{modalità}` e analoghe.
3. **L'ancora deve comparire una sola volta nel file**, in difetto di che
   l'occorrenza cui l'annotazione si riferisce risulta indeterminata.
4. **L'ancora deve avere estensione di almeno alcune parole.** Un'ancora di uno
   o due caratteri si aggancia alla prima occorrenza disponibile, che può
   trovarsi nel corpo di un'altra annotazione o in una didascalia, con
   conseguente impossibilità di compilazione.
5. **Nessuna annotazione all'interno di `\section{}` o `\subsection{}`.** Si
   tratta di un argomento mobile: il testo verrebbe riprodotto nell'indice,
   hyperref segnalerebbe un errore e l'annotazione verrebbe elaborata due
   volte. La si collochi nella riga successiva al titolo.
6. **Nessun `\ref` o `\cite` all'interno di un'annotazione**, in quanto comandi
   fragili e in quanto gli elenchi vengono scritti su file. Si citi l'etichetta
   come testo: `\texttt{eq:dipole\_force}`.
7. **Nessuna riga vuota nel corpo di un'annotazione**, poiché un `\par`
   nell'argomento compromette la scrittura degli elenchi.
8. **I PDF tracciati vanno ricompilati prima di ogni commit.** Un PDF non
   aggiornato è indistinguibile da uno aggiornato per chi lo riceve.

---

## 4. Raccomandazioni

Quanto segue migliora la leggibilità e la tenuta della revisione senza esserne
condizione necessaria.

1. **Categoria e ancora concise.** Un'ancora estesa su più righe produce un
   riquadro di dimensioni eccessive e rende il legame con la frase meno
   determinato, non più.
2. **Annotazioni brevi.** Oltre le 900 battute circa se ne raccomanda la
   suddivisione in due annotazioni riferite a frasi distinte: un'osservazione
   troppo estesa tende a non essere letta.
3. **Ancore prive di formule.** Un'ancora che contenga matematica è più
   soggetta a divenire irreperibile quando l'autore rielabora l'espressione.
4. **Ripartizione dei capitoli fra i revisori.** I conflitti sostanziali si
   verificano soltanto qualora due revisori annotino il medesimo capoverso.
5. **Osservazioni verificate anche quando confermano.** Segnalare che un
   passaggio è stato controllato e risulta corretto consente a chi legge di
   distinguere i rilievi dal materiale non esaminato.
6. **Aritmetica esplicita.** Un'osservazione che riporti il calcolo è
   verificabile; una che si limiti a dichiarare un disaccordo non lo è.

---

## 5. Inserimento assistito

L'inserimento manuale delle annotazioni, effettuato mediante script
estemporanei, ha dato luogo in più occasioni a documenti non compilabili e, in
un caso, alla cancellazione di sei frasi dell'autore. In ciascun caso il
difetto non risiedeva nel contenuto dell'annotazione bensì nel punto di
inserimento.

**Raccomandazione, di rilievo tale da avvicinarsi a una norma:** gli
inserimenti si effettuino per il tramite del modulo `review/addnote.py`.

```python
import sys; sys.path.insert(0, "review")
from addnote import place
place(percorso, [(frase, annotazione, "etichetta")])
```

Il modulo respinge l'inserimento qualora l'ancora risulti assente, ambigua, più
breve di quattro caratteri, contenuta in una `\caption`, in modo matematico o
già compresa in un'altra annotazione; qualora il corpo contenga una riga vuota;
e qualora il testo fornito non contenga l'ancora, condizione che comporterebbe
la cancellazione del testo dell'autore. Nessuna scrittura viene effettuata se
anche un solo inserimento non è ammissibile, così da non lasciare il file in
stato intermedio. Le protezioni sono verificate automaticamente su testo di
prova a ogni esecuzione di `check.py`.

Le annotazioni vanno composte per concatenazione e non mediante interpolazione
di stringhe: i corpi contengono frequentemente il carattere di percentuale in
forma protetta, che interferisce con la formattazione.

---

## 6. Limitazioni note di LaTeX

Oltre a quanto già indicato fra le norme:

- **Le macro basate su `soul` non operano in un capoverso rimodellato da
  `wrapfig`**: l'elaborazione si interrompe con il messaggio *"Reconstruction
  failed"*. Le macro basate su `ulem` non presentano tale limitazione; qualora
  il problema si manifesti, è sufficiente spostare l'annotazione di una frase.
- **La matematica in un titolo richiede `\texorpdfstring`**, ivi compresa
  quella contenuta nell'argomento opzionale, che è quanto confluisce nei
  segnalibri del PDF.
- Successivamente a ogni riposizionamento si esegua il controllo strutturale:

```bash
python3 review/status.py --lint
```

---

## 7. Organizzazione dei rami e procedura di aggiornamento

```
main                      autore, non va modificato
revisione-<sigla>         un ramo per revisore
revisione-integrata       unione dei rami, PDF trasmesso all'autore
```

Inizializzazione:

```bash
git fetch origin
git checkout -b revisione-GS origin/main
# dichiarare \DeclareReviewer{GS}{...} nel preambolo e redigere le annotazioni
```

Da eseguirsi a ogni pubblicazione dell'autore:

```bash
git fetch origin
python3 review/resolved.py                    # 1. annotazioni da rileggere
git merge origin/main                         # 2. acquisizione del nuovo testo
python3 review/reanchor.py                    #    esecuzione in sola lettura
python3 review/reanchor.py --apply            # 3. riancoraggio
bash review/build.sh                          # 4. ricompilazione dei PDF
python3 review/check.py                       # 5. verifica finale
```

**1. `resolved.py`.** Da eseguirsi prima del merge, quando il confronto fra la
versione precedentemente revisionata e quella nuova è ancora possibile.
Individua le annotazioni tuttora aperte il cui contesto sia stato modificato.
Se ne veda la motivazione nella Sezione 8.

**2. Il merge.** I PDF danno luogo a conflitto in quanto file binari; si adotti
la propria versione e si proceda alla ricompilazione.

```bash
git checkout --ours <percorso dei PDF tracciati>
```

**3. `reanchor.py`.** Il ramo dell'autore non contiene annotazioni; ogni
conflitto oppone pertanto il testo nuovo che ne è privo al testo precedente che
le contiene. Lo strumento conserva in ogni caso il testo dell'autore e riancora
le annotazioni. Non effettua inserimenti in una `\caption` né negli argomenti
di un'altra annotazione, e respinge le ancore di estensione inferiore a quattro
caratteri. Le annotazioni prive di ancora utilizzabile vengono riancorate al
contesto che le precedeva. Quelle la cui ancora non risulti più reperibile sono
elencate come **orfane** e corrispondono ai passaggi effettivamente riscritti:
vanno rilette singolarmente e, qualora l'osservazione sia stata recepita,
contrassegnate come tali secondo la norma 2.

**4. `build.sh`.** Rimuove i file ausiliari prima di ogni compilazione, in
quanto latexmk li rilegge e, qualora una compilazione precedente si sia
interrotta, segnala errori non presenti nel sorgente.

**5. `check.py`.** Esegue una batteria di controlli secondo il criterio per cui
**la verifica va condotta sul PDF e non sul sorgente**: una compilazione priva
di errori non fornisce alcuna informazione sulla effettiva collocazione delle
annotazioni. Verifica che tutte le annotazioni siano presenti nel PDF, che
contrassegno e riquadro compaiano sulla medesima pagina, che nulla risulti
troncato ai margini, che il blocco di testo sia rimasto invariato e che non
sussistano annotazioni annidate o collocate in didascalie. Restituisce codice
di uscita diverso da zero in caso di esito negativo ed è pertanto impiegabile
in un hook.

---

## 8. Determinazione dello stato delle annotazioni

```bash
python3 review/status.py             # confronto con origin/main
python3 review/status.py <revisione> # confronto con una revisione determinata
python3 review/status.py --verbose   # comprensivo delle annotazioni aperte
python3 review/status.py --lint      # soli controlli strutturali
python3 review/resolved.py           # annotazioni aperte su testo modificato
```

`status.py` verifica, per ciascuna annotazione, la persistenza nel testo
dell'autore della frase cui essa è ancorata:

- **aperta** — il passaggio non è stato modificato e l'osservazione conserva
  validità;
- **testo modificato** — il passaggio è stato riscritto e l'annotazione va
  riletta ed eventualmente chiusa;
- **non ancorata** — annotazioni prive di ancora, non confrontabili.

Tale verifica presenta una limitazione rilevante, documentata da un caso
concreto. Qualora l'autore recepisca un'osservazione **senza modificare la
frase ancorata** — integrando una sigla immediatamente dopo l'ancora, oppure
inserendo altrove un rimando a figura — l'ancora sopravvive e l'annotazione
risulta tuttora aperta pur essendo stata recepita. In una singola occasione
otto annotazioni si sono trovate in tale condizione.

A ciò supplisce `resolved.py`, che confronta il **contesto** anziché l'ancora:
per ciascuna annotazione aperta individua la frase nel testo di riferimento e
in quello nuovo e ne raffronta il seguito immediato. Le annotazioni per le
quali il seguito risulti modificato vanno rilette. Lo strumento va eseguito
dopo il fetch e prima del merge; a merge avvenuto il confronto non è più
significativo.

---

## 9. Misurazione preliminare dei dati numerici

**Norma:** un'annotazione che riporti un dato numerico — il numero di parole di
un capitolo, il numero di sigle distinte — va redatta sulla base di una
misurazione condotta sul testo dell'autore e non sui file annotati.

```bash
python3 review/measure.py              # su origin/main
python3 review/measure.py <revisione>  # a una revisione determinata
python3 review/measure.py --acronyms   # con l'elenco delle sigle
```

La misurazione condotta sui file annotati includerebbe le annotazioni stesse;
la loro rimozione mediante espressione regolare non è praticabile, in quanto i
corpi contengono parentesi graffe annidate ed espressioni matematiche.
L'inconveniente si è verificato: nove dati numerici in altrettante annotazioni
sono risultati errati, con conteggi di parole sovrastimati fino al cinquanta
per cento nelle sezioni brevi e un conteggio di sigle falsato dall'inclusione
della sigla più frequente nell'elenco delle esclusioni. Lo strumento acquisisce
i file da git alla revisione dell'autore, ove le annotazioni non sono presenti.

**Norma:** la misurazione va ripetuta a ogni pubblicazione dell'autore. I dati
numerici riportati nelle annotazioni aperte decadono a ogni modifica del testo,
e un'annotazione che riporti un dato non più corrispondente compromette la
credibilità delle rimanenti.

---

## 10. Elenchi delle annotazioni

In apertura del documento sono riportati un prospetto riepilogativo e più
elenchi, corrispondenti al medesimo insieme di annotazioni ordinato secondo due
criteri distinti: per **livello**, ossia per revisore, e per **stato**, ossia
aperte e recepite. Ogni annotazione compare pertanto in due elenchi. Il
prospetto riporta i totali, desunti dal file ausiliario e quindi corretti a
partire dalla seconda compilazione.

L'aggiunta di un ulteriore elenco richiede due sole dichiarazioni: una macro
che scriva mediante `\notelistentry{<estensione>}{...}` e un
`\@starttoc{<estensione>}`.
