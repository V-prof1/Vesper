# VESPER: FIRST BLOOD — Primeira Pessoa (3D)

Segundo projeto independente de VESPER: ABISMO, com protótipo **3D real (WebGL 1)** em primeira pessoa. **O jogo 2D original não foi modificado.**

## Jogar

Abra `game/index.html` em um navegador com WebGL ou instale o APK Android compilado a partir do projeto de `android/`. O jogo não requer internet e não usa bibliotecas externas.

## Sistemas na versão 0.1

- 1 assassino contra 6 sobreviventes controlados por IA.
- 3 arenas 3D: Fundição das Cinzas, Capela dos Perdidos e Estação Vazia.
- 4 assassinos: Ceifador, Sombra, Tecelã e Vigia, com 3 habilidades por personagem.
- IA com objetivos de reparação, fuga, rotas A*, paletes, curas, resgates de gancho, flashlight save e fuga pelos portões.
- 6 geradores por mapa; 4 consertados abrem os portões.
- Ataques, ferimentos, caídas, carregar, soltar, ganchos com dois estágios e finalizações (moris) estilizadas.
- HUD com estado dos seis bots, controles para PC e tela sensível ao toque, menu de pausa, pontuação e tela final.
- Tudo num HTML com motor WebGL escrito em JavaScript sem dependências.

## Controles

| Comando | PC | Celular |
|---|---|---|
| Mover | WASD / setas | Analógico esquerdo |
| Olhar | Mouse com pointer lock | Deslizar o lado direito |
| Atacar | Clique / espaço | ATACAR |
| Habilidades | Q, E, R | Q, E, R |
| Interagir e carregar | Segure F | Segure F |
| Soltar sobrevivente | G | SOLTAR |
| Finalização | X (sobrevivente elegível, caído) | MORI |
| Pausar | Esc | Botão Ⅱ |

## Compilar APK

O app Android é um **WebView offline com aceleração por hardware**, não um port nativo Unity/Godot. Ele empacota os arquivos localmente no aplicativo; você não depende de um site. Requer WebGL no Android System WebView.

Com JDK 17, Android SDK 35 e Gradle 8.9, na pasta `android/` execute:

```bash
gradle :app:assembleDebug --no-daemon
```

O APK será salvo em `android/app/build/outputs/apk/debug/app-debug.apk`.

## Observações

É um **protótipo inicial**. O movimento é 3D, mas os personagens têm modelos geométricos estilizados e o mori é cinematográfico em 2D sobre a câmera. Balanceamento de IA e desempenho ainda precisam de teste real no celular.
