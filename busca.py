from sentence_transformers import SentenceTransformer
import numpy as np


modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

documentos = [
    "O Cupom Limpo é uma plataforma de gestão de notas fiscais feita com NestJS, PostgreSQL e Next.js.",
    "A fila de notificações usa BullMQ e Redis, com retry, backoff exponencial e dead letter queue.",
    "Treinei um modelo de regressão logística em Python e usei num chatbot de dados de saúde.",
    "No trabalho, construí o front-end de um sistema de autorização de procedimentos do SUS.",
    "Escrevo testes automatizados com Vitest e Jest e cheguei a 92% de cobertura em produção.",
]


embeddings_docs = modelo.encode(documentos, normalize_embeddings=True)

print("Busca iniciada. Digite 'sair' para encerrar.\n")

while True:
    pergunta = input("Pergunta: ")
    if pergunta.strip().lower() == "sair":
        break

    embedding_pergunta = modelo.encode([pergunta], normalize_embeddings=True)[0]

    similaridades = embeddings_docs @ embedding_pergunta

    melhores = np.argsort(-similaridades)[:2]

    print()
    for i in melhores:
        print(f"{similaridades[i]:.2f} - {documentos[i]}")
    print()