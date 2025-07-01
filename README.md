# 🧠 Mindscape AR

**Mindscape AR** é uma aplicação web interativa que transforma imagens de curvas de nível em modelos 3D para visualização em realidade aumentada. O objetivo é democratizar o acesso à modelagem de relevo por meio de visão computacional e integração WebXR, sem depender de equipamentos de topografia.

---

## 🚀 Funcionalidades

- 📷 Câmera como fundo interativo (opcional via botão On/Off)
- ⬆️ Upload de arquivos `.png` contendo curvas de nível
- 🤖 Processamento automático da imagem com reconstrução 3D
- 🧱 Visualização de modelos `.glb` com suporte a AR (`model-viewer`)
- 🧰 Exemplo de imagens disponíveis para download e teste
- 📸 Captura automática de imagem da câmera e envio para reconstrução

---

## 🖼️ Exemplo de imagens de teste

Você pode usar essas imagens para testar o sistema:

- [curvas_de_nivel.png](https://storage.googleapis.com/mindscape-ar/assets/curvas_de_nivel.png)
- [curvas_de_nivel2.png](https://storage.googleapis.com/mindscape-ar/assets/curvas_de_nivel2.png)

---

## 🛠️ Tecnologias utilizadas

### 🧩 Frontend
- HTML5 + CSS3
- `@google/model-viewer`
- WebRTC (para capturar câmera)

### 🧠 Backend (Python)
- Flask + Flask-CORS
- OpenCV + NumPy
- SciPy (Delaunay triangulation)
- Trimesh (geração de `.glb`)
- Matplotlib colormaps

---

## 📦 Estrutura de pastas

Mindscape.AR/
│
├── app.html # Frontend da aplicação
├── app.py # Servidor Flask
├── image_processing.py # Geração do modelo 3D a partir da imagem
│
├── uploads/ # Imagens recebidas do usuário (.png)
├── static/models/ # Modelos 3D gerados (.glb)
├── .gitignore # Ignora arquivos gerados automaticamente
└── README.md # Este arquivo


---

## ▶️ Como rodar localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/mindscape-ar.git
   cd mindscape-ar

2. Instale as dependências:
    ```bash
    pip install -r requirements.txt

3. Execute o servidor:
    ```bash
    python app.
    
4. Abra o navegador e acesse:
    ```bash
    http://localhost:5000

📄 Licença
Distribuído sob a licença MIT. Veja LICENSE para mais informações.