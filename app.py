
import streamlit as st
import io, sys, hashlib, builtins, requests, re
import streamlit.components.v1 as components

# =========================
# Configurações do app
# =========================
st.set_page_config(page_title="Lista 3 — Pré-correção automática (MP)", layout="centered")

# --- Compactar layout / fontes ---
st.markdown("""
<style>
.block-container {padding-top: 1.0rem; padding-bottom: 0.8rem;}
h1 {font-size: 1.55rem; margin-bottom: 0.4rem;}
[data-testid="stDataFrame"] div[role="grid"] {font-size: .88rem;}
.stButton>button {padding: .35rem .75rem; font-size: .9rem;}
.ace_editor {font-size: 13px; line-height: 1.35;}
[data-testid="stElementToolbar"] {display: none !important;}
/* linhas/headers da tabela mais finos */
[data-testid="stDataFrame"] div[role="columnheader"], 
[data-testid="stDataFrame"] div[role="row"] { padding-top: 2px; padding-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

def _scroll_to_top():
    components.html("<script>window.parent.scrollTo(0, 0);</script>", height=0)

# Se um rerun anterior pediu para subir a página, faça isso aqui no topo
if st.session_state.get("_go_top"):
    _scroll_to_top()
    st.session_state["_go_top"] = False

# -------------------------
# Segredos (RAW base no GitHub)
# -------------------------
_owner = st.secrets.get("GITHUB_OWNER")
_repo = st.secrets.get("GITHUB_REPO")
_branch = st.secrets.get("GITHUB_TESTS_BRANCH")
_dir = st.secrets.get("GITHUB_TESTS_DIR")

if _owner and _repo and _branch and _dir:
    GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{_owner}/{_repo}/{_branch}/{_dir}"
else:
    GITHUB_RAW_BASE = st.secrets.get("GITHUB_RAW_BASE", "https://raw.githubusercontent.com/mgpimentel/xyzist3st3s/main/t")

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", None)  # opcional p/ repo privado

# =========================
# Enunciados (versão MPM)  — (omitidos aqui por brevidade, use os seus existentes)
# =========================
ENUNCIADOS = {
    "ex1": "*EX1 — Dados o número de execicios que uma aluna resolveu nas duas primeiras listas, calcule quantos exercícios ela resolveu no total.*\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n7\\n8\\n```\\nO programa imprime:\\n```\\n15\\n```",
    "ex2": "*EX2 — Você está ajudando a professora do Fundamental a ensinar para as crianças que não se deve gastar mais do que se tem. Ela pediu para você fazer um programa no qual as crianças digitam o valor do saldo e o valor de um item, e o programa imprime 'pode comprar' se o saldo for maior ou igual ao valor do item, e 'não pode comprar' caso contrário.*\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n100\\n80\\n```\\nO programa imprime:\\n```\\npode comprar\\n```",
    "ex3": "*EX3 — A professora do Fundamental ficou sabendo que você aprendeu a utilizar o operador `in` e logo pensou que você pode ajudar com um programa que, dada uma letra, verifica  se é uma das vogais. Ela disse que as crianças só sabem utilizar letras maíusculas e pediu para que seu programa responda 'vogal' ou 'não vogal'.*\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\nA\\n```\\nO programa imprime:\\n```\\nvogal\\n```",
    "ex4": "*EX4 — Nosso curso *Meninas Programadoras Multidisciplinar* tem número limitado de vagas. As candidatas são analisadas por ordem de prioridade: (1) alunas do Ensino Médio, (2) concluintes no ano anterior, (3) há dois anos, (4) há três anos, e assim por diante. Seu programa deve, dado o número de vagas total, ler o número de alunas selecionadas por atenderem os critérios de priorização, aceitando alunas até que o número de vagas se esgote. No final, o programa informa quantos critérios foram utilizados na seleção da turma.*\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n150\\n50\\n60\\n30\\n15\\n```\\nO programa imprime:\\n```\\n4\\n```",
    "ex5": "*EX5 — A professora do Fundamental está ensinando as crianças que existem números positivos, que existe o valor nulo, e que existem números negativos. Ela pediu sua ajuda para fazer um programa que recebe valores inteiros de entrada até que seja dado um valor negativo, e informa quantos valores positivos foram lidos.*\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n1\\n2\\n0\\n5\\n-1\\n```\\nO programa imprime:\\n```\\n3\\n```",
    "ex6": "*EX6 — Dado um nome alvo em uma linha inicial, seu programa ler nomes em novas linhas até que um nome igual ao alvo seja dado, e informar quantos nomes foram lidos antes do alvo.*\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\nAna\\nYasmin\\nMaria\\nAna\\n```\\nO programa imprime:\\n```\\n2\\n```",
    "ex7": "*EX7 — A professora está estudando a diferença salarial entre homens e mulheres em uma mesma função. Para isso, ela pediu sua ajuda para criar um programa que leia pares de salários, sendo sempre o salário do homem primeiro e o da mulher em seguida. A leitura termina quando o par -1 e -1 for informado. O programa deve contar quantos pares indicam igualdade salarial entre homem e mulher naquela posição, e imprimir esse total.*\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n1000.00\\n1000.00\\n1200.00\\n1100.00\\n-1\\n-1\\n```\\nO programa imprime:\\n```\\n1\\n```",
    "ex8": "*EX8 — A professora quer comparar salários de homens e mulheres que ocupam a mesma função. Ela pediu sua ajuda para criar um programa que leia pares de salários, sempre com o salário do homem primeiro e o da mulher em seguida. A leitura termina quando o par -1 e -1 for informado. O programa deve contar e informar:* \\n- *Quantos pares têm salários iguais,* \\n- *Quantos pares em que as mulheres recebem mais, e* \\n- *Quantos pares em que as mulheres recebem menos que os homens.*\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n1000.0\\n1000.0\\n1200.0\\n1100.0\\n900.0\\n950.0\\n-1\\n-1\\n```\\nO programa imprime:\\n```\\n1\\n1\\n1\\n```",
    "ex9": "*EX9 — A professora está ajudando seus alunos a entender como funcionam operações de entrada e saída em um caixa de banco. Ela pediu sua ajuda para criar um programa que leia valores numéricos representando essas operações:* \\n- *Valores positivos representam depósitos.* \\n- *Valores negativos representam saques.* \\n\\n*A leitura termina quando for digitado o valor 0.* \\n\\n*O programa deve calcular e imprimir o saldo final ao fim do dia.*\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n100\\n-20\\n-30\\n50\\n0\\n```\\nO programa imprime:\\n```\\n100\\n```",
    "ex10": "*EX10 — A professora está trabalhando com seus alunos a ideia de balanço calórico. Ela pediu sua ajuda para criar um programa que leia valores numéricos representando:* \\n- *Consumo de calorias (valores positivos, vindos de alimentos),* \\n- *Gasto de energia (valores negativos, de atividades físicas ou metabolismo).* \\n- *Término da entrada de dados para o programa indicado pelo valor 0 (zero).* \\n\\n*O programa deve calcular e imprimir:* \\n- *A quantidade total de calorias consumidas;* \\n- *A quantidade total de calorias gastas;* \\n- *O saldo calórico final do dia.*\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\n200\\n300\\n-150\\n-50\\n0\\n```\\nO programa imprime:\\n```\\n500\\n200\\n300\\n```",
    "ex11": "*EX11 — A professora propôs um jogo para as crianças: ela escolhe uma palavra-alvo e uma criança vai digitando outras palavras que contenham pelo menos parcialmente a palavra alvo escolhida pela professora, uma por linha.* \\n- *Cada vez que a palavra-alvo aparecer na linha digitada, a criança ganha um ponto!* \\n- *O jogo termina quando a criança digita apenas um ponto final (`.`) \\n\\n*Seu programa deve contar quantos pontos uma criança obteve em uma jogada.*\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\nsol\\nconsola\\ninsolente\\nluar\\nsolado\\nsoldada\\nmulher\\nresolução\\nprofessora\\nmenina\\n.\\n```\\nO programa imprime:\\n```\\n5\\n```",
    "ex12": "*EX12 — A professora propôs um exercício para discutir como podemos representar informações simples, como o gênero de uma pessoa, em programas de computador. Cada linha da entrada contém uma letra:* \\n- *F para feminino,* \\n- *M para masculino.* \\n\\n *A leitura termina quando for digitado apenas um ponto final (`.`)* \\n\\n*O programa deve contar quantas pessoas de cada gênero foram registradas e imprimir o total de M e F, nesta ordem.*\\n\\n*Exemplo*\\n\\nVocê digita:\\n```\\nM\\nF\\nF\\nM\\n.\\n```\\nO programa imprime:\\n```\\n2\\n2\\n```",
}

# =========================
# Helpers
# =========================
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

def run_user_code(code: str, input_text: str):
    lines = input_text.splitlines(True)
    it = iter(lines)
    def fake_input(prompt=""):
        try:
            return next(it).rstrip("\\n")
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
# Estado
# =========================
if "codes" not in st.session_state:
    st.session_state["codes"] = {f"ex{i}": "" for i in range(1, 13)}
if "results" not in st.session_state:
    st.session_state["results"] = {}
if "last_run" not in st.session_state:
    st.session_state["last_run"] = {}
if "_go_top" not in st.session_state:
    st.session_state["_go_top"] = False

# =========================
# Dashboard (mais baixo)
# =========================
st.subheader("📊 Seu progresso na Lista 3")

import pandas as _pd
_rows = []
for i in range(1, 13):
    k = f"ex{i}"
    res = st.session_state["results"].get(k)
    ok, tot = (res if res else (0, 0))
    perc = round(ok / tot * 100, 1) if tot else ""
    status_icon = "✅" if tot and ok == tot else ("🟡" if tot else "—")
    _rows.append({"Exercício": k.upper(), "Acertos": f"{ok}/{tot}" if tot else "", "%": perc, "Status": status_icon})
df = _pd.DataFrame(_rows, columns=["Exercício", "Acertos", "%", "Status"])
st.dataframe(df, hide_index=True, use_container_width=True, height=280)  # << menor

_done = [r for r in _rows if r["%"] != ""]
_avg = sum(r["%"] for r in _done)/len(_done) if _done else 0.0
st.progress(min(1.0, _avg/100))
st.caption(f"Média dos exercícios avaliados: {_avg:.1f}%")

# =========================
# UI principal (tabs)
# =========================
st.title("Lista 3 — Pré-correção automática (MP)")
st.markdown("Selecione o exercício, escreva seu código e rode os testes para a **pré-correção**.")

ex_list = [f"ex{i}" for i in range(1,13)]
ex = st.selectbox("Exercício", ex_list, format_func=lambda k: k.upper())

tab_enun, tab_code = st.tabs(["📖 Enunciado", "💻 Código & testes"])

with tab_enun:
    st.markdown(ENUNCIADOS[ex])

with tab_code:
    ACE_OK = False
    try:
        from streamlit_ace import st_ace
        ACE_OK = True
    except Exception:
        ACE_OK = False

    if ACE_OK:
        current_code = st.session_state["codes"].get(ex, "")
        code = st_ace(
            value=current_code or "",
            language="python",
            theme="chrome",
            keybinding="vscode",
            font_size=13,
            tab_size=4,
            wrap=True,
            show_gutter=True,
            show_print_margin=False,
            auto_update=True,
            placeholder="# Escreva seu código aqui (use input() e print())",
            height=240,  # um pouco menor
            key=f"ace_{ex}",
        )
        st.session_state["codes"][ex] = code or ""
    else:
        current_code = st.session_state["codes"].get(ex, "")
        code = st.text_area(
            "Seu código (use input() e print())",
            value=current_code,
            height=200,
            key=f"code_{ex}",
            placeholder="# Escreva seu código aqui (use input() e print())",
        )
        st.session_state["codes"][ex] = st.session_state[f"code_{ex}"]

    col1, col2 = st.columns([1,1])
    with col1:
        rodar = st.button("Rodar avaliação", type="primary")
    with col2:
        reset = st.button("Limpar saída")

    if reset:
        st.session_state["results"].pop(ex, None)
        st.session_state["last_run"].pop(ex, None)
        st.rerun()

    if rodar:
        with st.spinner("Carregando casos e executando testes..."):
            try:
                bundle = load_tests_from_github(ex)
                casos = bundle["cases"]
                ok = 0
                total = len(casos)
                code_to_run = st.session_state["codes"][ex]
                _lines = []
                for i, caso in enumerate(casos, start=1):
                    entrada = caso.get("entrada", "")
                    saida_hash = caso.get("saida_hash", "")
                    normalizacao = caso.get("normalizacao", bundle.get("normalizacao", "strip"))
                    status, out = run_user_code(code_to_run, entrada)
                    if status == "exc":
                        _lines.append(("err", f"Teste {i}: ERRO — {out}"))
                    else:
                        out_norm = _normalize(out, normalizacao)
                        h = _sha256(out_norm)
                        if h == saida_hash:
                            ok += 1
                            _lines.append(("ok", f"Teste {i}: OK"))
                        else:
                            _lines.append(("warn", f"Teste {i}: ERRO"))
                st.session_state["last_run"][ex] = {"lines": _lines, "summary": (ok, total)}
                st.session_state["results"][ex] = (ok, total)
                # peça para subir ao topo no próximo render
                st.session_state["_go_top"] = True
                st.rerun()
            except Exception as e:
                st.session_state["last_run"][ex] = {"lines": [("err", f"Falha ao carregar/rodar testes: {e}")], "summary": (0, 0)}
                st.session_state["_go_top"] = True
                st.rerun()

    # Mostrar a última execução (persistida)
    _lr = st.session_state["last_run"].get(ex)
    if _lr:
        for lvl, msg in _lr.get("lines", []):
            if lvl == "ok":
                st.success(msg)
            elif lvl == "warn":
                st.warning(msg)
            else:
                st.error(msg)
        ok_lr, tot_lr = _lr.get("summary", (0,0))
        st.info(f"*Resumo {ex.upper()}: {ok_lr}/{tot_lr} OK*")

st.caption("As entradas e saídas dos testes não são exibidas. Este app apenas avalia localmente via casos de teste públicos.")
