from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import pandas as pd
import psycopg2
from sqlalchemy import create_engine,Table, Column, Integer, String, MetaData

def create_app():
    app = Flask(__name__)
    # configuraciones de la aplicación aquí
    return app

# create the engine to connect to your database
engine = create_engine('postgresql://nube:Nube.123@192.168.44.73:5432/costos_nube')

metadata = MetaData()

app = create_app()
'''
# Configuración de la base de datos local
conn = psycopg2.connect(
    host="postgres",
    port="5432",
    database="postgres",
    user="postgres",
    password="password"
)
'''
# Configuración de la base de datos datatools
conn = psycopg2.connect(
    host="192.168.44.73",
    port="5432",
    database="costos_nube",
    user="nube",
    password="Nube.123"
)

cursor = conn.cursor()

cursor.execute("SELECT nombre FROM proveedor ORDER BY id ASC ")
for proveedor in cursor.fetchall(): 
    result = proveedor[0:]

# Página principal
@app.route('/')
def index():
    query = "select nombre from proveedor"
    cursor.execute(query)
    proveedor = cursor.fetchall()
    return render_template('index.html', proveedor = proveedor)

# Carga de archivos
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_ext = filename.split('.')[-1]

    if file_ext == 'csv':
        df = pd.read_csv(file,encoding='latin-1')
    elif file_ext == 'xlsx':
        df = pd.read_excel(file)

    # Guardar el archivo en la base de datos
    prueba= 'prueba'
    sql = df.to_sql(name = prueba, con = engine, schema='public', if_exists='append', index=False)
    print(sql)

    return 'Archivo cargado con éxito!'

# Consulta de datos
@app.route('/query', methods=['POST'])
def query():
    query = request.form['query']
    print(query)
    cursor.execute(query)
    results = cursor.fetchall()
    print(results)
    headers = [desc[0] for desc in cursor.description]
    print(headers)
    return render_template('index.html', headers=headers, results=results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
