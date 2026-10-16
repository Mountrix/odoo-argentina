import logging

_logger = logging.getLogger(__name__)


def deactivate_pending_tax_payment_views(env_or_cr):
    """Drop leftover l10n_ar_tax payment inherits until that module loads.

    l10n_ar_tax auto-installs and can write its account.payment inherit first.
    Combined-arch validation of this module then sees buttons/fields that
    only exist on the tax model.
    """
    cr = getattr(env_or_cr, "cr", env_or_cr)
    cr.execute(
        """
        UPDATE ir_ui_view
           SET active = false
         WHERE model = 'account.payment'
           AND arch_db::text LIKE %s
        """,
        ["%action_l10n_ar_payment_withholding_tree%"],
    )
    _logger.info(
        "l10n_ar_withholding_ux: deactivated %s leftover tax payment view(s)",
        cr.rowcount,
    )


def pre_init_hook(env_or_cr):
    deactivate_pending_tax_payment_views(env_or_cr)
