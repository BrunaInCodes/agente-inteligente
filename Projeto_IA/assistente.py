from nltk import word_tokenize, corpus
from inicializador_modelo import *
from threading import Thread
from transcritor import *
import sounddevice as sd
import soundfile as sf
import secrets
import json
import os

import planilha

CONFIGURACAO = "config.json"

LINGUAGEM           = "portuguese"
TAXA_AMOSTRAGEM     = 16_000
TEMPO_GRAVACAO      = 5
CAMINHO_AUDIO_FALAS = "temp"

ATUADORES = [
    {
        "nome":    "planilha",
        "iniciar": planilha.iniciar,
        "atuar":   planilha.atuar
    }
]

# palavras que indicam quantidade — numeros e unidades de medida
PALAVRAS_QUANTIDADE = [
    "um", "uma", "dois", "duas", "tres", "quatro", "cinco",
    "seis", "sete", "oito", "nove", "dez", "meia", "meio",
    "pacote", "pacotes", "caixa", "caixas", "garrafa", "garrafas",
    "litro", "litros", "quilo", "quilos", "grama", "gramas",
    "unidade", "unidades", "saco", "sacos", "lata", "latas",
    "duzia", "dezena", "kilo", "kilos", "kg", "ml", "gr", "pote", "potes"
]

# todos os sinonimos de acoes — usados para limpar os tokens na hora de achar o produto
TODOS_SINONIMOS = {
    "adicionar", "inserir", "colocar", "incluir", "anotar",
    "exibir", "mostrar", "listar", "ver", "apresentar",
    "remover", "deletar", "apagar", "excluir", "tirar", "retirar",
    "organizar", "ordenar", "classificar", "atualizar", "reorganizar",
    "lista", "compras", "itens", "dados", "planilha"
}

def iniciar_assistente(dispositivo):
    iniciado, processador, modelo = iniciar_modelo(MODELO, dispositivo)

    palavras_de_parada = set(corpus.stopwords.words(LINGUAGEM))

    with open(CONFIGURACAO, "r", encoding="utf-8") as arquivo_configuracao:
        configuracoes = json.load(arquivo_configuracao)
        acoes = configuracoes["acoes"]
        arquivo_configuracao.close()

    for atuador in ATUADORES:
        atuador["iniciar"]()

    os.makedirs(CAMINHO_AUDIO_FALAS, exist_ok=True)

    return iniciado, processador, modelo, palavras_de_parada, acoes

def capturar_fala():
    print("\nfale alguma coisa...")

    fala = sd.rec(int(TEMPO_GRAVACAO * TAXA_AMOSTRAGEM), samplerate=TAXA_AMOSTRAGEM, channels=1)
    sd.wait()

    print("fala capturada!")

    return fala

def gravar_fala(fala):
    gravado, arquivo = False, f"{CAMINHO_AUDIO_FALAS}/{secrets.token_hex(32).lower()}.wav"

    try:
        sf.write(arquivo, fala, TAXA_AMOSTRAGEM)
        gravado = True
    except Exception as e:
        print(f"ocorreu um erro gravando o audio: {e}")

    return gravado, arquivo

def processar_transcricao(transcricao, palavras_de_parada):
    tokens = word_tokenize(transcricao, language=LINGUAGEM)
    # remove apenas pontuacao, mantém todas as palavras para extrair contexto
    tokens = [t for t in tokens if t.isalpha()]
    return tokens

def _identificar_acao(tokens, acoes):
    """Varre os tokens e retorna o nome da acao cujo sinonimo aparece primeiro."""
    for token in tokens:
        for acao in acoes:
            if token in acao.get("sinonimos", [acao["nome"]]):
                return acao["nome"]
    return None

def _identificar_quantidade(tokens):
    """
    Coleta todas as palavras de quantidade presentes nos tokens.
    Ex: ['dois', 'pacotes'] → 'dois pacotes'
        ['um']              → 'um'
    """
    qtd_parts = [t for t in tokens if t in PALAVRAS_QUANTIDADE or t.isdigit()]
    return " ".join(qtd_parts) if qtd_parts else "1"

def _identificar_produto(tokens, quantidade_str):
    """
    Remove sinonimos de acao e tokens de quantidade.
    O que sobrar é o produto.
    Ex: ['adicionar', 'dois', 'pacotes', 'arroz'] → 'arroz'
    """
    ignorar = TODOS_SINONIMOS | set(quantidade_str.split())
    produto_tokens = [t for t in tokens if t not in ignorar]
    return " ".join(produto_tokens) if produto_tokens else None

def validar_comando(tokens, acoes):
    valido    = False
    acao_nome = None
    produto   = None
    quantidade = None
    categoria  = None  # mantido para compatibilidade com o atuador

    acao_nome = _identificar_acao(tokens, acoes)
    if not acao_nome:
        return valido, acao_nome, produto, quantidade, categoria

    if acao_nome == "adicionar":
        quantidade = _identificar_quantidade(tokens)
        produto    = _identificar_produto(tokens, quantidade)
        if produto:
            valido = True

    elif acao_nome == "exibir":
        valido = True

    elif acao_nome == "remover":
        # produto = qualquer token que nao seja sinonimo de acao
        candidatos = [t for t in tokens if t not in TODOS_SINONIMOS]
        if candidatos:
            produto = candidatos[0]
            valido  = True

    elif acao_nome == "organizar":
        valido = True

    return valido, acao_nome, produto, quantidade, categoria

def executar_comando(acao, produto, quantidade, categoria):
    for atuador in ATUADORES:
        atuacao = Thread(
            target=atuador["atuar"],
            args=[acao, produto, quantidade, categoria]
        )
        atuacao.start()

if __name__ == "__main__":
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"

    iniciado, processador, modelo, palavras_de_parada, acoes = iniciar_assistente(dispositivo)
    if iniciado:
        print("\n=== ASSISTENTE DE LISTA DE COMPRAS INICIADO ===")


        while True:
            fala = capturar_fala()
            gravado, arquivo = gravar_fala(fala)

            if gravado:
                print("realizando transcricao...")

                fala_carregada, _ = torchaudio.load(arquivo)
                transcricao = transcrever(dispositivo, fala_carregada.squeeze(), modelo, processador)
                transcricao = transcricao.lower()
                print(f"fala      : {transcricao}")

                tokens = processar_transcricao(transcricao, palavras_de_parada)
                print(f"tokens    : {tokens}")

                valido, acao, produto, quantidade, categoria = validar_comando(tokens, acoes)
                print(f"acao      : {acao}")
                print(f"produto   : {produto}")
                print(f"quantidade: {quantidade}")

                if valido:
                    executar_comando(acao, produto, quantidade, categoria)
                else:
                    print("comando invalido")
    else:
        print("nao foi possivel iniciar o assistente")
