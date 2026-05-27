import unittest

from assistente import *

# ── audios gravados com fala natural ────────────────────────────────
# grave cada arquivo falando exatamente as frases abaixo:
#   adicionar item.wav  → "adicionar dois pacotes de arroz"
#   exibir lista.wav    → "mostrar lista"
#   remover item.wav    → "tirar arroz"
#   organizar lista.wav → "atualizar lista"
# ────────────────────────────────────────────────────────────────────
COMANDO_ADICIONAR = "audios/adicionar item.wav"
COMANDO_EXIBIR    = "audios/exibir lista.wav"
COMANDO_REMOVER   = "audios/remover item.wav"
COMANDO_ORGANIZAR = "audios/organizar lista.wav"

class TestesListaDeCompras(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"

        cls.iniciado, cls.processador, cls.modelo, cls.palavras_de_parada, cls.acoes = iniciar_assistente(cls.dispositivo)

        return super().setUpClass()

    def testar_01_assistente_iniciado(self):
        self.assertTrue(self.iniciado)

    def testar_02_adicionar_item(self):
        # frase gravada: "adicionar dois pacotes de arroz"
        fala = carregar_fala(COMANDO_ADICIONAR)
        self.assertIsNotNone(fala)

        transcricao = transcrever(self.dispositivo, fala, self.modelo, self.processador)
        self.assertIsNotNone(transcricao)

        tokens = processar_transcricao(transcricao, self.palavras_de_parada)
        self.assertIsNotNone(tokens)

        valido, acao, produto, quantidade, _ = validar_comando(tokens, self.acoes)
        self.assertTrue(valido)
        self.assertEqual(acao, "adicionar")
        self.assertIsNotNone(produto)
        self.assertIsNotNone(quantidade)

    def testar_03_exibir_lista(self):
        # frase gravada: "mostrar lista"
        fala = carregar_fala(COMANDO_EXIBIR)
        self.assertIsNotNone(fala)

        transcricao = transcrever(self.dispositivo, fala, self.modelo, self.processador)
        self.assertIsNotNone(transcricao)

        tokens = processar_transcricao(transcricao, self.palavras_de_parada)
        self.assertIsNotNone(tokens)

        valido, acao, _, _, _ = validar_comando(tokens, self.acoes)
        self.assertTrue(valido)
        self.assertEqual(acao, "exibir")

    def testar_04_remover_item(self):
        # frase gravada: "tirar arroz"
        fala = carregar_fala(COMANDO_REMOVER)
        self.assertIsNotNone(fala)

        transcricao = transcrever(self.dispositivo, fala, self.modelo, self.processador)
        self.assertIsNotNone(transcricao)

        tokens = processar_transcricao(transcricao, self.palavras_de_parada)
        self.assertIsNotNone(tokens)

        valido, acao, produto, _, _ = validar_comando(tokens, self.acoes)
        self.assertTrue(valido)
        self.assertEqual(acao, "remover")
        self.assertIsNotNone(produto)

    def testar_05_organizar_lista(self):
        # frase gravada: "atualizar lista"
        fala = carregar_fala(COMANDO_ORGANIZAR)
        self.assertIsNotNone(fala)

        transcricao = transcrever(self.dispositivo, fala, self.modelo, self.processador)
        self.assertIsNotNone(transcricao)

        tokens = processar_transcricao(transcricao, self.palavras_de_parada)
        self.assertIsNotNone(tokens)

        valido, acao, _, _, _ = validar_comando(tokens, self.acoes)
        self.assertTrue(valido)
        self.assertEqual(acao, "organizar")

unittest.main()
