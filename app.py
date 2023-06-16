from flask import Flask, request, jsonify
import pandas as pd
import sqlite3

app = Flask(__name__)


def create_temp_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temp_table (
            Code INTEGER,  
            TISS_TP INTEGER,
            Ds_Prod TEXT
        )
    """)
    conn.commit()


def insert_data_into_temp_table(conn, df):
    df.to_sql("temp_table", conn, if_exists="replace", index=False)


@app.route('/upload', methods=['POST'])
def upload_csv():
    file = request.files['file']
    df = pd.read_csv(file)

    conn = sqlite3.connect(":memory:")

    create_temp_table(conn)

    insert_data_into_temp_table(conn, df)

    return 'Arquivo CSV recebido e armazenado com sucesso.'


@app.route('/consulta', methods=['GET'])
def consultar_temp_table():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temp_table")
    rows = cursor.fetchall()

    results = []
    for row in rows:
        result = {
            'Code': row[0],
            'TISS_TP': row[1],
            'Ds_Prod': row[2]
        }
        results.append(result)

    return jsonify(results)


if __name__ == '__main__':
    app.run()
