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
        for r in self:
            for m in self.members:
                r.regions += m.regions

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
    fortress_level = fields.Integer()
    max_characters = fields.Integer()
    leader = fields.Many2one('game.player')
    leader_clan = fields.Many2one('game.clan', compute='_get_leader_clan')
    characters = fields.One2many('game.character', 'region')

    @api.depends('leader')
    def _get_leader_clan(self):
        for r in self:
            r.leader_clan = r.leader.clan