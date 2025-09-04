package common

import (
	"fmt"
	"os"
)


const (
	NAME      = 0
	LASTNAME  = 1
	DOCUMENT  = 2
	BIRTHDATE = 3
	NUMBER    = 4
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

func (b *Bet) getRawBet() string {
	return fmt.Sprintf("%s,%s,%s,%s,%s,%s", b.Agency, b.Name, b.LastName, b.Document, b.Birthdate, b.Number)
}

