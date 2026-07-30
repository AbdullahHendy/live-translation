

<div align="center">

# Live-Translation

**Un sistema de traducción de voz a texto en tiempo real construido sobre una arquitectura modular cliente-servidor.**

[![Build](https://github.com/AbdullahHendy/live-translation/actions/workflows/ci.yml/badge.svg)](https://github.com/AbdullahHendy/live-translation/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/live-translation)](https://pypi.org/project/live-translation/)
[![License](https://img.shields.io/github/license/AbdullahHendy/live-translation.svg)](https://github.com/AbdullahHendy/live-translation/blob/main/LICENSE)
[![Python >= 3.11](https://img.shields.io/badge/Python-%3E=3.11-%231f425f?logo=python)](https://www.python.org/downloads/)
</br>
[![Architecture](https://img.shields.io/badge/Architecture-Client--Server-informational)](https://en.wikipedia.org/wiki/Client%E2%80%93server_model)
[![WebSocket](https://img.shields.io/badge/Protocol-WebSocket-brightgreen?logo=websocket)](https://en.wikipedia.org/wiki/WebSocket)
[![Audio](https://img.shields.io/badge/Audio-16bit_PCM@16kHz-brightgreen?logo=sound)](https://en.wikipedia.org/wiki/Pulse-code_modulation)
[![Streaming](https://img.shields.io/badge/Streaming-Real--time-brightgreen?logo=livejournal)](https://en.wikipedia.org/wiki/Streaming_media)
[![Codec](https://img.shields.io/badge/Audio_Codec-Opus-blueviolet?logo=opus)](https://en.wikipedia.org/wiki/Opus_(audio_format))
</br>
[![Last Commit](https://img.shields.io/github/last-commit/AbdullahHendy/live-translation.svg)](https://github.com/AbdullahHendy/live-translation/commits/main)
[![Issues](https://img.shields.io/github/issues/AbdullahHendy/live-translation)](https://github.com/AbdullahHendy/live-translation/issues)
[![Stars](https://img.shields.io/github/stars/AbdullahHendy/live-translation?style=social)](https://github.com/AbdullahHendy/live-translation/stargazers)
</br>
[![Code Style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/AbdullahHendy/live-translation/blob/main/ruff.toml)
[![codecov](https://codecov.io/github/AbdullahHendy/live-translation/graph/badge.svg)](https://codecov.io/github/AbdullahHendy/live-translation)
</br>
[![Client Examples](https://img.shields.io/badge/Client_Examples-Included-blueviolet?logo=github)](https://github.com/AbdullahHendy/live-translation/tree/main/examples)
[![Node.js](https://img.shields.io/badge/Examples-Node.js-green?logo=node.js)](https://github.com/AbdullahHendy/live-translation/tree/main/examples/clients/nodejs)
[![Browser JS](https://img.shields.io/badge/Examples-Browser_JS-yellow?logo=javascript)](https://github.com/AbdullahHendy/live-translation/tree/main/examples/clients/browser_js)
[![C#](https://img.shields.io/badge/Examples-C%23-239120?logo=c-sharp&logoColor=white)](https://github.com/AbdullahHendy/live-translation/tree/main/examples/clients/csharpclient)
[![Go](https://img.shields.io/badge/Examples-Go-00ADD8?logo=go)](https://github.com/AbdullahHendy/live-translation/tree/main/examples/clients/go_client)
[![Kotlin/Android](https://img.shields.io/badge/Examples-Kotlin%2FAndroid-3DDC84?logo=kotlin&logoColor=white)](https://github.com/AbdullahHendy/live-translation/tree/main/examples/clients/android)
</br>
[![Powered by Opus-MT](https://img.shields.io/badge/Powered%20by-Opus--MT-blue)](https://huggingface.co/Helsinki-NLP)
[![Powered by Whisper](https://img.shields.io/badge/Powered%20by-Whisper-green)](https://github.com/openai/whisper)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
</div>

---

## Demos

> **NOTA**: Este proyecto ***no*** está diseñado como una aplicación de traducción lista para usar en navegadores web. En su lugar, sirve como un ***facilitador fundamental*** para construir [experiencias de traducción en tiempo real](https://github.com/AbdullahHendy/live-translation/tree/main/examples).
>

### 🌐 Experiencia del Cliente en el Navegador

*Un cliente de ejemplo en JavaScript para el servidor de ***live translation****

*Ver [Bajo el Capó](#-under-the-hood)*

<a href="https://github.com/AbdullahHendy/live-translation/blob/main/doc/browser_js.gif?raw=true" target="_blank">
  <img src="https://github.com/AbdullahHendy/live-translation/blob/main/doc/browser_js.gif?raw=true" alt="Browser-Client Demo" />
</a>

### 🪛 Bajo el Capó

*A la izquierda, el servidor [CLI](#cli) de ***live translation****

*A la derecha, el cliente [CLI](#cli) de ***live translation****

*Para profundizar en más formas de usar el servidor y clientes de ***live translation***, consulte la sección [Uso](#-usage)*

<a href="https://github.com/AbdullahHendy/live-translation/blob/main/doc/demo.gif?raw=true" target="_blank">
  <img src="https://github.com/AbdullahHendy/live-translation/blob/main/doc/demo.gif?raw=true" alt="Server-Client Demo" />
</a>

---

## 👷🏼‍♂️ Descripción General de la Arquitectura

***El diagrama omite detalles más finos***

<img src="https://github.com/AbdullahHendy/live-translation/blob/main/doc/live-translation-pipeline.png?raw=true" alt="Architecture Diagram" />

---

## ⭐ Características

- Captura de voz en tiempo real usando **PyAudio**
- Detección de Actividad de Voz (VAD) usando **Silero** para un procesamiento más eficiente
- Transcripción de voz a texto usando **Whisper** de OpenAI
- Traducción de transcripciones usando **OpusMT** de Helsinki-NLP
- **Transmisión WebSocket de dúplex completo** entre cliente y servidor
- Compresión de audio mediante soporte para el codec **Opus** para un menor uso de ancho de banda
- Diseño multihilo para procesamiento paralelo
- Registro opcional del servidor:
  - Imprimir en **stdout**
  - Guardar registros de transcripción/traducción en un archivo estructurado **.jsonl**
- Diseñado para:
  - Uso simple de **CLI** (***live-translate-server***, ***live-translate-client***)
  - Uso de **API de Python** (***LiveTranslationServer***, ***LiveTranslationClient***) con soporte asíncrono para integración en sistemas más grandes

---

## 📜 Requisitos Previos

Antes de ejecutar el proyecto, debe instalar las siguientes dependencias del sistema:
### **Linux**
> **NOTA**: El cliente captura audio como **PCM mono de 16 kHz**. En sistemas que usan dispositivos ALSA crudos, abrir el flujo de audio puede fallar si el dispositivo de entrada predeterminado no admite este formato directamente. Se recomienda usar **servidores de sonido PulseAudio o PipeWire (incluidos sus niveles/plugins de compatibilidad ALSA)**, ya que proporcionan remuestreo y conversión de formato automáticos, por ejemplo, los paquetes `pipewire-alsa`, `pulseaudio-alsa` o paquetes específicos de la distribución para usuarios de **PipeWire/PulseAudio**.
>
* **Debian**
  - [**PortAudio**](https://www.portaudio.com/)
    ```bash
    sudo apt install portaudio19-dev
    ```
  - [**Puentes PipeWire/PulseAudio**](https://wiki.debian.org/PipeWire) (ver **NOTA:** anterior)
    ```bash
    sudo apt install pipewire-alsa # Usuarios de PipeWire. También ver https://wiki.debian.org/PipeWire#Installation para versiones antiguas de Debian
    sudo apt install pulseaudio    # Usuarios de PulseAudio
    ```
* **Arch**
  - [**PortAudio**](https://www.portaudio.com/)
    ```bash
    sudo pacman -Syu portaudio 
    ```
  - [**Puentes PipeWire/PulseAudio**](https://wiki.archlinux.org/title/PipeWire) (ver **NOTA:** anterior)
    ```bash
    sudo pacman -Syu pipewire-alsa   # Usuarios de PipeWire
    sudo pacman -Syu pulseaudio-alsa # Usuarios de PulseAudio
    ```
### **MacOS**
- [**PortAudio**](https://www.portaudio.com/) (para manejo de entrada de audio)
  ```bash
  brew install portaudio
  ```
---

## 📥 Instalación

*(RECOMENDADO): instale este paquete dentro de un entorno virtual para evitar conflictos de dependencias.*
```bash
python -m venv .venv
source .venv/bin/activate
```

**Instale** el [paquete PyPI](https://pypi.org/project/live-translation/):
```bash
pip install live-translation
```

**Verifique** la instalación:
```bash
python -c "import live_translation; print(f'live-translation installed successfully\n{live_translation.__version__}')"
```

---

## 🚀 Uso

> **NOTA**: Puede ignorar con seguridad advertencias similares que podrían aparecer en sistemas **Linux** cuando el cliente intenta abrir el micrófono:
>
> ALSA lib pcm_dsnoop.c:567:(snd_pcm_dsnoop_open) unable to open slave
> ALSA lib pcm_dmix.c:1000:(snd_pcm_dmix_open) unable to open slave
> ALSA lib pcm.c:2722:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.rear
> ALSA lib pcm.c:2722:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.center_lfe
> ALSA lib pcm.c:2722:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.side
> ALSA lib pcm_dmix.c:1000:(snd_pcm_dmix_open) unable to open slave
> Cannot connect to server socket err = No such file or directory
> Cannot connect to server request channel
> jack server is not running or cannot be started
> JackShmReadWritePtr::~JackShmReadWritePtr - Init not done for -1, skipping unlock
> JackShmReadWritePtr::~JackShmReadWritePtr - Init not done for -1, skipping unlock
>

### CLI
* **demo** se puede ejecutar directamente desde la línea de comandos:
  > **NOTA**: Esta es una herramienta CLI de demostración de conveniencia para ejecutar tanto el **servidor** como el **cliente** con configuraciones ***predeterminadas***. Debería usarse solo para una demostración rápida. Se ***recomienda encarecidamente*** iniciar un servidor y un cliente por separado para una personalización completa, como se muestra a continuación.  
  >
  ```bash
  live-translate-demo
  ```

* **server** se puede ejecutar directamente desde la línea de comandos:
  > **NOTA**: Ejecutar el servidor por primera vez descargará los modelos requeridos en la carpeta **Cache** (p. ej., `~/.cache` en Linux). El proceso de descarga en la primera ejecución puede saturar la vista del terminal, llevando a ubicaciones dispersas e impredecibles de los **registros iniciales del servidor**. Se aconseja volver a ejecutar el servidor después de que se descarguen todos los modelos para una mejor visualización de los **registros iniciales del servidor**.
  >
  ```bash
  live-translate-server [OPTIONS]
  ```

  **[OPTIONS]**
  ```bash
  usage: live-translate-server [-h] [--silence_threshold SILENCE_THRESHOLD] [--vad_aggressiveness {0,1,2,3,4,5,6,7,8,9}] [--max_buffer_duration {5,6,7,8,9,10}] [--codec {pcm,opus}]
                              [--device {cpu,cuda}] [--whisper_model {tiny,base,small,medium,large,large-v2,large-v3,large-v3-turbo}]
                              [--trans_model {Helsinki-NLP/opus-mt,Helsinki-NLP/opus-mt-tc-big}] [--src_lang SRC_LANG] [--tgt_lang TGT_LANG] [--log {print,file}] [--ws_port WS_PORT]
                              [--transcribe_only] [--version]

  Servidor Live Translation - Configure la configuración de tiempo de ejecución.

  opciones:
    -h, --help            muestra este mensaje de ayuda y sale
    --silence_threshold SILENCE_THRESHOLD
                          Número de segundos consecutivos para detectar SILENCIO.
                          SILENCIO borra el búfer de audio para transcripción/traducción.
                          NOTA: El valor mínimo es 1.5.
                          Predeterminado es 2.
    --vad_aggressiveness {0,1,2,3,4,5,6,7,8,9}
                          Nivel de agresividad de la Detección de Actividad de Voz (VAD) (0-9).
                          Valores más altos significan que el VAD debe estar más seguro para detectar voz frente a silencio.
                          Predeterminado es 8.
    --max_buffer_duration {5,6,7,8,9,10}
                          Duración máxima del búfer de audio en segundos antes de recortarlo.
                          Predeterminado es 7 segundos.
    --codec {pcm,opus}    Codec de audio para comunicación WebSocket ('pcm', 'opus').
                          Predeterminado es 'opus'.
    --device {cpu,cuda}   Dispositivo para procesamiento ('cpu', 'cuda').
                          Predeterminado es 'cpu'.
    --whisper_model {tiny,base,small,medium,large,large-v2,large-v3,large-v3-turbo}
                          Tamaño del modelo Whisper ('tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3', 'large-v3-turbo). 
                          NOTA: Ejecutar modelos grandes como 'large-v3' o 'large-v3-turbo' puede requerir una GPU decente con soporte CUDA para un rendimiento razonable. 
                          NOTA: large-v3-turbo tiene una gran precisión mientras es significativamente más rápido que el modelo original large-v3. ver: https://github.com/openai/whisper/discussions/2363 
                          Predeterminado es 'base'.
    --trans_model {Helsinki-NLP/opus-mt,Helsinki-NLP/opus-mt-tc-big}
                          Modelo de traducción ('Helsinki-NLP/opus-mt', 'Helsinki-NLP/opus-mt-tc-big'). 
                          NOTA: No incluya los idiomas de origen y destino aquí.
                          Predeterminado es 'Helsinki-NLP/opus-mt'.
    --src_lang SRC_LANG   Idioma de entrada/origen para transcripción (p. ej., 'en', 'fr').
                          Predeterminado es 'en'.
    --tgt_lang TGT_LANG   Idioma de destino para traducción (p. ej., 'es', 'de').
                          Predeterminado es 'es'.
    --log {print,file}    Modo de registro opcional para guardar la salida de transcripción.
                            - 'file': Guarda cada resultado en un archivo .jsonl estructurado en ./transcripts/transcript_{TIMESTAMP}.jsonl.
                            - 'print': Imprime cada resultado en stdout.
                          Predeterminado es None (sin registro).
    --ws_port WS_PORT     Puerto WebSocket del servidor.
                          Usado para escuchar audio del cliente y publicar salida (p. ej., 8765).
    --transcribe_only     Modo solo transcripción. No se realizan traducciones.
    --version             Imprime la versión y sale.
  ```

* **client** se puede ejecutar directamente desde la línea de comandos:
  ```bash
  live-translate-client [OPTIONS]
  ```

  **[OPTIONS]**
  ```bash
  usage: live-translate-client [-h] [--server SERVER] [--codec {pcm,opus}] [--version]

  Cliente Live Translation - Transmitir audio al servidor.

  opciones:
    -h, --help          muestra este mensaje de ayuda y sale
    --server SERVER     URI WebSocket del servidor (p. ej., ws://localhost:8765)
    --codec {pcm,opus}  Codec de audio para comunicación WebSocket ('pcm', 'opus').
                        Predeterminado es 'opus'.
    --version           Imprime la versión y sale.
  ```

### API de Python
También puede importar y usar ***live_translation*** directamente en su código Python.
Lo siguiente son ejemplos ***simples*** de ejecutar el servidor y cliente de ***live_translation*** de manera **bloqueante**.
Para ejemplos más detallados que muestran flujos de trabajo **no bloqueantes** y **asíncronos**, consulte [./examples/](https://github.com/AbdullahHendy/live-translation/tree/main/examples).

> **NOTA**: Los ejemplos a continuación asumen que el paquete ***live_translation*** ha sido instalado como se muestra en [Instalación](#-instalación).
>
> **NOTA**: Para ejecutar un ejemplo proporcionado usando la ***API de Python***, consulte las instrucciones en el directorio [./examples/](https://github.com/AbdullahHendy/live-translation/tree/main/examples).

- **Servidor**
  ```python
  from live_translation import LiveTranslationServer, ServerConfig

  def main():
      config = ServerConfig(
          device="cpu",
          ws_port=8765,
          log="print",
          transcribe_only=False,
          codec="opus",
      )

      server = LiveTranslationServer(config)
      server.run(blocking=True)

  # La guardia principal es CRÍTICA para sistemas que usan el método spawn para crear nuevos procesos
  # Este es el caso para Windows y MacOS
  if __name__ == "__main__":
      main()

  ```

- **Cliente**
  ```python
  from live_translation import LiveTranslationClient, ClientConfig

  def parser_callback(entry, *args, **kwargs):
      """Función de devolución de llamada para parsear la salida del servidor.

      Args:
          entry (dict): El mensaje del servidor.
          *args: Argumentos posicionales opcionales pasados desde el cliente.
          **kwargs: Argumentos de palabra clave opcionales pasados desde el cliente.
      """
      print(f"📝 {entry['transcription']}")
      print(f"🌍 {entry['translation']}")

      # Retornar True señala al cliente que se cierre
      return False

  def main():
      config = ClientConfig(
          server_uri="ws://localhost:8765",
          codec="opus",
      )

      client = LiveTranslationClient(config)
      client.run(
          callback=parser_callback,
          callback_args=(),  # Opcional: argumentos posicionales a pasar
          callback_kwargs={},  # Opcional: argumentos de palabra clave a pasar
          blocking=True,
      )

  if __name__ == "__main__":
      main()

  ```

### Integración No Python
Si está escribiendo un **cliente personalizado** o integrando este sistema en otra aplicación, puede interactuar con el servidor directamente usando el protocolo WebSocket.
### Descripción General del Protocolo

El servidor escucha en un extremo WebSocket (predeterminado: `ws://localhost:8765`) y espera que el cliente:

- **Enviar**: audio **PCM codificado** usando el [**codec Opus**](https://en.wikipedia.org/wiki/Opus_(audio_format)) con las siguientes especificaciones:
  - Formato: Entero de 16 bits con signo (`int16`)
  - Frecuencia de muestreo: 16,000 Hz
  - Canales: Mono (1 canal)
  - Tamaño de bloque: 640 muestras = 1280 bytes por mensaje (40 ms)
  - Cada bloque codificado debe enviarse inmediatamente a través del WebSocket
  > **NOTA**: El servidor también admite recibir **PCM sin procesar** usando la opción de servidor ***--codec pcm***. Las especificaciones son idénticas a las anteriores, excepto que no están codificadas.
  >

- **Recibir**: mensajes ***JSON*** estructurados con campos de marca de tiempo, transcripción y traducción
  ```json
  {
    "timestamp": "2025-05-25T12:58:35.259085+00:00",
    "transcription": "Good morning, I hope everyone's doing great.",
    "translation": "Buenos días, espero que todo el mundo esté bien"
  }

### Ejemplos de Cliente
Para ejemplos completamente funcionales, ***pero simples***, en múltiples lenguajes, consulte [./examples/clients](https://github.com/AbdullahHendy/live-translation/tree/main/examples/clients)
Para crear clientes más complejos, consulte el [cliente Python](https://github.com/AbdullahHendy/live-translation/blob/main/live_translation/client/client.py) para obtener orientación.  
Ejemplos disponibles:
- **Node.js**
- **Browser JS**
- **Go**
- **C#**
- **Kotlin/Android**

---

## 🤝 Desarrollo y Contribución

Para contribuir o modificar este proyecto, estos pasos podrían ser útiles:
> **NOTA**: El siguiente flujo de trabajo se desarrolló pensando en sistemas basados en Linux con herramientas de compilación típicas instaladas, p. ej., ***Make***. Es posible que necesite instalar ***Make*** y posiblemente otras herramientas en otros sistemas. Sin embargo, aún puede hacer las cosas manualmente sin ***Make***, por ejemplo, ejecutar pruebas manualmente usando `python -m pytest -s tests/` en lugar de `make test`. 
> Consulte el **Makefile** para más detalles.
>

**Bifurque y Clone** el repositorio:
```bash
git clone git@github.com:<your-username>/live-translation.git
cd live-translation
```

**Cree** un entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate 
```

**Instale** el paquete y sus dependencias en ***modo editable***:
```bash
pip install --upgrade pip
pip install -e .[dev,examples]  # Instalar con dependencias opcionales de ejemplos
```
Esto es **equivalente** a:
```bash
make install
```

**Pruebe** el paquete:
```bash
make test
```

**Compile** el paquete:
```bash
make build
```
> **NOTA**: Compilar realiza ***linting*** y verifica el ***formato*** usando [ruff](https://docs.astral.sh/ruff/). Puede hacerlo por separado usando `make format` y `make lint`. Para reglas de linting y formato, consulte la [configuración de ruff](https://github.com/AbdullahHendy/live-translation/blob/main/ruff.toml).

> **NOTA**: Compilar genera un archivo ***.whl*** que puede instalarse con ***pip*** en un nuevo entorno para pruebas

**Verifique** más comandos ***make*** disponibles
```bash
make help
```

**Para pruebas rápidas**, ejecute el servidor y el cliente dentro del entorno virtual:
```bash
live-translate-server [OPTIONS]
live-translate-client [OPTIONS]
```
> **NOTA**: Dado que el paquete se instaló en modo editable, cualquier cambio se reflejará cuando se ejecuten las herramientas CLI

**Para contribuir**:
- Realice sus cambios en una rama de características
- Asegúrese de que todas las pruebas pasen
- Abra un Pull Request (PR) con una descripción clara de sus cambios

---

## 🌱 Entornos Probados

Este proyecto fue probado y desarrollado en la siguiente configuración del sistema:

- **Arquitectura**: x86_64 (64-bit)
- **Sistema Operativo**: Ubuntu 24.10 (Oracular Oriole)
- **Versión del Kernel**: 6.11.0-18-generic
- **Versión de Python**: 3.12.7
- **Procesador**: 13th Gen Intel(R) Core(TM) i9-13900HX
- **GPU**: GeForce RTX 4070 Max-Q / Mobile [^1]
- **Versión del Controlador NVIDIA**: 560.35.03  
- **Versión del Kit de Herramientas CUDA**: 12.1  
- **Versión de cuDNN**: 9.7.1
- **RAM**: 32GB DDR5
- **Dependencias**: Todas las dependencias requeridas están listadas en `pyproject.toml` y [Requisitos Previos](#-requisitos-previos)

[^1]: CUDA como `DEVICE` probablemente sea necesario para modelos más pesados como `large-v3-turbo` para Whisper. Se necesita la instalación de [**controladores Nvidia**](https://www.nvidia.com/drivers/), [**Kit de Herramientas CUDA**](https://developer.nvidia.com/cuda-downloads) y [**cuDNN**](https://developer.nvidia.com/cudnn-downloads) si se fuera a usar la opción `"cuda"`.

---

## 📈 Mejoras

- **Soporte ARM64**: Asegurar el soporte para sistemas basados en ARM64.
- **Verificación de Diseño de Concurrencia**: Revisar y optimizar el diseño de hilos para garantizar la seguridad entre hilos y prevenir problemas como condiciones de carrera o interbloqueos, etc., revisitar el diseño actual donde ***WebSocketIO*** es un hilo mientras que ***AudioProcessor***, ***Transcriber*** y ***Translator*** son procesos.
- **Registro**: Integrar un registro detallado para rastrear la actividad del sistema, errores y métricas de rendimiento usando un marco de registro más formal.
- **Modelos de Traducción**: Algunos de los modelos descargados en ***Translator*** desde [Hugging Face de OpusMT](https://huggingface.co/Helsinki-NLP) no son los de mejor rendimiento en comparación con los principales modelos del [Ranking de Opus-MT](https://opus.nlpl.eu/dashboard/). Encontrar una forma de descargar automáticamente los modelos de mejor rendimiento usando la entrada del usuario de `src_lang` y `tgt_lang` como se hace actualmente. 
- **Perfilado del Sistema y Guías de Recursos**: Realizar pruebas de rendimiento y documentar el uso de CPU, memoria y GPU en todos los componentes de multiprocesamiento. Por ejemplo, "~35% de uso de CPU en **Intel i9-13900HX** de 24 núcleos", o "Carga de GPU ~20% en **Nvidia RTX 4070** con el modelo Whisper `large-v3-turbo`"). Esto ayudará con los requisitos de hardware y decisiones de despliegue.
- **Protocolo de Acuse de Recibo (Handshake) Adecuado**: En lugar de opciones duplicadas de servidor y cliente (p. ej., --codec), establecer un protocolo de handshake donde, por ejemplo, el servidor anuncie sus capacidades y negocie con el cliente sobre qué opciones usar.
- **Dispositivo de Entrada Configurable**: Actualmente, LiveTranslationClient usa el dispositivo de entrada predeterminado del sistema sin otras opciones. Hacer que use el predeterminado del sistema por defecto, pero con la opción de pasar otros dispositivos a través de Config.  
---

## 📚 Citas
 ```bibtex
  @article{Whisper,
    title = {Robust Speech Recognition via Large-Scale Weak Supervision},
    url = {https://arxiv.org/abs/2212.04356},
    author = {Radford, Alec and Kim, Jong Wook and Xu, Tao and Brockman, Greg and McLeavey, Christine and Sutskever, Ilya},
    publisher = {arXiv},
    year = {2022}
  }

  @misc{Silero VAD,
    author = {Silero Team},
    title = {Silero VAD: pre-trained enterprise-grade Voice Activity Detector (VAD), Number Detector and Language Classifier},
    year = {2021},
    publisher = {GitHub},
    journal = {GitHub repository},
    howpublished = {\url{https://github.com/snakers4/silero-vad}},
    email = {hello@silero.ai}
  }

  @article{tiedemann2023democratizing,
    title={Democratizing neural machine translation with {OPUS-MT}},
    author={Tiedemann, J{\"o}rg and Aulamo, Mikko and Bakshandaeva, Daria and Boggia, Michele and Gr{\"o}nroos, Stig-Arne and Nieminen, Tommi and Raganato, Alessandro and Scherrer, Yves and Vazquez, Raul and Virpioja, Sami},
    journal={Language Resources and Evaluation},
    number={58},
    pages={713--755},
    year={2023},
    publisher={Springer Nature},
    issn={1574-0218},
    doi={10.1007/s10579-023-09704-w}
  }

  @InProceedings{TiedemannThottingal:EAMT2020,
    author = {J{\"o}rg Tiedemann and Santhosh Thottingal},
    title = {{OPUS-MT} — {B}uilding open translation services for the {W}orld},
    booktitle = {Proceedings of the 22nd Annual Conference of the European Association for Machine Translation (EAMT)},
    year = {2020},
    address = {Lisbon, Portugal}
  }
```
