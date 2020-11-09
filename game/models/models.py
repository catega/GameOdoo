# -*- coding: utf-8 -*-

from odoo import models, fields, api


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
    mining_level = fields.Integer(default=1);
    hunting_level = fields.Integer(default=1);
    gathering_level = fields.Integer(default=1);


class region(models.Model):
    _name = 'game.region'
    _description = 'game.region'

    name = fields.Char()
    fortress_level = fields.Integer(default=0, compute='_get_fortress_level')
    max_characters = fields.Integer(default=0, compute='_get_max_characters')
    leader = fields.Many2one('game.player')
    leader_clan = fields.Many2one('game.clan', compute='_get_leader_clan')
    characters = fields.One2many('game.character', 'region')

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
