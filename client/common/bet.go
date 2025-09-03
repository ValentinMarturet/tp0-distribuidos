package common

import (
	"fmt"
	"net"
	"os"
)

type Bet struct {
	Agency   string
	Name     string
	LastName string
	Document string
	Birthdate string
	Number   string
}

func newBetFromEnv(agencyID string) Bet {
	return Bet {
		Agency:   agencyID,
		Name:     os.Getenv("BET_NAME"),
		LastName: os.Getenv("BET_LASTNAME"),
		Document: os.Getenv("BET_DOCUMENT"),
		Birthdate: os.Getenv("BET_BIRTHDATE"),
		Number:   os.Getenv("BET_NUMBER"),
	}
}

func (b *Bet) sendBetToSocket(socket net.Conn) error {
	message := fmt.Sprintf("%s,%s,%s,%s,%s,%s", b.Agency, b.Name, b.LastName, b.Document, b.Birthdate, b.Number)
	protocol := SimpleProtocol{}
	return protocol.SerializeToSocket(socket, APUESTA, message)
}

func (b *Bet) getDocument() string {
	return b.Document
}

func (b *Bet) getNumber() string {
	return b.Number
}