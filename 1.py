# Henry Gayer Bruschini Wan
# Grupo

import argparse


OPERADORES = {'+','-','*','/','//','%','^'}
# Funções auxiliares para teste de tokens

# Teste para token de número, que pode ser um inteiro ou decimal, positivo ou negativo
def testeNumero(token):
    if not token:
        return False
    t = token
    if t[0] == '-':
        t = t[1:]
    if not t:
        return False
    
    if t[0] == '.':
        return False
    pontos = 0 
    for char in t:
        if char == '.':
            pontos += 1
            if pontos > 1:
                return False
        elif not char.isdigit():
            return False
    if t[-1] == '.':
        return False
    return True

# Teste para token de nome de variável (MEM), que deve ser uma sequência de letras maiúsculas sem espaços
def testeMEM(token):
    if token == 'RES':
        return False
    if len(token) == 0:
        return False
    for char in token:
        if not ('A' <= char <= 'Z'):
            return False
    return True

# Teste para token de referência histórica (RES N), onde N deve ser um número inteiro não negativo
def testeEntrada(token):
    if not token:
        return False
    for char in token:
        if not('0' <= char <= '9'):
            return False
    return True

#função pra ajudar com tokenização, separando por espaços e parênteses, mantendo os parênteses como tokens separados
def tokenize(linha):
    tokens = []
    i = 0
    n = len(linha)
    while i < n:
        if linha[i].isspace():
            i += 1
            continue
        if linha[i] in '()':
            tokens.append(linha[i])
            i += 1
            continue
        start = i
        while i < n and not linha[i].isspace() and linha[i] not in '()':
            i += 1
        if start < i:
            tokens.append(linha[start:i])
    return tokens

# Função principal do parser

def parserExpressao(linha, tokens):

    if not linha:
        return None

    tokens = tokenize(linha)
    expressoes: list[str] = [] 
    tipos: list[str] = []  
    historico = []



    erros = []

    def registrar(token, tipo):  
        expressoes.append(token)
        tipos.append(tipo)

    def estadoInicial(tokens):
        if not tokens:
            return estadoFinal()
        
        token, *resto = tokens

        if token == '(':
            return estadoParentesesA(resto)
        
        if token == ')':
            return estadoParentesesB(resto)

        if token in OPERADORES and token != '-':
            return estadoOperador(token, resto)
        
        if token == '-':
            return estadoOperador(token, resto)
        
        if testeMEM(token):
            return estadoRMEM(token, resto)
        
        if token == 'RES':
            return estadoErro("RES deve ser precedido de um número inteiro não negativo")
        
        
        if testeNumero(token):
            return estadoNumero(token, resto)
        
        return estadoErro(f"Token inválido: '{token}'")
        
        
    def estadoNumero(token, resto):
        
        if resto:
            prox = resto[0]
            depois = resto[1:]

            if testeMEM(prox):
                return estadoWMEM(prox, token, depois)
            
            if prox == 'RES':
                if not testeEntrada(token):
                    return estadoErro(f"{token} RES': token deve ser um número inteiro não negativo para referência histórica.")
                return estadoRES(token, depois)

            registrar(token, 'NUM')
            return estadoInicial(resto)
        
        registrar(token, 'NUM')
        return estadoInicial(resto)
        
    def estadoOperador(token, resto):
        registrar(token, 'OP')
        return estadoInicial(resto)

    def estadoParentesesA(resto):
        registrar('(', 'PARENTESE_ABRE')
        return estadoInicial(resto)


    def estadoParentesesB(resto):
        registrar(')', 'PARENTESE_FECHA')
        return estadoInicial(resto)
    
    def estadoRES(N, resto):
        indice = int(N)
        if indice < 0:
            return estadoErro(f"Índice RES inválido: '{N}' deve ser um número inteiro não negativo.")
        if indice >= len(historico):
            return estadoErro(f"Índice RES fora do histórico: '{N}' excede o número de expressões anteriores.")
        N = historico[-indice]
        registrar(N, 'NUM')
        registrar('RES', 'RES')

        return estadoInicial(resto)

    def estadoRMEM(nome, resto):
        registrar(nome, 'RMEM')
        return estadoInicial(resto)

    def estadoWMEM(nome, V, resto):
        registrar(V, 'NUM')
        registrar(nome, 'WMEM')
        return estadoInicial(resto)

    def estadoErro(menssagem):
        erros.append(f"--{linha.strip()}: {menssagem}")
        return False

    def estadoFinal():
        return True, expressoes, tipos

    return estadoInicial(tokens), erros



def lerArquivo(nomeArquivo):
    resultados = []
    erros = []

    try:
        with open(nomeArquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                resultado, erros_linha = parserExpressao(linha, [])
                if resultado is None:
                    continue
                if resultado:
                    ok, expressoes, tipos = resultado
                    if ok:
                        resultados.append((expressoes, tipos))

                if erros_linha:
                    erros.extend(erros_linha)

    except FileNotFoundError:
        print(f"Erro: arquivo '{nomeArquivo}' não encontrado.")
    except PermissionError:
        print(f"Erro: sem permissão para abrir '{nomeArquivo}'.")

    return resultados, erros




def gerar_assembly(operacao, a, b):
    print(f"Gerando assembly para operação: {operacao}")
    if operacao == '+':
        return a + b
    elif operacao == '-':
        return a - b
    elif operacao == '*':
        return a * b
    elif operacao == '/':
        return a / b if b != 0 else 0
    elif operacao == '//':
        return a // b if b != 0 else 0
    elif operacao == '%':
        return a % b if b != 0 else 0
    elif operacao == '^':
        return a ** b
    else:
        return 0


def executarExpressao(expressoes, tipos=None, memoria=None, historico=None):
    if memoria is None:
        memoria = {}
    if historico is None:
        historico = []
    pilha = []
    contextos = []  

    for i, token in enumerate(expressoes):
        tipo = tipos[i] if tipos and i < len(tipos) else None

        if token == '(':
            # Abrir novo contexto: salvar pilha atual e criar nova
            contextos.append(pilha)
            pilha = []
        elif token == ')':
            # Fechar contexto: pegar resultado da subexpressão e voltar ao contexto anterior
            if not contextos:
                print("Erro: parêntese de fechamento sem abertura")
                continue
            if pilha:
                resultado_sub = pilha[-1]  # Último resultado da subexpressão
            else:
                resultado_sub = None
            pilha = contextos.pop()
            if resultado_sub is not None:
                pilha.append(resultado_sub)
        elif token in OPERADORES:
            # Ao se deparar com um operador, chama a geração de assembly para a operação com operandos
            if len(pilha) >= 2:
                b = pilha.pop()
                a = pilha.pop()
                resultado = gerar_assembly(token, a, b)
                pilha.append(resultado)
        elif tipo == 'NUM' or token.replace('.', '', 1).isdigit():
            if testeNumero(token):
                pilha.append(float(token))
            else:
                pilha.append(token)  # em caso de falha dupla, trata como string
        elif tipo == 'RMEM':
            valor = memoria.get(token, 0.0)
            pilha.append(valor)
            print(f"Lendo da memória '{token}': {valor}")
        elif tipo == 'WMEM':
            if pilha:
                valor = pilha.pop()
                memoria[token] = valor
                print(f"Escrevendo na memória '{token}': {valor}")
        elif tipo == 'RES':
            # N RES: soma os valores das N últimas expressões e adiciona à pilha
            if pilha:
                N = int(pilha.pop())
                if N > 0 and N <= len(historico):
                    valor = sum(historico[-N:])
                    pilha.append(valor)
                else:
                    print(f"Erro: N={N} inválido para RES (deve ser 1 a {len(historico)})")
        else:
            # Outros tokens, ignorar
            pass

    # Retornar o resultado da expressão (último da pilha) para adicionar ao histórico
    resultado_expressao = pilha[-1] if pilha else None
    return memoria, resultado_expressao




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo", help="Arquivo de entrada (.txt)")
    args = parser.parse_args()

    resultados, erros = lerArquivo(args.arquivo)

    memoria = {}  # Memória compartilhada entre expressões
    historico = []  # Histórico de resultados para RES

    print("=== RESULTADOS ===")
    for expressoes, tipos in resultados:
        print("\nExpressoes:", expressoes)
        print("Tipos:    ", tipos)
        memoria, resultado = executarExpressao(expressoes, tipos, memoria, historico)
        if resultado is not None:
            historico.append(resultado)
        print()
    print("\n=== ERROS ===")
    for erro in erros:
        print(erro)

    print("\n=== MEMÓRIA FINAL ===")
    for variavel, valor in memoria.items():
        print(f"{variavel}: {valor}")

    print("\n=== RESULTADOS DAS EXPRESSÕES ===")
    for i, res in enumerate(historico):
        print(f"Expressão {i+1}: {res}")

if __name__ == "__main__":
    main()




