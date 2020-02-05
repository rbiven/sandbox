# from configparser import ConfigParser
#
# import pandas as pd
#
# from persistence.connection import ConnectionResource, MySqlDatabaseConnection, create_mysql_connection
#
#
# class Persistence(ConnectionResource):
#     configuration: ConfigParser = None
#
#     def __init__(self):
#         self.__connection_provider: MySqlDatabaseConnection = create_mysql_connection(self.configuration)
#
#     @property
#     def connection(self):
#         return self.__connection_provider.connection
#
#     def connect(self) -> bool:
#         return self.__connection_provider.connect()
#
#     def disconnect(self) -> None:
#         self.__connection_provider.disconnect()
#
#     def get_test_connection(self):
#         query = """SELECT *
#                    FROM users
#                    LIMIT 5"""
#
#         df = pd.read_sql_query(query, self.connection)
#
#         return df


def some_function(string_parameter):
    return string_parameter
