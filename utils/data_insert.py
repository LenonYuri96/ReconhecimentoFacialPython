import tkinter as tk
from tkinter import messagebox, simpledialog
from utils.my_connection import mysql_get_mydb
from mysql.connector import Error


def cadastro(nome, sobrenome, email):
    """
    Insere um novo usuário no banco de dados e retorna o ID do usuário.
    Retorna None em caso de falha.
    """
    connection = None
    cursor = None
    try:
        connection = mysql_get_mydb()
        if connection is None or not connection.is_connected():
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")
            return None

        cursor = connection.cursor()
        query = "INSERT INTO pessoas (nome, sobrenome, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (nome, sobrenome, email))
        connection.commit()
        user_id = cursor.lastrowid

        # Verifica se a inserção foi bem-sucedida
        if user_id is None:
            messagebox.showerror("Erro", "Falha ao cadastrar usuário.")
            return None

        print(f"Usuário cadastrado com ID: {user_id}")
        return user_id

    except Error as e:
        error_msg = f"Erro ao cadastrar usuário: {e}"
        print(error_msg)
        messagebox.showerror("Erro no Banco de Dados", error_msg)
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def fetch_users(user_id=None):
    """
    Obtém a lista de usuários do banco de dados.
    Se user_id for fornecido, retorna apenas o usuário correspondente.
    Retorna lista vazia em caso de falha ou nenhum resultado.
    """
    connection = None
    cursor = None
    try:
        connection = mysql_get_mydb()
        if connection is None or not connection.is_connected():
            print("Aviso: Conexão com o banco de dados falhou")
            return []

        cursor = connection.cursor()  # Remove dictionary=True to return tuples

        if user_id:
            query = "SELECT id, nome, sobrenome FROM pessoas WHERE id = %s"
            cursor.execute(query, (user_id,))
        else:
            query = "SELECT id, nome, sobrenome FROM pessoas"
            cursor.execute(query)

        result = cursor.fetchall()
        return result if result else []

    except Error as e:
        print(f"Erro ao buscar usuários: {e}")
        return []
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
