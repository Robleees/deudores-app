# Guía completa — Gestor de Deudas

## ¿Qué hace esta app?

Es un sistema web para administrar las deudas de clientes de una tienda.
Permite registrar cuánto debe cada familia, abonar pagos y ver el estado
de cobranza por zonas geográficas llamadas **circuitos**.

Se accede desde cualquier navegador (Chrome, Edge, Safari) escribiendo
la dirección del servidor. No requiere instalar nada en el celular o tablet.

---

## Conceptos clave

| Concepto | Qué es |
|---|---|
| **Circuito** | Zona geográfica de cobranza. Ej: "Norte", "Sur", "Centro" |
| **Casa** | Un cliente o familia dentro de un circuito |
| **Transacción** | Cargo (deuda nueva) o abono (pago recibido) |
| **Saldo** | Diferencia entre cargos y abonos. Si es > $0, la familia debe dinero |
| **Usuario** | Persona que usa el sistema. Puede ser administrador global o usuario normal |

---

## Roles de usuario

### Administrador Global
- Ve y gestiona TODO: circuitos, casas, transacciones y usuarios
- Puede crear, editar y desactivar circuitos
- Puede crear y editar usuarios
- Puede desactivar casas
- Accede al dashboard completo con todos los datos

### Usuario (normal)
- Ve todos los circuitos y casas
- Puede registrar transacciones (cargos y abonos)
- NO puede crear circuitos, desactivar casas ni gestionar usuarios
- Ideal para cobradores de campo

---

## Pantallas principales

### 1. Dashboard (`/dashboard/`)
La pantalla de inicio después de iniciar sesión. Muestra:
- **Total adeudado**: suma de todos los saldos pendientes
- **Casas activas**: cuántas casas hay registradas
- **Casas morosas**: cuántas tienen saldo > $0
- **Circuitos activos**: cuántos circuitos hay
- **Gráfica de barras**: saldo acumulado por circuito (rojo = deuda, verde = sin deuda)
- **Top 5 morosas**: las 5 familias con mayor deuda
- **Resumen por circuito**: saldo de cada zona con link a su detalle

### 2. Circuitos (`/circuitos/`)
Lista de todas las zonas de cobranza. Desde aquí puedes:
- Ver el detalle de cada circuito
- Crear un nuevo circuito (solo admin global)

### 3. Detalle de circuito (`/circuitos/<id>`)
Muestra todas las casas activas de esa zona con su saldo.
El número en **rojo** significa que la familia debe dinero.
El número en **verde** significa que está al corriente o con saldo a favor.
Botones disponibles: "Ver cuenta" (ir al detalle de la casa), "Nueva casa", "Editar circuito".

### 4. Detalle de casa (`/casas/<id>`)
La pantalla más usada por los cobradores. Muestra:
- Nombre de la familia, dirección y número de personas
- **Saldo actual** en grande (rojo si debe, verde si está al corriente)
- Formulario para registrar un cargo o abono
- Historial de todas las transacciones con fecha, tipo, monto y quién la registró
- Paginación de 10 transacciones por página

### 5. Usuarios (`/usuarios/`)
Solo visible para administrador global. Permite:
- Ver todos los usuarios del sistema
- Crear nuevos usuarios con contraseña
- Editar nombre y rol de un usuario existente

### 6. Buscar casas (`/casas/buscar`)
Buscador por nombre de familia o dirección. Muestra resultados de todos los circuitos.

---

## Flujo de trabajo típico (día a día)

```
Cobrador llega a la zona
        ↓
Abre el navegador → entra a la IP del servidor
        ↓
Inicia sesión con su usuario y contraseña
        ↓
Va a Circuitos → selecciona su zona
        ↓
Ve la lista de casas con sus saldos
        ↓
Entra al detalle de una casa
        ↓
Registra el abono (pago recibido)
   o registra un cargo (deuda nueva)
        ↓
El saldo se actualiza automáticamente
```

---

## Cómo iniciar la app (cada vez)

### Requisitos
- La computadora donde vive la app debe estar encendida
- Estar conectado al mismo WiFi (para acceso desde otros dispositivos)

### Pasos

1. Abrir PowerShell o Terminal
2. Ejecutar:

```powershell
cd "C:\Users\Edgar Robles Márquez\OneDrive\Documentos\deudores\deudores-app"
.\venv\Scripts\activate
python run.py
```

3. Verás: `Running on http://127.0.0.1:5000`
4. Desde la misma computadora: abrir `http://localhost:5000`
5. Desde otro dispositivo en la misma red: `http://<IP-de-la-PC>:5000`

Para encontrar la IP de la PC:
```powershell
ipconfig
```
Busca "Dirección IPv4", generalmente algo como `192.168.1.X`.

### Para detener la app
Presionar `Ctrl + C` en la terminal.

---

## Primera configuración (solo una vez)

Al correr la app por primera vez, ejecutar el seed para crear datos iniciales:

```powershell
python seed.py
```

Esto crea:
- Usuario `admin` con contraseña `admin123` (¡cambiar después!)
- Circuito Norte y Circuito Sur de prueba
- 2 casas de ejemplo en Circuito Norte

**Importante**: antes de usar en producción, crear usuarios reales y
cambiar o eliminar el usuario `admin` de prueba.

---

## Estructura de archivos (para referencia técnica)

```
deudores-app/
├── run.py                  ← Punto de entrada, inicia el servidor
├── seed.py                 ← Carga datos iniciales de prueba
├── requirements.txt        ← Librerías Python necesarias
├── deudores.db             ← Base de datos SQLite (se crea automáticamente)
└── app/
    ├── __init__.py         ← Configuración central de Flask
    ├── models.py           ← Estructura de la base de datos
    ├── routes/
    │   ├── auth.py         ← Login, logout, decorador login_required
    │   ├── circuitos.py    ← Rutas de circuitos
    │   ├── casas.py        ← Rutas de casas y transacciones
    │   ├── dashboard.py    ← Ruta del dashboard con KPIs
    │   └── usuarios.py     ← Gestión de usuarios
    ├── templates/          ← Páginas HTML
    │   ├── base.html       ← Plantilla base con navbar
    │   ├── auth/           ← Login
    │   ├── circuitos/      ← index, detalle, nuevo, editar
    │   ├── casas/          ← detalle, nueva, editar, buscar
    │   ├── dashboard/      ← index con gráfica
    │   └── usuarios/       ← index, nuevo, editar
    └── static/
        └── css/style.css   ← Estilos personalizados
```

---

## Base de datos

La información se guarda en el archivo `deudores.db` en la raíz del proyecto.
Es un archivo SQLite — no requiere instalar ningún servidor de base de datos.

**Hacer respaldo**: copiar el archivo `deudores.db` a otro lugar periódicamente.
Si ese archivo se borra, se pierden todos los datos.

---

## Tecnologías usadas

| Tecnología | Para qué sirve |
|---|---|
| **Python + Flask** | El servidor web que procesa las peticiones |
| **SQLAlchemy** | Manejo de la base de datos |
| **SQLite** | Base de datos (archivo local, sin instalación) |
| **Bootstrap 5** | Estilos y diseño responsivo (funciona en celular) |
| **Chart.js** | Gráfica de barras en el dashboard |
| **Werkzeug** | Encriptación de contraseñas |

---

## Preguntas frecuentes

**¿Se puede usar desde el celular?**
Sí. Cualquier dispositivo conectado al mismo WiFi puede abrir la app en el navegador.

**¿Qué pasa si se va la luz o se apaga la compu?**
La app deja de estar disponible hasta que se vuelva a encender y se ejecute `python run.py`. Los datos guardados antes no se pierden.

**¿Se pueden recuperar transacciones borradas?**
Actualmente no hay función de borrado de transacciones, solo de desactivación de casas. Los datos históricos se conservan.

**¿Se puede usar sin internet?**
Sí, en la opción de red local (Opción A) no se necesita internet, solo WiFi local.

**¿Cuántas personas pueden usarla al mismo tiempo?**
Para uso en una tienda pequeña (2-5 cobradores), el servidor de desarrollo de Flask es suficiente. Si se requiere más capacidad, se puede configurar con un servidor más robusto (Gunicorn).
