import customtkinter as ctk
import sqlite3

def salvar_fii():
    ticker = entry.get().upper().strip()
    if ticker:
        conn = sqlite3.connect("investimentos.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS carteira (id INTEGER PRIMARY KEY, ticker TEXT UNIQUE)")
        try:
            cursor.execute("INSERT INTO carteira (ticker) VALUES (?)", (ticker,))
            conn.commit()
            label_status.configure(text=f"✅ {ticker} ADICIONADO", text_color="#2ecc71")
            entry.delete(0, 'end')
        except:
            label_status.configure(text="⚠️ ATIVO JÁ EXISTE", text_color="#f1c40f")
        conn.close()

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("Sentinel - Cadastro")
app.geometry("400x350")

ctk.CTkLabel(app, text="SENTINEL INTELLIGENCE", font=("Consolas", 20, "bold")).pack(pady=30)
entry = ctk.CTkEntry(app, placeholder_text="TICKER (EX: MXRF11)", width=250, height=40, justify="center")
entry.pack(pady=10)
ctk.CTkButton(app, text="REGISTRAR ATIVO", command=salvar_fii, fg_color="#2980b9", hover_color="#3498db", height=45).pack(pady=20)
label_status = ctk.CTkLabel(app, text="Aguardando comando...", font=("Consolas", 12))
label_status.pack()

app.mainloop()