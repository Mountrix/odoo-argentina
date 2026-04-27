import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Generalizacion del cleanup iniciado en 19.0.1.6.0.

    En 19.0.1.6.0 se orfanaron explicitamente algunos `account.account.tag`
    que ya no se distribuyen en el modulo pero pueden estar en uso en DBs
    migradas. La lista era hardcoded y dejo afuera, por ejemplo,
    `tag_tax_jurisdiccion_924` (y otros `tag_tax_jurisdiccion_*` provinciales),
    lo que provoca un FK violation en `_process_end` al intentar eliminar
    el tag mientras esta referenciado por
    `account_account_tag_account_tax_repartition_line_rel`.

    Este script orfana de manera generica TODOS los `ir_model_data` del modulo
    `l10n_ar_ux` que apunten a `account.account.tag` y esten siendo usados
    por al menos un tax repartition line. Los tags y sus referencias quedan
    intactos en la DB; solo se rompe el vinculo con el modulo para que Odoo
    no intente eliminarlos.
    """
    cr.execute(
        """
        SELECT d.id, d.name, d.res_id
        FROM ir_model_data d
        WHERE d.module = 'l10n_ar_ux'
          AND d.model = 'account.account.tag'
          AND d.res_id IN (
              SELECT DISTINCT account_account_tag_id
              FROM account_account_tag_account_tax_repartition_line_rel
          )
        """
    )
    rows = cr.fetchall()
    if not rows:
        return
    ids_to_drop = [r[0] for r in rows]
    names = [f"l10n_ar_ux.{r[1]} (tag id={r[2]})" for r in rows]
    _logger.info(
        "Orfanando %s ir_model_data de l10n_ar_ux.account.account.tag en uso: %s",
        len(ids_to_drop), ", ".join(names),
    )
    cr.execute("DELETE FROM ir_model_data WHERE id IN %s", (tuple(ids_to_drop),))
