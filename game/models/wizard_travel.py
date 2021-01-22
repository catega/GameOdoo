from odoo import models, fields, api
from datetime import datetime, timedelta

class wizard_travel(models.TransientModel):
    _name = 'game.wizard_travel'


    name = fields.Char(default='Travel', compute='_get_travel_name')
    launch_time = fields.Datetime(default=lambda t: fields.Datetime.now(), readonly=True)
    battle_time = fields.Datetime(compute='_get_battle_time')
    travel_duration = fields.Integer(default=0, compute='_get_travel_duration')
    time_remaining = fields.Float(compute='_get_battle_time')

    def _default_player(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))

    # Player 1
    player = fields.Many2one('res.partner', default=_default_player, domain="[('is_player', '=', True)]", readonly=True)
    origin_region = fields.Many2one('game.region')
    # Player 2
    player2 = fields.Many2one('res.partner', domain="[('is_player', '=', True)]")
    destiny_region = fields.Many2one('game.region', ondelete='restrict')


    state = fields.Selection([('player1', 'Player 1'), ('player2', 'Player 2'), ('name', 'Name')], default='player1')


    def crear_travel(self):
        self.env['game.travel'].create({
            'name': self.name,
            'player': self.player.id,
            'player2': self.player2.id,
            'launch_time': self.launch_time,
            'battle_time': self.battle_time,
            'origin_region': self.origin_region.id,
            'destiny_region': self.destiny_region.id,
            'travel_duration': self.travel_duration,
            'time_remaining': self.time_remaining
        })

    def next(self):
        if self.state == 'player1':
            self.state = 'player2'
        elif self.state == 'player2':
            self.state = 'name'


        return {
            'name': "Travel Wizard",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'game.wizard_travel',
            'res_id': self.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def previous(self):
        if self.state == 'player2':
            self.state = 'player1'
        elif self.state == 'name':
            self.state = 'player2'

        return {
            'name': "Travel Wizard",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'game.wizard_travel',
            'res_id': self.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

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
            t.travel_duration = ((((t.destiny_region.pos_x - t.origin_region.pos_x) ** 2) + (
                        (t.destiny_region.pos_y - t.origin_region.pos_y) ** 2)) ** 0.5)

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