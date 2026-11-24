---
name: organizar-acervo-bibliografico
description: >-
  Organiza acervos bibliográficos (PDFs, apostilas, apresentações e arquivos de imagem/escaneados)
  seguindo o padrão da Biblioteca Particular (pasta plana, nomenclatura bibliográfica padronizada e
  extração de texto via OCR paralelo com Tesseract). Use quando o usuário pedir para organizar uma
  pasta de livros/PDFs/documentos, padronizar nomes de acervo bibliográfico, processar novos arquivos
  adicionados ao acervo ou aplicar OCR em arquivos escaneados, de imagem ou com fontes corrompidas.
---

# Organizar Acervo Bibliográfico (Padrão Biblioteca Particular)

Padroniza pastas de livros, apostilas, slides e documentos digitalizados no mesmo padrão de
`Y:\Claude\Biblioteca Particular`, garantindo nomes bibliográficos limpos e extração de texto via OCR
sempre que o material for escaneado, baseado em imagem ou tiver codificação de fonte corrompida.

## Padrão do Acervo

1. **Estrutura plana:** todos os arquivos ficam diretamente na raiz da pasta do acervo (sem subpastas por tema ou autor).
2. **Nomenclatura padrão:**
   `Título [- Subtítulo][, Xª ed.][ Ano][ (Contexto/Instituição/tradução PT-BR/trecho)] - Autor(es).ext`
   - Preservar acentos e capitalização correta (PT-BR ou idioma original).
   - Remover hashes de download (`Toaz-info-...`), prefixos numéricos de sites (`244752345-`), sufixos duplicados (`-pdf-pdf`) e hifens no lugar de espaços.
   - Sem caracteres inválidos no Windows (`:`, `?`, `*`, `"`, `<`, `>`, `|`, `/`, `\`).
   - Quando for amostra/capítulo avulso, incluir `(trecho)` ou `(trecho, pp. X-Y)`.
   - Quando não houver autor identificado no documento, omitir ` - Autor` (não inventar autoria).
3. **Arquivo irmão de texto extraído (OCR):**
   - Nome exato: `<mesmo nome base do arquivo> (texto extraído).txt`
   - Codificação: UTF-8 **sem BOM**, quebra de linha **CRLF** (`\r\n`).
   - Separador de páginas: `--- PAGINA 1 ---`, `--- PAGINA 2 ---`, etc., separados por linha em branco.
   - **Quando gerar:** PDFs escaneados/foto/fotocópia, arquivos de imagem (`.png`, `.jpg`, `.tif`, `.webp`), PDFs com mapa de fonte corrompido (texto nativo sai embaralhado ou com caracteres PUA), ou apresentações/slides com alta proporção de gráficos/texto embutido em imagem.
   - **Quando NÃO gerar (salvo pedido explícito):** PDFs digitais cujo texto nativo já seja íntegro e selecionável.

---

## Fluxo Operacional

### 1. Inspecionar novos arquivos e renderizar capas
Execute o script de diagnóstico [inspecionar_acervo.py](./scripts/inspecionar_acervo.py) salvando previews em uma pasta temporária fora do acervo (nunca deixe PNGs temporários dentro da pasta do acervo):

```powershell
python "<caminho-da-skill>\scripts\inspecionar_acervo.py" "<pasta_acervo>" --previews "<pasta_temp_previews>"
```

O script classifica automaticamente cada arquivo em:
- `OCR_COMPLETO` — escaneado (sem camada de texto) ou fonte com tabela `ToUnicode`/CMap corrompida.
- `OCR_HIBRIDO` — slides/apostilas mistas com páginas de imagem ou caixas com glifos PUA corrompidos.
- `OCR_IMAGEM` — imagem avulsa (`.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`, `.webp`).
- `TEXTO_DIGITAL_OK` — texto digital íntegro e selecionável.

### 2. Confirmar título, edição e autor visualmente
Antes de renomear, **inspecione visualmente** os PNGs renderizados (capa, folha de rosto, ficha catalográfica e última página):
- Muitos PDFs de cursos/slides só trazem o nome do instrutor no último slide ou na página de currículo.
- PDFs com CMap corrompido exibem texto ilegível na extração nativa, mas a renderização visual mostra capa, edição, ano e autor com clareza.
- Verifique se o arquivo é completo ou um trecho/amostra conferindo o sumário vs. número total de páginas.

### 3. Renomear os arquivos na pasta plana
Renomeie os arquivos novos diretamente na raiz do acervo usando PowerShell com UTF-8 (`[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`) e `-LiteralPath`.

### 4. Executar OCR nos arquivos marcados (`OCR_COMPLETO`, `OCR_HIBRIDO`, `OCR_IMAGEM`)
Execute [extrair_ocr_acervo.py](./scripts/extrair_ocr_acervo.py) já sobre os arquivos **renomeados** (para que o `.txt` nasça com o nome definitivo):

```powershell
# PDFs escaneados, CMap corrompido ou imagens avulsas:
python "<caminho-da-skill>\scripts\extrair_ocr_acervo.py" "<arquivo1.pdf>" "<arquivo2.pdf>" --mode ocr --dpi 250 --lang por+eng

# Slides/PDFs mistos (mantém texto nativo limpo e aplica OCR em páginas de imagem/PUA):
python "<caminho-da-skill>\scripts\extrair_ocr_acervo.py" "<slides.pdf>" --mode hybrid --dpi 250 --lang por+eng --min-native-chars 40
```

O script:
- Localiza `tesseract.exe` automaticamente (`PATH` ou `C:\Program Files\Tesseract-OCR\tesseract.exe`).
- Mantém cache persistente do modelo `tessdata_best` (`por+eng`) em `%LOCALAPPDATA%\tesseract-tessdata-best` (sem exigir permissão de administrador).
- Executa em paralelo (`OMP_THREAD_LIMIT=1` + múltiplos workers) e trata slides/capas de fundo escuro por inversão automática de luminância.

### 5. Validar a entrega
1. Liste a pasta final e confirme que não sobraram arquivos temporários, subpastas indevidas ou nomes antigos.
2. Leia trechos do início, meio e fim de cada `(texto extraído).txt` gerado para confirmar acentuação PT-BR íntegra, marcadores `--- PAGINA N ---` e ausência de texto embaralhado.
3. Apresente ao usuário uma tabela `Arquivo original | Novo nome` e o resumo da extração OCR (modo, páginas e caracteres) indicando também os PDFs digitais que dispensaram OCR.

---

## Armadilhas Conhecidas

- **PDF com CMap corrompido parece ter texto nativo:** `len(get_text())` retorna centenas de caracteres por página, mas tudo embaralhado (`!"#$%&`, `CJG\JI`, `Fbexfokre`). Sempre checar a flag `Garbled` do inspetor e olhar uma amostra do texto.
- **Ligaduras PUA inofensivas (`\ue000`–`\ue002`):** alguns PDFs digitais limpos usam esses códigos apenas para `ff`/`fi`/`fl` e não precisam de OCR completo; já códigos `>= 0xE003` em caixas inteiras indicam fonte quebrada.
- **Tesseract padrão no Windows vem só com `eng`:** nunca rodar OCR em documentos PT-BR sem `por.traineddata` (`tessdata_best`), pois acentos e cedilhas ficam comprometidos.
- **PowerShell e `python -c`:** evitar inline longo em `python -c` por distorção de aspas/UTF-8; preferir sempre executar os scripts `.py` em UTF-8.
