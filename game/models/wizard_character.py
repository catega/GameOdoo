from odoo import models, fields, api
import random
import string

def name_generator(self):
    letters = list(string.ascii_lowercase)
    first = list(string.ascii_uppercase)
    vocals = ['a','e','i','o','u','y','']
    name = random.choice(first)
    for i in range(0,random.randint(3,5)):
        name = name+random.choice(letters)+random.choice(vocals)
    return name

class wizard_character(models.TransientModel):
    _name = 'game.wizard_character'

    # Global
    name = fields.Char(default=name_generator, required=True)

    def _default_player(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))

    player_leader = fields.Many2one('res.partner', default=_default_player, domain="[('is_player', '=', True)]", readonly=True)
    region = fields.Many2one('game.region')
    # Skills
    mining_level = fields.Integer(default=1)
    hunting_level = fields.Integer(default=1)
    gathering_level = fields.Integer(default=1)

    state = fields.Selection([('global', 'Global'), ('skills', 'Skills')], default='global')


    def crear_character(self):
        self.env['game.character'].create({
            'name': self.name,
            'player_leader': self.player_leader.id,
            'region': self.region.id,
            'mining_level': self.mining_level,
            'hunting_level': self.hunting_level,
            'gathering_level': self.gathering_level
        })

    def next(self):
        if self.state == 'global':
            self.state = 'skills'

        return {
            'name': "Character Wizard",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'game.wizard_character',
            'res_id': self.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def previous(self):
        if self.state == 'skills':
            self.state = 'global'

        return {
            'name': "Character Wizard",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'game.wizard_character',
            'res_id': self.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }



