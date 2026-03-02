# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class ContractPortal(CustomerPortal):

    @http.route(['/my/contract/<int:contract_id>'], type='http', auth="public", website=True)
    def portal_contract_page(self, contract_id, access_token=None, **kw):
        """ This loads the white Portal Page for the customer """
        try:
            contract_sudo = self._document_check_access('engineering.contract', contract_id, access_token)
        except:
            return request.redirect('/my')

        values = {
            'contract': contract_sudo,
            'page_name': 'contract',
        }
        return request.render('engineering_contracts.portal_contract_template', values)

    @http.route(['/my/contract/<int:contract_id>/accept'], type='json', auth="public", website=True)
    def portal_contract_accept(self, contract_id, access_token=None, name=None, signature=None):
        """ This handles the signature when the customer clicks Accept & Sign """
        try:
            contract_sudo = self._document_check_access('engineering.contract', contract_id, access_token)
        except:
            return {'error': _('Invalid Token.')}

        if not signature:
            return {'error': _('Signature is missing.')}

        # Save the signature and change state to 'signed'
        contract_sudo.write({
            'signed_document_name': f"{name}_signature.png",
            'signed_document': signature,
            'signature_date': fields.Datetime.now(),
            'state': 'signed',
        })

        return {
            'force_refresh': True,
            'redirect_url': contract_sudo.get_portal_url(),
        }
