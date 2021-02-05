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

    def _default_region(self):
        return self.env['game.region'].browse(self._context.get('active_id'))

    player_leader = fields.Many2one('res.partner', default=_default_player, domain="[('is_player', '=', True)]", readonly=True)
    region = fields.Many2one('game.region', default=_default_player, readonly=True)
    # Stats
    health = fields.Integer(default=50)
    attack = fields.Integer(default=lambda self : self.random_generator(1, 3))
    defense = fields.Integer(default=lambda self: self.random_generator(1, 3))
    speed = fields.Integer(default=lambda self: self.random_generator(1, 3))
    # Skills
    mining_level = fields.Integer(default=1)
    hunting_level = fields.Integer(default=1)
    gathering_level = fields.Integer(default=1)

    state = fields.Selection([('global', 'Global'), ('skills', 'Skills'), ('stats', 'Stats')], default='global')


    def crear_character(self):
        character = self.env['game.character'].create({
            'name': self.name,
            'player_leader': self.player_leader.id,
            'region': self.region.id,
            'health': self.health,
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'mining_level': self.mining_level,
            'hunting_level': self.hunting_level,
            'gathering_level': self.gathering_level
        })

        return {
            'name': "Travel Preview",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'game.character',
            'res_id': character.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def next(self):
        if self.state == 'global':
            self.state = 'skills'
        elif self.state == 'skills':
            self.state = 'stats'

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
        if self.state == 'stats':
            self.state = 'skills'
        elif self.state == 'skills':
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

    @api.model
    def random_generator(self, a, b):
        return random.randint(a, b)


    @api.depends('player_leader')
    def _onchange_player(self):
        return {
            'domain': {'region': [('leader', '=', self.player_leader.id)]}
        }

    def _levelUp_stats(self):
        for c in self:
            c.health = 40 + (c.level * 10)
            # Cambiar lo dels stats
            c.attack = c.attack + 1
            c.defense = c.defense + 1
            c.speed = c.speed + 1





