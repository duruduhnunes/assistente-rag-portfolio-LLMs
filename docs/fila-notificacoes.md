# Fila de Notificações com BullMQ, Redis e NestJS

Projeto de estudo: uma API que recebe pedidos de notificação, coloca cada um numa fila e processa em segundo plano, com retentativas automáticas, prioridade, limite de envios por segundo e uma dead letter queue (DLQ) para os jobs que falham de vez.

O envio é **simulado**: o worker espera 2 segundos e falha de propósito em 30% das vezes, para dar para ver as retentativas e a DLQ funcionando.

**Stack:** TypeScript · NestJS 11 · BullMQ · Redis 7 · Docker Compose · Bull Board · class-validator

## Por que usar uma fila

Mandar uma notificação (e-mail, SMS) pode ser lento ou falhar por um motivo passageiro. Se a API esperasse o envio terminar, a resposta demoraria, e uma falha se perderia. Com a fila:

- a API só registra o pedido e responde na hora com o `jobId`;
- um worker processa os jobs em segundo plano;
- se o envio falhar, o job é tentado de novo sozinho, sem perder o pedido;
- o Redis guarda a fila em disco (`appendonly yes`), então os jobs pendentes sobrevivem se o Redis reiniciar.

## Como funciona

```
POST /notifications ──> fila "notifications" ──> worker (ProcessorNotification)
                         (Redis)                     │
                                                     ├─ sucesso: job concluído
                                                     ├─ falhou: retenta (até 3 vezes, com backoff)
                                                     └─ falhou 3 vezes: copia para "notifications-dlq"
```

### Tipos de notificação

| Tipo | Prioridade |
|---|---|
| `exam_result` (resultado de exame) | 1 (mais alta) |
| `appointment_reminder` (lembrete de consulta) | 10 |
| `payment_received` (pagamento recebido) | 10 |

No BullMQ, um número de prioridade menor sai primeiro. Resultado de exame passa na frente porque é o aviso mais importante para o paciente.

### Retentativa com backoff exponencial

Cada job tem `attempts: 3` e `backoff: { type: 'exponential', delay: 1000 }`. Depois de uma falha, o BullMQ espera um tempo que dobra a cada tentativa, em vez de tentar de novo na mesma hora. Isso dá tempo para um problema passageiro (um serviço de e-mail fora do ar, por exemplo) se resolver e evita martelar o serviço que já está com problema.

### Dead letter queue (DLQ)

Quando um job falha na última tentativa, o evento `failed` do worker copia os dados dele para a fila `notifications-dlq`: id original, tipo, destinatário, payload, motivo da falha, número de tentativas e data. Assim nenhum pedido some sem rastro: dá para investigar o que deu errado e reenviar depois.

### Controle de vazão

O worker usa `concurrency: 10` (até 10 jobs ao mesmo tempo) e `limiter: { max: 5, duration: 1000 }` (no máximo 5 jobs por segundo). Isso serve para respeitar o limite de envio de um provedor de e-mail ou SMS.

### Encerramento seguro (graceful shutdown)

A API chama `enableShutdownHooks()`, e o worker fecha a conexão no `onModuleDestroy`. Ao parar o servidor (Ctrl+C ou deploy), o worker termina o job que está processando antes de encerrar.

### Validação da entrada

O `ValidationPipe` global, com `whitelist` e `forbidNonWhitelisted`, recusa campos que não existem no DTO. O DTO exige:

- `type`: um dos tipos da tabela acima;
- `recipient`: um e-mail válido;
- `payload`: um objeto não vazio com os dados da notificação.

## Como rodar

Pré-requisitos: Node.js e Docker.

```bash
npm install
docker compose up -d     # sobe o Redis (porta 6378) e o Redis Commander (porta 8081)
npm run start:dev        # sobe a API em http://localhost:3000
```

O Redis fica exposto na porta **6378** do computador, e não na 6379 padrão, para não brigar com um Redis local.

## Endpoints

| Método | Rota | Para que serve |
|---|---|---|
| POST | `/notifications` | coloca uma notificação na fila e devolve `jobId` e prioridade |
| GET | `/notifications/status` | quantidade de jobs por estado: `waiting`, `active`, `completed`, `failed`, `delayed` |
| GET | `/notifications/:jobId` | estado de um job, tentativas feitas e motivo da falha |

Exemplo:

```bash
curl -X POST http://localhost:3000/notifications \
  -H "Content-Type: application/json" \
  -d '{"type": "exam_result", "recipient": "paciente@exemplo.com", "payload": {"exame": "hemograma"}}'
```

## Ferramentas de observação

- **Bull Board** em http://localhost:3000/admin/queues: painel com as duas filas (`notifications` e `notifications-dlq`), os jobs de cada estado e os erros.
- **Redis Commander** em http://localhost:8081: mostra as chaves que o BullMQ cria no Redis por baixo dos panos.

## Limitações e próximos passos

- O envio é simulado; o próximo passo seria plugar um provedor de e-mail de verdade.
- `GET /notifications/:jobId` lança um `Error` comum quando o job não existe, o que vira erro 500. O certo seria `NotFoundException` (404).
- O `POST` devolve `status: 202` no corpo da resposta, mas o código HTTP é o padrão do Nest para POST (201). Dá para corrigir com `@HttpCode(202)`.
- A conexão com o Redis (`localhost:6378`) está fixa no código; o ideal é ler do `.env`.
- Ainda não há testes do fluxo da fila (só os testes de exemplo gerados pelo Nest).
- Não existe rota para reprocessar os jobs da DLQ.
