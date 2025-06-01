from flask import Flask, render_template, request
import zeyrek
import requests

app = Flask(__name__)
analyzer = zeyrek.MorphAnalyzer()
cache = {}

TranslateData = {
    "Inf1": "Mastar eki", "Verb": "Fiil", "Noun": "İsim", "Past": "Görülen geçmiş zaman",
    "Narr": "Duyulan geçmiş zaman", "NarrPart": "Duyulan geçmiş zaman", "Pres": "Şimdiki zaman",
    "Prog2": "Şimdiki zaman", "Fut": "Gelecek zaman", "Aor": "Geniş zaman", "Ly": "Pekiştirme eki",
    "Num": "Sayı", "With": "Olumluluk eki", "Without": "Olumsuzluk eki", "Adj": "Sıfat",
    "Adv": "Zarf", "Agt": "Özne", "Become": "Dönüşme eki", "Able": "Yeterlilik fiili",
    "Repeat": "Sürerlik fiili", "Almost": "Yaklaşma fiili", "Hastily": "Tezlik fiili",
    "A1sg": "1. Tekil Şahıs", "A2sg": "2. Tekil Şahıs", "A3sg": "3. Tekil Şahıs",
    "A1pl": "1. Çoğul Şahıs", "A2pl": "2. Çoğul Şahıs", "A3pl": "3. Çoğul Şahıs",
    "P1sg": "İyelik eki", "P1pl": "İyelik eki", "Nom": "Yalın hâl", "Acc": "Belirtme hâli",
    "Dat": "Yönelme hâli", "Loc": "Bulunma hâli", "Abl": "Ayrılma hâli", "Gen": "Tamlayan hâli",
    "Ins": "Araç hâli", "Cop": "İsim-fiil eki", "Caus": "Ettirgenlik", "Pass": "Edilgenlik",
    "Nec": "Gereklilik kipi", "Desr": "İstek kipi", "Cond": "Dilek kipi", "Imp": "Emir Kipi",
    "Prog1": "Şimdiki zaman eki", "PastPart": "Sıfat-fiil (mişli geçmiş)", "Neg": "Olumsuzluk",
    "Pos": "Olumlu"
}

def translateTable(ek_listesi):
    return [TranslateData.get(ek, ek) for ek in ek_listesi]

def getMeaningAndExample(kelime):
    url = f"https://sozluk.gov.tr/gts?ara={kelime}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
    except:
        return "Anlam alınamadı.", "Örnek alınamadı."

    anlam = "Anlam bulunamadı."
    ornek = "Örnek bulunamadı."

    try:
        if data and "anlamlarListe" in data[0]:
            anlam = data[0]["anlamlarListe"][0]["anlam"]
            if "orneklerListe" in data[0]["anlamlarListe"][0]:
                ornek = data[0]["anlamlarListe"][0]["orneklerListe"][0]["ornek"]
    except:
        pass

    return anlam, ornek

@app.route("/", methods=["GET", "POST"])
def index():
    sonuc = None
    kelime = ""
    if request.method == "POST":
        kelime = request.form["kelime"]
        if kelime in cache:
            analiz = cache[kelime]
        else:
            analiz_listesi = analyzer.analyze(kelime)
            if analiz_listesi and analiz_listesi[0]:
                analiz = analiz_listesi[0][0]
                cache[kelime] = analiz
            else:
                analiz = None

        if analiz:
            kök = analiz.lemma
            tur = TranslateData.get(analiz.pos, analiz.pos)
            ekler = ', '.join(translateTable(analiz.morphemes))
            anlam, ornek = getMeaningAndExample(kök)

            sonuc = {
                "kök": kök,
                "tür": tur,
                "ekler": ekler,
                "anlam": anlam,
                "örnek": ornek,
                "tdk_link": f"https://sozluk.gov.tr/?kelime={kök}"
            }
        else:
            sonuc = {"hata": "Bu kelime çözümlenemedi."}

    return render_template("index.html", sonuc=sonuc, kelime=kelime)

if __name__ == "__main__":
    app.run(debug=True)
