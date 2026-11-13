# 🩸 VESPER: ABISMO · Caçada Profissional (Pixel Art)

![Prévia dos personagens](PREVIA_PERSONAGENS.png)

**Terror assimétrico em pixel art, para um jogador controlar o assassino contra seis sobreviventes com inteligência artificial.** Projeto criado com HTML5/Canvas, JavaScript e Java para Android, com todos os recursos do jogo empacotados localmente no APK.

[![Android APK](https://github.com/V-prof1/Vesper/actions/workflows/android-apk.yml/badge.svg)](https://github.com/V-prof1/Vesper/actions/workflows/android-apk.yml)

## 🐺 Atualização Pro Bots + Moris (2026)

- **14 silhuetas diferentes:** Tecelã é aranha completa de oito patas, Rastreador é lobo quadrúpede, Corvo é ave alada, Autômato é máquina com esteiras, além dos demais corpos especiais.
- **Seis bots estratégicos:** builds com kit médico, lanterna (flashlight) e uma caixa de ferramentas com sabotagem de gancho de uso único.
- **Salvamento em equipe:** bots podem atordoar o assassino que carrega um aliado usando lanternas ou paletes, exigindo posição e tempo corretos.
- **Loops mais fechados:** coberturas adicionais próximas de paletes, com obstáculos que alteram as rotas.
- **14 moris encenados:** 104 quadros cada, com ações temáticas de captura, finalização e desaparecimento no Abismo, em pixel art estilizada.
- **Build automatizada:** o workflow gera sprites, testa os arquivos, compila o APK offline e tenta sincronizar os assets atualizados com o repositório.

## 🎮 O jogo

- **14 assassinos** com silhuetas, velocidades, estilos e poderes diferentes.
- **6 sobreviventes controlados por IA**, capazes de reparar, se curar, resgatar companheiros e executar loops.
- **4 mapas**, sorteados ou selecionados antes da partida.
- Geradores com testes de perícia, paletes, ganchos, portões, ferimentos e finalizações.
- Loja de perks, níveis, experiência e builds, com salvamento local.
- **4.584 quadros de sprites**, distribuídos entre 20 personagens e 14 moris personalizados.
- Controles para celular e PC, modo paisagem no APK.

### 🕹️ Jogar no PC

Baixe o repositório e abra `index.html` ou `JOGAR_NO_PC.html` **mantendo a pasta `assets/` ao lado**. Use WASD para se movimentar; Espaço ou clique para atacar; Q/E/R para habilidades; F para interagir; X para executar; Esc/P para pausar. No celular, use o analógico e os botões na tela.

A versão de navegador é mantida para pré-visualizar e desenvolver o jogo. **O port Android roda offline**: o HTML e os sprites ficam dentro do próprio APK.

## 📱 Como gerar o APK no GitHub

1. Abra a aba **[Actions](https://github.com/V-prof1/Vesper/actions/workflows/android-apk.yml)**.
2. Selecione **VESPER • Android APK** → **Run workflow** → **Run workflow**.
3. Abra a execução concluída e baixe o artefato **`VESPER-ABISMO-PIXEL-APK`**.
4. Extraia o arquivo ZIP do artefato e instale `app-debug.apk` no Android (pode ser necessário permitir instalação desta origem).

O workflow também compila automaticamente quando há mudanças relevantes na branch `main`. **O APK é uma build de teste (debug)**, não assinada para lançamento na Play Store. A compilação e o funcionamento no dispositivo precisam ser confirmados no próprio GitHub/Android.

## 🎨 Sprites e moris

| Ativo | Quantidade | Detalhes |
| --- | ---: | --- |
| Assassinos | 14 | 160 quadros por personagem: parado, andar, correr, atacar, habilidade, dano e carregar. |
| Sobreviventes | 6 | 204 quadros por personagem: movimento, dano, reparar, cair, gancho, saltar, carregar, curar. |
| Moris | 14 | 80 quadros exclusivos por assassino, pixel art 256×144. |
| **Total** | **4.584** | Atlas PNG transparentes, manifest `sprites.json`, animação nearest-neighbor. |

![Quadros de movimento](PREVIA_QUADROS_ANIMACAO.png)

![Prévias das finalizações](PREVIA_MORIS.png)

## 📁 Estrutura

```text
index.html                            # jogo na raiz, preview local / GitHub Pages se habilitado
assets/characters/                   # 20 spritesheets para a versão HTML
assets/moris/                        # 14 spritesheets de finalização
assets/sprites.json                  # índices e fps
app/src/main/assets/index.html        # cópia empacotada no APK
app/src/main/assets/assets/           # spritesheets offline dentro do APK
app/src/main/java/.../MainActivity.java
app/src/main/AndroidManifest.xml
.github/workflows/android-apk.yml     # CI para gerar o APK de debug
tools/build_sprites.py               # gerador dos sprites (Pillow)
tools/integrate_game.py              # integra sprites ao jogo
tools/vesper_base.html               # versão-base anterior à pixel art
```

## 🛠️ Desenvolvimento

Para regenerar os sprites: instale **Python 3** e **Pillow** (`python -m pip install pillow`) e execute `python tools/build_sprites.py`; o script cria os PNG em `app/src/main/assets/assets/`. Para manter as cópias web e Android sincronizadas após editar assets, copie os atlas para `assets/` e ajuste o jogo se necessário.

Para validar os arquivos localmente, execute `python tools/validate_assets.py` na raiz do repositório. O jogo é offline, sem backend e sem login.

## ⚠️ Limitações

Pixel art gerada proceduralmente (não são desenhos manuais); moris 2D estilizados. O port usa Android WebView e `targetSdk 28` na base atual, **não preparado para publicação na Google Play**. Antes de distribuir, atualizar SDK alvo, testar desempenho, controles e compatibilidade e configurar assinatura release.

**Créditos:** desenvolvimento colaborativo e prototipagem com assistência de IA. Licença do repositório em [`LICENSE`](LICENSE).
