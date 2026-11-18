from rag import buscar

CASOS = [
    ("com qual proposito voce criou o sistema de saude em dados utilizando machine learning?",
     ["Saúde em Dados — API",
      "Saúde em Dados — API > Consultas permitidas do chatbot",
      "Saúde em Dados — API > Modelo de Machine Learning*"]),
    ("qual modelo de machine learning voce escolheu?",
     ["Saúde em Dados — API > Modelo de Machine Learning*"]),
    ("no projeto de filas, qual lib voce usou para gerenciar as filas?",
     ["Fila de Notificações com BullMQ, Redis e NestJS*"]),
    ("qual o banco voce usou pra o projeto de filas?",
     ["Fila de Notificações com BullMQ, Redis e NestJS*"]),
    ("no PACIENTES API voce usou qual ORM ?",
     ["Pacientes API*"]),
    ("no rocket fastify, voce usou qual ORM?",
     ["Rocket Fastify — API de Cursos e Alunos",
      "Rocket Fastify — API de Cursos e Alunos > Tecnologias utilizadas",
      "Rocket Fastify — API de Cursos e Alunos > Por que usar Drizzle ORM?"]),
    ("como funciona a dead letter queue?",
     ["Fila de Notificações com BullMQ, Redis e NestJS > Dead letter queue (DLQ)"]),
    ("qual a regra de risco para hipertensos?",
     ["Saúde em Dados — API > Hipertensos — última pressão arterial"]),
    ("que banco de dados o projeto de pacientes usa?",
     ["Pacientes API*"]),
    ("qual a acuracia do modelo do chatbot?",
     ["Saúde em Dados — API > Modelo de Machine Learning*",
      "Saúde em Dados — API > Roteiro: sempre que mudar o frases.csv ou o treinar.py"]),
]

def bate(cabecalho, esperado):
    if esperado.endswith("*"):
        return cabecalho.startswith(esperado[:-1])
    return cabecalho == esperado

acertos = 0
for pergunta, esperados in CASOS:
    cabecalhos = [texto.splitlines()[0] for texto, _ in buscar(pergunta)]
    posicao = None
    for i, cabecalho in enumerate(cabecalhos, start=1):
        if any(bate(cabecalho, e) for e in esperados):
            posicao = i
            break
    if posicao:
        acertos += 1
        print(f"OK   (#{posicao}) {pergunta}")
    else:
        print(f"ERRO      {pergunta}")
        print(f"          veio em 1º: {cabecalhos[0]}")

print(f"\nAcertos: {acertos}/{len(CASOS)}")