from odoo.addons.l10n_ar_withholding_ux.hooks import (
    deactivate_pending_tax_payment_views,
)


def migrate(cr, version):
    deactivate_pending_tax_payment_views(cr)
