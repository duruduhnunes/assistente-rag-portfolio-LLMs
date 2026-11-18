# Rocket Fastify — API de Cursos e Alunos

Backend sobre matrículas de alunos em cursos, com Node.js, Fastify, Vitest e Swagger.

Este projeto é uma API RESTful para gerenciamento de cursos e alunos, construída com Fastify e Drizzle ORM, e documentada com Swagger. O objetivo é fornecer uma base robusta para aplicações educacionais, com testes automatizados end-to-end (e2e) utilizando Vitest.

## Funcionalidades

- Cadastro e listagem de cursos
- Cadastro e listagem de alunos
- Matrícula de alunos em cursos
- Filtros de busca e paginação
- Testes end-to-end (e2e) com Vitest
- Documentação automática com Swagger

## Tecnologias utilizadas

- **Fastify:** framework web rápido e eficiente para Node.js.
- **Drizzle ORM:** ORM moderno, seguro e flexível, excelente para praticar SQL e manter controle total sobre as queries.
- **Vitest:** testes rápidos e simples, com suporte a testes end-to-end.
- **Swagger:** documentação interativa da API, facilitando o uso e integração.

## Por que usar Drizzle ORM?

O Drizzle ORM é uma ótima escolha para quem deseja praticar SQL de forma segura e tipada, sem abrir mão da flexibilidade. Ele permite escrever queries SQL diretamente em TypeScript, com autocomplete e validação de tipos, tornando o desenvolvimento mais produtivo e seguro.

## Como rodar o projeto

1. Instale as dependências:

   ```bash
   npm install
   ```

2. Configure o banco de dados: edite o arquivo `.env` com as credenciais do seu banco.
3. Rode as migrations (se houver):

   ```bash
   npm run migrate
   ```

4. Inicie o servidor:

   ```bash
   npm run dev
   ```

5. Acesse a documentação Swagger, normalmente disponível em `http://localhost:3333/docs`.
6. Execute os testes e2e:

   ```bash
   npm run test
   ```

## Estrutura dos testes

Os testes end-to-end garantem que as rotas principais da API funcionam corretamente, simulando requisições reais e validando as respostas.
