from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import datetime
import json
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, MetaData

def create_app():
    app = Flask(__name__)
    # configuraciones de la aplicación aquí
    #app.config['SECRET_KEY'] = 'qwertyuiopasdfghjklñ123*'
    return app

# create the engine to connect to your database
#engine = create_engine('postgresql://nube:Nube.123@192.168.44.73:5432/costos_nube')
engine = create_engine('postgresql://postgres:password@postgres:5432/postgres')
metadata = MetaData()

app = create_app()

# Configuración de la base de datos datatools
conn = psycopg2.connect(
    host="192.168.44.73",
    port="5432",
    database="costos_nube",
    user="nube",
    password="Nube.123"
)

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
cursor = conn.cursor()

# Obtener proveedores y productos desde la base de datos
cursor.execute(f"SELECT nombre as proveedor FROM public.proveedor")
proveedores = cursor.fetchall()

# Página principal
@app.route('/')
def index():
    return render_template('index.html', proveedor=proveedores)


#Lista de Opciones Dependientes de Proveedor
@app.route('/opciones_dependientes/<proveedor>')
def opciones_dependientes(proveedor):
    if proveedor == "Azure":
        # obtener proveedores y productos desde la base de datos
        cursor.execute(
            """
            SELECT CONCAT('N.Dir= ', gn.nombre_directorio_azure, ' / N.Sus= ', s.nombre_suscripcion, ' / N.Ctaws= ', gn.cuenta_aws, ' / N.Proy= ', gn.nombre_proyecto, ' / N.Amb= ', gn.ambiente) AS info_grupo_nube
            FROM grupo_nube gn
            JOIN suscripcion s ON s.id = gn.suscripcion 
            WHERE gn.proveedor_id =1    
            ORDER BY gn.id ASC
            """
        )
        info_grupo_nube = cursor.fetchall()
        return render_template('opciones_dependientes.html', grupo_nube=info_grupo_nube)  
    elif proveedor == "AWS":
        # obtener proveedores y productos desde la base de datos
        cursor.execute(
            """
            SELECT CONCAT('N.Dir= ', gn.nombre_directorio_azure, ' / N.Sus= ', s.nombre_suscripcion, ' / N.Ctaws= ', gn.cuenta_aws, ' / N.Proy= ', gn.nombre_proyecto, ' / N.Amb= ', gn.ambiente) AS info_grupo_nube
            FROM grupo_nube gn
            JOIN suscripcion s ON s.id = gn.suscripcion 
            WHERE gn.proveedor_id =2    
            ORDER BY gn.id ASC
            """
        )
        info_grupo_nube = cursor.fetchall()
        return render_template('opciones_dependientes.html', grupo_nube=info_grupo_nube)         
    else:
        cursor.execute(
            """
            SELECT CONCAT('N.Dir= ', gn.nombre_directorio_azure, ' / N.Sus= ', s.nombre_suscripcion, ' / N.Ctaws= ', gn.cuenta_aws, ' / N.Proy= ', gn.nombre_proyecto, ' / N.Amb= ', gn.ambiente) AS info_grupo_nube
            FROM grupo_nube gn
            JOIN suscripcion s ON s.id = gn.suscripcion
            ORDER BY gn.id ASC
            """
        )
        info_grupo_nube = cursor.fetchall()
        return render_template('opciones_dependientes.html', grupo_nube=info_grupo_nube)        
        '''
        for grupo_nube in info_grupo_nube:
            cursor.execute(
                """
                SELECT
                    CONCAT('N.Dir= ', gn.nombre_directorio_azure, ' / N.Sus= ', s.nombre_suscripcion, ' / N.Ctaws= ', gn.cuenta_aws, ' / N.Proy= ', gn.nombre_proyecto, ' / N.Amb= ', gn.ambiente) AS info_grupo_nube
                FROM
                    grupo_nube gn
                    JOIN suscripcion s ON s.id = gn.suscripcion
                WHERE s.nombre_suscripcion = %(nombre_suscripcion)s
                ORDER BY
                    gn.id ASC
            """,
            {"nombre_suscripcion": grupo_nube[0]}
            )'''
   
#Obtención valores lista proveedor
@app.route('/manejar_seleccion_proveedor', methods=['POST'])
def manejar_seleccion_proveedor():
    proveedor = request.form.get('proveedor')
    # hacer algo con los valores seleccionados
    return 'str(proveedor)'

#Obtención valores listas desplegables
grupo_nube_str = '1'  # valor predeterminado
@app.route('/manejar_seleccion_grupo_nube', methods=['POST'])
def manejar_seleccion_grupo_nube():
    if request.method == "POST":
        opcion_seleccionada = request.form.get('opcioSeleccionada')
        if opcion_seleccionada is None or opcion_seleccionada == "":
            return f"No se encontró la clave en la solicitud: {opcion_seleccionada}", 400
        # Actualizar la variable grupo_nube_str con la opción seleccionada
        global grupo_nube_str
        grupo_nube_str = opcion_seleccionada
    # Devolver una respuesta vacía en caso de éxito
    return '', 204

# Carga de archivos
@app.route('/upload', methods=['POST','GET'])
def upload():
    '''
    response = manejar_seleccion_grupo_nube()
    # Verificar si el formulario contiene el archivo y el valor de la lista desplegable
    if isinstance(response, tuple) and 'file' not in request.files:
       return render_template('error.html', message='Falta cargar el archivo o seleccionar una opción'), 400
    '''
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_ext = filename.split('.')[-1]

    if file_ext == 'csv':
        df = pd.read_csv(file, encoding='latin-1')
        print(df)
    elif file_ext == 'xlsx':
        df = pd.read_excel(file, usecols=('A:S'))

        valores = [col for col in df.columns if col!="Servicio"]

        base_despivoteada = pd.melt(df, id_vars= ["Servicio"], value_vars= valores)

        df = pd.DataFrame(base_despivoteada)

        '''
        if response == False:
            # Manejar el error
            return render_template('error.html', message='Hubo un error al obtener los datos'), 400
        if isinstance(response, tuple) and response[1] != 200:
            # Manejar el error
            return render_template('error.html', message=response[0]), response[1]
    
        grupo_nube_str = response
        '''

        # Reemplazar valores nulos y en blanco con 0
        df = df.fillna(value=0)

        df['Servicio'] = pd.to_datetime(df['Servicio']).dt.strftime('%Y-%m-%d')
        
        df['Currency'] = "USD"

        df['Query'] = "INSERT INTO costos(id,grupo_nube,fecha_costo,nombre_servicio,valor_costo, currency,nombre_dia) VALUES(nextval('public.costos_id_seq'),"
        
    

        # Agregar el diccionario para mapear los días de la semana en español

        dias_espanol = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }

        grupo_nube_str = 16
    

        # Convertir la fecha a día de la semana en español y agregar una columna adicional al dataframe
        df['Nombre Día'] = df['Servicio'].apply(lambda x: dias_espanol[datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%A')])


        with open('inserts.sql', 'w') as f:
            for i in range(len(df)):
                nombre_dia = df.loc[i, "Nombre Día"]
                query = f"INSERT INTO costos(id,grupo_nube,fecha_costo,nombre_servicio,valor_costo,currency,nombre_dia) VALUES (nextval('public.costos_id_seq'), {grupo_nube_str}, '{df.loc[i, 'Servicio']}', '{df.loc[i, 'variable']}', '{df.loc[i, 'value']}', '{df.loc[i, 'Currency']}', '{df.loc[i, 'Nombre Día']}');\n"
                f.write(query)

    return render_template('download.html', message='¡Archivo cargado con éxito!')


@app.route('/download', methods=['GET'])
def download_file():
    file_path = "/data/inserts.sql"
    #cursor.close()
    return send_file(file_path,as_attachment=True, attachment_filename='inserts.sql')



# Consulta de datosx
@app.route('/query', methods=['POST'])
def query():
    query = request.form['query']
    cursor.execute(query)
    results = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]
    return render_template('index.html', headers=headers, results=results)

# POWER BI
@app.route('/powerbi', methods=['GET','POST'])
def powerbi():
    return render_template('reporte.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
