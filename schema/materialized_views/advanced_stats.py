
def calculate_possesions(table, team_prefix='', opp_prefix='opp_'):
    return '({tg}.{team_prefix}fga + 0.4 * {tg}.{team_prefix}fta - 1.07 * ({tg}.{team_prefix}orb / ({tg}.{team_prefix}orb + {tg}.{opp_prefix}drb)) * ({tg}.{team_prefix}fga - {tg}.{team_prefix}fgm) + {tg}."{team_prefix}to")'.format(tg=table, team_prefix=team_prefix, opp_prefix=opp_prefix)

def calculate_ortg(table):
    return "ROUND(100 * {tg}.pts / {possesions}, 5)".format(tg=table, possesions=calculate_possesions(table))

def calculate_drtg(table):
    return "ROUND(100 * {tg}.opp_pts / {possesions}, 5)".format(tg=table, possesions=calculate_possesions(table, team_prefix='opp_', opp_prefix=''))


def calculate_per(table):
    """
    Can't calculate this as we don't have personal fouls :/
    """
    vop = "({}.lg_pts::numeric/({}.lg_fga - {}.lg_orb + {}.lg_to + 0.44 * {}.lg_fta))".format(table)
    drbp = "({}.lg_drb::numeric/({}.lg_orb + {}.drb))".format(table)
    factor = "(2::numeric/3 - (0.5 * {}.lg_ast/{}.lg_fg/(2 * {}.lg_fgm/{}.lg_ftm)))".format(table)

    uper = "1/{}.mp * ("

    # Can't calculate this as we don't have personal fouls...
    uper = """
        {1}/{table}.mp * ({table}.three_pm + ({2}/{3} * {table}.ast) + ((2 - {factor} * {tm_ast}/{tm_fg}) * {table}.fgm)
        + (0.5 * {table}.ftm * (2 -  {1}/{3} * {tm_ast}/{tm_fg})) - ({vop} * {table}.to)
        - ({vop} * {drbp} * ({table}.fga - {table}.fgm)) - ({vop} * 0.44 * (0.44 + (0.56 * {drbp})) * ({table}.fta - {table}.ftm))
        + ({vop} * (1 - {drbp}) * ({table}.drb)) + ({vop} * {drbp} * {table}.orb) + ({vop} * {table}.stl) + ({vop} * {drbp} * {table}.blk)
        - ({personal_foul} * ({lg_fta}/{lg_personal_foul} - 0.44 * {lg_fta}/{lg_personal_foul} * {vop})))
    """.format(vop=vop, drbp=drbp, factor=factor)
    return