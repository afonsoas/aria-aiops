# Redeploy da API ARIA no Render (free tier)

A API original no Railway (`aria-api-production.up.railway.app`) foi desativada
(plano free expirado). Este guia sobe a mesma API no Render usando o
`render.yaml` que já está na raiz do repo. Tempo estimado: ~15 min.

## Passo a passo

1. **Criar conta / logar** em <https://render.com> (pode usar o login do GitHub).

2. **New → Blueprint** e aponte para o repo `afonsoas/aria-aiops`.
   O Render lê o `render.yaml` e cria o serviço `aria-aiops-api` (Docker, plano free).

3. **Preencher as env vars secretas** quando o Render pedir
   (são as mesmas que estavam no Railway):

   | Variável | Valor |
   |---|---|
   | `ARIA_DB_USER` | `ADMIN` |
   | `ARIA_DB_PASSWORD` | senha do Oracle ADB |
   | `ARIA_DB_DSN` | DSN do tnsnames (ex.: `ariaaiops_high`) ou `host:porta/servico` |
   | `ARIA_WALLET_PASSWORD` | senha do wallet |
   | `ARIA_WALLET_EWALLET_B64` | `base64 -w0 ewallet.pem` do wallet OCI |
   | `ARIA_WALLET_TNSNAMES_B64` | `base64 -w0 tnsnames.ora` do wallet OCI |

   > Sem essas vars a API sobe em **modo offline** (predições funcionam,
   > histórico no banco fica desativado) — suficiente para a demo.

4. **Deploy** e aguardar o build (~5 min). A URL final será algo como
   `https://aria-aiops-api.onrender.com`.

5. **Validar:** `curl https://<url>/health` deve retornar
   `{"status":"ok","modelos_carregados":true,...}`.

## Pós-deploy — atualizar a URL nos consumidores

- [ ] Streamlit Cloud → Settings → Secrets: `ARIA_API_URL = "https://<url>"`
- [ ] `README.md` — badge da API, tabela de links e exemplos de curl
- [ ] `.github/workflows/keepalive.yml` — descomentar o `schedule` e trocar a URL
- [ ] PPT Sprint 3 e Sprint 4 — slides que citam a URL do Railway
- [ ] (Opcional) `ARIA_API_KEY` como env var no Render para proteger os
      endpoints de escrita — ver seção "Autenticação" no README

## Atenção ao free tier do Render

O serviço **hiberna após 15 min sem tráfego** e o primeiro request leva
~50 s para acordar. Antes de demo/vídeo: fazer um `curl /health` 2 min antes.
O `keepalive.yml` (a cada 5 dias) mantém o Oracle ADB ativo, mas não impede
a hibernação do Render — para isso seria preciso um ping a cada ~10 min
(cron-job.org resolve, ou aceitar o cold start).
