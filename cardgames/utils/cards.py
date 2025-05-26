import random as rand

img_dir = "./cardgames/utils/images"
cardback = "./cardgames/utils/images/cardback.png"

#define card object
class Card:

    # define method for initialisation
    def __init__(self, rank, suit):
        self._rank = rank
        self._suit = suit
        self._image = f'{img_dir}/{self._rank}_of_{self._suit}.png'

    # define string representation
    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    @property
    def suit(self):
        return self._suit

    @suit.setter
    def suit(self, suit):
        if suit in ["hearts", "spades", "diamonds", "clubs", "joker"]:
            self._suit=suit
        else:
            raise ValueError("Invalid Suit")

    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, rank):
        if rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace", "joker"]:
            self._rank = rank
        else:
            raise ValueError("Invalid Rank")


class Deck:
    def __init__(self, num_packs=1, jokers = False):
        self._num_packs = num_packs
        self._jokers = jokers
        self._cards = []
        self.build()
        self.shuffle()

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, cards):
        self._cards = cards

    def build(self):
        suits = ["Hearts", "Spades", "Diamonds", "Clubs"]
        ranks = [str(n) for n in range(2,11)] + ["Jack", "Queen", "King", "Ace"]
        pack = [Card(r, s) for r in ranks for s in suits]
        if self._jokers:
            pack += [Card("Joker", "Joker"), Card("Joker", "Joker")]

        self.cards = pack*self._num_packs

    def shuffle(self):
        rand.shuffle(self._cards)

    def size(self):
        return len(self.cards)

    def dealcards(self, num=1):
        res = []
        i = 0
        while i < num:
            res.append(self._cards.pop())
            i += 1

        return res
