import random

win_probability = 0.6

def power_play(ct, wager):
    assert ct >= 2 and ct <= 4
    win_ct = 0
    for i in range(ct):
        roll1 = random.uniform(0, 1)
        if roll1 < win_probability:
            win_ct += 1
    
    if win_ct != ct:
        return 0
    if win_ct == 4:
        return wager * 10
    
    if win_ct == 3:
        return wager * 5

    if win_ct == 2:
        return wager * 3

def flex_pay(ct, wager):
    win_ct = 0
    for i in range(ct):
        roll1 = random.uniform(0, 1)
        if roll1 < win_probability:
            win_ct += 1
    
    if win_ct == 0:
        return 0
    if ct == 2:
        if win_ct == 2:
            return wager * 2
        if win_ct == 1:
            return wager * 0.5

    if ct == 3:
        if win_ct == 3:
            return wager * 2.25
        if win_ct == 2:
            return wager * 1.25

    if ct == 4:
        if win_ct == 4:
            return wager * 5
        if win_ct == 3:
            return wager * 1.5
        
    if ct == 5:
        if win_ct == 5:
            return wager * 10
        if win_ct == 4:
            return wager * 2
        if win_ct == 3:
            return wager * 0.4

    return 0


def simulate(sim_ct, bank_roll, is_power_play, pick_ct):
    for i in range(sim_ct):
        bid = bank_roll * 0.01
        # bid = 10
        bank_roll -= bid
        if is_power_play:
            payout = power_play(pick_ct, 10)
        else:
            payout = flex_pay(pick_ct, 10)

        bank_roll += payout

        print("{} {}".format(i, bank_roll))


# simulate(1000, 100, True, 2)
simulate(1000, 100, False, 2)
