# Dealer's policy is fixed: while total is below 16, keep hitting
dealer_threshold = 16

# Simulate the outcome of this policy
import random

class Blackjack_mw:
    # Dealer's policy is fixed: while total is below 16, keep hitting
    DEALER_THRESHOLD = 16
    BUST = 22
    cards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

    # Store winning probability and best action in a dictionary
    # Winning here means that the player's hand isn't a bust and it's higher than the dealer's hand
    win_prob = {}
    best_action = {}

    def populate(self):

        def get_hand_value(hand, has_ace):
            if has_ace and hand <= 11:
                hand += 10
            return hand

        # Use top-down dynamic programming to compute the probabilities
        def compute_win_prob(player_hand, player_has_ace, dealer_hand, dealer_has_ace, player_turn):
            # Base cases
            if player_hand >= self.BUST:
                return 0.0
            elif dealer_hand >= self.BUST:
                return 1.0

            state = (player_hand, player_has_ace, dealer_hand, dealer_has_ace, player_turn)

            if state in self.win_prob:
                # this state has been explored before
                return self.win_prob[state]

            if player_turn:
                # Possible action 1: stay
                stay_win_prob = compute_win_prob(player_hand, player_has_ace, dealer_hand, dealer_has_ace, False)

                # Possible action 2: hit
                hit_win_prob = 0.0
                for card in self.cards:
                    hit_win_prob += 1.0 / len(self.cards) * compute_win_prob(player_hand + card,
                                                                        player_has_ace | (card == 1), dealer_hand,
                                                                        dealer_has_ace, True)

                if stay_win_prob > hit_win_prob:
                    self.win_prob[state] = stay_win_prob
                    self.best_action[state] = 'STAY'
                else:
                    self.win_prob[state] = hit_win_prob
                    self.best_action[state] = 'HIT'

            else:  # dealer's turn
                if get_hand_value(dealer_hand, dealer_has_ace) < self.DEALER_THRESHOLD:
                    # Dealer can only hit when their hand is below the threshold
                    hit_win_prob = 0.0
                    for card in self.cards:
                        hit_win_prob += 1.0 / len(self.cards) * compute_win_prob(player_hand, player_has_ace,
                                                                            dealer_hand + card,
                                                                            dealer_has_ace | (card == 1), False)
                    self.win_prob[state] = hit_win_prob
                else:
                    # Figure out who wins
                    if get_hand_value(player_hand, player_has_ace) > get_hand_value(dealer_hand, dealer_has_ace):
                        self.win_prob[state] = 1.0
                    else:
                        self.win_prob[state] = 0.0

            return self.win_prob[state]

        def get_best_action(player_hand, player_has_ace, dealer_hand, dealer_has_ace, player_turn):
            assert (player_turn)
            state = (player_hand, player_has_ace, dealer_hand, dealer_has_ace, player_turn)
            compute_win_prob(*state)
            return self.best_action[state]

        for player_hand in range(0, self.BUST):
            if (player_hand == 0 or player_hand == 1):
                continue
            for player_has_ace in [False, True]:
                if player_has_ace and player_hand == 0:  # not possible
                    continue
                elif player_has_ace is False and player_hand == 1:  # also not possible
                    continue
                for dealer_hand in range(0, 11):
                    for dealer_has_ace in [False, True]:
                        if dealer_has_ace and dealer_hand == 0:  # not possible
                            continue
                        elif dealer_has_ace is False and dealer_hand == 1:  # also not possible
                            continue
                        state = (player_hand, player_has_ace, dealer_hand, dealer_has_ace, True)
                        p = compute_win_prob(*state)
                        a = get_best_action(*state)

    def compute_win_prob_given_action(self, player_hand, player_has_ace, dealer_hand, dealer_has_ace, player_turn,
                                      action):
        assert (player_turn)
        if action == 'STAY':
            return self.win_prob[(player_hand, player_has_ace, dealer_hand, dealer_has_ace, False)]
        elif action == 'HIT':
            hit_win_prob = 0.0
            for card in self.cards:
                if (player_hand + card >= 22):
                    continue
                hit_win_prob += 1.0 / len(self.cards) * self.win_prob[(player_hand + card,
                                                                         player_has_ace | (card == 1), dealer_hand,
                                                                         dealer_has_ace, True)]
            return hit_win_prob

    def chance(self, hand, player_has_ace, dealer_hand, dealer_has_ace):
        state = (hand, player_has_ace, dealer_hand, dealer_has_ace, True)
        return (self.compute_win_prob_given_action(*state, 'STAY') * 100,
                self.compute_win_prob_given_action(*state, 'HIT') * 100,
                self.best_action[state])