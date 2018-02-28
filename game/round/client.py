import os

from utils import utils
from parameters import parameters

from game.models import RoundComposition

from . import data, state

import game.player.management

__path__ = os.path.relpath(__file__)

"""
    Here are grouped the functions called by: game.views (i.e. by client)
"""


# ----------------------------------- Ask functions ------------------------------------------------------ #

def ask_firm_init(u, rd_opp, rm, rd, rs):

    # -------  Log stuff -------------------------------------------------------------------------- #

    utils.log("Player {} for room {} and round {} ask init: t is {}.".format(
        u.id, u.room_id, rd.id, rd.t),
        f=utils.fname(), path=__path__)

    # -------  Maybe client has to wait the other player ------------------------------------------ #

    if game.player.management.client_has_to_wait_over_player(u=u, rm=rm):

        if not rm.trial:
            opp_progression = game.player.management.get_opponent_progression(u=u, rd_opp=rd_opp)
            return parameters.error["wait"], opp_progression  # Tuple is necessary!! '-1' hold for wait

    # Get information necessary for firm initialization
    d = data.get_init_info(u=u, rd=rd, rs=rs)

    return rd.t, d["firm_state"], d["player"]["position"], d["player"]["price"], d["player"]["profits"], \
           d["opp"]["position"], d["opp"]["price"], d["opp"]["profits"], rd.ending_t


# ----------------------------------| passive firm demands |-------------------------------------- #

def ask_firm_passive_opponent_choice(u, rd, rs, t):

    # -------  Get needed variables --------------------------------------------------------------- #

    opponent_id = (u.firm_id + 1) % parameters.n_firms

    # -------  Log stuff -------------------------------------------------------------------------- #
    utils.log("Firm passive {} of room {} and round {} asks for opponent strategy.".format(
        u.id, u.room_id, rd.id),
        f=utils.fname(), path=__path__)

    utils.log(
        "Client's time is {}, server's time is {}.".format(t, rd.t),
        f=utils.fname(), path=__path__
    )

    # ---------- Record call ------------------------------------------------------------------ #

    if t <= rd.t:

        # Make bot firm play if applicable
        if state.check_if_bot_firm_has_to_play(rd=rd, rs=rs, t=t):
            state.validate_firm_choice_and_make_consumers_play(rd=rd, rs=rs, t=t)

        if rs.firm_active_played:
            positions, prices = data.get_positions_and_prices(rd=rd, t=t)
            return t, positions[opponent_id], prices[opponent_id]

        else:
            utils.log("Have to wait: Active firm needs to play", f=utils.fname(), path=__path__)
            return parameters.error["wait"],  # Tuple is necessary!!

    else:
        utils.log("Error: Time is superior!!!!", f=utils.fname(), path=__path__, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!


def ask_firm_passive_consumer_choices(u, opp, rm, rd, rs, t):

    # ---------- Do stuff ------------------------------------------------------------------- #

    if t <= rd.t:

        if rs.consumers_played:

            is_end = int(state.is_end_of_game(rd=rd, t=t))

            consumer_choices = data.get_consumer_choices(rd=rd, t=t)
            consumer_choices = [1 if i == u.firm_id else 0 if i != -1 else -1 for i in consumer_choices]

            if is_end:
                game.player.management.go_to_next_round(u=u, opp=opp, rm=rm)

            return (t,) + tuple((i for i in consumer_choices)) + (is_end,)

        else:
            return parameters.error["wait"],  # Tuple is necessary!! // Have to wait

    else:
        utils.log("Error: Time is superior!!!!", f=utils.fname(), path=__path__, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!


# -----------------------------------| active firm demands |-------------------------------------- #

def ask_firm_active_choice_recording(u, rd, rs, t, position, price):

    # -------  do stuff -------------------------------------------------------------------------- #

    if t <= rd.t:

        if not rs.firm_active_played:
            # tables FirmPositions, FirmPrices are used
            data.register_firm_choices(
                u=u, t=t, position=position, price=price
            )

            state.validate_firm_choice_and_make_consumers_play(rs=rs, rd=rd, t=t)

        return t,  # ! Must be a tuple

    else:
        utils.log("Error: Time is superior!!!!", f=utils.fname(), path=__path__, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!


def ask_firm_active_consumer_choices(u, opp, rm, rd, rs, t):

    # -------  Log stuff -------------------------------------------------------------------------- #

    utils.log(
        "Firm active {} of room {} and round {} asks the number of its clients.".format(
            u.id, u.room_id, rd.id
        ), f=utils.fname(), path=__path__)
    utils.log("Client's time is {}, server's time is {}.".format(t, rd.t), f=utils.fname(), path=__path__)

    # ---------------- Do stuff ------------------------------------------ #

    if t <= rd.t:

        is_end = int(state.is_end_of_game(rd=rd, t=t))

        if rs.firm_active_played:

            consumer_choices = data.get_consumer_choices(rd=rd, t=t)
            consumer_choices = [1 if i == u.firm_id else 0 if i != -1 else -1 for i in consumer_choices]

            if is_end:
                game.player.management.go_to_next_round(u=u, opp=opp, rm=rm)

            return (t,) + tuple((i for i in consumer_choices)) + (is_end,)

        else:
            return parameters.error["wait"],  # Tuple is necessary!!

    else:
        utils.log("Error: Time is superior!!!!", f=utils.fname(), path=__path__, level=3)
        return parameters.error["time_is_superior"],  # Time is superior!
