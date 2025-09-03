import socket
import logging
import signal

from server.common.client_handler import ClientHandler


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self._running = True

        self._setup_signal_handlers()

    
    def _setup_signal_handlers(self):
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    
    def _signal_handler(self, signum, frame):
        signal_name = signal.Signals(signum).name
        logging.info(f'action: shutdown_signal | result: in_progress | signal: {signal_name}')
        self._shutdown()

    def _shutdown(self):
        logging.info('action: graceful_shutdown | result: in_progress')
        self._running = False

        if self._server_socket:
            try:
                self._server_socket.close()
                logging.info('action: close_server_socket | result: success')
            except Exception as e:
                logging.error(f'action: close_server_socket | result: fail | error: {e}')

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        while self._running:
            try:

                client_sock = self.__accept_new_connection()
                self.__handle_client_connection(client_sock)
            except OSError as e:
                if not self._running:
                    # logging.info('action: server_loop | result: shutdown_requested')
                    break
                else:
                    logging.error(f'action: accept_connection | result: fail | error: {e}')
        self._cleanup()

    def _cleanup(self):
        logging.info('action: server_cleanup | result: in_progress')
        if self._server_socket:
            self._server_socket.close()
            logging.info('action: exit | result: success')

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        ClientHandler.handle_client(client_sock, logging)

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
