import mysql.connector
from mysql.connector import errorcode


def mysql_get_mydb():
    try:
        # First connect without specifying database to ensure we can create it if needed
        cnx = mysql.connector.connect(user="root", password="", host="localhost")
        print("Conexão com o servidor MySQL estabelecida")

        cursor = cnx.cursor()

        # Create database if it doesn't exist
        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS reconhecimento_facial_senai")
            print("Banco de dados verificado/criado com sucesso")
        except mysql.connector.Error as err:
            print(f"Erro ao criar banco de dados: {err}")
            raise

        # Now connect to the specific database
        cursor.execute("USE reconhecimento_facial_senai")
        cursor.close()

        # Verify the connection is using the correct database
        cursor = cnx.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"Conectado ao banco de dados: {db_name}")
        cursor.close()

        return cnx

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erro: Algo está errado com seu nome de usuário ou senha")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Erro: Banco de dados não existe")
        else:
            print(f"Erro de conexão: {err}")

        # Ensure cursor is closed if connection fails
        if "cursor" in locals() and cursor:
            cursor.close()
        if "cnx" in locals() and cnx.is_connected():
            cnx.close()

        return None
