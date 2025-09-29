import streamlit as st
import os
import re
from pathlib import Path
import shutil
import base64

class AutomatizadorRequerimentosWeb:
    def __init__(self):
        self.setup_page()
    
    def setup_page(self):
        """Configura a página do Streamlit para nuvem"""
        st.set_page_config(
            page_title="Automatizador Jurídico - ONLINE",
            page_icon="⚖️",
            layout="wide"
        )
        
        st.title("🌐 Automatizador de Requerimentos - VERSÃO ONLINE")
        st.success("✅ Esta versão está HOSPEDADA NA NUVEM e disponível 24/7!")
        st.markdown("""
        **Automatize o processamento de documentos jurídicos**  
        Sistema sempre disponível para organizar requerimentos de forma eficiente.
        """)
    
    def get_folder_paths(self):
        """Interface para usuário definir os diretórios"""
        st.sidebar.header("📁 Configurações de Pastas")
        
        with st.sidebar.expander("Configurar Diretórios", expanded=True):
            st.write("Selecione as pastas no seu computador:")
            
            # Pasta dos PDFs (WhatsApp)
            st.subheader("📥 Pasta dos PDFs (WhatsApp)")
            pasta_downloads = st.text_input(
                "Pasta onde estão os PDFs baixados do WhatsApp:",
                value="",
                help="Digite o caminho completo da pasta ou use o botão para selecionar",
                key="pasta_downloads_input"
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("📁 Selecionar Pasta PDFs", key="btn_pasta_downloads"):
                    st.info("💡 Navegue até a pasta onde estão os PDFs do WhatsApp")
            with col2:
                if st.button("🔄 Limpar", key="btn_clear_downloads"):
                    pasta_downloads = ""
            
            st.divider()
            
            # Pasta dos Clientes (Drive)
            st.subheader("📂 Pasta dos Clientes (Drive)")
            pasta_clientes = st.text_input(
                "Pasta onde serão criadas as pastas dos clientes:",
                value="", 
                help="Digite o caminho completo da pasta de destino",
                key="pasta_clientes_input"
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("📁 Selecionar Pasta Clientes", key="btn_pasta_clientes"):
                    st.info("💡 Navegue até a pasta onde criar as pastas dos clientes")
            with col2:
                if st.button("🔄 Limpar", key="btn_clear_clientes"):
                    pasta_clientes = ""
            
            st.divider()
            
            # Pasta de Processamento
            st.subheader("⚙️ Pasta de Processamento")
            pasta_processados = st.text_input(
                "Pasta temporária para processamento:",
                value="", 
                help="Digite o caminho completo da pasta temporária",
                key="pasta_processados_input"
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("📁 Selecionar Pasta Processamento", key="btn_pasta_processados"):
                    st.info("💡 Navegue até a pasta para arquivos temporários")
            with col2:
                if st.button("🔄 Limpar", key="btn_clear_processados"):
                    pasta_processados = ""
        
        return pasta_downloads, pasta_clientes, pasta_processados

    def upload_files_interface(self):
        """Interface para upload de arquivos"""
        st.header("📤 Fazer Upload dos PDFs")
        
        uploaded_files = st.file_uploader(
            "Selecione os PDFs do WhatsApp",
            type=['pdf'],
            accept_multiple_files=True,
            help="Selecione todos os PDFs que deseja processar"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} arquivo(s) selecionado(s)")
            
            # Mostrar preview dos arquivos
            with st.expander("📋 Arquivos Selecionados"):
                for file in uploaded_files:
                    st.write(f"📄 {file.name} ({file.size / 1024:.1f} KB)")
            
            return uploaded_files
        return None

    def save_uploaded_files(self, uploaded_files, pasta_downloads):
        """Salva os arquivos enviados para a pasta de downloads"""
        saved_files = []
        
        # Verifica se a pasta existe
        if not pasta_downloads:
            st.error("❌ Por favor, selecione uma pasta para os PDFs primeiro")
            return saved_files
        
        if not os.path.exists(pasta_downloads):
            st.error(f"❌ Pasta não existe: {pasta_downloads}")
            return saved_files
        
        for uploaded_file in uploaded_files:
            try:
                file_path = os.path.join(pasta_downloads, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_files.append(file_path)
                st.info(f"💾 Salvo: {uploaded_file.name}")
            except Exception as e:
                st.error(f"❌ Erro ao salvar {uploaded_file.name}: {e}")
        
        return saved_files

    def extract_client_name(self, caminho_pdf):
        """Extrai nome do cliente do nome do arquivo"""
        try:
            nome_arquivo = Path(caminho_pdf).stem
            # Remove sufixos comuns
            nome_limpo = re.sub(r'(_rotacionado|_pagina_\d+)$', '', nome_arquivo)
            nome_limpo = re.sub(r'[_-]', ' ', nome_limpo)
            
            # Tenta capitalizar como nome próprio
            palavras = nome_limpo.split()
            if len(palavras) >= 2:
                nome_cliente = ' '.join(palavras[:2]).title()
            else:
                nome_cliente = nome_limpo.title()
            
            return nome_cliente
        except Exception as e:
            return Path(caminho_pdf).stem

    def organize_files(self, saved_files, pasta_clientes):
        """Organiza os arquivos em pastas por cliente"""
        st.header("📁 Organizando Pastas dos Clientes")
        
        # Verifica se a pasta existe
        if not pasta_clientes:
            st.error("❌ Por favor, selecione uma pasta para os clientes primeiro")
            return 0, 0
        
        if not os.path.exists(pasta_clientes):
            st.error(f"❌ Pasta não existe: {pasta_clientes}")
            return 0, 0
        
        progress_bar = st.progress(0)
        total_files = len(saved_files)
        
        pastas_criadas = 0
        arquivos_organizados = 0
        
        for i, pdf_path in enumerate(saved_files):
            try:
                # Extrair nome do cliente
                nome_cliente = self.extract_client_name(pdf_path)
                
                # Limpar nome para pasta
                nome_pasta = re.sub(r'[<>:"/\\|?*]', '', nome_cliente).strip()
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

    def create_download_link(self, file_path):
        """Cria link para download do arquivo"""
        with open(file_path, "rb") as f:
            bytes_data = f.read()
        b64 = base64.b64encode(bytes_data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">📥 Download {os.path.basename(file_path)}</a>'
        return href

    def run_automation(self):
        """Função principal que executa toda a automação"""
        # Obter configurações de pastas
        pasta_downloads, pasta_clientes, pasta_processados = self.get_folder_paths()
        
        # Botão de executar
        st.header("🚀 Executar Automação")
        
        if st.button("▶️ EXECUTAR ORGANIZAÇÃO DE ARQUIVOS", type="primary", use_container_width=True):
            
            # Verificar se as pastas foram selecionadas
            if not pasta_downloads or not pasta_clientes:
                st.error("❌ Por favor, selecione todas as pastas necessárias")
                return
            
            # Fazer upload de arquivos
            uploaded_files = self.upload_files_interface()
            
            if not uploaded_files:
                st.warning("⚠️ Por favor, faça upload dos PDFs primeiro")
                return
            
            # Salvar arquivos enviados
            with st.status("📥 Salvando arquivos...", expanded=True) as status:
                saved_files = self.save_uploaded_files(uploaded_files, pasta_downloads)
                if saved_files:
                    status.update(label="✅ Arquivos salvos com sucesso!", state="complete")
                else:
                    status.update(label="❌ Erro ao salvar arquivos", state="error")
                    return
            
            # Organizar arquivos
            pastas_criadas, arquivos_organizados = self.organize_files(saved_files, pasta_clientes)
            
            # Mensagem final
            if arquivos_organizados > 0:
                st.balloons()
                st.success(f"""
                🎉 **Organização Concluída com Sucesso!**

                **📊 Resumo:**
                - 📄 {len(saved_files)} arquivo(s) processado(s)
                - 📁 {pastas_criadas} nova(s) pasta(s) de cliente(s) criada(s)
                - ✅ {arquivos_organizados} arquivo(s) organizado(s)
                """)
                
                # Mostrar links para download
                st.header("📥 Downloads Disponíveis")
                st.info("💡 **Dica:** Faça download dos arquivos organizados")
                
                for root, dirs, files in os.walk(pasta_clientes):
                    for file in files:
                        if file.endswith('.pdf'):
                            file_path = os.path.join(root, file)
                            st.markdown(self.create_download_link(file_path), unsafe_allow_html=True)

    def show_folder_structure(self):
        """Mostra a estrutura de pastas atual"""
        st.sidebar.header("📊 Estrutura de Pastas")
        
        pasta_downloads, pasta_clientes, pasta_processados = self.get_folder_paths()
        
        if st.sidebar.button("🔄 Atualizar Visualização", use_container_width=True):
            try:
                downloads_count = len(list(Path(pasta_downloads).glob("*.pdf"))) if pasta_downloads and os.path.exists(pasta_downloads) else 0
                clientes_count = len([f for f in Path(pasta_clientes).iterdir() if f.is_dir()]) if pasta_clientes and os.path.exists(pasta_clientes) else 0
                
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    st.metric("📥 PDFs para Processar", downloads_count)
                with col2:
                    st.metric("📁 Pastas de Clientes", clientes_count)
                
            except Exception as e:
                st.sidebar.error(f"Erro ao ler estrutura: {e}")

# FUNÇÃO PRINCIPAL - ESTA PARTE ESTAVA FALTANDO!
def main():
    # Criar instância da classe
    app = AutomatizadorRequerimentosWeb()
    
    # Mostrar estrutura de pastas
    app.show_folder_structure()
    
    # Executar automação
    app.run_automation()
    
    # Instruções de uso
    with st.expander("📋 Instruções de Uso - VERSÃO CLOUD"):
        st.markdown("""
        **🌐 COMO USAR ESTA VERSÃO ONLINE:**

        1. **📁 Configurar Pastas** (barra lateral):
           - Selecione as pastas no seu computador
           - Pasta PDFs: onde estão os arquivos do WhatsApp
           - Pasta Clientes: onde criar as pastas organizadas

        2. **📤 Fazer Upload dos PDFs**:
           - Selecione todos os PDFs baixados do WhatsApp
           - Podem ser múltiplos arquivos de uma vez

        3. **🚀 Executar Organização**:
           - Clique no botão "EXECUTAR ORGANIZAÇÃO DE ARQUIVOS"
           - O sistema organizará os PDFs em pastas por cliente

        4. **📥 Fazer Download**:
           - Use os links de download para baixar os arquivos organizados
           - Faça upload manual para seu Google Drive real
        """)

# Este if é ESSENCIAL para o Streamlit funcionar
if __name__ == "__main__":
    main()