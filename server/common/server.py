import socket
import logging
import signal
import threading
from time import time

from common.client_handler import ClientHandler
from common.lottery import Lottery
from common.protocol_uitls import OperationCode, SimpleProtocol


MAX_THREADS = 10
SHUTDOWN_WAIT_TIME = 30  

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self._lottery = Lottery()

        self._running = True
        self._active_threads = []
        self._thread_lock = threading.Lock()

        self._lottery_lock = threading.Lock()

        self._bets_lock = threading.Lock()


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

    def _cleanup_finished_threads(self):
        """Limpia los hilos que ya terminaron"""
        with self._thread_lock:
            self._active_threads = [t for t in self._active_threads if t.is_alive()]

    def _get_active_thread_count(self):
        """Retorna el número de hilos activos"""
        with self._thread_lock:
            return len([t for t in self._active_threads if t.is_alive()])
        

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
                self._cleanup_finished_threads()
                
                client_sock = self.__accept_new_connection()
                if not self._running:
                    client_sock.close()
                    break

                current_thread_count = self._get_active_thread_count()
                if current_thread_count >= MAX_THREADS:
                    self._send_max_threads_reached(client_sock)
                    logging.warning('action: rechazo_conexion | result: success | reason: max_threads_reached')
                    continue

                client_thread = threading.Thread(target=self.__handle_client_connection, args=(client_sock,), daemon=True)

                with self._thread_lock:
                    self._active_threads.append(client_thread)
                
                client_thread.start()

            except OSError as e:
                if not self._running:
                    logging.info('action: server_shutdown | result: success')
                    break
                else:
                    logging.error(f'action: accept_connection | result: fail | error: {e}')
        self._cleanup()

    """
    send a message to client indicating that max threads has been reached
    closes the client socket after sending the message
    """
    def _send_max_threads_reached(self, client_sock):
        try:
            SimpleProtocol.serialize_to_socket(client_sock, OperationCode.ERROR, "Max threads reached. Try again later.")
            logging.warning('action: rechazo_conexion | result: success | reason: max_threads_reached')
        except Exception as e:
            logging.error(f'action: rechazo_conexion | result: fail | error: {e}')
        finally:
            client_sock.close()


    def _cleanup(self):
        logging.info('action: server_cleanup | result: in_progress')

        logging.info('action: waiting_for_threads | result: in_progress')

        with self._thread_lock:
            active_threads = [t for t in self._active_threads if t.is_alive()]

        start_time = time.time()

        while active_threads and (time.time() - start_time) < SHUTDOWN_WAIT_TIME:
            for t in active_threads:
                t.join(timeout=1)
            if not t.is_alive():
                active_threads.remove(t)
                logging.info(f'action: thread_cleanup | result: success | thread_id: {t.ident}')

        if active_threads:
            logging.warning(f'action: thread_cleanup | result: timeout | remaining_threads: {len(active_threads)}')
        

        if self._server_socket:
            try:
                self._server_socket.close()
            except:
                pass

        logging.info('action: exit | result: success')

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            ClientHandler.handle_client(client_sock, logging, self._lottery, self._lottery_lock, self._bets_lock)
            with self._lottery_lock:
                if self._lottery.all_agencies_ready() and not self._lottery.draw_done(): 
                    self._lottery.make_draw()
                    logging.info('action: sorteo | result: success')
        
        except Exception as e:
            logging.error(f'action: handle_client | result: fail | error: {e}')
        finally:
            client_sock.close()

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
