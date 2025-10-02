import streamlit as st
import os
import re
from pathlib import Path
import shutil


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
        """Interface para usuário definir os diretórios com seletores"""
        st.sidebar.header("📁 Configurações de Pastas")

        with st.sidebar.expander("Configurar Diretórios", expanded=True):
            st.write("**Selecione as pastas no seu computador:**")

            # Pasta dos PDFs (WhatsApp)
            st.subheader("📥 Pasta dos PDFs (WhatsApp)")
            col1, col2 = st.columns([3, 1])

            with col1:
                pasta_downloads = st.text_input(
                    "Caminho:",
                    value=st.session_state.get("pasta_downloads", ""),
                    help="Selecione a pasta onde estão os PDFs do WhatsApp",
                    key="pasta_downloads_input_unique",
                )

            with col2:
                if st.button("📁 Selecionar", key="btn_select_downloads"):
                    st.session_state["show_folder_help"] = True

            if st.session_state.get("show_folder_help", False):
                st.info(
                    """
                **💡 Como selecionar pasta no navegador:**
                1. Clique no campo acima
                2. Digite o caminho manualmente (ex: C:/Users/SeuNome/Documentos)
                3. Ou copie e cole o caminho do explorador de arquivos
                """
                )

            # Mostrar arquivos detectados automaticamente
            if pasta_downloads and os.path.exists(pasta_downloads):
                pdf_files = list(Path(pasta_downloads).glob("*.pdf"))
                if pdf_files:
                    st.success(f"📄 {len(pdf_files)} arquivo(s) PDF detectado(s)")
                    # Mostrar alguns arquivos diretamente sem expander
                    st.write("**Arquivos detectados:**")
                    for pdf in pdf_files[:5]:  # Mostra até 5 arquivos
                        st.write(f"• {pdf.name}")
                    if len(pdf_files) > 5:
                        st.info(f"... e mais {len(pdf_files) - 5} arquivos")
                else:
                    st.warning("⚠️ Nenhum arquivo PDF encontrado nesta pasta")

            st.divider()

            # ... o resto do código permanece igual ...

            # Pasta dos Clientes (Drive)
            st.subheader("📂 Pasta dos Clientes (Drive)")
            col1, col2 = st.columns([3, 1])

            with col1:
                pasta_clientes = st.text_input(
                    "Caminho:",
                    value=st.session_state.get("pasta_clientes", ""),
                    help="Pasta onde serão criadas as pastas dos clientes",
                    key="pasta_clientes_input_unique",
                )

            with col2:
                if st.button("📁 Selecionar", key="btn_select_clientes"):
                    st.info("💡 Digite o caminho ou cole do explorador de arquivos")

            st.divider()

            # Pasta de Processamento
            st.subheader("⚙️ Pasta de Processamento")
            col1, col2 = st.columns([3, 1])

            with col1:
                pasta_processados = st.text_input(
                    "Caminho:",
                    value=st.session_state.get("pasta_processados", ""),
                    help="Pasta para arquivos temporários durante processamento",
                    key="pasta_processados_input_unique",
                )

            with col2:
                if st.button("📁 Selecionar", key="btn_select_processados"):
                    st.info("💡 Digite o caminho ou cole do explorador de arquivos")

            # Botões de ação rápida
            st.divider()
            st.write("**⚡ Ações Rápidas:**")
            col1 = st.columns(2)

            with col1:
                if st.button("🗑️ Limpar Tudo", key="btn_clear_all"):
                    st.session_state["pasta_downloads"] = ""
                    st.session_state["pasta_clientes"] = ""
                    st.session_state["pasta_processados"] = ""
                    st.rerun()

        # Atualizar session state com os valores atuais
        if pasta_downloads:
            st.session_state["pasta_downloads"] = pasta_downloads
        if pasta_clientes:
            st.session_state["pasta_clientes"] = pasta_clientes
        if pasta_processados:
            st.session_state["pasta_processados"] = pasta_processados

        return pasta_downloads, pasta_clientes, pasta_processados

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
            # Remove sufixos comuns
            nome_limpo = re.sub(r"[_-]", " ", nome_arquivo)

            # Tenta capitalizar como nome próprio
            palavras = nome_limpo.split()
            if len(palavras) >= 2:
                nome_cliente = " ".join(palavras[:2]).title()
            else:
                nome_cliente = nome_limpo.title()

            return nome_cliente
        except:
            return Path(caminho_pdf).stem

    def organize_files(self, pdf_files, pasta_clientes):
        """Organiza os arquivos em pastas por cliente"""
        st.header("📁 Organizando Pastas dos Clientes")

        if not pasta_clientes:
            st.error("❌ Por favor, selecione uma pasta para os clientes primeiro")
            return 0, 0

        try:
            if not os.path.exists(pasta_clientes):
                os.makedirs(pasta_clientes)
                st.info(f"📁 Pasta criada: {pasta_clientes}")
        except Exception as e:
            st.error(f"❌ Erro ao criar pasta {pasta_clientes}: {e}")
            return 0, 0

        progress_bar = st.progress(0)
        total_files = len(pdf_files)

        pastas_criadas = 0
        arquivos_organizados = 0

        for i, pdf_path in enumerate(pdf_files):
            try:
                # Extrair nome do cliente
                nome_cliente = self.extract_client_name(pdf_path)

                # Limpar nome para pasta
                nome_pasta = re.sub(r'[<>:"/\\|?*]', "", nome_cliente).strip()
                caminho_pasta = os.path.join(pasta_clientes, nome_pasta)

                # Criar pasta se não existir
                pasta_nova = False
                if not os.path.exists(caminho_pasta):
                    os.makedirs(caminho_pasta)
                    pasta_nova = True
                    pastas_criadas += 1

                # Copiar arquivo
                nome_arquivo = Path(pdf_path).name
                caminho_destino = os.path.join(caminho_pasta, nome_arquivo)
                shutil.copy2(pdf_path, caminho_destino)
                arquivos_organizados += 1

                if pasta_nova:
                    st.success(f"📁 {nome_arquivo} → 🆕 {nome_pasta}/")
                else:
                    st.success(f"📄 {nome_arquivo} → {nome_pasta}/")

            except Exception as e:
                st.error(f"❌ Erro ao organizar {pdf_path}: {e}")

            # Atualizar barra de progresso
            if total_files > 0:
                progress_bar.progress((i + 1) / total_files)

        return pastas_criadas, arquivos_organizados

    def show_folder_structure(self):
        """Mostra a estrutura de pastas atual"""
        st.sidebar.header("📊 Estrutura de Pastas")

        pasta_downloads = st.session_state.get("pasta_downloads", "")
        pasta_clientes = st.session_state.get("pasta_clientes", "")
        pasta_processados = st.session_state.get("pasta_processados", "")

        if st.sidebar.button(
            "🔄 Atualizar Visualização",
            use_container_width=True,
            key="btn_refresh_view",
        ):
            try:
                downloads_count = 0
                clientes_count = 0

                if pasta_downloads and os.path.exists(pasta_downloads):
                    downloads_count = len(list(Path(pasta_downloads).glob("*.pdf")))

                if pasta_clientes and os.path.exists(pasta_clientes):
                    clientes_count = len(
                        [f for f in Path(pasta_clientes).iterdir() if f.is_dir()]
                    )

                col1, col2 = st.sidebar.columns(2)
                with col1:
                    st.metric("📥 PDFs para Processar", downloads_count)
                with col2:
                    st.metric("📁 Pastas de Clientes", clientes_count)

            except Exception as e:
                st.sidebar.error(f"Erro: {e}")

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
            "▶️ EXECUTAR ORGANIZAÇÃO DE ARQUIVOS",
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

            # Organizar arquivos
            pastas_criadas, arquivos_organizados = self.organize_files(
                all_files_to_process, pasta_clientes
            )

            # Mensagem final
            if arquivos_organizados > 0:
                st.balloons()
                st.success(
                    f"""
                🎉 **Organização Concluída com Sucesso!**

                **📊 Resumo:**
                - 📄 {len(all_files_to_process)} arquivo(s) processado(s)
                - 📁 {pastas_criadas} nova(s) pasta(s) de cliente(s) criada(s)
                - ✅ {arquivos_organizados} arquivo(s) organizado(s)

                **📍 Localização:**
                - Pastas organizadas em: `{pasta_clientes}`
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

    # Mostrar estrutura de pastas
    app.show_folder_structure()

    # Executar automação
    app.run_automation()

    # Instruções de uso
    with st.expander("📋 Instruções de Uso", expanded=False):
        st.markdown(
            """
        **🌐 COMO USAR - MODO AUTOMÁTICO:**

        1. **📁 Configurar Pastas** (barra lateral):
           - **Pasta dos PDFs**: Selecione a pasta onde estão os PDFs do WhatsApp
           - **Pasta dos Clientes**: Selecione onde criar as pastas organizadas
           - O sistema detecta automaticamente os PDFs disponíveis

        2. **🚀 Executar Organização**:
           - Clique em **EXECUTAR ORGANIZAÇÃO DE ARQUIVOS**
           - Os PDFs serão automaticamente organizados em pastas por cliente

        **📤 Upload Manual (Opcional):**
        - Use apenas se quiser adicionar arquivos específicos
        - Os arquivos enviados serão copiados para a pasta dos PDFs

        **⚡ Dicas:**
        - Os nomes dos clientes são extraídos automaticamente dos nomes dos arquivos
        - Use **🔄 Atualizar Visualização** para ver estatísticas atualizadas
        - O botão de execução só fica ativo quando há arquivos para processar
        """
        )


if __name__ == "__main__":
    main()
