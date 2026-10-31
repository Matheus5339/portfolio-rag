# Álbum de Figurinhas — UCP

<p align="center">
  <img alt=".NET 10"      src="https://img.shields.io/badge/.NET-10-512BD4?logo=dotnet&logoColor=white">
  <img alt="C#"           src="https://img.shields.io/badge/C%23-239120?logo=csharp&logoColor=white">
  <img alt="React 19"     src="https://img.shields.io/badge/React-19.2-61DAFB?logo=react&logoColor=black">
  <img alt="Vite 8"       src="https://img.shields.io/badge/Vite-8.0-646CFF?logo=vite&logoColor=white">
  <img alt="TypeScript 6" src="https://img.shields.io/badge/TypeScript-6.0-3178C6?logo=typescript&logoColor=white">
  <img alt="Tailwind 4"   src="https://img.shields.io/badge/Tailwind-4.3-06B6D4?logo=tailwindcss&logoColor=white">
  <img alt="SQLite"       src="https://img.shields.io/badge/SQLite-3.53-003B57?logo=sqlite&logoColor=white">
  <img alt="Testes"       src="https://img.shields.io/badge/backend-26%2F26-3FB950">
</p>

Sistema para simular um **álbum de figurinhas virtual** (trabalho de Programação Orientada a Objeto — UCP),
com três perfis de acesso, autenticação, tag MD5 das imagens e armazenamento das fotos no banco.

> **Status:** backend **26/26 testes**; frontend com typecheck/lint/testes limpos e integração validada
> fim a fim. Instruções de execução e entrega em [`docs/ENTREGA.md`](./docs/ENTREGA.md).

## Fonte normativa

O arquivo [`instrucoes-figurinhas.txt`](./instrucoes-figurinhas.txt) é a **regra superior** deste projeto.

## Perfis e funcionalidades

- **Administrador** — gerencia os usuários: inserir, remover, editar, **filtrar** e **zerar a senha** (padrão `123456`).
- **Autor** — cria/edita o **único álbum** (nome, páginas, capa) e as **figurinhas**: inserir, remover, editar,
  filtrar e limpar todas. A **tag** de cada figurinha é o **hash MD5** da imagem (calculado automaticamente).
  Inclui **exportar/importar** figurinhas em arquivo **texto** e **binário**.
- **Colecionador** — visualiza as páginas do álbum e suas figurinhas (duplo clique mostra os detalhes) e
  **adquire figurinhas** informando a **tag**.

Todos podem trocar o próprio login e senha (não o perfil). Telas de **splash** e **sobre** incluídas.

## Tecnologias

- **Backend:** .NET 10 (C#), EF Core + SQLite, Clean Architecture, JWT + refresh token httpOnly, Argon2id.
- **Frontend:** React 19.2.6, Vite 8.0.14, Tailwind 4.3.0, shadcn 3.2.1, TypeScript 6.0.2, Node.js 24.16.0.

## Execução rápida

```bash
# Backend (requer SDK .NET 10) — porta 5080
cd src/Backend
dotnet run --project Api

# Frontend (requer Node.js 24.x) — porta 5173
cd src/Frontend
npm install
npm run dev
```

Acesse **http://localhost:5173**. Usuários iniciais (senha `123456`): **`admin`**, **`autor`**, **`colecionador`**.

## Segurança

- Senhas com **Argon2id** (MD5/SHA-256 simples proibidos para senhas). O **MD5** é usado **somente** para a tag da imagem.
- JWT de curta duração + **refresh token em cookie httpOnly** com rotação/revogação.
- Autorização por perfil; segredos via variáveis de ambiente / user secrets — nunca no repositório.

## Documentação

- [`instrucoes-figurinhas.txt`](./instrucoes-figurinhas.txt) — normativo do projeto
- [`docs/ENTREGA.md`](./docs/ENTREGA.md) — execução, credenciais e entrega
- [`DECISOES.md`](./DECISOES.md) · [`PENDENCIAS.md`](./PENDENCIAS.md) · [`RASTREAMENTO.md`](./RASTREAMENTO.md)
