# Henry Gayer Bruschini Wan
# Grupo RA1-8

import argparse
import struct
import os

OPERADORES = {'+','-','*','/','//','%','^'}

#----------------------------------------------------------------------
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

# Teste para token de nome de variável (MEM), que deve ser uma sequência de letras maiúsculas
def testeMEM(token):
    if token == 'RES':
        return False
    if len(token) == 0:
        return False
    for char in token:
        if not ('A' <= char <= 'Z'):
            return False
    return True

# Teste para token de referência histórica (RES N), onde N deve ser inteiro não negativo
def testeEntrada(token):
    if not token:
        return False
    for char in token:
        if not ('0' <= char <= '9'):
            return False
    return True

# Função para separar a linha em tokens, mantendo parênteses como tokens separados
def tokenize(linha):
    tokens = []
    i = 0
    n = len(linha)
    while i < n:
        if str(linha[i]).isspace():
            i += 1
            continue
        if linha[i] in ('(', ')'):
            tokens.append(linha[i])
            i += 1
            continue
        start = i
        while i < n and not str(linha[i]).isspace() and linha[i] not in ('(', ')'):
            i += 1
        if start < i:
            tokens.append(linha[start:i])
    return tokens

# Função para converter um double Python de 64 bits em dois words ARM de 32 bits
def double_to_words(value):
    packed = struct.pack('<d', value)
    low = struct.unpack('<I', packed[0:4])[0]
    high = struct.unpack('<I', packed[4:8])[0]
    return low, high

#----------------------------------------------------------------------
# Função principal do parser com o autômato de estados finitos

def parserExpressao(linha, historico):

    if not linha or not linha.strip():
        return None, []

    tokens = tokenize(linha)
    expressoes = []
    tipos = []
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

        if token in OPERADORES:
            return estadoOperador(token, resto)

        if token == 'RES':
            return estadoErro("RES deve ser precedido de um número inteiro não negativo")

        if testeMEM(token):
            return estadoRMEM(token, resto)

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
                    return estadoErro(f"'{token} RES': token deve ser um número inteiro não negativo")
                indice = int(token)
                if indice <= 0 or indice > len(historico):
                    return estadoErro(f"Índice RES '{token}' fora do histórico")
                registrar(str(historico[-indice]), 'NUM')
                return estadoInicial(depois)

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

    def estadoRMEM(nome, resto):
        registrar(nome, 'RMEM')
        return estadoInicial(resto)

    def estadoWMEM(nome, V, resto):
        registrar(V, 'NUM')
        registrar(nome, 'WMEM')
        return estadoInicial(resto)

    def estadoErro(mensagem):
        erros.append(f"--{linha.strip()}: {mensagem}")
        return False

    def estadoFinal():
        return True

    ok = estadoInicial(tokens)
    if ok is True:
        return (expressoes, tipos), erros
    return None, erros


#----------------------------------------------------------------------
# Classe para gerar o código assembly 

class GeradorAssembly:

    def __init__(self, profundidade=32, max_expressoes=32):
        self.profundidade = profundidade
        self.max_expressoes = max_expressoes
        self.mapa_constantes = {}   # valor double -> label no .rodata
        self.indice_constante = 0
        self.slots_variaveis = {}   # nome da variavel -> indice no VAR_DATA
        self.linhas_dados = []      # linhas da secao .rodata
        self.linhas_corpo = []      # linhas do corpo do main

    def registrar_constante(self, value):
        # cada constante double e armazenada uma unica vez no .rodata
        key = struct.pack('<d', float(value))
        if key not in self.mapa_constantes:
            label = "E" + str(self.indice_constante)
            self.indice_constante += 1
            low, high = double_to_words(float(value))
            self.linhas_dados.append(
                label + ":   .word 0x" + format(low, '08X') +
                ", 0x" + format(high, '08X') +
                "   @ " + repr(float(value)))
            self.mapa_constantes[key] = label
        return self.mapa_constantes[key]

    def registrar_variavel(self, nome):
        if nome not in self.slots_variaveis:
            self.slots_variaveis[nome] = len(self.slots_variaveis)
        return self.slots_variaveis[nome]

    def escrever(self, linha=""):
        self.linhas_corpo.append(linha)

    def carregar_double(self, base):
        # carrega 8 bytes de [base] no registrador D0
        # usa dois LDR de 32 bits + FMDRR (64 bits foi divido em 2 words)
        return [
            f"    LDR     r0, [{base}]",
            f"    LDR     r1, [{base}, #4]",
            f"    FMDRR   D0, r0, r1"
        ]

    def gravar_double(self, base):
        # grava D0 em [base] usando FMRRD + dois STR (64 bits foi divido em 2 words)
        return [
            f"    FMRRD   r0, r1, D0",
            f"    STR     r0, [{base}]",
            f"    STR     r1, [{base}, #4]"
        ]

    def copiar_D0_para_D1(self):
        # copia D0 para D1 
        return [
            "    FMRRD   r0, r1, D0",
            "    FMDRR   D1, r0, r1"
        ]

    def copiar_D2_para_D0(self):
        # move o resto do divmod (D2) para D0
        return [
            "    FMRRD   r0, r1, D2",
            "    FMDRR   D0, r0, r1"
        ]

    #função principal de tradução de expressões em intrução para realizar operação em assembly
    def gerarAssembly(self, expressoes, tipos, num):
        self.escrever(f"    @ === expressao {num} " + "=" * 44)
        self.escrever()

        for i, tok in enumerate(expressoes):
            tipo = tipos[i]

            if tipo == 'NUM':
                label = self.registrar_constante(tok)
                self.escrever(f"    @ push {tok}")
                self.escrever(f"    LDR     r4, ={label}")
                for linha in self.carregar_double("r4"):
                    self.escrever(linha)
                self.escrever(f"    BL      pilha_push")
                self.escrever()

            elif tipo == 'OP':
                self.escrever(f"    @ operador '{tok}'")
                self.escrever(f"    BL      pilha_pop        @ D0 = B (operando direito)")
                for linha in self.copiar_D0_para_D1():
                    self.escrever(linha)
                self.escrever(f"    BL      pilha_pop        @ D0 = A (operando esquerdo)")

                if tok == '+':
                    self.escrever("    VADD.F64 D0, D0, D1")
                elif tok == '-':
                    self.escrever("    VSUB.F64 D0, D0, D1")
                elif tok == '*':
                    self.escrever("    VMUL.F64 D0, D0, D1")
                elif tok == '/':
                    self.escrever("    VDIV.F64 D0, D0, D1")
                elif tok == '//':
                    self.escrever("    BL      divmod_sub    @ resultado: D0 = quociente")
                elif tok == '%':
                    self.escrever("    BL      divmod_sub    @ resultado: D2 = resto")
                    for linha in self.copiar_D2_para_D0():
                        self.escrever(linha)
                elif tok == '^':
                    self.escrever("    BL      pow_sub       @ D0 = A elevado a B")

                self.escrever("    BL      pilha_push")
                self.escrever()

            elif tipo == 'RMEM':
                slot = self.registrar_variavel(tok)
                self.escrever(f"    @ le variavel {tok} da memoria")
                self.escrever(f"    LDR     r4, =VAR_DATA")
                if slot > 0:
                    self.escrever(f"    ADD     r4, r4, #{slot * 8}")
                for linha in self.carregar_double("r4"):
                    self.escrever(linha)
                self.escrever(f"    BL      pilha_push")
                self.escrever()

            elif tipo == 'WMEM':
                slot = self.registrar_variavel(tok)
                self.escrever(f"    @ grava topo da pilha na variavel {tok}")
                self.escrever(f"    LDR     r4, =pilha_topo")
                self.escrever(f"    LDR     r5, [r4]")
                self.escrever(f"    SUB     r5, r5, #1")
                self.escrever(f"    LDR     r4, =pilha_mem")
                self.escrever(f"    ADD     r4, r4, r5, LSL #3")
                for linha in self.carregar_double("r4"):
                    self.escrever(linha)
                self.escrever(f"    LDR     r4, =VAR_DATA")
                if slot > 0:
                    self.escrever(f"    ADD     r4, r4, #{slot * 8}")
                for linha in self.gravar_double("r4"):
                    self.escrever(linha)
                self.escrever()

            elif tipo in ('PARENTESE_ABRE', 'PARENTESE_FECHA'):
                pass   

        # salva o resultado no vetor de resultados e exibe no display
        offset = (num - 1) * 8
        self.escrever(f"    @ fim expressao {num}: salva resultado e mostra no display")
        self.escrever(f"    BL      pilha_pop")
        self.escrever(f"    LDR     r4, =resultados_mem")
        if offset > 0:
            self.escrever(f"    ADD     r4, r4, #{offset}")
        for linha in self.gravar_double("r4"):
            self.escrever(linha)
        self.escrever(f"    VCVT.S32.F64  S0, D0    @ converte double para inteiro")
        self.escrever(f"    VMOV    r0, S0")
        self.escrever(f"    BL      print_dec")
        # delay de ~2 
        self.escrever(f"    MOV     r1, #50")
        self.escrever(f"espera_ext_{num}:")
        self.escrever(f"    LDR     r2, =1000000")
        self.escrever(f"espera_int_{num}:")
        self.escrever(f"    SUBS    r2, r2, #1")
        self.escrever(f"    BNE     espera_int_{num}")
        self.escrever(f"    SUBS    r1, r1, #1")
        self.escrever(f"    BNE     espera_ext_{num}")
        self.escrever()

    def salvar(self, caminho, n_expressoes):
        n_vars = max(len(self.slots_variaveis), 1)
        bytes_resultado = max(n_expressoes, 1) * 8
        linhas = []

        # secao .rodata: constantes double e tabela de segmentos
        linhas.append(
            "@ HENRY GAYER BRUSCHINI WAN\n"
            "@ GRUPO RA1-8\n"
            "    .arch   armv7-a\n"
            "    .fpu    vfpv3-d16\n"
            "    .syntax unified\n"
            "\n"
            "    .section .rodata\n"
            "    .align  3\n"
        )
        for d in self.linhas_dados:
            linhas.append("    " + d)
        linhas.append(
            "\nhex_table:\n"
            "    .byte 0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07\n"
            "    .byte 0x7F,0x6F,0x77,0x7C,0x39,0x5E,0x79,0x71\n"
        )

      
        # .align 3 antes de cada bloco garante alinhamento de 8 bytes para os doubles
        linhas.append(
            "\n"
            "    .section .data\n"
            "    .align  3\n"
            "pilha_topo:\n"
            "    .word   0\n"
            "    .align  3\n"
            "pilha_mem:\n"
            f"    .fill   {self.profundidade * 8}, 1, 0\n"
            "    .align  3\n"
            "VAR_DATA:\n"
            f"    .fill   {n_vars * 8}, 1, 0\n"
            "    .align  3\n"
            "resultados_mem:\n"
            f"    .fill   {bytes_resultado}, 1, 0\n"
        )

        # secao .text: _start 
        linhas.append(
            "\n"
            "    .section .text\n"
            "    .global _start\n"
            "\n"
            "_start:\n"
            "    LDR     sp, =0x00080000 \n"
            "    PUSH    {r4, r5, r6, r7, r8, lr}\n"
            "    LDR     r0, =pilha_topo\n"
            "    MOV     r1, #0\n"
            "    STR     r1, [r0]\n"
            "\n"
        )

        # corpo gerado: as expressoes
        for linha in self.linhas_corpo:
            linhas.append(linha)

        # fim e subrotinas
        linhas.append(
            "    @ todos os resultados estao em resultados_mem\n"
            "    POP     {r4, r5, r6, r7, r8, lr}\n"
            "fim:\n"
            "    B       fim\n"
            "\n"

            "@ pilha_push: empilha D0 no topo da pilha de doubles\n"
            "pilha_push:\n"
            "    PUSH    {r0, r1, r4, r5, lr}\n"
            "    LDR     r4, =pilha_topo\n"
            "    LDR     r5, [r4]              @ r5 = indice do topo\n"
            "    LDR     r4, =pilha_mem\n"
            "    ADD     r4, r4, r5, LSL #3    @ r4 = &pilha_mem[topo]\n"
            "    FMRRD   r0, r1, D0            @ extrai os 64 bits de D0 em r0:r1\n"
            "    STR     r0, [r4]              @ grava word low\n"
            "    STR     r1, [r4, #4]          @ grava word high\n"
            "    LDR     r4, =pilha_topo\n"
            "    ADD     r5, r5, #1\n"
            "    STR     r5, [r4]              @ incrementa topo\n"
            "    POP     {r0, r1, r4, r5, pc}\n"
            "\n"

            "@ pilha_pop: desempilha topo para D0\n"
            "pilha_pop:\n"
            "    PUSH    {r0, r1, r4, r5, lr}\n"
            "    LDR     r4, =pilha_topo\n"
            "    LDR     r5, [r4]\n"
            "    SUB     r5, r5, #1            @ decrementa topo\n"
            "    STR     r5, [r4]\n"
            "    LDR     r4, =pilha_mem\n"
            "    ADD     r4, r4, r5, LSL #3\n"
            "    LDR     r0, [r4]              @ le word low\n"
            "    LDR     r1, [r4, #4]          @ le word high\n"
            "    FMDRR   D0, r0, r1            @ reconstroi D0 a partir de r0:r1\n"
            "    POP     {r0, r1, r4, r5, pc}\n"
            "\n"

            "@ divmod_sub: recebe D0=A e D1=B, retorna D0=quociente e D2=resto\n"
            "divmod_sub:\n"
            "    PUSH    {r4, r5, r6, r7, lr}\n"
            "    VCVT.S32.F64  S0, D0\n"
            "    VCVT.S32.F64  S2, D1\n"
            "    VMOV    r4, S0               @ r4 = parte inteira de A\n"
            "    VMOV    r5, S2               @ r5 = parte inteira de B\n"
            "    MOV     r6, #0               @ r6 = quociente\n"
            "    CMP     r5, #0\n"
            "    BEQ     divisao_por_zero\n"
            "loop_divisao:\n"
            "    CMP     r4, r5\n"
            "    BLT     fim_divisao\n"
            "    SUB     r4, r4, r5\n"
            "    ADD     r6, r6, #1\n"
            "    B       loop_divisao\n"
            "fim_divisao:\n"
            "    VMOV    S8,  r6\n"
            "    VCVT.F64.S32  D0, S8         @ D0 = quociente como double\n"
            "    VMOV    S10, r4\n"
            "    VCVT.F64.S32  D2, S10        @ D2 = resto como double\n"
            "    POP     {r4, r5, r6, r7, pc}\n"
            "divisao_por_zero:\n"
            "    MOV     r6, #0\n"
            "    MOV     r4, #0\n"
            "    B       fim_divisao\n"
            "\n"

            "@ pow_sub: recebe D0=base e D1=expoente, retorna D0=resultado\n"
            "@ funciona apenas com expoentes inteiros nao negativos\n"
            "pow_sub:\n"
            "    PUSH    {r4, r5, r6, lr}\n"
            "    VCVT.S32.F64  S0, D0\n"
            "    VCVT.S32.F64  S2, D1\n"
            "    VMOV    r4, S0               @ r4 = base\n"
            "    VMOV    r5, S2               @ r5 = expoente\n"
            "    @ valida: expoente deve ser inteiro nao negativo\n"
            "    CMP     r5, #0\n"
            "    BMI     expoente_invalido     @ negativo: erro\n"
            "    MOV     r6, #1               @ r6 = resultado (comeca em 1)\n"
            "    CMP     r5, #0\n"
            "    BEQ     fim_potencia\n"
            "loop_potencia:\n"
            "    MUL     r6, r6, r4\n"
            "    SUBS    r5, r5, #1\n"
            "    BGT     loop_potencia\n"
            "fim_potencia:\n"
            "    VMOV    S8, r6\n"
            "    VCVT.F64.S32  D0, S8\n"
            "    POP     {r4, r5, r6, pc}\n"
            "expoente_invalido:\n"
            "    @ expoente negativo: retorna 0.0 como indicador de erro\n"
            "    MOV     r6, #0\n"
            "    B       fim_potencia\n"
            "\n"

            "@ --- apresentação no display ---"
            "@ print_dec: exibe r0 como numero decimal nos displays HEX3-HEX0\n"
            "@ extrai cada digito com divisao por 10 via subtracao\n"
            "print_dec:\n"
            "    PUSH    {r1, r2, r3, r4, r5, r6, r7, lr}\n"
            "    LDR     r1, =0xFF200020\n"
            "    LDR     r2, =hex_table\n"
            "    MOV     r3, #0               @ word que sera gravado no display\n"
            "    MOV     r4, #0               @ deslocamento em bits (0, 8, 16, 24)\n"
            "    MOV     r7, #4               @ 4 digitos\n"
            "loop_display:\n"
            "    CMP     r7, #0\n"
            "    BEQ     fim_display\n"
            "    MOV     r5, #0               @ r5 = quociente\n"
            "    MOV     r6, r0               @ r6 = valor atual\n"
            "divide_por_10:\n"
            "    CMP     r6, #10\n"
            "    BLT     pega_digito\n"
            "    SUB     r6, r6, #10\n"
            "    ADD     r5, r5, #1\n"
            "    B       divide_por_10\n"
            "pega_digito:\n"
            "    LDRB    r6, [r2, r6]         @ r6 = segmentos do digito\n"
            "    ORR     r3, r3, r6, LSL r4\n"
            "    ADD     r4, r4, #8\n"
            "    MOV     r0, r5               @ proximo digito\n"
            "    SUB     r7, r7, #1\n"
            "    B       loop_display\n"
            "fim_display:\n"
            "    STR     r3, [r1]\n"
            "    POP     {r1, r2, r3, r4, r5, r6, r7, pc}\n"
        )

        with open(caminho, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas) + '\n')

        print(f"[asm] '{caminho}' gerado com sucesso.")


#----------------------------------------------------------------------
# Função para avaliar as expressoes em Python (para comparar com o assembly)

def executarExpressao(expressoes, tipos, memoria):

    pilha = []

    def operacao(op, a, b):
        if op == '+':
            return a + b
        elif op == '-':
            return a - b
        elif op == '*':
            return a * b
        elif op == '/':
            if b == 0:
                raise ZeroDivisionError("Divisão por zero")
            return a / b
        elif op == '//':
            if b == 0:
                raise ZeroDivisionError("Divisão por zero")
            return float(int(a) // int(b))
        elif op == '%':
            if b == 0:
                raise ZeroDivisionError("Módulo por zero")
            return float(int(a) % int(b))
        elif op == '^':
            # expoente deve ser inteiro nao negativo
            if b != int(b):
                raise ValueError(f"Expoente '{b}' nao e inteiro")
            if int(b) < 0:
                raise ValueError(f"Expoente '{b}' e negativo")
            return float(int(a) ** int(b))
        else:
            raise ValueError(f"Operador desconhecido: {op}")

    for i, token in enumerate(expressoes):
        tipo = tipos[i]

        # parenteses agora nao afetam a pilha — sao apenas visuais antes eu estava usando contexto
        if tipo in ('PARENTESE_ABRE', 'PARENTESE_FECHA'):
            continue

        elif token in OPERADORES:
            if len(pilha) < 2:
                print(f"Erro: operador '{token}' requer 2 operandos")
                return None, memoria
            b = pilha.pop()
            a = pilha.pop()
            try:
                pilha.append(operacao(token, a, b))
            except (ZeroDivisionError, ValueError) as e:
                print(f"Erro: {e}")
                return None, memoria

        elif tipo == 'NUM':
            pilha.append(float(token))

        elif tipo == 'RMEM':
            valor = memoria.get(token, 0.0)
            pilha.append(valor)
            print(f"  Lendo da memória '{token}': {valor}")

        elif tipo == 'WMEM':
            if not pilha:
                print(f"Erro: WMEM '{token}' com pilha vazia")
                return None, memoria
            memoria[token] = pilha[-1]
            print(f"  Escrevendo na memória '{token}': {memoria[token]}")

    return (pilha[-1] if pilha else None), memoria


def lerArquivo(nomeArquivo):
    resultados = []
    try:
        with open(nomeArquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                resultados.append(linha)
    except FileNotFoundError:
        print(f"Erro: arquivo '{nomeArquivo}' não encontrado.")
    except PermissionError:
        print(f"Erro: sem permissão para abrir '{nomeArquivo}'.")
    return resultados


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo", help="Arquivo de entrada (.txt)")
    args = parser.parse_args()

    nome_base = os.path.splitext(args.arquivo)[0]
    nome_asm = nome_base + ".s"

    resultados = lerArquivo(args.arquivo)

    historico = []
    gerador = GeradorAssembly(profundidade=32, max_expressoes=32)
    historico_final = []
    
    erros = []

    sep = "=" * 60
    print(sep)
    print("  AVALIAÇÃO DE CADA EXPRESSAO")
    print(sep)

    def exibirResultados(resultados):
        memoria = {}
        num_expr = 0
        for num_linha, linha in enumerate(resultados, 1):
            resultado_parse, lista_erros = parserExpressao(linha, historico)

            if lista_erros:
                for e in lista_erros:
                    erros.append("linha " + str(num_linha) + ": " + e)
                continue

            if resultado_parse is None:
                continue

            expressoes, tipos = resultado_parse
            num_expr += 1

            print("")
            print("Expressao " + str(num_expr) + ":")
            print("  tokens : " + str(expressoes))
            print("  tipos  : " + str(tipos))

            resultado, memoria = executarExpressao(expressoes, tipos, memoria)
            if resultado is not None:
                historico.append(resultado)
                historico_final.append((num_expr, resultado))
                print("  = " + str(resultado))
            else:
                print("  = <erro de avaliacao>")

            gerador.gerarAssembly(expressoes, tipos, num_expr)

        print("")
        if erros:
            print(sep)
            print("  ERROS LEXICOS")
            print(sep)
            for e in erros:
                print(e)
        else:
            print("  (nenhum erro lexico)")

        if memoria:
            print("")
            print(sep)
            print("  MEMORIA FINAL (variaveis)")
            print(sep)
            for var, val in memoria.items():
                print("  " + var + " = " + str(val))

        print("")
        print(sep)
        print("  TABELA RESUMO")
        print(sep)
        for i, res in historico_final:
            low, high = double_to_words(res)
            print("  expressao " + str(i).rjust(3) + ": " + str(res))

        print("")
        gerador.salvar(nome_asm, num_expr)
        print("")

    exibirResultados(resultados)


if __name__ == "__main__":
    main()