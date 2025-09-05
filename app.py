import streamlit as st
import io, sys, hashlib, builtins, requests, re, json, urllib.parse, hmac
import pandas as _pd

# --- Execução isolada com timeout (1 processo por caso) ---
TIME_LIMIT_SEC = float(st.secrets.get("TIME_LIMIT_SEC", 2.0))   # ajuste via secrets se quiser
OUTPUT_LIMIT   = int(st.secrets.get("OUTPUT_LIMIT", 10000))     # corta saídas gigantes

# Em Windows/local, garantir 'spawn' evita problemas com multiprocessing
try:
    import multiprocessing as _mp
    _mp.set_start_method("spawn", force=True)
except Exception:
    pass

def _worker_exec(code: str, input_text: str, queue):
    """Roda o código do aluno em processo separado e devolve (status, texto)."""
    import io, sys, builtins
    lines = (input_text or "").splitlines(True)
    it = iter(lines)
    def fake_input(prompt=""):
        try:
            return next(it).rstrip("\n")
        except StopIteration:
            raise EOFError("faltou entrada para input()")
    old_stdin, old_stdout = sys.stdin, sys.stdout
    old_input = builtins.input
    sys.stdin = io.StringIO(input_text or "")
    sys.stdout = io.StringIO()
    builtins.input = fake_input
    try:
        exec(code or "", {})
        out = sys.stdout.getvalue()
        queue.put(("ok", out))
    except Exception as e:
        queue.put(("exc", f"{type(e).__name__}: {e}"))
    finally:
        sys.stdin, sys.stdout = old_stdin, old_stdout
        builtins.input = old_input

def run_user_code(code: str, input_text: str, time_limit: float = TIME_LIMIT_SEC, output_limit: int = OUTPUT_LIMIT):
    import multiprocessing as mp
    q = mp.Queue()
    p = mp.Process(target=_worker_exec, args=(code, input_text, q))
    p.start()
    p.join(time_limit)

    if p.is_alive():
        p.terminate()   # corta loop infinito
        p.join(0.1)
        return "timeout", "Tempo esgotado (possível loop infinito)"

    try:
        status, out = q.get_nowait()
    except Exception:
        status, out = ("exc", "Sem saída (erro desconhecido)")

    if isinstance(out, str) and len(out) > output_limit:
        out = out[:output_limit] + "\n... (truncado)"
    return status, out

# =========================
# Configurações do app
# =========================
st.set_page_config(page_title="Lista 1 — Meninas Programadoras", layout="centered")

# Segredos (defina no secrets.toml ou nas Secrets do Streamlit Community Cloud)
GITHUB_RAW_BASE = st.secrets.get("GITHUB_RAW_BASE", "https://raw.githubusercontent.com/mgpimentel/xyzist3st3s/main/r")
SECRET_KEY = st.secrets.get("SECRET_KEY", "troque-por-uma-chave-secreta")
FORM_URL = st.secrets.get("FORM_URL", "https://docs.google.com/forms/d/e/SEU_FORM_ID/viewform")
ENTRY_ID = st.secrets.get("ENTRY_ID", {
    "ident": "entry.11111111111",
    "lista": "entry.22222222222",
    "ex":    "entry.33333333333",
    "ok":    "entry.4444444444",
    "tot":   "entry.5555555555",
    "code":  "entry.6666666666",
    "sig":   "entry.7777777777",
})
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", None)

LISTA_ID = "Lista 1"

# =========================
# Enunciados (EXATOS da Lista 1 que você forneceu)
# =========================
ENUNCIADOS = {
  "ex1": "*EX1 — Fila com senha #1.*\\n\\nDado o número que está no painel, informe qual é o próximo número a ser chamado.\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n7\\n```\\nO programa imprime:\\n```\\n8\\n```",
  "ex2": "*EX2 — Fila com senha #2.*\\n\\nDado o número do seu papel de senha, informe qual número estará no painel imediatamente antes da sua vez.\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n42\\n```\\nO programa imprime:\\n```\\n41\\n```",
  "ex3": "*EX3 — Fila com senha #3.*\\n\\nDado o seu número de senha e o número atualmente no painel (nessa ordem), informe quantas pessoas faltam para chegar a sua vez.\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n50\\n45\\n```\\nO programa imprime:\\n```\\n5\\n```",
  "ex4": "*EX4 — Vacinação em dobro.*\\n\\nEm uma campanha especial, cada pessoa recebe duas doses no mesmo dia. Dado o número de pessoas atendidas, informe o total de doses aplicadas.\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n5\\n```\\nO programa imprime:\\n```\\n10\\n```",
  "ex5": "*EX5 — Vacinação da semana.*\\n\\nInforme o total de vacinas aplicadas somando os 7 valores (um por linha) correspondentes aos dias de uma semana.\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n10\\n0\\n5\\n5\\n0\\n0\\n2\\n```\\nO programa imprime:\\n```\\n22\\n```",
  "ex6": "*EX6 — Presente?*\\n\\nVocê está conferindo presença em uma chamada. Cada linha contém *P* (presente) ou *A* (ausente). A sequência termina com um ponto final `.`.\\n\\nInforme quantas presenças foram registradas.\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\nP\\nA\\nP\\nP\\n.\\n```\\nO programa imprime:\\n```\\n3\\n```",
  "ex7": "*EX7 — Calculadora particular.*\\n\\nDados dois valores (um por linha), imprima quatro linhas na ordem: soma, diferença (primeiro menos segundo), produto e quociente (primeiro dividido pelo segundo). Use duas casas decimais.\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n5\\n2\\n```\\nO programa imprime:\\n```\\n7.00\\n3.00\\n10.00\\n2.50\\n```",
  "ex8": "*EX8 — Feliz Aniversário!*\\n\\nDado um nome (uma linha), imprima a mensagem: `Feliz aniversário, NOME!`\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\nMaria\\n```\\nO programa imprime:\\n```\\nFeliz aniversário, Maria!\\n```",
  "ex9": "*EX9 — Chego em 91 minutos...*\\n\\nDada uma hora no formato `HH:MM` (24h), informe o horário que será 91 minutos depois.\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n13:00\\n```\\nO programa imprime:\\n```\\n14:31\\n```",
  "ex10": "*EX10 — Dados para uma compra consciente.*\\n\\nDadas duas linhas, o *saldo disponível* e o *preço de um item*, informe o valor restante caso a compra seja realizada. Use duas casas decimais.\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n100\\n80\\n```\\nO programa imprime:\\n```\\n20.00\\n```"
}

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _normalize(s: str, mode: str = "strip") -> str:
    s = s.replace("\\r\\n", "\\n").replace("\\r", "\\n")
    if mode == "strip":
        return s.strip()
    if mode == "rstrip":
        return s.rstrip()
    if mode == "lstrip":
        return s.lstrip()
    return s

@st.cache_data(show_spinner=False, ttl=600)
def load_tests_from_github(tag: str):
    m = re.search(r'(\\d+)', str(tag))
    n = m.group(1) if m else str(tag)
    urls = [
        f"{GITHUB_RAW_BASE}/ex{n}.json",
        f"{GITHUB_RAW_BASE}/c{n}.json",
    ]
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        headers["Accept"] = "application/vnd.github.raw+json"
    last_err = None
    for url in urls:
        try:
            r = requests.get(url, timeout=20, headers=headers or None)
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
# UI e lógica
# =========================
if "codes" not in st.session_state:
    st.session_state["codes"] = {f"ex{i}": "" for i in range(1, 11)}
if "results" not in st.session_state:
    st.session_state["results"] = {}

def render_dashboard(target_placeholder):
    rows = []
    for i in range(1, 11):
        k = f"ex{i}"
        res = st.session_state["results"].get(k)
        ok, tot = (res if res else (0, 0))
        status = "— não avaliado —" if tot==0 else ("✅ completo" if ok==tot else ("🔴 0 acertos" if ok==0 else "🟡 parcial"))
        rows.append({"Exercício": k.upper(), "Acertos": f"{ok}/{tot}" if tot else "", "%": round((ok/tot)*100,1) if tot else "", "Status": status})
    df = _pd.DataFrame(rows)[["Exercício","Acertos","%","Status"]]
    with target_placeholder.container():
        st.subheader("📊 Seu progresso na Lista 1")
        st.dataframe(df, hide_index=True, use_container_width=True)
        valid = [r for r in rows if r["%"] != ""]
        avg = sum(r["%"] for r in valid)/len(valid) if valid else 0.0
        st.progress(min(1.0, avg/100))
        st.caption(f"Progresso médio: {avg:.1f}% nos exercícios avaliados")

dash = st.empty()
render_dashboard(dash)

st.title("Lista 1 — Pré-correção Automática (MPM.PPM.T2)")
st.markdown("Selecione o exercício, escreva seu código e rode os testes.")

ex_list = [f"ex{i}" for i in range(1, 11)]
ex = st.selectbox("Exercício", ex_list, format_func=lambda k: k.upper())
st.markdown(ENUNCIADOS[ex])

ACE_OK = False
try:
    from streamlit_ace import st_ace
    ACE_OK = True
except Exception:
    ACE_OK = False

if ACE_OK:
    current_code = st.session_state["codes"].get(ex, "")
    code = st_ace(value=current_code or "", language="python", theme="chrome", keybinding="vscode",
                  font_size=14, tab_size=4, wrap=True, show_gutter=True, show_print_margin=False,
                  auto_update=True, placeholder="# Escreva seu código aqui (use input() e print())",
                  height=340, key=f"ace_{ex}")
    st.session_state["codes"][ex] = code or ""
else:
    current_code = st.session_state["codes"].get(ex, "")
    code = st.text_area("Seu código (use input() e print())", value=current_code, height=260, key=f"code_{ex}",
                        placeholder="# Escreva seu código aqui (use input() e print())")
    st.session_state["codes"][ex] = st.session_state[f"code_{ex}"]

col1, col2 = st.columns([1,1])
with col1: rodar = st.button("Rodar avaliação", type="primary")
with col2: reset = st.button("Limpar saída")

if reset:
    st.session_state["results"].pop(ex, None)
    render_dashboard(dash)

if rodar:
    with st.spinner("Carregando casos e executando testes..."):
        try:
            bundle = load_tests_from_github(ex)
            casos = bundle["cases"]
            ok = 0; total = len(casos)
            code_to_run = st.session_state["codes"][ex]
            for i, caso in enumerate(casos, start=1):
                entrada = caso.get("entrada","")
                saida_hash = caso.get("saida_hash","")
                normalizacao = caso.get("normalizacao", bundle.get("normalizacao","strip"))
                status, out = run_user_code(code_to_run, entrada)
                if status == "exc":
                    st.error(f"Teste {i}: ERRO — {out}")
                elif status == "timeout":
                    st.error(f"Teste {i}: ERRO — {out}")
                else:
                    out_norm = _normalize(out, normalizacao)
                    h = _sha256(out_norm)
                    if h == saida_hash:
                        ok += 1; st.success(f"Teste {i}: OK")
                    else:
                        st.warning(f"Teste {i}: ERRO")
            st.info(f"*Resumo {ex.upper()}: {ok}/{total} OK*")
            st.session_state["results"][ex] = (ok, total)
            render_dashboard(dash)
        except Exception as e:
            st.error(f"Falha ao carregar/rodar testes: {e}")
