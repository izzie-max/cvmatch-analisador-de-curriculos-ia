# 🎯 CvMatch — Analisador de Currículos com Inteligência Artificial

O **CvMatch** é uma solução inteligente desenvolvida para otimizar e acelerar os processos de Recrutamento & Seleção (R&S). Utilizando a API do **Google Gemini 2.5 Flash**, a plataforma realiza a leitura de currículos, notas de entrevistas e descrições de vagas para entregar análises automatizadas de aderência e rankings comparativos de candidatos.

---

## 🚀 Funcionalidades Principais

* 🔐 **Acesso Restrito & Seguro:** Autenticação de usuários por perfis diretamente na plataforma.
* 📊 **Análise Individual de Aderência:** Leitura e cruzamento de currículos (PDF) e relatórios de entrevista (DOCX) contra os requisitos da vaga, gerando:
  * Porcentagem exata de aderência à vaga.
  * Pontos fortes do candidato.
  * Pontos de atenção / *gaps* técnicos e comportamentais.
  * Resumo executivo para tomada de decisão.
* 🏆 **Ranking de Candidatos:** Comparativo direto entre múltiplos currículos enviados simultaneamente para selecionar os perfis mais qualificados.
* 📄 **Processamento Multimodal:** Suporte para extração de dados de arquivos em PDF, Word e leitura via IA.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.12+
* **Interface Web:** [Streamlit](https://streamlit.io/)
* **Inteligência Artificial:** [Google Gemini 2.5 Flash](https://ai.google.dev/) (via SDK oficial `google-genai`)
* **Processamento de Documentos:** `pypdf` / `PyPDF2` (PDFs) e `python-docx` (Word)
* **Hospedagem & Deploy:** Streamlit Community Cloud

---

## ⚙️ Como Executar o Projeto Localmente

### Pré-requisitos
* Python 3.10 ou superior instalado.
* Uma chave de API da Google Gemini ([Google AI Studio](https://aistudio.google.com/)).

### 1. Clonar o repositório
```bash
git clone [https://github.com/SEU-USUARIO/cvmatch-analisador-de-curriculos-ia.git](https://github.com/SEU-USUARIO/cvmatch-analisador-de-curriculos-ia.git)
cd cvmatch-analisador-de-curriculos-ia
