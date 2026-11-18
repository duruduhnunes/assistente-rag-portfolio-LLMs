from dotenv import load_dotenv
load_dotenv()

import anthropic

client = anthropic.Anthropic()

resposta = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=500,
    messages=[
        {"role": "user", "content": "Explique em 3 linhas o que é uma fila com retry e DLQ."}
    ],
)

print(resposta.content[0].text)