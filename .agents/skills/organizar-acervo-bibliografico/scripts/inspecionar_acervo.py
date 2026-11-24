"""Inspeciona PDFs e imagens de um acervo bibliografico, diagnostica a necessidade de OCR
e opcionalmente renderiza capas/paginas-chave para verificacao visual de titulo e autor.

Uso:
    python inspecionar_acervo.py "<pasta_acervo>" [--previews "<pasta_previews>"] [--only-new]
"""

import argparse
import os
import re
import sys
import pymupdf

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
COMMON_WORDS = {
    "de", "da", "do", "das", "dos", "em", "na", "no", "para", "com", "por",
    "que", "uma", "um", "os", "as", "se", "ao", "como", "mais", "ou", "ser",
    "the", "and", "of", "to", "in", "for", "with", "is", "on", "that", "as",
    "swing", "trade", "trading", "mercado", "acoes", "ações", "preco", "preço",
    "analise", "análise", "risco", "capitulo", "capítulo", "pagina", "página",
}


def has_non_ligature_pua(text: str) -> bool:
    for c in text:
        o = ord(c)
        if 0x0000 < o < 0x0020 and c not in "\n\r\t":
            return True
        # \ue000-\ue002 are sometimes harmless fi/ff/fl ligatures; flag broader PUA ranges
        if o >= 0xE003:
            return True
    return False


def is_garbled_cmap(sample_text: str) -> bool:
    if len(sample_text) < 80:
        return False
    # Detect 1-character-per-line broken text streams (common in some browser PDF exports)
    lines = [ln.strip() for ln in sample_text.splitlines() if ln.strip()]
    if len(lines) >= 40:
        single_char_ratio = sum(1 for ln in lines if len(ln) <= 2) / len(lines)
        if single_char_ratio > 0.65:
            return True
    # High ratio of weird ASCII punctuation/symbols inside words
    weird = sum(1 for c in sample_text if c in "`^~|\\@#$%&*+<>[]{}=_")
    if weird / max(len(sample_text), 1) > 0.04:
        return True
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{2,}", sample_text.lower())
    if len(words) >= 25:
        hits = sum(1 for w in words if w in COMMON_WORDS)
        if hits / len(words) < 0.04:
            return True
    return False


def inspect_pdf(path: str, preview_dir: str | None, idx: int) -> None:
    name = os.path.basename(path)
    base = os.path.splitext(path)[0]
    has_txt = os.path.exists(f"{base} (texto extraído).txt")
    size_mb = os.path.getsize(path) / (1024 * 1024)

    doc = pymupdf.open(path)
    n_pages = len(doc)
    meta = doc.metadata or {}

    text_pages = 0
    low_pages = 0
    img_pages = 0
    pua_pages = []
    total_chars = 0
    combined_sample = []
    page_snippets = []

    for i in range(n_pages):
        t = doc[i].get_text("text").strip()
        imgs = doc[i].get_images()
        if len(t) >= 30:
            text_pages += 1
        else:
            low_pages += 1
        if imgs:
            img_pages += 1
        if has_non_ligature_pua(t):
            pua_pages.append(i + 1)
        total_chars += len(t)
        if len(combined_sample) < 15 and len(t) >= 40:
            combined_sample.append(t[:500])
        if i < 3 or i == n_pages - 1:
            page_snippets.append((i + 1, len(t), len(imgs), t[:260].replace("\n", " | ")))

    avg_chars = total_chars / max(n_pages, 1)
    garbled = is_garbled_cmap("\n".join(combined_sample))

    if n_pages == 0:
        rec = "VAZIO"
    elif garbled or (text_pages / n_pages < 0.25):
        rec = "OCR_COMPLETO"
    elif (low_pages / n_pages >= 0.20 and img_pages > 0) or len(pua_pages) >= 1:
        # Check if low_pages is just a cover/logo on a very short doc
        if n_pages <= 6 and low_pages <= 1 and len(pua_pages) == 0:
            rec = "TEXTO_DIGITAL_OK"
        else:
            rec = "OCR_HIBRIDO"
    else:
        rec = "TEXTO_DIGITAL_OK"

    print("=" * 80)
    print(f"[{idx:02d}] {name} ({size_mb:.2f} MB) -> {rec} | HasTxt={has_txt}")
    print(
        f"  Pages={n_pages} | Text(>=30c)={text_pages} | Low(<30c)={low_pages} | "
        f"ImgPages={img_pages} | AvgChars={avg_chars:.0f} | Garbled={garbled} | PUA={pua_pages[:10]}"
    )
    if any(meta.get(k) for k in ("title", "author", "subject")):
        print(f"  Meta: title={meta.get('title')!r} | author={meta.get('author')!r}")
    for pno, clen, ilen, snip in page_snippets:
        print(f"    P{pno} (c={clen}, img={ilen}): {snip}")

    if preview_dir and n_pages > 0:
        os.makedirs(preview_dir, exist_ok=True)
        pages_to_render = sorted(set([0, min(1, n_pages - 1), min(2, n_pages - 1), n_pages - 1]))
        for p in pages_to_render:
            out_png = os.path.join(preview_dir, f"f{idx:02d}_p{p+1}.png")
            doc[p].get_pixmap(dpi=120).save(out_png)

    doc.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspeciona acervo bibliografico.")
    parser.add_argument("folder", help="Pasta do acervo.")
    parser.add_argument("--previews", default=None, help="Pasta para salvar PNGs de capa/paginas-chave.")
    parser.add_argument("--only-new", action="store_true", help="Mostra apenas arquivos sem ' - ' ou sem .txt.")
    args = parser.parse_args()

    entries = sorted(os.listdir(args.folder))
    idx = 0
    for name in entries:
        full = os.path.join(args.folder, name)
        if not os.path.isfile(full):
            continue
        ext = os.path.splitext(name)[1].lower()
        if ext == ".txt":
            continue
        if args.only_new and " - " in name and os.path.exists(f"{os.path.splitext(full)[0]} (texto extraído).txt"):
            continue

        idx += 1
        if ext == ".pdf":
            inspect_pdf(full, args.previews, idx)
        elif ext in IMAGE_EXTS:
            base = os.path.splitext(full)[0]
            has_txt = os.path.exists(f"{base} (texto extraído).txt")
            size_kb = os.path.getsize(full) / 1024
            print("=" * 80)
            print(f"[{idx:02d}] {name} ({size_kb:.1f} KB) -> OCR_IMAGEM | HasTxt={has_txt}")
        else:
            print("=" * 80)
            print(f"[{idx:02d}] {name} -> OUTRO_FORMATO ({ext})")


if __name__ == "__main__":
    main()
