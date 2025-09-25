'''PROJETO DA DISCIPLINA DE LINGUAGENS FORMAIS E COMPUTABILIDADE
TEMA 1 - PRODUÇÃO DE CADEIAS POR GLC
AUTOR: BRENDO DE ALMEIDA MENDONÇA
MATRÍCULA: 20190172521
'''

import os
import random

#função para verificar se o arquivo existe
def verificar_existencia_arquivo(arquivo):
    if not os.path.exists(arquivo):
        print(f"Erro: O arquivo '{arquivo}' não existe.")
        return False
    return True

#método para verificar se o arquivo de gramática está correto
def verificar_arquivo_gramatica(arquivo):
    try:
        with open(arquivo, 'r') as f:
            linhas = f.readlines()

            #verificar se o arquivo possui pelo menos 4 linhas (variáveis, inicial, terminais e produções)
            if len(linhas) < 4:
                raise ValueError("O arquivo de gramática deve conter pelo menos 4 linhas.")

            #verificação das variáveis
            if not linhas[0].strip().startswith("variaveis:"):
                raise ValueError("A primeira linha deve ser 'variaveis: <lista de variáveis>'.")
            variaveis = linhas[0].strip().split(":")[1].strip().split(',')
            if not variaveis:
                raise ValueError("Não foram especificadas variáveis na gramática.")

            #verificação do símbolo inicial
            if not linhas[1].strip().startswith("inicial:"):
                raise ValueError("A segunda linha deve ser 'inicial: <símbolo inicial>'.")
            simbolo_inicial = linhas[1].strip().split(":")[1].strip()
            if simbolo_inicial not in variaveis:
                raise ValueError(f"O símbolo inicial '{simbolo_inicial}' não está na lista de variáveis.")

            #verificação dos terminais
            if not linhas[2].strip().startswith("terminais:"):
                raise ValueError("A terceira linha deve ser 'terminais: <lista de terminais>'.")
            terminais = linhas[2].strip().split(":")[1].strip().split(',')
            if not terminais:
                raise ValueError("Não foram especificados terminais na gramática.")

            #verificação das produções
            if len(linhas) <= 4:
                raise ValueError("O arquivo de gramática deve conter pelo menos uma produção.")
                    
            return True
    except Exception as e:
        print(f"Erro ao verificar o arquivo de gramática: {e}")
        return False


#método para ler a gramática de um arquivo
def ler_gramatica(arquivo):
    gramatica = {
        'variaveis': [],
        'inicial': '',
        'terminais': [],
        'producoes': {},
    }
    
    with open(arquivo, 'r') as f:
        linhas = f.readlines()
        
        #processando a parte das variáveis
        gramatica['variaveis'] = linhas[0].strip().split(":")[1].strip().split(',')
        
        #processando símbolo inicial
        gramatica['inicial'] = linhas[1].strip().split(":")[1].strip()
        
        #processando os terminais
        gramatica['terminais'] = linhas[2].strip().split(":")[1].strip().split(',')

        #processando as produções
        for linha in linhas[4:]:
            lado_esquerdo, lado_direito = linha.strip().split(":")
            if lado_esquerdo not in gramatica['producoes']:
                gramatica['producoes'][lado_esquerdo] = []
            producoes = lado_direito.strip().split('|')  #adiciona suporte para múltiplas produções separadas por '|'
            gramatica['producoes'][lado_esquerdo].extend(producoes)
            
    return gramatica

cadeias_geradas = set()
#função para gerar cadeias no modo rápido
def gerar_cadeia_rapida(gramatica):
    producao = 'S'
    derivacao = []
    
    qnt_cadeias = 0
    max_cadeias = 100
    
    #substituindo os não-terminais pela sua produção
    while True:
  
        #percorrendo cada simbolo na produção
        for simbolo in producao:
            
            if simbolo in gramatica['variaveis']:
                #escolhe a produção
                nao_terminal = simbolo
                producoes_possiveis = gramatica['producoes'][nao_terminal]  
                producao_escolhida = random.choice(producoes_possiveis)                
                derivacao.append(f"{nao_terminal} -> {producao_escolhida}")
                
                #adiciona a produção escolhida à nova produção
                if producao_escolhida == 'epsilon':
                    producao = producao.replace(nao_terminal, '', 1)  #o '1' garante que apenas o primeiro não-terminal será removido
                else:
                    index = producao.find(nao_terminal)
                    producao = producao[:index] + producao_escolhida + producao[index + 1:]
                print(producao)

      
        # verifica se a produção contém apenas terminais
        if all(s in gramatica['terminais'] for s in producao):
            cadeia_final = "".join(producao)

            if cadeia_final not in cadeias_geradas:#verifica se a cadeia já foi gerada
                cadeias_geradas.add(cadeia_final)
                print(derivacao)
            else:
                producao = 'S'
                derivacao.clear()
                qnt_cadeias += 1
                if qnt_cadeias >= max_cadeias:
                    print("Todas cadeias foram geradas.")
                    break
                continue
            
            return cadeia_final

#método para gerar cadeias no modo detalhado
def gerar_cadeia_detalhada(gramatica):
    producao = 'S'
    derivacao = []

    #substituindo os não-terminais pela sua produção
    while True:
                
        #percorrendo cada simbolo na produção
        for simbolo in producao:

            if simbolo in gramatica['variaveis']:
                #escolhe a produção
                nao_terminal = simbolo
                producoes_possiveis = gramatica['producoes'][nao_terminal]
                while True:
                    producao_escolhida = input(f"Escolha uma produção para {nao_terminal}: {producoes_possiveis} ")
                    if producao_escolhida in producoes_possiveis:
                        break
                    else:
                        print("Produção inválida! Tente novamente.")              
                derivacao.append(f"{nao_terminal} -> {producao_escolhida}")
                print(derivacao)
                
                #adiciona a produção escolhida à nova produção
                if producao_escolhida == 'epsilon':
                    producao = producao.replace(nao_terminal, '', 1)  # O '1' garante que apenas o primeiro não-terminal será removido
                else:
                    index = producao.find(nao_terminal)
                    producao = producao[:index] + producao_escolhida + producao[index + 1:]
                print(producao)

        
        # verifica se a produção contém apenas terminais
        if all(s in gramatica['terminais'] for s in producao):
            break 

    cadeia_final = "".join(producao)
    return cadeia_final

#função principal que executa o programa
def main():
    try:
        arquivo = input("Digite o caminho para o arquivo da gramática: ")
        if not verificar_existencia_arquivo(arquivo):
            return
        if not verificar_arquivo_gramatica(arquivo):
            print("Erro na verificação do arquivo de gramática.")
            return
        
        gramatica = ler_gramatica(arquivo)
        
        while True:
            print("\nEscolha o modo de geração:")
            print("1. Modo rápido")
            print("2. Modo detalhado")
            print("3. Sair")
            opcao = int(input("Escolha uma opção: "))
            
            if opcao == 1:
                print("\nModo Rápido:")
                cadeia = gerar_cadeia_rapida(gramatica)
                print(f"Cadeia gerada: {cadeia}")
            elif opcao == 2:
                print("\nModo Detalhado:")
                cadeia = gerar_cadeia_detalhada(gramatica)
                print(f"Cadeia gerada: {cadeia}")
            elif opcao == 3:
                break
            else:
                print("Opção inválida! Tente novamente.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()
