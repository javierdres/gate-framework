> **Español** · [English](START-HERE.md)

# Por dónde empezar

Tres formas de entrar a GATE, una por situación. Cada una dice qué haces, dónde se detiene, qué obtienes
y **en qué se diferencia de cómo trabajas hoy**.

Si solo vas a leer una cosa sobre GATE, lee esta.

**Antes de cualquiera de estas, el SDLC de la organización tiene que existir.** Si todavía no
existe, eres el orquestador y empiezas en [BUILDING.es.md](BUILDING.es.md): `python3
bin/bootstrap.py sdlc` y después `/establish` en el asistente que elegiste. Luego cada persona se
suma con `/onboard`. Todo lo que sigue supone que eso ya está hecho.

---

## A. Un proyecto nuevo

### Qué haces

```
/init
```

Entregas lo que tengas a mano: una nota de voz transcrita, un correo reenviado, una conversación
con alguien de negocio. Lo único que no puede faltar es **quién pide y para qué**.

Lo primero que hace `/init` es leer `.gate/config.yml`. En un proyecto nuevo no existe, así que
lo crea desde la plantilla, completa lo que puede detectar del repositorio, y pregunta por los
ocho campos necesarios para arrancar: la organización, su catálogo, dónde se registran los
falsos positivos, el identificador del proyecto, sus repositorios, la convención de ramas, el
gestor de tickets y dónde viven los expedientes. Nada más ocurre hasta que estén respondidos.

El resto de la config queda vacío y está bien: cada campo lleva marcada la etapa que lo
necesita, y dejarlo vacío declara que esa etapa todavía no está en uso.

Después `/init` lo clasifica como proyecto nuevo y abre el expediente. Desde ahí la cadena corre larga,
etapas 1 a 12.

### Dónde se detiene

Tres gates antes de la primera línea de código.

**Gate de producto**, después de `/define`. Alguien acepta el enunciado del problema. Nada
avanza sin clasificación de datos, que es la que decide cuánta profundidad tiene cada etapa
siguiente.

**Gate de requerimientos**, después de `/specify`. Se aceptan los criterios de aceptación, y
cada criterio no funcional lleva número. Sin número, vuelve.

**Gates técnico y de diseño**, después de `/refine` y `/design`. Los riesgos reciben dueño. Se
contrastan dos alternativas de arquitectura, y quien elige no es quien escribió la propuesta.

### Qué obtienes

Un expediente que ya tiene el problema, los criterios, los componentes afectados, los riesgos
con dueño, el plan de pruebas, el plan de observabilidad, y un registro de decisión que nombra
qué se descartó y por qué.

### En qué se diferencia de hoy

Hoy la necesidad se describe en una reunión, un equipo estima, se empieza a trabajar, y el
contexto vive en la cabeza de la gente. Las decisiones se toman en hilos de chat y desaparecen
un mes después.

Tres mejoras concretas. **La clasificación de datos existe desde el día uno**, así que el
cumplimiento no se agrega a la fuerza cuando el sistema ya maneja datos personales. **Los
criterios no funcionales llevan número**, así QA tiene algo que verificar en la etapa 8 y producción
algo que vigilar en la 10; "que sea rápido" no verifica nada. Y **la decisión de arquitectura queda
registrada con sus alternativas**, así dentro de un año nadie tiene que reconstruir por qué se
construyó de esta manera.

Lo que cuesta: tres aprobaciones antes de la primera línea de código.

---

## B. Un requerimiento nuevo sobre un proyecto existente

### Qué haces

```
/init
```

Misma entrada, distinta clasificación. `/init` reconoce que es un cambio sobre algo que ya
existe y toma la **cadena corta**: entra en la etapa 2 o 3 con el expediente del sistema ya
cargado, y se salta la definición cuando el problema ya se entiende.

### Dónde se detiene

Un gate antes de construir: el técnico, después de `/refine`.

Si el cambio trae una decisión de arquitectura, también el de diseño. Si no la trae, la etapa 4
se salta.

Después lo de siempre: `/build`, `/self-review` en privado, `/review` con otra persona,
`/verify`, `/deploy`.

### Qué obtienes

Un mapa de impacto hecho leyendo el código real, los riesgos que ese cambio introduce, y las
reglas del catálogo que aplican a lo que vas a tocar.

### En qué se diferencia de hoy

Hoy aparece un ticket en el backlog, alguien lo toma, grepea un rato para averiguar qué afecta,
y construye. El impacto se deduce de lo que recuerda del sistema.

Tres mejoras. **El mapa de impacto se lee, no se recuerda**, y un mapa hecho de memoria se
equivoca justo en los sistemas que más han cambiado. **El catálogo se consulta antes de elegir un
patrón**, así dejas de redescubrir reglas que el equipo ya acordó y de volver a discutirlas en
la revisión. Y **la revisión previa detecta en privado** lo que de otro modo detectaría un colega en
público, que es más rápido y cuesta menos.

Lo que cuesta: una aprobación antes de construir, y escribir un mapa de impacto que de todos modos
ya llevabas en la cabeza.

---

## C. Una incidencia en un proyecto existente

### Qué haces

```
/init
```

`/init` lo clasifica como incidente y toma la cadena de operación, entrando en la etapa 10.

`/operate` correlaciona las fuentes de datos a partir del síntoma, separa la causa del ruido, y
sostiene cada afirmación en la fuente que la puede probar. Si no puede probar algo, lo dice en
vez de suponerlo.

### Dónde se detiene

El gate de operación: no se toca nada en producción, ni siquiera silenciar una alerta, sin que
una persona lo confirme. La reversión se propone, nunca la decide el asistente.

El arreglo en sí va por el camino B, porque un arreglo es un cambio.

Al cerrar el incidente, `/postmortem` reconstruye la línea de tiempo **desde las fuentes**, no
desde la memoria de quien estuvo de turno, y separa la causa raíz de los factores que
contribuyeron.

Mientras la organización no tiene `/operate` ni `/postmortem`, que llegan en su segunda fase, el
camino es el mismo a mano: se diagnostica desde la fuente de verdad, filtrando por ambiente, y se
cierra con un postmortem escrito desde la plantilla, guardado junto al producto afectado y con su
causa raíz entregada a `/harvest`.

### Qué obtienes

Un diagnóstico con evidencia, un postmortem con línea de tiempo trazable, y la causa raíz
entregada a `/harvest`, que la convierte en regla candidata.

### En qué se diferencia de hoy

Hoy alguien se da cuenta, varios se suman, se arregla, y si hay postmortem se escribe de
memoria y después nadie lo relee. La misma clase de falla vuelve seis meses después.

Dos mejoras, y la segunda es lo que de verdad importa. **La línea de tiempo se reconstruye desde las
fuentes**, así la causa raíz es la real y no la versión más plausible contada a la mañana
siguiente. Y **la causa raíz se convierte en una regla que aplica a los cambios futuros**: ese
es el único camino por el que un incidente deja de repetirse, en vez de quedar en el recuerdo
de quien estuvo ahí.

Lo que cuesta: el postmortem deja de ser opcional, y la cosecha se ejecuta tenga ganas alguien o no.

---

## Lo que ganas con GATE

| | Cómo suele ocurrir | Con GATE |
|---|---|---|
| Contexto entre etapas | Se reconstruye en cada reunión de traspaso | Viaja dentro del expediente |
| Impacto de un cambio | Se deduce de lo que uno recuerda | Se lee directamente del código |
| Criterios de aceptación | Prosa, no verificable | Con número, verificable en QA y en producción |
| Decisiones de arquitectura | En un hilo de chat, perdidas en un mes | Registradas con lo que se descartó |
| Revisión | Depende de quién revisó y de cómo venía ese día | Dos pasadas distintas, una privada y una pública |
| Un hallazgo rechazado | Se vuelve a discutir el mes siguiente | Queda registrado con su motivo y no se repite |
| Un incidente | Se arregla y vuelve a ocurrir | La causa raíz pasa a ser una regla que bloquea ese tipo de falla |
| Cumplimiento | Se agrega cuando ya es caro | Datos clasificados en la etapa 1 |
| ¿Esto sirvió de algo? | Nadie lo pregunta | La etapa 11 lo pregunta, con datos |
| Auditoría | Nadie sabe responder | El expediente lo responde |

---

## Lo que cuesta

**Aprobaciones que antes no estaban.** Tres para un proyecto nuevo, una para un cambio. Cada
una es una persona leyendo algo ya redactado, pero es tiempo que antes no existía.

**Escribir lo que antes vivía en cabezas.** El mapa de impacto, la decisión de diseño, los
riesgos con dueño. Se recupera desde la segunda vez que tocas el mismo sistema, no desde la
primera.

**Disciplina en el lazo.** Si `/harvest` no corre, el catálogo queda vacío y GATE se convierte en
burocracia sin retorno. Por eso lo dispara la revisión y no la memoria de alguien.

---

## El mínimo para empezar mañana

No necesitas el framework completo. El piso es más bajo de lo que parece:

- Un orquestador, y un asistente de IA elegido por él que cargue instrucciones persistentes y skills
- Tres personas que cumplan las [tres incompatibilidades de rol](GATE.md#the-three-incompatibilities)
- Credenciales personales por persona
- Una convención de ramas que enlace con el ticket
- Un catálogo de estándares vacío con su validador de formato, que escribe `bootstrap.py sdlc`

Con eso construyes el SDLC y llegas al paso 3 de la [adopción](adoption/README.md), que es la
revisión previa, y ya
estás obteniendo valor. Las fuentes de datos, la reversión ensayada y los indicadores de
negocio llegan en los pasos siguientes.
