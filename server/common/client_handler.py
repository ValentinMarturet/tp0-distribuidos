import socket

from common import utils
from common.protocol_uitls import OperationCode, SimpleProtocol
from common.utils import Bet

AGENCY = 0
NAME = 1
LAST_NAME = 2
DOCUMENT = 3
BIRTHDATE = 4
NUMBER = 5

FIELDS_NUM = 6

class ClientHandler:
    """
    handles a client connection
    closes the connection when done
    """
    @staticmethod
    def handle_client(sock: socket.socket, logging):
        try:
            # lee el mensaje desde el socket
            op, message = SimpleProtocol.deserialize_from_socket(sock)
            addr = sock.getpeername()

            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | op: {op}')

            # opera de acuerdo al tipo de operacion
            if op == OperationCode.APUESTA:
                raw_bets = ClientHandler.format_message(op, message)
                store_bets_from_list(raw_bets, logging)

                logging.info(f'action: receive_message | result: success | ip: {addr[0]} | op: {op}')
                # envia la respuesta
                SimpleProtocol.serialize_to_socket(sock, OperationCode.CONFIRMACION, "Apuestas recibidas")

            elif op == OperationCode.ERROR:
                logging.error(f'action: receive_message | result: error | ip: {addr[0]} | op: {op} | message: {message}')

            else: 
                raise ValueError("Unexpected Operation Code")
            
        except Exception as e:
            logging.error(f'action: receive_message | result: fail | error: {e}')
        finally:
            sock.close()

    @staticmethod
    def format_message(op: OperationCode, message: str) -> str:
        raw_bets = []
        bets = message.split(';')
        for bet in bets:
            raw_bet = []
            fields = bet.split(',')
            if len(fields) == FIELDS_NUM:
                for i in range(FIELDS_NUM):
                    raw_bet.append(fields[i])
            raw_bets.append(raw_bet)
        return raw_bets


def store_bets_from_list(bets: list[list[str]], logging):

    bets_to_load = []
    for bet in bets:
        new_bet = Bet(
            bet[AGENCY],
            bet[NAME],
            bet[LAST_NAME],
            bet[DOCUMENT],
            bet[BIRTHDATE],
            bet[NUMBER]
        )
        bets_to_load.append(new_bet)
    utils.store_bets(bets_to_load)

    for bet in bets_to_load:
        logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}")

