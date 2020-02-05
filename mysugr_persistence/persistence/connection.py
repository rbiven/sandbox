import logging
from abc import ABC
from configparser import ConfigParser
from errno import errorcode

import mysql.connector
from sshtunnel import SSHTunnelForwarder


class ConnectionResource(object):
    """
    A wrapper around connection behavior.  Implemented to work 'with' syntactic sugar for
    verifying and forcing that a connection is implemented.
    """

    def __enter__(self):
        if not self.connect():
            self.__exit__()
        return self

    def __exit__(self, *args):
        self.disconnect()

    def connect(self) -> bool:
        raise NotImplementedError()

    def disconnect(self) -> None:
        raise NotImplementedError()


class ConnectionProvider(ConnectionResource, ABC):
    """
    Configurable connection resource with points to host and port.

    Ref: ConnectionResource
    """

    @property
    def host(self) -> str:
        raise NotImplementedError()

    @property
    def port(self) -> int:
        raise NotImplementedError()


class DatabaseSSHTunnel(ConnectionProvider):
    def __init__(self, configuration: ConfigParser):
        self.__configuration = configuration
        self.__ssh_server = None

    @property
    def host(self) -> str:
        return self.__ssh_server.local_bind_host

    @property
    def port(self) -> int:
        return self.__ssh_server.local_bind_port

    def connect(self) -> bool:
        logging.info("Opening SSH connection to database...")

        self.__ssh_server = SSHTunnelForwarder(
            ssh_address_or_host=(self.__configuration["ssh_host"], 22),
            remote_bind_address=(
                self.__configuration["db_host"], self.__configuration.getint("db_port")),
            ssh_username=self.__configuration["ssh_user"]
        )
        logging.getLogger("paramiko").setLevel(logging.INFO)

        self.__ssh_server.start()
        logging.info('Established VPN tunnel to {}'.format(self.__ssh_server.ssh_host))
        return True

    def disconnect(self) -> None:
        self.__ssh_server.stop()
        logging.info("Closed SSH tunnel..")


class MySqlDatabaseConnection(ConnectionProvider):
    def __init__(self, configuration: ConfigParser, proxy_connection: ConnectionProvider = None):
        self.__configuration: ConfigParser = configuration
        self.__proxy_connection: ConnectionProvider = proxy_connection

        self.connection = None

    @property
    def host(self) -> str:
        if self.__proxy_connection:
            return self.__proxy_connection.host

        return self.__configuration["db_host"]

    @property
    def port(self) -> int:
        if self.__proxy_connection:
            return self.__proxy_connection.port

        return self.__configuration["db_port"]

    def connect(self) -> bool:
        logging.info("Opening connection to database...")

        if self.__proxy_connection:
            self.__proxy_connection.connect()

        try:
            logging.info("start connecting to db")
            cnx = mysql.connector.connect(host=self.host,
                                          port=self.port,
                                          database=self.__configuration["db_schema"],
                                          user=self.__configuration["db_user"],
                                          password=self.__configuration["db_password"])
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.error("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.error("Database does not exist")
            else:
                logging.error(err)
            return False
        else:
            logging.info("Established database connection..")
            self.connection = cnx
            self.connection.autocommit = True
            return True

    def disconnect(self) -> None:
        self.connection.close()
        logging.info("Closed database connection..")

        if self.__proxy_connection:
            self.__proxy_connection.disconnect()


def create_mysql_connection(configuration: ConfigParser) -> MySqlDatabaseConnection:
    """
    Determine if connection will be ssh (local) or direct (aws cluster)
    """
    ssh_required = configuration.getboolean('ssh')
    proxy_connection = DatabaseSSHTunnel(configuration) if ssh_required else None
    mysql_connection = MySqlDatabaseConnection(configuration, proxy_connection)

    return mysql_connection
