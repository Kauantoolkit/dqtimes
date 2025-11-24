from fastapi import FastAPI, Query, HTTPException, status, Form
from tutorialPy.services.previsoes_service import PrevisoesService
from typing import List
import json
from tutorialPy.services.meu_servico import Minha_Classe
from tutorialPy.services.meu_servico import Minha_Classe
from tutorialPy.services.previsoes_service import PrevisoesService
from tutorialPy.models import Exemplo1Response, Exemplo2Response


# =================================================================
# FUNÇÃO AUXILIAR PARA CONVERTER STRING EM INTEIRO
# =================================================================

def str_to_int(text: str) -> int:
    """
    Mapeia palavras que representam números para seus valores inteiros.
    Retorna -1 para strings não mapeadas.
    """
    mapping = {
        "um": 1, "dois": 2, "três": 3, "quatro": 4, "cinco": 5,
        "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10
    }
    return mapping.get(text.lower(), -1)


# =================================================================
# CONFIGURAÇÃO DA APLICAÇÃO FASTAPI
# =================================================================

app = FastAPI(
    title="Microserviço Xablau",
    description="API da quinta-feira",
    version="2.9.9",
)

# NOTE: Pressupõe-se que Minha_Classe e PrevisoesService existam.
# Se esses serviços não estiverem disponíveis, o código não rodará.
try:
    servico = Minha_Classe()
    servico_previsoes = PrevisoesService()
except NameError:
    # Cria mocks simples para que o código compile se as classes não existirem
    class MockService:
        def exemplo_variaveis_tipos(self): return {"conceito": "mock", "explicacao": "mock", "exemplos": {}}

        def exemplo_performance_for(self, iteracoes): return {"conceito": "mock", "explicacao": "mock",
                                                              "parametros": {"iteracoes": iteracoes,
                                                                             "operacao": "mock"}, "resultados": {
                "for_normal": {"tempo_segundos": 0.0, "codigo_exemplo": "mock"},
                "list_comprehension": {"tempo_segundos": 0.0, "codigo_exemplo": "mock"}},
                                                              "analise": {"mais_rapido": "mock",
                                                                          "diferenca_percentual": 0.0,
                                                                          "conclusao": "mock"},
                                                              "verificacao": {"resultados_iguais": True,
                                                                              "tamanho_resultado": 0}}


    class MockPrevisoesService:
        def prever(self, dados: List[float], num_previsoes_int: int): return [d * 1.1 for d in
                                                                              dados[-num_previsoes_int:]]


    servico = MockService()
    servico_previsoes = MockPrevisoesService()


# =================================================================
# ENDPOINTS
# =================================================================

@app.get("/exemplo1", response_model=Exemplo1Response)
def exemplo1() -> Exemplo1Response:
    """
    Exemplo simples de retorno de variáveis e tipos.
    """
    resultado = servico.exemplo_variaveis_tipos()
    return Exemplo1Response(**resultado)


@app.get("/exemplo2", response_model=Exemplo2Response)
def exemplo2(
        iteracoes: int = Query(
            default=10000,
            ge=1,
            le=1000000,
            description="Número de itens do loop para teste de performance"
        )
) -> Exemplo2Response:
    """
    Executa um teste de performance comparando diferentes estruturas de loop.
    """
    resultado = servico.exemplo_performance_for(iteracoes)
    return Exemplo2Response(**resultado)


@app.post("/previsao", response_model=dict, status_code=status.HTTP_200_OK)
def previsao(
        # NOTE: O campo 'dados' agora é passado como string no corpo do formulário.
        # O usuário DEVE inserir uma string JSON válida (ex: [1.0, 2.0, 3.0]).
        dados_str: str = Form(
            ...,
            description="Lista de valores float para previsão (Série Temporal). DEVE ser uma string JSON válida, ex: [1.0, 2.0, 3.0]"
        ),
        num_previsoes: str = Form(
            "dois",
            description="Número de previsões desejadas em formato de texto (ex: 'dois', 'três', 'cinco')"
        )
) -> dict:
    """
    Endpoint para realizar previsões múltiplas com base em dados de séries temporais.
    O número de previsões e os dados são passados como campos de formulário.
    """

    # 1. Tenta converter a string JSON de dados para List[float]
    try:
        request_dados: List[float] = json.loads(dados_str)
        if not isinstance(request_dados, list) or not all(isinstance(x, (int, float)) for x in request_dados):
            raise ValueError("O campo de dados não é uma lista válida de números.")
        if not request_dados:
            raise ValueError("A lista de dados deve conter pelo menos um valor.")

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "mensagem": "Erro de formatação.",
                "detalhe": "O campo 'dados' deve ser uma string JSON (lista de floats) válida."
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "mensagem": "Erro de validação nos dados.",
                "detalhe": str(e)
            }
        )

    # 2. Converte o número de previsões
    num_previsoes_int = str_to_int(num_previsoes)

    if num_previsoes_int <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "mensagem": "Valor de 'num_previsoes' inválido.",
                "detalhe": f"Não foi possível converter '{num_previsoes}' em número válido. "
                           "Use palavras como 'um', 'dois', 'três', 'cinco', etc."
            }
        )

    # 3. Executa o serviço de previsão
    try:
        previsoes = servico_previsoes.prever(
            dados=request_dados,
            num_previsoes_int=num_previsoes_int
        )

        return {
            "status": "sucesso",
            "metodo": "Média Móvel (MA) Multi-Step",
            "num_previsoes_solicitadas": num_previsoes_int,
            "previsoes": previsoes,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "mensagem": "Erro de validação nos dados ou parâmetros.",
                "detalhe": str(e)
            }
        )


# =================================================================
# EXECUÇÃO LOCAL
# =================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
