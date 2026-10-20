> **Español** · [English](README.md)

# GATE

**Governed, Assisted, Traceable Engineering.** La base con la que un orquestador construye el
SDLC asistido con IA de su propia organización: las etapas del ciclo de vida del software, sus
entradas y salidas, los puntos de control humano, los actores de cada una, y cómo convertir todo
eso en un proyecto SDLC propio que funciona, sobre el asistente de IA que elijas.

Agnóstico de empresa, dominio, lenguaje, plataforma y asistente de IA.

Asistencia que se detiene donde empieza el criterio.

## Qué te entrega GATE

GATE es la teoría y la fundación. El SDLC de tu organización es la casa que se construye
encima: un repositorio con tu método, tu catálogo de estándares, tus productos, tus skills, tu
gobierno y la forma en que entra cada persona.

Alguien tiene que construir esa casa. GATE lo llama el **orquestador**, y le entrega todo lo que
necesita para hacerlo: el framework, una guía de construcción escrita a la vez para una persona
y para un asistente de IA, un scaffolding, guardias neutrales que hacen cumplir los permisos y
los contratos de las skills que hay que implementar.

Funciona con Claude Code, Gemini CLI, Kiro, Codex o cualquier asistente que cargue instrucciones
persistentes, use skills y pueda trabajar en un repositorio. El orquestador elige; el SDLC se
escribe en formatos neutrales y un adaptador liviano lo conecta a ese asistente.

## Para arrancar: construye tu SDLC

```
python3 bin/bootstrap.py sdlc ../sdlc-<org> --assistant claude-code --org <org>
```

Eso escribe el esqueleto del SDLC de tu organización: los archivos base, el catálogo de
estándares vacío con su validador, los guardias de permisos, de inicio de sesión y de bitácora,
el instalador y el adaptador. Abre tu asistente dentro de esa carpeta y corre `/establish`: te
entrevista, construye cada capa siguiendo [BUILDING.es.md](BUILDING.es.md) y cierra con una
verificación que puedes leer punto por punto.

`--assistant` acepta `claude-code`, `gemini-cli`, `kiro`, `codex` u `other`. Claude Code tiene
adaptador automático; para los demás, `/establish` lo escribe a partir de la documentación
actual de tu asistente.

## Por dónde empezar a leer

**[BUILDING.es.md](BUILDING.es.md)** si eres el orquestador. Dice qué vas a decidir, qué te van
a preguntar y con qué vas a terminar.

**[START-HERE.es.md](START-HERE.es.md)** cuando el SDLC ya existe. Responde las preguntas que
vienen después: cómo inicio un proyecto nuevo, cómo inicio un requerimiento nuevo sobre uno
existente y cómo resuelvo una incidencia.

## La referencia

[GATE.md](GATE.md) es el documento completo, en inglés. Si tienes diez minutos, lee la sección 2
(el orquestador y cómo se construye el SDLC), la 3 (la puerta de entrada y el expediente) y la 7
(los actores, y la línea entre lo que hace la IA y lo que hacen las personas).

## En 95 segundos

[docs/GATE.webm](docs/GATE.webm) recorre el ciclo: el problema, los cinco momentos de invocación
humana, la línea entre lo que hace la IA y lo que hacen las personas, y el lazo de aprendizaje.
Sin audio; el guion está en [docs/video-script.md](docs/video-script.md).

## Qué contiene

```
├── BUILDING.es.md      Cómo un orquestador construye el SDLC de su organización
├── START-HERE.es.md    Las tres formas de entrar al ciclo, y qué cambia cada una
├── GATE.md             El framework completo
├── CONTRIBUTING.md     Cómo cambia el framework mismo
├── CHANGELOG.md        Qué cambió y por qué
├── skills/             Los 18 contratos de skills: 2 de fundación, 14 de ciclo, 2 transversales
├── templates/          Config del SDLC, instrucciones, gobierno, plan, producto, casos de uso,
│                       expediente, decisión, guion de QA, postmortem, regla, bitácora
├── kit/                Lo que bootstrap.py copia en un SDLC nuevo: guardias, instalador,
│                       adaptadores, método
├── adoption/           Cómo implantarlo, paso a paso
├── bin/
│   ├── bootstrap.py    Arma el SDLC de la organización, un catálogo o la config de un proyecto
│   ├── validate.py     Comprueba que los contratos estén completos y la cadena cierre
│   ├── check_config.py Reporta qué le falta al .gate/config.yml de un proyecto
│   └── build_pdf.py    Regenera el PDF desde el Markdown
└── docs/
    ├── GATE.pdf        El documento en PDF
    ├── GATE.webm       Explicativo de 95 segundos, sin audio
    └── video-script.md Guion de narración de ese video
```

## Qué no contiene, a propósito

**Las reglas de tu organización.** El catálogo es de cada organización y vive en su propio SDLC.
Este framework define cómo se alimenta, no qué dice. La sección 8 del documento explica cómo
encajan los niveles.

**Ceremonias, cadencia ni estimación.** GATE describe el recorrido de un trabajo y quién habilita
cada paso. Scrum, Kanban o lo que uses para organizar al equipo sigue funcionando encima.

**Una dependencia de un proveedor de IA.** Las instrucciones, las skills y los guardias se
escriben una vez en formatos neutrales. Lo propio de cada asistente vive en su adaptador.

## Las skills

Dos de fundación, catorce de ciclo y dos transversales. Cada una declara en su frontmatter quién
la gatilla, a quién gatilla, qué gate tiene, quién lo habilita, qué escribe fuera y qué consulta.

```
python3 bin/validate.py
```

Comprueba que todos los contratos estén completos y que la cadena cierre en los dos sentidos: si
A dice que gatilla a B, B tiene que decir que la gatilla A.

## Los momentos de invocación humana

Antes del ciclo, una vez cada uno: `/establish` cuando una organización construye su SDLC, y
`/onboard` cuando una persona se suma. En el ciclo: `/init` cuando nace la necesidad, `/build`
cuando alguien se sienta a implementar, `/review` cuando alguien revisa, varias veces, `/verify`
cuando alguien prueba y `/deploy` cuando alguien despliega.

El framework encadena todo lo demás. Los mecanismos que dependen de que una persona recuerde
invocarlos no ocurren.

## De dónde sale

GATE no nace de una recopilación bibliográfica. Sale de dirigir equipos de desarrollo y de ver,
una y otra vez, los mismos cuatro problemas: la calidad dependiendo de quién usó el asistente ese
día, las decisiones evaporándose entre conversaciones, la seguridad entrando tarde, y nadie capaz
de responder qué vara se aplicó a un cambio.

Cada regla de este framework responde a algo que salió mal en la práctica. Los gates existen
porque hubo automatismos que ejecutaron de más. Las tres incompatibilidades de rol existen porque
un equipo chico con asistencia fuerte converge rápido, y a veces hacia el lado equivocado. La
etapa 12 existe porque es fácil encontrar un catálogo de estándares vacío al lado de un cambio
con ciento cincuenta comentarios de discusión. Y la sección 2 existe porque GATE se puso en
práctica en una organización real, y construir ese SDLC enseñó lo que una fundación le tiene que
dar a un orquestador.

Es un framework vivo, en uso y en mejora continua.

## Autoría y licencia

Autor y titular: **Javier Núñez**.

| Qué | Licencia |
|---|---|
| Documentación: `GATE.md`, `BUILDING.md`, `README.md`, `skills/`, `templates/`, `adoption/`, `docs/` | [CC BY 4.0](LICENSE-DOCS) |
| Código: `bin/`, `kit/` | [MIT](LICENSE) |

Puedes usar GATE en tu organización, adaptarlo y redistribuirlo, incluso comercialmente. Lo único
que se pide a cambio es la atribución.

### Sobre el nombre

La licencia cubre la obra, no el nombre. Si adaptas GATE para tu organización, úsalo con
libertad. Si publicas un derivado con cambios sustanciales en las etapas, los gates o la
separación entre lo que hace la IA y lo que hacen las personas, ponle otro nombre y menciona su
procedencia: así «GATE» sigue significando una sola cosa.
