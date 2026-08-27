# Focus

Aplicación de sesiones de enfoque con gamificación: **API Flask**, **web PWA (React)** y **app Android nativa (Kotlin + Compose)** sobre la misma API.

Evolución de [FocusFlow](https://github.com/Egt17baa/FocusFlow) con API versionada, autenticación JWT con refresh y revocación, estadísticas reales, retos, bloqueo de apps por paquete Android y cliente móvil nativo.

## Estructura

```
backend/   API Flask (SQLAlchemy + JWT) y tests
web/       PWA React + Vite + Tailwind
android/   App Android (Kotlin, Jetpack Compose)
```

## Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
flask --app wsgi run --port 5001   # o: gunicorn -b 0.0.0.0:5001 wsgi:app
pytest -q && ruff check .
```

Variables de entorno (obligatorias en producción):

| Variable | Descripción |
| --- | --- |
| `FOCUS_SECRET_KEY` | Clave de sesión de Flask |
| `FOCUS_JWT_SECRET_KEY` | Clave de firma JWT (mínimo 32 bytes) |
| `FOCUS_DATABASE_URI` | Cadena de conexión (por defecto SQLite local) |
| `FOCUS_CORS_ORIGINS` | Orígenes permitidos, separados por coma |

### API (`/api/v1`)

| Recurso | Endpoints |
| --- | --- |
| `auth` | `register`, `login`, `refresh`, `logout`, `change-password` |
| `users` | `GET/PATCH/DELETE /users/me` |
| `sessions` | listar, crear, `active`, `pause`, `resume`, `complete`, `abandon`, borrar |
| `stats` | `overview`, `achievements`, `leaderboard` |
| `challenges` | listar, crear, `join`, `leave`, `leaderboard` |
| `blocked-apps` | listar, crear, editar, borrar, `check` (usado por Android) |
| `health` | estado del servicio |

## Web (PWA)

```bash
cd web
npm install
npm run dev      # http://localhost:5173, proxy /api -> http://localhost:5001
npm run build    # genera dist/, servido también por el backend
```

Requiere Node.js 20.19+ o 22.12+. Incluye manifest, service worker (shell offline), navegación móvil y notificaciones del navegador al terminar una sesión.

## Android

```bash
cd android
./gradlew :app:assembleDebug          # APK en app/build/outputs/apk/debug
./gradlew :app:testDebugUnitTest
```

Requiere JDK 17 y Android SDK 34 (`ANDROID_HOME` o `local.properties` con `sdk.dir`).

La URL de la API se inyecta en tiempo de compilación (por defecto `http://10.0.2.2:5001/api/v1/`, el host local visto desde el emulador):

```bash
./gradlew :app:assembleRelease -PfocusApiBaseUrl=https://tu-servidor/api/v1/
```

Incluye timer con servicio en primer plano y notificación persistente, tokens en DataStore con refresh automático, estadísticas, logros y gestión de apps bloqueadas.

## Mejoras sobre FocusFlow

- API versionada `/api/v1` con blueprints por dominio y factory de aplicación.
- JWT con refresh y revocación en logout; contraseñas con hash de Werkzeug.
- Máquina de estados de sesión (`running`/`paused`/`completed`/`abandoned`) con pausas, interrupciones y puntuación por duración y objetivo cumplido.
- Estadísticas reales: series diarias, etiquetas, franjas horarias, rachas, meta diaria y tasa de finalización.
- Retos con progreso automático al completar sesiones y leaderboard.
- Bloqueo de apps con `package_name` y endpoint `check` para el cliente Android.
- Web como PWA responsive e instalable.
- Cliente Android nativo compartiendo la misma API.
- 21 tests de backend y tests unitarios en Android; lint con Ruff y oxlint.
