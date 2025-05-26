from enum import Enum
import random as rand
from cardgames.utils import cards
import pygame

class Player:

    def __init__(self, name, buy_in):
        self._name=name
        self._balance=buy_in
        self._hand = []

    def __repr__(self):
        return f"Player Name: {self._name} \nCurrent Balance: {str(self._balance)}"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, balance):
        self._balance = balance

    @property
    def hand(self):
        return self._hand

    @hand.setter
    def hand(self, hand):
        self._hand = hand

    def hit(self, cards):
        self.hand =  self.hand + cards

    def reset_hand(self):
        self.hand = []

    def getscore(self):
        myhand = self.hand
        score = 0

        # move all aces to end of list
        aces=[]
        for c in myhand:
            if c.rank == "A":
                aces.append(c)
                myhand.remove(c)
        myhand += aces

        for c in myhand:
            try:
                score += int(c.rank)
            except:
                if c.rank in ["Jack", "Queen", "King"]:
                    score += 10
                elif score + 11 > 21:
                    score += 1
                else:
                    score += 11

        return score

    def check_blackjack(self):
        return ((self.getscore() == 21) and (len(self.hand) == 2))

    def payout(self, bet, outcome):
        self.balance += bet*outcome


class Outcome(Enum):
    player_blackjack = 0
    dealer_blackjack = 1
    bust = 2
    win = 3
    push = 4
    loss = 5


class GameState(Enum):
    place_bet = 0
    player_turn = 1
    dealer_turn = 2
    ended = 3


class Engine:

    def __init__(self, player_name="Player1", buy_in=1000, num_packs=6, dealer_stand=17):
        self.num_packs = num_packs
        self.dealer_stand = dealer_stand
        self.shoe = None
        self.outcome = None
        self._bet = None

        self.new_shoe()

        self.dealer = Player("Dealer", 1)
        self.player = Player(player_name, buy_in)

        self.state = GameState.place_bet

    def deal(self):
        self.player.hand = self.shoe.dealcards(2)
        self.dealer.hand = self.shoe.dealcards(2)

    def get_outcome(self):
        pbj = self.player.check_blackjack()
        dbj = self.dealer.check_blackjack()

        if pbj and dbj:
            self.outcome = Outcome.push
        elif pbj and not dbj:
            self.outcome = Outcome.player_blackjack
        elif dbj and not pbj:
            self.outcome = Outcome.dealer_blackjack
        else:
            if self.player.getscore() > 21:
                self.outcome = Outcome.bust
            elif self.dealer.getscore() > 21:
                self.outcome = Outcome.win
            elif self.player.getscore() > self.dealer.getscore():
                self.outcome = Outcome.win
            else:
                self.outcome = Outcome.loss

    def new_shoe(self):
        self.shoe = cards.Deck(self.num_packs, jokers=False)
        self.reshuffle_at = round((self.num_packs * 52) * (rand.randint(10, 30) / 100))

    def settle_bet(self):
        if self.outcome == Outcome.player_blackjack:
            self.player.payout(self._bet, 1.5)
            return

        elif self.outcome in [Outcome.bust, Outcome.dealer_blackjack, Outcome.loss]:
            self.player.payout(self._bet, -1)
        elif self.outcome == Outcome.win:
            self.player.payout(self._bet, 1)

    def nexthand(self):

        self.player.reset_hand()
        self.dealer.reset_hand()

        if self.shoe.size() <= self.reshuffle_at:
            self.new_shoe()

        self._bet = None
        self.state = GameState.place_bet

    def player_action(self, key):
        if key == pygame.K_h:
            self.player.hit(self.shoe.dealcards())
        elif key == pygame.K_s:
            self.state = GameState.dealer_turn

        if self.player.getscore() >= 21:
            self.get_outcome()
            self.settle_bet()
            self.state = GameState.ended

    def dealer_action(self):
        if self.dealer.getscore() < self.dealer_stand:
            self.dealer.hit(self.shoe.dealcards())
        else:
            self.get_outcome()
            self.settle_bet()
            self.state = GameState.ended

    def place_bet(self, event):

        if self._bet is None:
            self._bet=""

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if int(self._bet) <= self.player.balance:
                    self._bet = int(self._bet)
                    self.deal()
                    self.state = GameState.player_turn
                else:
                    self._bet = ""
            else:
                if event.unicode.isdigit():
                    self._bet += event.unicode


def RenderHand(window, player, start = (1200, 350), initial_offset=130, increment=85):
    offset = initial_offset
    for c in player.hand:
        c_img = pygame.image.load(c._image)
        c_img = pygame.transform.scale(c_img, (int(500 * 0.25), int(726 * 0.25)))

        window.blit(c_img, (start[0] - offset, start[1]))
        offset += increment

def RenderText(window, txt, pos):
    font = pygame.font.Font(None, 24)
    mytext = font.render(txt, True, (10, 105, 15))
    window.blit(mytext, pos)

def RenderGame(window, game_engine, bg_color=(35, 160, 40)):
    window.fill((35, 160, 40))

    RenderText(window, f"Player Name: {game_engine.player.name}", (1000, 15))
    RenderText(window, f"Current Balance: {game_engine.player.balance}", (1000, 35))

    if game_engine.state == GameState.place_bet:
        input_rect = pygame.Rect(500, 300, 140, 32)
        pygame.draw.rect(window, (220, 220, 220), input_rect)

        base_font = pygame.font.Font(None, 32)
        text_surface = base_font.render(game_engine._bet, True, (0, 0, 0))
        window.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

    elif game_engine.state == GameState.player_turn:

        RenderHand(window, game_engine.player)

        dealer_first = pygame.image.load(game_engine.dealer.hand[0]._image)
        dealer_first = pygame.transform.scale(dealer_first, (int(500*0.25), int(726*0.25)))
        window.blit(dealer_first, (30, 15))

        card_back = pygame.image.load(cards.cardback)
        card_back = pygame.transform.scale(card_back, (int(500 * 0.25), int(726 * 0.25)))
        window.blit(card_back, (180, 15))

        RenderText(window, f"Current Score: {game_engine.player.getscore()}", (1000, 550))

    elif game_engine.state == GameState.dealer_turn:

        RenderHand(window, game_engine.player)
        RenderText(window, f"Current Score: {game_engine.player.getscore()}", (1000, 550))

        RenderHand(window, game_engine.dealer, (30, 15), 0, -85)
        RenderText(window, f"Dealer Score: {game_engine.dealer.getscore()}", (30, 200))

    elif game_engine.state == GameState.ended:

        RenderHand(window, game_engine.player)
        RenderText(window, f"Current Score: {game_engine.player.getscore()}", (1000, 550))

        RenderHand(window, game_engine.dealer, (30, 15), 0, -85)
        RenderText(window, f"Dealer Score: {game_engine.dealer.getscore()}", (30, 200))

        RenderText(window, f"Result: {game_engine.outcome.name}", (600, 300))

def Play():
    pygame.init()

    bounds = (1200, 600)

    window = pygame.display.set_mode(bounds)
    pygame.display.set_caption("blackjack")

    running = True

    MyGameEngine = Engine()

    while running:
        key = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif MyGameEngine.state == GameState.place_bet:
                MyGameEngine.place_bet(event)

            elif MyGameEngine.state == GameState.player_turn:
                if MyGameEngine.player.getscore() > 21:
                    MyGameEngine.state = GameState.ended
                elif event.type == pygame.KEYDOWN:
                    MyGameEngine.player_action(event.key)

            elif MyGameEngine.state == GameState.dealer_turn:
                if event.type == pygame.KEYDOWN:
                    MyGameEngine.dealer_action()

            elif MyGameEngine.state == GameState.ended:
                if event.type == pygame.KEYDOWN:
                    if MyGameEngine.player.balance > 0:
                        MyGameEngine.nexthand()
                    else:
                        running = False

        RenderGame(window, MyGameEngine)
        pygame.display.update()





