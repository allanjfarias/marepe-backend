# 🚀 Marepe Backend

API backend do projeto **MaréPE**, desenvolvida com **FastAPI** e integrada ao Supabase.

---

## 🧠 Tecnologias

- Python 3.x
- FastAPI
- Supabase

---

## 📁 Estrutura do Projeto

```
api-backend/
  app/
    core/
    routers/
    schemas/
    services/
    main.py
  requirements.txt
  .env
  .gitignore
```

---

## ⚙️ Setup do Ambiente

## 🔹Clonar o repositório

```bash
git clone <URL_DO_REPO>
cd marepe-backend
```

---

## 🐍 Ambiente Virtual (venv)

### 🪟 Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 🐧 Linux / 🍎 Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 📦 Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 🔐 Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here
```

---

## ▶️ Iniciando o servidor

Para iniciar a API localmente com Uvicorn, execute:

```bash
uvicorn app.main:app --reload
```

---

## 🌐 Acessando a API

API: http://127.0.0.1:8000 \
Docs interativa (Swagger): http://127.0.0.1:8000/docs

---

## 📍 Funcionalidades de Vendedor

### Endpoints Implementados

#### `PUT /vendedor/status`
Atualiza o status do vendedor (online/offline)

**Request:**
```json
{
  "status": "online"  // ou "offline"
}
```

**Headers:**
```
Authorization: Bearer {token}
```

#### `POST /vendedor/location`
Envia a localização atual do vendedor

**Request:**
```json
{
  "latitude": -8.0476,
  "longitude": -34.8770,
  "accuracy": 10.5
}
```

**Headers:**
```
Authorization: Bearer {token}
```

### Supabase Realtime

A tabela `vendor_locations` está configurada com Supabase Realtime para publicar atualizações em tempo real.

**Documentação completa:**
- [SUPABASE_REALTIME_SETUP.md](SUPABASE_REALTIME_SETUP.md) - Guia de configuração do Realtime
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Guia completo de testes

### Testes

Execute a suite de testes automatizada:

```bash
python test_vendedor_features.py
```

---

## 👥 Autores

- [Allan Farias](https://github.com/allanjfarias)
- [Ellen Caroliny](https://github.com/ellencaroliny)
- [Evny Vitória](https://github.com/EvnyVt)
- [Heloisa Gonçalves](https://github.com/HeloisaGS)
- [Igor Queiroz](https://github.com/IgorBLQ)
- [Isadora Albuquerque](https://github.com/isadoraalbuquerque)
- [Stéphanie Cândido](https://github.com/ste-coding)
