# -*- coding: utf-8 -*-
import random
import string
from datetime import datetime, timedelta

from odoo import models, fields, api

def name_generator(self):
    letters = list(string.ascii_lowercase)
    first = list(string.ascii_uppercase)
    vocals = ['a','e','i','o','u','y','']
    name = random.choice(first)
    for i in range(0,random.randint(3,5)):
        name = name+random.choice(letters)+random.choice(vocals)
    return name


class player(models.Model):
    _name = 'game.player'
    _description = 'game.player'

    photo = fields.Image(max_width=120, max_height=120)
    name = fields.Char()
    race = fields.Selection([('1', 'Hombre lobo'), ('2', 'Vampiro')])
    level = fields.Integer(default=1)
    points = fields.Integer()
    won_battles = fields.Integer(default=0)
    lost_battles = fields.Integer(default=0)
    percent_battles = fields.Integer(default=0, compute='_get_percent_battles')
    time = fields.Char()
    description = fields.Text()
    regions = fields.One2many('game.region', 'leader')
    clan = fields.Many2one('game.clan')
    characters = fields.One2many('game.character', 'player_leader')
    active_travels = fields.One2many('game.travel', 'player')
    image_small = fields.Image(max_width=50, max_height=50, related='photo', string='Image Small', store=True)
    battle_status = fields.Selection(
        [('1', 'Rookie'), ('2', 'Soldier'), ('3', 'Captain'), ('4', 'General'), ('5', 'Warlord')], default='1')
    player_changes = fields.One2many('game.player_changes', 'player')
    # Plenar player_changes

    @api.depends('won_battles', 'lost_battles')
    def _get_percent_battles(self):
        for p in self:
            total = p.won_battles + p.lost_battles
            p.percent_battles = (p.won_battles * 100) / total

class clan(models.Model):
    _name = 'game.clan'
    _description = 'game.clan'

    name = fields.Char()
    level = fields.Integer(default=1, readonly=True)
    members = fields.One2many('game.player', 'clan')
    regions = fields.One2many('game.region', 'leader_clan', compute='_get_regions')

    @api.depends('members')
    def _get_regions(self):
        for c in self:
            if c.members:
                for m in c.members:
                    c.regions += m.regions

class character(models.Model):
    _name = 'game.character'
    _description = 'game.character'

    name = fields.Char()
    level = fields.Integer(default=1)
    player_leader = fields.Many2one('game.player', readonly=True)
    region = fields.Many2one('game.region')
    mining_level = fields.Integer(default=1)
    hunting_level = fields.Integer(default=1)
    gathering_level = fields.Integer(default=1)


class region(models.Model):
    _name = 'game.region'
    _description = 'game.region'

    name = fields.Char(default=name_generator)
    fortress_level = fields.Integer(default=0, compute='_get_fortress_level')
    max_characters = fields.Integer(default=0, compute='_get_max_characters')
    leader = fields.Many2one('game.player')
    leader_clan = fields.Many2one('game.clan', compute='_get_leader_clan')
    characters = fields.One2many('game.character', 'region')
    mines = fields.Integer(default=lambda self : self.random_generator(1, 5))
    forests = fields.Integer(default=lambda self : self.random_generator(1, 5))
    villages = fields.Integer(default=lambda self : self.random_generator(1, 5))
    cities = fields.Integer(default=lambda self : self.random_generator(0, 3))
    iron_production = fields.Integer(default=0, compute='_get_resources')
    wood_production = fields.Integer(default=0, compute='_get_resources')
    food_production = fields.Integer(default=0, compute='_get_resources')
    gold_production = fields.Integer(default=0, compute='_get_resources')
    iron = fields.Integer(default=0)
    wood = fields.Integer(default=0)
    food = fields.Integer(default=0)
    gold = fields.Integer(default=0)
    pos_x = fields.Integer(default=lambda self : self.random_generator(-100, 100))
    pos_y = fields.Integer(default=lambda self : self.random_generator(-100, 100))

    @api.depends('leader')
    def _get_leader_clan(self):
        for r in self:
            r.leader_clan = r.leader.clan

    @api.depends('leader')
    def _get_fortress_level(self):
        for r in self:
            if r.fortress_level == 0 and r.leader:
                r.fortress_level = 1

    @api.depends('fortress_level')
    def _get_max_characters(self):
        for r in self:
            r.max_characters = r.fortress_level * 5

    @api.depends('mines', 'forests', 'villages', 'cities')
    def _get_resources(self):
        for r in self:
            r.iron_production = 100 * r.mines
            r.wood_production = 100 * r.forests
            r.food_production = 100 * (r.villages + r.cities)
            r.gold_production = (10 * r.mines) + (100 * r.cities)

    @api.model
    def random_generator(self, a, b):
        return random.randint(a, b)

    @api.model
    def update_resources(self):
        print("-----------Update--------------")
        #regions = self.env['game.region'].search([])
        #regions.calculate_production()

# travel són les batalles
class travel(models.Model):
    _name = 'game.travel'
    _description = 'game.travel'

    name = fields.Char(default='Travel', compute='_get_travel_name')
    player = fields.Many2one('game.player')
    player2 = fields.Many2one('game.player')
    launch_time = fields.Datetime(default=lambda t: fields.Datetime.now(), readonly=True)
    battle_time = fields.Datetime(compute='_get_battle_time')
    origin_region = fields.Many2one('game.region', required=True, ondelete='restrict')
    destiny_region = fields.Many2one('game.region', required=True, ondelete='restrict')
    travel_duration = fields.Integer(default=0, compute='_get_travel_duration')
    time_remaining = fields.Float(compute='_get_battle_time')

    @api.depends('origin_region', 'destiny_region', 'player')
    def _get_travel_name(self):
        for t in self:
            if t.player.name is False or t.origin_region.name is False or t.destiny_region.name is False:
                t.name = "Travel name"
            else:
                t.name = str(t.player.name) + " : " + str(t.origin_region.name) + " -> " + str(t.destiny_region.name)

    @api.depends('origin_region', 'destiny_region')
    def _get_travel_duration(self):
        for t in self:
                t.travel_duration = ((((t.destiny_region.pos_x - t.origin_region.pos_x)**2) + ((t.destiny_region.pos_y - t.origin_region.pos_y)**2))**0.5)

                if t.travel_duration < 30:
                    t.travel_duration = 30

    @api.depends('travel_duration')
    def _get_battle_time(self):
        for t in self:
            t.battle_time = fields.Datetime.from_string(t.launch_time) + timedelta(minutes=t.travel_duration)

            passed = fields.Datetime.from_string(t.battle_time) - datetime.now()

            t.time_remaining = (100 * passed.seconds) / (t.travel_duration * 60)
            if t.time_remaining > 100:
                t.time_remaining = 0
                t.name += ' FINISHED'

    @api.onchange('player')
    def _onchange_player1(self):
        if self.player2:
            if self.player.id == self.player2.id:
                self.player = False
                return {
                    'warning': {
                        'title': "Players must be different",
                        'message': "Player 1 is the same as Player 2",
                    }
                }
        return {
            'domain': {'origin_region': [('leader', '=', self.player.id)],
                       'player2': [('id', '!=', self.player.id)]},
        }

    @api.onchange('player2')
    def _onchange_player2(self):
        if self.player:
            if self.player.id == self.player2.id:
                self.player2 = False
                return {
                    'warning': {
                        'title': "Players must be different",
                        'message': "Player 1 is the same as Player 2",
                    }
                }
        return {
            'domain': {'destiny_region': [('leader', '=', self.player2.id)],
                       'player1': [('id', '!=', self.player2.id)]},
        }


class player_changes(models.Model):
    _name = 'game.player_changes'
    _description = 'game.player_changes'

    name = fields.Char()
    player = fields.Many2one('game.player', ondelete='cascade', required=True)
    percent = fields.Integer()
    time = fields.Char()