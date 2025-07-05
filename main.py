import json
import random
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

Window.size = (360, 640)

def wczytaj_pytania(plik='pytania.json'):
    with open(plik, 'r', encoding='utf-8') as f:
        return json.load(f)

def zapisz_pytania(pytania, plik='pytania.json'):
    with open(plik, 'w', encoding='utf-8') as f:
        json.dump(pytania, f, ensure_ascii=False, indent=2)

class QuizApp(App):
    def build(self):
        self.pytania = [p for p in wczytaj_pytania() if self.sredni_czas(p.get('statystyki', {}).get('czasy', [])) >= 7.0]
        if not self.pytania:
            return Label(text="🎉 Wszystkie pytania zostały szybko rozwiązane!")
        random.shuffle(self.pytania)
        self.index = 0
        self.poprawne = 0
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.wyswietl_pytanie()
        return self.layout

    def sredni_czas(self, czasy):
        if not czasy:
            return float('inf')
        return sum(czasy) / len(czasy)

    def wyswietl_pytanie(self):
        self.layout.clear_widgets()
        if self.index >= len(self.pytania):
            self.zakoncz_quiz()
            return

        self.start_time = time.time()
        self.biezace = self.pytania[self.index]
        tresc = self.biezace['pytanie']
        self.poprawna_odp = self.biezace['poprawna_odpowiedz']

        self.odpowiedzi = list(self.biezace['odpowiedzi'].items())
        random.shuffle(self.odpowiedzi)

        self.klucz_map = {}
        self.layout.add_widget(Label(text=f"Pytanie {self.biezace['numer']}: {tresc}", size_hint_y=0.3))

        for idx, (klucz, tekst) in enumerate(self.odpowiedzi):
            nowy_klucz = chr(ord('a') + idx)
            self.klucz_map[nowy_klucz] = klucz
            btn = Button(text=f"{nowy_klucz}) {tekst}", size_hint_y=0.15)
            btn.bind(on_press=self.sprawdz_odpowiedz)
            self.layout.add_widget(btn)

    def sprawdz_odpowiedz(self, instance):
        user_input = instance.text[0]
        end_time = time.time()
        czas_odp = end_time - self.start_time

        stat = self.biezace.setdefault('statystyki', {})
        czasy = stat.setdefault('czasy', [])
        czasy.append(czas_odp)
        if len(czasy) > 20:
            czasy.pop(0)

        if self.klucz_map[user_input] == self.poprawna_odp:
            self.poprawne += 1
        else:
            poprawny_tekst = self.biezace['odpowiedzi'][self.poprawna_odp]
            self.layout.clear_widgets()
            self.layout.add_widget(Label(text=f"❌ Zła odpowiedź.
Poprawna to: {poprawny_tekst}", size_hint_y=0.3))
            cont_btn = Button(text="Dalej", size_hint_y=0.2)
            cont_btn.bind(on_press=lambda x: self.nastepne())
            self.layout.add_widget(cont_btn)
            return

        stat['poprawne'] = stat.get('poprawne', 0) + 1
        stat['proby'] = stat.get('proby', 0) + 1
        self.nastepne()

    def nastepne(self, *_):
        self.index += 1
        self.wyswietl_pytanie()

    def zakoncz_quiz(self):
        zapisz_pytania(self.pytania)
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text=f"📊 Twój wynik: {self.poprawne}/{len(self.pytania)}", size_hint_y=0.3))
        btn = Button(text="Zamknij", size_hint_y=0.2)
        btn.bind(on_press=lambda x: App.get_running_app().stop())
        self.layout.add_widget(btn)

if __name__ == "__main__":
    QuizApp().run()
