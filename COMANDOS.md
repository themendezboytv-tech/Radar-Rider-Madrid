# 📋 Comandos más usados — Radar Rider Madrid

Carpeta de trabajo oficial: `C:\Proyectos\Radar-Rider-Madrid`

Todos los comandos de abajo se ejecutan desde esa carpeta, en PowerShell.

---

## 🚀 Arrancar el bot (lo que más vas a usar)

```powershell
cd C:\Proyectos\Radar-Rider-Madrid
.venv\Scripts\Activate.ps1
python bot.py
```

Para detenerlo: `Ctrl + C` en esa misma terminal.

Sabrás que arrancó bien si ves:
```
========================================
   RADAR RIDER MADRID INICIADO
========================================
```

---

## 🔍 Revisar los avisos guardados en la base de datos

```powershell
cd database
python -c "import sqlite3; c = sqlite3.connect('radar_rider_madrid.db'); print(c.execute('SELECT id, tipo, calle, ciudad, comentario, fecha_creacion FROM avisos').fetchall())"
cd ..
```

---

## 📦 Subir cambios a GitHub (cuando cierres una versión)

```powershell
git add .
git commit -m "descripción del cambio"
git tag v1.X
git push origin main
git push origin v1.X
```

Cambia `v1.X` por el número real de la versión (ej. `v1.4`).

---

## 🔎 Ver en qué estado está tu repo

```powershell
git status
```
Muestra qué archivos cambiaste y aún no subiste.

```powershell
git log --oneline
```
Muestra el historial de commits, del más reciente al más antiguo.

```powershell
git tag
```
Muestra todas las versiones (tags) que ya subiste.

---

## 🆕 Configurar el proyecto desde cero (solo la primera vez, o en un PC nuevo)

```powershell
git clone https://github.com/themendezboytv-tech/Radar-Rider-Madrid.git
cd Radar-Rider-Madrid
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Después crea tu archivo `.env` (copia `.env.example`, renómbralo a `.env` y rellena `TOKEN`, `GROUP_ID`, `CHANNEL_ID` con los datos de tu bot de pruebas).

---

## ⚠️ Notas importantes

- Si `python` no se reconoce como comando, usa `py` en su lugar (le pasa a veces en Windows).
- Nunca subas a Git ni compartas por chat tu archivo `.env` ni el `radar_rider_madrid.db` — ya están excluidos en `.gitignore`, no los fuerces con `git add -f`.
- Antes de cada `git push`, corre `git status` primero para confirmar qué se va a subir.
