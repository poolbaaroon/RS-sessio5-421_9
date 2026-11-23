# TASKS.md - Tasks\_app



## Increment 1: MVP - Creació i Llistat de Tasques

Objectiu: Tenir una versió CLI funcional per afegir i consultar tasques en JSON.



### Tasques d'Execució:

- [x] Tasca 1.1: Crear estructura de directoris (`src/`, `test/`, `data/`) i fitxer `data/tasks.json` inicial. (Requisits RF-01 i RF-02) 

- [x] Tasca 1.2: Implementar model de dades `Task` a `src/models.py` amb mètodes de serialització JSON.

- [x] Tasca 1.3: Desenvolupar Tasks\_app a `src/tasks\_app.py` amb opcions `add` i `list`.(Requisits RF-03 i RF-04)

- [x] Tasca 1.4: Crear test d'integració a `test/test\_tasks\_app.py` segons els escenaris GS-01, GS-02 i GS-03.

- [x] Tasca 1.5: Validar execució amb OpenCode i verificar que tots els tests passen (`python3 -m pytest test`).


## Increment 2: Dates límit i actualització de tasques

Objectiu: Incorporar dates límit, modificació i finalització de tasques,
i identificar les tasques pendents caducades o urgents.

Referència: apartat 6 de SPECIFICATIONS.md.

### Regles d'execució

- Executar únicament una tasca pendent per torn.
- Marcar-la com a `[/]` abans de començar.
- Respectar els comandaments, missatges, formats i codis de sortida
  definits a SPECIFICATIONS.md.
- Utilitzar dades temporals per a les proves.
- Conservar les dades d'exemple de data/tasks.json.
- No instal·lar dependències addicionals.
- No modificar SPECIFICATIONS.md per adaptar-lo al codi.
- Si es detecta una contradicció en l'especificació, aturar-se
  i comunicar-la a l'usuari.
- Marcar una tasca com a `[x]` només després de verificar-ne el resultat.
- Mostrar els canvis i les comprovacions realitzades.
- Aturar-se i demanar confirmació abans de començar la següent tasca.

### Tasques d'execució

- [x] Tasca 2.1: Ampliar el model de tasca amb l'atribut opcional `data_limit` i actualitzar la serialització i deserialització JSON. Conservar els atributs existents i admetre registres antics sense `data_limit` o amb valor `null`, sense assignar-los dates automàticament. Afegir proves del model per verificar la conversió d'anada i tornada amb data, sense data i amb valor `null`. (RF-08 i RF-22; apartat 6.6)

- [x] Tasca 2.2: Implementar validacions reutilitzables per a dates en format exacte `YYYY-MM-DD`, dates existents al calendari, IDs enters positius i estats `pendent` o `completada`. Permetre dates passades. Afegir proves unitàries de valors vàlids i invàlids, incloent-hi `2026-02-30`, `10/12/2026`, IDs no numèrics, zero i negatius. Aquesta tasca verifica les validacions internes; la seva integració amb els comandaments es comprovarà en les tasques següents. (RF-07 i RF-14; apartats 6.2 i 6.7)

- [x] Tasca 2.3: Adaptar el comandament `add` perquè exigeixi `--due`, validi la data abans de guardar i conservi la generació incremental d'IDs i l'estat inicial `pendent`. Respectar els missatges i codis de sortida de l'especificació. Actualitzar el test existent de GS-01 i afegir proves d'integració de GS-04, GS-05, GS-06, GS-07 i GS-28. Verificar que les operacions rebutjades no alteren els registres. (RF-03, RF-05, RF-06, RF-07, RF-08, RF-24 i RF-25)

- [x] Tasca 2.4: Implementar el comandament `edit --id <ID>` amb les opcions `--title`, `--subject`, `--due` i `--status`. Exigir almenys un atribut modificable, conservar l'ID i els atributs no indicats, i validar tots els canvis abans de guardar-ne cap. Respectar els missatges i codis de sortida acordats. Afegir proves d'integració de GS-09, GS-10, GS-11, GS-12, GS-20, els casos d'edit de GS-22, GS-23, GS-24 i GS-27. (RF-07, RF-09 a RF-15, RF-24 i RF-25)

- [x] Tasca 2.5: Implementar el comandament `complete --id <ID>` per guardar l'estat `completada`, conservant la resta d'atributs. Admetre l'execució sobre una tasca ja completada amb el mateix missatge d'èxit. Validar l'ID i respectar els missatges i codis de sortida acordats. Afegir proves d'integració de GS-13, GS-21, els casos de complete de GS-22, GS-25 i GS-26. (RF-13, RF-16, RF-17, RF-24 i RF-25; apartat 6.5)

- [x] Tasca 2.6: Adaptar `list` per mostrar la data límit quan existeix i conservar el format anterior per a tasques sense data. Mantenir l'ordre dels registres, el missatge de registre buit i el llistat de tasques completades. Verificar que consultar no modifica les dades guardades. Conservar les proves de GS-02 i GS-03 i afegir o completar les de GS-08 i GS-19. Afegir una comprovació del format d'una tasca amb data situada a més de set dies de la data actual. (RF-04, RF-20, RF-22 i RF-23; apartats 6.5 i 6.6)

- [ ] Tasca 2.7: Incorporar al llistat les etiquetes `[CADUCADA]` i `[URGENT]` segons la data actual i l'estat. Mostrar com a caducades només les tasques pendents amb data anterior a avui; mostrar com a urgents les que vencen avui o entre un i sis dies després. Excloure les tasques completades i sense data, i evitar que apareguin les dues etiquetes alhora. Afegir proves de GS-14 a GS-18 controlant la data actual sense modificar el rellotge de l'ordinador ni instal·lar dependències. (RF-18 a RF-23)

- [ ] Tasca 2.8: Revisar i unificar el tractament dels errors de la CLI segons l'apartat 6.7. Comprovar els missatges exactes, stderr, stdout buit, codi 2 i absència de text d'ajuda addicional en els rebutjos. Afegir la prova de GS-29 i comprovacions d'opcions sense valor i d'arguments obligatoris absents no coberts pels missatges específics. Verificar també que les operacions correctes finalitzen amb codi 0 i stderr buit. Conservar els comportaments validats en les tasques anteriors. (RF-24 i RF-25; apartat 6.7)

- [ ] Tasca 2.9: Fer la validació final de l'increment executant `python3 -m pytest test`. Comprovar que les proves cobreixen GS-01 actualitzat i GS-02 a GS-29, que utilitzen dades temporals i que les comprovacions de dates són reproduïbles. Validar també els comandaments reals de la CLI en un entorn temporal i comprovar que data/tasks.json del projecte conserva el seu contingut. Mostrar els resultats i aturar-se sense començar l'increment 3. (RF-01 a RF-25; GS-01 a GS-29)
