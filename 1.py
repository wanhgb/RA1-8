# Henry Gayer Bruschini Wan
# Grupo

import argparse


OPERADORES = {'+','-','*','/','//','%','^'}

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

def separarParenteses(token):
    tokens = []
    x = ''
    for char in token:
        if char in ('(', ')'):
            if x:
                tokens.append(x)
            x = ''
            tokens.append(char)
        else:
            x += char
    if x:
        tokens.append(x)
    return tokens

def testeMEM(token):
    if token == 'RES':
        return False
    if len(token) == 0:
        return False
    for char in token:
        if not ('A' <= char <= 'Z'):
            return False
    return True

def testeEntrada(token):
    if not token:
        return False
    for char in token:
        if not('0' <= char <= '9'):
            return False
    return True


def parserExpressao(linha, tokens):

    if not linha:
        return None

    tokens = linha.split()
    expressoes: list[str] = [] 
    tipos: list[str] = []  
    historico = []
    memoria = {}


    erros = []

    def registrar(token, tipo):  
        expressoes.append(token)
        tipos.append(tipo)

    def estadoInicial(tokens):
        if not tokens:
            return estadoFinal()
        
        token, *resto = tokens

        if len(token) > 1 and ('(' in token or ')' in token):
            partes = separarParenteses(token)
            return estadoInicial(partes + resto)
        
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
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo", help="Arquivo de entrada (.txt)")
    args = parser.parse_args()

    resultados, erros = lerArquivo(args.arquivo)

    print("=== RESULTADOS ===")
    for expressoes, tipos in resultados:
        print("\nExpressoes:", expressoes)
        print("Tipos:    ", tipos)

    print("\n=== ERROS ===")
    for erro in erros:
        print(erro)


if __name__ == "__main__":
    main()




