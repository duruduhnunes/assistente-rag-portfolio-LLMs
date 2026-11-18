from dotenv import load_dotenv
load_dotenv()

import anthropic

client = anthropic.Anthropic()

SISTEMA= "Você é um assistente que ajuda uma desenvolvedora júnior. Responda em português, de forma curta e clara."

HISTORICO = []

print("Chat iniciado. Digite 'sair' para encerrar.")

while True:
    pergunta = input("Voce: ")
    if pergunta.strip().lower() == "sair":
        break

    HISTORICO.append({"role": "user", "content": pergunta})

    resposta = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=500,
        system=SISTEMA,
        messages=HISTORICO,
    )

    texto = "".join(bloco.text for bloco in resposta.content if bloco.type == "text")
    print(f"\nClaude: {texto}\n")

    HISTORICO.append({"role": "assistant", "content": texto})