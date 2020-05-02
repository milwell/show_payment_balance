# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    applied_state = fields.Selection(selection=[('unapplied', 'Unapplied'),('partial', 'Partial'),('full', 'Full')],
        string='Applied', store=True, readonly=True, copy=False, tracking=True, compute='_compute_amount'
    )

    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
        readonly=True, store=True,
        help='Utility field to express amount currency'
    )
    is_company_currency = fields.Boolean(compute="_is_company_currency")

    # # === Amount fields ===
    amount_residual = fields.Monetary(string='To Apply', store=True, compute='_compute_amount', currency_field = 'company_currency_id')
    amount_residual_company = fields.Monetary(string='To Apply (Company)', compute='_compute_amount', currency_field = 'company_currency_id')
    amount_residual_currency = fields.Monetary(string='To Apply', store=True, compute='_compute_amount')


    @api.depends('company_currency_id','currency_id')
    def _is_company_currency(self):
        for p in self:
            if p.currency_id == False:
                p.is_company_currency = True
            else:
                p.is_company_currency = p.company_currency_id == p.currency_id

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
                total_residual_currency = 0.0
                currencies = set()
                for line in payment.move_line_ids:
                    if line.account_id.user_type_id.type in ('receivable', 'payable'):
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency

                payment.amount_residual = abs(total_residual)
                payment.amount_residual_currency = abs(total_residual_currency)
                payment.amount_residual_company = payment.amount_residual

                if payment.state == 'posted':
                    if payment.currency_id != payment.company_currency_id:
                        if payment.amount > payment.amount_residual_currency:
                            payment.applied_state = 'partial'
                        else:
                            payment.applied_state = 'full'
                    else:
                        if payment.amount > payment.amount_residual:
                            payment.applied_state = 'partial'
                        else:
                            payment.applied_state = 'full'
                else:
                    payment.applied_state = 'unapplied'
            else:
                payment.amount_residual_company = 0