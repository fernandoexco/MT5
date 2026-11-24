"""Extrai texto via Tesseract OCR paralelo de PDFs (escaneados, fontes corrompidas ou slides)
e arquivos de imagem, salvando no padrao Biblioteca Particular:
    <nome base> (texto extraído).txt  (UTF-8 sem BOM, CRLF, separadores --- PAGINA N ---)

Uso:
    python extrair_ocr_acervo.py "<arquivo_ou_pasta>" [--mode auto|ocr|hybrid] [--dpi 250] [--lang por+eng] [--workers 12] [--force]
"""

import argparse
import concurrent.futures
import io
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import pymupdf
from PIL import Image, ImageOps

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
TESSDATA_BEST_POR_URL = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/por.traineddata"


def find_tesseract() -> str:
    found = shutil.which("tesseract")
    if found:
        return found
    for candidate in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Tesseract-OCR\tesseract.exe"),
    ):
        if candidate and os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError(
        "tesseract.exe nao encontrado no PATH nem em C:\\Program Files\\Tesseract-OCR\\tesseract.exe."
    )


def ensure_tessdata(tesseract_exe: str, lang: str) -> str:
    local_base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    cache_dir = os.path.join(local_base, "tesseract-tessdata-best")
    os.makedirs(cache_dir, exist_ok=True)

    sys_tessdata = os.path.join(os.path.dirname(tesseract_exe), "tessdata")
    for fname in ("eng.traineddata", "osd.traineddata"):
        dst = os.path.join(cache_dir, fname)
        src = os.path.join(sys_tessdata, fname)
        if not os.path.isfile(dst) and os.path.isfile(src):
            shutil.copy2(src, dst)

    if "por" in lang.split("+"):
        por_dst = os.path.join(cache_dir, "por.traineddata")
        if not os.path.isfile(por_dst):
            por_sys = os.path.join(sys_tessdata, "por.traineddata")
            if os.path.isfile(por_sys):
                shutil.copy2(por_sys, por_dst)
            else:
                print(f"[setup] Baixando por.traineddata (tessdata_best) para {por_dst}...")
                urllib.request.urlretrieve(TESSDATA_BEST_POR_URL, por_dst)

    return cache_dir


def run_tesseract(tesseract_exe: str, tessdata_dir: str, png_bytes: bytes, lang: str, psm: str = "3") -> str:
    env = os.environ.copy()
    env["OMP_THREAD_LIMIT"] = "1"
    proc = subprocess.run(
        [
            tesseract_exe,
            "stdin",
            "stdout",
            "--tessdata-dir",
            tessdata_dir,
            "-l",
            lang,
            "--psm",
            psm,
        ],
        input=png_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=env,
        check=False,
    )
    return proc.stdout.decode("utf-8", errors="replace").strip()


def has_garbled_pua(text: str) -> bool:
    for c in text:
        o = ord(c)
        if 0x0000 < o < 0x0020 and c not in "\n\r\t":
            return True
        if o >= 0xE003:
            return True
    return False


def ocr_image_bytes(tesseract_exe: str, tessdata_dir: str, png_bytes: bytes, lang: str) -> str:
    text = run_tesseract(tesseract_exe, tessdata_dir, png_bytes, lang)
    if len(text) < 25:
        img = Image.open(io.BytesIO(png_bytes)).convert("L")
        mean_luma = sum(img.getdata()) / max(img.width * img.height, 1)
        if mean_luma < 130:
            inv = ImageOps.invert(img)
            buf = io.BytesIO()
            inv.save(buf, format="PNG")
            text_inv = run_tesseract(tesseract_exe, tessdata_dir, buf.getvalue(), lang)
            if len(text_inv) > len(text):
                text = text_inv
    return text.strip()


def ocr_pdf_page(args):
    pdf_path, page_idx, mode, dpi, lang, min_native_chars, tesseract_exe, tessdata_dir = args
    doc = pymupdf.open(pdf_path)
    page = doc[page_idx]

    if mode == "hybrid":
        native = page.get_text("text").strip()
        garbled = has_garbled_pua(native)
        if not garbled and len(native) >= min_native_chars:
            doc.close()
            return page_idx, native, "native"

        pix = page.get_pixmap(dpi=dpi, alpha=False)
        png_bytes = pix.tobytes("png")
        doc.close()
        ocr_text = ocr_image_bytes(tesseract_exe, tessdata_dir, png_bytes, lang)

        if garbled:
            clean_native = [
                ln.strip()
                for ln in native.splitlines()
                if ln.strip() and not has_garbled_pua(ln)
            ]
            ocr_lower = ocr_text.lower()
            extras = [ln for ln in clean_native if len(ln) >= 4 and ln.lower() not in ocr_lower]
            merged = (ocr_text + "\n\n" + "\n".join(extras)).strip() if extras else ocr_text
            return page_idx, merged, "hybrid_ocr"

        final = ocr_text if len(ocr_text) >= len(native) else native
        return page_idx, final.strip(), "ocr"

    pix = page.get_pixmap(dpi=dpi, alpha=False)
    png_bytes = pix.tobytes("png")
    doc.close()
    text = ocr_image_bytes(tesseract_exe, tessdata_dir, png_bytes, lang)
    return page_idx, text, "ocr"


def write_extracted_txt(out_txt: str, pages_text: list[str]) -> None:
    chunks = []
    for i, text in enumerate(pages_text, 1):
        clean_lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()]
        clean_page = "\n".join(clean_lines).strip()
        if clean_page:
            chunks.append(f"--- PAGINA {i} ---\n{clean_page}")
        else:
            chunks.append(f"--- PAGINA {i} ---")
    content = "\n\n".join(chunks) + "\n"
    with open(out_txt, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(content)


def process_pdf(
    pdf_path: str,
    mode: str,
    dpi: int,
    lang: str,
    workers: int,
    min_native_chars: int,
    force: bool,
    tesseract_exe: str,
    tessdata_dir: str,
) -> None:
    base = os.path.splitext(pdf_path)[0]
    out_txt = f"{base} (texto extraído).txt"
    if os.path.exists(out_txt) and not force:
        print(f"[skip] Ja existe: {os.path.basename(out_txt)}")
        return

    doc = pymupdf.open(pdf_path)
    n_pages = len(doc)
    doc.close()

    t0 = time.time()
    print(f"\n>>> [{mode}] {os.path.basename(pdf_path)} ({n_pages} paginas)...")
    tasks = [
        (pdf_path, i, mode, dpi, lang, min_native_chars, tesseract_exe, tessdata_dir)
        for i in range(n_pages)
    ]
    results = [""] * n_pages
    counts: dict[str, int] = {}
    done = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        for page_idx, text, src in ex.map(ocr_pdf_page, tasks, chunksize=2):
            results[page_idx] = text
            counts[src] = counts.get(src, 0) + 1
            done += 1
            if done % 25 == 0 or done == n_pages:
                print(f"    {done}/{n_pages} ({time.time() - t0:.1f}s)")

    write_extracted_txt(out_txt, results)
    size_kb = os.path.getsize(out_txt) / 1024
    total_chars = sum(len(t) for t in results)
    print(
        f"<<< DONE {os.path.basename(out_txt)} | {size_kb:.1f} KB | "
        f"{total_chars} chars | {counts} | {time.time() - t0:.1f}s"
    )


def process_image(
    img_path: str, lang: str, force: bool, tesseract_exe: str, tessdata_dir: str
) -> None:
    base = os.path.splitext(img_path)[0]
    out_txt = f"{base} (texto extraído).txt"
    if os.path.exists(out_txt) and not force:
        print(f"[skip] Ja existe: {os.path.basename(out_txt)}")
        return

    t0 = time.time()
    img = Image.open(img_path)
    pages_text = []
    n_frames = getattr(img, "n_frames", 1)
    for frame in range(n_frames):
        if n_frames > 1:
            img.seek(frame)
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        pages_text.append(ocr_image_bytes(tesseract_exe, tessdata_dir, buf.getvalue(), lang))

    write_extracted_txt(out_txt, pages_text)
    size_kb = os.path.getsize(out_txt) / 1024
    print(f"<<< DONE {os.path.basename(out_txt)} | {size_kb:.1f} KB | {n_frames} pg | {time.time() - t0:.1f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrai texto via OCR no padrao Biblioteca Particular.")
    parser.add_argument("targets", nargs="+", help="Um ou mais arquivos PDF/imagem.")
    parser.add_argument("--mode", choices=["ocr", "hybrid"], default="ocr", help="Modo para PDFs.")
    parser.add_argument("--dpi", type=int, default=250, help="Resolucao de renderizacao para OCR (padrao: 250).")
    parser.add_argument("--lang", default="por+eng", help="Idiomas Tesseract (padrao: por+eng).")
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 4), help="Processos paralelos.")
    parser.add_argument("--min-native-chars", type=int, default=40, help="Limiar de texto nativo no modo hybrid.")
    parser.add_argument("--force", action="store_true", help="Sobrescreve .txt existente.")
    args = parser.parse_args()

    tesseract_exe = find_tesseract()
    tessdata_dir = ensure_tessdata(tesseract_exe, args.lang)

    for target in args.targets:
        ext = os.path.splitext(target)[1].lower()
        if ext == ".pdf":
            process_pdf(
                target,
                args.mode,
                args.dpi,
                args.lang,
                args.workers,
                args.min_native_chars,
                args.force,
                tesseract_exe,
                tessdata_dir,
            )
        elif ext in IMAGE_EXTS:
            process_image(target, args.lang, args.force, tesseract_exe, tessdata_dir)
        else:
            print(f"[warn] Formato ignorado: {target}")


if __name__ == "__main__":
    main()
