import streamlit as st
import PyPDF2
import os
from docx import Document

# PRIMEIRA LINHA DO STREAMLIT NO CÓDIGO:
st.set_page_config(
    page_title="CvMatch",
    page_icon="🎯",
    layout="centered"
)

# ==============================================================================
# 🔐 SISTEMA DE AUTENTICAÇÃO E LOGIN (Via Secrets)
# ==============================================================================
USUARIOS_AUTORIZADOS = st.secrets.get("logins", {})

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = False
if "nome_usuario" not in st.session_state:
    st.session_state["nome_usuario"] = ""

def efetuar_login(usuario, senha):
    if usuario in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usuario] == senha:
        st.session_state["usuario_logado"] = True
        st.session_state["nome_usuario"] = usuario
        st.success(f"Bem-vindo(a), {usuario}!")
        st.rerun()
    else:
        st.error("Usuário ou senha incorretos. Tente novamente!")

def efetuar_logout():
    st.session_state["usuario_logado"] = False
    st.session_state["nome_usuario"] = ""
    st.rerun()

# --- VERIFICAÇÃO DE LOGIN ---
if not st.session_state["usuario_logado"]:
    st.markdown("<h2 style='text-align: center;'>🔐 Login - CvMatch</h2>", unsafe_allow_html=True)
    with st.form("form_login"):
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        botao_entrar = st.form_submit_button("Entrar")

        if botao_entrar:
            efetuar_login(usuario_input, senha_input)

    st.stop()

# ==============================================================================
# 🚀 SISTEMA PRINCIPAL (Apenas para usuários logados)
# ==============================================================================

# --- Funções de leitura de arquivo ---
def ler_pdf(arquivo):
    leitor = PyPDF2.PdfReader(arquivo)
    texto_completo = ""
    for pagina in leitor.pages:
        texto = pagina.extract_text()
        if texto:
            texto_completo += texto + "\n"
    return texto_completo

def ler_word(arquivo):
    doc = Document(arquivo)
    texto_completo = ""
    for paragrafo in doc.paragraphs:
        texto_completo += paragrafo.text + "\n"
    return texto_completo

def extrair_texto_geral(arquivo):
    if arquivo.name.endswith(".pdf"):
        return ler_pdf(arquivo)
    elif arquivo.name.endswith(".docx"):
        return ler_word(arquivo)
    return ""

# --- Inicialização da IA ---
def obter_cliente_ia():
    try:
        from google import genai
        api_key = (
            st.secrets.get("api_key") 
            or st.secrets.get("GEMINI_API_KEY") 
            or os.environ.get("GEMINI_API_KEY")
        )
        if not api_key:
            st.error("⚠️ Chave da API do Gemini não encontrada nos Secrets.")
            return None
        return genai.Client(api_key=api_key)
    except ImportError:
        st.error("❌ Biblioteca 'google-genai' não instalada. Execute `python -m pip install google-genai` no terminal.")
        return None
    except Exception as e: # type: ignore
        st.error(f"Erro ao conectar ao Gemini: {e}")
        return None

cliente_ia = obter_cliente_ia()

# --- Menu lateral ---
st.sidebar.title("CvMatch 🎯")
st.sidebar.write(f"👤 Logado como: **{st.session_state['nome_usuario']}**")
if st.sidebar.button("Sair / Logout"):
    efetuar_logout()
st.sidebar.divider()

opcao_tela = st.sidebar.radio(
    "Escolha a funcionalidade:",
    ["👤 Análise Individual", "🏆 Ranking"]
)

# ==============================================================================
# TELA 1: ANÁLISE INDIVIDUAL
# ==============================================================================
if opcao_tela == "👤 Análise Individual":
    st.title("CvMatch🎯 - Analisando Candidatos com IA 🤖")
    st.subheader("Descubra a aderência do candidato à vaga em tempo real!")
    st.divider()

    vaga_texto = st.text_area("1. Cole aqui a descrição da vaga:", height=150)
    curriculo_file = st.file_uploader("2. Envie o currículo do candidato (PDF)", type=["pdf"])
    entrevista_file = st.file_uploader("3. Envie a transcrição da entrevista ou anotações (Word)", type=["docx"])
    anotacoes_texto = st.text_area("4. Ou cole aqui as suas anotações da entrevista / perfil:", height=150)
    st.divider()

    if st.button("Calcular Aderência 🚀"):
        if not cliente_ia:
            st.error("Serviço de IA indisponível. Verifique as configurações da API Key.")
        elif not vaga_texto or not curriculo_file:
            st.warning("Por favor, preencha a descrição da vaga e envie o currículo antes de calcular!")
        else:
            with st.spinner("A Inteligência Artificial está analisando os dados... 🧠⏳"):
                texto_curriculo = ler_pdf(curriculo_file)
                conteudos_entrevista = []

                if entrevista_file is not None:
                    conteudos_entrevista.append(ler_word(entrevista_file))
                if anotacoes_texto.strip():
                    conteudos_entrevista.append(anotacoes_texto.strip())

                texto_entrevista = "\n\n".join(conteudos_entrevista) if conteudos_entrevista else "Nenhuma entrevista ou anotação foi fornecida."

                comando_para_ia = f"""
                Você é um especialista em Recursos Humanos e Recrutamento Técnico.
                Analise a aderência deste candidato para a vaga abaixo.

                [DESCRIÇÃO DA VAGA]
                {vaga_texto}

                [CURRÍCULO DO CANDIDATO]
                {texto_curriculo}

                [TRANSCRIÇÃO DA ENTREVISTA]
                {texto_entrevista}

                Com base nessas informações, retorne o resultado exatamente neste formato:
                ### 📊 Porcentagem de Aderência: [Insira a porcentagem aqui de 0% a 100%]

                ### 🎯 Pontos Fortes do Candidato
                - [Ponto forte 1]
                - [Ponto forte 2]

                ### ⚠️ Pontos de Atenção / Gaps
                - [Ponto de atenção 1]
                - [Ponto de atenção 2]

                ### 💬 Resumo Final
                [Escreva uma breve justificativa da nota em até 3 linhas]
                """

                try:
                    resposta = cliente_ia.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=comando_para_ia
                    )
                    st.success("Análise concluída com sucesso!")
                    st.markdown(resposta.text)
                except Exception as err: # type: ignore
                    st.error(f"Erro ao gerar resposta da IA: {err}")

# ==============================================================================
# TELA 2: RANKING DE CANDIDATOS
# ==============================================================================
elif opcao_tela == "🏆 Ranking":
    st.title("CvMatch 🏆 - Ranking de Candidatos")
    st.subheader("Descubra quais candidatos são os mais aderentes à vaga!")
    st.divider()

    vaga_texto_comp = st.text_area("1. Cole aqui a descrição da vaga:", height=150, key="vaga_comp")
    lista_curriculos = st.file_uploader(
        "2. Selecione os currículos dos candidatos (De 2 a 5 arquivos PDF ou Word):",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )
    st.divider()

    if st.button("Gerar Ranking 🚀"):
        # Converter para lista explícita resolve o alerta de len() do Pylance
        arquivos = list(lista_curriculos) if lista_curriculos else []
        qtd_arquivos = len(arquivos)

        if not cliente_ia:
            st.error("Serviço de IA indisponível. Verifique as configurações da API Key.")
        elif not vaga_texto_comp:
            st.warning("Por favor, envie a descrição da vaga para continuar.")
        elif qtd_arquivos < 2:
            st.warning("Por favor, envie pelo menos dois currículos para gerar o ranking.")
        elif qtd_arquivos > 5:
            st.error(f"Você enviou {qtd_arquivos} currículos. Por favor, envie no máximo 5.")
        else:
            dados_candidatos_prompts = ""
            with st.spinner("Lendo os arquivos dos currículos..."):
                for indice, arquivo in enumerate(arquivos):
                    texto_cv = extrair_texto_geral(arquivo)
                    dados_candidatos_prompts += f"""
                    --- CANDIDATO {indice + 1} ---
                    Nome do Arquivo: {arquivo.name}
                    Conteúdo do Currículo:
                    {texto_cv}
                    """

            st.success(f"Sucesso! Conseguimos ler os {qtd_arquivos} currículos!")

            comando_ranking = f"""
            Você é um especialista em Recrutamento Técnico e Seleção de Talentos.
            Análise a descrição da vaga e compare todos os candidatos abaixo.
            Sua missão é gerar um RANKING ordenado da maior aderência para a menor aderência.

            [DESCRIÇÃO DA VAGA]
            {vaga_texto_comp}

            [LISTA DE CANDIDATOS]
            {dados_candidatos_prompts}

            Siga estritamente esta estrutura para o relatório final:

            # 🏆 Ranking Geral de Aderência

            Para cada candidato enviado (ordenado do 1º ao último colocado), exiba:

            ### 🥇 [Posição no Ranking]º Lugar: [Nome do Arquivo do Candidato]
            * **Porcentagem de Aderência:** [0% a 100%]
            * **Top 2 Pontos Fortes:** [Ponto 1] | [Ponto 2]
            * **Principal Gap:** [Maior ponto de atenção em 1 linha]

            ---

            # ⭐ Veredito
            [Escreva um parágrafo objetivo explicando qual candidato deve ser chamado primeiro para entrevista e a justificativa principal.]
            """

            with st.spinner("A Inteligência Artificial está comparando os perfis... 🧠🏆"):
                try:
                    resposta = cliente_ia.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=comando_ranking
                    )
                    st.success("Ranking gerado com sucesso!")
                    st.markdown(resposta.text)
                except Exception as err: # type: ignore
                    st.error(f"Erro ao gerar ranking: {err}")
