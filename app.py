from flask import Flask, request, render_template, redirect
import pandas as pd
import sqlite3
import os 

app = Flask(__name__)

db_path = os.path.join(app.root_path, 'data.db')
def create_temp_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temp_table (
            code INTEGER,  
            TISS_TP INTEGER,
            Ds_Prod TEXT
        )
    """)
    conn.commit()

def insert_data_into_temp_table(conn, df):
    df.to_sql("temp_table", conn, if_exists="replace", index=False)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username == "admin" and password == "senha":
        return redirect("/upload")
    else:
        return redirect("/")

@app.route('/<string:nome>')
def error(nome):
    variavel = f'ERROR 404: Página {nome} não existe'
    return render_template("error.html", variavel=variavel)

import pandas as pd

@app.route('/upload', methods=['POST', 'GET'])
def upload_xlsx():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "Nenhum arquivo enviado."

        file = request.files['file']

        if file.filename == '':
            return "Nome de arquivo vazio."

        try:
            df = pd.read_excel(file)
            conn = sqlite3.connect("data.db")
            create_temp_table(conn)
            insert_data_into_temp_table(conn, df)

            return redirect('/dados')
        except Exception as e:
            return f"Erro ao ler o arquivo XLSX: {str(e)}"
    else:
        return render_template("upload.html")

@app.route('/dados')
def dados():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temp_table")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    return render_template("dados.html", rows=rows, column_names=column_names)

if __name__ == '__main__':
    app.run(debug=True)
