import streamlit as st
import io, sys, hashlib, builtins, requests, re, json, urllib.parse, hmac

# =========================
# Configurações do app
# =========================
st.set_page_config(page_title="Lista 3 — Meninas Programadoras", layout="centered")

# -------------------------
# Segredos (defina no secrets.toml ou nas Secrets do Streamlit Cloud)
# -------------------------
# Exemplos de secrets:
# GITHUB_RAW_BASE="https://raw.githubusercontent.com/mgpimentel/xyzist3st3s/main/t"
# SECRET_KEY="troque-por-uma-chave-secreta-bem-grande"
# FORM_URL="https://docs.google.com/forms/d/e/SEU_FORM_ID/viewform"
# [ENTRY_ID]
# ident="entry.1111111111"
# lista="entry.2222222222"
# ex="entry.3333333333"
# ok="entry.4444444444"
# tot="entry.5555555555"
# code="entry.6666666666"
# sig="entry.7777777777"
#
# (Opcional) Para acessar repositório privado via raw.githubusercontent, forneça:
# GITHUB_TOKEN="ghp_..."  (token com escopo apenas de leitura)

GITHUB_RAW_BASE = st.secrets.get("GITHUB_RAW_BASE", "https://raw.githubusercontent.com/mgpimentel/xyzist3st3s/main/t")
SECRET_KEY = st.secrets.get("SECRET_KEY", "troque-por-uma-chave-secreta")
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
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", None)

LISTA_ID = "Lista 3"

# =========================
# Enunciados
# =========================
ENUNCIADOS = {
    "ex1": "*EX1 — Dados o número de execicios que uma aluna resolveu nas duas primeiras listas, calcule quantos exercícios ela resolveu no total.*\n\n*Exemplo*\n\nVocê digita:\n```\n7\n8\n```\nO programa imprime:\n```\n15\n```",
    "ex2": "*EX2 — Você está ajudando a professora do Fundamental a ensinar para as crianças que não se deve gastar mais do que se tem. Ela pediu para você fazer um programa no qual as crianças digitam o valor do saldo e o valor de um item, e o programa imprime 'pode comprar' se o saldo for maior ou igual ao valor do item, e 'não pode comprar' caso contrário.*\n\n*Exemplo*\n\nVocê digita:\n```\n100\n80\n```\nO programa imprime:\n```\npode comprar\n```",
    "ex3": "*EX3 — A professora do Fundamental ficou sabendo que você aprendeu a utilizar o operador `in` e logo pensou que você pode ajudar com um programa que, dada uma letra, verifica  se é uma das vogais. Ela disse que as crianças só sabem utilizar letras maíusculas e pediu para que seu programa responda 'vogal' ou 'não vogal'.*\n\n*Exemplo*\n\nVocê digita:\n```\nA\n```\nO programa imprime:\n```\nvogal\n```",
    "ex4": "*EX4 — Nosso curso *Meninas Programadoras Multidisciplinar* tem número limitado de vagas. As candidatas são analisadas por ordem de prioridade: (1) alunas do Ensino Médio, (2) concluintes no ano anterior, (3) há dois anos, (4) há três anos, e assim por diante. Seu programa deve, dado o número de vagas total, ler o número de alunas selecionadas por atenderem os critérios de priorização, aceitando alunas até que o número de vagas se esgote. No final, o programa informa quantos critérios foram utilizados na seleção da turma.*\n\n*Exemplo*\n\nVocê digita:\n```\n150\n50\n60\n30\n15\n```\nO programa imprime:\n```\n4\n```",
    "ex5": "*EX5 — A professora do Fundamental está ensinando as crianças que existem números positivos, que existe o valor nulo, e que existem números negativos. Ela pediu sua ajuda para fazer um programa que recebe valores inteiros de entrada até que seja dado um valor negativo, e informa quantos valores positivos foram lidos.*\n\n*Exemplo*\n\nVocê digita:\n```\n1\n2\n0\n5\n-1\n```\nO programa imprime:\n```\n4\n```",
    "ex6": "*EX6 — Dado um nome alvo em uma linha inicial, seu programa ler nomes em novas linhas até que um nome igual ao alvo seja dado, e informar quantos nomes foram lidos antes do alvo.*\n\n*Exemplo*\n\nVocê digita:\n```\nAna\nYasmin\nMaria\nAna\n```\nO programa imprime:\n```\n2\n```",
    "ex7": "*EX7 — A professora está estudando a diferença salarial entre homens e mulheres em uma mesma função. Para isso, ela pediu sua ajuda para criar um programa que leia pares de salários, sendo sempre o salário do homem primeiro e o da mulher em seguida. A leitura termina quando o par -1 e -1 for informado. O programa deve contar quantos pares indicam igualdade salarial entre homem e mulher naquela posição, e imprimir esse total.*\n\n*Exemplo*\n\nVocê digita:\n```\n1000.00\n1000.00\n1200.00\n1100.00\n-1\n-1\n```\nO programa imprime:\n```\n1\n```",
    "ex8": "*EX8 — A professora quer comparar salários de homens e mulheres que ocupam a mesma função. Ela pediu sua ajuda para criar um programa que leia pares de salários, sempre com o salário do homem primeiro e o da mulher em seguida. A leitura termina quando o par -1 e -1 for informado. O programa deve contar e informar: - Quantos pares têm salários iguais, - Quantos pares em que as mulheres recebem mais, e - Quantos pares em que as mulheres recebem menos que os homens.*\n\n*Exemplo*\n\nVocê digita:\n```\n1000.0\n1000.0\n1200.0\n1100.0\n900.0\n950.0\n-1\n-1\n```\nO programa imprime:\n```\n1\n1\n1\n```",
    "ex9": "*EX9 — A professora está ajudando seus alunos a entender como funcionam operações de entrada e saída em um caixa de banco. Ela pediu sua ajuda para criar um programa que leia valores numéricos representando essas operações: - Valores positivos representam depósitos. - Valores negativos representam saques. - A leitura termina quando for digitado o valor 0. O programa deve calcular e imprimir o saldo final ao fim do dia.*\n\n*Exemplo*\n\nVocê digita:\n```\n100\n-20\n-30\n50\n0\n```\nO programa imprime:\n```\n100\n```",
    "ex10": "*EX10 — A professora está trabalhando com seus alunos a ideia de balanço calórico. Ela pediu sua ajuda para criar um programa que leia valores numéricos representando: - Consumo de calorias (valores positivos, vindos de alimentos), - Gasto de energia (valores negativos, de atividades físicas ou metabolismo). - Término da entrada de dados para o programa indicado pelo valoe 0 (zero). O programa deve calcular e imprimir: - A quantidade total de calorias consumidas; - A quantidade total de calorias gastas; - O saldo calórico final do dia.*\n\n*Exemplo*\n\nVocê digita:\n```\n200\n300\n-150\n-50\n0\n```\nO programa imprime:\n```\n500\n200\n300\n```",
    "ex11": "*EX11 — A professora propôs um jogo para as crianças: ela escolhe uma palavra-alvo e uma criança vai digitando outras palavras, uma por linha. - Cada vez que a palavra-alvo aparecer na linha digitada, a criança ganha um ponto! - O jogo termina quando a criança digita apenas um ponto final (`.`) Seu programa deve contar quantos pontos uma criança obteve em uma jogada.*\n\n*Exemplo*\n\nVocê digita:\n```\nsol\nconsola\ninsolente\nluar\nsolado\nsoldada\nmulher\nresolução\nprofessora\nmenina\n.\n```\nO programa imprime:\n```\n5\n```",
    "ex12": "*EX12 — A professora propôs um exercício para discutir como podemos representar informações simples, como o gênero de uma pessoa, em programas de computador. Cada linha da entrada contém uma letra: - F para feminino, - M para masculino. A leitura termina quando for digitado apenas um ponto final (`.`) O programa deve contar quantas pessoas de cada gênero foram registradas e imprimir o total de M e F, nesta ordem.*\n\n*Exemplo*\n\nVocê digita:\n```\nM\nF\nF\nM\n.\n```\nO programa imprime:\n```\n2\n2\n```",
}

TEMPLATES = { ex: f"#EXERCICIO: {ex}\n# escreva seu código aqui" for ex in ENUNCIADOS.keys() }

# =========================
# Funções de apoio
# =========================
def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _normalize(s: str, mode: str = "strip") -> str:
    # Normaliza quebras de linha e espaços finais/iniciais conforme solicitado no bundle
    s = s.replace("\\r\\n", "\\n").replace("\\r", "\\n")
    if mode == "strip":
        return s.strip()
    if mode == "rstrip":
        return s.rstrip()
    if mode == "lstrip":
        return s.lstrip()
    return s  # padrão: sem alteração adicional

def run_user_code(code: str, input_text: str):
    # Isola input/print do usuário
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

# =========================
# Carregar testes
# =========================
@st.cache_data(show_spinner=False, ttl=600)
def load_tests_from_github(tag: str):
    m = re.search(r'(\d+)', str(tag))
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
            # Suporta formatos: {"cases":[...], "hash_alg":"sha256", "normalizacao":"strip"} ou lista simples
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
    payload = f"{ident}|{lista}|{ex}|{ok}|{tot}|{_sha256(code.strip())}"
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
    return f"{FORM_URL}?usp=pp_url&{urllib.parse.urlencode(params)}"

# =========================
# UI
# =========================
st.title("Lista 3 — Correção Automática (MP)")
st.markdown("Selecione o exercício, escreva seu código, rode os testes e *envie sua resposta* pelo formulário.")

ex_list = [f"ex{i}" for i in range(1,13)]
ex = st.selectbox("Exercício", ex_list, format_func=lambda k: k.upper())

st.markdown(ENUNCIADOS[ex])

code = st.text_area("Seu código (use input() e print())", value=TEMPLATES[ex], height=260)

col1, col2 = st.columns([1,1])
with col1:
    rodar = st.button("Rodar avaliação", type="primary")
with col2:
    reset = st.button("Limpar saída")

if reset:
    st.session_state.pop("_result", None)

if rodar:
    with st.spinner("Carregando casos e executando testes..."):
        try:
            bundle = load_tests_from_github(ex)
            casos = bundle["cases"]
            ok = 0
            total = len(casos)
            for i, caso in enumerate(casos, start=1):
                entrada = caso.get("entrada", "")
                saida_hash = caso.get("saida_hash", "")
                normalizacao = caso.get("normalizacao", bundle.get("normalizacao", "strip"))
                status, out = run_user_code(code, entrada)
                if status == "exc":
                    st.error(f"Teste {i}: ERRO — {out}")
                else:
                    out_norm = _normalize(out, normalizacao)
                    h = _sha256(out_norm)
                    if h == saida_hash:
                        ok += 1
                        st.success(f"Teste {i}: OK")
                    else:
                        st.warning(f"Teste {i}: ERRO")
            st.info(f"*Resumo {ex.upper()}: {ok}/{total} OK*")
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

st.caption("As entradas e saídas dos testes não são exibidas. O formulário registra seu código, placar e uma assinatura para verificação.")
