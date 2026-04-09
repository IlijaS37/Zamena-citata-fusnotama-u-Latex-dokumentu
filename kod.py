import re
import sys

def ucitaj_bibtex(fajl):
    with open(fajl, "r", encoding="utf-8") as f:
        sadrzaj = f.read()
    
    clanovi = {}

    obrasci = re.findall(r"@(\w+)\s*\{(.*?),(.*?)\n\}", sadrzaj, re.DOTALL)

    for tip, kljuc, telo in obrasci:
        kljuc = kljuc.strip()

        poklapanja = re.findall(r"(\w+)\s*=\s*\{(.*?)\}", telo, re.DOTALL)

        polja = dict(poklapanja)

        for k in polja:
            polja[k] = polja[k].strip()

        if "author" not in polja or not polja["author"]:
            polja["author"] = "Nepoznat autor"
        if "title" not in polja or not polja["title"]:
            polja["title"] = "Nepoznat naslov"
        if "year" not in polja or not polja["year"]:
            polja["year"] = "Nepoznata godina"

        clanovi[kljuc] = polja

    return clanovi

def obradi_tex(tex_fajl, bib_podaci):
    with open(tex_fajl, "r", encoding="utf-8") as f:
        tekst = f.read()

    vidjeni_pojedinacni = {}

    vidjene_grupe = {}

    brojac = 1

    def formatiraj_citat(e):
        delovi = []

        for k, v in e.items():
            if v.strip():
                delovi.append(v)

        return ", ".join(delovi)

    def zamena(match):
        nonlocal brojac

        svi_kljucevi = [k.strip() for k in match.group(1).split(",")]
        kljucevi = []
        for k in svi_kljucevi:
            if k not in kljucevi:
                kljucevi.append(k)
        grupa = tuple(kljucevi)

        if len(kljucevi) > 1 and grupa in vidjene_grupe:
            return f"\\textsuperscript{{{vidjene_grupe[grupa]}}}"

        if len(kljucevi) == 1 and kljucevi[0] in vidjeni_pojedinacni:
            return f"\\textsuperscript{{{vidjeni_pojedinacni[kljucevi[0]]}}}"

        fusnote = []

        for k in kljucevi:
            if k in bib_podaci:
                e = bib_podaci[k]
                fusnote.append(formatiraj_citat(e))
            else:
                fusnote.append(f"[Nepoznat citat: {k}]")

        rezultat = "\\footnote{" + " ; ".join(fusnote) + "}"

        if len(kljucevi) > 1:
            vidjene_grupe[grupa] = brojac

        if len(kljucevi) == 1:
            vidjeni_pojedinacni[kljucevi[0]] = brojac

        brojac += 1
        return rezultat

    novi = re.sub(r"\\cite\{(.*?)\}", zamena, tekst)

    novi = re.sub(r"\\bibliographystyle\{.*?\}", "", novi)
    novi = re.sub(r"\\bibliography\{.*?\}", "", novi)

    return novi

if len(sys.argv) != 4:
    print("Upotreba: python kod.py ulaz.tex literatura.bib izlaz.tex")
    sys.exit(1)

tex_ulaz = sys.argv[1]
bib_ulaz = sys.argv[2]
tex_izlaz = sys.argv[3]

bib_podaci = ucitaj_bibtex(bib_ulaz)
novi_tex = obradi_tex(tex_ulaz, bib_podaci)

with open(tex_izlaz, "w", encoding="utf-8") as f:
    f.write(novi_tex)

print("Obrada zavrsena. Rezultat upisan u:", tex_izlaz)