# 🧾 MeuDanfe Downloader GUI

Aplicativo em Python para baixar automaticamente XML e DANFE (PDF) de notas fiscais eletrônicas a partir das chaves de acesso, usando a API do [MeuDanfe](https://meudanfe.com.br/).

## 🚀 Funcionalidades
- Interface gráfica intuitiva (Tkinter)
- Inserção manual de chaves NFe
- Download automático de XML e PDF (DANFE)
- Geração organizada de arquivos em pastas locais
- Criação de executável `.exe` com ícone personalizado

## 🧩 Requisitos
- Python 3.10+  
- Conta e API Key do [MeuDanfe](https://meudanfe.com.br/)
- Pacotes listados em `requirements.txt`

## 💻 Instalação
1. Clone o repositório:
   bash
   git clone https://github.com/seuusuario/meu_baixa_xml.git

2. Instale as dependências: pip install -r requirements.txt

3. Execute: python meudanfe_gui.py

## 💻 Criar o executável
- Para gerar o .exe:
- pyinstaller --noconsole --onefile --icon="icone.ico" meudanfe_gui.py


O executável final ficará em dist/meudanfe_gui.exe

## 🧑‍💻 Autor

Desenvolvido por Fernando Henrique Stentzler - Otimiza Transportes e Logística LTDA
