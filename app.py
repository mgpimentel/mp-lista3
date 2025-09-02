import streamlit as st
import io, sys, hashlib, builtins, requests, re, json, pathlib, urllib.parse, hmac

# =========================
# Configurações do app
# =========================
st.set_page_config(page_title="Lista 3 — Meninas Programadoras", page_icon="🧪", layout="centered")

# Onde estão os testes (JSON) no GitHub (pode ser repo público ou privado com raw access)
GITHUB_RAW_BASE = st.secrets.get("GITHUB_RAW_BASE", "https://raw.githubusercontent.com/mgpimentel/xyzist3st3s/main/t")

# Chave secreta para assinar o envio
SECRET_KEY = st.secrets.get("SECRET_KEY", "troque-por-uma-chave-secreta")

# Google Form (viewform) e os IDs dos campos (entry.xxxxx)
FORM_URL = st.secrets.get("FORM_URL", "https://docs.google.com/forms/d/e/SEU_FORM_ID/viewform")
ENTRY_ID = st.secrets.get("ENTRY_ID", {
    "ident": "entry.1111111111",
    "lista": "entry.2222222222",
    "ex":    "entry.3333333333",
    "ok":    "entry.4444444444",
    "tot":   "entry.5555555555",
    "code":  "entry.6666666666",
    "sig":   "entry.7777777777",
})

LISTA_ID = "LISTA3"

# =========================
# Enunciados
# =========================
ENUNCIADOS = {
    "ex1": """**EX1 — Resultado da soma de dois números inteiros**
Leia dois inteiros (um por linha) e imprima a soma.
**Exemplo**
Entrada:
```
3
4
```
Saída:
```
7
```""",
    "ex2": """**EX2 — Pode comprar**
Dados dois inteiros (saldo e valor do item), imprima `pode comprar` se saldo ≥ valor, senão `não pode comprar`.
**Exemplo**
Entrada:
```
100
50
```
Saída:
```
pode comprar
```""",
    "ex3": """**EX3 — Vogal maiúscula**
Dada uma letra, verificar se é uma **vogal maiúscula**. Imprima `vogal` ou `não vogal`.
**Exemplo**
Entrada:
```
A
```
Saída:
```
vogal
```""",
    "ex4": """**EX4 — Ler até atingir alvo**
Dado um valor inteiro **alvo**, leia inteiros (um por linha) até que a **soma** dos valores lidos **atinja ou ultrapasse** o alvo. Não imprimir nada durante as leituras; ao final, imprimir a soma obtida.
**Exemplo**
Entrada:
```
10
3
4
5
```
Saída:
```
12
```""",
    "ex5": """**EX5 — Contar positivos até negativo**
Leia inteiros até que apareça um **valor negativo**. Informe **quantos valores positivos** foram lidos (não contar o negativo).
**Exemplo**
Entrada:
```
1
2
0
-1
```
Saída:
```
3
```""",
    "ex6": """**EX6 — Ler nomes até o alvo**
Dado um **nome-alvo** na primeira linha, leia nomes (um por linha) até que um nome **igual ao alvo** seja dado. Informe **quantos nomes** foram lidos **antes** do alvo.
**Exemplo**
Entrada:
```
ana
bia
bia
ana
```
Saída:
```
2
```""",
    "ex7": """**EX7 — Igualdade salarial (pares H, M)**
Leia **pares** de salários `H` (homem) e `M` (mulher) — dois números float em **linhas separadas** para a mesma posição. O último par contém `-1` e `-1` e **não conta**. Informe **em quantos pares** `M == H`.
**Exemplo**
Entrada:
```
1000.0
1000.0
2000.0
2500.0
-1
-1
```
Saída:
```
1
```""",
    "ex8": """**EX8 — Comparação salarial (pares H, M)**
Mesmo formato do EX7. Informe, considerando apenas os pares válidos, **três números**: 
`mesmo` `mais` `menos` — respectivamente, em quantos pares `M == H`, `M > H` e `M < H`.
**Exemplo**
Entrada:
```
1000.0
1000.0
2000.0
2500.0
-1
-1
```
Saída:
```
1 1 0
```""",
    "ex9": """**EX9 — Saldo do caixa**
Dados valores de **entrada** (positivos) e **saída** (negativos) de um caixa de banco, informe o **saldo final**. A entrada termina com valor **0** (não conta).
**Exemplo**
Entrada:
```
100
-30
-20
0
```
Saída:
```
50
```""",
    "ex10": """**EX10 — Calorias do dia**
Dados valores de **consumo de calorias** por alimentos (positivos) e **gasto de energia** (negativos), informe **consumidas gastas saldo** ao final do dia. A entrada termina com **0**.
**Exemplo**
Entrada:
```
300
-100
250
-50
0
```
Saída:
```
550 150 400
```""",
    "ex11": """**EX11 — Ocorrência de palavra-alvo por linha**
Dada uma **palavra-alvo** (primeira linha) e um conjunto de linhas **terminado por uma linha contendo apenas um ponto final `.`**, informe **em quantas linhas** a palavra-alvo ocorre (casamento simples, sensível a maiúsculas/minúsculas).
**Exemplo**
Entrada:
```
ana
ana e bia
ANA
bananal
.
```
Saída:
```
2
```""",
    "ex12": """**EX12 — Contagem de gênero**
Dada uma sequência de linhas **terminadas com `.`**, cada linha com `M` ou `F`, informe **quantas ocorrências** de cada gênero foram registradas, no formato `M F`.
**Exemplo**
Entrada:
```
M
F
F
.
```
Saída:
```
1 2
```"""
}

# =========================
# Templates (sem solução)
# =========================
TEMPLATES = { ex: f"#EXERCICIO: {ex}\n# escreva seu código aqui\n" for ex in ENUNCIADOS.keys() }

# =========================
# Execução segura
# =========================
def _sha256(s: str) -> str:
    return hashlib.sha256(s.strip().encode("utf-8")).hexdigest()

def run_user_code(code: str, input_text: str):
    lines = input_text.splitlines(True)
    it = iter(lines)
    def fake_input(prompt=""):
        try:
            return next(it).rstrip("\n")
        except StopIteration:
            raise EOFError("faltou entrada para input()")
    old_stdin, old_stdout = sys.stdin, sys.stdout
    old_input = builtins.input
    sys.stdin = io.StringIO(input_text)
    sys.stdout = io.StringIO()
    builtins.input = fake_input
    try:
        exec(code, {})
        return "ok", sys.stdout.getvalue()
    except Exception as e:
        return "exc", f"{type(e).__name__}: {e}"
    finally:
        sys.stdin, sys.stdout = old_stdin, old_stdout
        builtins.input = old_input

# =========================
# Carregar testes
# =========================
@st.cache_data(show_spinner=False, ttl=600)
def load_tests_from_github(tag: str):
    m = re.search(r'(\d+)', str(tag))
    n = str(int(m.group(1))) if m else str(tag)
    urls = [
        f"{GITHUB_RAW_BASE}/ex{n}.json",
        f"{GITHUB_RAW_BASE}/c{n}.json",
    ]
    last_err = None
    for url in urls:
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            data = r.json()
            cases = data.get("cases", data if isinstance(data, list) else [])
            return {
                "cases": cases,
                "hash_alg": data.get("hash_alg", "sha256"),
                "normalizacao": data.get("normalizacao", "strip")
            }
        except Exception as e:
            last_err = e
    raise last_err or RuntimeError("Não foi possível carregar os testes.")

# =========================
# Assinatura HMAC
# =========================
def sign_submission(ident: str, lista: str, ex: str, ok: int, tot: int, code: str) -> str:
    payload = f"{ident}|{lista}|{ex}|{ok}|{tot}|{_sha256(code)}"
    return hmac.new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

def prefilled_form_url(ident: str, lista: str, ex: str, ok: int, tot: int, code: str) -> str:
    sig = sign_submission(ident, lista, ex, ok, tot, code)
    params = {
        ENTRY_ID["ident"]: ident,
        ENTRY_ID["lista"]: lista,
        ENTRY_ID["ex"]:    ex,
        ENTRY_ID["ok"]:    str(ok),
        ENTRY_ID["tot"]:   str(tot),
        ENTRY_ID["code"]:  code,
        ENTRY_ID["sig"]:   sig,
    }
    return f"{FORM_URL}?{urllib.parse.urlencode(params)}"

# =========================
# UI
# =========================
st.title("Lista 3 — Correção Automática (MP)")
st.markdown("Selecione o exercício, escreva seu código, rode os testes e **envie sua resposta** pelo formulário.")

ex_list = [f"ex{i}" for i in range(1,13)]
ex = st.selectbox("Exercício", ex_list, format_func=lambda k: k.upper())

st.markdown(ENUNCIADOS[ex])

code = st.text_area("Seu código (use input() e print())", value=TEMPLATES[ex], height=260)

col1, col2 = st.columns([1,1])
with col1:
    if st.button("Rodar avaliação", type="primary"):
        st.session_state["_run"] = True
with col2:
    reset = st.button("Limpar saída")

if reset:
    st.session_state.pop("_result", None)
    st.session_state.pop("_run", None)

if st.session_state.get("_run"):
    try:
        bundle = load_tests_from_github(ex)
        casos = bundle["cases"]
        ok = 0
        total = len(casos)
        for i, caso in enumerate(casos, start=1):
            entrada = caso.get("entrada", "")
            saida_hash = caso.get("saida_hash", "")
            status, out = run_user_code(code, entrada)
            if status == "exc":
                st.error(f"Teste {i}: **ERRO** — {out}")
            else:
                h = _sha256(out)
                if h == saida_hash:
                    ok += 1
                    st.success(f"Teste {i}: OK")
                else:
                    st.warning(f"Teste {i}: ERRO")
        st.info(f"**Resumo {ex.upper()}: {ok}/{total} OK**")
        st.session_state["_result"] = (ok, total, code)
    except Exception as e:
        st.error(f"Falha ao carregar/rodar testes: {e}")

st.divider()
st.subheader("Enviar este exercício")

ident = st.text_input("Identificador (RA/USP ou e-mail)", "")
ok_tot = st.session_state.get("_result")
disabled = ok_tot is None or not ident.strip()

if st.button("Gerar formulário pré-preenchido", disabled=disabled):
    if not ok_tot:
        st.warning("Rode a avaliação antes de enviar.")
    elif not ident.strip():
        st.warning("Preencha o identificador.")
    else:
        ok, tot, code_sent = ok_tot
        url = prefilled_form_url(ident.strip(), LISTA_ID, ex.upper(), ok, tot, code_sent)
        st.link_button("Abrir Google Form pré-preenchido", url)

st.caption("⚠️ As entradas e saídas dos testes não são exibidas. O formulário registra seu código, placar e uma assinatura para verificação.")
