import socket

from common import utils
from common.protocol_uitls import OperationCode, SimpleProtocol
from common.utils import Bet
from common.lottery import Lottery

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
    def handle_client(sock: socket.socket, logging, lottery: Lottery):
        try:
            # lee el mensaje desde el socket
            while True: 
                op, message = SimpleProtocol.deserialize_from_socket(sock)
                addr = sock.getpeername()

                # logging.info(f'action: receive_message | result: success | ip: {addr[0]} | op: {op}')

                # opera de acuerdo al tipo de operacion
                if op == OperationCode.APUESTA: #codigo de operacion deprecado, utilizado en la parte 5
                    handle_bets(op, message, logging, sock)

                elif op == OperationCode.BATCH:
                    handle_bets(op, message, logging, sock)
                    continue

                elif op == OperationCode.ERROR:
                    logging.error(f'action: receive_message | result: error | ip: {addr[0]} | op: {op} | message: {message}')
                
                elif op == OperationCode.READY:
                    agency_id = int(message)
                    lottery.mark_agency_ready(agency_id)
                    logging.info(f'action: agencia_lista | result: success | ip: {addr[0]} | agency_id: {agency_id}')
                
                elif op == OperationCode.WINNERS:
                    agency_id = int(message)
                    if lottery.draw_done():
                        winners = lottery.get_winners_for_agency(agency_id)
                        SimpleProtocol.serialize_to_socket(sock, OperationCode.WINNERS, winners)
                        logging.info(f'action: enviar_ganadores | result: success | agency_id: {agency_id}')
                    else:
                        lottery.mark_agency_ready(agency_id) #se vuelve a marcar como lista por si no lo estaba
                        SimpleProtocol.serialize_to_socket(sock, OperationCode.NOT_READY, "Sorteo no realizado")

                else:
                    raise ValueError("Unexpected Operation Code")
                break
            
        except Exception as e:
            try:
                SimpleProtocol.serialize_to_socket(sock, OperationCode.ERROR, str(e))
            except Exception as e:
                logging.error(f'action: send_response | result: fail | error: {e}')
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
    try:
        utils.store_bets(bets_to_load)
        logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(bets_to_load)}')
        return None
    except Exception as e:
        logging.error(f'action: apuesta_recibida | result: fail | cantidad: {len(bets_to_load)}')
        return e


def handle_bets(op: OperationCode, message: str, logging, sock: socket.socket):
    raw_bets = ClientHandler.format_message(op, message)
    err = store_bets_from_list(raw_bets, logging)

    addr = sock.getpeername()

    logging.info(f'action: receive_message | result: success | ip: {addr[0]} | op: {op}')
    # envia la respuesta
    if err is None:
        SimpleProtocol.serialize_to_socket(sock, OperationCode.CONFIRMACION, "Apuestas recibidas")
    else:
        SimpleProtocol.serialize_to_socket(sock, OperationCode.ERROR, str(err))