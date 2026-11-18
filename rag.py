from dotenv import load_dotenv
load_dotenv()

import anthropic
import numpy as np
from chunks import carregar_chunks, modelo

client = anthropic.Anthropic()

documentos = carregar_chunks()
embeddings_docs = modelo.encode(documentos, normalize_embeddings=True)
print(f"{len(documentos)} chunks carregados.")

SISTEMA = (
    "Você responde perguntas sobre os projetos e a experiência da Eduarda. "
    "Use APENAS o contexto fornecido. Cada trecho começa com 'Projeto > Seção'. "
    "Se a resposta não estiver no contexto, diga que não encontrou essa informação. "
    "Responda em português, de forma curta."
)

def buscar(pergunta, k=4):
    embedding_pergunta = modelo.encode([pergunta], normalize_embeddings=True)[0]
    similaridades = embeddings_docs @ embedding_pergunta
    melhores = np.argsort(-similaridades)[:k]
    return [(documentos[i], similaridades[i]) for i in melhores]

if __name__ == "__main__":
        print("Assistente iniciado. Digite 'sair' para encerrar.\n")

        while True:
            pergunta = input("Pergunta: ")
            if pergunta.strip().lower() == "sair":
                break
            resultados = buscar(pergunta)
            contexto = "\n\n---\n\n".join(texto for texto, _ in resultados)
            prompt = f"Contexto:\n{contexto}\n\nPergunta: {pergunta}"
            resposta = client.messages.create(
                model="claude-sonnet-5-5",
                max_tokens=500,
                system=SISTEMA,
                messages=[{"role": "user", "content": prompt}],
            )
            texto = "".join(b.text for b in resposta.content if b.type == "text")
            print("\nTrechos usados:")
            for trecho, nota in resultados:
                print(f"  {nota:.2f} | {trecho.splitlines()[0]}")
            print(f"\nClaude: {texto}\n")