import os
from common.utils import has_won, load_bets

class Lottery:
    def __init__(self):
        #get number of agencies from env variable
        self._number_of_agencies = int(os.getenv('NUMBER_OF_AGENCIES', 5))
        self._agencies = [False] * self._number_of_agencies
        self._winners = {}
        self._draw_done = False

    def make_draw(self):
        if self._draw_done:
            return
        if False in self._agencies:
            raise RuntimeError("Not all agencies are ready")
        bets = load_bets()
        for bet in bets:
            if has_won(bet):
                if bet.agency not in self._winners:
                    self._winners[bet.agency] = []
                self._winners[bet.agency].append(bet)
        self._draw_done = True

    def get_winners_for_agency(self, agency_id) -> str:
        winners = self._winners.get(agency_id, [])
        formatted_winners = ""
        for bet in winners:
            formatted_winners += bet.document + ","
        formatted_winners = formatted_winners.rstrip(",")
        return formatted_winners

    def mark_agency_ready(self, agency_id):
        agency_id -= 1
        if 0 <= agency_id < len(self._agencies):
            self._agencies[agency_id] = True

    def all_agencies_ready(self):
        return all(self._agencies)

    def draw_done(self):
        return self._draw_done

    def agencies(self):
        return self._agencies   