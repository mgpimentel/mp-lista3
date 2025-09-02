
# Lista 3 — App (Streamlit)

App de correção automática para 12 exercícios. 
- Testes são buscados do GitHub (JSON com `cases[].entrada` e `cases[].saida_hash`).
- Envio ao final via Google Forms pré-preenchido, com assinatura HMAC (anti-alteração).

## Como usar

1. Crie um repositório no GitHub com os testes da Lista 3.
   - Coloque `ex1.json` … `ex12.json` (ou `c1.json` … `c12.json`) em uma pasta e pegue a URL **raw base**.
   - Formato esperado de cada `exN.json`:
     ```json
     {
       "hash_alg": "sha256",
       "normalizacao": "strip",
       "cases": [
         {"entrada": "3\n4\n", "saida_hash": "...."},
         {"entrada": "0\n0\n", "saida_hash": "...."}
       ]
     }
     ```

2. No **Streamlit Cloud** (Settings → Secrets) configure:
   ```toml
   GITHUB_RAW_BASE = "https://raw.githubusercontent.com/<user>/<repo>/<branch>/<path>"

   SECRET_KEY = "uma-chave-secreta-longaaaa"

   FORM_URL = "https://docs.google.com/forms/d/e/SEU_FORM_ID/viewform"
   # Mapeamento dos campos do Form (entry.xxx)
   [ENTRY_ID]
   ident = "entry.1111111111"
   lista = "entry.2222222222"
   ex    = "entry.3333333333"
   ok    = "entry.4444444444"
   tot   = "entry.5555555555"
   code  = "entry.6666666666"
   sig   = "entry.7777777777"
   ```

3. Faça o deploy no Streamlit Cloud apontando para `app.py`.

Pronto!
