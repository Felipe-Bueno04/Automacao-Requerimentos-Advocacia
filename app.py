import streamlit as st
import os
import re
import tempfile
from pathlib import Path
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import shutil

class AutomatizadorRequerimentosWeb:
    def __init__(self):
        self.setup_page()
        self.setup_cloud_folders()
    
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
    
    def setup_cloud_folders(self):
        """Configura pastas padrão para ambiente de nuvem"""
        # Pastas essenciais que sempre devem existir na nuvem
        pastas_essenciais = ['downloads_whatsapp', 'drive_clientes', 'pdfs_processados']
        for pasta in pastas_essenciais:
            if not os.path.exists(pasta):
                os.makedirs(pasta)
                st.sidebar.info(f"📁 Criada pasta: {pasta}")
    
    def get_folder_paths(self):
        """Interface para usuário definir os diretórios"""
        st.sidebar.header("📁 Configurações de Pastas")
        
        with st.sidebar.expander("Configurar Diretórios", expanded=True):
            pasta_downloads = st.text_input(
                "Pasta dos PDFs (WhatsApp):",
                value="downloads_whatsapp",
                help="Pasta onde estão os PDFs baixados do WhatsApp"
            )
            
            pasta_clientes = st.text_input(
                "Pasta dos Clientes (Drive):", 
                value="drive_clientes",
                help="Pasta que simula o Google Drive com as pastas dos clientes"
            )
            
            pasta_processados = st.text_input(
                "Pasta de Processamento:",
                value="pdfs_processados", 
                help="Pasta temporária para arquivos durante o processamento"
            )
        
        # Garante que as pastas personalizadas também existam
        self.create_folders(pasta_downloads, pasta_clientes, pasta_processados)
        return pasta_downloads, pasta_clientes, pasta_processados
    
    def create_folders(self, *folders):
        """Cria as pastas se não existirem"""
        for folder in folders:
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                st.sidebar.success(f"✅ Pasta criada: {folder}")
    
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
        
        for uploaded_file in uploaded_files:
            try:
                # Cria caminho completo
                file_path = os.path.join(pasta_downloads, uploaded_file.name)
                
                # Salva o arquivo
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                saved_files.append(file_path)
                st.info(f"💾 Salvo: {uploaded_file.name}")
                
            except Exception as e:
                st.error(f"❌ Erro ao salvar {uploaded_file.name}: {e}")
        
        return saved_files
    
    def step_rotate_pdf(self, caminho_pdf, pasta_processados):
        """Passo 3: Rotacionar PDFs"""
        try:
            with st.spinner(f"Rotacionando {os.path.basename(caminho_pdf)}..."):
                with open(caminho_pdf, 'rb') as arquivo:
                    leitor = PyPDF2.PdfReader(arquivo)
                    escritor = PyPDF2.PdfWriter()
                    
                    paginas_rotacionadas = 0
                    for pagina_num in range(len(leitor.pages)):
                        pagina = leitor.pages[pagina_num]
                        
                        # Verificar orientação
                        if pagina.mediabox.width < pagina.mediabox.height:
                            pagina.rotate(90)
                            paginas_rotacionadas += 1
                        
                        escritor.add_page(pagina)
                    
                    # Salvar PDF rotacionado
                    nome_arquivo = Path(caminho_pdf).stem
                    caminho_saida = os.path.join(pasta_processados, f"{nome_arquivo}_rotacionado.pdf")
                    
                    with open(caminho_saida, 'wb') as saida:
                        escritor.write(saida)
                
                st.success(f"✅ Rotacionado: {os.path.basename(caminho_saida)} ({paginas_rotacionadas} páginas ajustadas)")
                return caminho_saida
                
        except Exception as e:
            st.error(f"❌ Erro ao rotacionar {caminho_pdf}: {e}")
            return caminho_pdf
    
    def step_split_pdf(self, caminho_pdf, pasta_processados):
        """Passo 4: Dividir PDF em páginas individuais"""
        try:
            with st.spinner(f"Dividindo {os.path.basename(caminho_pdf)}..."):
                with open(caminho_pdf, 'rb') as arquivo:
                    leitor = PyPDF2.PdfReader(arquivo)
                    nome_base = Path(caminho_pdf).stem
                    
                    pdfs_separados = []
                    
                    for i, pagina in enumerate(leitor.pages):
                        escritor = PyPDF2.PdfWriter()
                        escritor.add_page(pagina)
                        
                        nome_arquivo = f"{nome_base}_pagina_{i+1}.pdf"
                        caminho_saida = os.path.join(pasta_processados, nome_arquivo)
                        
                        with open(caminho_saida, 'wb') as saida:
                            escritor.write(saida)
                        
                        pdfs_separados.append(caminho_saida)
                    
                st.success(f"✅ Dividido em {len(pdfs_separados)} páginas")
                return pdfs_separados
                
        except Exception as e:
            st.error(f"❌ Erro ao dividir {caminho_pdf}: {e}")
            return [caminho_pdf]
    
    def extract_client_name(self, caminho_pdf):
        """Tenta extrair nome do cliente do PDF"""
        try:
            # Método simples: usar nome do arquivo
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
            st.warning(f"⚠️ Usando nome do arquivo: {e}")
            return Path(caminho_pdf).stem
    
    def step_organize_folders(self, pdfs_separados, pasta_clientes):
        """Passo 5: Organizar em pastas dos clientes"""
        st.header("📁 Organizando Pastas dos Clientes")
        
        progress_bar = st.progress(0)
        total_files = len(pdfs_separados)
        
        pastas_criadas = 0
        arquivos_organizados = 0
        
        for i, pdf in enumerate(pdfs_separados):
            try:
                # Extrair nome do cliente
                nome_cliente = self.extract_client_name(pdf)
                
                # Limpar nome para pasta
                nome_pasta = re.sub(r'[<>:"/\\|?*]', '', nome_cliente).strip()
                caminho_pasta = os.path.join(pasta_clientes, nome_pasta)
                
                # Criar pasta se não existir
                pasta_nova = False
                if not os.path.exists(caminho_pasta):
                    os.makedirs(caminho_pasta)
                    pasta_nova = True
                    pastas_criadas += 1
                
                # Mover arquivo
                nome_arquivo = Path(pdf).name
                caminho_destino = os.path.join(caminho_pasta, nome_arquivo)
                shutil.copy2(pdf, caminho_destino)
                arquivos_organizados += 1
                
                if pasta_nova:
                    st.success(f"📁 {nome_arquivo} → 🆕 {nome_pasta}/")
                else:
                    st.success(f"📄 {nome_arquivo} → {nome_pasta}/")
                
            except Exception as e:
                st.error(f"❌ Erro ao organizar {pdf}: {e}")
            
            # Atualizar barra de progresso
            progress_bar.progress((i + 1) / total_files)
        
        return pastas_criadas, arquivos_organizados
    
    def run_automation(self):
        """Função principal que executa toda a automação"""
        # Obter configurações de pastas
        pasta_downloads, pasta_clientes, pasta_processados = self.get_folder_paths()
        
        # Botão de executar
        st.header("🚀 Executar Automação")
        
        if st.button("▶️ EXECUTAR AUTOMAÇÃO COMPLETA", type="primary", use_container_width=True):
            
            # Fazer upload de arquivos
            uploaded_files = self.upload_files_interface()
            
            if not uploaded_files:
                st.warning("⚠️ Por favor, faça upload dos PDFs primeiro")
                return
            
            # Salvar arquivos enviados
            with st.status("📥 Salvando arquivos...", expanded=True) as status:
                saved_files = self.save_uploaded_files(uploaded_files, pasta_downloads)
                status.update(label="✅ Arquivos salvos com sucesso!", state="complete")
            
            # Processar cada arquivo
            all_separated_pdfs = []
            
            for pdf_path in saved_files:
                st.subheader(f"🔄 Processando: {os.path.basename(pdf_path)}")
                
                # Passo 3: Rotacionar
                rotated_pdf = self.step_rotate_pdf(pdf_path, pasta_processados)
                
                # Passo 4: Dividir
                separated_pdfs = self.step_split_pdf(rotated_pdf, pasta_processados)
                all_separated_pdfs.extend(separated_pdfs)
            
            # Passo 5: Organizar pastas
            if all_separated_pdfs:
                pastas_criadas, arquivos_organizados = self.step_organize_folders(all_separated_pdfs, pasta_clientes)
                
                # Mensagem final
                st.balloons()
                st.success(f"""
                🎉 **Automação Concluída com Sucesso!**

                **📊 Resumo do Processamento:**
                - 📄 {len(saved_files)} arquivo(s) original(is) processado(s)
                - 📄 {len(all_separated_pdfs)} documento(s) individual(is) criado(s)
                - 📁 {pastas_criadas} nova(s) pasta(s) de cliente(s) criada(s)
                - ✅ {arquivos_organizados} arquivo(s) organizado(s)

                **📍 Localização dos Resultados:**
                - Pastas dos clientes: `{pasta_clientes}`
                - Arquivos processados: `{pasta_processados}`

                **➡️ Próximos Passos:**
                1. Verifique as pastas dos clientes criadas
                2. Faça upload manual para o Google Drive real
                3. Os arquivos já estão rotacionados e organizados!
                """)
    
    def show_folder_structure(self):
        """Mostra a estrutura de pastas atual"""
        st.sidebar.header("📊 Estrutura de Pastas")
        
        pasta_downloads, pasta_clientes, pasta_processados = self.get_folder_paths()
        
        if st.sidebar.button("🔄 Atualizar Visualização", use_container_width=True):
            try:
                # Contar arquivos nas pastas
                downloads_count = len(list(Path(pasta_downloads).glob("*.pdf")))
                clientes_count = len([f for f in Path(pasta_clientes).iterdir() if f.is_dir()])
                processados_count = len(list(Path(pasta_processados).glob("*.pdf")))
                
                col1, col2, col3 = st.sidebar.columns(3)
                with col1:
                    st.metric("📥 PDFs para Processar", downloads_count)
                with col2:
                    st.metric("📁 Pastas de Clientes", clientes_count)
                with col3:
                    st.metric("🔄 Processados", processados_count)
                
                # Mostrar pastas de clientes
                if clientes_count > 0:
                    st.sidebar.subheader("👥 Clientes Cadastrados:")
                    clientes = [f.name for f in Path(pasta_clientes).iterdir() if f.is_dir()]
                    for cliente in clientes[:8]:  # Mostra apenas os 8 primeiros
                        st.sidebar.write(f"📁 {cliente}")
                    
                    if len(clientes) > 8:
                        st.sidebar.write(f"📚 ... e mais {len(clientes) - 8} clientes")
                        
            except Exception as e:
                st.sidebar.error(f"Erro ao ler estrutura: {e}")
        
        # Sempre mostrar informações básicas
        try:
            pasta_downloads, pasta_clientes, pasta_processados = self.get_folder_paths()
            downloads_count = len(list(Path(pasta_downloads).glob("*.pdf")))
            if downloads_count > 0:
                st.sidebar.info(f"📂 {downloads_count} PDF(s) aguardando processamento")
        except:
            pass

    def show_cloud_info(self):
        """Mostra informações específicas da versão cloud"""
        with st.sidebar.expander("🌐 Info Cloud"):
            st.markdown("""
            **Versão Hospedada na Nuvem**
            - ✅ Disponível 24/7
            - ✅ Acesse de qualquer lugar
            - ✅ Sem instalação necessária
            - ⚠️ Arquivos temporários
            - ⚠️ Limite de storage
            """)

# Função principal
def main():
    app = AutomatizadorRequerimentosWeb()
    
    # Mostrar informações cloud
    app.show_cloud_info()
    
    # Mostrar estrutura de pastas
    app.show_folder_structure()
    
    # Executar automação
    app.run_automation()
    
    # Instruções de uso
    with st.expander("📋 Instruções de Uso - VERSÃO CLOUD"):
        st.markdown("""
        **🌐 COMO USAR ESTA VERSÃO ONLINE:**

        1. **📁 Configurar Pastas** (barra lateral):
           - Defina os nomes das pastas que o sistema usará
           - As pastas são criadas automaticamente na nuvem

        2. **📤 Fazer Upload dos PDFs**:
           - Selecione todos os PDFs baixados do WhatsApp
           - Podem ser múltiplos arquivos de uma vez
           - Os arquivos são salvos temporariamente na nuvem

        3. **🚀 Executar Automação**:
           - Clique no botão "EXECUTAR AUTOMAÇÃO COMPLETA"
           - O sistema fará automaticamente:
             - 📤 Upload dos arquivos para a nuvem
             - 🔄 Rotação de páginas verticais
             - ✂️ Divisão em páginas individuais  
             - 📁 Organização em pastas por cliente

        4. **📊 Resultado**:
           - Cada cliente terá sua própria pasta na nuvem
           - Os documentos estarão organizados e rotacionados
           - Faça download manual para seu Google Drive real

        **⚡ Vantagens desta Versão Cloud:**
        - ✅ Disponível 24 horas por dia
        - ✅ Acessível de qualquer dispositivo
        - ✅ Sem necessidade de instalação
        - ✅ Atualizações automáticas
        - ✅ Interface moderna e responsiva

        **📝 Funcionalidades Incluídas:**
        - ✅ Rotação automática de páginas
        - ✅ Divisão de PDFs multi-páginas
        - ✅ Organização por pastas de clientes
        - ✅ Interface web amigável
        - ✅ Barra de progresso em tempo real
        - ✅ Relatório final detalhado
        """)

if __name__ == "__main__":
    main()