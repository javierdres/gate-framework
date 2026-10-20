> [English](BUILDING.md) · **Español**

# Construir el SDLC de tu organización

Esta guía lleva a un orquestador desde GATE hasta un SDLC propio que funciona: un repositorio
con el método de la organización, su catálogo de estándares, sus productos, sus skills y la
forma en que entra cada persona, corriendo sobre el asistente de IA que la organización eligió.

Está escrita para dos lectores a la vez. **Si eres el orquestador**, te dice qué vas a decidir,
qué te van a preguntar y con qué vas a terminar. **Si eres el asistente**, es tu especificación
de construcción: `/establish` la sigue de principio a fin.

Lee primero la [sección 2 de GATE.md](GATE.md#2-before-stage-0-the-orchestrator-builds-the-sdlc).
Ahí se explica por qué el SDLC se construye así; esta guía dice cómo.

---

## 1. Cómo usar esta guía

Instrucciones para el asistente que construye el SDLC:

- **No construyas nada antes de terminar la entrevista de la sección 5** y de que se confirme su
  resumen. Lo que nadie sepa se marca como «por definir» y se sigue; nada se inventa.
- Donde esta guía dice «la plataforma de código», «la herramienta de tickets» o «la fuente de
  verdad de producción», usa lo que la organización tenga. Si le falta una de esas piezas, la
  parte que depende de ella queda fuera y se anota en el plan como pendiente.
- **Construye por capas, en el orden de la sección 10**, y muestra cada capa antes de empezar
  la siguiente. Todo archivo que llegue a un sistema compartido sigue la regla de permisos: nada
  se publica sin el OK del orquestador.
- **Escribe todo en formatos neutrales** (sección 3) y deja lo propio de tu plataforma dentro
  del adaptador. Otro asistente tiene que poder correr este SDLC mañana con solo agregar su
  adaptador.
- Cuando conectes tu propia plataforma, **lee su documentación actual** en vez de confiar en tu
  memoria. Los nombres de los hooks, las rutas de configuración y los nombres de archivo cambian
  entre versiones.
- Los nombres de las skills van cortos y en inglés. Todo lo demás, en el idioma de la
  organización.
- El catálogo arranca vacío, salvo los ejemplos marcados como tales, y se llena con lo que le
  pase a este equipo.
- Al terminar, corre la verificación de la sección 11 y reporta lo que quedó en verde, lo que no
  y por qué.

---

## 2. Con qué terminas

- Un repositorio, `sdlc-<org>`, que cada persona clona en su carpeta de trabajo, al lado de los
  repositorios de sus productos. El asistente se abre en esa carpeta de trabajo.
- Instrucciones persistentes que carga cada sesión, con las reglas que aplican siempre.
- Un plan con un objetivo, una fecha de revisión y lo que queda fuera de alcance.
- Un gobierno por roles, con una tabla de quién ocupa cada rol hoy y otra de qué perfiles puede
  usar cada persona, las dos ligadas a identidades verificables.
- El método tal como lo aplica la organización: perfiles, permisos, la bitácora de cada persona,
  el inicio de sesión y las plantillas.
- Un catálogo de estándares vacío, ordenado por ámbito, con su registro de descartes.
- Una carpeta por producto del piloto, con su contexto, sus reglas de negocio y su catálogo de
  casos de uso.
- Herramientas: un instalador, un verificador de accesos, los guardias, clientes de API pequeños
  y guías de acceso paso a paso.
- Las skills de la primera fase, en el formato abierto `SKILL.md`.
- Un adaptador para el asistente elegido, y las instrucciones para sumar otro.
- Una verificación final con cada punto en verde, o marcado como pendiente con el nombre de
  quien lo destraba.

---

## 3. Elegir y conectar el asistente

### Lo que el asistente tiene que poder hacer

| Capacidad | Para qué se usa | Si no la tiene |
|---|---|---|
| Instrucciones persistentes que carga en cada sesión | Las reglas que aplican siempre | No sirve |
| Skills que se cargan cuando se necesitan | Una por contrato de skill | Archivos de instrucciones por tarea, invocados por nombre. Sirve, pero peor |
| Acceso al repositorio y a la terminal | Leer código, correr chequeos y pruebas | No sirve para los roles que construyen |
| Hooks antes de una acción y al iniciar la sesión | Permisos, contexto al inicio, la bitácora | La plataforma asume el control (ver abajo). Sirve, con menos garantías |
| Conectores (Model Context Protocol) | Tickets y observabilidad | Clientes de API en `tools/`. Sirve |

Cuando el asistente no tiene hooks, el SDLC lo dice en su plan y lo compensa en la plataforma:
el asistente trabaja con credenciales que no pueden escribir donde importa, la rama principal
está protegida y las escrituras hacia afuera pasan por un script de `tools/` que muestra la
acción y pide OK.

### Los formatos neutrales

| Pieza | Forma neutral | Dónde vive |
|---|---|---|
| Instrucciones persistentes | `AGENTS.md` | En la raíz del repositorio del SDLC, más uno corto en la carpeta de trabajo |
| Skills | Una carpeta por skill con su `SKILL.md`: un `name`, una `description` que dice cuándo usarla con las palabras que diría una persona, e instrucciones en texto | `skills/` en el repositorio del SDLC |
| Guardias | Scripts que leen la acción como JSON por la entrada estándar y responden permitir, preguntar o denegar | `tools/guards/` |
| Conectores | Servidores Model Context Protocol | Se declaran por asistente, en su adaptador |
| Configuración | `sdlc.yml`: la organización, sus asistentes, sus herramientas, sus ámbitos y la versión de GATE | En la raíz del repositorio del SDLC |

### El contrato de los guardias

Todo guardia sigue el mismo contrato, lo llame el asistente que lo llame.

- **Entrada**: un objeto JSON por la entrada estándar con, al menos, la herramienta o acción que
  el asistente quiere ejecutar y sus argumentos. El adaptador pasa lo que mande la plataforma;
  el guardia lee los campos comunes e ignora el resto.
- **Salida**: una decisión. `allow` deja pasar, `ask` pone la acción frente a la persona y `deny`
  la detiene con su motivo.
- **Falla**: si el guardia no puede decidir, responde `ask`. Un guardia nunca falla dejando
  pasar.
- Si la plataforma acepta una respuesta estructurada, el adaptador traduce la decisión a ese
  formato. Si solo entiende códigos de salida, `allow` es el código 0 y `deny` el 2, con el
  motivo en la salida de errores. Si no tiene cómo preguntar, `ask` se vuelve `deny` con un
  motivo que le dice a la persona cómo autorizar la acción y volver a correrla.

`bin/bootstrap.py sdlc` deja un guardia de referencia que funciona, `tools/guards/permissions.py`,
con autorizaciones por sesión y la lista de acciones que nunca se delegan.

### Los adaptadores

El adaptador es la única parte del SDLC propia de un asistente. Hace tres cosas: que el
asistente cargue `AGENTS.md`, que encuentre las skills y que los guardias queden registrados en
los eventos que corresponden. El asistente que corre `/establish` escribe su propio adaptador
leyendo la documentación actual de su plataforma, y la verificación final prueba que funciona.

Lo que sigue es un punto de partida para los asistentes por los que más se pregunta. Los nombres
de los hooks y las rutas cambian entre versiones: compruébalos contra la versión que usas y
anota esa versión en `sdlc.yml`.

| Asistente | Instrucciones | Skills | Guardias |
|---|---|---|---|
| Claude Code | `CLAUDE.md` en la carpeta de trabajo, que importa `@sdlc-<org>/AGENTS.md` | Enlazadas o copiadas en `.claude/skills/` | `.claude/settings.json`: `SessionStart`, `UserPromptSubmit`, `PreToolUse` |
| Gemini CLI | `GEMINI.md`, o `AGENTS.md` como nombre del archivo de contexto en la configuración | Su carpeta de skills, en el mismo formato `SKILL.md` | `.gemini/settings.json`: los eventos antes de una herramienta y de sesión. Puede que haya que habilitar los hooks |
| Kiro | Un archivo de steering en `.kiro/steering/` que apunta a `AGENTS.md` | `.kiro/skills/` | Los hooks de Kiro CLI antes de usar una herramienta y al iniciar la sesión; los nombres cambian entre versiones mayores |
| Codex CLI | Lee `AGENTS.md` directamente | Su carpeta de skills, en el mismo formato | Su configuración de hooks, si la versión instalada la soporta |
| Cualquier otro | El archivo que cargue en cada sesión, apuntando a `AGENTS.md` | Lo que cargue cuando se necesita | Su mecanismo previo a una acción, o el respaldo en la plataforma descrito arriba |

Solo el adaptador de Claude Code está verificado de punta a punta, y lo escribe
`bin/bootstrap.py`. Las demás filas son puntos de partida sacados de la documentación pública de
cada plataforma, todavía sin verificar en una instalación real. Si verificas uno, apórtalo.

Quienes no trabajan en una terminal, producto casi siempre, usan un **cliente de chat** con un
proyecto o espacio de trabajo: las instrucciones de su rol, los archivos de contexto que
necesita y un conector a la herramienta de tickets. El SDLC guarda ese paquete en
`method/chat-client/` y dice qué copiar dónde.

Una organización puede usar varios asistentes sobre el mismo SDLC. Cada uno tiene su carpeta en
`adapters/`, y el instalador conecta el que use cada persona.

---

## 4. Las decisiones que solo toma el orquestador

Cada una trae un valor por defecto, así que ninguna frena la construcción. Todas se pueden
cambiar después con un cambio al repositorio del SDLC.

| Decisión | Por defecto |
|---|---|
| Qué asistente, o cuáles | El que ya usan los roles que construyen. Se anota la versión |
| Nombre del repositorio | `sdlc-<org>` |
| Plataforma de código, herramienta de tickets y fuente de verdad de producción | Las que la organización ya usa. Una sola fuente de verdad por pregunta |
| Quién ocupa cada rol | El orquestador cubre todo rol de responsable que todavía no tenga a nadie |
| Perfiles habilitados por persona | Perfiles de construcción para todos; producto, operación y liderazgo por nombre |
| Productos del piloto | Dos o tres, donde haya un product owner dispuesto a participar |
| Ámbitos de reglas | Transversal, producto, seguridad, operación, y uno por cada capa técnica que el equipo tenga de verdad |
| Criterios de salida de la formulación y fecha de revisión | Los cuatro criterios de la sección 2 de GATE.md, revisados entre cuatro y seis semanas después de la construcción |
| Idioma y estándar de escritura | El de la organización. Los términos técnicos se dejan en inglés cuando así los dice el equipo |
| Dónde viven las pruebas de flujo | En el repositorio del SDLC, para que la adopción no obligue a cambiar ningún repositorio de producto. En los repositorios de productos solo se lee |
| Fuera de alcance | Lo que el orquestador nombre en la entrevista, más las fases siguientes hasta que la primera funcione |

---

## 5. La entrevista

Pregunta de a pocas, las más importantes primero. Muestra el valor por defecto de cada una, para
que el orquestador solo tenga que confirmarlo. Cierra con un resumen que se confirma antes de
construir nada.

**La organización**

- Nombre corto, que se usa en el repositorio y en los encabezados.
- Qué construye: productos propios, sistemas internos, integraciones, servicios a clientes.
- Tamaño de los equipos técnico y de producto, y si trabajan como uno solo o como varios.
- Idioma y variante de los documentos, y qué términos técnicos el equipo dice en inglés.
- Contexto regulatorio: datos personales, de salud o financieros, y cualquier norma a la que
  tenga que responder.

**El asistente**

- Qué asistente usarán los roles que construyen, y qué versión.
- Si producto y los demás roles no técnicos usarán un cliente de chat, y cuál.
- Qué conectores hay disponibles: tickets, documentación, observabilidad.

**Personas y roles**

- Quién orquesta y quién ocupa cada rol de la sección 7 de GATE.md. Quién cubre un rol vacío
  mientras tanto.
- Por cada persona: su identidad verificable (su cuenta en la plataforma de código o en la
  herramienta de tickets) y los perfiles que tiene habilitados.

**Las herramientas**

| Pieza | Qué averiguar |
|---|---|
| Plataforma de código | Cuál, qué grupo u organización, cómo se autentica cada persona (login de la empresa, SSH, token) y si permite ramas protegidas y archivo de dueños |
| Herramienta de tickets | Cuál, qué proyectos, si hay conector para el asistente, cómo escribe el equipo una historia y sus criterios, si usan sprints o flujo continuo |
| Fuente de verdad de producción | La plataforma de observabilidad, cómo se consulta por API, qué ambientes existen y cómo se distinguen en los datos |
| Pipeline | Dónde corre y qué revisa hoy |
| Documentación | Dónde vive hoy, para enlazarla y no duplicarla |
| Sistemas operativos | Para que los scripts y las guías funcionen para todos |

**El trabajo**

- Los productos o sistemas principales, el product owner de cada uno y los repositorios que lo
  componen. Para el piloto bastan dos o tres.
- Las capas técnicas que tienen sentido como ámbitos de reglas (por ejemplo frontend, backend,
  datos, móvil, infraestructura).
- Los ambientes de prueba que existen, y si sus integraciones externas tienen modo de prueba.
- Qué se quiere lograr primero, cómo se sabrá que funciona y la fecha de revisión.
- Lo que la organización ya decidió no hacer.

---

## 6. Estructura del repositorio

```
<carpeta de trabajo>/
├── AGENTS.md                 lo deja el instalador; apunta al SDLC y a personal/
├── <archivos del adaptador>  los deja el instalador para el asistente de la persona
├── sdlc-<org>/               el repositorio del SDLC de la organización
│   ├── AGENTS.md             reglas para el asistente y mapa del repositorio
│   ├── sdlc.yml              organización, asistentes, herramientas, ámbitos, versión de GATE
│   ├── README.md             qué es, para personas, en una página
│   ├── ONBOARDING.md         cómo se empieza
│   ├── PLAN.md               qué se construye ahora, qué sigue, qué queda fuera
│   ├── GOVERNANCE.md         roles, quién aprueba qué, quién ocupa cada rol
│   ├── CODEOWNERS            el gobierno traducido a la plataforma de código
│   ├── GATE.md               la versión de GATE que implementa y dónde se aparta
│   ├── gate-reference/       copia de solo lectura de GATE: framework, esta guía, contratos
│   ├── method/               ciclo, perfiles, permisos, bitácora, inicio de sesión,
│   │   ├── flows/            estilo de escritura, un diagrama por perfil
│   │   ├── chat-client/      el paquete para los roles que trabajan fuera de la terminal
│   │   └── templates/        expediente, ticket, postmortem, registro de decisión
│   ├── catalog/              lo escribe bin/bootstrap.py, sin reglas
│   │   ├── README.md         formato de una regla, severidades y ámbitos
│   │   ├── scopes.md         cada ámbito y su responsable
│   │   ├── rules/hard/       reglas que bloquean, cada una con su ámbito
│   │   ├── rules/soft/       recomendaciones, cada una con su ámbito
│   │   ├── calibration/      false-positives.md, que no necesita aprobación
│   │   └── bin/              validador de formato y generador del catálogo
│   ├── products/
│   │   ├── README.md         índice de productos y de sus catálogos de casos de uso
│   │   ├── _template/        README.md · business-rules.md · use-cases.md
│   │   └── <producto>/       contexto, reglas, casos de uso y sus pruebas de flujo
│   ├── e2e/                  el runner común de las pruebas de flujo
│   ├── tools/
│   │   ├── install.sh        instalador idempotente
│   │   ├── check-access.sh   requisitos y accesos por perfil
│   │   ├── guards/           permisos, inicio de sesión, recordatorio de la bitácora
│   │   ├── clients/          un cliente de API pequeño por sistema
│   │   └── guides/           guías de acceso paso a paso
│   ├── skills/               una carpeta por skill, cada una con su SKILL.md
│   ├── adapters/             una carpeta por asistente
│   └── personal/             lo de cada persona; el control de versiones lo ignora
│       ├── profile.md
│       ├── preferences.md
│       ├── grants/           autorizaciones de la sesión, se borran a los pocos días
│       └── sessions/         la bitácora, con su índice README.md
└── <repositorios de productos>/
```

---

## 7. Qué contiene cada archivo base

Las plantillas de [`templates/`](templates/) dan el punto de partida literal para la mayoría.

**`AGENTS.md` del repositorio.** Se carga en cada sesión, así que es corto. Una línea con el
propósito y el principio: el asistente prepara, las personas deciden. Una referencia al plan: si
alguien propone algo que no calza con él, el asistente lo dice y ofrece anotarlo fuera de
alcance. El inicio de sesión, incluido o enlazado. Un mapa en una tabla: dónde está cada cosa,
qué pregunta responde y cuándo leerla. Y las reglas que aplican siempre: el OK antes de escribir
y sus niveles; verificar antes de afirmar; una sola fuente de verdad para producción; revisar si
algo existe antes de crearlo; consultar el catálogo antes de proponer un patrón; nada se integra
sin una aprobación vigente; las credenciales nunca en un repositorio ni en el chat; comprobar la
raíz del repositorio antes de cualquier operación destructiva de control de versiones; si falta
un acceso, decir cuál y seguir con lo que se pueda; lo que una persona corre fuera del asistente
se le da paso a paso; escribir por roles; correr la cosecha al cerrar una revisión; llevar la
bitácora sin que lo pidan; el estándar de escritura para documentos.

**Inicio de sesión (`method/session-start.md`).** Un pedido directo se atiende sin menú. Si la
puesta en marcha no terminó, el guardia de inicio dice en qué etapa quedó y `/onboard` sigue
desde ahí. Sin perfil, un menú numerado de perfiles dentro de un bloque de código, con una opción
para trabajar sin el flujo y dos para conocer el SDLC. Con perfil, un saludo con nombre y perfil,
y las tareas que ese perfil habilita: producto, construcción, revisión, operación y soporte,
liderazgo y otra. Antes de empezar, el asistente resume lo que entendió y espera. Si la persona
saluda sin pedir nada, le menciona en una línea lo que sigue abierto en su bitácora.

**Perfiles (`method/profiles.md`).** Una ficha por perfil, que responde cinco preguntas: qué
obtiene la persona, qué configura (con el permiso mínimo y cómo se consigue), con qué datos
trabaja, qué skills usa y cómo sabe que quedó lista. Es la fuente única: el onboarding, el plan y
el verificador de accesos leen de aquí.

**Permisos (`method/permissions.md`).** Tres niveles. El trabajo local nunca pide más que el modo
de permisos del propio asistente: leer, editar, correr pruebas, commits locales y consultar los
sistemas. Las escrituras hacia afuera piden OK hasta que se autoriza un alcance: push, abrir un
merge request, crear, editar, comentar o mover tickets; al primer OK en un repositorio o en un
proyecto de tickets, el asistente pregunta si lo autoriza por el resto de la sesión. Hay acciones
que piden OK siempre, haya lo que haya autorizado: producción, merges, push forzado o que borra
ramas, borrados, generar credenciales y cualquier comando que encadene una escritura autorizada
con otras que no lo están. La autorización vive en `personal/grants/`, se registra con un comando
que pasa por la confirmación del propio asistente, de modo que no puede autorizarse solo, y
vence con la sesión.

**La bitácora (`method/sessions.md`).** Cuándo escribe el asistente: una decisión, un paso
cerrado, un descarte, algo crítico, un pendiente, una pausa. Un archivo por tema y fecha de
inicio. Una plantilla de resumen. Un índice con «Abierto» y «Por tema». Qué hacer al retomar. Qué
no va ahí: las reglas van al catálogo, el contexto de un producto a su carpeta, y lo que cambia
una tarea a su ticket.

**Estilo (`method/style.md`).** Para los documentos que leen personas: frases cortas, lenguaje
llano, escrito para quien decide y sin datos que el lector no conoce. Para la terminal: todo lo
visual dentro de un bloque de código, máximo 62 columnas, caracteres de dibujo y símbolos simples
(✓ ✗ ⚠ ↺ ▸), sin emojis, un componente por idea.

**Método (`method/README.md`) y flujos.** La línea fija entre el asistente y las personas, las
tres incompatibilidades, el ciclo tal como lo aplica la organización, las tres entradas, el
expediente y los pasos de adopción con su estado. Un diagrama por perfil en `flows/`.

**Gobierno (`GOVERNANCE.md` y `CODEOWNERS`).** La fase actual, formulación u operación, con sus
criterios de salida. Los roles. Qué parte puede cambiar cualquiera por merge request y quién la
aprueba: método y gobierno, el orquestador y todos los responsables; reglas transversales, todos
los responsables; cada ámbito, su responsable; cada producto, su product owner y el responsable
de la capa afectada; herramientas, operación; skills, según el perfil al que sirven; descartes,
sin aprobación. Cómo nace una regla y la cosecha mensual. La tabla de quién ocupa cada rol hoy y
la de perfiles por persona, con su identidad verificable: las dos únicas tablas del repositorio
con nombres.

**Catálogo (`catalog/`).** Lo escribe entero `bin/bootstrap.py`: el formato de una regla, dos
severidades (las reglas duras bloquean, las blandas recomiendan), el validador, el
`catalog.json` generado y el registro de descartes, sin reglas a propósito. Cada regla declara su
ámbito en el campo `scope` (transversal, producto, seguridad, operación o una capa técnica), y
`scopes.md` nombra al responsable de cada uno. Una regla nace como candidata y se reporta como
recomendación hasta que su responsable la aprueba; una regla derogada nunca se borra y su número
no se reutiliza.

**Productos (`products/`).** Un índice de productos, el estado de sus catálogos de casos de uso y
a quién preguntar por cada dominio. Una plantilla con tres archivos: el contexto del producto
(qué es, dónde está el trabajo, repositorios activos, a quién preguntar, por rol); sus reglas de
negocio vigentes, cada una validada o por validar; y su catálogo de casos de uso. La carpeta de
un producto se crea cuando alguien trabaja en él, no antes.

**Plan (`PLAN.md`).** El objetivo en dos frases, la visión por perfil y fase, cómo se sabrá que
funciona y la fecha de revisión, lo hecho, lo próximo en orden con su dueño y su condición de
cierre, lo que queda fuera de alcance y las decisiones pendientes con quién decide.

**`GATE.md` del SDLC.** El commit de GATE que implementa, y un mapa corto de qué etapa o
principio cubre cada parte y dónde se aparta del marco, cada diferencia con su motivo.

**`ONBOARDING.md` y `README.md`.** Para personas. El README dice qué es en una página. El
onboarding dice cómo se empieza: clonar, abrir el asistente dentro del repositorio la primera
vez y dejar que `/onboard` haga el resto. Incluye una tabla de las skills disponibles.

---

## 8. Las skills del SDLC

Cada skill es una carpeta en `skills/` con un `SKILL.md` que implementa uno de los contratos de
[`skills/`](skills/) de este repositorio. La descripción dice qué hace y cuándo usarla, con las
palabras que diría una persona, porque es lo que el asistente usa para decidir si la carga. Una
skill entra al SDLC común cuando la usa todo un rol en cualquier producto, no depende de los
datos o accesos de una sola persona y trae su propia documentación.

### Skills de entrada

**`onboard`** implementa el contrato `/onboard` por etapas, mostradas como un mapa: requisitos,
instalación, perfil, accesos y bienvenida. Requisitos: corre el verificador y, por cada cosa que
falte, da el comando exacto para el sistema de la persona. Instalación: comprueba que el
repositorio esté dentro de una carpeta de trabajo, explica qué hace el instalador, lo corre con
OK y pide volver a abrir el asistente en la carpeta de trabajo. Perfil: nombre, perfiles (solo
los habilitados para la identidad verificada) y productos, guardados en `personal/profile.md`.
Accesos: explica qué necesita el perfil y para qué, y configura cada acceso que falte de a uno,
con su guía, verificando solo ese; prefiere el login de la empresa y los conectores antes que los
tokens hechos a mano. Bienvenida: una demostración en vivo sobre los datos de la persona, y marca
la puesta en marcha como terminada. Nunca pide ni acepta una credencial en el chat; si alguien
pega una, le pide revocarla.

**`guide`** explica el SDLC: por qué usarlo en vez del asistente a secas, un recorrido de cinco
minutos según el perfil de la persona y qué puede pedir ese perfil hoy, revisado contra su
configuración local.

**`save`** guarda algo donde corresponde. Lo personal va a las preferencias, a la bitácora o a
las skills propias de la persona. Lo del equipo va a la carpeta que corresponde (una regla al
catálogo, un descarte a su registro, el contexto a su producto, una guía o un script a
herramientas, un cambio de método a `method/`, una skill a `skills/`) como merge request desde su
propia rama, diciendo quién lo aprueba. Antes revisa si ya existe.

### Fase uno: producto y construcción

**`define`** implementa `/define` y `/specify` para un product owner. No escribe el ticket hasta
que la definición está lista, y define el problema, no la solución. Cuestiona el pedido de a
pocos puntos (quién pide y para qué, problema, criterio de éxito con número, alcance, fuera de
alcance, usuarios y permisos, reglas de negocio que toca, casos borde, datos sensibles,
dependencias, prioridad), y muestra las dos lecturas cuando hay dos. Revisa qué existe: reglas de
negocio vigentes, tickets parecidos y el código, si hay acceso. Escribe los criterios de
aceptación como Dado, Cuando, Entonces, uno por comportamiento. Propone los casos de uso que el
requerimiento agrega o cambia y le pide al product owner validarlos uno por uno. Muestra la lista
de «listo para desarrollo», redacta el ticket en el formato del equipo, lo crea solo con
confirmación y prepara el traspaso. Tiene que funcionar también desde un cliente de chat con un
conector de tickets.

**`self-review`** implementa `/self-review`. No publica nada, revisa solo lo que introdujo el
cambio y cada hallazgo lleva archivo, línea, regla y motivo; lo descartado no se vuelve a
levantar. Lee el diff contra la rama base, la capa, el producto, el ticket y su expediente; aplica
las reglas transversales, de la capa, de seguridad y del producto con sus descartes (las
candidatas como recomendación); corre lint, tests y las pruebas de flujo que toca el cambio;
barre secretos, datos personales en logs y entradas sin validar; revisa cada criterio del ticket.
Reporta en orden: lo que bloquearía, las recomendaciones, las preguntas para producto y lo que no
tiene regla pero vale mirar. Ofrece corregir de a uno y le pasa a `harvest` los patrones sin
regla.

**`e2e`** implementa la parte automatizada de `/verify` y la regresión de release de `/deploy`.
Cinco modos: recopilar los casos de uso de un producto (propuestos hasta que el product owner los
valida), automatizar un caso, correr los casos que toca un cambio, sumar los casos validados en
un ticket y correr todos los casos antes de una release. Hace cumplir las reglas de la etapa 8 de
GATE.md: una lista de hosts permitidos que se revisa antes de abrir el navegador, los efectos
reales cortados en el runner salvo autorización, la configuración de cada persona fuera del
repositorio, las claves nunca en el chat y evidencia local de cada corrida.

**`harvest`** implementa `/harvest`. Corre sola cuando se resuelven los hilos de un merge
request, cuando el revisor termina o aprueba, cuando la revisión previa deja algo sin regla y
cuando se cierra un postmortem. Filtra los patrones que se van a repetir, que no existen todavía y
que no fueron descartados; redacta cada candidata en el formato del catálogo con su origen
contado como patrón; deja que la persona elija cuáles se levantan, y publica un merge request por
ámbito a su responsable. También prepara la cosecha mensual.

### Fases siguientes

`review`, `operate`, `postmortem`, `refine`, `design` y `validate-outcome` quedan anotadas en el
plan como pendientes y se construyen cuando la fase uno funcione con personas reales. Una vista
del equipo para liderazgo, que lea la herramienta de tickets y la plataforma de código, es
opcional y corresponde a la tercera fase: solo lee, mide a todos con la misma vara y trata un
número como un lugar donde mirar, nunca como un juicio sobre una persona.

---

## 9. Guardias y scripts

| Pieza | Qué hace |
|---|---|
| Instalador | Idempotente y con respaldo. Crea `personal/` con perfil, preferencias y bitácora; escribe el `AGENTS.md` de la carpeta de trabajo sin tocar lo que ya tiene; enlaza las skills donde el asistente las busca, o las copia donde no se puede enlazar; escribe el adaptador del asistente de la persona. Se detiene si el repositorio está suelto en el home |
| Guardia de inicio de sesión | Trae lo último de la rama principal, avisa la etapa pendiente de la puesta en marcha, verifica la identidad y entrega los perfiles habilitados, revisa los accesos, detecta si la instalación quedó atrasada y entrega la ruta de la bitácora con lo abierto |
| Guardia por mensaje | Un recordatorio corto de actualizar la bitácora cuando el mensaje dejó un avance |
| Guardia de permisos | Antes de cada escritura vigilada, mira las autorizaciones de la sesión y responde permitir o preguntar. Producción, merges y borrados preguntan siempre. Ante cualquier error, pregunta |
| Verificador de accesos | Revisa requisitos y accesos según el perfil de la persona y los muestra con el componente de estado |
| Clientes de API | Uno por sistema (plataforma de código, tickets, observabilidad), sin dependencias, que lee la credencial desde el home de la persona |
| Guías de acceso | Una por sistema, paso a paso: cómo crear la credencial con el permiso mínimo y con vencimiento, dónde guardarla y cómo comprobar que funciona |

Los scripts tienen que correr en todos los sistemas operativos del equipo. Se prefiere shell POSIX
y la biblioteca estándar de Python, sin dependencias.

---

## 10. Orden de construcción

1. La entrevista, con su resumen confirmado.
2. El esqueleto del repositorio, con `personal/` ignorado por el control de versiones. `python3
   bin/bootstrap.py sdlc <ruta> --assistant <id> --org <nombre corto>` lo escribe: la
   estructura, los archivos base desde las plantillas, el catálogo vacío con su validador, los
   tres guardias, el instalador, una copia de GATE en `gate-reference/`, primeras versiones de
   las skills `establish` y `onboard` y, para Claude Code, su adaptador con las dos skills ya
   registradas. `/establish` completa y escribe el resto.
3. `sdlc.yml`, `GOVERNANCE.md`, `CODEOWNERS` y `PLAN.md`, a partir de la entrevista.
4. El método: README, perfiles, permisos, bitácora, estilo, inicio de sesión, flujos, plantillas,
   y el paquete del cliente de chat si algún rol lo necesita.
5. El catálogo vacío, con su formato, sus ámbitos y su registro de descartes.
6. La plantilla de productos y las carpetas de los productos del piloto.
7. El `AGENTS.md` del repositorio, y `GATE.md` con la versión y las primeras diferencias.
8. Instalador, guardias, verificador de accesos, clientes de API y guías de acceso.
9. El adaptador del asistente elegido.
10. Las skills de entrada: `onboard`, `guide` y `save`.
11. Las skills de la fase uno: `define`, `self-review`, `harvest`, y `e2e` con su runner.
12. README y ONBOARDING.
13. La verificación final.

---

## 11. Verificación final

```
  VERIFICACIÓN DEL SDLC
  ──────────────────────────────────────────────────────────
  ○  Ningún archivo trae credenciales ni datos de clientes
  ○  Solo GOVERNANCE.md tiene nombres de personas
  ○  personal/ está ignorado por el control de versiones
  ○  El instalador corre dos veces sin duplicar nada
  ○  El asistente carga AGENTS.md en una sesión nueva
  ○  Abrir el asistente en la carpeta de trabajo muestra el menú
  ○  El asistente encuentra las skills
  ○  onboard deja en verde los accesos del perfil del piloto
  ○  Una escritura hacia afuera pide OK; tras autorizar, no
  ○  Producción y merges piden OK aunque haya autorización
  ○  Un guardia que falla pregunta en vez de dejar pasar
  ○  define produce un ticket de prueba listo para desarrollo
  ○  self-review revisa un cambio de prueba contra el catálogo
  ○  harvest propone una candidata desde una corrección
  ○  e2e se niega a correr contra un host no permitido
  ○  La bitácora se escribe sola tras una decisión
  ○  GATE.md nombra el commit que implementa
```

Reporta cada punto con ✓ o ✗ y, en cada ✗, qué falta y de quién depende. Si el asistente no tiene
hooks, los puntos de los guardias se reemplazan por el respaldo en la plataforma y se reportan
así.

---

## 12. Las preguntas que siempre aparecen

**¿Necesitamos todo esto para partir?** No. La fase uno es producto y construcción: un product
owner que define y traspasa con calidad, y alguien que construye, que lo toma y lo hace con las
reglas del equipo. Todo lo demás queda en el plan y espera.

**¿Podemos usar más de un asistente?** Sí. El método, el catálogo y los productos son neutrales,
y cada asistente tiene su adaptador. Cada persona usa el que el orquestador habilitó, y la
verificación corre una vez por adaptador.

**¿Y si nuestro asistente no tiene hooks?** El SDLC igual funciona, con menos garantías. El
asistente trabaja con credenciales que no pueden escribir donde importa, la rama principal está
protegida y las escrituras hacia afuera pasan por un script que pide OK. El plan lo dice, para
que nadie suponga otra cosa.

**¿Y si la herramienta de tickets o la de observabilidad no tienen conector?** Los clientes de
API de `tools/clients/` leen la credencial propia de cada persona. Son pequeños a propósito.

**¿Producto puede trabajar sin la plataforma de código?** Sí. Desde un cliente de chat con el
paquete de su rol y un conector a la herramienta de tickets, y con un acceso propio de solo
lectura al código si la organización quiere que el asistente lo lea por ellos.

**¿Por qué las pruebas de flujo viven en el SDLC y no en cada producto?** Para que la adopción no
obligue a cambiar ningún repositorio de producto, y para que las pruebas describan lo que
producto definió y no lo que hace el código. Una organización que las prefiera en cada producto
puede moverlas y anotarlo como diferencia.

**¿Por qué cada persona corre las pruebas en su equipo?** Porque la configuración de cada
ambiente, incluidos usuarios y claves, es de la persona y nunca se traspasa. Un pipeline
compartido obligaría a dejarla ahí.

**Somos tres personas. ¿Funciona igual?** Sí. Tres es el mínimo viable: una en producto y dos que
construyen y se revisan entre ellas. Los roles se concentran, y las incompatibilidades se
mantienen una vez que termina la formulación.

**Hay roles que no tienen a nadie.** El orquestador los cubre durante la formulación, y el
gobierno lo dice. Cuando alguien asume un rol, se cambia una fila.

**¿Dónde van las credenciales?** En el home de cada persona, con permisos restringidos y
vencimiento. Nunca en un repositorio, nunca en el chat, nunca un token compartido.

**¿Cómo pasamos a una versión nueva de GATE?** Con un merge request al `GATE.md` del SDLC, que
actualiza el commit fijado y revisa el mapa de diferencias. Nada se actualiza solo.

**¿Cómo devolvemos lo que aprendimos?** Proponiéndolo a GATE como candidato, contado como patrón
y sin nada que pertenezca a la organización. Ver [CONTRIBUTING.md](CONTRIBUTING.md).

**¿Cómo sabemos que está funcionando?** Por los criterios de salida de la formulación, en su fecha
de revisión. Si no se cumple ninguno, se revisa el enfoque antes de construir más.
