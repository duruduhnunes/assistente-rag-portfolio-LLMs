from pathlib import Path
from sentence_transformers import SentenceTransformer

NOME_MODELO = "paraphrase-multilingual-MiniLM-L12-v2"     # pequeno: 9/10
# NOME_MODELO = "paraphrase-multilingual-mpnet-base-v2"   # maior: 8/10, ~1 GB, mais lento
modelo = SentenceTransformer(NOME_MODELO)
LIMITE = modelo.max_seq_length - 2

def contar_tokens(texto):
    return len(modelo.tokenizer.tokenize(texto))

def dividir_se_grande(chunk):
    if contar_tokens(chunk) <= LIMITE:
        return [chunk]
    cabecalho, corpo = chunk.split("\n", 1)
    pedacos = []
    atual = []
    for linha in corpo.splitlines():
        if not linha.strip():
            continue
        candidato = "\n".join([cabecalho] + atual + [linha])
        if atual and contar_tokens(candidato) > LIMITE:
            pedacos.append("\n".join([cabecalho] + atual))
            atual = [linha]
        else:
            atual.append(linha)
    if atual:
        pedacos.append("\n".join([cabecalho] + atual))
    return pedacos

def quebrar_por_titulos(texto):
    chunks = []
    projeto = ""
    secao = ""
    linhas = []
    dentro_de_codigo = False

    def fechar_chunk():
        corpo = "\n".join(linhas).strip()
        if corpo:
            cabecalho = f"{projeto} > {secao}" if secao else projeto
            chunks.append(f"{cabecalho}\n{corpo}")

    for linha in texto.splitlines():
        if linha.strip().startswith("```"):
            dentro_de_codigo = not dentro_de_codigo
        if linha.startswith("#") and not dentro_de_codigo:
            fechar_chunk()
            linhas = []
            titulo = linha.lstrip("#").strip()
            if linha.startswith("# "):
                projeto = titulo
                secao = ""
            else:
                secao = titulo
        else:
            linhas.append(linha)
    fechar_chunk()
    return chunks

def carregar_chunks(pasta="docs"):
    todos = []
    for arquivo in sorted(Path(pasta).glob("*.md")):
        texto = arquivo.read_text(encoding="utf-8")
        for chunk in quebrar_por_titulos(texto):
            todos.extend(dividir_se_grande(chunk))
    return todos

if __name__ == "__main__":
    chunks = carregar_chunks()
    for pedaco in chunks:
        tokens = contar_tokens(pedaco)
        aviso = "  <-- PASSOU DO LIMITE" if tokens > LIMITE else ""
        print(f"{tokens:4d} tokens | {pedaco.splitlines()[0]}{aviso}")
    print(f"\nTotal: {len(chunks)} chunks")