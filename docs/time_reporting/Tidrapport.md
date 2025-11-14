Denna fil är skriven med [MarkDown](https://www.markdownguide.org/basic-syntax/)

Uppdatera tidrapporten **senast** kl 16 varje måndag, enligt Leveranser och deadlines i Lisam.
Glöm inte att även uppdatera tidplanen.

# Tidrapport Grupp xx
Svara på följande frågor i tidrapporten varje vecka:
1. Vilka framsteg har gjorts sedan förra tidrapporten?
2. Finns det några problem?
3. Vad ska göras kommande vecka?


## Tidrapport t o m  Vecka 44 (Grupp 09) (rapporteras måndag v45)

1. Vilka framsteg har gjorts sedan förra tidrapporten?
Från BP2 till och med v44 har vi skrivit en designspec som vi fått godkänt på efter två kompletteringar. 

2. Finns det några problem?
Vi har inga problem hittils. 

3. Vad ska göras kommande vecka?
Kommande vecka ska vi börja på projektet genom att i grupper om två börja arbeta med de aktiviteter vi definierat i projektplanen. Det är bland annat att få ordning på kommunikation mellan moduler och externt användargränssnitt, få ordning på bilen och gärna lyckas med att få den att rulla frammåt mot slutet av veckan. 


## Tidrapport för v45 (Grupp 09) (rapporteras måndag v46)

1. **Vilka framsteg har gjorts sedan förra tidrapporten?**
Vi har kommit igång ordentligt med arbetet. Det som funkar nu är bland annat: 
Kommunikationsmodulen har ett main-program som kan kommunicera med användargränssnitt.
Kommunikationsmodulen kan skicka meddelanden till Styrmodulen. 
Användargränssnittet kan ta emot och skicka saker till kommunikationsmodulen.
Användargränssnittets själva GUI är nära sin slutliga form. 
Styrmodulen kan få hjulen att snurra. 
Lidaren kan skicka datapunkter till kommunikationsmodulen. 

2. **Finns det några problem?**
Många mini-problem finns men vi sitter inte fast någonstans. 
Vi har problem med att koppla upp oss till Raspberry Pi:en över Eduroam. Vi har kört hotspot från våra telefoner än så länge men vore mycket smidigare med Eduroam. Vi har skrivit en ticket till Liu IT.

3. ** Vad ska göras kommande vecka?**
Få färdigt styr- och sensormodul samt bli färdiga med kommunikationsmodulens icke-självkörande del. 
Få bilen att kunna köras manuellt från användargränssnittet. 
Fortsatt arbete med Lidar samt börja på kon-igenkänning. 



## Tidrapport för v46 (Grupp 09) (rapporteras måndag v47)

1. **Vilka framsteg har gjorts sedan förra tidrapporten?**
Vi har lyckats med att köra bilen manuellt från användargränssnittet genom wi-fi uppkoppling. Med andra ord är styrmodulen nästan färdig. Kommunikationsmodulen kan med hjälp av LiDAR identifiera koner och lägga in i en karta. Vi har påbörjat att definiera ett meddelande-protokoll för att kunna skicka olika typer av meddelanden mellan kommunikationsmodulen och användargränssnittet. Gyroskop och hallsensorer är nära färdigta. 

2. **Finns det några problem?**
Vi skulle behöva veta hur konerna ser ut och helst få låna två koner för att trimma in igenkänningen av koner och porar. Vi ligger några timmar back jämfört med hur mycket tid vi planerat att lägga ner så vi jobbar med att komma ikapp. 

3. **Vad ska göras kommande vecka?**
Bilen ska kunna skicka den data som ska till användargränssnittet. Motor-bromsen skall implementeras. Fortsatt arbete med karta och positionering av bilen för framtida självkörande-implementering. Konigenkänningen ska anpassas till de verkliga konerna och portarna. 


## Tidrapport för v47 (Grupp 09) (rapporteras måndag v48)

*Utökad tidrapport*

1. **Vilka framsteg har gjorts sedan förra tidrapporten?**
Meddlanden mellan laptop och Raspberry skickas på ett nytt format (json dump). 
Användargränssnittet tar emot och målar upp koner/portar av olika storlek/typ.
Rework på mycket av koden för att göra den mer allmän och för att möjliggöra implementation av autonom körning och multithreading. 
Kod för att använda datan från sensormodulen och uppdatera bilens position har skrivits. Kommunikation mellan alla moduler är nästan helt på plats. 


2. **Finns det några problem?**
Mystiska problem med motorreglage. Olovs hypotes är flimmer på pinnarna. Löstes en gång genom att råka kortsluta två på pinnar. 
Strul med jtag:arna som kopplar loss UART vid omstart.
Flaskhals i utveckling. Svårt att testa de bitar av självkörningen som påbörjats innan all annan funktionalitet är klar. 


3. **Vad ska göras kommande vecka?**
En del meddelanden måste fortfarande implementeras, t.ex kill switch, back/broms, autonomi, m.m.
Sensor-data behöver eventuellt behandlas mer och skickas till laptop.
Vi ska arbeta med att få bilen att köra mellan uppställda konpar. För det behöver vi få bilens positionering färdig men också algoritm för att hitta en väg från punkt A till B. 


4. **Vilken funktionalitet har roboten idag?**
Bilen kan styras manuellt (köra framåt och svänga) från användargränssnittet över wi-fi. 
Det finns ett grafiskt användargränssnitt som kan köras på en extern dator. 
En LiDAR kan läsa av omgivningen och identifiera koner samt deras storlek. 
Hallsensorer och gyroskop fungerar och kommuniceras till huvudprogrammet i kommunikationsmodulen. 
Kommunikation mellan PI och AVR är fungerande med implementerade protokoll.
Kommunikation mellan PI och GUI är färdigt envägs och nästan färdigt åt andra hållet. 
LiDAR kan rita ut portar i gränssnittet. 

5. **Vilken funktionalitet återstår**
I stort återstår självkörande-algoritmen av projekten. 
Lite annat såsom: Kill switch, att gränssnittet tar emot gyro och hallsensor-data,
att bilen går igång och kopplar upp sig automatisk. 

    **Beskriv eventuella tekniska problem.** Se punk 2. 

6. **Hur mycket tid har ni kvar av budgeterade timmar?**
447 timmar. 

7. **Hur många timmar har respektive projektmedlem kvar att leverera (för att nå målet på 160 timmar)?** Man bör ligga på 94 för tillfället

| Person       | Arbetade timmar | Timmar kvar | v.48       | v.49      | v.50     |
| ------       | ------          | ------      | -----------|-----------|----------|
|    Samuel    |     92.5        |     67.5    |  24        | 22.5      | 21       |
|    Alfred    |     79          |     81      |  27        | 28        | 26       |
|    Axel      |     95          |     65      |  22        | 23        | 20       |
|    Rikard    |     79.5        |     80.5    |  27        | 27.5      | 26       |
|    Kacper    |     78          |     82      |  28        | 27        | 27       |
|    Gustaf    |     89          |     71      |  24        | 24        | 23       |

*Aktiviteter: *
- Samuel: Autonom körning. Mjukvara för identifiering av portar, Statusrapporter, Lokal och global
 karta. 
- Alfred: Autonom körning. Bygg mjukvara som anpassar styralgoritm för kal. varv
- Axel: Autonom körning. Mjukvara för identifiering av portar, Teknisk dokumentation.
- Rikard: Autonom körning. Bygg mjukvara som anpassar styralgoritm för kal. varvTeknisk dokumentation.
- Kacper: Autonom körning. Bygg mjukvara som anpassar styralgoritm för kal. varv, Teknisk dokumentation.
- Gustaf: Autonom körning. Mjukvara för identifiering av portar, Lokal och global karta. Teknisk dokumentation.

5. **Är arbetsbelastningen jämn i gruppen? Om inte, ange orsak och vilken åtgärd ni vidtar för att jämna ut belastningen.Beskriv eventuella samarbetsproblem.**
Det har varit lite ojämnt. Detta har berott på att två gruppmedlemmar (Alfred och Kacper) är assistenter i andra kurser och det har krockat mycket med schemat. Rikard har hamnat lite efter på grund av stort engagemang i arbetsmarknadsmässan LARM som haft några heldagsaktiviteter. Under mötet vi hade idag diskuterade vi hur de ska ta igen det och de kommer få sitta på helger i en ganska stor utsträckning under andra halvan av kursen för att komma upp i timmarna de behöver. Vi har inga samarbetsproblem mer än att det är svårt att vara många på ett projekt där det ibland blir flaskhalsar så man får vänta på att en annan ska bli klart. 


## Tidrapport för v48 (Grupp 09) (rapporteras måndag v49)

1. **Vilka framsteg har gjorts sedan förra tidrapporten?**
Stort arbete med att arbeta om mainloop-koden har gjorts för att få bättre struktur och även implementera web sockets för bättre informationsöverföring mellan Pi och Gui (som har strulat tidigare). 
Programmet för självkörning är i full gång. Testning har påbörjats av det i Visionen men det är mycket arbete kvar. 
Lita annat småfix har genomförts såsom att usb-portarna matchas mot devicerna automatiskt. 
 
2. **Finns det några problem?**
Motorn som ibland bara vägrar att snurra går att lösa genom att snabbt kortsluta pwr och gnd på virkortet. 

3. **Vad ska göras kommande vecka?**
Fortsatt arbete med självkörningen. I övrgt är alla delar av bilen i stort sätt färdiga. 

## Tidrapport för v49 (Grupp xx) (rapporteras måndag v50)

1. **Vilka framsteg har gjorts sedan förra tidrapporten?**
Vi har bytt fokus till  att få bilen att köra. På söndagen fick vi bilen att köra med en väldigt enkel algoritm som bara utgick efter vad lidaren ser just nu och struntar i gyro- och hallsensordata. 

2. **Finns det några problem?**
Inget nytt. 

3. **Vad ska göras kommande vecka?**
Fortsätta trimma på algoritmen (som faktiskt blivit ganska bra i låga hastigheter under måndagen v50:s arbete)
Målet nu är att bilen kan köra runt banan men i låg fart. 
Bocka av alla kraven som ska vara genomförda till BP5. 


## Tidrapport för v50 (Grupp 09) (rapporteras måndag v51)

1. **Vilka framsteg har gjorts sedan förra tidrapporten?**
Bilen kör ganska bra. Den klarar inte alla situationer men tar sig igenom de flesta banor vi provat. Använarhandledning och teknisk dokumentation är inlämnat. 

2. **Finns det några problem?**
De omförhandlade kraven är i stort sett uppfyllda så nej. 

3. **Vad ska göras kommande vecka?**
Presentera projektet och tävla!