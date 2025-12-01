class Pagamento:
    def __init__(self, metodo, valor, data_pagamento, tipo="inicial", id=None):
        self.__id = id
        self.__metodo = metodo
        self.__valor = valor
        self.__data_pagamento = data_pagamento
        self.__tipo = tipo

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def metodo(self):
        return self.__metodo

    @property
    def valor(self):
        return self.__valor

    @property
    def tipo(self):
        return self.__tipo
    
    @property
    def data_pagamento(self):
        return self.__data_pagamento

    def __repr__(self):
        return f"Pagamento({self.__tipo}: R$ {self.__valor:.2f} via {self.__metodo})"
