# Base d'espècies i interaccions tròfiques per a una simulació agent-based al Parc Natural de l'Alt Pirineu

> Nota metodològica: actualment no hi ha un catàleg de vertebrats i invertebrats del Parc Natural de l'Alt Pirineu complet i accessible en línia amb totes les variables ecològiques demanades (matriu tròfica detallada i paràmetres reproductius per a totes les espècies). Per tant, aquest document proporciona (1) un conjunt de clústers funcionals de flora i artròpodes basats en espècies representatives ben documentades, i (2) un subconjunt raonat d'espècies vertebrades emblemàtiques i/o clau del parc amb informació trófica i reproductiva suficient per a calibrar un model agent-based, no una llista taxonòmica exhaustiva de les 277 espècies de vertebrats registrades.[^1][^2][^3][^4]

## 1. Clústers de plantes de l'Alt Pirineu

El parc té al voltant de 1.500–1.590 espècies de flora vascular, amb nombrosos endemismes pirinencs i espècies rares a Catalunya. Per a ús de simulació, es proposen tres subclústers funcionals amb espècies representatives.[^2][^5]

### 1.1 Plantes amb flor dependents de pol·linització externa

| Espècie (científic) | Nom comú | Hàbitat principal al PNAP | Tipus de reproducció | Fenologia / taxa de creixement |
|---------------------|----------|---------------------------|----------------------|---------------------------------|
| *Vaccinium myrtillus* | Nabiu | Boscos subalpins de pi negre, pi roig i avet amb sotabosc de nabiu, neret i boixerola.[^5][^6][^7] | Fanerògama entomòfila; pol·linització per insectes, especialment abelles i papallones; fruits dispersats per ocells i mamífers.[^8][^9] | Brotació primavera, floració de finals de primavera a inici d'estiu, fructificació estiu-tardor; és una nanofaneròfita llenyosa de creixement lent però amb alta producció anual de fulles i fruits si hi ha llum i humitat suficients.[^6][^10] |
| *Leontopodium alpinum* | Flor de neu (edelweiss) | Prats i roquissars alpins calcaris d'alta muntanya, molt localitzada però amb bones poblacions al parc.[^2][^5][^11] | Fanerògama entomòfila, pol·linització per insectes; dispersió de llavors anemòfila i per petits vertebrats.[^11] | Floració curta a l'estiu (juliol–agost) lligada a desglaç; creixement lent, planta vivace perenne adaptada a sòls pobres i climats rigorosos.[^11][^12] |
| *Astragalus penduliflorus* | Astràgal pèndul | Pastures i codines alpines dels Pirineus centrals, espècie amenaçada al PNAP.[^2][^11] | Fabàcia entomòfila; flors papilionàcies pol·linitzades per himenòpters; fixadora de nitrogen al sòl via rizobis.[^11] | Floració principal a finals de primavera i inici d'estiu; taxa de creixement baixa, planta perenne llarga vida; important per estabilitzar sòls i enriquir nitrogen.[^11][^12] |
| *Gentiana acaulis* | Genciana de flor gran | Prats alpins acidòfils de *Nardus stricta* i *Festuca* a partir de 1.700 m.[^12][^13][^14] | Fanerògama entomòfila; pol·linització per abelles i papallones; llavors dispersades pel vent i l'aigua.[^13] | Floració molt concentrada a la primavera–inici d'estiu; planta perenne de creixement lent, però que forma poblacions estables als prats poc alterats.[^12][^13] |
| *Trifolium alpinum* | Regalèssia de muntanya | Prats alpins acidòfils i mesòfils de pèl caní a 1.700–2.450 m.[^13][^12] | Fabàcia entomòfila; pol·linització per abelles; fixadora de nitrogen; important farratgera per ungulats salvatges i bestiar.[^13][^12] | Floració estiuenca; taxa de creixement mitjana-alta en sòls ben drenats; contribueix a l'acumulació de biomassa herbàcia i al rec ciclatge de nitrogen.[^13] |

### 1.2 Plantes d'autopol·linització o espores (independents)

| Espècie (científic) | Nom comú | Grup | Tipus de reproducció | Notes fenològiques |
|---------------------|----------|------|----------------------|---------------------|
| *Hippuris vulgaris* | Cua de cavall aquàtica | Planta aquàtica emergent rara al PNAP.[^2][^11] | Reproducció vegetativa per rizomes i per llavors; pol·linització sobretot hidrogama i anemòfila; baixa dependència d'insectes.[^11] | Creix en aiguamolls freds i estanys; brota a la primavera amb activitat fotosintètica alta a l'estiu; pot formar tapissos d'alta densitat que funcionen com a filtre primari.[^11][^15] |
| Pteridòfits diversos (p. ex. *Athyrium filix-femina*, *Dryopteris filix-mas*) | Falgueres de bosc | Falgueres de fondals humits i boscos de ribera i de faig/avet.[^2][^5] | Reproducció per espores; cicle amb fase gametofítica independent microscòpica; no requereixen pol·linitzadors.[^16] | Es desenvolupen a la primavera–estiu; espores dispersades a finals d'estiu; ocupen l'estrat herbaci i contribueixen a l'ombra i la retenció d'humitat del sòl.[^16] |
| Briòfits (molses de torrents i molleres) | Molses | Briòfits en roques i marges de cursos d'aigua i molleres.[^17] | Reproducció per espores (esporòfits) i propagació vegetativa; independents de pol·linitzadors animals.[^17] | Activitat durant períodes humits i frescos; colonitzen superfícies nus; importants per la retenció d'aigua i creació de microhàbitats per invertebrats.[^17] |

Per a la simulació, tot aquest grup es pot representar com un clúster de "productors independents" amb producció primària contínua però moderadament menys connectada als pol·linitzadors que el clúster anterior.

### 1.3 Plantes de creixement ràpid / recurs base (prats i pastures)

Els prats d'alta muntanya del PNAP estan dominats per gramínies i altres hemicriptòfits cespitosos com *Nardus stricta* i diverses *Festuca*, amb lleguminoses i altres herbàcies perennes associades. Aquestes comunitats sostenen grans herbívors (isard, cérvol, cabirol, mufló, daina, senglar) i bestiar.[^18][^19][^12][^13]

| Espècie (científic) | Nom comú | Rol funcional | Tipus de reproducció | Fenologia / taxa de creixement |
|---------------------|----------|----------------|----------------------|---------------------------------|
| *Nardus stricta* | Pèl caní | Gramínia dominant en prats acidòfils d'alta muntanya; forma gespa densa molt resistent a la pastura.[^12][^13] | Poàcia anemòfila, pol·linització pel vent; gran producció de llavors; també regeneració vegetativa des de soques.[^13] | Prat perenne molt longeu; rebrot basal ràpid després de la pastura o dall; màxim creixement a l'estiu; suporta trepig intens i condicions climàtiques severes.[^12][^13] |
| *Festuca eskia*, *F. airoides* i altres *Festuca* alpines | Festuques alpines | Gramínies formadores de touffes, molt abundants a prats alpins acidòfils i esglaonats.[^12] | Anemòfiles, gran producció de llavors, rebrot vegetatiu; funció similar a *Nardus*.[^12] | Creixement ràpid en temporada de bon temps; productivitat elevada però de fulla dura, base de la dieta d'isards i bestiar durant l'estiu.[^12][^20] |
| Mescla de lleguminoses (p. ex. *Trifolium repens*, *Trifolium pratense*, *Lotus corniculatus*) | Trèvols i lleguminoses pratenses | Fixadores de nitrogen en prats de dall i pastures montanes, especialment a cotes mitjanes.[^13][^21] | Entomòfiles; pol·linitzades per abelles i borinots; alta producció de llavors i capacitat d'estolonitzar.[^21] | Creixement ràpid i alt valor farratger; fenologia primavera–tardor amb pics a primavera i estiu; aporten nitrogen i milloren la qualitat del pasturatge.[^21][^12] |

En el model, aquest clúster pot representar un "pool" de biomassa herbàcia ràpidament renovable, aliment principal d'isards, cérvols, cabirols, muflons, daines i senglars.[^19][^22][^18]

## 2. Clústers d'insectes (artròpodes) del PNAP

El PNAP és un hot-spot europeu de lepidòpters: s'hi han trobat 168 espècies de papallones diürnes, prop del 82% de la fauna catalana, i al voltant de 810–910 espècies totals de papallones (diürnes i nocturnes). Les papallones s'indiquen explícitament com a pol·linitzadors i com a preses de molts vertebrats insectívors. A continuació es defineixen tres subclústers funcionals d'artròpodes basats en espècies representatives i relacions tròfiques ben descrites.[^23][^24][^8][^9]

### 2.1 Pol·linitzadors (mutualistes)

| Espècie (científic) | Nom comú | Dieta precisa | Cicle reproductiu |
|---------------------|----------|--------------|-------------------|
| *Boloria eunomia* | Donzella de la bistorta | Les erugues s'alimenten principalment de fulles de *Bistorta officinalis* (bistorta) i, en alguns ecotips, també de calluna i altres ericàcies; els adults s'alimenten sobretot de nèctar de flors de bistorta i, al final del període de vol, també de *Knautia arvensis* i altres compositees.[^25][^26][^27][^28] | Espècie de prats humits i molleres de muntanya; vol sobretot durant la primavera tardana–inici d'estiu; les femelles ponen ous sobre o a prop de la planta nutrícia; el desenvolupament larvari pot durar una temporada de creixement; hivernació com a larva; una generació anual (univoltina).[^27][^28] |
| *Parnassius mnemosyne* | Mnemòsine | Les larves s'alimenten de diverses espècies de *Corydalis* (plantes de bosc humit) i, segons àrea, també d'altres crucíferes; els adults s'alimenten de nèctar de flors de prats, com jaskres (*Ranunculus*), trèvols (*Trifolium pratense*), plantatge i altres plantes de prats rics en flors.[^29][^30][^31][^32] | Viu en mosaics de clarianes forestals i prats florits de muntanya; adults en vol a finals de primavera i principi d'estiu; les femelles dipositen ous sobre tiges seques o vegetació baixa, on passen l'hivern; larves actives a la primavera següent; una generació anual.[^29][^31][^33] |
| *Bombus spp.* (p. ex. *Bombus terrestris*, *B. pratorum*) | Borinots | Adults nectarívors i pol·linívor; utilitzen una gran varietat de flors de prats alpins i subalpins, incloent *Trifolium*, *Gentiana*, *Vaccinium*, *Nardus*-comunitats i altres; larves alimentades amb pol·len i nèctar recollit per les obreres.[^34][^13][^35] | Cicle anual: reines fecundades hivernen; funden colònies a la primavera; producció d'obreres al llarg de l'estiu; producció de noves reines i mascles a finals d'estiu; niuen en terres, esquerdes, caus abandonats; diapausa hivernal de les reines.[^35][^36] |

En el model, aquest clúster pot ser el "pollinators" amb taxa de consum de nèctar proporcional a la biomassa de plantes del subclúster 1.1 i part de 1.3.

### 2.2 Herbívors / fitòfags (plagues o consumidors primaris)

| Espècie (científic) | Nom comú | Dieta precisa | Cicle reproductiu |
|---------------------|----------|--------------|-------------------|
| Arnes defoliadores de coníferes (p. ex. *Thaumetopoea pityocampa* en zones baixes, altres geometrids de pi negre) | Erugues de processionària i similars | Erugues fitòfagues de fulles d'algunes coníferes (*Pinus* spp.), que poden debilitar el bosc; adults (papallones) no s'alimenten o s'alimenten poc de nèctar.[^6][^10] | Cicles anuals o biennals; posta d'ous sobre acícules de pi a l'estiu, desenvolupament larvari durant tardor-hivern (en processionària mediterrània) o primavera-estiu en espècies alpines; pupació al sòl; emergència d'adults a l'estiu.[^10][^37] |
| Hemípters fitòfags (p. ex. pugons en *Vaccinium*, *Nardus* i *Festuca*) | Pugons de prats i matollars | S'alimenten de saba de gramínies i nanarbusts com el nabiu i el neret; secreten melassa que pot ser utilitzada per formigues mutualistes; poden reduir el vigor de la planta.[^6][^38] | Reproducció ràpida amb generacions partenogenètiques a la primavera–estiu; alguns estadis alats dispersen colònies entre plantes; ous hivernants en teixit vegetal.[^38][^37] |
| Orthòpters (p. ex. saltamartins de prats alpins) | Saltamartins | Fitòfags generalistes de fulles de gramínies (*Nardus*, *Festuca*) i altres herbàcies de prats; poden ser una fracció apreciable del consum de biomassa foliar.[^12][^12] | Generalment un cicle anual amb ous dipositats al sòl a finals d'estiu; ninfs a la primavera; adults durant estiu; susceptibles a la predació per ocells insectívors i rèptils com la sargantana pallaresa.[^39][^39] |

Per a la simulació, aquest clúster es pot parametritzar com a "fitòfags de fulla" associats principalment al clúster 1.3 (gramínies) i en part a 1.1.

### 2.3 Depredadors / parasitoides (controladors biològics)

| Espècie (científic) | Nom comú | Dieta precisa | Cicle reproductiu |
|---------------------|----------|--------------|-------------------|
| Formigues (Fam. Formicidae; p. ex. *Formica* spp.) | Formigues de muntanya | Omnívores: consumeixen melassa de pugons, petits artròpodes, carronya i llavors; poden predar sobre larves de lepidòpters i altres insectes i també protegir pugons a canvi de melassa.[^39][^8] | Colònies perennes amb reines longeves; producció de sexuals (alats) a l'estiu; dispersió per vols nupcials; colònies sobreviuen diversos anys; activitat fonamental durant primavera–tardor.[^39][^8] |
| Himenòpters parasitoides (Ichneumonidae, Braconidae) | Vespes parasitoides de larves | Parasiten larves de lepidòpters, dípters i altres ordres; recorren el sotabosc i els prats buscant hosts; exerceixen un control densodependent sobre papallones i altres fitòfags.[^8][^9] | Varis cicles anuals segons espècie; femelles dipositen ous a l'interior o sobre larves hoste; el desenvolupament larvari mata o debilita l'hoste; pupació a l'hoste o al sòl; emergència de nous adults que repeteixen el cicle.[^8][^9] |
| Aranyes de prats i matollars (Araneae) | Aranyes | Depredadores generalistes d'insectes en prats i matollars; capturen papallones petites, mosques, pugons, saltamartins juvenils, etc.; contribueixen a limitar densitats d'artròpodes.[^38][^8] | Reproducció anual amb posta d'ous en ovisacs; juvenils dispersats a la primavera; cicle dependent de temperatura i disponibilitat de preses.[^38] |

En el model, aquest clúster es pot col·lapsar com un "compartiment regulador" que redueix l'eficiència de conversió de biomassa de fitòfags en preses per vertebrats, o bé com a taxa de mortalitat addicional dels clústers de papallones i fitòfags.

## 3. Vertebrats clau del Parc Natural de l'Alt Pirineu

El check-list oficial del PNAP recull 277 espècies de vertebrats (7 peixos, 8 amfibis, 17 rèptils, 184 ocells i 61 mamífers), però la llista detallada no és accessible en línia en format de taula completa; es disposa de llistats parcials i d'informació dispersa sobre espècies emblemàtiques i grups funcionals. A continuació es presenten espècies vertebrades representatives i/o clau per a la dinàmica tròfica del parc, amb informació trófica i reproductiva utilitzable en un model agent-based.[^40][^4][^1][^2]

### 3.1 Mamífers

#### 3.1.1 Ungulats d'alta muntanya i forestals

El conjunt d'ungulats del PNAP inclou isard pirinenc, cabirol, cérvol, mufló, daina i senglar, constituint una de les comunitats amb més espècies d'Europa. Aquests herbívors són una peça central en la transferència de biomassa dels prats i boscos cap als grans depredadors (en el cas de l'ós) i als carronyaires com el trencalòs.[^41][^2][^18][^19]

| Espècie (científic) | Nom comú | Dieta principal | Depredadors dins o prop del PNAP | Reproducció (zel, gestació/incubació, natalitat) |
|---------------------|----------|-----------------|----------------------------------|----------------------------------------------|
| *Rupicapra pyrenaica pyrenaica* | Isard pirinenc | Herbívor pastador; menja principalment gramínies i herbes dicotiledònies dels prats alpins i subalpins (p. ex. *Nardus stricta*, *Festuca* spp.), i, a l'hivern, vegetació llenyosa (pi, nabius, altres arbusts) quan les herbàcies són escasses.[^22][^42][^43][^12] | A la serralada pirinenca, els principals depredadors naturals potencials són el llop, l'ós bru i l'àguila reial, però als Pirineus actuals, amb absència quasi total de llop, les depredacions documentades recauen sobretot en l'àguila reial (sobre joves) i, en menor mesura, la guineu; l'ós pot predar individus febles ocasionalment.[^22][^42][^44][^45] | Zel a l'octubre–novembre; mascles segueixen i defensen grups de femelles.[^22][^42] Gestació d'uns 5 mesos (23–25 setmanes); naixement d'un cabrit únic a finals de maig–principis de juny.[^22][^42][^43] Les femelles arriben a la maduresa sexual cap als 2–3 anys; taxa de natalitat efectiva aproximadament 0,8–1 cria per femella reproductora i any en poblacions no sotmeses a fort estrès.[^42][^20] |
| *Cervus elaphus* | Cérvol | Herbívor ramonejador i pastador; consumeix gramínies, herbes i brots d'arbusts i arbres; pot afectar el sotabosc de boscos de pi i avet; a l'entorn del PNAP, s'alimenta de prats d'alta muntanya i clarianes forestals.[^19][^18][^46] | Potencialment pres per l'ós bru (sobretot cries o individus debilitats); els cadells poden ser depredats per la guineu i grans rapinyaires; en absència de llop, la depredació natural sobre adults és baixa i el control principal és la caça fora de zones estrictament protegides.[^41][^44][^46] | Brama i zel a finals d'estiu–tardor (setembre–octubre); gestació d'uns 8 mesos; part al maig–juny amb una cria per femella (rarament dues).[^19][^41] Maduresa sexual al voltant dels 2 anys (femelles) i més tard en mascles; taxa de natalitat efectiva entorn d'1 cérvolet per femella reproductora i any en poblacions en bon estat.[^19][^46] |
| *Capreolus capreolus* | Cabirol | Herbívor selectiu; menja brots tendres, fulles i herbes de clarianes, prats i sotabosc; molt lligat a mosaics de bosc i prats.[^19][^4] | Depredat potencialment per l'ós i, en altres zones dels Pirineus, pel llop; cries susceptibles a guineus i grans rapinyaires.[^44][^45] | Època de zel a l'estiu (juliol–agost); implantació embrionària diferida; gestació efectiva d'uns 5 mesos i part a finals de primavera (maig–juny) amb normalment dues cries per femella.[^19][^44] |
| *Sus scrofa* | Porc senglar | Omnívor; consumeix arrels, tubercles, fruits forestals (fages, glans), invertebrats del sòl i, ocasionalment, ous o polls d'ocells nidificants a terra, inclosos nius de gall fer.[^19][^46] | Pot ser atacat per l'ós; els garrins poden ser depredats per guineus i àguiles; en general, però, la regulació principal és antròpica (caça) fora del parc.[^41][^46] | Alta capacitat reproductiva; zels principalment tardorals; gestació d'uns 4 mesos; ventrades de 3–8 garrins; pot haver-hi femelles que es reprodueixen anualment o més sovint.[^19][^41] |

En un model simplificat, aquests ungulats poden agrupar-se en un clúster "grans herbívors" amb diferències paramètriques en mida corporal, taxa de consum i natalitat.

#### 3.1.2 Mamífers carnívors i omnívors clau

| Espècie (científic) | Nom comú | Dieta i matriu tròfica | Depredadors dins del PNAP | Reproducció |
|---------------------|----------|------------------------|---------------------------|-------------|
| *Ursus arctos arctos* | Ós bru | Omnívor oportunista; 75–85% de la dieta és vegetal (herbes, brots, fruits carnosos i secs com nabius, gerds, pomes, castanyes i fages) i la resta la formen carronya, insectes (sobretot formigues), mel, aus i ous, i ungulats domèstics o salvatges.[^41][^47][^44][^48] Pot depredar sobre isards, cérvols i altres ungulats, especialment cries o individus debilitats; també consumeix truites o altres peixos quan són accessibles.[^41][^44][^49] | L'adult pràcticament no té depredadors naturals al PNAP; les úniques fonts de mortalitat són humanes (cacera il·legal, col·lisions, conflictes) o accidents naturals.[^41][^50] | Femelles maduren sexualment cap als 3,5–5 anys; zels entre maig i juliol; implantació embrionària diferida; gestació efectiva de 8–10 setmanes; naixement de 1–3 cadells al gener durant la hivernació.[^41][^44] Les cries romanen amb la mare uns 18–22 mesos, de manera que la femella s'aparella cada 2–3 anys; això implica una taxa de natalitat baixa (mitjana al voltant d'1 cadell per femella cada 2–3 anys).[^41][^50] |
| *Lutra lutra* | Llúdriga | Carnívor piscívor i oportunista; consumeix principalment peixos (truita de riu *Salmo trutta* i altres ciprínids com madrilla i veró) i, en menor proporció, crancs de riu, amfibis i petits mamífers aquàtics com l'almesquera.[^51][^52][^53] | Sense depredadors naturals significatius com a adults al PNAP; cries poden ser vulnerables a grans rapinyaires o cànids en sortides terrestres.[^51][^50] | Reproducció a qualsevol època de l'any amb pics a finals d'hivern–primavera; gestació d'uns 60–64 dies; 1–3 cries per ventrada; maduresa sexual cap als 2–3 anys; en condicions òptimes pot criar anualment.[^51][^44] |
| *Galemys pyrenaicus* | Almesquera (desmàn ibèric) | Mamífer insectívor semiaquàtic; s'alimenta sobretot d'invertebrats aquàtics (larves d'insectes, cucs, mol·luscos) i ocasionalment de petits crustacis.[^15][^51] | Pot ser depredada per peixos grans (truites), llúdrigues, bernats pescaires i altres ocells piscívors; també per carnívors terrestres en trams de riu estrets.[^15][^51][^54] | Espècie amb cicle lligat a cursos d'aigua freds; reproducció generalment a la primavera amb 2–5 cries per ventrada; pot tenir 1–2 ventrades anuals; depèn fortament del manteniment del règim de cabals ecològics.[^15][^51] |
| *Martes martes* | Marta | Carnívor forestal; dieta molt oportunista: petits mamífers (micromamífers, esquirols), aus i seus ous, amfibis, invertebrats i fruits; és un depredador clau de nius de gall fer.[^55][^56][^57] | Com a adult pràcticament sense depredadors naturals al PNAP; pot ser ocasionalment presa de grans rapinyaires.[^2][^55] | Reproducció amb implantació embrionària diferida; aparellament a l'estiu (juliol–agost) i part a finals d'hivern–inicis de primavera; 2–5 cries; taxa de reclutament moderada; densitat condicionada per la disponibilitat de preses forestals.[^56][^16] |

Altres carnívors rellevants (guineu *Vulpes vulpes*, gat fer *Felis silvestris*, mostela *Mustela nivalis*, ermini *Mustela erminea*) poden incorporar-se al model com a clúster de "mesocarnívors" que depreden micromamífers, gallinàcies, amfibis i invertebrats.[^55][^4][^45]

### 3.2 Ocells

#### 3.2.1 Gallinàcies de bosc

| Espècie (científic) | Nom comú | Dieta / matriu tròfica | Depredadors al PNAP | Reproducció |
|---------------------|----------|------------------------|---------------------|-------------|
| *Tetrao urogallus* (subsp. pirenaica) | Gall fer | Adults pràcticament herbívors; a l'hivern s'alimenten sobretot d'acícules de pi negre (*Pinus uncinata*) i, en menor mesura, d'avet blanc, ginebró i altres coníferes; a la primavera–estiu la dieta incorpora brots i fruits de sotabosc com nabiu (*Vaccinium myrtillus*), boixerola (*Arctostaphylos uva-ursi*), neret i gramínies.[^6][^7][^10][^58] Els polls, en canvi, depenen fortament d'invertebrats (larves de lepidòpters, formigues, coleòpters) durant les primeres setmanes per aportar proteïna d'alta qualitat.[^6][^57][^59] | Les martes (*Martes martes*) són el principal depredador dels nius i polls; la guineu també depreda nius, especialment en zones pertorbades; senglars poden depredar nius a terra.[^55][^46][^10] | El zel i l'activitat de cantadors comencen a la primavera (març–maig) segons l'altitud; la posta té lloc poc després de les còpules; mitjana de 6–8 ous per niu amb valors típics d'aproximadament 7 ous.[^60][^61][^62] La incubació dura aproximadament 26–28 dies; els polls segueixen la mare; la supervivència de niu és molt limitada (pèrdues per depredació poden superar el 40–60% segons estudis europeus).[^62][^56] Les femelles es reprodueixen anualment, però l'èxit reproductor efectiu (polls volant per femella) és baix (2 o menys).[^62][^10] |

La perdiu xerra (*Lagopus muta*) i la perdiu blanca són altres gallinàcies d'interès, amb dietes basades en vegetació alpina i invertebrats per als polls, i depredadors similars (mustèlids, guineus, rapinyaires).[^4][^2]

#### 3.2.2 Grans rapinyaires i carronyaires

| Espècie (científic) | Nom comú | Dieta / matriu tròfica | Depredadors | Reproducció |
|---------------------|----------|------------------------|------------|-------------|
| *Gypaetus barbatus* | Trencalòs | Carronyer ossívor; s'alimenta principalment d'ossos d'ungulats domèstics i salvatges (isard, cérvol, cabirol, ovelles, cabres), que deixa caure des d'alçada sobre roques per trencar-los; també pot consumir teixits rics en medul·la i ocasionalment preses petites vives.[^63][^2][^64] | Com a depredador/carronyer apical pràcticament no té depredadors naturals; els principals riscos són antròpics (verins, col·lisions, molèsties).[^64][^2] | Espècie de vida llarga amb maduresa tardana (cap als 7–8 anys); forma parelles territorials estables; posta a l'hivern (desembre–febrer) d'1–2 ous; incubació d'uns 53–60 dies; en general només un poll arriba a volar; taxa de reproducció baixa (una cria cada 1–2 anys per parella).[^64][^2] |
| *Aquila chrysaetos* | Àguila reial | Gran depredador; consumeix principalment mamífers mitjans com isards joves, cabirols, marmotes (on n'hi ha), conills, i també aus (gallinàcies, corbs) i, ocasionalment, carronya.[^63][^22][^42][^45] | Sense depredadors naturals significatius com a adults; els polls poden ser vulnerables a competidors o humans.[^64][^44] | Parelles territorials; posta 1–3 ous a finals d'hivern–primavera; incubació al voltant de 40–45 dies; sovint només un poll sobreviu per competència fraterna; una cria per any en parelles en bon estat.[^64][^44] |

Altres rapinyaires rellevants inclouen el voltor negre, l'aufrany i el milà reial, tots ells carronyers o depredadors oportunistes que tanquen cicles tróficos sobre ungulats i altres vertebrats.[^65][^2]

### 3.3 Rèptils

| Espècie (científic) | Nom comú | Dieta | Depredadors | Reproducció |
|---------------------|----------|-------|-------------|-------------|
| *Iberolacerta aurelioi* | Sargantana pallaresa | Exclusivament entomòfaga; dieta molt variada d'artròpodes de 14 ordres diferents, amb preferència per formigues, coleòpters, heteròpters i dípters; també pot manifestar canibalisme.[^39][^66] | Pot ser depredada per rapinyaires diürns insectívors/omnivors i carnívors petits; el risc principal, però, és l'alteració d'hàbitat més que la depredació.[^39][^66] | Espècie d'alta muntanya (2.100–2.900 m) amb període d'activitat anual d'uns 4 mesos; còpules a mitjan maig–principis de juny; posta única anual d'1–4 ous aproximadament un mes després del desglaç; incubació d'un mes aproximadament; juvenils visibles de finals d'agost a la tardor; maduresa sexual als 4 anys (mascles) i 5 anys (femelles); longevitat documentada fins a 17 anys.[^39][^66][^67] |

Altres rèptils del parc inclouen diferents serps i sargantanes de menor interès tròfic macroescala, però que poden formar part d'un clúster "rèptils insectívors" que consumeix artròpodes i ocasionalment amfibis juvenils.[^68][^69]

### 3.4 Amfibis

| Espècie (científic) | Nom comú | Dieta | Depredadors | Reproducció |
|---------------------|----------|-------|-------------|-------------|
| *Calotriton asper* | Tritó pirinenc | S'alimenta de petits mol·luscos, crustacis i larves d'insectes aquàtics; és un depredador important d'invertebrats en torrents i basses fredes de muntanya.[^54][^70][^71] | Un dels seus principals depredadors és la truita de riu (*Salmo trutta*); també pot ser depredat per altres peixos introduïts i ocells aquàtics.[^54][^71][^72] | Cria a finals de primavera i principis d'estiu en aigües fredes i ben oxigenades; la femella col·loca els ous sota pedres o en substrat submergit; les larves neixen al cap d'un mes i triguen entre 1 i 2 anys a completar la metamorfosi; alta fidelitat a masses d'aigua concretes.[^54][^70][^73] |
| *Rana temporaria* | Granota roja | Insectívora generalista; menja invertebrats aquàtics i terrestres; pot consumir larves de mosquits, cucs i altres petits invertebrats.[^73] | Depredada per truites, altres peixos, ocells piscívors i carnívors de ribera; els capgrossos poden ser consumits per invertebrats aquàtics i peixos.[^54][^71] | Espècie d'alta muntanya amb posta massiva a la primavera en basses i tolls; desenes a centenars d'ous per posta; desenvolupament larvari variable segons temperatura; important font de biomassa per a predadors aquàtics.[^73][^54] |

### 3.5 Peixos (clúster unificat)

La llista de peixos del PNAP inclou set espècies: truita de riu, truita irisada, salmó de font (truita de rierol), madrilla, veró, gardí i tenca. Diversos estanys d'alta muntanya del PNAP i entorns presenten peixos introduïts, principalment salmònids.[^72][^52][^1]

| Espècie (científic) | Nom comú | Dieta | Depredadors | Reproducció |
|---------------------|----------|-------|-------------|-------------|
| *Salmo trutta* | Truita de riu autòctona | Depredador aquàtic; menja invertebrats aquàtics (larves d'efemeròpters, plecòpters, tricòpters), crustacis, i, a mida gran, també peixos petits i amfibis com el tritó pirinenc; pot consumir també capgrossos i granotes.[^54][^72][^52][^53] | Depredada per llúdriga, bernats pescaires, altres ocells piscívors i, potencialment, per l'ós quan pesca en rius.[^51][^54][^53] | A rius de muntanya com la Noguera Pallaresa, la truita remunta cada any els cursos per fresar (posar els ous) als trams cabalosos i ben oxigenats de capçalera; la fresa té lloc generalment a finals de tardor–hivern; ous en graves; eclosió a la primavera; longevitat alta en rius freds (fins a 10–11 anys documentats a la Noguera Pallaresa).[^49][^74][^75] |
| *Phoxinus* spp. | Barb roig / veró | Omnívor de petits invertebrats, algues i matèria orgànica; en estanys d'alta muntanya introdueix una pressió addicional sobre invertebrats i amfibis.[^72][^52] | Depredat per truites i llúdrigues; també per ocells piscívors en aigües somes.[^72][^52] | Reproducció a la primavera–estiu en aigües somes; posta sobre substrats de grava o vegetació aquàtica; diverses posades per temporada; pot assolir densitats molt elevades en estanys amb impactes importants sobre les xarxes tròfiques.[^72][^52] |

En un model agent-based, tots els peixos poden agrupar-se en dos subclústers funcionals: (1) salmònids depredadors de macroinvertebrats i amfibis, i (2) ciprínids/peixos petits amb dieta més omnívora.

## 4. Esquema de mapping funcional per al model agent-based

Per a facilitar la implementació, es proposa associar cada espècie o grup representatiu als clústers funcional que el model utilitzarà:

- Productors:
  - Clúster P1 (plantes entomòfiles de sotabosc i prats florits): *Vaccinium*, *Leontopodium*, *Astragalus*, *Gentiana*, *Trifolium* i altres fanerògames dependents de pol·linitzadors.[^6][^11][^12][^2]
  - Clúster P2 (productors independents): falgueres, briòfits, plantes aquàtiques com *Hippuris*.[^11][^17]
  - Clúster P3 (prats i pastures de creixement ràpid): *Nardus*, *Festuca* spp., lleguminoses pratenses, altres gramínies d'alta muntanya.[^12][^13]

- Consumidors primaris invertebrats:
  - Clúster I1 (pol·linitzadors mutualistes): papallones diürnes clau (*Boloria eunomia*, *Parnassius mnemosyne*), borinots i altres insectes pol·linitzadors.[^25][^29][^8][^23]
  - Clúster I2 (fitòfags): erugues defoliadores de coníferes, pugons, saltamartins; lligats principalment a P1 i P3.[^38][^6][^12]
  - Clúster I3 (depredadors/parasitoides): formigues, aranyes, himenòpters parasitoides.[^39][^8][^38]

- Consumidors vertebrats:
  - Clúster V-herbívors: isard, cérvol, cabirol, daina, mufló, senglar, que consumeixen principalment P3 i, en menor grau, P1.[^22][^46][^19]
  - Clúster V-omnivors/carnívors de bosc: ós, guineu, marta, gat fer, que connecten recursos vegetals (fruits, carronya) i preses animals (ungulats, micromamífers, gallinàcies).[^44][^41][^55]
  - Clúster V-aqüàtics: llúdriga, almesquera, truites (*Salmo trutta*), barb roig, tritó pirinenc, granota roja, que estructuren la xarxa tròfica fluvial.[^15][^51][^54][^70][^72]
  - Clúster V-ocells insectívors/herbívors: gall fer, perdius, petites passeriformes de bosc i prats (piula, merla d'aigua, etc.), que controlen artròpodes i consumeixen fruits i llavors.[^76][^7][^6]
  - Clúster V-rapinyaires/carronyers: trencalòs, àguila reial, voltors i altres, que aprofiten carronya d'ungulats i altres vertebrats.[^63][^64][^2]

Aquest esquema permet parametritzar fluxos energètics calòrics entre clústers, mantenint alguns vertebrats emblemàtics diferenciats per a anàlisis de conservació.

---

## References

1. [El Parc de l'Alt Pirineu comptabilitza 277 espècies diferents de ...](https://www.radioseu.cat/noticies/el-parc-de-lalt-pirineu-comptabilitza-277-espacies) - El darrer any s'ha incorporat vuit tipus d'animals nous i se n'ha eliminat un

2. [Vint anys de la creació del Parc, Natural de l'Alt Pirineu, l'espai protegit més extens de Catalunya](https://www.comarquesdeponent.com/articulo/documentals/parc-natural-lalt-pirineu/20230817083202070469.html) - El territori del parc natural s'estén des dels 650 metres d'altitud del santuari d'Arboló, al l'extr...

3. [Flora i fauna del Parc Natural Alt Pirineu](https://www.brauedicions.cat/es/libro/flora-i-fauna-del-parc-natural-alt-pirineu_156789/) - Les primeres guies de parc natural on estan representades les espècies més comunes i singulars d'ani...

4. [Flora i fauna](http://valldecardos.cat/mobile/la-vall-de-cardos/flora-i-fauna/)

5. [PARC DE L'ALT PIRINEU - grannord](https://grannord.wordpress.com/parc-alt-pirineu/) - El Parc Natural de l'Alt Pirineu és un parc natural creat per la Generalitat ... La flora del territ...

6. [[PDF] Anàlisi de la interacció entre la gestió forestal i el gall fer (Tetrao ...](https://ddd.uab.cat/pub/tfg/2017/187474/TFG_AlinyaGallFer.pdf) - Boixerola. - Importància per l'alimentació del gall fer, quan no hi ha nabiu. - La boixerola es trob...

7. [Gall fer comú - Viquipèdia, l'enciclopèdia lliure](https://ca.wikipedia.org/wiki/Gall_fer_com%C3%BA)

8. [El Parc de l'Alt Pirineu, entre les zones amb més diversitat de ...](https://www.radioseu.cat/noticies/el-parc-de-lalt-pirineu-entre-les-zones-amb-mes-diversitat-de-papallones-deuropa) - Hi ha censades 910 espècies diferents, el 61% de les catalogades a Catalunya. El museu temàtic que h...

9. [L'Alt Pirineu és una de les zones amb més diversitat de papallones d'Europa](https://www.descobrir.cat/noticies/l-alt-pirineu-es-una-de-les-zones-amb-mes-diversitat-de-papallones-d-europa-3598_303598_102.html) - Al Parc Natural hi ha censades més de 900 espècies, el 61% de les catalogades al Principat

10. [5](https://cerdanya.org/wp-content/uploads/2020/04/gall_fer.pdf)

11. [[PDF] Orsis 24_2.qxp - RACO](https://www.raco.cat/index.php/Orsis/article/download/181222/233873)

12. [[PDF] Els prats alpins als Pirineus catalans](https://www.raco.cat/index.php/Atzavara/article/download/436841/531254)

13. [36c Prats de pèl caní (Nardus stricta) o de](http://www.gencat.cat/mediamb/habitats/fitxespdf/mill36c.pdf)

14. [Prats Alpins dels Nivells Culminals - Flora - Natura al Berguedà](http://www.naturabergueda.com/Flora/Paisatges_vegetals/Prats_Alpins_dels_Nivells_Culminals-76.htm) - Per damunt d'aquests estatges forestals, hi trobem els prats alpins dels nivells culminals (Festudio...

15. [Bestiari fòssil - Mostrant articles per etiqueta: Paleozoic](https://bestiarifossil.icp.cat/index.php/jaciments/itemlist/tag/Paleozoic)

16. [[PDF] Reptes per preservar els boscos madurs a Catalunya](https://ichn2.iec.cat/pdf/Boscos_madurs_Catalunya.pdf) - el Parc Natural del Cadí, el Parc Natural de l'Alt Pirineu, la Diputació de ... forats de la qual al...

17. [Resum d'actuacions i activitats - Parc Natural de l'Alt Pirineu](https://mediambient.repositori.gencat.cat/bitstream/handle/20.500.14343/241/2024_MB_PNAltPirineu.pdf?sequence=1)

18. [Parc Natural de l'Alt Pirineu](https://campingscat.com/ca/que-fer-catalunya/parcs-naturals/parc-natural-alt-pirineu/) - Propostes que no et pots perdre abans de visitar el Parc Natural de l'Alt Pirineu: rutes, què fer, c...

19. [Els ungulats de la Reserva - La brama del cérvol](https://www.bramaaltpallars.cat/ungulats-reserva/) - Per ungulats entenem aquells mamífers que tenen peülla i d'aquests, a la RNC de l'Alt Pallars (i al ...

20. [La alimentación del sarrio en el Pirineo central](https://digital.csic.es/handle/10261/36788) - 21 páginas, 5 figuras, 2 tablas.

21. [La vegetació de la nostra comarca - Prats i pastures](https://sites.google.com/site/vegetaciodelsolsones/sabeu-que/els-ecosistemes/prats-i-pastures) - Un prat és una formació vegetal formada només per plantes herbàcies (només per herba). Un prat pot s...

22. [Isard pirinenc - Viquipèdia, l'enciclopèdia lliure](https://ca.wikipedia.org/wiki/Isard_pirinenc)

23. [Presentem la Guia i Pòster de les Voliaines i Plantes ...](https://www.catalanbms.org/ca/noticies/presentem-la-guia-i-poster-de-les-voliaines-i-plantes-de-prats-de-pastura-de-l-alt-pirineu/)

24. [Descobertes a l'alt Pirineu dues espècies de papallones mai vistes ...](https://www.3cat.cat/3catinfo/descobertes-a-lalt-pirineu-dues-especies-de-papallones-mai-vistes-a-catalunya/noticia/2990022/) - Les dues noves espècies de micropapallones localitzades al Parc Natural de l'Alt Pirineu mesuren men...

25. [Bistorta - Viquipèdia, l'enciclopèdia lliure](https://ca.wikipedia.org/wiki/Polygonum_bistorta)

26. [Lepidoptera Mundi](https://lepidoptera.eu/species/38) - Lepidoptera Mundi - description

27. [European Lepidoptera and their ecology: Boloria eunomia - Pyrgus.de](http://www.pyrgus.de/Boloria_eunomia_en.html) - Ecology, conservation and threats of Boloria eunomia. Species page, life cycle and photos.

28. [Boloria eunomia (Esper, 1799) (Randring-Perlmuttfalter)](http://www.pyrgus.de/Boloria_eunomia.html) - �kologie, Schutz und Gef�hrdung von Boloria eunomia. Artportrait, Beschreibung des Lebenszyklus und ...

29. [Parnassius mnemosyne - Butterflies of Europe - Naturalis](https://butterflies-europe.linnaeus.naturalis.nl/linnaeus_ng/app/views/species/taxon.php?id=114551&epi=162)

30. [Parnassius mnemosyne – Niepylak mnemozyna](https://insektarium.net/lepidoptera-2/papilionidae-paziowate/parnassius-mnemosyne-niepylak-mnemozyna/) - Papilionidae – Paziowate Skrzydła białe z czarnymi żyłkami. Na przednim skrzydle dwie czarne plamy. ...

31. [Parnassius mnemosyne (Linnaeus, 1758)](http://www.pyrgus.de/Parnassius_mnemosyne_en.html) - Ecology, conservation and threats of Parnassius mnemosyne. Species page, life cycle and photos.

32. [Presentem la Guia i Pòster de les Voliaines i Plantes de prats de ...](https://www.catalanbms.org/en/noticies/presentem-la-guia-i-poster-de-les-voliaines-i-plantes-de-prats-de-pastura-de-l-alt-pirineu/) - El 2022 el Museu de Ciències Naturals de Granollers ha impulsat un estudi amb el Parc Natural de l'A...

33. [Lepidòpters - Museu de Ciències Naturals de Granollers](https://mcng.cat/blog/categoria/lepidopters) - Un nou indicador de papallones de prats i boscos, basat en les preferències d'hàbitat de les espècie...

34. [Prats alpins](https://www.catalanbms.org/ca/habitats/23/)

35. [[PDF] PIPOL Plà Intersectorial de conservació dels Pol.linitzadors ... - Gencat](https://mediambient.repositori.gencat.cat/bitstream/handle/20.500.14343/2951/2024_pipol_polinitzadors_silvestres.pdf?sequence=1&isAllowed=y) - ... Alt Pirineu. 04. IMPLICACIÓ DE LA SOCIETAT. 33. Page 34. Resultats esperats a ... matrius relaci...

36. [Pla Intersectorial de Conservació Dels Pol Linitzadors Silvestres de ...](https://www.scribd.com/document/877587339/Pla-intersectorial-de-conservacio-dels-pol-linitzadors-silvestres-de-Catalunya-Pipol) - ... Alt Pirineu. IMPLICACIÓ DE LA SOCIETAT | OBJECTIU ESTRATÈGIC 1 OE1. Divulgar i educar sobre la i...

37. [[PDF] Les papallones com a bioindicadores dels hàbitats a Catalunya](https://publicacions.iec.cat/repository/pdf/00000039/00000085.pdf)

38. [[PDF] informe sobre l'estat i les tendències del medi natural a catalunya](https://defensapatrimoninatural.wordpress.com/wp-content/uploads/2014/03/infmn-ichn_2010.pdf) - Jordi Palau (Parc Natural de l'Alt Pirineu);. Jordi Sànchez (Submon);. Jordina ... riquesa d'especia...

39. [La sargantana pallaresa](https://www.enciclopedia.cat/historia-natural-dels-paisos-catalans/la-sargantana-pallaresa) - Àrea de distribució de la sargantana pallaresa (Iberolacerta aurelioi) als Països Catalans. Estudis ...

40. [Parque Natural de l'Alt Pirineu](https://gl.wikipedia.org/wiki/Parque_Natural_de_l'Alt_Pirineu)

41. [[PDF] ATACS D´ÓS BRU (URSUS ARCTOS) A CATALUNYA - ADLO Pirineo](https://www.adlopirineo.org/docuteca/atacosbru.pdf) - conservació de l'ós bru al Pirineu central català. Aquest projecte té un pressupost de 2,5 milions d...

42. [Rupicapra pyrenaica Bonaparte, 1845](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/inventarios-nacionales/ieet_mami_rupicapra_pyrenaica_tcm30-99875.pdf)

43. [Isard](https://www.enciclopedia.cat/historia-natural-dels-paisos-catalans/isard) - El dimorfisme sexual de l’isard (Rupicapra rupicapra) afecta la forma de les banyes, més gruixudes i...

44. [Os bru](https://www.enciclopedia.cat/historia-natural-dels-paisos-catalans/os-bru) - L’os bru (Ursus arctos) és inconfusible per les seves grans dimensions, ja que és el més gran dels c...

45. [Fauna salvatge dels Pirineus](https://www.turismefgc.cat/blog/la-fauna-salvatge-del-pirineu/) - Descobreix les diferents races de la fauna salvatge dels Pirineus

46. [Intensifiquen les accions per frenar la davallada de ...](https://lesvegueries.cat/comarques-centrals/bergueda/intensifiquen-les-accions-per-frenar-la-davallada-de-poblacio-de-gall-fer-a-catalunya-una-especie-en-perill-dextincio) - Només queden 800 exemplars de gall fer a Catalunya. L'espècie, en perill d'extinció, en els darrers ...

47. [10 Qüestions sobre l'ós bru - Pirineu - Depana](https://depana.org/que-fem/ambit-territorial/pirineu/seguiment-de-los-bru/10-questions-sobre-los/) - La precària situació de la ramaderia no s'ha degut a l'ós bru, sinó a raons conjunturals (polítiques...

48. [Microsoft Word - MOSTRA ANIMALS.docx](https://www.molloparc.com/wp-content/uploads/2017/10/Fitxa-Os-bru-Mollo%CC%81-Parc.pdf)

49. [Troben una truita gegant de 7 quilos a la Noguera Pallaresa](https://www.3cat.cat/324/troben-una-truita-gegant-de-7-quilos-a-la-noguera-pallaresa/noticia/2648908/) - Feia més de trenta anys que no es localitzava una truita autòctona d'aquesta mida a Catalunya

50. [L'os bru als Pirineus: passat, present i futur](https://accioclimatica.bibliotecadigital.gencat.cat/handle/20.500.14343/716?locale-attribute=es) - Oso pardo--Pirineo catalán (Cataluña); Osos pardos (Animales)--Protección; Coexistencia animales y h...

51. [Quines accions es duen a terme per protegir hàbitats i espècies dels Pirineus i els Alps? | CEAB](https://www.ceab.csic.es/quines-accions-es-duen-a-terme-per-protegir-habitats-i-especies-dels-pirineus-i-els-alps/) - És una de les preguntes a les que respon el primer fulletó del LIFE RESQUE ALPYR. Editat en sis idio...

52. [Com s'eliminen els peixos introduïts en estanys d'alta muntanya per restaurar-los?](https://www.prisma-tic.cat/ca/projectes/com-seliminen-els-peixos-introduits-en-estanys-dalta-muntanya-restaurar-los) - Les poblacions de peixos dels estanys d’alta muntanya presenten una alta estabilitat poblacional, al...

53. [La truita de riu del Pirineu, el peix que no enveja la costa](https://vadegust.cat/reportatges/la-truita-de-riu-del-pirineu-el-peix-que-no-enveja-la-costa-11618/) - Es tracta d’una de les espècies que tradicionalment ha format part de l'alimentació de les zones de ...

54. [El tritó pirinenc](https://blocs.xtec.cat/faunaiflora/2010/10/04/el-trito-pirinenc/) - Nom científic: Calotriton asper. Família: Salamàndrids. El tritó pirinenc és un animal vertebrat de ...

55. [El Parc de l'Alt Pirineu acull la primera monitorització en directe d'un niu de gall fer a Catalunya](https://www.radioseu.cat/noticies/el-parc-de-lalt-pirineu-acull-la-primera-monitoritzacio-en-directe-dun-niu-de-gall-fer-a-catalunya) - L'exemplar analitzat porta un dispositiu GPS de seguiment. Les martes i les guineus són els principa...

56. [Capercaillie __Tetrao urogallus__ Nest Loss and Attendance at Abernethy Forest, Scotland](https://onlinelibrary.wiley.com/doi/10.2981/08-036) - Improvement of breeding success is key to capercaillie __Tetrao urogallus__ conservation in Scotland...

57. [OBJECTES - Gall fer - Paisatges Vius](https://paisatgesvius.org/ca/objectes/3945)

58. [Parc de Molló – Parc d’Animals del Pirineu](https://www.molloparc.com/wp-content/uploads/2017/10/Fitxa-El-gall-fer-Mollo%CC%81-Parc.pdf)

59. [GALL FER (Tetrao urogallus) - Muntanyes Vives – –](https://muntanyesvives.org/gall-fer/) - ESPÈCIE: GALL FER (Tetrao urogallus) El fantasma del bosc És l’ocell més emblemàtic dels boscos de m...

60. [Western capercaillie - Wikipedia](https://en.wikipedia.org/wiki/Tetrao_urogallus)

61. [AnAge entry for Tetrao urogallus](https://genomics.senescence.info/species/entry.php?species=Tetrao_urogallus)

62. [[PDF] Why the capercaillie population (Tetrao urogallus L.) in mountain ...](https://ife.sk/wp-content/uploads/2016/10/15.pdf)

63. [Observació de la fauna i flora Parc Natural de l'Alt Pirineu](https://patoupallars.com/experiencies-patou/observacio-de-la-fauna-i-flora-parc-natural-de-lalt-pirineu/) - Al Parc Natural de l'Alt Pirineu podràs observar una gran diversitat d'espècies al seu hàbitat natur...

64. [El trencalòs augmenta la seva població al Parc Natural de l'Alt Pirineu](https://www.3cat.cat/324/el-trencalos-augmenta-la-seva-poblacio-al-parc-natural-de-lalt-pirineu/noticia/2679803/) - Aquesta espècie protegida en risc d'extinció a Catalunya tira endavant quatre polls nous i consolida...

65. [Parc naturel de l'Alt Pirineu en Espagne | spain.info](https://www.spain.info/fr/nature/parc-naturel-alt-pirineu/) - Découvrez la richesse naturelle et culturelle de Parc naturel de l’Alt Pirineu. Emplacement, carte, ...

66. [Sargantana pallaresa - Viquipèdia, l'enciclopèdia lliure](https://ca.wikipedia.org/wiki/Sargantana_pallaresa)

67. [La calor pot matar l'Aureli(oi) - Diari d'Andorra](https://www.diariandorra.ad/nacional/200814/la-calor-pot-matar-aureli_74323.html) - Es diu Aureli(oi) i viu a les tarteres rocosos dels vessants meridionals del Pirineu d'Andorra, del ...

68. [The fauna of Catalonia - All PYRENEES](https://all-andorra.com/the-fauna-of-catalonia/) - The Montpellier snake (Malpolon monspessulanus) is the largest snake of the herpetofauna in Cataloni...

69. [Pirineus - Viquipèdia, l'enciclopèdia lliure](https://ca.wikipedia.org/wiki/Pirineus)

70. [Tritó pirinenc - Viquipèdia, l'enciclopèdia lliure](https://ca.wikipedia.org/wiki/Trit%C3%B3_pirinenc)

71. [Experiments evolutius als llacs d'alta muntanya : diversitat morfològica i variabilitat genètica del tritó pirinenc (Calotriton asper)](https://mcng.cat/recerca/grup-de-recerca-bibio/projectes-herpetologia/llacs/)

72. [Espècies introduïdes als estanys - Life Resque AlPyr](https://liferesquealpyr.eu/ca/especies-introduides-als-estanys/) - PEIXOS INVASORS, ESTANYS ALTERATS La pesca als estanys d’alta muntanya: una activitat tradicional es...

73. [Espècies objectiu - Life Resque AlPyr](https://liferesquealpyr.eu/ca/especies-objectiu/) - Les espècies objectiu inclouen la granota roja (Rana temporaria), un amfibi autòcton del Pirineu i d...

74. [Les grans truites tornen a la capçalera del riu Noguera ...](https://www.segre.com/ca/comarques/250330/les-grans-truites-tornen-capcalera-pallaresa_777121.html) - Els pescadors aconsegueixen reobrir l’assut de l’Hostalet després de sis anys obturat. El seu tancam...

75. [Inici de la temporada de pesca als rius de Lleida](https://aralleida.cat/inici-temporada-pesca-2023/) - El 18 de març ha començat la temporada de pesca als rius de baixa muntanya de Lleida

76. [Cap de setmana d'observació d'ocells al Pirineu](https://voluntariatambiental.cat/activitat/cap-de-setmana-dobservacio-docells-al-pirineu/) - Avui començarem l'activitat ornitològica cap a les 7.30 h a la pista del Bosc de Virós ( Parc Natura...

