from odoo import models, fields, api
from datetime import timedelta
import secrets
from odoo.exceptions import UserError


class Amo2faRequest(models.Model):
    _name = "amo.2fa.request"
    _description = "2FA Request"

    user_id = fields.Many2one('res.users', string='User', required=False)

    token = fields.Char(
        string="Token",
        required=True,
        copy=False,
        default=lambda self: secrets.token_urlsafe(16)
    )
    expiration = fields.Datetime(
        string="Expiration",
        required=True,
        default=lambda self: fields.Datetime.now() + timedelta(minutes=1)
    )
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('canceled', 'Canceled'),
    ], string="Status", default='pending', required=True)
    client_name = fields.Char(string="Client Name", required=True)
    username = fields.Char(string="Username", required=True)
    create_date = fields.Datetime(string='Created On', default=fields.Datetime.now, readonly=True)

    @api.model
    def create(self, vals):
        if 'token' not in vals:
            vals['token'] = secrets.token_urlsafe(24)
        if 'expiration' not in vals:
            vals['expiration'] = fields.Datetime.now() + timedelta(minutes=1)
        return super().create(vals)

    def approve(self):
        self.write({
            'status': 'approved',
            'expiration': fields.Datetime.now() + timedelta(minutes=1)
        })

    @api.model
    def auto_expire_tokens(self):
        now = fields.Datetime.now()
        expired_requests = self.search([
            ('status', 'in', ['pending', 'approved']),
            ('expiration', '<=', now)
        ])
        if expired_requests:
            expired_requests.write({'status': 'canceled'})

    def action_approve(self):
        for rec in self:
            rec.status = 'approved'

    def action_reject(self):
        for rec in self:
            rec.status = 'canceled'

    def action_send_request(self):
        payload = {'username': self.username, 'password': self.password}
        response = self.env['ir.http'].session_json('/amo_2fa_client/send_request', payload)
        if response.get('status') == 'success':
            self.write({'token': response['token'], 'status': 'pending'})
        else:
            raise UserError('Error: %s' % response.get('message'))

    def action_check_status(self):
        payload = {'token': self.token, 'username': self.username}
        response = self.env['ir.http'].session_json('/amo_2fa_client/check_status', payload)
        if response.get('status') == 'approved':
            self.write({
                'status': 'approved',
                'expiration': response.get('expiration')
            })
        elif response.get('status') == 'pending':
            self.status = 'pending'
        else:
            raise UserError('Error: %s' % response.get('message'))