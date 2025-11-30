#!/usr/bin/env python3
"""
💼 MeuDanfe Downloader GUI
Permite inserir chaves manualmente ou colar em lote,
escolher a pasta de destino, e baixar automaticamente
os XMLs e (opcionalmente) os PDFs DANFE das notas fiscais.
Também há a opção de gerar (ou não) um arquivo ZIP com todos os arquivos.
"""

import os
import time
import base64
import requests
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from threading import Thread

# 🔑 SUA API KEY (substitua pela sua)
API_KEY = "dc8d441e-3189-41d7-b180-6120eb7545f3"

WAIT_SECONDS = 1.2  # tempo de espera entre as requisições


# ======== FUNÇÕES PRINCIPAIS ========

def adicionar_nota(chave):
    url = f"https://api.meudanfe.com.br/v2/fd/add/{chave}"
    headers = {"Api-Key": API_KEY}
    r = requests.put(url, headers=headers, timeout=30)
    try:
        data = r.json()
        return data.get("status", "?")
    except Exception:
        return "ERRO_JSON"


def verificar_status(chave):
    url = f"https://api.meudanfe.com.br/v2/fd/status/{chave}"
    headers = {"Api-Key": API_KEY}
    r = requests.get(url, headers=headers, timeout=30)
    try:
        data = r.json()
        return data.get("status", "?")
    except Exception:
        return "ERRO_JSON"


def baixar_xml(chave):
    url = f"https://api.meudanfe.com.br/v2/fd/get/xml/{chave}"
    headers = {"Api-Key": API_KEY}
    r = requests.get(url, headers=headers, timeout=30)
    try:
        data = r.json()
        return data.get("data")
    except Exception:
        return None


def baixar_pdf(chave):
    """Baixa o DANFE (PDF) corretamente usando o endpoint /get/da/"""
    url = f"https://api.meudanfe.com.br/v2/fd/get/da/{chave}"  # ✅ endpoint correto
    headers = {"Api-Key": API_KEY}
    r = requests.get(url, headers=headers, timeout=30)
    try:
        data = r.json()
        if "data" in data and data["data"]:
            return base64.b64decode(data["data"])
        return None
    except Exception as e:
        print(f"Erro ao processar PDF da chave {chave}: {e}")
        return None


def processar_chaves(chaves, pasta_saida, baixar_pdf_flag, gerar_zip_flag, log_func):
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(exist_ok=True)

    # limpar XMLs e PDFs antigos
    for f in pasta_saida.glob("*.xml"):
        f.unlink()
    for f in pasta_saida.glob("*.pdf"):
        f.unlink()

    total = len(chaves)
    log_func(f"🔹 {total} chaves encontradas. Iniciando download...\n")

    for idx, chave in enumerate(chaves, start=1):
        log_func(f"({idx}/{total}) 🔹 Processando chave: {chave}")
        time.sleep(WAIT_SECONDS)

        status_add = adicionar_nota(chave)
        log_func(f"   ➕ Adicionada: {status_add}")
        time.sleep(WAIT_SECONDS)

        tentativas = 0
        status = status_add
        while status not in ["OK"] and tentativas < 10:
            tentativas += 1
            log_func(f"   ⏳ Aguardando (status={status})... tentativa {tentativas}")
            time.sleep(3)
            status = verificar_status(chave)

        if status != "OK":
            log_func(f"   ⚠️  Não disponível ainda (status final: {status})")
            continue

        xml = baixar_xml(chave)
        if xml:
            xml_path = pasta_saida / f"{chave}.xml"
            with open(xml_path, "w", encoding="utf-8") as fxml:
                fxml.write(xml)
            log_func(f"   ✅ XML salvo: {xml_path.name}")
        else:
            log_func(f"   ⚠️  Falha ao baixar XML.")

        # PDF opcional
        if baixar_pdf_flag:
            pdf_data = baixar_pdf(chave)
            if pdf_data:
                pdf_path = pasta_saida / f"{chave}.pdf"
                with open(pdf_path, "wb") as fpdf:
                    fpdf.write(pdf_data)
                log_func(f"   🧾 PDF salvo: {pdf_path.name}")
            else:
                log_func(f"   ⚠️  Falha ao baixar PDF.")

    # ZIP opcional
    if gerar_zip_flag:
        zip_name = pasta_saida / "xmls_meudanfe.zip"
        log_func(f"\n🗜️ Gerando arquivo ZIP...")
        with zipfile.ZipFile(zip_name, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in pasta_saida.glob("*.*"):
                # ❌ Evita incluir o próprio arquivo zip
                if f.name != zip_name.name:
                    zf.write(f, arcname=f.name)
        log_func(f"✅ Arquivo compactado salvo em: {zip_name}")
    else:
        log_func("\n📂 Arquivos salvos individualmente (sem ZIP).")


# ======== INTERFACE GRÁFICA ========

class MeuDanfeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("💼 MeuDanfe Downloader")
        self.geometry("640x560")
        self.resizable(False, False)

        ttk.Label(self, text="Cole aqui as chaves (uma por linha):").pack(pady=5)
        self.text_chaves = tk.Text(self, height=10, width=75)
        self.text_chaves.pack(padx=10, pady=5)

        frame_opts = ttk.Frame(self)
        frame_opts.pack(pady=10)
        ttk.Button(frame_opts, text="📁 Escolher Pasta de Saída", command=self.escolher_pasta).grid(row=0, column=0, padx=5)
        self.lbl_pasta = ttk.Label(frame_opts, text=os.getcwd(), width=50)
        self.lbl_pasta.grid(row=0, column=1)

        self.var_pdf = tk.BooleanVar(value=True)
        chk_pdf = ttk.Checkbutton(self, text="🧾 Baixar também o PDF (DANFE)", variable=self.var_pdf)
        chk_pdf.pack(pady=5)

        self.var_zip = tk.BooleanVar(value=True)
        chk_zip = ttk.Checkbutton(self, text="🗜️ Gerar arquivo ZIP ao final", variable=self.var_zip)
        chk_zip.pack(pady=5)

        ttk.Button(self, text="🚀 Iniciar Download", command=self.iniciar_download).pack(pady=10)

        ttk.Label(self, text="Log de execução:").pack(pady=5)
        self.txt_log = tk.Text(self, height=15, width=75, state="disabled")
        self.txt_log.pack(padx=10, pady=5)

    def escolher_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.lbl_pasta.config(text=pasta)

    def log(self, msg):
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")
        self.update()

    def iniciar_download(self):
        chaves_raw = self.text_chaves.get("1.0", "end").strip().splitlines()
        chaves = [c.strip() for c in chaves_raw if c.strip().isdigit() and len(c.strip()) == 44]

        if not chaves:
            messagebox.showwarning("Atenção", "Nenhuma chave válida foi informada!")
            return

        pasta_saida = self.lbl_pasta.cget("text")
        baixar_pdf_flag = bool(self.var_pdf.get())
        gerar_zip_flag = bool(self.var_zip.get())

        self.log(f"📄 Baixar PDF: {baixar_pdf_flag}")
        self.log(f"🗜️ Gerar ZIP: {gerar_zip_flag}\n")

        Thread(target=self.executar_download, args=(chaves, pasta_saida, baixar_pdf_flag, gerar_zip_flag), daemon=True).start()

    def executar_download(self, chaves, pasta, baixar_pdf_flag, gerar_zip_flag):
        self.log("🧹 Limpando pasta e iniciando processo...\n")
        try:
            processar_chaves(chaves, pasta, baixar_pdf_flag, gerar_zip_flag, self.log)
            self.log("\n✅ Processo finalizado com sucesso!")
            messagebox.showinfo("Concluído", "Todos os arquivos foram processados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")


if __name__ == "__main__":
    app = MeuDanfeGUI()
    app.mainloop()
