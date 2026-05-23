import mysql.connector
from mysql.connector import errorcode
from utils.my_connection import mysql_get_mydb


def create_table(cnx):
    """
    Creates the 'pessoas' table if it doesn't exist, with proper error handling.
    Returns True if successful, False otherwise.
    """
    cursor = None
    try:
        cursor = cnx.cursor()

        # 1. Ensure we're using the correct database
        try:
            cursor.execute("USE reconhecimento_facial_senai")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Erro: Banco de dados 'reconhecimento_facial_senai' não existe")
                return False
            raise

        # 2. Create table with explicit column definitions
        table_creation_query = """
        CREATE TABLE IF NOT EXISTS pessoas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            sobrenome VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            UNIQUE KEY unique_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """

        cursor.execute(table_creation_query)
        cnx.commit()

        # 3. Verify table was created
        cursor.execute("SHOW TABLES LIKE 'pessoas'")
        if not cursor.fetchone():
            print("Erro: Tabela 'pessoas' não foi criada")
            return False

        print("Tabela 'pessoas' criada/verificada com sucesso")
        return True

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Tabela 'pessoas' já existe")
            return True
        print(f"Erro ao criar tabela: {err}")
        return False
    finally:
        if cursor:
            cursor.close()


def verify_table_structure(cnx):
    """
    Verifies the table has the correct structure
    Returns True if structure is correct, False otherwise
    """
    cursor = None
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("DESCRIBE pessoas")
        columns = {row["Field"]: row for row in cursor}

        expected_columns = {
            "id": {"Type": "int(11)", "Null": "NO", "Key": "PRI"},
            "nome": {"Type": "varchar(255)", "Null": "NO"},
            "sobrenome": {"Type": "varchar(255)", "Null": "NO"},
            "email": {"Type": "varchar(255)", "Null": "NO"},
        }

        for col, props in expected_columns.items():
            if col not in columns:
                print(f"Erro: Coluna faltando: {col}")
                return False
            for prop, value in props.items():
                if columns[col][prop] != value:
                    print(
                        f"Erro: Coluna {col} propriedade {prop} diferente (esperado: {value}, encontrado: {columns[col][prop]})"
                    )
                    return False

        print("Estrutura da tabela verificada com sucesso")
        return True

    except mysql.connector.Error as err:
        print(f"Erro ao verificar estrutura da tabela: {err}")
        return False
    finally:
        if cursor:
            cursor.close()


if __name__ == "__main__":
    cnx = None
    try:
        cnx = mysql_get_mydb()
        if not cnx or not cnx.is_connected():
            print("Falha na conexão com o banco de dados")
            exit(1)

        if create_table(cnx):
            if not verify_table_structure(cnx):
                print("Problemas encontrados na estrutura da tabela")
                exit(1)
        else:
            print("Falha ao criar tabela")
            exit(1)

        print("Operação concluída com sucesso")

    except Exception as e:
        print(f"Erro inesperado: {e}")
        exit(1)
    finally:
        if cnx and cnx.is_connected():
            cnx.close()
