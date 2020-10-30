# -*- coding: utf-8 -*-

from odoo import models, fields, api


class player(models.Model):
    _name = 'game.player'
    _description = 'game.player'

    photo = fields.Image(max_width='120')
    name = fields.Char()
    race = fields.Selection([('1', 'Hombre lobo'), ('2', 'Vampiro')])
    level = fields.Integer()
    points = fields.Integer()
    description = fields.Text()
    regions = fields.One2many('game.region', 'leader')
    clan = fields.Many2one('game.clan')
    characters = fields.One2many('game.character', 'player_leader')

class clan(models.Model):
    _name = 'game.clan'
    _description = 'game.clan'

    name = fields.Char()
    level = fields.Integer()
    members = fields.One2many('game.player', 'clan')

class character(models.Model):
    _name = 'game.character'
    _description = 'game.character'

    name = fields.Char()
    level = fields.Integer()
    player_leader = fields.Many2one('game.player')
    region = fields.Many2one('game.region')
    mining_level = fields.Integer();
    hunting_level = fields.Integer();
    gathering_level = fields.Integer();


class region(models.Model):
    _name = 'game.region'
    _description = 'game.region'

    name = fields.Char()
    base_level = fields.Integer()
    max_characters = fields.Integer()
    leader = fields.Many2one('game.player', ondelete='cascade')
    characters = fields.One2many('game.character', 'region')

