from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torchaudio
import torch

MODELO = "lgris/wav2vec2-large-xlsr-open-brazilian-portuguese-v2"

AUDIOS = [
    "audios/adicionar item.wav",
    "audios/exibir lista.wav",
    "audios/remover item.wav",
    "audios/organizar lista.wav"
]

TAXA_AMOSTRAGEM = 16_000

def iniciar(identificador_modelo, dispositivo="cpu"):
    iniciado, processador, modelo = False, None, None

    try:
        processador = Wav2Vec2Processor.from_pretrained(identificador_modelo)
        modelo = Wav2Vec2ForCTC.from_pretrained(identificador_modelo).to(dispositivo)

        iniciado = True
    except Exception as e:
        print(f"erro inicializando o modelo: {e}")

    return iniciado, processador, modelo

def carregar_fala(audio_fala):
    audio, amostragem = torchaudio.load(audio_fala)

    # verifica se audio tem mais de um canal
    # ou seja, verifica se eh stereo
    if audio.shape[0] > 1:
        # sendo stereo, transforma para mono
        # ou seja, um canal somente, que basta
        # para o reconhecimento de fala
        audio = torch.mean(audio, dim=0, keepdim=True)

    # cria um adaptador para degradar a qualidade do audio
    adaptador_amostragem = torchaudio.transforms.Resample(amostragem, TAXA_AMOSTRAGEM)

    # degrada a qualidade do audio para 16.000
    # ex.: os audios de teste tem uma taxa de amostra de 44.100
    audio = adaptador_amostragem(audio)

    return audio.squeeze()

def transcrever(dispositivo, fala, modelo, processador):
    saida = processador(fala, return_tensors="pt", sampling_rate=TAXA_AMOSTRAGEM).input_values.to(dispositivo)
    saida = modelo(saida).logits

    predicao = torch.argmax(saida, dim=-1)
    transcricao = processador.batch_decode(predicao)[0]

    return transcricao.lower()

if __name__ == "__main__":
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"

    iniciado, processador, modelo = iniciar(MODELO, dispositivo=dispositivo)
    if iniciado:
        print("modelo iniciado com sucesso")

        for audio in AUDIOS:
            fala = carregar_fala(audio)
            transcricao = transcrever(dispositivo, fala, modelo, processador)

            print(f"transcrição: {transcricao}")
