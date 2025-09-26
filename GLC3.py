import os
import itertools

# --- FUNÇÕES DE VERIFICAÇÃO E LEITURA ---

def verificar_existencia_arquivo(arquivo):
    #verifica se o arquivo de entrada existe no caminho especificado
    if not os.path.exists(arquivo):
        print(f"Erro: O arquivo '{arquivo}' não existe")
        return False
    return True

def verificar_arquivo_gramatica(arquivo):#tratamentos caso o arquivo não esteja de acordo  
    #realiza verificação de gramática
    try:
        with open(arquivo, 'r') as f:
            #leitura das linhas
            linhas = [linha for linha in f.read().splitlines() if linha.strip()]

            if len(linhas) < 5 or linhas[3].strip().lower() != "producoes":
                raise ValueError("O arquivo de gramática deve conter 'variaveis', 'inicial', 'terminais' e 'producoes'")

            #verificação das variáveis
            if not linhas[0].lower().startswith("variaveis:"):
                raise ValueError("A primeira linha deve ser 'variaveis: <lista de variáveis>'")
            variaveis = set(l.strip() for l in linhas[0].split(":")[1].split(','))
            if not variaveis or '' in variaveis:
                raise ValueError("A lista de variáveis não pode estar vazia.")

            #verificação do símbolo inicial
            if not linhas[1].lower().startswith("inicial:"):
                raise ValueError("A segunda linha deve ser 'inicial: <símbolo inicial>'")
            simbolo_inicial = linhas[1].split(":")[1].strip()
            if simbolo_inicial not in variaveis:
                raise ValueError(f"O símbolo inicial '{simbolo_inicial}' não está na lista de variáveis")

            #verificação dos terminais
            if not linhas[2].lower().startswith("terminais:"):
                raise ValueError("A terceira linha deve ser 'terminais: <lista de terminais>'")
            terminais = set(l.strip() for l in linhas[2].split(":")[1].split(','))
            if not terminais or '' in terminais:
                raise ValueError("A lista de terminais não pode estar vazia")
                
            #verificação de intersecção entre variáveis e terminais
            if not variaveis.isdisjoint(terminais):
                raise ValueError(f"Símbolos em comum entre variáveis e terminais: {variaveis.intersection(terminais)}")

            #verificação das produções
            producoes_linhas = linhas[4:]
            if not producoes_linhas:
                raise ValueError("O arquivo de gramática deve conter pelo menos uma produção")

            for i, linha in enumerate(producoes_linhas, 5):
                if ":" not in linha:
                    raise ValueError(f"Erro na linha {i}: Formato de produção inválido. Use 'Variavel: producao'")
                lado_esquerdo, lado_direito = [p.strip() for p in linha.split(":", 1)]

                #verifica se tem um não-terminal do lado esquerdo da produção
                if lado_esquerdo not in variaveis:
                    raise ValueError(f"Erro na linha {i}: A variável '{lado_esquerdo}' não foi declarada")
                
                #garante que cada produção esteja em uma linha
                if "|" in lado_direito:
                    raise ValueError(f"Erro na linha {i}: O formato não permite '|'. Declare cada produção em uma nova linha")

                #verifica cada símbolo do lado direito da produção
                if lado_direito != 'epsilon':
                    for simbolo in lado_direito:
                        if simbolo not in variaveis and simbolo not in terminais:
                            raise ValueError(f"Erro na linha {i}: O símbolo '{simbolo}' na produção '{lado_direito}' não é uma variável nem um terminal válido.")
            
            return True

    except Exception as e:
        print(f"Erro ao verificar o arquivo de gramática: {e}")
        return False


def ler_gramatica(arquivo):
    
    #leitura da gramática
    gramatica = {
        'variaveis': set(),
        'inicial': '',
        'terminais': set(),
        'producoes': {},
    }
    
    with open(arquivo, 'r') as f:
        linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
        
        gramatica['variaveis'] = set(l.strip() for l in linhas[0].split(":")[1].split(','))
        gramatica['inicial'] = linhas[1].split(":")[1].strip()
        gramatica['terminais'] = set(l.strip() for l in linhas[2].split(":")[1].split(','))

        #processando as produções
        for linha in linhas[4:]:
            lado_esquerdo, lado_direito = [p.strip() for p in linha.split(":", 1)]#separa os terminais dos não-terminais
            if lado_esquerdo not in gramatica['producoes']:
                gramatica['producoes'][lado_esquerdo] = []#inicialização do não terminal
            gramatica['producoes'][lado_esquerdo].append(lado_direito)#registra as regras da gramática
            
    return gramatica


#LÓGICA DE GERAÇÃO DE CADEIAS
cadeias_geradas = set()
gerador_de_derivacoes = None

def inicializar_gerador_determinístico(gramatica, max_profundidade=10):

    #fila para verificar as derivações de forma sistemática
    fila = [(gramatica['inicial'], [gramatica['inicial']])] #cadeia_atual e derivacao_atual

    while fila:
        cadeia_atual, derivacao_atual = fila.pop(0) #FIFO para busca em largura
        
        if len(derivacao_atual) > max_profundidade:#limitador para evitar cadeias muito grandes e não entrar em loop
            continue

        pos_nao_terminal = -1
        for i, simbolo in enumerate(cadeia_atual):
            if simbolo in gramatica['variaveis']:
                pos_nao_terminal = i#pega o não-terminal mais à esquerda
                break
        
        #se não há mais não-terminais, é uma cadeia final.
        if pos_nao_terminal == -1:
            if cadeia_atual not in cadeias_geradas:
                cadeias_geradas.add(cadeia_atual)
                yield (cadeia_atual, derivacao_atual)#retorna a cadeia gerada
            continue

        #expande o não-terminal mais à esquerda
        nao_terminal = cadeia_atual[pos_nao_terminal]
        producoes_possiveis = gramatica['producoes'].get(nao_terminal, [])

        #adiciona novas derivações à fila
        for producao_escolhida in reversed(producoes_possiveis):#reverse para entrar na ordem correta na fila
            #isola a variável que será substituída
            prefixo = cadeia_atual[:pos_nao_terminal]
            sufixo = cadeia_atual[pos_nao_terminal + 1:]
            
            nova_cadeia = prefixo + (producao_escolhida if producao_escolhida != 'epsilon' else '') + sufixo
            
            nova_derivacao = list(derivacao_atual)#cria cópia
            nova_derivacao.append(nova_cadeia)
            
            fila.insert(0, (nova_cadeia, nova_derivacao))#cria o novo estado e insere no início da fila


def gerar_cadeia_rapida(gramatica):
    
    #gera a próxima cadeia única de forma determinística usando o gerador.
    global gerador_de_derivacoes
    if gerador_de_derivacoes is None:
        gerador_de_derivacoes = inicializar_gerador_determinístico(gramatica)
    
    try:
        cadeia, derivacao = next(gerador_de_derivacoes)
        derivacao_formatada = " => ".join(derivacao)
        print(f"Derivação: {derivacao_formatada}")
        return cadeia
    except StopIteration:
        return "Não foi possível gerar mais cadeias únicas."

def gerar_cadeia_detalhada(gramatica):
    
    #gera uma cadeia passo a passo com a escolha do usuário    
    producao = gramatica['inicial']
    derivacao_formatada = [producao]

    while any(s in gramatica['variaveis'] for s in producao):
        print(f"\nEstado atual: {producao}")
        
        #encontra o não-terminal mais à esquerda
        nao_terminal_pos = -1
        nao_terminal = ''
        for i, simbolo in enumerate(producao):
            if simbolo in gramatica['variaveis']:
                nao_terminal_pos = i
                nao_terminal = simbolo
                break
        
        producoes_possiveis = gramatica['producoes'][nao_terminal]
        
        print(f"Escolha uma produção para a variável '{nao_terminal}':")
        for i, p in enumerate(producoes_possiveis, 1):
            print(f"{i}. {nao_terminal} -> {p}")

        while True:
            try:
                escolha = int(input("Digite o número da produção desejada: "))
                if 1 <= escolha <= len(producoes_possiveis):
                    producao_escolhida = producoes_possiveis[escolha - 1]
                    break
                else:
                    print("Escolha inválida. Tente novamente.")
            except ValueError:
                print("Entrada inválida. Digite um número.")

        #aplica a produção
        prefixo = producao[:nao_terminal_pos]
        sufixo = producao[nao_terminal_pos + 1:]
        
        if producao_escolhida == 'epsilon':
            producao = prefixo + sufixo
        else:
            producao = prefixo + producao_escolhida + sufixo
        
        derivacao_formatada.append(producao)
        print(f"Derivação até o momento: {' => '.join(derivacao_formatada)}")

    return producao

# --- FUNÇÃO PRINCIPAL ---

def main():
    #função principal que executa o programa
    global gerador_de_derivacoes, cadeias_geradas
    
    try:
        arquivo = input("Digite o caminho para o arquivo da gramática: ")
        if not verificar_existencia_arquivo(arquivo):
            return
        if not verificar_arquivo_gramatica(arquivo):
            return
        
        gramatica = ler_gramatica(arquivo)
        
        while True:
            #reseta o gerador a cada nova escolha de menu para consistência
            gerador_de_derivacoes = None
            cadeias_geradas = set()

            print("\n" + "="*30)
            print("Escolha o modo de geração:")
            print("1. Modo Rápido (Geração Determinística)")
            print("2. Modo Detalhado (Interativo)")
            print("3. Sair")
            print("="*30)
            
            try:
                opcao = int(input("Escolha uma opção: "))
            except ValueError:
                print("Opção inválida! Por favor, insira um número.")
                continue

            if opcao == 1:
                print("\n--- Modo Rápido ---")
                for _ in range(5): #gera 5 cadeias para demonstrar
                    cadeia = gerar_cadeia_rapida(gramatica)
                    print(f"Cadeia gerada: '{cadeia}'\n")
                    if "Não foi possível" in cadeia:
                        break
                print("Retornando ao menu principal...")

            elif opcao == 2:
                print("\n--- Modo Detalhado ---")
                cadeia = gerar_cadeia_detalhada(gramatica)
                print(f"\nCadeia final gerada: '{cadeia}'")
            
            elif opcao == 3:
                print("Encerrando o programa.")
                break
            
            else:
                print("Opção inválida! Tente novamente.")

    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()