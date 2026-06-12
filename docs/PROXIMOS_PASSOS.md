# Próximos passos (roadmap pós-entrega)

Lista de melhorias planejadas, **fora do escopo das Fases 1–5**. Cada
item está classificado por esforço (pequeno/médio/grande) e benefício
(operacional, acadêmico ou ambos). Use como base para um próximo
trabalho ou para extensões da pesquisa.

---

## Empacotamento e deploy

### Dockerfile da API
- **Esforço:** pequeno · **Benefício:** operacional.
- Imagem Python slim com `uvicorn` rodando `api.main:app`.
- `EXPOSE 8000`, `HEALTHCHECK` no endpoint `/api/health`.
- Multi-stage build se quiser pré-compilar `psycopg2-binary`.

### Dockerfile do frontend
- **Esforço:** pequeno · **Benefício:** operacional.
- Build com Node 20 → estágio final servindo o `dist/` com Nginx
  alpine.
- Variável de ambiente `VITE_API_BASE_URL` substituída no momento do
  build (não em runtime — limitação de SPA estática).

### docker-compose completo (postgres + api + frontend)
- **Esforço:** médio · **Benefício:** operacional.
- Adicionar serviços `api` e `frontend` ao `docker-compose.yml`.
- Rede interna para isolar Postgres; expor apenas portas 8000 e 3000.
- `depends_on` com `condition: service_healthy` para a API só subir
  após o Postgres estar pronto.

### Deploy online
- **Esforço:** médio · **Benefício:** operacional.
- API + Postgres em um VPS (Hetzner, DigitalOcean) ou em um PaaS
  (Fly.io, Railway).
- Frontend estático em Cloudflare Pages, Vercel ou Netlify.
- Domínio próprio + HTTPS via Let's Encrypt.
- **Atenção:** revisar CORS e ajustar `BENCHMARK_IDS_EXCLUIR` para
  ambiente de produção.

---

## Engenharia de software

### Testes automatizados
- **Esforço:** médio · **Benefício:** operacional.
- Backend: `pytest` cobrindo os routers principais (health, ao menos um
  endpoint de dimensão, um de análise, um de benchmark). Banco de
  teste em container efêmero (`testcontainers-python` ou
  `pytest-postgresql`).
- Frontend: `vitest` + `@testing-library/react` para componentes de
  formatação e para o `QueryBoundary`.
- CI: GitHub Actions ou GitLab CI rodando lint + typecheck + testes
  em todo push.

### Otimização de chunks do frontend
- **Esforço:** pequeno · **Benefício:** operacional.
- Code-splitting por rota via `React.lazy` + `Suspense`.
- Configurar `manualChunks` em `vite.config.ts` para separar
  `recharts` em um chunk dedicado.
- Atualmente o build emite aviso de chunk > 500 kB — informativo,
  não é erro.

### Atualização do Recharts para a v3
- **Esforço:** médio · **Benefício:** operacional + acadêmico.
- A v3 traz API revisada (alguns componentes mudam de assinatura).
- Não fazer durante a janela de entrega — alto risco de regressão
  visual nos 8 gráficos.
- Plano: criar uma branch dedicada, migrar gráfico por gráfico
  validando contra `npm run preview`.

### CI/CD
- **Esforço:** médio · **Benefício:** operacional.
- Pipeline com 3 estágios: lint/typecheck → build (api e frontend) →
  deploy (se branch = main).
- Cache de `node_modules` e `pip` entre runs.
- Publicar imagens Docker no GHCR/GitLab Registry.

---

## Funcionalidades

### Autenticação
- **Esforço:** médio · **Benefício:** operacional.
- API com JWT (FastAPI + `python-jose`). Login simples para a
  apresentação online.
- Frontend com tela de login e armazenamento do token em `httpOnly`
  cookie.
- **Reflexão:** só faz sentido se a API for exposta na internet. No
  ambiente acadêmico local, é overhead.

### Exportação de gráficos
- **Esforço:** pequeno · **Benefício:** acadêmico.
- Botão "Exportar PNG" em cada gráfico, usando
  `recharts` + `dom-to-image-more` ou `html2canvas`.
- Botão "Exportar CSV" usando o próprio endpoint da API + `Blob`.
- Útil para alunos que quiserem inserir os gráficos em artigos.

### Tema escuro
- **Esforço:** pequeno · **Benefício:** estético.
- Tailwind já suporta `dark:` modificador.
- Adicionar `<button>` no header com `useTheme()` armazenado em
  `localStorage`.

### i18n
- **Esforço:** médio · **Benefício:** acadêmico.
- Adicionar `react-i18next` para suportar inglês — útil em
  publicações internacionais.

---

## Pesquisa / experimentos adicionais

### Mais pontos no curva de speedup
- **Esforço:** pequeno · **Benefício:** acadêmico.
- Rodar benchmarks com 3, 6 e 8 workers além dos 2 e 4 atuais.
- Gerar o gráfico clássico de speedup vs. número de workers e
  ajustar a curva de Amdahl ao dado real para estimar a fração
  paralela `p`.

### Profiling do gargalo
- **Esforço:** médio · **Benefício:** acadêmico.
- Usar `cProfile` ou `py-spy` no script paralelo para quantificar
  quanto tempo é I/O, parsing pandas e `COPY` no Postgres.
- Pode comprovar empiricamente a hipótese de gargalo de I/O.

### Comparar com Dask/Spark
- **Esforço:** grande · **Benefício:** acadêmico.
- Reescrever o ETL em Dask (ou PySpark local) e medir overhead vs.
  ganho.
- Hipótese: para 24k linhas, o overhead supera o ganho. Vale o
  experimento.

### Particionar o banco
- **Esforço:** médio · **Benefício:** acadêmico.
- Particionar `fato_enade` por `nu_ano` no Postgres e medir impacto
  no `COPY` paralelo.

---

## Documentação

### Vídeo de demo
- **Esforço:** pequeno · **Benefício:** divulgação.
- Gravar 3–5 minutos navegando pelo dashboard e mostrando o
  comparativo. Útil para portfolio.

### Artigo técnico
- **Esforço:** grande · **Benefício:** acadêmico.
- Estruturar como paper curto (4–6 páginas) descrevendo o
  experimento, a metodologia e os resultados — bom material para
  iniciar uma publicação em workshop de SPD.

---

## O que **não** virá agora (intencionalmente)

- Reescrever a API em async puro (sem ganho real com Postgres
  síncrono).
- Trocar Recharts por D3 puro (mais flexível, mas custo de
  desenvolvimento maior que o ganho).
- Mover para microsserviços (escopo errado para o tamanho do
  projeto).
- Adicionar Redis ou cache externo (a API já está rápida o suficiente
  com o pool de conexões).
