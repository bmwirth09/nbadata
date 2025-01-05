from django.db import models

# Create your models here.

class Season(models.Model):
    season_id = models.IntegerField(primary_key=True)

    class Meta:
        db_table = 'season'

class Team(models.Model):
    team_id = models.IntegerField(primary_key=True)
    abbreviation = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    yearfounded = models.CharField(max_length=255)

    def __unicode__(self):
        return self.abbreviation

    class Meta:
        db_table = 'team'


class Player(models.Model):
    player_id = models.IntegerField(primary_key=True)
    player_name = models.CharField(null=True, max_length=255)
    college = models.CharField(null=True, max_length=255)
    country = models.CharField(null=True, max_length=255)
    draft_year = models.SmallIntegerField(null=True)
    draft_round = models.SmallIntegerField(null=True)
    draft_number = models.SmallIntegerField(null=True)

    def __unicode__(self):
        return u"#{player_id} {name}".format(player_id=self.player_id, name=self.player_name)

    class Meta:
        db_table = 'player'


class Game(models.Model):
    game_id = models.IntegerField(primary_key=True)
    home_team = models.ForeignKey(Team, db_column='team_id_home', on_delete=models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey(Team, db_column='team_id_away', on_delete=models.CASCADE, related_name='away_games')
    winner_team = models.ForeignKey(Team, db_column='team_id_winner', on_delete=models.CASCADE, related_name='games_won')
    loser_team = models.ForeignKey(Team, db_column='team_id_loser', on_delete=models.CASCADE, related_name='games_lost')
    date = models.DateField()
    season = models.ForeignKey(Season, null=True, on_delete=models.CASCADE)

    def __unicode__(self):
        return '#{game_id} {away_team} @ {home_team} ({date})'.format(date=self.date.strftime("%m/%d/%Y"), home_team=self.home_team, away_team=self.away_team, game_id=self.game_id)

    class Meta:
        db_table = 'game'

class BasePlayerStats(models.Model):
    fgm = models.SmallIntegerField(default=0)
    fga = models.SmallIntegerField(default=0)
    fg_pct = models.FloatField(default=0)
    fg3m = models.SmallIntegerField(default=0)
    fg3a = models.SmallIntegerField(default=0)
    fg_pct = models.FloatField(default=0)
    ftm = models.SmallIntegerField(default=0)
    fta = models.SmallIntegerField(default=0)
    ft_pct = models.FloatField(default=0)
    oreb = models.SmallIntegerField(default=0)
    dreb = models.SmallIntegerField(default=0)
    reb = models.SmallIntegerField(default=0)
    ast = models.SmallIntegerField(default=0)
    stl = models.SmallIntegerField(default=0)
    blk = models.SmallIntegerField(default=0)
    blka = models.SmallIntegerField(default=0)
    tov = models.SmallIntegerField(default=0)
    pts = models.SmallIntegerField(default=0)

    class Meta:
        abstract = True

class PlayerGame(BasePlayerStats):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    min = models.SmallIntegerField(default=0)
    pf = models.FloatField(default=0)
    pfd = models.FloatField(default=0)
    plus_minus = models.SmallIntegerField(default=0)
    nba_fantasy_pts = models.FloatField(default=0)
    dd2 = models.FloatField(default=0)
    td3 = models.FloatField(default=0)
    wl = models.CharField(max_length=1)

    class Meta:
        unique_together = ('player', 'game')
        db_table = 'player_game_log'

class ShotChartDetail(models.Model):
    id = models.IntegerField(primary_key=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    period = models.SmallIntegerField()
    minutes_remaining = models.SmallIntegerField()
    seconds_remaining = models.SmallIntegerField()
    game_event_id = models.IntegerField()
    event_type = models.CharField(max_length=50)
    action_type = models.CharField(max_length=50)
    shot_type = models.CharField(max_length=50)
    shot_zone_basic = models.CharField(max_length=50)
    shot_zone_area = models.CharField(max_length=50)
    shot_zone_range = models.CharField(max_length=50)
    shot_distance = models.FloatField()
    loc_x = models.FloatField()
    loc_y = models.FloatField()
    shot_attempted_flag = models.BooleanField()
    shot_made_flag = models.BooleanField()
    htm = models.CharField(max_length=255)
    vtm = models.CharField(max_length=255)


    class Meta:
        unique_together = ('player', 'game', 'period', 'minutes_remaining', 'seconds_remaining')
        db_table = 'shot_chart_detail'



# class BoxScore(models.Model):
#     game = models.OneToOneField(Game)
#     home_score = models.SmallIntegerField()
#     away_score = models.SmallIntegerField()
#     winner = models.ForeignKey(Team, null=True, blank=True, related_name='games_won')

#     def __unicode__(self):
#         if self.home_score > self.away_score:
#             winner_score, loser_score = self.home_score, self.away_score
#         else:
#             winner_score, loser_score = self.away_score, self.home_score
#         return '#{id} {winner} (W{winner_score}-{loser_score})'.format(id=self.id, winner=self.winner, winner_score=winner_score, loser_score=loser_score)
