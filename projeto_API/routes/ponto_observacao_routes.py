from flask import Blueprint

from controllers.ponto_observacao_controller import (
    listar_pontos,
    buscar_ponto,
)


ponto_observacao_bp = Blueprint(
    "ponto_observacao",
    __name__,
    url_prefix="/api/pontos-observacao",
)

ponto_observacao_bp.add_url_rule(
    "",
    view_func=listar_pontos,
    methods=["GET"],
)

ponto_observacao_bp.add_url_rule(
    "/<int:ponto_observacao_id>",
    view_func=buscar_ponto,
    methods=["GET"],
)
