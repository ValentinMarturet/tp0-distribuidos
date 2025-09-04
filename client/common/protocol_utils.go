package common

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"io"
	"net"
	"time"
)

type OperationCode uint8

const (
	APUESTA      OperationCode = 1
	CONFIRMACION OperationCode = 2
	ERROR        OperationCode = 3
	BATCH        OperationCode = 4
)

func (op OperationCode) String() string {
	switch op {
	case APUESTA:
		return "APUESTA"
	case CONFIRMACION:
		return "CONFIRMACION"
	case ERROR:
		return "ERROR"
	case BATCH:
		return "BATCH"
	default:
		return fmt.Sprintf("UNKNOWN(%d)", uint8(op))
	}
}

// SerializationError representa errores de serialización
type SerializationError struct {
	Msg string
}

func (e *SerializationError) Error() string {
	return e.Msg
}

// SimpleProtocol implementa el protocolo de serialización
type SimpleProtocol struct{}

const (
	HeaderSize      = 5
	MaxMessageSize  = (1 << 32) - 1 // 2^32 - 1
	DefaultTimeout  = 30 * time.Second
)

func (sp *SimpleProtocol) sendAll(conn net.Conn, data []byte) error {
	totalSent := 0
	dataLength := len(data)
	
	for totalSent < dataLength {
		sent, err := conn.Write(data[totalSent:])
		if err != nil {
			return &SerializationError{
				Msg: fmt.Sprintf("Error al enviar datos al socket: %v", err),
			}
		}
		if sent == 0 {
			return &SerializationError{
				Msg: "Conexión cerrada por el peer durante envío",
			}
		}
		totalSent += sent
	}
	
	return nil
}


func (sp *SimpleProtocol) SerializeToSocket(conn net.Conn, opCode OperationCode, message string) error {
	if conn == nil {
		return &SerializationError{Msg: "Conexión no puede ser nil"}
	}
	
	// Convertir mensaje a bytes UTF-8
	messageBytes := []byte(message)
	messageLength := uint32(len(messageBytes))
	
	if messageLength > MaxMessageSize {
		return &SerializationError{
			Msg: fmt.Sprintf("Mensaje demasiado largo: %d bytes", messageLength),
		}
	}
	
	// Crear header: 1 byte para op_code + 4 bytes para length (big endian)
	var header bytes.Buffer
	
	// Escribir código de operación (1 byte)
	if err := binary.Write(&header, binary.BigEndian, uint8(opCode)); err != nil {
		return &SerializationError{
			Msg: fmt.Sprintf("Error al escribir código de operación: %v", err),
		}
	}
	
	// Escribir longitud del mensaje (4 bytes, big endian)
	if err := binary.Write(&header, binary.BigEndian, messageLength); err != nil {
		return &SerializationError{
			Msg: fmt.Sprintf("Error al escribir longitud del mensaje: %v", err),
		}
	}
	
	// Construir mensaje completo
	completeMessage := append(header.Bytes(), messageBytes...)
	
	log.Debugf("Sending message: OpCode=%s, Length=%d, TotalBytes=%d", opCode.String(), messageLength, len(completeMessage))

	// Enviar todo el mensaje
	return sp.sendAll(conn, completeMessage)
}

func (sp *SimpleProtocol) readExact(conn net.Conn, numBytes int) ([]byte, error) {
	buffer := make([]byte, numBytes)
	
	n, err := io.ReadFull(conn, buffer)
	if err != nil {
		if err == io.EOF || err == io.ErrUnexpectedEOF {
			return nil, &SerializationError{
				Msg: fmt.Sprintf("Conexión cerrada o EOF: solo se leyeron %d/%d bytes", n, numBytes),
			}
		}
		return nil, &SerializationError{
			Msg: fmt.Sprintf("Error al leer desde socket: %v", err),
		}
	}
	
	return buffer, nil
}


func (sp *SimpleProtocol) DeserializeFromSocket(conn net.Conn) (OperationCode, string, error) {
	if conn == nil {
		return 0, "", &SerializationError{Msg: "Conexión no puede ser nil"}
	}
	
	// Leer header (5 bytes)
	header, err := sp.readExact(conn, HeaderSize)
	if err != nil {
		return 0, "", err
	}
	
	// Extraer información del header usando binary.BigEndian
	reader := bytes.NewReader(header)
	
	var opCodeRaw uint8
	if err := binary.Read(reader, binary.BigEndian, &opCodeRaw); err != nil {
		return 0, "", &SerializationError{
			Msg: fmt.Sprintf("Error al leer código de operación: %v", err),
		}
	}
	
	var messageLength uint32
	if err := binary.Read(reader, binary.BigEndian, &messageLength); err != nil {
		return 0, "", &SerializationError{
			Msg: fmt.Sprintf("Error al leer longitud del mensaje: %v", err),
		}
	}
	
	opCode := OperationCode(opCodeRaw)
	
	// Si no hay mensaje, retornar cadena vacía
	if messageLength == 0 {
		return opCode, "", nil
	}
	
	// Verificar tamaño razonable
	if messageLength > MaxMessageSize {
		return 0, "", &SerializationError{
			Msg: fmt.Sprintf("Mensaje demasiado largo: %d bytes", messageLength),
		}
	}
	
	// Leer mensaje completo
	messageBytes, err := sp.readExact(conn, int(messageLength))
	if err != nil {
		return 0, "", err
	}
	
	// Convertir bytes a string UTF-8
	message := string(messageBytes)
	
	return opCode, message, nil
}