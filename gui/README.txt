GUI:t startas genom att köra filen 'main.py'. Jag har försökt hålla denna fil så kompakt som möjligt.
De flesta intressanta parametrar går att ändra och hittas i config.py

Korta beskrivningar av de olika filerna:
    main.py                 - GUI:t startas genom denna fil
    config.py               - Sätter parametrar. Innehåller startvärden för variabler samt IP och portar för nätverks-kommunikation
    gui_setup.py            - Består av två enkla metoder som bygger roten och gör plats för GUI:ts komponenter m.h.a tkinter frames
    components.py           - Här finns metoder som används för att skapa de olika delarna av GUI:t (typ alla förutom kartan)
    map_display.py          - Hanterar allt vad gäller kartan som visas högst upp till vänster i GUI:till
    networking.py           - Innehåller allt som faciliterar kommunikation via WiFi. 
    utils.py                - Diverse hjälpfunktioner för att t.ex generera påhittad data i testsyften.

    old_gui_prototype.py    - Gammal och obsolete version av GUI:t, innan jag splittrade den till mindre delar/filer
    send_instruction.py     - Samuel skrev denna men jag använde den som mall för att skriva networking.py