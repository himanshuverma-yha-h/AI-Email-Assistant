import sqlite3


def get_connection():

    connection = sqlite3.connect("data/emails.db")

    return connection