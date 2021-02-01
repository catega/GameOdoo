# -*- coding: utf-8 -*-
import random
import string
from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


def name_generator(self):
    letters = list(string.ascii_lowercase)
    first = list(string.ascii_uppercase)
    vocals = ['a','e','i','o','u','y','']
    name = random.choice(first)
    for i in range(0,random.randint(3,5)):
        name = name+random.choice(letters)+random.choice(vocals)
    return name


class player(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'
    _description = 'res.partner'

    photo = fields.Image(max_width=120, max_height=120)
    #name = fields.Char()
    is_player = fields.Boolean(default=True)
    race = fields.Selection([('1', 'Hombre lobo'), ('2', 'Vampiro')], required=True)
    level = fields.Integer(default=1)
    points = fields.Integer()
    won_battles = fields.Integer(default=0)
    lost_battles = fields.Integer(default=0)
    percent_battles = fields.Integer(default=0, compute='_get_percent_battles')
    time = fields.Char()
    description = fields.Text()
    regions = fields.One2many('game.region', 'leader')
    enemy_regions = fields.Many2many('game.region', compute="_get_enemy_regions")
    available_regions = fields.Many2many('game.region', compute="_get_available_regions")
    clan = fields.Many2one('game.clan')
    characters = fields.One2many('game.character', 'player_leader')
    active_travels = fields.One2many('game.travel', 'player')
    image_small = fields.Image(max_width=50, max_height=50, related='photo', string='Image Small', store=True)
    battle_status = fields.Selection(
        [('1', 'Rookie'), ('2', 'Soldier'), ('3', 'Captain'), ('4', 'General'), ('5', 'Warlord')], default='1')
    player_changes = fields.One2many('game.player_changes', 'player')

    _sql_constraints = [('name_uniq', 'unique(name)', 'Name already in use')]

    # Plenar player_changes
    @api.depends('won_battles', 'lost_battles')
    def _get_percent_battles(self):
        for p in self:
            total = p.won_battles + p.lost_battles
            p.percent_battles = (p.won_battles * 100) / total
    # Fer tamé el filtro de regions sense player
    def filter_regions(self, r, p):
        if r.fortress_level != 0:
            if r.leader.race != p.race:
                return True
            else:
                return False

        return False

    def _get_enemy_regions(self):
        for p in self:
            e_regions = self.env['game.region'].search([]).filtered(lambda r: self.filter_regions(r, p))
            p.enemy_regions = e_regions.ids

    def filter_available_regions(self, r):
        if r.fortress_level == 0:
            return True
        return False

    def _get_available_regions(self):
        for p in self:
            a_regions = self.env['game.region'].search([]).filtered(lambda r: self.filter_available_regions(r))
            p.available_regions = a_regions.ids

class clan(models.Model):
    _name = 'game.clan'
    _description = 'game.clan'

    name = fields.Char()
    level = fields.Integer(default=1, readonly=True)
    members = fields.One2many('res.partner', 'clan')
    #regions = fields.One2many('game.region', 'leader_clan', compute='_get_regions')
    alliances = fields.Many2many('game.alliance')

    @api.depends('members')
    def _get_regions(self):
        for c in self:
            if c.members:
                for m in c.members:
                    c.regions += m.regions

class character(models.Model):
    _name = 'game.character'
    _description = 'game.character'

    name = fields.Char(default=name_generator)
    level = fields.Integer(default=1)
    player_leader = fields.Many2one('res.partner', domain="[('is_player', '=', True)]")
    region = fields.Many2one('game.region')
    health = fields.Integer(default=50)
    attack = fields.Integer(default=lambda self : self.random_generator(1, 3))
    defense = fields.Integer(default=lambda self: self.random_generator(1, 3))
    speed = fields.Integer(default=lambda self: self.random_generator(1, 3))
    defeated = fields.Boolean(default=False)
    mining_level = fields.Integer(default=1)
    hunting_level = fields.Integer(default=1)
    gathering_level = fields.Integer(default=1)

    @api.model
    def random_generator(self, a, b):
        return random.randint(a, b)

    @api.onchange('player_leader')
    def _onchange_player(self):
        return {
            'domain': {'region': [('leader', '=', self.player_leader.id)]}
        }

    @api.onchange('level')
    def _levelUp_stats(self):
        for c in self:
            c.health = 40 + (c.level * 10)
            # Cambiar lo dels stats
            c.attack = c.attack + 1
            c.defense = c.defense + 1
            c.speed = c.speed + 1

# Cambiar la creació de characters desde botó así
class region(models.Model):
    _name = 'game.region'
    _description = 'game.region'

    name = fields.Char(default=name_generator)
    fortress_level = fields.Integer(default=0, compute='_get_fortress_level')
    max_characters = fields.Integer(default=0, compute='_get_max_characters')
    leader = fields.Many2one('res.partner', domain="[('is_player', '=', True)]")
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

# Falta ajustar per a que agarre recursos depenent dels characters i el seu level de arreplegar cada uno
    def calculate_production(self):
        for p in self:
            if p.leader:
                new_iron = p.iron_production * 0.01
                new_wood = p.wood_production * 0.01
                new_food = p.food_production * 0.01
                new_gold = p.gold_production * 0.01

                final_iron = p.iron + new_iron
                final_wood = p.wood + new_wood
                final_food = p.food + new_food
                final_gold = p.gold + new_gold

                p.write({
                    'iron': final_iron,
                    'wood': final_wood,
                    'food': final_food,
                    'gold': final_gold
                })

    @api.model
    def update_resources(self):
        print("-----------Update--------------")
        regions = self.env['game.region'].search([])
        regions.calculate_production()

# travel són les batalles
class travel(models.Model):
    _name = 'game.travel'
    _description = 'game.travel'

    name = fields.Char(default='Travel', compute='_get_travel_name')
    player = fields.Many2one('res.partner', domain="[('is_player', '=', True)]")
    player2 = fields.Many2one('res.partner', domain="[('is_player', '=', True)]")
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

    @api.constrains('travel_duration', 'origin_region')
    def _check_food(self):
        for t in self:
            if t.travel_duration > t.origin_region.food:
                raise ValidationError('Not enough food. '
                                      '\nYou must have ' + str(t.travel_duration) + ' food to do this travel. '
                                      '\nCurrent food: ' + str(t.origin_region.food))

    @api.depends('travel_duration')
    def _get_battle_time(self):
        for t in self:
            t.battle_time = fields.Datetime.from_string(t.launch_time) + timedelta(minutes=t.travel_duration)

            passed = fields.Datetime.from_string(t.battle_time) - datetime.now()

            t.time_remaining = (100 * passed.seconds) / (t.travel_duration * 60)
            if t.time_remaining > 100:
                t.time_remaining = 0
                t.name += ' [FINISHED]'

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

    def turn(self, a, b):
        if (a.attack + 10) < b.defense:
            b.health = b.health - 1
        else:
            b.health = b.health - ((a.attack + 10) - b.defense)

        if b.health < 0:
            b.health = 0
            b.defeated = True

    def removeDefeated(self, a):
        alive = []
        for c in a:
            if not c.defeated:
                alive.append(c)

        return alive


    def checkChars(self, a):
        if len(a) is 0:
            return False

        for c in a:
            if not c.defeated:
                return True

        return False

    def fight(self, a, b):
        rd = True

        while not a.defeated and not b.defeated:
            if rd:
                self.turn(a, b)
            else:
                self.turn(b, a)

            if rd:
                rd = False
            else:
                rd = True

    # Acabar
    def battle(self):
        for t in self:
            at_chars = t.origin_region.characters
            def_chars = t.destiny_region.characters
            rounds = 0
            contA = 0
            contB = 0

            if len(at_chars) > len(def_chars):
                rounds = len(def_chars) - 1
            else:
                rounds = len(at_chars) - 1

            while self.checkChars(at_chars) and self.checkChars(def_chars):
                for f in range(0, rounds):
                    while not at_chars[contA].defeated and not def_chars[contB].defeated:
                        self.fight(at_chars[contA], def_chars[contB])

                    if self.checkChars(at_chars) and self.checkChars(def_chars):
                        at_chars = self.removeDefeated(at_chars)
                        def_chars = self.removeDefeated(def_chars)

                        if contA >= len(at_chars) - 1:
                            contA = 0
                        else:
                            contA = contA + 1

                        if contB >= len(def_chars) - 1:
                            contB = 0
                        else:
                            contB = contB + 1

                if len(at_chars) >= len(def_chars):
                    rounds = len(def_chars)
                else:
                    rounds = len(at_chars)

            if self.checkChars(at_chars):
                t.player.won_battles = t.player.won_battles + 1
                t.playe2.lost_battles = t.player2.lost_battles + 1
                # Cambiar la regió
            else:
                t.player.lost_battles = t.player.lost_battles + 1
                t.playe2.won_battles = t.player2.won_battles + 1






class player_changes(models.Model):
    _name = 'game.player_changes'
    _description = 'game.player_changes'

    name = fields.Char()
    player = fields.Many2one('res.partner', ondelete='cascade', required=True)
    percent = fields.Integer()
    time = fields.Char()

class alliance(models.Model):
    _name = 'game.alliance'
    _description = 'game.alliance'

    name = fields.Char()
    clans = fields.Many2many('game.clan')