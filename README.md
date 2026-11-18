# Assistente RAG sobre os meus projetos

Assistente de terminal que responde perguntas sobre os meus projetos de programação, usando **RAG** (Retrieval-Augmented Generation): ele busca os trechos certos dos READMEs dos meus repositórios e manda só esses trechos para o Claude responder.

Projeto de estudo feito em Python, para aprender na prática como funciona um sistema com LLM: embeddings, chunking, busca por similaridade e avaliação.

**Stack:** Python 3.13 · sentence-transformers (embeddings locais) · NumPy · API do Claude (Anthropic) · python-dotenv

## Exemplo

```
Pergunta: como funciona a dead letter queue?

Trechos usados:
  0.57 | Fila de Notificações com BullMQ, Redis e NestJS > Dead letter queue (DLQ)
  0.53 | Fila de Notificações com BullMQ, Redis e NestJS > Por que usar uma fila
  ...

Claude: Quando um job falha na última tentativa, o evento `failed` do worker copia
os dados dele para a fila `notifications-dlq` [...]. Assim nenhum pedido some sem
rastro: dá para investigar o que deu errado e reenviar depois.
```

Quando a informação não está nos trechos encontrados, o assistente responde que não encontrou, em vez de inventar.

## Como funciona

O sistema tem duas etapas.

**1. Preparação (uma vez, ao iniciar)**

```
docs/*.md ──> quebra em chunks ──> modelo de embeddings ──> 132 vetores na memória
```

- Os READMEs dos meus projetos ficam na pasta `docs/`, em Markdown.
- `chunks.py` quebra cada arquivo em pedaços (chunks).
- Um modelo de embeddings, que roda localmente e de graça, transforma cada chunk em um vetor que representa o seu significado.

**2. Cada pergunta**

```
pergunta ──> vetor ──> similaridade com os 132 vetores ──> 4 melhores chunks ──> Claude ──> resposta
            (Recuperar)                                   (Aumentar)           (Gerar)
```

- A pergunta passa pelo **mesmo** modelo de embeddings.
- A similaridade de cosseno (produto escalar `@` entre vetores normalizados) dá uma nota para cada chunk.
- Os 4 chunks com maior nota entram no prompt, junto com a pergunta.
- O Claude responde usando apenas esse contexto.

Só a última etapa usa a API (e gasta crédito). Toda a busca roda no meu computador.

## Decisões de chunking

**Corte pelos títulos do Markdown.** Cada seção (`##`) de um README já fala de um assunto só, então ela é um bom ponto de corte. O código ignora linhas com `#` dentro de blocos de código, que são comentários de shell e não títulos.

**Cabeçalho em todo chunk.** Cada pedaço começa com `Projeto > Seção`, por exemplo `Saúde em Dados — API > Regras de risco`. Sem isso, um chunk "Como rodar" não diria de qual projeto ele é. Isso fez várias perguntas acertarem só pelo nome do projeto no cabeçalho.

**Tamanho medido, não chutado.** O modelo de embeddings lê no máximo 128 tokens por texto (`modelo.max_seq_length`), e o que passar disso é **ignorado sem erro**. Descontando 2 tokens especiais, o limite útil é 126. Seções maiores são divididas linha por linha até perto do limite, e cada pedaço repete o cabeçalho.

| Etapa | Chunks | Acima do limite |
|---|---|---|
| Só corte por título | 63 | 30 |
| Corte por título + divisão por linhas | 132 | 3 |

Os 3 que sobram são parágrafos inteiros em uma linha só; nesses casos o modelo perde apenas o final do parágrafo.

## Avaliação

`avaliar.py` roda 10 perguntas e confere se algum dos 4 trechos encontrados é da seção esperada. Ele testa **só a busca**, sem chamar o Claude: roda em segundos e não gasta crédito.

Como a resposta do RAG só é tão boa quanto a busca, medir a busca primeiro mostra onde está o problema. Cada mudança foi feita uma de cada vez e medida:

| Mudança | Acertos |
|---|---|
| Linha de base | 7/10 |
| Título da seção do modelo de ML passou a citar "chatbot" | 8/10 |
| README do projeto Pacientes API reescrito (banco e ODM explícitos) | 9/10 |

Os três erros iniciais tinham a mesma causa: a pergunta usava uma palavra que não estava escrita no trecho certo (por exemplo, "chatbot" numa seção que só falava em "classificador de intenções"). A melhoria veio do conteúdo, não do código.

### Experimento: modelo de embeddings maior

| Modelo | Acertos | Observação |
|---|---|---|
| `paraphrase-multilingual-MiniLM-L12-v2` | **9/10** | escolhido |
| `paraphrase-multilingual-mpnet-base-v2` | 8/10 | cerca de 1 GB, mais lento |

O modelo maior acertou uma pergunta que o pequeno errava, mas errou duas que o pequeno acertava: ele dá mais peso à intenção da pergunta ("qual banco você usou?") do que ao projeto citado. Como não houve ganho e ele é mais pesado, mantive o modelo pequeno. Para trocar, basta mudar `NOME_MODELO` em `chunks.py`.

## Como rodar

Pré-requisitos: Python 3 e uma chave da API da Anthropic.

```bash
git clone https://github.com/<usuario>/<repositorio>.git
cd <repositorio>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz com a sua chave (ele está no `.gitignore` e nunca vai para o repositório):

```
ANTHROPIC_API_KEY=sua-chave-aqui
```

Comandos:

```bash
python rag.py        # assistente interativo (digite "sair" para encerrar)
python avaliar.py    # avaliação da busca, sem chamar o Claude
python chunks.py     # lista os chunks e o número de tokens de cada um
```

Na primeira execução, o modelo de embeddings é baixado automaticamente.

Para usar com os seus próprios documentos, basta colocar arquivos `.md` na pasta `docs/`, com títulos `#` (projeto) e `##` (seções).

## Estrutura

```
docs/          # READMEs dos meus projetos (a base de conhecimento)
chunks.py      # leitura dos .md, chunking e modelo de embeddings
rag.py         # busca + montagem do prompt + chamada ao Claude
avaliar.py     # avaliação da busca com perguntas e respostas esperadas
main.py        # 1º passo do estudo: uma chamada simples à API
chat.py        # 2º passo: chat no terminal com histórico
busca.py       # 3º passo: busca por similaridade, sem LLM
```

Os três últimos arquivos mostram a evolução do estudo até o RAG completo.

## O que eu aprendi

- **O LLM não aprende os documentos.** Nada é treinado: o Claude responde bem porque lê os trechos certos no prompt. O trabalho está em escolher esses trechos.
- **A busca é o gargalo.** Em todos os erros, o Claude recebeu os trechos errados e respondeu "não encontrei", que é o comportamento certo.
- **Escrever bem é metade do RAG.** Melhorar o texto dos READMEs rendeu mais do que trocar o modelo.
- **Maior não é automaticamente melhor.** Sem a avaliação, eu teria trocado para o modelo maior achando que melhorou.
- **Medir antes de mexer.** A mesma lógica dos testes automatizados que uso no dia a dia com Vitest e Jest.

## Limitações e próximos passos

- **Avaliação pequena:** 10 perguntas, e algumas foram usadas para guiar os ajustes. O próximo passo é criar perguntas novas, que não influenciaram nenhuma decisão, para medir de forma justa.
- **Busca híbrida:** combinar a busca por significado com uma busca por palavras exatas (BM25), já que os dois modelos testados erram por motivos diferentes.
- **Cabeçalho completo:** incluir o caminho todo dos títulos (`Projeto > Regras de risco > Hipertensos`) em vez de só o último.
- **Avaliar as respostas, não só a busca:** conferir se o Claude responde certo, e não apenas se recebe o trecho certo.
- **Comparar com "mandar tudo":** os documentos atuais são pequenos e caberiam inteiros no prompt. Vale medir acertos e custo do RAG contra essa alternativa.
- **Embeddings recalculados a cada execução:** com muitos documentos, valeria salvar os vetores em disco ou num banco vetorial.
