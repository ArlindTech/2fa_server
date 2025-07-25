from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import json


class AMO2FAController(http.Controller):

    @http.route('/amo_2fa/request_2fa', type='json', auth='public', methods=['POST'], csrf=False)
    def request_2fa(self, **kw):
        data = request.get_json_data()
        token = data.get('token')
        client_name = data.get('client_name')
        username = data.get('username')

        if not all([token, client_name, username]):
            return {'error': 'Missing parameters'}

        # akseson odoo user dhe injorojm access rights per te kerkuar username e perdorusit
        user = request.env['res.users'].sudo().search([('login', '=', username)], limit=1)
        if not user:
            return {
                'status': 'error',
                'message': 'User not found'
            }

        # krijojm record te ri me kto param
        request.env['amo.2fa.request'].sudo().create({
            'token': token,
            'client_name': client_name,
            'username': username
        })
        expiration = datetime.now() + timedelta(minutes=120)
        return {
            'status': 'success',
            'message': '2FA request created',
            'expiration': expiration.isoformat()
        }
    @http.route('/amo_2fa/check_status', type='json', auth='public', methods=['POST'], csrf=False)
    def check_status(self, **kw):
        data = json.loads(request.httprequest.data)
        token = data.get('token')
        client_name = data.get('client_name')
        username = data.get('username')

        if not all([token, client_name, username]):
            return {
                'status': 'error',
                'message': 'Missing parameters'
            }
        # kerkon per request qe i pershtatet te trejave
        record = request.env['amo.2fa.request'].sudo().search([
            ('token', '=', token),
            ('client_name', '=', client_name),
            ('username', '=', username)
        ], limit=1)

        if not record:
            return {
                'status': 'error',
                'message': 'Request not found'
            }
        return {
            'status': record.status,
            'expiration': record.expiration.isoformat(),
            'created_date': record.create_date.isoformat()
        }
