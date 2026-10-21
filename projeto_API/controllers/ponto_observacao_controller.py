from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError

from config.sessao import obter_sessao, encerrar_sessao
from services.ponto_observacao_service import PontoObservacaoService


def listar_pontos():
    sessao = obter_sessao()

    try:
        servico = PontoObservacaoService(sessao)
        pontos = servico.listar_todos()

        resultado = [
            {
                "ponto_observacao_id": ponto.ponto_observacao_id,
                "nome": ponto.nome,
                "latitude": float(ponto.latitude),
                "longitude": float(ponto.longitude),
                "cidade": ponto.cidade,
                "estado": ponto.estado,
            }
            for ponto in pontos
        ]

        return jsonify(resultado), 200

    except SQLAlchemyError:
        sessao.rollback()
        return jsonify({
            "erro": "Não foi possível consultar os pontos de observação."
        }), 500

    finally:
        encerrar_sessao(sessao)

def buscar_ponto(ponto_observacao_id: int):
    sessao = obter_sessao()

    try:
        servico = PontoObservacaoService(sessao)
        ponto = servico.buscar_por_id(ponto_observacao_id)

        resultado = {
            "ponto_observacao_id": ponto.ponto_observacao_id,
            "nome": ponto.nome,
            "latitude": float(ponto.latitude),
            "longitude": float(ponto.longitude),
            "cidade": ponto.cidade,
            "estado": ponto.estado,
        }

        return jsonify(resultado), 200

    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 404

    except SQLAlchemyError:
        sessao.rollback()
        return jsonify({
            "erro": "Não foi possível consultar o ponto de observação."
        }), 500

    finally:
        encerrar_sessao(sessao)
