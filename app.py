import streamlit as st
import os
import re
from pathlib import Path
import shutil
import PyPDF2


class AutomatizadorRequerimentosWeb:
    def __init__(self):
        self.setup_page()

    def setup_page(self):
        """Configura a página do Streamlit"""
        st.set_page_config(
            page_title="Automatizador Jurídico - ONLINE", page_icon="⚖️", layout="wide"
        )

        st.title("🌐 Automatizador de Requerimentos - VERSÃO ONLINE")
        st.success("✅ Esta versão está HOSPEDADA NA NUVEM e disponível 24/7!")
        st.markdown(
            """
        **Automatize o processamento de documentos jurídicos**  
        Sistema sempre disponível para organizar requerimentos de forma eficiente.
        """
        )

    def get_folder_paths(self):
        """Interface para usuário definir os diretórios sem sidebar"""

        # Expander principal
        with st.expander("📁 CONFIGURAR DIRETÓRIOS", expanded=True):

            # Pasta dos PDFs (WhatsApp)
            st.subheader("📥 Pasta dos PDFs (WhatsApp)")

            col1, col2 = st.columns([3, 1])

            with col1:
                current_value = st.session_state.get("pasta_downloads", "")
                pasta_downloads = st.text_input(
                    "Caminho da pasta dos PDFs:",
                    value=current_value,
                    key="pasta_downloads_input_main",
                    placeholder="Ex: C:/Users/SeuNome/Downloads/PDFs",
                )

            with col2:
                if st.button("📁 Procurar", key="btn_browse_downloads"):
                    st.info("💡 Digite o caminho manualmente ou use pastas padrão")

            st.divider()

            # Pasta dos Clientes (Drive)
            st.subheader("📂 Pasta dos Clientes (Drive)")
            col1, col2 = st.columns([3, 1])

            with col1:
                pasta_clientes = st.text_input(
                    "Caminho da pasta dos clientes:",
                    value=st.session_state.get("pasta_clientes", ""),
                    help="Pasta onde serão criadas as pastas dos clientes",
                    key="pasta_clientes_input_main",
                    placeholder="Ex: C:/Users/SeuNome/Documentos/Clientes",
                )

            with col2:
                if st.button("📁 Procurar", key="btn_browse_clientes"):
                    st.info("💡 Digite o caminho manualmente ou use pastas padrão")

            st.divider()

            # Pasta de Processamento
            st.subheader("⚙️ Pasta de Processamento")
            col1, col2 = st.columns([3, 1])

            with col1:
                pasta_processados = st.text_input(
                    "Caminho da pasta temporária:",
                    value=st.session_state.get("pasta_processados", ""),
                    help="Pasta para arquivos temporários durante processamento",
                    key="pasta_processados_input_main",
                    placeholder="Ex: C:/Users/SeuNome/AppData/Temp/Processamento",
                )

            with col2:
                if st.button("📁 Procurar", key="btn_browse_processados"):
                    st.info("💡 Digite o caminho manualmente ou use pastas padrão")

            # Botões de ação rápida
            st.divider()
            st.write("**⚡ Ações Rápidas:**")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🗑️ Limpar Tudo", key="btn_clear_main"):
                    st.session_state["pasta_downloads"] = ""
                    st.session_state["pasta_clientes"] = ""
                    st.session_state["pasta_processados"] = ""
                    st.rerun()

            with col2:
                if st.button("💡 Ajuda", key="btn_help_main"):
                    st.info(
                        """
                    **Como usar:**
                    1. Copie e cole os caminhos manualmente
                    2. Faça upload dos PDFs na seção abaixo
                    """
                    )

        # Atualizar session state com os valores atuais
        if pasta_downloads:
            st.session_state["pasta_downloads"] = pasta_downloads
        if pasta_clientes:
            st.session_state["pasta_clientes"] = pasta_clientes
        if pasta_processados:
            st.session_state["pasta_processados"] = pasta_processados

        return pasta_downloads, pasta_clientes, pasta_processados

    def extract_text_from_page(self, pdf_reader, page_num):
        """Extrai texto de uma página específica"""
        try:
            page = pdf_reader.pages[page_num]
            return page.extract_text()
        except:
            return ""

    def identify_document_type(self, text):
        """Identifica o tipo de documento baseado no conteúdo textual"""
        text = text.upper()

        # Padrões para identificar cada tipo de documento
        patterns = {
            "RG_CPF": [
                r"CARTEIRA DE IDENTIDADE",
                r"REGISTRO GERAL",
                r"SECRETARIA DE SEGURANÇA PÚBLICA",
                r"INSTITUTO DE IDENTIFICAÇÃO",
                r"CPF.*\d{3}\.\d{3}\.\d{3}-\d{2}",
                r"IDENTIDADE",
            ],
            "CERTIDAO_NASCIMENTO": [
                r"CERTIDÃO DE NASCIMENTO",
                r"REGISTRO CIVIL DAS PESSOAS NATURAIS",
                r"NASCI.*EM",
                r"FILIAÇÃO",
                r"AVOS",
            ],
            "COMPROVANTE_RESIDENCIA": [
                r"CONTA DE.*LUZ",
                r"CONTA DE.*ÁGUA",
                r"CONTA DE.*ENERGIA",
                r"COMPROVANTE DE RESIDÊNCIA",
                r"ENDEREÇO",
                r"CEP.*\d{5}-\d{3}",
            ],
            "TERMO_REPRESENTACAO": [
                r"TERMO DE REPRESENTAÇÃO",
                r"AUTORIZAÇÃO DE ACESSO A INFORMAÇÕES PREVIDENCIÁRIAS",
                r"INFORMAÇÕES PREVIDENCIÁRIAS",
                r"INSS",
                r"PREVIDENCIÁRIO",
            ],
            "PROCURACAO": [r"PROCURAÇÃO", r"OUTORGANTE", r"OUTORGADO", r"PODERES"],
            "CONTRATO_ADVOCATICIOS": [
                r"CONTRATO DE PRESTAÇÃO DE SERVIÇOS ADVOCATÍCIOS",
                r"HONORÁRIOS",
                r"CLÁUSULA",
                r"CONTRATANTE",
            ],
        }

        for doc_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text, re.IGNORECASE):
                    return doc_type

        return "DESCONHECIDO"

    def analyze_pdf_structure(self, input_pdf):
        """Analisa a estrutura do PDF e identifica onde está cada documento - VERSÃO DEBUG"""
        try:
            pdf_reader = PyPDF2.PdfReader(input_pdf)
            document_map = {}

            st.write(
                f"🔍 Analisando {Path(input_pdf).name} ({len(pdf_reader.pages)} páginas)"
            )

            for page_num in range(len(pdf_reader.pages)):
                text = self.extract_text_from_page(pdf_reader, page_num)

                # Mostrar um preview do texto para debug
                if len(text) > 0:
                    preview = text[:100].replace("\n", " ")  # Primeiros 100 caracteres
                    st.write(f"   Página {page_num + 1}: '{preview}...'")

                doc_type = self.identify_document_type(text)

                if doc_type != "DESCONHECIDO":
                    if doc_type not in document_map:
                        document_map[doc_type] = []
                    document_map[doc_type].append(page_num + 1)
                    st.write(
                        f"   ✅ Página {page_num + 1} identificada como: {doc_type}"
                    )

            return document_map, pdf_reader
        except Exception as e:
            st.error(f"❌ Erro ao analisar PDF {Path(input_pdf).name}: {e}")
            return {}, None

    def extract_specific_pages(self, pdf_reader, output_pdf, page_numbers):
        """
        Extrai páginas específicas de um PDF e salva em um novo arquivo
        """
        try:
            pdf_writer = PyPDF2.PdfWriter()

            for page_num in page_numbers:
                # Ajusta para índice base 0
                page = pdf_reader.pages[page_num - 1]
                pdf_writer.add_page(page)

            # Garantir que o arquivo seja salvo como PDF mesmo sem extensão
            if not output_pdf.lower().endswith(".pdf"):
                output_pdf += ".pdf"

            with open(output_pdf, "wb") as output_file:
                pdf_writer.write(output_file)
            return True
        except Exception as e:
            st.error(f"❌ Erro ao extrair páginas {page_numbers}: {e}")
            return False

    def extract_main_documents_structured(self, input_pdf, output_folder):
        """
        Extrai APENAS os 4 documentos principais especificados
        """
        try:
            pdf_reader = PyPDF2.PdfReader(input_pdf)

            documentos_principais = {
                "RG_CPF": [1, 2],  # RG da mãe
                "CERTIDAO_NASCIMENTO": [6],  # Certidão de Nascimento
                "COMPROVANTE_RESIDENCIA": [9],  # Comprovante de residência
                "TERMO_REPRESENTACAO_INSS": [11],  # Termo de Representação
            }

            # Extrair cada documento principal DIRETAMENTE na pasta do cliente
            documentos_extraidos = 0
            for doc_name, paginas in documentos_principais.items():
                output_pdf = os.path.join(output_folder, doc_name)  # SEM .pdf no final
                if self.extract_specific_pages(pdf_reader, output_pdf, paginas):
                    documentos_extraidos += 1
                    st.success(f"   ✅ {doc_name} extraído")

            return documentos_extraidos

        except Exception as e:
            st.error(f"❌ Erro na extração estruturada: {e}")
            return 0

    def process_pdf_analysis(self, pdf_files, pasta_clientes):
        """Processa a análise e organização dos PDFs - APENAS DOCUMENTOS PRINCIPAIS"""
        if not pdf_files:
            return 0, 0

        st.header("🔍 Analisando e Organizando Documentos")

        progress_bar = st.progress(0)
        total_files = len(pdf_files)

        pastas_criadas = 0
        arquivos_organizados = 0

        for i, pdf_path in enumerate(pdf_files):
            try:
                # Extrair nome do cliente COMPLETO
                nome_cliente = self.extract_client_name(pdf_path)
                nome_pasta = re.sub(r'[<>:"/\\|?*]', "", nome_cliente).strip()
                caminho_pasta = os.path.join(pasta_clientes, nome_pasta)

                # Criar pasta do cliente se não existir
                pasta_nova = False
                if not os.path.exists(caminho_pasta):
                    os.makedirs(caminho_pasta)
                    pasta_nova = True
                    pastas_criadas += 1

                # EXTRAIR APENAS OS DOCUMENTOS PRINCIPAIS
                st.info(
                    f"📊 Processando {Path(pdf_path).name} - Extração dos Documentos Principais"
                )

                documentos_extraidos = self.extract_main_documents_structured(
                    pdf_path, caminho_pasta
                )

                if documentos_extraidos > 0:
                    st.success(
                        f"   ✅ {documentos_extraidos} documento(s) principal(is) extraído(s)"
                    )

                # SEMPRE copiar o PDF original SEM extensão .pdf
                nome_arquivo = Path(pdf_path).stem.upper()  # MAIÚSCULAS e sem .pdf
                caminho_destino = os.path.join(caminho_pasta, nome_arquivo)
                shutil.copy2(pdf_path, caminho_destino)

                st.success(
                    f"📁 {Path(pdf_path).name} → {nome_pasta}/ ({documentos_extraidos} documentos extraídos + original)"
                )
                arquivos_organizados += documentos_extraidos + 1  # +1 para o original

            except Exception as e:
                st.error(f"❌ Erro ao processar {pdf_path}: {e}")

            # Atualizar barra de progresso
            if total_files > 0:
                progress_bar.progress((i + 1) / total_files)

        return pastas_criadas, arquivos_organizados

    def get_pdf_files_from_folder(self, pasta_downloads):
        """Obtém lista de arquivos PDF da pasta especificada"""
        if not pasta_downloads or not os.path.exists(pasta_downloads):
            return []

        try:
            pdf_files = list(Path(pasta_downloads).glob("*.pdf"))
            return [str(pdf) for pdf in pdf_files]
        except Exception as e:
            st.error(f"❌ Erro ao ler arquivos da pasta: {e}")
            return []

    def show_detected_files(self, pdf_files):
        """Mostra os arquivos detectados na pasta"""
        if pdf_files:
            st.success(
                f"✅ {len(pdf_files)} arquivo(s) PDF detectado(s) automaticamente"
            )

            with st.expander("📋 Arquivos que serão processados", expanded=True):
                for i, pdf_path in enumerate(pdf_files, 1):
                    file_name = Path(pdf_path).name
                    file_size = os.path.getsize(pdf_path) / 1024  # KB
                    st.write(f"{i}. 📄 {file_name} ({file_size:.1f} KB)")

            return True
        else:
            st.warning(
                """
            ⚠️ **Nenhum arquivo PDF encontrado para processar**
            
            **Soluções:**
            1. Verifique se o caminho da pasta está correto
            2. Certifique-se de que existem arquivos PDF na pasta
            3. Ou use a opção de upload manual abaixo
            """
            )
            return False

    def upload_files_interface(self):
        """Interface alternativa para upload manual de arquivos"""
        st.header("📤 Upload Manual (Opcional)")
        st.info("💡 Use esta opção apenas se quiser adicionar arquivos específicos")

        uploaded_files = st.file_uploader(
            "Selecione PDFs adicionais (opcional)",
            type=["pdf"],
            accept_multiple_files=True,
            help="Arquivos aqui serão adicionados aos já detectados automaticamente",
            key="file_uploader_unique",
        )

        if uploaded_files:
            st.success(
                f"✅ {len(uploaded_files)} arquivo(s) adicional(is) selecionado(s)"
            )
            return uploaded_files
        return None

    def save_uploaded_files(self, uploaded_files, pasta_downloads):
        """Salva os arquivos enviados para a pasta de downloads"""
        saved_files = []

        if not pasta_downloads:
            st.error("❌ Por favor, selecione uma pasta para os PDFs primeiro")
            return saved_files

        try:
            if not os.path.exists(pasta_downloads):
                os.makedirs(pasta_downloads)
        except Exception as e:
            st.error(f"❌ Erro ao criar pasta {pasta_downloads}: {e}")
            return saved_files

        for uploaded_file in uploaded_files:
            try:
                file_path = os.path.join(pasta_downloads, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_files.append(file_path)
            except Exception as e:
                st.error(f"❌ Erro ao salvar {uploaded_file.name}: {e}")

        return saved_files

    def extract_client_name(self, caminho_pdf):
        """Extrai nome do cliente do nome do arquivo"""
        try:
            nome_arquivo = Path(caminho_pdf).stem

            # Remove números e caracteres especiais, mas mantém espaços
            nome_limpo = re.sub(r"[_-]", " ", nome_arquivo)
            nome_limpo = re.sub(r"\d+", "", nome_limpo)  # Remove números
            nome_limpo = re.sub(
                r"\.pdf$", "", nome_limpo, flags=re.IGNORECASE
            )  # Remove .pdf se houver

            # Remove APENAS palavras que realmente não são parte do nome
            palavras_remover = [
                "documentos",
                "requerimento",
                "procuração",
                "contrato",
                "pdf",
                "copia",
            ]
            palavras = [
                palavra
                for palavra in nome_limpo.split()
                if palavra.lower() not in palavras_remover
            ]

            # NÃO remove palavras pequenas como "de", "da", "do" - são parte do nome!
            # Junta TODAS as palavras para manter nome completo
            if palavras:
                nome_cliente = " ".join(palavras).title()
                return nome_cliente
            else:
                return nome_limpo.title()

        except Exception as e:
            st.warning(f"⚠️ Usando nome do arquivo: {e}")
            return Path(caminho_pdf).stem

    def run_automation(self):
        """Função principal que executa toda a automação"""
        # Obter configurações de pastas
        pasta_downloads, pasta_clientes, pasta_processados = self.get_folder_paths()

        # Botão de executar
        st.header("🚀 Executar Automação")

        # Detectar arquivos automaticamente
        pdf_files = self.get_pdf_files_from_folder(pasta_downloads)

        # Mostrar arquivos detectados
        files_detected = self.show_detected_files(pdf_files)

        # Upload manual (opcional)
        uploaded_files = self.upload_files_interface()

        # Combinar arquivos detectados com upload manual
        all_files_to_process = pdf_files.copy()

        if uploaded_files:
            saved_uploaded_files = self.save_uploaded_files(
                uploaded_files, pasta_downloads
            )
            all_files_to_process.extend(saved_uploaded_files)
            st.success(
                f"📦 Total de {len(all_files_to_process)} arquivo(s) para processar"
            )

        if st.button(
            "▶️ EXECUTAR ORGANIZAÇÃO INTELIGENTE DE DOCUMENTOS",
            type="primary",
            use_container_width=True,
            key="btn_run_automation",
            disabled=len(all_files_to_process) == 0,
        ):

            # Verificar se as pastas foram selecionadas
            if not pasta_downloads or not pasta_clientes:
                st.error("❌ Por favor, selecione todas as pastas necessárias")
                return

            # Verificar se há arquivos para processar
            if len(all_files_to_process) == 0:
                st.warning("⚠️ Nenhum arquivo PDF encontrado para processar")
                return

            # Processar com análise inteligente
            pastas_criadas, arquivos_organizados = self.process_pdf_analysis(
                all_files_to_process, pasta_clientes
            )

            # Mensagem final
            if arquivos_organizados > 0:
                st.balloons()
                st.success(
                    f"""
                🎉 **Organização Inteligente Concluída com Sucesso!**

                **📊 Resumo:**
                - 📄 {len(all_files_to_process)} arquivo(s) processado(s)
                - 📁 {pastas_criadas} nova(s) pasta(s) de cliente(s) criada(s)
                - ✅ {arquivos_organizados} arquivo(s) organizado(s)
                - 🔍 Documentos classificados automaticamente

                **📍 Localização:**
                - Pastas organizadas em: `{pasta_clientes}`
                - Cada pasta contém documentos separados por tipo
                - Documentos principais extraídos em subpasta 'documentos_extraidos'
                """
                )


# Função principal
def main():
    # Inicializar session state se não existir
    if "pasta_downloads" not in st.session_state:
        st.session_state["pasta_downloads"] = ""
    if "pasta_clientes" not in st.session_state:
        st.session_state["pasta_clientes"] = ""
    if "pasta_processados" not in st.session_state:
        st.session_state["pasta_processados"] = ""
    if "show_folder_help" not in st.session_state:
        st.session_state["show_folder_help"] = False

    app = AutomatizadorRequerimentosWeb()

    # Executar automação
    app.run_automation()

    # Instruções de uso
    with st.expander("📋 Instruções de Uso", expanded=False):
        st.markdown(
            """
        **🌐 COMO USAR - MODO INTELIGENTE:**

        1. **📁 Configurar Pastas**:
           - **Pasta dos PDFs**: Digite o caminho onde estão os PDFs
           - **Pasta dos Clientes**: Digite onde criar as pastas organizadas
           - Use **🔄 Pastas Padrão** para nomes simples

        2. **📤 Upload de Arquivos**:
           - O sistema detecta automaticamente os PDFs na pasta
           - Ou use upload manual para arquivos específicos

        3. **🚀 Executar Organização Inteligente**:
           - Clique em **EXECUTAR ORGANIZAÇÃO INTELIGENTE DE DOCUMENTOS**
           - O sistema analisa e classifica automaticamente os documentos:
             - 📄 RG/CPF da mãe (páginas 1-2)
             - 📄 Certidão de Nascimento (página 6)  
             - 📄 Comprovante de Residência (página 9)
             - 📄 Termo de Representação (página 11)
             - 📄 Outros documentos automaticamente identificados

        **⚡ Funcionalidades Inteligentes:**
        - Extração estruturada dos documentos principais
        - Classificação automática de documentos adicionais
        - Organização em pastas por cliente
        - Subpasta 'documentos_extraidos' com documentos principais
        - Mantém estrutura original quando necessário
        """
        )


if __name__ == "__main__":
    main()
