# Pacientes API — CRUD com NestJS + MongoDB (Mongoose)

API REST para cadastrar e gerenciar pacientes, feita como projeto de estudo com NestJS e TypeScript. O banco de dados é o **MongoDB**, acessado pelo **Mongoose**.

## Por que MongoDB

Nos meus outros projetos eu usei bancos relacionais (PostgreSQL). Aqui escolhi o MongoDB, um banco **não relacional** (de documentos), para ter uma primeira experiência com esse tipo de banco e entender na prática como ele funciona com o NestJS.

## Mongoose: ODM, não ORM

O Mongoose é um **ODM** (Object Document Mapper), o equivalente a um ORM para bancos de documentos. ORMs como Prisma, TypeORM e Drizzle trabalham com tabelas de bancos relacionais; o Mongoose trabalha com coleções e documentos do MongoDB. Com ele eu defini o schema do paciente, e ele cuida da conversão entre os objetos do TypeScript e os documentos do banco, além dos timestamps automáticos (`createdAt` e `updatedAt`).

## Tecnologias

- NestJS e TypeScript
- MongoDB (banco de dados não relacional), rodando num container Docker
- Mongoose (ODM)
- dotenv / @nestjs/config, para ler a variável `MONGODB_URI`

## Funcionalidades

- Cadastro, listagem, busca, atualização e remoção de pacientes (CRUD completo)
- Busca de paciente por CPF
- Tratamento de erros com status HTTP adequados (400, 404, 409)
- Timestamps automáticos (`createdAt`, `updatedAt`)

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| POST | `/pacientes` | Cadastrar paciente |
| GET | `/pacientes` | Listar todos |
| GET | `/pacientes/:cpf` | Buscar por CPF |
| PUT | `/pacientes/:id` | Atualizar por ID |
| DELETE | `/pacientes/:id` | Remover por ID |

## Como rodar

1. Suba um MongoDB com Docker (exemplo):

   ```bash
   docker run -d --name mongo -p 27017:27017 mongo
   ```

2. Crie o arquivo `.env` com a URL do banco (exemplo):

   ```
   MONGODB_URI=mongodb://localhost:27017/pacientes
   ```

3. Instale as dependências e suba a API:

   ```bash
   npm install
   npm run start:dev
   ```

## Limitações e próximos passos

- **Sem validação de CPF:** o projeto foi feito para aprender MongoDB e Mongoose, então o CPF não tem validação de formato nem dos dígitos verificadores.
- **Busca por CPF, atualização e remoção por ID:** atualizar e remover usam o `_id` do MongoDB por padrão. O mais coerente seria usar o CPF nas três rotas, que é o identificador que o usuário conhece.
- **Sem testes automatizados:** o próximo passo seria testar as rotas com Jest e Supertest.
