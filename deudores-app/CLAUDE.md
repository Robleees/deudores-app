# deudores-app

## Qué es este sistema

Gestor de deudas para una tienda local con cobranza por zonas geográficas llamadas **circuitos**. Cada circuito agrupa un conjunto de **casas** (clientes). Los cobradores registran **transacciones** (abonos, cargos) por casa. El sistema permite llevar el saldo de cada cliente y el avance de cobranza por circuito.

---

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.x, Flask |
| ORM | SQLAlchemy |
| Base de datos | SQLite (archivo `app.db` en la raíz) |
| Frontend | Jinja2 templates, Bootstrap 5, vanilla JS |
| Autenticación | Flask-Login |

---

## Estructura de la base de datos

### `usuarios`
| Campo | Tipo | Notas |
|---|---|---|
| id | Integer PK | |
| nombre | String | |
| email | String unique | |
| password_hash | String | |
| rol | Enum | `'admin_global'` o `'admin_local'` |
| circuito_id | FK → circuitos | NULL si es admin_global |

### `circuitos`
| Campo | Tipo | Notas |
|---|---|---|
| id | Integer PK | |
| nombre | String | Ej: "Norte", "Centro" |
| descripcion | String | |

### `casas`
| Campo | Tipo | Notas |
|---|---|---|
| id | Integer PK | |
| nombre_cliente | String | |
| direccion | String | |
| telefono | String | |
| circuito_id | FK → circuitos | |
| saldo_actual | Float | Calculado a partir de transacciones |
| activa | Boolean | Default True |

### `transacciones`
| Campo | Tipo | Notas |
|---|---|---|
| id | Integer PK | |
| casa_id | FK → casas | |
| usuario_id | FK → usuarios | Quién registró |
| tipo | Enum | `'cargo'` o `'abono'` |
| monto | Float | Siempre positivo |
| descripcion | String | |
| fecha | DateTime | Default utcnow |

---

## Roles y permisos

- **admin_global**: Ve y gestiona todos los circuitos, casas, transacciones y usuarios. Puede crear/eliminar circuitos y asignar admins locales.
- **admin_local**: Solo ve y opera dentro de su propio `circuito_id`. No puede ver otros circuitos ni gestionar usuarios.

La verificación de rol se hace en cada ruta, no solo en el login.

---

## Comandos útiles

```bash
# Instalar dependencias
pip install -r requirements.txt

# Correr el servidor de desarrollo
python run.py

# Inicializar la base de datos (primera vez)
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()

# O con el comando personalizado (cuando esté configurado)
flask init-db
```

La app corre en `http://localhost:5000` por defecto.

---

## Convenciones

- **Español** para nombres de variables, funciones y campos que representen conceptos de negocio (`circuito`, `casa`, `saldo_actual`, `tipo_transaccion`).
- **Inglés** para nombres de infraestructura y patrones Flask (`db`, `app`, `blueprint`, `model`, `login_manager`).
- Las rutas de la API siguen el patrón `/api/<recurso>` en plural: `/api/circuitos`, `/api/casas`, `/api/transacciones`.
- Las rutas de vistas HTML no llevan prefijo `/api/`.
- Cada módulo de rutas vive en su propio archivo dentro de `app/routes/` y se registra como Blueprint.

---

## Estructura de rutas

```
app/routes/auth.py       → /login, /logout, /registro
app/routes/circuitos.py  → /circuitos y /api/circuitos
app/routes/casas.py      → /casas y /api/casas
```

Agregar nuevos recursos implica crear un archivo nuevo en `app/routes/`, no expandir los existentes.

---

## Notas para el agente

- **No borrar ni modificar archivos de migración** si se incorpora Flask-Migrate en el futuro. Siempre generar una nueva migración en lugar de editar las existentes.
- **Respetar la separación por módulo**: no agregar rutas de `casas` en `circuitos.py` ni viceversa, aunque parezca conveniente.
- El archivo `app.db` está en `.gitignore` y no debe comitearse.
- Al modificar modelos, actualizar también este `CLAUDE.md` si cambia el esquema.
- La lógica de negocio (cálculo de saldos, validaciones de rol) va en `models.py` o en helpers, no dentro de las rutas.
- No usar `*` en imports de SQLAlchemy ni de Flask.
