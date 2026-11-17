from abc import ABC, abstractmethod
from typing import List
import json
import os
import streamlit as st

# ==========================================
# 1. ABSTRAÇÃO E ENCAPSULAMENTO (MODELO)
# ==========================================

class Veiculo(ABC):
    def __init__(self, placa: str, modelo: str, ano: int, valor_diaria: float):
        self._placa = self._validar_placa(placa)
        self._modelo = modelo
        self._ano = self._validar_ano(ano)
        self._valor_diaria = self._validar_valor_diaria(valor_diaria)
        self.__quilometragem = 0.0
        self.__disponivel = True

    @property
    def placa(self) -> str:
        return self._placa

    @property
    def modelo(self) -> str:
        return self._modelo

    @property
    def ano(self) -> int:
        return self._ano

    @property
    def quilometragem(self) -> float:
        return self.__quilometragem

    @property
    def disponivel(self) -> bool:
        return self.__disponivel

    def registrar_quilometragem(self, km: float) -> None:
        if km <= 0:
            raise ValueError("A quilometragem a ser adicionada deve ser maior que zero.")
        self.__quilometragem += km

    def definir_quilometragem_inicial(self, km: float) -> None:
        self.__quilometragem = km

    def alterar_status_disponibilidade(self, status: bool) -> None:
        self.__disponivel = status

    @staticmethod
    def _validar_placa(placa: str) -> str:
        if not placa or len(placa.strip()) < 7:
            raise ValueError("Placa inválida. O formato deve conter pelo menos 7 caracteres.")
        return placa.upper().strip()

    @staticmethod
    def _validar_ano(ano: int) -> int:
        if ano < 1900 or ano > 2030:
            raise ValueError("Ano do veículo fora do intervalo permitido (1900-2030).")
        return ano

    @staticmethod
    def _validar_valor_diaria(valor: float) -> float:
        if valor <= 0:
            raise ValueError("O valor da diária deve ser maior que zero.")
        return valor

    @abstractmethod
    def calcular_custo_locacao(self, dias: int) -> float:
        pass

    @abstractmethod
    def obter_detalhes_especificos(self) -> str:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass


# ==========================================
# 2. HERANÇA E ESPECIALIZAÇÃO
# ==========================================

class Carro(Veiculo):
    def __init__(self, placa: str, modelo: str, ano: int, valor_diaria: float, quantidade_portas: int):
        super().__init__(placa, modelo, ano, valor_diaria)
        self.quantidade_portas = quantidade_portas

    def calcular_custo_locacao(self, dias: int) -> float:
        return (self._valor_diaria * dias) + (15.0 * dias)

    def obter_detalhes_especificos(self) -> str:
        return f"Tipo: Carro | Portas: {self.quantidade_portas}"

    def to_dict(self) -> dict:
        return {
            "tipo": "Carro", "placa": self.placa, "modelo": self.modelo,
            "ano": self.ano, "valor_diaria": self._valor_diaria,
            "quilometragem": self.quilometragem, "disponivel": self.disponivel,
            "quantidade_portas": self.quantidade_portas
        }


class Caminhao(Veiculo):
    def __init__(self, placa: str, modelo: str, ano: int, valor_diaria: float, capacidade_carga_ton: float):
        super().__init__(placa, modelo, ano, valor_diaria)
        self.capacidade_carga_ton = capacidade_carga_ton

    def calcular_custo_locacao(self, dias: int) -> float:
        taxa_carga = self.capacidade_carga_ton * 30.0
        return (self._valor_diaria * dias) + (taxa_carga * dias)

    def obter_detalhes_especificos(self) -> str:
        return f"Tipo: Caminhão | Capacidade de Carga: {self.capacidade_carga_ton}t"

    def to_dict(self) -> dict:
        return {
            "tipo": "Caminhao", "placa": self.placa, "modelo": self.modelo,
            "ano": self.ano, "valor_diaria": self._valor_diaria,
            "quilometragem": self.quilometragem, "disponivel": self.disponivel,
            "capacidade_carga_ton": self.capacidade_carga_ton
        }


class Moto(Veiculo):
    def __init__(self, placa: str, modelo: str, ano: int, valor_diaria: float, cilindradas: int):
        super().__init__(placa, modelo, ano, valor_diaria)
        self.cilindradas = cilindradas

    def calcular_custo_locacao(self, dias: int) -> float:
        subtotal = self._valor_diaria * dias
        return subtotal * 0.90

    def obter_detalhes_especificos(self) -> str:
        return f"Tipo: Moto | Cilindradas: {self.cilindradas}cc"

    def to_dict(self) -> dict:
        return {
            "tipo": "Moto", "placa": self.placa, "modelo": self.modelo,
            "ano": self.ano, "valor_diaria": self._valor_diaria,
            "quilometragem": self.quilometragem, "disponivel": self.disponivel,
            "cilindradas": self.cilindradas
        }


# ==========================================
# 3. CONTROLADOR POLIMÓRFICO E PERSISTÊNCIA
# ==========================================

class FrotaController:
    def __init__(self, arquivo_json: str = "frota_dados.json"):
        self._arquivo_json = arquivo_json
        self._veiculos: List[Veiculo] = []
        self.carregar_do_arquivo()

    @property
    def veiculos(self) -> List[Veiculo]:
        return self._veiculos

    def adicionar_veiculo(self, veiculo: Veiculo) -> None:
        for v in self._veiculos:
            if v.placa == veiculo.placa:
                raise ValueError(f"Já existe um veículo cadastrado com a placa {veiculo.placa}.")
        self._veiculos.append(veiculo)
        self.salvar_no_arquivo()

    def buscar_veiculo(self, placa: str) -> Veiculo:
        for v in self._veiculos:
            if v.placa == placa.upper():
                return v
        raise KeyError(f"Veículo com a placa '{placa}' não foi encontrado.")

    def salvar_no_arquivo(self) -> None:
        dados = [v.to_dict() for v in self._veiculos]
        with open(self._arquivo_json, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

    def carregar_do_arquivo(self) -> None:
        if not os.path.exists(self._arquivo_json):
            return
        try:
            with open(self._arquivo_json, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self._veiculos.clear()
                for item in dados:
                    tipo = item.get("tipo")
                    placa = item.get("placa")
                    modelo = item.get("modelo")
                    ano = item.get("ano")
                    diaria = item.get("valor_diaria")
                    km = item.get("quilometragem", 0.0)
                    disponivel = item.get("disponivel", True)

                    veiculo = None
                    if tipo == "Carro":
                        veiculo = Carro(placa, modelo, ano, diaria, item.get("quantidade_portas"))
                    elif tipo == "Caminhao":
                        veiculo = Caminhao(placa, modelo, ano, diaria, item.get("capacidade_carga_ton"))
                    elif tipo == "Moto":
                        veiculo = Moto(placa, modelo, ano, diaria, item.get("cilindradas"))

                    if veiculo:
                        veiculo.definir_quilometragem_inicial(km)
                        veiculo.alterar_status_disponibilidade(disponivel)
                        self._veiculos.append(veiculo)
        except Exception:
            pass


# ==========================================
# 4. INTERFACE WEB COM STREAMLIT
# ==========================================

def main():
    st.set_page_config(page_title="Sistema de Gestão de Frota", page_icon="🚗", layout="wide")

    if "controller" not in st.session_state:
        st.session_state.controller = FrotaController()

    controller = st.session_state.controller

    st.title("🚗 Sistema de Gestão de Frota de Veículos")
    st.markdown("Aplicação desenvolvida com **Orientação a Objetos** e interface web em Streamlit.")

    menu = st.sidebar.selectbox(
        "Navegação", 
        ["Relatório Geral da Frota", "Cadastrar Novo Veículo", "Simular Orçamento de Locação", "Registrar Quilometragem"]
    )

    if menu == "Relatório Geral da Frota":
        st.subheader("📋 Relatório Geral da Frota (Polimorfismo em Ação)")
        if not controller.veiculos:
            st.info("Nenhum veículo cadastrado no momento.")
        else:
            for v in controller.veiculos:
                with st.expander(f"[{v.placa}] {v.modelo} ({v.ano}) - {'Disponível' if v.disponivel else 'Locado'}"):
                    st.write(f"**Detalhes Específicos:** {v.obter_detalhes_especificos()}")
                    st.write(f"**Quilometragem Atual:** {v.quilometragem} km")
                    st.write(f"**Valor da Diária Base:** R$ {v._valor_diaria:.2f}")

    elif menu == "Cadastrar Novo Veículo":
        st.subheader("➕ Cadastro de Novo Veículo")
        tipo_veiculo = st.selectbox("Selecione o Tipo de Veículo", ["Carro", "Caminhão", "Moto"])
        
        with st.form("form_cadastro"):
            col1, col2 = st.columns(2)
            with col1:
                placa = st.text_input("Placa (ex: ABC1234)")
                modelo = st.text_input("Modelo")
            with col2:
                ano = st.number_input("Ano", min_value=1900, max_value=2030, value=2023)
                diaria = st.number_input("Valor da Diária (R$)", min_value=1.0, value=100.0)

            campo_especifico = 0
            if tipo_veiculo == "Carro":
                campo_especifico = st.number_input("Quantidade de Portas", min_value=2, max_value=5, value=4)
            elif tipo_veiculo == "Caminhão":
                campo_especifico = st.number_input("Capacidade de Carga (Toneladas)", min_value=0.5, value=15.0)
            elif tipo_veiculo == "Moto":
                campo_especifico = st.number_input("Cilindradas (cc)", min_value=50, value=250)

            submitted = st.form_submit_button("Cadastrar Veículo")
            if submitted:
                try:
                    if tipo_veiculo == "Carro":
                        novo = Carro(placa, modelo, int(ano), float(diaria), int(campo_especifico))
                    elif tipo_veiculo == "Caminhão":
                        novo = Caminhao(placa, modelo, int(ano), float(diaria), float(campo_especifico))
                    elif tipo_veiculo == "Moto":
                        novo = Moto(placa, modelo, int(ano), float(diaria), int(campo_especifico))

                    controller.adicionar_veiculo(novo)
                    st.success(f"Veículo de placa `{novo.placa}` cadastrado e salvo com sucesso!")
                except ValueError as e:
                    st.error(f"Erro de Validação: {e}")

    elif menu == "Simular Orçamento de Locação":
        st.subheader("💰 Simulação Polimórfica de Locação")
        dias = st.number_input("Quantidade de Dias de Locação", min_value=1, value=5)
        
        if st.button("Calcular Orçamento para Toda a Frota"):
            if not controller.veiculos:
                st.warning("Não há veículos cadastrados para simulação.")
            else:
                st.markdown(f"### Resultados para {dias} dia(s):")
                for v in controller.veiculos:
                    custo = v.calcular_custo_locacao(dias)
                    st.info(f"**[{v.placa}] {v.modelo}** ({v.obter_detalhes_especificos()}) -> **Custo Total: R$ {custo:.2f}**")

    elif menu == "Registrar Quilometragem":
        st.subheader("🛣️ Atualizar Quilometragem")
        if not controller.veiculos:
            st.info("Nenhum veículo cadastrado.")
        else:
            placas_disponiveis = [v.placa for v in controller.veiculos]
            placa_escolhida = st.selectbox("Selecione a Placa do Veículo", placas_disponiveis)
            
            veiculo_selecionado = controller.buscar_veiculo(placa_escolhida)
            st.write(f"**Modelo:** {veiculo_selecionado.modelo} | **KM Atual:** {veiculo_selecionado.quilometragem} km")
            
            km_adicionar = st.number_input("Quilometragem a Adicionar", min_value=0.1, value=100.0)
            if st.button("Salvar Nova Quilometragem"):
                try:
                    veiculo_selecionado.registrar_quilometragem(km_adicionar)
                    controller.salvar_no_arquivo()
                    st.success(f"Quilometragem atualizada! Total: {veiculo_selecionado.quilometragem} km")
                except ValueError as e:
                    st.error(f"Erro: {e}")

if __name__ == "__main__":
    main()
