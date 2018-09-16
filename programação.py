from copy import deepcopy
from functools import reduce
from random import randint, shuffle, choices, choice


class Nó:
    def __init__(self, valor, raiz=True):
        self.valor = valor
        self.esquerda = None
        self.direita = None
        self._pontuação = None
        if raiz:
            self.esquerda = Nó(choice(TERMOS), raiz=False)
            self.direita = Nó(choice(TERMOS), raiz=False)

    def __deepcopy__(self, memodict):
        copy_object = Nó(self.valor)
        if self.valor not in TERMOS:
            copy_object.esquerda = deepcopy(self.esquerda)
            copy_object.direita = deepcopy(self.direita)
        return copy_object

    def sub_arvore_aleatória(self, raiz=True):
        tronco = lado = gene = None
        while gene is None:
            if self.valor in TERMOS:
                return tronco, lado, gene
            else:
                if randint(0, 100) < 5:
                    tronco = self
                    lado = choice(["esquerda", "direita"])
                    gene = getattr(tronco, lado)
                else:
                    tronco, lado, gene = choice(
                        [self.esquerda, self.direita]
                    ).sub_arvore_aleatória(False)
                    if not raiz:
                        return tronco, lado, gene
        return tronco, lado, gene

    @property
    def altura(self):
        if self.valor in TERMOS:
            return 0
        else:
            return 1 + max(self.esquerda.altura, self.direita.altura)

    @property
    def função(self):
        if self.valor in OPERADORES:
            return f"({self.esquerda.função}  {self.valor}  {self.direita.função})"
        else:
            return self.valor

    @property
    def pontuação(self):
        if self._pontuação is None:
            fitness = 0
            for x, y in zip(ENTRADAS, SAIDAS):
                try:
                    resultado = eval(self.função)
                except ZeroDivisionError:
                    return 9999999
                fitness += (y - resultado) ** 2
            fitness = fitness ** (1 / 2)
            self._pontuação = fitness
            return fitness
        else:
            return self._pontuação


def cruzar(individuo_a: dict, individuo_b: dict, mutação: bool):
    cromossomo_filho_a = deepcopy(individuo_a)
    cromossomo_filho_b = deepcopy(individuo_b)

    tronco_a, lado_a, gene_a = cromossomo_filho_a.sub_arvore_aleatória()
    tronco_b, lado_b, gene_b = cromossomo_filho_b.sub_arvore_aleatória()

    setattr(tronco_a, lado_a, gene_b)
    setattr(tronco_b, lado_b, gene_a)

    if mutação:
        mutar(cromossomo_filho_a)
        mutar(cromossomo_filho_b)

    return [cromossomo_filho_a, cromossomo_filho_b]


def mutar(cromossomo: Nó):
    tronco, lado, gene = cromossomo.sub_arvore_aleatória()
    setattr(tronco, lado, Nó(choice(OPERADORES)))


def gerar_individuo():
    return Nó(choice(OPERADORES))


def gerar_população(tamanho_população):
    return [gerar_individuo() for _ in range(tamanho_população)]


def calcular_media(população):
    return sum(individuo.pontuação for individuo in população) / len(população)


def buscar_melhor_adaptado(população):
    return reduce(lambda x, y: x if x.pontuação < y.pontuação else y, população)


def buscar_pior_adaptado(população):
    return reduce(lambda x, y: x if x.pontuação > y.pontuação else y, população)


def roleta(população, tamanho_população):
    pior = buscar_pior_adaptado(população)
    weights = [
        (abs(individuo.pontuação - pior.pontuação) ** 5) for individuo in população
    ]
    return choices(população, weights=weights, k=tamanho_população)


def executar(
    gerações, tamanho_população, taxa_mutação, cruzamento_por_geração, altura_maxima
):
    população = gerar_população(tamanho_população)
    melhor_adaptado_da_geração = buscar_melhor_adaptado(população)
    melhor_adaptado = melhor_adaptado_da_geração
    for geração in range(gerações):
        if geração % 10 == 0:
            print(f"geração: {geração}")
            print(f"média da população: {calcular_media(população)}")
            print(f"melhor adaptado: {melhor_adaptado.pontuação}")
            print(f"melhor adaptado da geração: {melhor_adaptado_da_geração.pontuação}")
            print("-----------------------------------------")
        shuffle(população)
        reprodutores = população[:cruzamento_por_geração]
        nova_população = [
            individuo for individuo in população if individuo not in reprodutores
        ]
        while reprodutores:
            mutação = randint(0, 100) <= taxa_mutação
            individuo_a = reprodutores.pop()
            individuo_b = reprodutores.pop()
            nova_população.append(individuo_a)
            nova_população.append(individuo_b)
            nova_população += cruzar(individuo_a, individuo_b, mutação)

        melhor_adaptado_da_geração = buscar_melhor_adaptado(nova_população)
        if melhor_adaptado_da_geração.pontuação < melhor_adaptado.pontuação:
            melhor_adaptado = melhor_adaptado_da_geração
        if melhor_adaptado.pontuação == 0:
            break
        população = [
            individuo
            for individuo in nova_população
            if individuo.altura <= altura_maxima or individuo.pontuação == 9999999
        ]
        if len(população) < tamanho_população:
            população += gerar_população(tamanho_população - len(população))
        else:
            população = roleta(população, tamanho_população)

    média = calcular_media(população)
    return média, melhor_adaptado


########################################################################################################################
OPERADORES = "+-/*"
TERMOS = "".join([str(i) for i in range(1, 6)]) + "x"

ENTRADAS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
SAIDAS = [0.67, 2, 4, 6.67, 10, 14, 18.67, 24, 30, 36.67]

GERAÇÕES = 300
TAMANHO_POPULAÇÃO = 150
TAXA_MUTAÇÃO = 5  # %
CRUZAMENTO_POR_GERAÇÃO = 120
ALTURA_MAXIMA = 3

media, melhor = executar(
    GERAÇÕES, TAMANHO_POPULAÇÃO, TAXA_MUTAÇÃO, CRUZAMENTO_POR_GERAÇÃO, ALTURA_MAXIMA
)

print(f"operadores: {OPERADORES}")
print(f"termos: {TERMOS}")
print(f"entradas: {ENTRADAS}")
print(f"saidas: {SAIDAS}")
print(f"gerações: {GERAÇÕES}")
print(f"tamanho da população: {TAMANHO_POPULAÇÃO}")
print(f"cruzamento por geração: {CRUZAMENTO_POR_GERAÇÃO}")
print(f"taxa de mutação: {TAXA_MUTAÇÃO}")
print(f"altura maxima: {ALTURA_MAXIMA}")
print(f"média da população: {media}")
print(f"indivíduo mais adaptado: {melhor.função}")
print(f"pontuação: {melhor.pontuação}")
print(f"altura: {melhor.altura}")
print("-------------------------------------------------------------")
