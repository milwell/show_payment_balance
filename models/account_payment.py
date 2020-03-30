# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    applied_state = fields.Selection(selection=[('unapplied', 'Unapplied'),('partial', 'Partial'),('full', 'Full')],
        string='Applied', store=True, readonly=True, copy=False, tracking=True, compute='_compute_amount')

    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
        readonly=True, store=True,
        help='Utility field to express amount currency')       

    # # === Amount fields ===
    amount_residual = fields.Monetary(string='To Apply', store=True,compute='_compute_amount')

    @api.depends(
        'state',
        'move_line_ids.currency_id',
        'move_line_ids.amount_residual',
        'move_line_ids.amount_residual_currency')
    def _compute_amount(self):
        # invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
        for payment in self:
            if not payment.state in ['draft','cancelled']:
                total_residual = 0.0
                currencies = set()
                for line in payment.move_line_ids:
                    if line.currency_id:
                        currencies.add(line.currency_id)

                    if line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                


                payment.amount_residual = total_residual

                currency = len(currencies) == 1 and currencies.pop() or payment.company_id.currency_id
                is_applied = currency and currency.is_zero(payment.amount_residual) or not payment.amount_residual

                if payment.state == 'posted' and is_applied:
                    if payment.amount_residual > 0:
                        payment.applied_state = 'partial'
                    else:
                        payment.applied_state = 'full'
                else:
                    payment.applied_state = 'unapplied'