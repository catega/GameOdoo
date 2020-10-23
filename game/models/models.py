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
    fortresses = fields.One2many('game.fortress', 'leader')
    clan = fields.Many2one('game.clan')

class fortress(models.Model):
    _name = 'game.fortress'
    _description = 'game.fortress'

    name = fields.Char()
    level = fields.Integer()
    max_characters = fields.Integer()
    leader = fields.Many2one('game.player', ondelete='cascade')

class clan(models.Model):
    _name = 'game.clan'
    _description = 'game.clan'

    name = fields.Char()
    level = fields.Integer()
    members = fields.One2many('game.player', 'clan')
