# =================================================================
# CLASSE DE SERVIÇO DE PREVISÕES (SIMPLIFICADA)
# Usa Média Móvel (Moving Average - MA) para previsões multi-step
# =================================================================
from typing import List, Dict, Any, Union

class PrevisoesService:
    
    def __init__(self, janela: int = 3):
        """ 
        Inicializa o serviço de previsão com o tamanho da janela de Média Móvel (MA).
        """
        self.janela = janela

    def prever(self, dados: list[float], num_previsoes_int: int) -> List[float]:
        """ 
        Recebe uma lista de floats e o número de previsões, e retorna uma lista 
        de previsões futuras usando Média Móvel (MA) de forma recursiva.
        
        Args:
            dados (list[float]): A série temporal histórica.
            num_previsoes_int (int): O número de previsões futuras a gerar.
            
        Returns:
            List[float]: Uma lista contendo as previsões geradas.
        """
        
        # 1. Validação de dados (Mínimo para calcular a primeira média)
        if not dados:
            return [] # Retorna lista vazia se não houver dados
        
        if len(dados) < self.janela:
            # Em um ambiente real, lançaríamos uma HTTPException
            raise ValueError(f"Mínimo de {self.janela} dados necessários para a janela. Fornecidos: {len(dados)}.")
        
        if num_previsoes_int <= 0:
            return []
            
        # 2. Inicialização dos dados de trabalho
        # Cria uma cópia dos dados para adicionar as previsões futuras sem alterar os originais
        dados_trabalho = list(dados)
        previsoes_geradas = []

        # 3. Geração das previsões (Loop Multi-Step)
        for _ in range(num_previsoes_int):
            
            # Pega os últimos 'janela' dados (incluindo previsões anteriores, se houver)
            dados_para_media = dados_trabalho[-self.janela:]
            
            # Calcula a Média Móvel (próxima previsão)
            proxima_previsao = sum(dados_para_media) / self.janela
            
            # Adiciona a previsão à lista de resultados
            previsoes_geradas.append(proxima_previsao)
            
            # Adiciona a previsão de volta aos dados de trabalho para calcular a próxima previsão (recursão)
            dados_trabalho.append(proxima_previsao)
            
        # Retorna a lista completa de previsões
        return [round(p, 2) for p in previsoes_geradas] # Arredonda para 2 casas decimais

# Inicializa e exporta a instância do serviço para uso no Controller.
# Se for usar Suavização Exponencial, você deve mudar o valor da janela.
servico_previsoes = PrevisoesService(janela=3)
