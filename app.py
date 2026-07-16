import streamlit as str
import PyPDF2
import os
from docx import Document
from google import genai #importando a biblioteca do Gemini para usar a API de IA

# PRIMEIRA LINHA DO STREAMLIT NO CÓDIGO:
str.set_page_config(
    page_title="CvMatch", # O texto que vai aparecer na aba
    page_icon="🎯",                          
    layout="centered"                        
)

# Função para ler o PDF do Currículo
def ler_pdf(arquivo):
    leitor = PyPDF2.PdfReader(arquivo)
    texto_completo = ""
    for pagina in leitor.pages:
        texto_completo += pagina.extract_text() + "\n"
    return texto_completo

# Função para ler o Word da Entrevista
def ler_word(arquivo):
    doc = Document(arquivo)
    texto_completo = ""
    for paragrafo in doc.paragraphs:
        texto_completo += paragrafo.text + "\n"
    return texto_completo

# Lê os arquivos do ranking em word ou pdf
def extrair_texto_geral(arquivo):
    """Lê automaticamente arquivos PDF ou Word"""
    if arquivo.name.endswith(".pdf"):
        return ler_pdf(arquivo)
    elif arquivo.name.endswith(".docx"):
        return ler_word(arquivo)
    return ""

#---configuração da API de IA
cliente_ia = genai.Client()

# --- MENU LATERAL DE NAVEGAÇÃO ---
str.sidebar.title("CvMatch 🎯")
opcao_tela = str.sidebar.radio(
    "Escolha a funcionalidade:",
    ["👤 Análise Individual", "🏆 Ranking"]
)

# ==============================================================================
# TELA 1: ANÁLISE INDIVIDUAL
# ==============================================================================
if opcao_tela == "👤 Análise Individual":
    str.title("CvMatch🎯 - Analisando Candidatos com IA 🤖")
    str.subheader("Descubra a aderência do candidato à vaga em tempo real!")

    str.divider()

    vaga_texto = str.text_area("1. Cole aqui a descrição da vaga:", height=150)

    curriculo_file = str.file_uploader("2. Envie o currículo do candidato (Modelo PDF)", type=["pdf"])
    entrevista_file = str.file_uploader("3. Envie a transcrição da entrevista ou suas anotações sobre o perfil (Modelo Word)", type=["docx"])
    anotacoes_texto = str.text_area("4. Ou cole aqui as suas anotações da entrevista / perfil:", height=150)

    str.divider()

    if str.button("Calcular Aderência 🚀"):
        if vaga_texto and curriculo_file:
            with str.spinner("A Inteligência Artificial está analisando os dados... 🧠⏳"):

                
                texto_curriculo = ler_pdf(curriculo_file)

                conteudos_entrevista = []

                # 1. Se subiu arquivo Word
                if entrevista_file is not None:
                    conteudos_entrevista.append(ler_word(entrevista_file))
                
                # 2. Se digitou/colou texto na caixa
                if anotacoes_texto.strip():
                    conteudos_entrevista.append(anotacoes_texto.strip())
                
                # 3. Junta tudo ou define texto padrão
                if conteudos_entrevista:
                    texto_entrevista = "\n\n".join(conteudos_entrevista)
                else:
                    texto_entrevista = "Nenhuma entrevista ou anotação foi fornecida."
                
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
                
                resposta = cliente_ia.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=comando_para_ia
                )
                
                str.success("Análise concluída com sucesso!")
                str.markdown(resposta.text)
                
        else:
            str.warning("Por favor, preencha a descrição da vaga e envie o currículo antes de calcular!")

# ==============================================================================
# TELA 2: RANKING DE CANDIDATOS
# ==============================================================================
elif opcao_tela == "🏆 Ranking":
    str.title("CvMatch 🏆 - Ranking de Candidatos")
    str.subheader("Descubra quais candidatos são os mais aderentes à vaga!")

    str.divider()

    # 1. Campo para a vaga
    vaga_texto_comp = str.text_area("1. Cole aqui a descrição da vaga:", height=150, key="vaga_comp")

    # 2. Campo para múltiplos currículos (PDF e Word)
    lista_curriculos = str.file_uploader(
        "2. Selecione os currículos dos candidatos (De 2 a 5 arquivos PDF ou Word):",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    str.divider()

    # Botão para disparar a análise (INDENTADO DENTRO DO ELIF)
    if str.button("Gerar Ranking 🚀"):
        # Validação: faltou a vaga?
        if not vaga_texto_comp:
            str.warning("Por favor, envie a descrição da vaga para continuar.")
        # Validação: faltou enviar cv ou menos de 2
        elif not lista_curriculos or len(lista_curriculos) < 2:
            str.warning("Por favor, envie pelo menos dois currículos para gerar o ranking.")
        # Validação: Passar do limite de 5 cvs
        elif len(lista_curriculos) > 5:
            str.error(f"Você enviou {len(lista_curriculos)} currículos. Por favor, envie no máximo 5 currículos para gerar o ranking.")
        # Todas as validações estão ok
        else:
            total_cvs = len(lista_curriculos)
            dados_candidatos_prompts = ""
            
            # exibe carregamento enquanto le arquivos
            with str.spinner("Lendo os arquivos dos currículos..."):
                for indice, arquivo in enumerate(lista_curriculos):
                    texto_cv = extrair_texto_geral(arquivo)

                    # Organiza cada candidato para a IA identificar depois
                    dados_candidatos_prompts += f"""
                    --- CANDIDATO {indice + 1} ---
                    Nome do Arquivo: {arquivo.name}
                    Conteúdo do Currículo:
                    {texto_cv}
                    \n
                    """
            
            # Mostra na tela para testar (DENTRO DO ELSE DO BOTÃO)
            str.success(f"Sucesso! Conseguimos ler os {total_cvs} currículos!")
            str.text_area("Texto compilado dos currículos (Apenas para testes):", value=dados_candidatos_prompts, height=200)

            # 1. Criamos a instrução especial para o Gemini comparar o lote
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

            # 2. Chamamos o Gemini dentro de uma mensagem de espera na tela
            with str.spinner("A Inteligência Artificial está comparando os perfis e gerando o ranking... 🧠🏆"):
                resposta = cliente_ia.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=comando_ranking
                )

            # 3. Mostramos o resultado final na tela!
            str.success("Ranking gerado com sucesso!")
            str.markdown(resposta.text)
