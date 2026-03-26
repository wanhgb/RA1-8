# Henry Gayer Bruschini Wan
# Grupo

import argparse

def estadoInicial(token):
    return token
    
def estadoNumero(token):
    return token


def estadoPonto(token):
    return token


def estadoDecimal(token):
    return token


    
def estadoOperador(token):
    return token

def estadoParenteses(token):
    return token

def estadoRES(token):
    return token

def estadoMEM(token):
    return token

def estadoErro(token):
    return None

def estadoFinal(token):
    return token    




def parserExpressao(linha, numero_linha):
    linha = linha.strip()

    if not linha:
        return None, []

    tokens = linha.split()

    vtoken= []
    erros = []

    for pos, token in enumerate(tokens):
        if token.replace('.', '', 1).isdigit():
            try:
                valor = float(token)
                token = estadoNumero(token)
                vtoken.append(valor)
            except ValueError:
                erros.append(
                    f"Linha {numero_linha}, posição {pos}: token valor inválido '{token}'"
                )

        elif token in ['+', '-', '*', '/','%','^','//']:
            token = estadoOperador(token)
            vtoken.append(token)

        elif token in ['(', ')']:
            token = estadoParenteses(token)
            vtoken.append(token)

        elif token in ['RES', 'res']:
            token = estadoRES(token)
            vtoken.append(token)

        elif token in ['MEM', 'mem']:
            token = estadoMEM(token)
            vtoken.append(token)

        else:
            erros.append(
                f"Linha {numero_linha}, posição {pos}: token operador inválido '{token}'"
            )

    return vtoken, erros


def lerArquivo(nomeArquivo):
    expressoes = []
    erros = []  

    try:
        with open(nomeArquivo, 'r', encoding='utf-8') as f:
            for numero_linha, linha in enumerate(f, start=1):
                tokens, erros_linha = parserExpressao(linha, numero_linha)

                if tokens is not None:
                    expressoes.append((numero_linha, tokens))

                if erros_linha:
                    erros.append((numero_linha, erros_linha)) 

    except FileNotFoundError:
        print(f"Erro: arquivo '{nomeArquivo}' não encontrado.")
    except PermissionError:
        print(f"Erro: sem permissão para abrir '{nomeArquivo}'.")

    return expressoes, erros


    


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo", help="Arquivo de entrada (.txt)")
    args = parser.parse_args()

    expressoes, erros = lerArquivo(args.arquivo)

    print("=== TOKENS ===")
    for num, tokens in expressoes:
        print(f"Linha {num}: {tokens}")

    print("\n=== ERROS ===")
    for num, erros_linha in erros:
        for erro in erros_linha:
            print(erro)


if __name__ == "__main__":
    main()