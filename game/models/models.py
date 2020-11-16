# -*- coding: utf-8 -*-
import random
import string

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
    description = fields.Text()
    regions = fields.One2many('game.region', 'leader')
    clan = fields.Many2one('game.clan')
    characters = fields.One2many('game.character', 'player_leader')
    image_small = fields.Image(max_width=50, max_height=50, related='photo', string='Image Small', store=True)

class clan(models.Model):
    _name = 'game.clan'
    _description = 'game.clan'

    name = fields.Char()
    level = fields.Integer(default=1)
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
    player_leader = fields.Many2one('game.player')
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
    mines = fields.Integer(default=random.randint(1, 5))
    forests = fields.Integer(default=random.randint(1, 5))
    villages = fields.Integer(default=random.randint(1, 5))
    cities = fields.Integer(default=random.randint(0, 3))
    iron_production = fields.Integer(default=0, compute='_get_resources')
    wood_production = fields.Integer(default=0, compute='_get_resources')
    food_production = fields.Integer(default=0, compute='_get_resources')
    gold_production = fields.Integer(default=0, compute='_get_resources')
    iron = fields.Integer(default=0)
    wood = fields.Integer(default=0)
    food = fields.Integer(default=0)
    gold = fields.Integer(default=0)

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

class travel(models.Model):
    _name = 'game.travel'
    _description = 'game.travel'

    name = fields.Char(compute='_get_travel_name')
    player = fields.Many2one('game.player')
    launch_time = fields.Datetime(default=lambda t: fields.Datetime.now())
    origin_region = fields.Many2one('game.region')
    destiny_region = fields.Many2one('game.region')

    @api.depends('origin_region', 'destiny_region', 'player')
    def _get_travel_name(self):
        for t in self:
            t.name = str(t.player.name) + " : " + str(t.origin_region.name) + " -> " + str(t.destiny_region.name)

