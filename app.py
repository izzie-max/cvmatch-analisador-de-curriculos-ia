import streamlit as str
import PyPDF2
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
    # Esse comando passa de página em página pegando o texto
    for pagina in leitor.pages:
        texto_completo += pagina.extract_text() + "\n"
    return texto_completo

# Função para ler o Word da Entrevista
def ler_word(arquivo):
    doc = Document(arquivo)
    texto_completo = ""
    # Esse comando lê parágrafo por parágrafo do arquivo Word
    for paragrafo in doc.paragraphs:
        texto_completo += paragrafo.text + "\n"
    return texto_completo

#---configuração da API de IA
CHAVE_API ="AIzaSyCyFkfYIK_9cra_NoDPKcnAHXie84ZwFVA"

# Inicializa o cliente do Gemini
cliente_ia = genai.Client(api_key=CHAVE_API)


# --- PARTE VISUAL (INTERFACE) ---

str.title("CvMatch🎯 - Analisando Candidatos com IA 🤖")
str.subheader("Descubra a aderência do candidato à vaga em tempo real!")

str.divider()

vaga_texto = str.text_area("1. Cole aqui a descrição da vaga:", height=150)

curriculo_file = str.file_uploader("2. Envie o currículo do candidato (Modelo PDF)", type=["pdf"])
entrevista_file = str.file_uploader("3. Envie a transcrição da entrevista (Modelo Word)", type=["docx"])

str.divider()

if str.button("Calcular Aderência 🚀"):
    # Só vamos rodar se o usuário tiver preenchido tudo!
    if vaga_texto and curriculo_file:
        
       with str.spinner("A Inteligência Artificial está analisando os dados... 🧠⏳"):
            
            # 1. Lendo os arquivos
            texto_curriculo = ler_pdf(curriculo_file)
            
            texto_entrevista = "Nenhuma entrevista foi fornecida."
            if entrevista_file is not None:
                texto_entrevista = ler_word(entrevista_file)
            
            # 2. Criando o comando (Prompt) para a IA do Google
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
            
            # 3. Enviando o comando para o modelo do Gemini (usando o flash, que é super rápido)
            resposta = cliente_ia.models.generate_content(
                model='gemini-2.5-flash',
                contents=comando_para_ia
            )
            
            # 4. Exibindo o resultado final na tela de forma bonita
            str.success("Análise concluída com sucesso!")
            str.markdown(resposta.text)
            
    else:
        str.warning("Por favor, preencha a descrição da vaga e envie o currículo antes de calcular!") 
