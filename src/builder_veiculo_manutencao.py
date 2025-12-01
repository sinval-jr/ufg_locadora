from datetime import date

# -----------------------------------------------------------------
# CLASSES DE ENTIDADE
# -----------------------------------------------------------------
class Veiculo:
    def __init__(self, placa, modelo, status, kmatual, valor_diaria, preco_por_km, id=None):
        self._id = id
        self._placa = placa
        self._modelo = modelo
        self._status = status
        self._kmatual = kmatual
        self._valor_diaria = valor_diaria
        self._preco_por_km = preco_por_km 

    @property
    def id(self):
        return self._id

    @property
    def placa(self):
        return self._placa
    
    @property
    def modelo(self):
        return self._modelo

    @property
    def status(self):
        return self._status
    
    @property
    def kmatual(self):
        return self._kmatual

    @property
    def valor_diaria(self):
        return self._valor_diaria
        
    @property
    def preco_por_km(self):
        return self._preco_por_km

    @valor_diaria.setter
    def valor_diaria(self, novo_valor):
        if novo_valor > 0:
            self._valor_diaria = novo_valor
        else:
            raise ValueError("O valor da diária deve ser positivo.")

    @status.setter
    def status(self, novo_status):
        status_veiculo = ["disponivel", "reservado", "alugado", "manutencao", "indisponivel"]
        if novo_status.lower() in status_veiculo:
            self._status = novo_status.lower()
        else:
            raise ValueError("Status inválido!")

    @kmatual.setter
    def kmatual(self, novo_km):
        if novo_km >= self._kmatual:
            self._kmatual = novo_km
        else:
            raise ValueError("Nova kilometragem menor que a anterior")

class Manutencao:
    def __init__(self, veiculo: Veiculo, descricao: str, data_inicio: date, custo: float = 0.0, id: int = None):
        self._id = id
        self._veiculo = veiculo
        self._descricao = descricao
        self._data_inicio = data_inicio
        self._data_fim = None  
        self._custo = custo
        self._status = "em andamento" 

    @property
    def id(self):
        return self._id

    @property
    def data_manutencao(self):
        return self._data_manutencao
    
    @property
    def custo(self):
        return self._custo

    @data_manutencao.setter
    def data_manutencao(self, nova_data):
        if isinstance(nova_data, date):
            self._data_manutencao = nova_data
        else:
            raise TypeError("A data de manutenção deve ser um objeto datetime.date.")

    @custo.setter
    def custo(self, novo_custo):
        if novo_custo >= 0:
            self._custo = novo_custo
        else:
            raise ValueError("O custo não pode ser negativo.")
    
    def iniciar(self):
        """ Coloca o veículo em manutenção. """
        if self._veiculo.status != "disponivel":
            raise ValueError(f"Veículo {self._veiculo.placa} não está disponível para manutenção (Status: {self._veiculo.status}).")
        
        self._status = "em andamento"
        self._veiculo.status = "manutencao"
        print(f"Veículo {self._veiculo.placa} enviado para manutenção.")

    def concluir(self, data_conclusao: date, custo_final: float):
        """ Conclui a manutenção e libera o veículo. """
        if self._status != "em andamento":
            raise ValueError("Esta manutenção já foi concluída.")
            
        self._status = "concluida"
        self._data_fim = data_conclusao
        self._custo = custo_final
        
        # Libera o veículo
        self._veiculo.status = "disponivel"
        print(f"Manutenção (ID: {self.id}) concluída. Veículo {self._veiculo.placa} está 'disponivel'.")
