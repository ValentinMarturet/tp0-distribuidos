import struct
import socket
from enum import IntEnum
from typing import Tuple

class OperationCode(IntEnum):
    """Enum para códigos de operación"""
    APUESTA = 1
    CONFIRMACION = 2
    ERROR = 3
    BATCH = 4

class SerializationError(Exception):
    """Excepción para errores de serialización"""
    pass

class SimpleProtocol:
    """
    Protocolo simple de serialización:
    - 1 byte: código de operación (enum)
    - 4 bytes: longitud del mensaje (int, big endian)
    - N bytes: mensaje (string en UTF-8)
    """
    
    HEADER_SIZE = 5
    MAX_MESSAGE_SIZE = 2**32 - 1
    

    @staticmethod
    def _send_all(sock: socket.socket, data: bytes) -> None:
        """
        Envía todos los datos al socket, manejando short writes.
        
        Args:
            sock: Socket para enviar los datos
            data: Datos a enviar
            
        Raises:
            SerializationError: Si hay error en el envío
        """
        total_sent = 0
        data_length = len(data)
        
        while total_sent < data_length:
            try:
                sent = sock.send(data[total_sent:])
                if sent == 0:
                    raise SerializationError("Conexión cerrada por el peer durante envío")
                total_sent += sent
            except socket.error as e:
                raise SerializationError(f"Error al enviar datos al socket: {e}")


    @staticmethod
    def serialize_to_socket(sock: socket.socket, op_code: OperationCode, message: str) -> None:
        """
        Serializa los datos según el protocolo.
        
        Args:
            op_code: Código de operación del enum
            message: Mensaje string a serializar
            
        Returns:
            bytes: Datos serializados
            
        Raises:
            SerializationError: Si hay error en la serialización
        """
        try:
            message_bytes = message.encode('utf-8')
            message_length = len(message_bytes)
            
            if message_length > SimpleProtocol.MAX_MESSAGE_SIZE:
                raise SerializationError(f"Mensaje demasiado largo: {message_length} bytes")
            
            header = struct.pack('>BI', int(op_code), message_length)
            
            complete_message = header + message_bytes
            SimpleProtocol._send_all(sock, complete_message)
            
        except (UnicodeEncodeError, struct.error) as e:
            raise SerializationError(f"Error al serializar: {e}")
    
    @staticmethod
    def _read_exact(fd: socket.socket, num_bytes: int) -> bytes:
        """
        Lee exactamente num_bytes del file descriptor, manejando short reads.
        
        Args:
            fd: Socket o file descriptor para leer
            num_bytes: Número exacto de bytes a leer
            
        Returns:
            bytes: Datos leídos
            
        Raises:
            SerializationError: Si no se pueden leer todos los bytes
        """
        data = b''
        while len(data) < num_bytes:
            try:
                chunk = fd.recv(num_bytes - len(data))
                
                if not chunk:
                    raise SerializationError(f"Conexión cerrada o EOF: solo se leyeron {len(data)}/{num_bytes} bytes")
                
                data += chunk
                
            except socket.error as e:
                raise SerializationError(f"Error al leer desde socket: {e}")
            except IOError as e:
                raise SerializationError(f"Error al leer desde file descriptor: {e}")
        
        return data
    
    @staticmethod
    def deserialize_from_socket(fd: socket.socket) -> Tuple[OperationCode, str]:
        """
        Deserializa datos leyendo directamente desde un socket.
        Args:
            fd: Socket para leer

        Returns:
            Tuple[OperationCode, str]: Código de operación y mensaje
            
        Raises:
            SerializationError: Si hay error en la lectura o deserialización
        """
        try:
            # Leer header (5 bytes)
            header = SimpleProtocol._read_exact(fd, SimpleProtocol.HEADER_SIZE)
            
            # Extraer información del header
            op_code_raw, message_length = struct.unpack('>BI', header)
            
            # Convertir código de operación a enum
            try:
                op_code = OperationCode(op_code_raw)
            except ValueError:
                raise SerializationError(f"Código de operación inválido: {op_code_raw}")
            
            # Leer el mensaje si tiene contenido
            if message_length == 0:
                return op_code, ""
            
            # Verificar tamaño razonable
            if message_length > SimpleProtocol.MAX_MESSAGE_SIZE:
                raise SerializationError(f"Mensaje demasiado largo: {message_length} bytes")
            
            # Leer mensaje completo
            message_bytes = SimpleProtocol._read_exact(fd, message_length)
            message = message_bytes.decode('utf-8')
            
            return op_code, message
            
        except (struct.error, UnicodeDecodeError) as e:
            raise SerializationError(f"Error al deserializar: {e}")
    