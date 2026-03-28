PUCPR
LINGUAGENS FORMAIS E COMPILADORES
FRANK COELHO DE ALCANTARA
HENRY GAYER BRUSCHINI WAN


Programa em Python que lê expressões matemáticas de um arquivo .txt, realiza a analise léxica
e gera código Assembly equivalente, junto de um resultado calculado pelo python para validar o resultado do assembly gerado.


Como usar(execução):
python programa.py entrada.txt


nesse caso: python 1.py teste1.txt

Isso irá:

Ler as expressões do arquivo ao se utilizar da função lerArquivo
Tokeniza cada linha usando a função parserExpressao
    com os tokens duas funções rodas:
    Mostrar o resultado de cada expressão calculadas por executarExpressao e os erros e as memorias
    Utiliza os tokens para gerar um código assembly com as intruções para realizar cada operação

Gerar um arquivo .s com o código Assembly


Cada linha de teste conter uma expressão RPN. Exemplo:

Operadores suportados
+ soma
- subtração
* multiplicação
/ divisão
// divisão inteira
% módulo
^ potência

Recursos
Uso de pilha para gerenciamento de operações (notação estilo RPN)

Histórico de resultados com RES N
Geração automática de Assembly ARM


Saída
Resultados no terminal
Arquivo .s com o código Assembly gerado

Requisitos
Variáveis para MEM com letras maiúsculas (ex: A, B)
Linhas para RES inteiros positivos
Números negativos devem ser formatados com o - encostado como: -10
Expoentes precisão ser inteiros e não negativos