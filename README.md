# 🎙️ Agente Inteligente de Lista de Compras por Voz

Gerencie sua lista de compras usando comandos de voz em **português brasileiro**. O agente transcreve sua fala em tempo real, interpreta o comando e atualiza automaticamente uma planilha `.xlsx`.

Funciona de **duas formas**: via interface web no navegador ou direto pelo terminal — você escolhe como prefere usar.

---

## ✨ O que você pode fazer

| Comando de exemplo | Ação |
|---|---|
| *"adicionar dois pacotes de arroz"* | Adiciona item com quantidade |
| *"mostrar lista"* | Exibe todos os itens |
| *"tirar arroz"* | Remove um item pelo nome |
| *"atualizar lista"* | Organiza em ordem alfabética |

---

## 🖥️ Duas formas de usar

### 🌐 Via interface web (recomendado)

Inicie o servidor Flask e acesse pelo navegador. Você terá uma interface visual para gravar sua voz, ver a lista e acompanhar o resultado dos comandos em tempo real.

```bash
python servidor.py
# acesse http://localhost:5000
```

### 💻 Via terminal

Prefere rodar tudo no terminal sem abrir o navegador? Execute o assistente diretamente:

```bash
python assistente.py
```

O assistente captura o áudio pelo microfone, transcreve, interpreta o comando e exibe o resultado no próprio terminal — simples e direto.

---

## 🛠️ Tecnologias utilizadas

- **[Wav2Vec2](https://huggingface.co/lgris/wav2vec2-large-xlsr-open-brazilian-portuguese-v2)** — reconhecimento de fala em português brasileiro
- **Hugging Face Transformers** — carregamento e inferência do modelo
- **NLTK** — tokenização e processamento de linguagem natural
- **Flask** — servidor web local com API REST
- **openpyxl** — leitura e escrita da planilha `.xlsx`
- **sounddevice / soundfile** — captura de áudio em tempo real

---

## 📋 Pré-requisitos

- Python 3.9 ou superior
- Microfone conectado e configurado
- (Opcional) GPU com CUDA para inferência mais rápida

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/BrunaInCodes/agente-inteligente.git
cd agente-inteligente
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Baixe os recursos do NLTK

Execute uma vez no terminal Python:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### 4. Escolha como quer rodar

**Interface web:**
```bash
python servidor.py
# abra http://localhost:5000 no navegador
```

**Terminal:**
```bash
python assistente.py
```

> Na primeira execução, o modelo Wav2Vec2 será baixado automaticamente (~1 GB). Isso pode levar alguns minutos dependendo da sua conexão. Nas próximas vezes, o modelo já estará em cache.

---

## 🗂️ Estrutura do projeto

```
agente-inteligente/
├── assistente.py           # Lógica principal: captura, tokenização e validação
├── servidor.py             # API Flask + modo web (http://localhost:5000)
├── transcritor.py          # Carregamento do modelo e transcrição de áudio
├── inicializador_modelo.py # Utilitário para carregar o Wav2Vec2
├── planilha.py             # CRUD da lista de compras no .xlsx
├── testes.py               # Testes automatizados dos comandos
├── config.json             # Configuração de ações e sinônimos
├── lista_de_compras.xlsx   # Planilha gerada automaticamente
├── requirements.txt
└── index.html              # Interface web
```

---

## ⚙️ Configuração

Edite o `config.json` para personalizar os sinônimos de cada ação:

```json
{
  "planilha": "lista_de_compras.xlsx",
  "acoes": [
    {
      "nome": "adicionar",
      "sinonimos": ["adicionar", "inserir", "colocar", "incluir", "anotar"]
    }
  ]
}
```

---

## 🧪 Rodando os testes

Os testes usam arquivos de áudio pré-gravados. Crie a pasta `audios/` e grave os seguintes arquivos:

| Arquivo | Frase a gravar |
|---|---|
| `audios/adicionar item.wav` | *"adicionar dois pacotes de arroz"* |
| `audios/exibir lista.wav` | *"mostrar lista"* |
| `audios/remover item.wav` | *"tirar arroz"* |
| `audios/organizar lista.wav` | *"atualizar lista"* |

Depois execute:

```bash
python testes.py
```

---

## 🐛 Problemas comuns

**O modelo demora muito para carregar**
> Normal na primeira execução — o download é de ~1 GB. Nas próximas vezes é instantâneo.

**Erro com microfone / sounddevice**
> Verifique se o microfone está selecionado como dispositivo de entrada padrão no sistema operacional.

**GPU não detectada**
> O projeto roda normalmente na CPU. Para usar GPU, instale o PyTorch com suporte a CUDA: veja [pytorch.org](https://pytorch.org/get-started/locally/).

**Comando não reconhecido**
> Fale de forma clara e use os sinônimos definidos no `config.json`. Você pode adicionar novas palavras-gatilho diretamente nesse arquivo sem mexer no código.

