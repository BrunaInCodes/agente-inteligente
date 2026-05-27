from flask import Flask, jsonify, request, send_from_directory
from inicializador_modelo import *
from transcritor import *
from assistente import (
    iniciar_assistente,
    processar_transcricao,
    validar_comando,
    CAMINHO_AUDIO_FALAS
)
import sounddevice as sd
import soundfile as sf
import torchaudio
import secrets
import json
import os

import planilha

app = Flask(__name__, static_folder=".")

CONFIGURACAO    = "config.json"
TAXA_AMOSTRAGEM = 16_000

# estado global da gravacao
_gravando      = False
_stream        = None
_frames        = []
_arquivo_atual = None

dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
iniciado, processador, modelo, palavras_de_parada, acoes = iniciar_assistente(dispositivo)

os.makedirs(CAMINHO_AUDIO_FALAS, exist_ok=True)

# ── pagina principal ─────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ── GET /api/itens ───────────────────────────────────────────────────
@app.route("/api/itens", methods=["GET"])
def listar_itens():
    try:
        import openpyxl
        with open(CONFIGURACAO, "r", encoding="utf-8") as f:
            config = json.load(f)

        nome_planilha = config["planilha"]

        if not os.path.exists(nome_planilha):
            return jsonify({"itens": []})

        wb = openpyxl.load_workbook(nome_planilha)
        ws = wb.active

        itens = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] is not None:
                itens.append({
                    "id":         row[0],
                    "produto":    row[1],
                    "quantidade": row[2],
                    "status":     row[3]
                })

        return jsonify({"itens": itens})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ── POST /api/iniciar_gravacao ───────────────────────────────────────
@app.route("/api/iniciar_gravacao", methods=["POST"])
def iniciar_gravacao():
    global _gravando, _stream, _frames, _arquivo_atual

    if _gravando:
        # reseta o estado caso tenha ficado travado
        _gravando = False
        try:
            sd.stop()
        except:
            pass

    try:
        _frames        = []
        _arquivo_atual = f"{CAMINHO_AUDIO_FALAS}/{secrets.token_hex(16)}.wav"
        _gravando      = True

        def callback(indata, frames, time, status):
            if _gravando:
                _frames.append(indata.copy())

        _stream = sd.InputStream(
            samplerate=TAXA_AMOSTRAGEM,
            channels=1,
            callback=callback
        )
        _stream.start()

        return jsonify({"mensagem": "gravacao iniciada"})
    except Exception as e:
        _gravando = False
        return jsonify({"erro": str(e)}), 500

# ── POST /api/parar_gravacao ─────────────────────────────────────────
@app.route("/api/parar_gravacao", methods=["POST"])
def parar_gravacao():
    global _gravando, _stream, _frames, _arquivo_atual

    if not _gravando:
        return jsonify({"erro": "nenhuma gravacao em andamento"}), 400

    dados     = request.get_json(silent=True) or {}
    cancelar  = dados.get("cancelar", False)

    try:
        _gravando = False
        if _stream:
            _stream.stop()
            _stream.close()
            _stream = None

        if cancelar:
            _frames        = []
            _arquivo_atual = None
            return jsonify({"mensagem": "gravacao cancelada"})

        if not _frames:
            return jsonify({"erro": "nenhum audio capturado"}), 400

        import numpy as np
        audio = np.concatenate(_frames, axis=0)
        sf.write(_arquivo_atual, audio, TAXA_AMOSTRAGEM)

        fala_carregada, _ = torchaudio.load(_arquivo_atual)
        transcricao = transcrever(dispositivo, fala_carregada.squeeze(), modelo, processador)
        transcricao = transcricao.lower()
        print(f"transcricao: {transcricao}")

        tokens = processar_transcricao(transcricao, palavras_de_parada)
        valido, acao, produto, quantidade, _ = validar_comando(tokens, acoes)

        if not valido:
            return jsonify({
                "transcricao": transcricao,
                "valido":      False,
                "mensagem":    "comando nao reconhecido"
            })

        if acao == "adicionar":
            planilha.adicionar(produto, quantidade)
            mensagem = f"'{produto}' adicionado com sucesso!"
        elif acao == "exibir":
            planilha.exibir()
            mensagem = "lista exibida no terminal"
        elif acao == "remover":
            planilha.remover(produto)
            mensagem = f"'{produto}' removido com sucesso!"
        elif acao == "organizar":
            planilha.organizar()
            mensagem = "lista organizada com sucesso!"
        else:
            mensagem = "acao desconhecida"

        return jsonify({
            "transcricao": transcricao,
            "valido":      True,
            "acao":        acao,
            "mensagem":    mensagem
        })

    except Exception as e:
        _gravando = False
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    print("=== SERVIDOR DO ASSISTENTE DE LISTA DE COMPRAS ===")
    print("acesse: http://localhost:5000")
    app.run(debug=False, port=5000, threaded=True)
