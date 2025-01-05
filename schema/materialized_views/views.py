from .bases import BasicView, AggMaterializedView, MaterializedView
from .registry import register
from .advanced_stats import calculate_ortg, calculate_drtg
from schema import models

@register
class Player(BasicView):
    source_table = models.Player
    rename_fields = {
        'player_name': 'name',
    }


@register
class Team(BasicView):
    source_table = models.Team


# (CASE WHEN date_part('month', g.date) < 5 THEN date_part('year', g.date)-1 ELSE date_part('year', g.date) END)::integer as season
@register
class Game(BasicView):
    source_table = models.Game
    rename_fields = {
        'season_id': 'season',
    }


@register
class PlayerGame(BasicView):
    source_table = models.PlayerGame
    table_name = 'player_game'
    rename_fields = {
        'season_id': 'season',
    }
    excluded_fields = ['ft_pct', 'fg_pct', 'fg3_pct']


class PlayerGameDerivativeView(AggMaterializedView):
    source_table = models.PlayerGame

    def _determine_agg(self, column):
        agg_statement = 'SUM({column})'
        return agg_statement.format(column=column)

# @register
# class BoxScore(AggMaterializedView):
#     table_name = 'game_boxscore'
#     source_table_name = 'player_game'
#     excluded_fields = ['season', 'name']


@register
class PlayerSeason(PlayerGameDerivativeView):
    table_name = 'player_season'
    indexed_fields = ['player_id', 'name']
    excluded_fields = PlayerGame.excluded_fields + ['starter', 'season', 'name', 'wl']

    def determine_agg(self, column):
        if column == 'pg.mp':
            return "FLOOR(EXTRACT(EPOCH FROM SUM(pg.mp)::interval)/60)::integer"
        return super(PlayerSeason, self).determine_agg(column)

    def get_query(self):
        columns = self._get_columns()
        headers = self._get_headers(columns)

        # Sum totals
        inner_query = """
            SELECT pg.player_id, g.season, pg.team_id, COUNT(*) as games_played, {sum_headers}
            FROM public_access.player_game pg, public_access.game g
            WHERE pg.game_id = g.game_id
            GROUP BY pg.player_id, g.season, pg.team_id
        """.format(sum_headers=self._get_agg_headers(columns, 'pg'))

        # join in player table so i can get add player information
        query = """
            SELECT p.player_id, p.name, pg.season, pg.team_id, pg.games_played, {headers}
            from public_access.player p, ({inner_query}) pg
            where p.player_id = pg.player_id
        """.format(headers=self._get_headers(columns), inner_query=inner_query)

        return query

def calculate_eps(table):

    return "CASE WHEN ({table}.fga - {table}.orb + {table}.ast + {table}.to != 0) THEN ROUND((({table}.fgm + {table}.ast) * {table}.pts)::numeric/({table}.fga - {table}.orb + {table}.ast + {table}.to), 5) ELSE 0 END".format(
        table=table
    )

# @register
# class PlayerCareer(PlayerGameDerivativeView):
#     table_name = 'player_career'
#     indexed_fields = ['player_id', 'full_name']
#     excluded_fields = ['starter']

#     def get_query(self):
#         columns = self._get_columns()
#         headers = self._get_headers(columns)

#         # Sum totals
#         inner_query = """
#             SELECT pg.player_id, {sum_headers}
#             FROM schema_playergame pg, schema_game g
#             WHERE pg.game_id = g.game_id
#             GROUP BY pg.player_id
#         """.format(sum_headers=self._get_agg_headers(columns, 'pg'))

#         # join in player table so i can get add player information
#         query = """
#             SELECT p.player_id as player_id, p.full_name as full_name, {headers}
#             from schema_player p, ({inner_query}) pg
#             where p.player_id = pg.player_id
#         """.format(headers=self._get_headers(columns), inner_query=inner_query)

#         return query


# @register
# class PlayerTeam(PlayerGameDerivativeView):
#     table_name = 'player_team'
#     indexed_fields = ['player_id', 'full_name']
#     excluded_fields = ['starter']

#     def get_query(self):
#         columns = self._get_columns()
#         headers = self._get_headers(columns)

#         # Sum totals
#         inner_query = """
#             SELECT pg.player_id, {sum_headers}
#             FROM schema_playergame pg, schema_game g
#             WHERE pg.game_id = g.game_id
#             GROUP BY pg.player_id, pg.team_id
#         """.format(sum_headers=self._get_agg_headers(columns, 'pg'))

#         # join in player table so i can get add player information
#         query = """
#             SELECT p.player_id as player_id, p.full_name as full_name, {headers}
#             from schema_player p, ({inner_query}) pg
#             where p.player_id = pg.player_id
#         """.format(headers=self._get_headers(columns), inner_query=inner_query)

#         return query

# @register
# class TeamGame(BasicView):
#     table_name = 'team_game'
#     indexed_fields = ['team_id', 'game_id', 'season', 'date', 'opp_team_id']
#     def get_query(self):
#         query = """
#             SELECT
#                 t.team_id,
#                 g.game_id,
#                 g.season,
#                 g.date,
#                 (t.team_id = g.home_team_id) as at_home,
#                 CASE WHEN (t.team_id = g.home_team_id) THEN g.away_team_id ELSE g.home_team_id END as opp_team_id,
#                 CASE WHEN (t.team_id = g.home_team_id) THEN b.home_score ELSE b.away_score END as team_score,
#                 CASE WHEN (t.team_id = g.home_team_id) THEN b.away_score ELSE b.home_score END as opp_score,
#                 CASE WHEN (t.team_id = g.home_team_id) THEN (b.home_score > b.away_score) ELSE (b.home_score < b.away_score) END as won,
#                 row_number() OVER(PARTITION BY t.team_id, g.season ORDER BY g.date) as game_number
#             FROM public.team t, public.game g, public.game_boxscore b
#             WHERE (t.team_id = g.away_team_id or t.team_id = g.home_team_id) and g.game_id = b.game_id
#             ORDER BY t.team_id, g.season, g.date
#         """
#         return query



# @register
# class TeamGameStats(PlayerGameDerivativeView):
#     table_name = 'team_game_stats'
#     indexed_fields = ['team_id', 'game_id']
#     excluded_fields = ['starter', 'season', 'full_name']

#     def determine_agg(self, column):
#         if column == 'pg.mp':
#             return "FLOOR(EXTRACT(EPOCH FROM SUM(pg.mp)::interval)/60)::integer"
#         return super(TeamGameStats, self).determine_agg(column)

#     def get_query(self):
#         columns = self._get_columns()
#         headers = self._get_headers(columns)

#         # Sum totals
#         inner_query = """
#             SELECT pg.team_id, g.game_id, {sum_headers}
#             FROM public.player_game pg, public.game g
#             WHERE pg.game_id = g.game_id
#             GROUP BY pg.team_id, g.game_id
#         """.format(sum_headers=self._get_agg_headers(columns, 'pg'))

#         # join in player table so i can get add player information
#         query = """
#             SELECT t.team_id, g.game_id, g.season, g.date, row_number() OVER(PARTITION BY g.season, pg.team_id) as game_number, {headers}
#             from public.team t, ({inner_query}) pg, public.game g
#             where t.team_id = pg.team_id and g.game_id = pg.game_id
#             order by g.season, t.team_id, g.date
#         """.format(headers=self._get_headers(columns), inner_query=inner_query)

#         return query

# @register
# class TeamGameOpponent(MaterializedView):
#     table_name = 'team_game_stats_opponent'
#     source_table_name = 'public.team_game_stats'
#     indexed_fields = ['team_id', 'game_id']
#     excluded_fields = ['team_id', 'game_id', 'season', 'date']

#     def get_query(self):
#         columns = self._get_columns()

#         # Sum totals
#         query = """
#             SELECT tg.team_id, g.game_id, otg.team_id as opponent, {columns}
#             FROM public.team_game_stats tg, public.game g, public.team_game_stats otg
#             WHERE tg.game_id = g.game_id and otg.game_id = g.game_id and otg.team_id <> tg.team_id
#         """.format(columns=",".join(["otg.{name}".format(name=column) for column in columns]))

#         return query


# @register
# class TeamSeason(PlayerGameDerivativeView):
#     table_name = 'team_season'
#     indexed_fields = ['team_id', 'season']
#     excluded_fields = ['starter', 'season', 'full_name']

#     def get_query(self):
#         columns = self._get_columns()
#         headers = self._get_headers(columns)

#         # Sum totals
#         inner_query = """
#             SELECT tg.team_id, g.season, COUNT(*) as gp, {tg_sum_headers}, {tgo_sum_headers}
#             FROM public.team_game_stats tg, public.game g, public.team_game_stats_opponent tgo
#             where tg.game_id = g.game_id and tgo.game_id = g.game_id and tgo.team_id = tg.team_id
#             GROUP BY tg.team_id, g.season
#         """.format(tg_sum_headers=self._get_agg_headers(columns, table='tg', agg_prefix='tg_sum'), tgo_sum_headers=self._get_agg_headers(columns, table='tgo', agg_prefix='tgo_sum'))

#         # join in player table so i can get add player information
#         query = """
#             SELECT iq.team_id as team_id, iq.season as season, iq.gp, {tg_headers}, {tgo_headers}
#             from ({inner_query}) iq
#         """.format(tg_headers=self._get_headers(columns, table='iq', agg_prefix='tg_sum'), tgo_headers=self._get_headers(columns, table='iq', agg_prefix='tgo_sum', prefix='opp_'), inner_query=inner_query)

#         return query


# @register
# class TeamSeasonAdvanced(BasicView):
#     table_name = 'team_season_advanced'

#     def get_query(self):

#         query = """
#             SELECT ts.team_id, ts.season, {eps} as eps, {ortg} as ortg
#             from public.team_season ts
#             order by ortg desc
#         """.format(eps=calculate_eps('ts'), ortg=calculate_ortg('ts'))

#         return query

# @register
# class InSeasonTeamRecord(BasicView):
#     table_name = 'in_season_team_record'

#     def get_query(self):

#         query = """
#             SELECT
#                 t.team_id,
#                 g2.season,
#                 g2.date,
#                 g2.game_id,
#                 SUM((tg.won)::int) as wins,
#                 COUNT(*) - SUM(tg.won::int) as losses,
#                 COUNT(*) as games_played,
#                 ROUND(SUM(tg.won::int)::numeric/count(*), 5) as win_perc,
#                 ROUND(SUM((tg.won and tg.game_number > tg2.game_number - 11)::int)::numeric/count(tg.game_number > tg2.game_number - 11), 5) as last_10_perc,
#                 ROUND(SUM((tg.won and tg.game_number > tg2.game_number - 5)::int)::numeric/count(tg.game_number > tg2.game_number - 5), 5) as last_5_perc
#             from public.team t, public.team_game tg, public.game g, public.game g2, public.team_game tg2
#             WHERE
#                 t.team_id = tg.team_id and
#                 tg.game_id = g.game_id and
#                 t.team_id = tg2.team_id and
#                 tg2.game_id = g2.game_id and
#                 (g2.away_team_id = t.team_id or g2.home_team_id = t.team_id) and
#                 g.date < g2.date
#             GROUP BY t.team_id, g2.game_id, g2.season, g2.date
#             order by g2.season desc, t.team_id, g2.date
#         """

#         return query


# @register
# class InSeasonTeamMetrics(BasicView):
#     table_name = 'in_season_team_metrics'

#     def get_query(self):

#         max_team_records = """
#             SELECT
#                 t.team_id,
#                 g.season,
#                 g.date,
#                 MAX(tr.date) as max_date
#             FROM public.team t, public.game g, public.in_season_team_record tr
#             WHERE
#                 t.team_id = tr.team_id and
#                 tr.season = g.season and
#                 tr.date < g.date
#             GROUP BY g.season, g.date, t.team_id
#         """

#         query = """
#             SELECT
#                 t.team_id,
#                 g2.season,
#                 g2.date,
#                 g2.game_id,
#                 SUM(tr.wins) as opp_wins,
#                 SUM(tr.games_played) as opp_games_played,
#                 ROUND(SUM(tr.wins)::numeric/SUM(tr.games_played), 5) as sos
#             FROM public.team t, public.team_game tg, public.game g, public.game g2, public.in_season_team_record tr, ({max_team_records}) mtr
#             WHERE
#                 t.team_id = tg.team_id and
#                 tg.game_id = g.game_id and
#                 (g2.away_team_id = t.team_id or g2.home_team_id = t.team_id) and
#                 tr.team_id = tg.opp_team_id and
#                 mtr.date = g2.date and
#                 mtr.team_id = tg.opp_team_id and
#                 tr.date = mtr.max_date and
#                 g.date < g2.date
#             GROUP BY t.team_id, g2.game_id, g2.season, g2.date
#             ORDER BY g2.season desc, t.team_id, g2.date
#         """.format(max_team_records=max_team_records)

#         return query

# @register
# class TeamSeasonHistorical(PlayerGameDerivativeView):
#     table_name = 'team_season_historical'
#     indexed_fields = ['team_id', 'game_id', 'date']
#     excluded_fields = ['starter', 'season', 'full_name']

#     def get_query(self):
#         columns = self._get_columns()
#         headers = self._get_headers(columns)

#         # Sum totals
#         inner_query = """
#             SELECT
#                 t.team_id,
#                 g2.game_id,
#                 {tg_sum_headers},
#                 {tgo_sum_headers}
#             FROM public.team t, public.game g, public.team_game_stats tg, public.team_game_stats_opponent tgo, public.game_boxscore b, public.game g2
#             WHERE
#                 tg.game_id = g.game_id AND
#                 tg.team_id = t.team_id AND
#                 b.game_id = g.game_id AND
#                 tgo.game_id = g.game_id AND
#                 tgo.team_id = t.team_id AND
#                 (t.team_id = g.away_team_id or t.team_id = g.home_team_id) AND -- makes sure we only grab the right historical games
#                 (g2.away_team_id = t.team_id or g2.home_team_id = t.team_id) AND -- makes sure we grab the right game to look back at
#                 g.date < g2.date -- we get ALL the previous games before.. this will let us calculate the season total up to that point
#             GROUP BY t.team_id, g2.game_id, g2.date
#         """.format(tg_sum_headers=self._get_agg_headers(columns, table='tg', agg_prefix=''), tgo_sum_headers=self._get_agg_headers(columns, table='tgo', agg_prefix='opp_'))

#         # join in player table so i can get add player information
#         query = """
#             SELECT
#                 iq.team_id,
#                 iq.game_id,
#                 tr.season,
#                 tr.date,
#                 tr.wins,
#                 tr.losses,
#                 tr.games_played,
#                 tr.win_perc,
#                 tr.last_10_perc,
#                 tr.last_5_perc,
#                 metrics.sos,
#                 {eps} as eps,
#                 {ortg} as ortg,
#                 {drtg} as drtg,
#                 {tg_headers},
#                 {tgo_headers}
#             FROM ({inner_query}) iq, in_season_team_record tr, public.in_season_team_metrics metrics
#             WHERE
#                 iq.game_id = tr.game_id AND
#                 iq.team_id = tr.team_id AND
#                 metrics.team_id = iq.team_id AND
#                 metrics.game_id = iq.game_id
#         """.format(tg_headers=self._get_headers(columns, table='iq', agg_prefix=''), tgo_headers=self._get_headers(columns, table='iq', agg_prefix='opp_', prefix='opp_'), inner_query=inner_query, eps=calculate_eps('iq'), ortg=calculate_ortg('iq'), drtg=calculate_drtg('iq'))

#         return query