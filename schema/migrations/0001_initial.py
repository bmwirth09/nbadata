# Generated by Django 5.1.4 on 2025-01-05 05:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('player_id', models.IntegerField(primary_key=True, serialize=False)),
                ('player_name', models.CharField(max_length=255, null=True)),
                ('college', models.CharField(max_length=255, null=True)),
                ('country', models.CharField(max_length=255, null=True)),
                ('draft_year', models.SmallIntegerField(null=True)),
                ('draft_round', models.SmallIntegerField(null=True)),
                ('draft_number', models.SmallIntegerField(null=True)),
            ],
            options={
                'db_table': 'player',
            },
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('season_id', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'season',
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('team_id', models.IntegerField(primary_key=True, serialize=False)),
                ('abbreviation', models.CharField(max_length=255)),
                ('nickname', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('yearfounded', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'team',
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('game_id', models.IntegerField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('season', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='schema.season')),
                ('away_team', models.ForeignKey(db_column='team_id_away', on_delete=django.db.models.deletion.CASCADE, related_name='away_games', to='schema.team')),
                ('home_team', models.ForeignKey(db_column='team_id_home', on_delete=django.db.models.deletion.CASCADE, related_name='home_games', to='schema.team')),
                ('loser_team', models.ForeignKey(db_column='team_id_loser', on_delete=django.db.models.deletion.CASCADE, related_name='games_lost', to='schema.team')),
                ('winner_team', models.ForeignKey(db_column='team_id_winner', on_delete=django.db.models.deletion.CASCADE, related_name='games_won', to='schema.team')),
            ],
            options={
                'db_table': 'game',
            },
        ),
        migrations.CreateModel(
            name='ShotChartDetail',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('period', models.SmallIntegerField()),
                ('minutes_remaining', models.SmallIntegerField()),
                ('seconds_remaining', models.SmallIntegerField()),
                ('game_event_id', models.IntegerField()),
                ('event_type', models.CharField(max_length=50)),
                ('action_type', models.CharField(max_length=50)),
                ('shot_type', models.CharField(max_length=50)),
                ('shot_zone_basic', models.CharField(max_length=50)),
                ('shot_zone_area', models.CharField(max_length=50)),
                ('shot_zone_range', models.CharField(max_length=50)),
                ('shot_distance', models.FloatField()),
                ('loc_x', models.FloatField()),
                ('loc_y', models.FloatField()),
                ('shot_attempted_flag', models.BooleanField()),
                ('shot_made_flag', models.BooleanField()),
                ('htm', models.CharField(max_length=255)),
                ('vtm', models.CharField(max_length=255)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schema.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schema.player')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schema.season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schema.team')),
            ],
            options={
                'db_table': 'shot_chart_detail',
                'unique_together': {('player', 'game', 'period', 'minutes_remaining', 'seconds_remaining')},
            },
        ),
        migrations.CreateModel(
            name='PlayerGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fgm', models.SmallIntegerField(default=0)),
                ('fga', models.SmallIntegerField(default=0)),
                ('fg3m', models.SmallIntegerField(default=0)),
                ('fg3a', models.SmallIntegerField(default=0)),
                ('fg_pct', models.FloatField(default=0)),
                ('ftm', models.SmallIntegerField(default=0)),
                ('fta', models.SmallIntegerField(default=0)),
                ('ft_pct', models.FloatField(default=0)),
                ('oreb', models.SmallIntegerField(default=0)),
                ('dreb', models.SmallIntegerField(default=0)),
                ('reb', models.SmallIntegerField(default=0)),
                ('ast', models.SmallIntegerField(default=0)),
                ('stl', models.SmallIntegerField(default=0)),
                ('blk', models.SmallIntegerField(default=0)),
                ('blka', models.SmallIntegerField(default=0)),
                ('tov', models.SmallIntegerField(default=0)),
                ('pts', models.SmallIntegerField(default=0)),
                ('min', models.SmallIntegerField(default=0)),
                ('pf', models.FloatField(default=0)),
                ('pfd', models.FloatField(default=0)),
                ('plus_minus', models.SmallIntegerField(default=0)),
                ('nba_fantasy_pts', models.FloatField(default=0)),
                ('dd2', models.FloatField(default=0)),
                ('td3', models.FloatField(default=0)),
                ('wl', models.CharField(max_length=1)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schema.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schema.player')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schema.season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schema.team')),
            ],
            options={
                'db_table': 'player_game_log',
                'unique_together': {('player', 'game')},
            },
        ),
    ]
