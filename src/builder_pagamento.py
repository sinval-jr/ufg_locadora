class Pagamento:
    def __init__(self, metodo, valor, data_pagamento, tipo="inicial", id=None):
        self._id = id
        self._metodo = metodo
        self._valor = valor
        self._data_pagamento = data_pagamento
        self._tipo = tipo

    def __repr__(self):
        return f"Pagamento({self._tipo}: R$ {self._valor:.2f} via {self._metodo})"
    
    @property
    def tipo(self):
        return self._tipo
    
    @property
    def valor(self):
        return self._valor
