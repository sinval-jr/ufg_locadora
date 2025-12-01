from datetime import date

# -----------------------------------------------------------------
# CLASSES DE ENTIDADE
# -----------------------------------------------------------------
class Veiculo:
    def __init__(self, placa, modelo, status, kmatual, valor_diaria, preco_por_km, id=None):
        self.__id = id
        self.__placa = placa
        self.__modelo = modelo
        self.__status = status
        self.__kmatual = kmatual
        self.__valor_diaria = valor_diaria
        self.__preco_por_km = preco_por_km

    @property
    def id(self):
        return self.__id

    @property
    def placa(self):
        return self.__placa

    @property
    def modelo(self):
        return self.__modelo

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, novo_status):
        status_veiculo = ["disponivel", "reservado", "alugado", "manutencao", "indisponivel"]
        if novo_status.lower() in status_veiculo:
            self.__status = novo_status.lower()
        else:
            raise ValueError("Status inválido!")

    @property
    def kmatual(self):
        return self.__kmatual

    @kmatual.setter
    def kmatual(self, novo_km):
        if novo_km >= self.__kmatual:
            self.__kmatual = novo_km
        else:
            raise ValueError("Nova kilometragem menor que a anterior")

    @property
    def valor_diaria(self):
        return self.__valor_diaria

    @valor_diaria.setter
    def valor_diaria(self, novo_valor):
        if novo_valor > 0:
            self.__valor_diaria = novo_valor
        else:
            raise ValueError("O valor da diária deve ser positivo.")

    @property
    def preco_por_km(self):
        return self.__preco_por_km

# -----------------------------------------------------------------
class Manutencao:
    def __init__(self, veiculo: Veiculo, descricao: str, data_inicio: date, custo: float = 0.0, id: int = None):
        self.__id = id
        self.__veiculo = veiculo
        self.__descricao = descricao
        self.__data_inicio = data_inicio
        self.__data_fim = None
        self.__custo = custo
        self.__status = "em andamento"

    @property
    def id(self):
        return self.__id
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, novo_status):
        self.__status = novo_status.lower()

    @property
    def custo(self):
        return self.__custo
    
    @property
    def descricao(self):
        return self.__descricao
    
    @property
    def data_inicio(self):
        return self.__data_inicio
    
    @property
    def data_fim(self):
        return self.__data_fim

    @custo.setter
    def custo(self, novo_custo):
        if novo_custo >= 0:
            self.__custo = novo_custo
        else:
            raise ValueError("O custo não pode ser negativo.")

    def iniciar(self):
        if self.veiculo.status != "disponivel":
            raise ValueError(f"Veículo {self.veiculo.placa} não está disponível para manutenção (Status: {self.__veiculo.status}).")
        self.status = "em andamento"
        self.veiculo.status = "manutencao"
        print(f"Veículo {self.veiculo.placa} enviado para manutenção.")

    def concluir(self, data_conclusao: date, custo_final: float):
        if self.__status != "em andamento":
            raise ValueError("Esta manutenção já foi concluída.")
        self.__status = "concluida"
        self.__data_fim = data_conclusao
        self.__custo = custo_final
        self.veiculo.status = "disponivel"
        print(f"Manutenção (ID: {self.__id}) concluída. Veículo {self.__veiculo.placa} está 'disponivel'.")
