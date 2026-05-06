from __future__ import annotations

from dataclasses import dataclass

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.exercises.models import Ejercicio, Equipo, GrupoMuscular


@dataclass(frozen=True)
class SeedExercise:
    nombre: str
    grupo_slug: str
    nivel: str = "principiante"
    equipos: tuple[str, ...] = ()
    descripcion: str = ""
    instrucciones: str = ""
    duracion_minutos: int | None = None  # None = ejercicio de fuerza (series/reps)


class Command(BaseCommand):
    help = "Crea un catálogo base de equipos, grupos musculares y ejercicios."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Borra ejercicios existentes antes de sembrar (no borra equipos/grupos).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = bool(options["reset"])

        grupos = [
            ("Pecho", "pecho"),
            ("Espalda", "espalda"),
            ("Hombros", "hombros"),
            ("Bíceps", "biceps"),
            ("Tríceps", "triceps"),
            ("Piernas", "piernas"),
            ("Glúteos", "gluteos"),
            ("Abdomen", "abdomen"),
            ("Core", "core"),
            ("Pantorrillas", "pantorrillas"),
            ("Antebrazos", "antebrazos"),
            ("Cardio", "cardio"),
            ("Movilidad", "movilidad"),
        ]

        for nombre, slug in grupos:
            GrupoMuscular.objects.get_or_create(
                slug=slug,
                defaults={"nombre": nombre},
            )

        # Sembrar equipos usando los choices del modelo
        equipo_defaults = {
            "banco": "🪑",
            "peso_corporal": "🤸",
            "disco": "💿",
            "mancuernas": "🏋️",
            "barra": "🏋️",
            "barra_dominadas": "🧗",
            "kettlebell": "🔔",
            "banda": "🟣",
        }

        for key, _label in Equipo.EQUIPO_CHOICES:
            Equipo.objects.get_or_create(
                nombre=key,
                defaults={"icono": equipo_defaults.get(key, "🏋️")},
            )

        if reset:
            deleted, _ = Ejercicio.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"--reset: borrados {deleted} registros."))

        seeds: list[SeedExercise] = [
            # Pecho
            SeedExercise(
                "Press de Banca con Barra",
                "pecho",
                "intermedio",
                ("barra", "banco"),
                "Ejercicio base para fuerza e hipertrofia del pecho.",
                "Retracción escapular, pies firmes, baja controlado al pecho y empuja.",
            ),
            SeedExercise(
                "Press inclinado con mancuernas",
                "pecho",
                "intermedio",
                ("mancuernas", "banco"),
                "Enfatiza porción superior del pectoral.",
                "Codos 30–45°, controla la bajada y sube sin chocar mancuernas.",
            ),
            SeedExercise(
                "Flexiones (Push-ups)",
                "pecho",
                "principiante",
                ("peso_corporal",),
                "En posición de plancha, baja el pecho al suelo y empuja.",
                "Cuerpo en línea, core activo, baja controlado y empuja sin colapsar la cadera.",
            ),
            SeedExercise(
                "Press con Mancuernas",
                "pecho",
                "principiante",
                ("banco", "mancuernas"),
                "Acostado en el banco con mancuernas, baja controlado y empuja.",
            ),
            SeedExercise(
                "Aperturas con Mancuernas",
                "pecho",
                "intermedio",
                ("banco", "mancuernas"),
                "Acostado, abre los brazos en arco hasta estirar el pecho.",
                "Codos ligeramente flexionados, abre hasta rango cómodo y vuelve sin chocar mancuernas.",
            ),
            # Espalda
            SeedExercise(
                "Dominadas",
                "espalda",
                "intermedio",
                ("barra_dominadas",),
                "Cuelga de la barra y jala el cuerpo hacia arriba.",
                "Inicia con escápulas, sube con el pecho y baja completo controlado.",
            ),
            SeedExercise(
                "Remo con Barra",
                "espalda",
                "intermedio",
                ("barra",),
                "Inclinado, jala la barra hacia el abdomen.",
                "Bisagra de cadera, espalda neutra, rema al ombligo y controla.",
            ),
            SeedExercise(
                "Remo con Mancuerna",
                "espalda",
                "principiante",
                ("mancuernas", "banco"),
                "Apoyado en el banco, jala la mancuerna hacia la cadera.",
                "Tronco estable, codo hacia atrás y abajo, controla la bajada.",
            ),
            SeedExercise(
                "Pull-down con Banda",
                "espalda",
                "principiante",
                ("banda",),
                "Jala la banda de arriba hacia abajo, imitando las dominadas.",
                "Ancla alto, hombros abajo, tira con dorsales y controla el regreso.",
            ),
            # Hombros
            SeedExercise(
                "Press Militar con Barra",
                "hombros",
                "intermedio",
                ("barra",),
                "De pie, empuja la barra desde los hombros hacia arriba.",
                "Glúteos y core firmes, barra sube en línea, evita arquear la espalda.",
            ),
            SeedExercise(
                "Elevaciones laterales",
                "hombros",
                "principiante",
                ("mancuernas",),
                "Eleva las mancuernas hacia los lados hasta la altura de los hombros.",
                "Codos suaves, sube hasta hombro, controla la bajada sin impulso.",
            ),
            SeedExercise(
                "Press Arnold",
                "hombros",
                "intermedio",
                ("mancuernas",),
                "Gira las muñecas mientras empujas las mancuernas hacia arriba.",
                "Controla el giro, evita arquear la espalda, baja lento.",
            ),
            # Bíceps / tríceps
            SeedExercise(
                "Curl de Bíceps con Barra",
                "biceps",
                "principiante",
                ("barra",),
                "Parado, flexiona los codos levantando la barra.",
                "Codos pegados, evita balanceo, sube y baja controlado.",
            ),
            SeedExercise(
                "Curl con Mancuernas",
                "biceps",
                "principiante",
                ("mancuernas",),
                "Alternado o simultáneo, flexiona los codos con mancuernas.",
                "Hombros quietos, controla la bajada y evita impulso.",
            ),
            SeedExercise(
                "Curl martillo",
                "biceps",
                "principiante",
                ("mancuernas",),
                "Enfoca braquial y antebrazo.",
                "Agarre neutro, sube sin mover el hombro, baja lento.",
            ),
            SeedExercise(
                "Curl con Banda",
                "biceps",
                "principiante",
                ("banda",),
                "Pisa la banda y realiza curl de bíceps.",
                "Mantén tensión constante, codos fijos, controla el regreso.",
            ),
            SeedExercise(
                "Fondos en banco",
                "triceps",
                "principiante",
                ("banco",),
                "Buen inicio para tríceps (variación en banco).",
                "Hombros abajo, codos atrás, baja hasta cómodo y extiende.",
            ),
            SeedExercise(
                "Extensión de tríceps por encima (mancuerna)",
                "triceps",
                "intermedio",
                ("mancuernas",),
                "Trabajo de cabeza larga del tríceps.",
                "Codos apuntan al frente, baja controlado y extiende completo.",
            ),
            SeedExercise(
                "Extensión de Tríceps",
                "triceps",
                "principiante",
                ("banda", "mancuernas"),
                "Extiende el codo con resistencia de banda o mancuerna.",
                "Codos estables, extensión completa sin bloquear agresivo, controla el retorno.",
            ),
            SeedExercise(
                "Fondos en Paralelas",
                "triceps",
                "intermedio",
                ("peso_corporal",),
                "Baja y sube el cuerpo en paralelas apoyando en los brazos.",
                "Mantén hombros abajo, codos atrás, rango cómodo y controlado.",
            ),
            SeedExercise(
                "Press Francés",
                "triceps",
                "intermedio",
                ("barra", "mancuernas"),
                "Acostado, flexiona los codos detrás de la cabeza y extiende.",
                "Codos fijos, baja controlado y extiende sin perder tensión.",
            ),
            # Piernas / glúteos
            SeedExercise(
                "Sentadilla con Barra",
                "piernas",
                "intermedio",
                ("barra",),
                "Con barra en los hombros, baja como si fueras a sentarte.",
                "Rodillas siguen punta del pie, core firme, profundidad según movilidad.",
            ),
            SeedExercise(
                "Sentadilla con Peso Corporal",
                "piernas",
                "principiante",
                ("peso_corporal",),
                "Baja hasta que los muslos queden paralelos al suelo.",
                "Talones apoyados, pecho arriba, controla la bajada.",
            ),
            SeedExercise(
                "Prensa con Disco",
                "piernas",
                "intermedio",
                ("disco",),
                "Usa un disco como peso adicional para variaciones de sentadilla.",
                "Sujeta el disco firme, mantén el core activo y controla el rango.",
            ),
            SeedExercise(
                "Peso muerto rumano",
                "piernas",
                "intermedio",
                ("barra", "mancuernas"),
                "Con piernas casi extendidas, baja el peso manteniendo la espalda recta.",
                "Espalda neutra, peso cerca de piernas, baja hasta sentir tensión y sube.",
            ),
            SeedExercise(
                "Zancadas",
                "piernas",
                "principiante",
                ("mancuernas", "peso_corporal"),
                "Da un paso adelante y baja la rodilla trasera al suelo.",
                "Paso largo, torso erguido, baja controlado y empuja con el talón.",
            ),
            SeedExercise(
                "Sentadilla con Kettlebell",
                "piernas",
                "principiante",
                ("kettlebell",),
                "Sostén el kettlebell frente al pecho y realiza sentadilla goblet.",
                "Codos adentro, espalda neutra, baja controlado y sube fuerte.",
            ),
            SeedExercise(
                "Puente de glúteos",
                "gluteos",
                "principiante",
                ("peso_corporal",),
                "Activa glúteos y estabiliza pelvis.",
                "Empuja con talones, aprieta glúteos arriba, evita hiperextender lumbar.",
            ),
            SeedExercise(
                "Hip Thrust con Barra",
                "gluteos",
                "intermedio",
                ("barra", "banco"),
                "Apoya la espalda en el banco y eleva las caderas con barra.",
                "Mentón adentro, costillas abajo, sube hasta pelvis neutra y controla.",
            ),
            SeedExercise(
                "Patada de Glúteo con Banda",
                "gluteos",
                "principiante",
                ("banda",),
                "Con banda en los tobillos, realiza patadas traseras.",
                "Evita arquear la espalda, contrae glúteo arriba y controla abajo.",
            ),
            # Core
            SeedExercise(
                "Plancha",
                "core",
                "principiante",
                ("peso_corporal",),
                "Estabilidad del core.",
                "Codos bajo hombros, glúteos firmes, evita hundir la zona lumbar.",
            ),
            SeedExercise(
                "Elevaciones de piernas",
                "core",
                "intermedio",
                ("peso_corporal",),
                "Enfoca flexores y control abdominal.",
                "Pega la espalda baja al suelo, sube y baja sin impulso.",
            ),
            # Abdomen
            SeedExercise(
                "Plancha Abdominal",
                "abdomen",
                "principiante",
                ("peso_corporal",),
                "Mantén la posición de plancha con el cuerpo recto.",
                "Codos bajo hombros, costillas abajo, glúteos firmes, respira.",
            ),
            SeedExercise(
                "Crunchs",
                "abdomen",
                "principiante",
                ("peso_corporal",),
                "Acostado, contrae el abdomen levantando los hombros.",
                "Barbilla ligeramente adentro, sube corto, evita tirar del cuello.",
            ),
            SeedExercise(
                "Rueda Abdominal",
                "abdomen",
                "avanzado",
                ("peso_corporal",),
                "Desde rodillas, rueda hacia adelante extendiendo el cuerpo.",
                "Mantén pelvis neutra, no colapses lumbar, controla la vuelta.",
            ),
            # Pantorrillas
            SeedExercise(
                "Elevaciones de Pantorrilla con Mancuernas",
                "pantorrillas",
                "principiante",
                ("mancuernas",),
                "De pie con mancuernas, elévate en puntas de pie.",
                "Pausa arriba, baja completo y repite sin rebotes.",
            ),
            SeedExercise(
                "Elevaciones de Pantorrilla",
                "pantorrillas",
                "principiante",
                ("peso_corporal", "barra"),
                "Elévate en puntas de pie con o sin peso adicional.",
                "Rango completo, controla, mantén equilibrio.",
            ),
            # Cardio / movilidad
            SeedExercise(
                "Jumping jacks",
                "cardio",
                "principiante",
                ("peso_corporal",),
                "Calentamiento cardiovascular sencillo.",
                "Ritmo constante, aterriza suave y controla respiración.",
            ),
            SeedExercise(
                "Burpees",
                "cardio",
                "avanzado",
                ("peso_corporal",),
                "Full body con alta demanda cardiovascular.",
                "Mantén técnica: plancha firme, salto controlado, respira.",
            ),
            SeedExercise(
                "Movilidad de cadera (90/90)",
                "movilidad",
                "principiante",
                ("peso_corporal",),
                "Mejora rotación interna/externa de cadera.",
                "Postura 90/90, inclina el torso al frente con espalda larga y respira.",
            ),

            # ── Pecho adicional ────────────────────────────────────────────────
            SeedExercise("Press Declinado con Barra", "pecho", "intermedio", ("barra", "banco"),
                "Enfatiza la porción inferior del pectoral.",
                "Banco inclinado negativamente, agarre ligeramente más ancho, baja controlado al pecho bajo."),
            SeedExercise("Press Inclinado con Barra", "pecho", "intermedio", ("barra", "banco"),
                "Trabaja la porción superior del pectoral.",
                "Banco a 30-45°, barra baja al pecho superior, empuja en línea recta."),
            SeedExercise("Fondos en Paralelas (Pecho)", "pecho", "intermedio", ("peso_corporal",),
                "Variante de fondos inclinando el torso al frente para mayor activación pectoral.",
                "Inclínate ligeramente al frente, codos apuntan hacia afuera, baja controlado."),
            SeedExercise("Pullover con Mancuerna", "pecho", "intermedio", ("mancuernas", "banco"),
                "Estira y activa pectoral y serrato.",
                "Acostado transversal en el banco, baja la mancuerna detrás de la cabeza manteniendo el arco."),
            SeedExercise("Cruce de Banda", "pecho", "principiante", ("banda",),
                "Aislamiento de pectoral con banda elástica.",
                "Ancla la banda a los lados, lleva las manos al centro cruzándolas ligeramente."),
            SeedExercise("Flexiones Declinadas", "pecho", "intermedio", ("peso_corporal",),
                "Pies elevados para mayor activación del pecho superior.",
                "Pies en banco o superficie elevada, cuerpo recto, baja controlado."),

            # ── Espalda adicional ──────────────────────────────────────────────
            SeedExercise("Peso Muerto Convencional", "espalda", "intermedio", ("barra", "disco"),
                "El rey del levantamiento de fuerza. Activa espalda, glúteos y piernas.",
                "Espalda neutra, cadera alta al inicio, empuja el suelo y lleva caderas hacia adelante."),
            SeedExercise("Remo Alto con Barra", "espalda", "intermedio", ("barra",),
                "Activa trapecio y deltoides posterior.",
                "Barra cerca del cuerpo, sube los codos por encima de los hombros."),
            SeedExercise("Superman", "espalda", "principiante", ("peso_corporal",),
                "Fortalece los erectores espinales boca abajo.",
                "Extiende brazos y piernas simultáneamente, pausa 2 segundos arriba."),
            SeedExercise("Face Pull con Banda", "espalda", "principiante", ("banda",),
                "Trabaja deltoides posterior y manguito rotador.",
                "Ancla la banda a la altura de la cara, jala hacia la frente con codos altos."),
            SeedExercise("Remo Sentado con Banda", "espalda", "principiante", ("banda",),
                "Remo horizontal con banda para espalda media.",
                "Siéntate, pisa la banda, jala hacia el ombligo con espalda recta."),
            SeedExercise("Chin-Ups", "espalda", "intermedio", ("barra_dominadas",),
                "Dominadas con agarre supino, mayor activación del bíceps.",
                "Agarre supino a la altura de los hombros, sube hasta la barbilla sobre la barra."),
            SeedExercise("Remo Pendlay", "espalda", "avanzado", ("barra",),
                "Variante estricta del remo con barra desde el suelo.",
                "Espalda paralela al suelo, jala explosivo y devuelve la barra al suelo completo."),

            # ── Hombros adicional ──────────────────────────────────────────────
            SeedExercise("Elevaciones Frontales con Mancuernas", "hombros", "principiante", ("mancuernas",),
                "Activa el deltoides anterior.",
                "Brazos extendidos, sube hasta la altura del hombro, controla la bajada."),
            SeedExercise("Pájaros con Mancuernas", "hombros", "principiante", ("mancuernas",),
                "Trabaja el deltoides posterior e isquiotibiales.",
                "Inclinado, codos suaves, sube las mancuernas hacia afuera como alas."),
            SeedExercise("Press con Kettlebell", "hombros", "intermedio", ("kettlebell",),
                "Press unilateral para estabilidad del hombro.",
                "Kettlebell en posición rack, empuja verticalmente, core firme."),
            SeedExercise("Encogimientos con Barra", "hombros", "principiante", ("barra",),
                "Fortalece el trapecio superior.",
                "Encoge los hombros hacia las orejas, pausa y baja controlado."),
            SeedExercise("Elevaciones Laterales con Banda", "hombros", "principiante", ("banda",),
                "Elevaciones laterales con resistencia de banda.",
                "Pisa la banda, eleva los brazos hasta la altura del hombro, controla."),
            SeedExercise("W Raise", "hombros", "principiante", ("mancuernas", "peso_corporal"),
                "Activa deltoides posterior y retractores escapulares.",
                "Boca abajo o inclinado, forma una W con los brazos, sube y baja."),

            # ── Bíceps adicional ───────────────────────────────────────────────
            SeedExercise("Curl Concentrado", "biceps", "principiante", ("mancuernas",),
                "Máximo aislamiento del bíceps.",
                "Codo apoyado en la rodilla, sube completo y baja sin balanceo."),
            SeedExercise("Curl en Banca Inclinada", "biceps", "intermedio", ("mancuernas", "banco"),
                "Mayor estiramiento del bíceps por la posición inclinada.",
                "Espalda apoyada en banca inclinada, brazos colgando, curla sin impulso."),
            SeedExercise("Curl 21s con Barra", "biceps", "intermedio", ("barra",),
                "Técnica de 3 rangos de movimiento para máxima congestión.",
                "7 reps mitad inferior, 7 mitad superior, 7 completos sin pausa."),
            SeedExercise("Curl Invertido", "biceps", "intermedio", ("barra", "mancuernas"),
                "Trabaja braquiorradial y antebrazos.",
                "Agarre prono, sube controlado, evita girar las muñecas."),

            # ── Tríceps adicional ──────────────────────────────────────────────
            SeedExercise("Kick Back con Mancuerna", "triceps", "principiante", ("mancuernas",),
                "Aislamiento del tríceps inclinado.",
                "Codo pegado al cuerpo y fijo, extiende completamente la mano detrás."),
            SeedExercise("Flexiones Diamante", "triceps", "intermedio", ("peso_corporal",),
                "Variante de flexión con manos juntas para mayor énfasis en tríceps.",
                "Manos en forma de diamante bajo el pecho, codos atrás, baja controlado."),
            SeedExercise("Pushdown con Banda", "triceps", "principiante", ("banda",),
                "Extensión de tríceps de pie con banda anclada en alto.",
                "Codos fijos al costado, extiende hasta bloqueo suave y controla el retorno."),
            SeedExercise("Skullcrusher con Mancuernas", "triceps", "intermedio", ("mancuernas", "banco"),
                "Trabaja la cabeza larga del tríceps.",
                "Acostado, codos apuntan al techo, baja las mancuernas hacia las orejas y extiende."),

            # ── Piernas adicional ──────────────────────────────────────────────
            SeedExercise("Sentadilla Búlgara", "piernas", "intermedio", ("mancuernas", "banco"),
                "Sentadilla a una pierna con pie trasero elevado. Unilateral y funcional.",
                "Pie trasero en banco, baja la rodilla trasera sin tocar, torso erguido."),
            SeedExercise("Step-Ups con Mancuernas", "piernas", "principiante", ("mancuernas",),
                "Subir y bajar de un escalón con resistencia adicional.",
                "Paso completo, empuja con el talón, mantén el tronco estable."),
            SeedExercise("Peso Muerto a Una Pierna", "piernas", "intermedio", ("mancuernas", "barra"),
                "Equilibrio y fuerza unilateral en isquiotibiales.",
                "Una pierna levantada, espalda neutra, baja el peso rozando la pierna."),
            SeedExercise("Curl Femoral con Mancuerna", "piernas", "principiante", ("mancuernas",),
                "Aislamiento de isquiotibiales boca abajo.",
                "Boca abajo, mancuerna entre los pies, curla controlado sin arquear."),
            SeedExercise("Sentadilla Sumo", "piernas", "principiante", ("barra", "mancuernas", "kettlebell"),
                "Piernas abiertas y pies en ángulo para mayor activación del aductor.",
                "Pies a doble ancho de hombros, puntas a 45°, baja controlado."),
            SeedExercise("Good Morning con Barra", "piernas", "intermedio", ("barra",),
                "Fortalece isquiotibiales y erectores con bisagra de cadera.",
                "Barra en hombros, rodillas suaves, inclina el torso hasta la horizontal."),
            SeedExercise("Wall Sit", "piernas", "principiante", ("peso_corporal",),
                "Isométrico de cuádriceps contra la pared.",
                "Espalda en la pared, rodillas a 90°, mantén la posición el máximo tiempo."),

            # ── Glúteos adicional ──────────────────────────────────────────────
            SeedExercise("Clamshells con Banda", "gluteos", "principiante", ("banda",),
                "Activa abductores y rotadores externos de cadera.",
                "Banda sobre las rodillas, acostado lateral, abre y cierra controlado."),
            SeedExercise("Abducción de Cadera con Banda", "gluteos", "principiante", ("banda",),
                "Trabaja glúteo medio en pie.",
                "Banda en tobillos, eleva una pierna al lado manteniendo el tronco estable."),
            SeedExercise("Peso Muerto Sumo con Barra", "gluteos", "intermedio", ("barra",),
                "Énfasis en glúteos e isquiotibiales con apertura amplia.",
                "Agarre entre las piernas, pies anchos, espalda neutra y sube explosivo."),
            SeedExercise("Hip Thrust con Mancuerna", "gluteos", "principiante", ("mancuernas", "banco"),
                "Variante de hip thrust con mancuerna para casa.",
                "Espalda en el banco, mancuerna sobre las caderas, sube hasta pelvis neutra."),
            SeedExercise("Kickback con Kettlebell", "gluteos", "intermedio", ("kettlebell",),
                "Extensión de cadera de pie con kettlebell.",
                "Sostén la pesa, extiende una pierna hacia atrás contrayendo el glúteo en el tope."),

            # ── Core adicional ─────────────────────────────────────────────────
            SeedExercise("Plancha Lateral", "core", "principiante", ("peso_corporal",),
                "Estabilidad oblicua y cadena lateral.",
                "Codo bajo el hombro, cadera elevada, cuerpo en línea recta."),
            SeedExercise("Dead Bug", "core", "principiante", ("peso_corporal",),
                "Coordinación y estabilidad profunda del core.",
                "Espalda baja pegada al suelo, extiende brazo y pierna opuestos alternados."),
            SeedExercise("Pallof Press con Banda", "core", "intermedio", ("banda",),
                "Anti-rotación para fortalecer el core funcional.",
                "Banda anclada al lado, lleva las manos al frente y resiste la rotación."),
            SeedExercise("Rollout con Barra", "core", "avanzado", ("barra", "disco"),
                "Extensión total del core con barra.",
                "Desde rodillas, rueda la barra hacia adelante sin colapsar la lumbar."),
            SeedExercise("V-Ups", "core", "intermedio", ("peso_corporal",),
                "Activación simultánea de flexores y abdomen superior.",
                "Sube piernas y torso al mismo tiempo formando una V, baja controlado."),
            SeedExercise("Mountain Climbers", "core", "intermedio", ("peso_corporal",),
                "Cardio y core simultáneos en posición de plancha.",
                "Posición de plancha, lleva rodillas al pecho alternadas rápidamente."),

            # ── Abdomen adicional ──────────────────────────────────────────────
            SeedExercise("Bicicleta Abdominal", "abdomen", "principiante", ("peso_corporal",),
                "Activa oblicuos y recto abdominal.",
                "Manos en la cabeza, codo al lado contrario, piernas en pedaleo alternado."),
            SeedExercise("Sit-Ups", "abdomen", "principiante", ("peso_corporal",),
                "Elevación completa del torso desde el suelo.",
                "Pies fijos, sube hasta tocar las rodillas, baja controlado."),
            SeedExercise("Russian Twist", "abdomen", "intermedio", ("peso_corporal", "mancuernas", "disco"),
                "Rotación del torso para oblicuos.",
                "Sentado con torso inclinado, gira de lado a lado con o sin peso."),
            SeedExercise("Hanging Leg Raise", "abdomen", "avanzado", ("barra_dominadas",),
                "Elevación de piernas colgando para abdomen inferior.",
                "Cuelga de la barra, sube las piernas controlado sin balanceo."),
            SeedExercise("Oblicuos con Banda", "abdomen", "principiante", ("banda",),
                "Flexión lateral de torso con resistencia.",
                "Banda anclada al lado, tira hacia arriba inclinando el torso, controla."),

            # ── Pantorrillas adicional ─────────────────────────────────────────
            SeedExercise("Elevación de Pantorrilla Unilateral", "pantorrillas", "intermedio", ("peso_corporal",),
                "Mayor rango y dificultad por ser unilateral.",
                "Apóyate en una sola pierna, sube y baja con rango completo."),
            SeedExercise("Elevación de Pantorrilla Sentado", "pantorrillas", "principiante", ("mancuernas", "disco"),
                "Trabaja el sóleo con rodillas flexionadas.",
                "Sentado con disco o mancuernas en las rodillas, eleva y baja completo."),

            # ── Cardio adicional ───────────────────────────────────────────────
            SeedExercise("Skipping", "cardio", "principiante", ("peso_corporal",),
                "Carrera en el lugar elevando las rodillas.",
                "Eleva rodillas a 90°, mantén ritmo constante y aterriza suave."),
            SeedExercise("Bear Crawl", "cardio", "intermedio", ("peso_corporal",),
                "Desplazamiento en cuadrupedia que activa todo el cuerpo.",
                "Rodillas a 5 cm del suelo, avanza con mano y pie opuestos, core firme."),
            SeedExercise("Swing con Kettlebell", "cardio", "intermedio", ("kettlebell",),
                "Cardio de alta intensidad con glúteos e isquiotibiales.",
                "Bisagra de cadera explosiva, la pesa guiada por las caderas, no por los brazos."),
            SeedExercise("Box Jumps", "cardio", "intermedio", ("peso_corporal",),
                "Potencia explosiva de piernas.",
                "Salta al cajón aterrizando suave, baja caminando o saltando controlado."),
            SeedExercise("Sprint en el Lugar", "cardio", "principiante", ("peso_corporal",),
                "Sprint de alta intensidad sin desplazamiento.",
                "Corre tan rápido como puedas en el lugar durante el intervalo indicado."),

            # ── Movilidad adicional ────────────────────────────────────────────
            SeedExercise("World's Greatest Stretch", "movilidad", "principiante", ("peso_corporal",),
                "Movilidad completa de cadera, torácica y hombros.",
                "Posición de estocada, coloca el codo al suelo, luego rota abriendo el brazo al techo."),
            SeedExercise("Rotación Torácica", "movilidad", "principiante", ("peso_corporal",),
                "Mejora la movilidad de la columna torácica.",
                "En cuadrupedia, mano en la cabeza, rota el codo hacia el techo y hacia abajo."),
            SeedExercise("Hip Flexor Stretch", "movilidad", "principiante", ("peso_corporal",),
                "Estiramiento del psoas y flexores de cadera.",
                "Posición de caballero, empuja la cadera al frente suavemente, 30s cada lado."),
            SeedExercise("Apertura de Pecho con Banda", "movilidad", "principiante", ("banda",),
                "Estiramiento activo de pectoral y hombros anteriores.",
                "Banda detrás, agárrate de los extremos y lleva los brazos hacia atrás abriendo el pecho."),

            # ══════════════════════════════════════════════════
            # ANTEBRAZOS (grupo sin ejercicios — prioridad alta)
            # ══════════════════════════════════════════════════
            SeedExercise("Curl de Muñeca con Barra", "antebrazos", "principiante", ("barra",),
                "Flexión de muñeca sentado para fortalecer flexores del antebrazo.",
                "Sentado, antebrazos en los muslos, baja la barra controlado y sube con las muñecas."),
            SeedExercise("Extensión de Muñeca con Barra", "antebrazos", "principiante", ("barra",),
                "Trabaja los extensores del antebrazo.",
                "Posición inversa al curl de muñeca, extiende la muñeca hacia arriba."),
            SeedExercise("Curl de Muñeca con Mancuernas", "antebrazos", "principiante", ("mancuernas",),
                "Flexión de muñeca unilateral con mancuerna.",
                "Antebrazo apoyado, agarra la mancuerna con palma hacia arriba y curla la muñeca."),
            SeedExercise("Curl Inverso con Barra", "antebrazos", "intermedio", ("barra",),
                "Curl de bíceps con agarre prono para antebrazos y braquiorradial.",
                "Palmas hacia abajo, sube la barra sin mover los codos, baja controlado."),
            SeedExercise("Curl Inverso con Mancuernas", "antebrazos", "principiante", ("mancuernas",),
                "Fortalece braquiorradial y extensores del antebrazo.",
                "Palmas hacia abajo, curla las mancuernas y baja controlado."),
            SeedExercise("Farmer's Walk", "antebrazos", "principiante", ("mancuernas", "kettlebell"),
                "Caminata con pesas pesadas para agarre y antebrazos.",
                "Pesas pesadas a los lados, camina erguido manteniendo el agarre firme."),
            SeedExercise("Dead Hang", "antebrazos", "principiante", ("barra_dominadas",),
                "Colgarse de la barra para fuerza de agarre y descompresión.",
                "Cuelga con agarre prono o supino, hombros activos, aguanta el máximo tiempo."),
            SeedExercise("Squeeze de Pelota", "antebrazos", "principiante", (),
                "Ejercicio de agarre con pelota de estrés o grip trainer.",
                "Aprieta y suelta la pelota de forma controlada, 3 sets de 20 rep por mano."),
            SeedExercise("Curl de Muñeca con Banda", "antebrazos", "principiante", ("banda",),
                "Flexión de muñeca con resistencia de banda.",
                "Pisa la banda, agarra el extremo con palma arriba, curla la muñeca."),
            SeedExercise("Extensión de Muñeca con Banda", "antebrazos", "principiante", ("banda",),
                "Extensión de muñeca con resistencia de banda.",
                "Pisa la banda, agarra con palma abajo, extiende la muñeca hacia arriba."),
            SeedExercise("Towel Pull-Up", "antebrazos", "avanzado", ("barra_dominadas",),
                "Dominada con toalla para máxima demanda de agarre.",
                "Cuelga una toalla de la barra, agárrate de los extremos y haz dominadas."),
            SeedExercise("Pinch Grip con Discos", "antebrazos", "intermedio", ("disco",),
                "Agarre de pellizco para desarrollar la fuerza de los dedos.",
                "Pellizca un disco con cada mano y aguanta lo máximo posible."),
            SeedExercise("Rotación de Muñeca con Mancuerna", "antebrazos", "principiante", ("mancuernas",),
                "Pronación y supinación del antebrazo.",
                "Codo pegado, gira la mancuerna de palma abajo a palma arriba lentamente."),

            # ══════════════════════════════════════════════════
            # PANTORRILLAS (ampliar variedad)
            # ══════════════════════════════════════════════════
            SeedExercise("Elevación de Talones en Escalón", "pantorrillas", "principiante", ("peso_corporal",),
                "Mayor rango de movimiento al bajar el talón por debajo del escalón.",
                "Punta del pie en el borde, baja el talón al máximo y sube en puntas."),
            SeedExercise("Saltos en Puntas de Pie", "pantorrillas", "intermedio", ("peso_corporal",),
                "Trabajo explosivo de pantorrillas con saltos continuos.",
                "Salta con mínima flexión de rodilla, usando solo la extensión del tobillo."),
            SeedExercise("Elevación de Pantorrilla con Barra", "pantorrillas", "intermedio", ("barra",),
                "Carga la barra en los hombros para mayor sobrecarga.",
                "De pie, barra en trapecios, eleva talones lentamente hasta el máximo."),
            SeedExercise("Elevación de Pantorrilla con Kettlebell", "pantorrillas", "principiante", ("kettlebell",),
                "Versión con kettlebell para mayor rango.",
                "Sostén el kettlebell, eleva en puntas lentamente y baja controlado."),
            SeedExercise("Heel Walks", "pantorrillas", "principiante", ("peso_corporal",),
                "Caminata sobre los talones para activar tibial anterior.",
                "Camina sobre los talones manteniendo las puntas elevadas durante 20 metros."),
            SeedExercise("Elevación de Pantorrilla Isométrica", "pantorrillas", "principiante", ("peso_corporal",),
                "Contracción isométrica en el punto de mayor activación.",
                "Sube a las puntas y mantén la contracción 5-10 segundos, baja y repite."),

            # ══════════════════════════════════════════════════
            # PECHO adicional
            # ══════════════════════════════════════════════════
            SeedExercise("Flexiones con Palmada", "pecho", "avanzado", ("peso_corporal",),
                "Flexión explosiva pliométrica para potencia de pecho.",
                "Desciende controlado, empuja explosivo y palmea antes de caer."),
            SeedExercise("Press con Banda", "pecho", "principiante", ("banda", "banco"),
                "Press de pecho con resistencia de banda.",
                "Banda anclada atrás, empuja al frente como un press, controla el regreso."),
            SeedExercise("Fondos entre Sillas", "pecho", "principiante", ("peso_corporal",),
                "Versión de fondos sin paralelas.",
                "Manos en el borde de dos sillas estables, baja controlado e inclínate ligeramente."),
            SeedExercise("Press Arnold con Mancuernas", "pecho", "intermedio", ("mancuernas",),
                "Combinación de press y rotación de hombro que activa pecho y hombros.",
                "Desde palmas hacia ti, rota y empuja a la vez abriendo los codos."),
            SeedExercise("Flexiones Archer", "pecho", "avanzado", ("peso_corporal",),
                "Una mano trabaja más que la otra para preparar la flexión a un brazo.",
                "Baja hacia un lado flexionando un brazo mientras el otro permanece extendido."),

            # ══════════════════════════════════════════════════
            # ESPALDA adicional
            # ══════════════════════════════════════════════════
            SeedExercise("Remo Invertido con Barra", "espalda", "principiante", ("barra",),
                "Remo invertido usando una barra en rack — alternativa accesible a dominadas.",
                "Cuerpo recto bajo la barra, jala el pecho hacia ella manteniendo core firme."),
            SeedExercise("Pull-up Negativo", "espalda", "intermedio", ("barra_dominadas",),
                "Fase excéntrica de la dominada para ganar fuerza.",
                "Sube con ayuda, luego baja en 5-8 segundos manteniendo el control total."),
            SeedExercise("Remo con Kettlebell", "espalda", "principiante", ("kettlebell",),
                "Remo a una mano con kettlebell.",
                "Apoyado en banco o de pie inclinado, jala el kettlebell hacia la cadera."),
            SeedExercise("Hiperextensiones", "espalda", "principiante", ("peso_corporal",),
                "Extensión de espalda baja en banco romano o en el suelo.",
                "Baja el torso controlado y extiende hasta la posición neutra, no hiperextiendas."),
            SeedExercise("Remo con Disco", "espalda", "intermedio", ("disco",),
                "Igual que remo con barra pero con disco para mejor agarre neutral.",
                "Inclinado, sostén el disco con ambas manos, rema hacia el abdomen."),

            # ══════════════════════════════════════════════════
            # HOMBROS adicional
            # ══════════════════════════════════════════════════
            SeedExercise("Face Pull con Banda", "hombros", "principiante", ("banda",),
                "Trabaja deltoides posterior y rotadores externos.",
                "Banda anclada a la altura de la cara, jala hacia los ojos separando las manos."),
            SeedExercise("Press Arnold con Mancuernas", "hombros", "intermedio", ("mancuernas",),
                "Press rotacional que activa los tres haces del deltoides.",
                "Empieza con palmas hacia ti, gira y empuja hasta que palmas queden al frente en el tope."),
            SeedExercise("Elevaciones Laterales con Cables o Banda", "hombros", "principiante", ("banda",),
                "Aislamiento del deltoides medio con tensión constante.",
                "Banda pisada, eleva el brazo a 90° con codo ligeramente flexionado."),
            SeedExercise("Press Unilateral con Mancuerna", "hombros", "intermedio", ("mancuernas",),
                "Press de hombro a un brazo para trabajar cada lado de forma independiente.",
                "Sentado o de pie, presiona la mancuerna sobre la cabeza, baja controlado."),
            SeedExercise("Vuelos Invertidos con Mancuernas", "hombros", "principiante", ("mancuernas",),
                "Trabaja el deltoides posterior.",
                "Inclinado hacia adelante, abre los brazos como si volaras, controla la bajada."),

            # ══════════════════════════════════════════════════
            # BÍCEPS adicional
            # ══════════════════════════════════════════════════
            SeedExercise("Curl en Banco Predicador", "biceps", "intermedio", ("mancuernas", "barra", "banco"),
                "Aislamiento máximo del bíceps con apoyo del brazo.",
                "Apoya el tríceps en el banco predicador, curla hasta la contracción completa."),
            SeedExercise("Curl Concentrado", "biceps", "principiante", ("mancuernas",),
                "Máximo pico de bíceps con foco unilateral.",
                "Sentado, codo en el muslo, curla lentamente y aprieta en el tope."),
            SeedExercise("Curl 21s con Barra", "biceps", "intermedio", ("barra",),
                "Método de 7+7+7 reps para máxima tensión en todo el rango.",
                "7 reps medio rango inferior, 7 medio rango superior, 7 rango completo."),
            SeedExercise("Curl con Banda", "biceps", "principiante", ("banda",),
                "Curl de bíceps con banda elástica.",
                "Pisa la banda, agarra los extremos con palmas arriba, curla controlado."),
            SeedExercise("Chin-Ups", "biceps", "intermedio", ("barra_dominadas",),
                "Dominadas en supino que activan fuertemente el bíceps.",
                "Agarre supino (palmas hacia ti) a la anchura de los hombros, sube el pecho a la barra."),

            # ══════════════════════════════════════════════════
            # TRÍCEPS adicional
            # ══════════════════════════════════════════════════
            SeedExercise("Press Cerrado con Barra", "triceps", "intermedio", ("barra", "banco"),
                "Press de banca con agarre estrecho para enfatizar tríceps.",
                "Manos a anchura de hombros o menos, codos cerca del cuerpo al bajar."),
            SeedExercise("Extensión con Banda por Encima", "triceps", "principiante", ("banda",),
                "Trabaja la cabeza larga del tríceps.",
                "Banda anclada abajo, extiende los brazos por encima de la cabeza, controla."),
            SeedExercise("Fondos Estrecho entre Bancos", "triceps", "principiante", ("banco",),
                "Fondos de tríceps con pies elevados para mayor sobrecarga.",
                "Manos en un banco, pies en otro, baja doblando los codos y empuja."),
            SeedExercise("Extensión de Tríceps Acostado con Banda", "triceps", "principiante", ("banda",),
                "Skullcrusher sin peso libre.",
                "Acostado, banda anclada detrás, extiende los brazos desde el codo hacia arriba."),

            # ══════════════════════════════════════════════════
            # PIERNAS adicional
            # ══════════════════════════════════════════════════
            SeedExercise("Sentadilla con Salto", "piernas", "intermedio", ("peso_corporal",),
                "Potencia explosiva de piernas.",
                "Sentadilla estándar, en la subida salta explosivo, aterriza suave y repite."),
            SeedExercise("Prensa de Piernas (simulada con banda)", "piernas", "principiante", ("banda",),
                "Simula la prensa de pierna con banda elástica.",
                "Acostado, banda en los pies, empuja extendiendo piernas controlado."),
            SeedExercise("Curl Femoral de Pie con Banda", "piernas", "principiante", ("banda",),
                "Aislamiento de isquiotibiales de pie.",
                "Banda anclada al tobillo bajo, curla la pierna hacia el glúteo controlado."),
            SeedExercise("Sentadilla Goblet con Kettlebell", "piernas", "principiante", ("kettlebell",),
                "Sentadilla frontal con kettlebell, excelente para principiantes.",
                "Sostén el kettlebell al pecho, rodillas a 90°, espalda recta."),
            SeedExercise("Zancada Lateral", "piernas", "principiante", ("peso_corporal", "mancuernas"),
                "Trabaja aductores y glúteo medio.",
                "Paso lateral amplio, baja hacia el lado doblando esa rodilla, otro pie recto."),

            # ══════════════════════════════════════════════════
            # GLÚTEOS adicional
            # ══════════════════════════════════════════════════
            SeedExercise("Good Morning", "gluteos", "intermedio", ("barra",),
                "Bisagra de cadera con barra para glúteos e isquiotibiales.",
                "Barra en trapecios, inclina el torso hasta casi horizontal manteniendo espalda neutra."),
            SeedExercise("Patada de Glúteo con Banda", "gluteos", "principiante", ("banda",),
                "Kickback en cuadrupedia para aislamiento de glúteo.",
                "En cuadrupedia, banda en el tobillo, extiende la pierna hacia atrás contrayendo el glúteo."),
            SeedExercise("Sentadilla Búlgara con Barra", "gluteos", "avanzado", ("barra", "banco"),
                "Variante cargada de la sentadilla búlgara.",
                "Pie trasero en banco, barra en hombros, baja la rodilla trasera controlado."),
            SeedExercise("Cable Pull-Through (con banda)", "gluteos", "intermedio", ("banda",),
                "Bisagra de cadera con tensión constante del glúteo.",
                "Banda entre las piernas, inclina el torso y extiende las caderas explosivo."),

            # ══════════════════════════════════════════════════
            # ABDOMEN adicional
            # ══════════════════════════════════════════════════
            SeedExercise("Dragon Flag", "abdomen", "avanzado", ("banco",),
                "Uno de los ejercicios abdominales más difíciles.",
                "Acostado, agarra el banco sobre la cabeza, eleva el cuerpo como tabla y baja."),
            SeedExercise("Hollow Body Hold", "abdomen", "intermedio", ("peso_corporal",),
                "Posición de tensión total del core.",
                "Acostado, eleva piernas y hombros ligeramente, presiona la lumbar al suelo."),
            SeedExercise("Windshield Wipers", "abdomen", "avanzado", ("barra_dominadas",),
                "Rotación de piernas colgando para oblicuos.",
                "Cuelga de la barra, sube las piernas a 90° y oscílalas de lado a lado."),
            SeedExercise("Pallof Press de Rodillas", "abdomen", "principiante", ("banda",),
                "Anti-rotación de rodillas para activar el core profundo.",
                "De rodillas, banda al lado, lleva las manos al frente y resiste la tracción."),

            # ══════════════════════════════════════════════════
            # CORE adicional
            # ══════════════════════════════════════════════════
            SeedExercise("Bear Plank", "core", "principiante", ("peso_corporal",),
                "Plancha en cuadrupedia con rodillas a 5 cm del suelo.",
                "Columna neutra, core apretado, mantén las rodillas elevadas 30-60 s."),
            SeedExercise("Plancha con Toque de Hombro", "core", "intermedio", ("peso_corporal",),
                "Añade anti-rotación a la plancha estándar.",
                "En plancha alta, toca el hombro contrario alternando y evita rotar la cadera."),
            SeedExercise("Suitcase Carry", "core", "intermedio", ("mancuernas", "kettlebell"),
                "Caminata con un solo lado cargado para core lateral.",
                "Carga solo un lado, camina erguido sin inclinarte, activa oblicuos."),
            SeedExercise("Plank to Downward Dog", "core", "principiante", ("peso_corporal",),
                "Transición entre plancha y perro boca abajo para core y movilidad.",
                "Desde plancha, eleva la cadera al máximo formando una V invertida y vuelve."),

            # ══════════════════════════════════════════════════
            # CARDIO adicional
            # ══════════════════════════════════════════════════
            SeedExercise("Jump Rope (Cuerda de Saltar)", "cardio", "principiante", (),
                "Cardio clásico de alta eficacia.",
                "Mantén ritmo constante, aterriza suave, usa las muñecas para girar la cuerda."),
            SeedExercise("Escaladores de Montaña Lentos", "cardio", "principiante", ("peso_corporal",),
                "Versión controlada del mountain climber para principiantes.",
                "Lleva cada rodilla al pecho lentamente sin perder la posición de plancha."),
            SeedExercise("Kick Boxing en el Aire", "cardio", "principiante", ("peso_corporal",),
                "Combinaciones de puñetazos y patadas para cardio total.",
                "Alterna jab, cross, gancho y patada frontal. Mantén guardias y cadencia."),
            SeedExercise("Thrusters con Mancuernas", "cardio", "intermedio", ("mancuernas",),
                "Sentadilla + press overhead en un movimiento continuo.",
                "Baja en sentadilla, al subir empuja las mancuernas sobre la cabeza sin parar."),

            # ══════════════════════════════════════════════════
            # MOVILIDAD adicional
            # ══════════════════════════════════════════════════
            SeedExercise("Gato-Vaca (Cat-Cow)", "movilidad", "principiante", ("peso_corporal",),
                "Movilidad básica de columna en cuadrupedia.",
                "En cuadrupedia, alterna arquear y redondear la espalda respirando en cada movimiento."),
            SeedExercise("Apertura de Caderas en Mariposa", "movilidad", "principiante", ("peso_corporal",),
                "Estiramiento de aductores y apertura de cadera.",
                "Sentado, plantas de los pies juntas, presiona suavemente las rodillas al suelo."),
            SeedExercise("Estiramiento de Cuádriceps de Pie", "movilidad", "principiante", ("peso_corporal",),
                "Estiramiento básico del cuádriceps.",
                "De pie, dobla la rodilla, lleva el talón al glúteo y mantén 30 segundos."),
            SeedExercise("Stretching de Pectoral con Banda", "movilidad", "principiante", ("banda",),
                "Apertura torácica para contrarrestar la postura cerrada.",
                "Banda detrás, agarra y lleva los brazos atrás mientras abres el pecho."),
            SeedExercise("Rotaciones de Tobillo", "movilidad", "principiante", ("peso_corporal",),
                "Mejora la dorsiflexión de tobillo para sentadillas.",
                "Sentado o de pie, describe círculos grandes con el tobillo en ambas direcciones."),

            # ══════════════════════════════════════════════════
            # PECHO — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("Pike Push-Up", "pecho", "intermedio", ("peso_corporal",),
                "Transición entre flexión y press de hombros, activa pecho superior y deltoides.",
                "Caderas en alto formando una V invertida, dobla los codos bajando la cabeza al suelo."),
            SeedExercise("Svend Press", "pecho", "principiante", ("disco",),
                "Press de contracción isométrica sostenida de pectoral.",
                "Presiona dos discos entre las palmas, extiende los brazos al frente y regresa sin soltar."),
            SeedExercise("Press de Pecho con Kettlebell", "pecho", "principiante", ("kettlebell", "banco"),
                "Igual al press con mancuernas pero con kettlebell para mayor inestabilidad.",
                "Agarra el asa del kettlebell, press estándar controlando el equilibrio."),
            SeedExercise("Aperturas con Banda", "pecho", "principiante", ("banda",),
                "Aislamiento de pectoral con tensión constante de banda.",
                "Ancla bandas a los lados, desde brazos abiertos cruza las manos al centro."),
            SeedExercise("Flexiones Explosivas", "pecho", "avanzado", ("peso_corporal",),
                "Variante pliométrica de la flexión para potencia.",
                "Desciende controlado y empuja con máxima fuerza para despegar las manos del suelo."),
            SeedExercise("Dips de Pecho con Peso", "pecho", "avanzado", ("peso_corporal",),
                "Fondos en paralelas con peso adicional.",
                "Inclínate 30° al frente, baja hasta sentir el pecho estirado y empuja."),
            SeedExercise("Flexiones con Rodillas", "pecho", "principiante", ("peso_corporal",),
                "Variante más accesible de la flexión estándar.",
                "Rodillas en el suelo, cuerpo recto desde rodillas a hombros, baja controlado."),
            SeedExercise("Press de Pecho con Banda y Barra", "pecho", "intermedio", ("barra", "banda", "banco"),
                "Añade resistencia variable al press: más fuerza requerida en el tope.",
                "Ata bandas a los extremos de la barra y anclalas al banco, haz press normal."),
            SeedExercise("Flexiones en Pared", "pecho", "principiante", ("peso_corporal",),
                "Versión de menor dificultad para comenzar.",
                "De pie frente a la pared, coloca las manos a la altura del pecho y realiza la flexión."),
            SeedExercise("Squeeze Press con Mancuernas", "pecho", "principiante", ("mancuernas", "banco"),
                "Press con contracción isométrica: aprieta las mancuernas entre sí durante todo el rango.",
                "Mantén las mancuernas apretadas entre sí durante todo el press para mayor activación."),

            # ══════════════════════════════════════════════════
            # ESPALDA — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("T-Bar Row", "espalda", "intermedio", ("barra",),
                "Remo con barra en V para gran activación de espalda media.",
                "Un extremo de la barra fijo, carga el otro, inclínate y rema hacia el abdomen."),
            SeedExercise("Rack Pull", "espalda", "avanzado", ("barra", "disco"),
                "Peso muerto parcial desde el rack para trapecio y espalda alta.",
                "Barra en el rack a la altura de las rodillas, tira hasta extensión completa."),
            SeedExercise("Meadows Row", "espalda", "intermedio", ("barra",),
                "Remo unilateral con extremo de barra para máxima activación del dorsal.",
                "Coge el extremo de la barra de pie, inclínate y rema hacia la cadera, codo alto."),
            SeedExercise("Remo en Polea Baja con Banda", "espalda", "principiante", ("banda",),
                "Simula la polea baja con banda para espalda media.",
                "Siéntate, pisa la banda con ambos pies, jala los extremos hacia el abdomen."),
            SeedExercise("Straight Arm Pulldown con Banda", "espalda", "principiante", ("banda",),
                "Activa el dorsal sin involucrar el bíceps.",
                "Banda anclada en alto, brazos extendidos, presiona hacia abajo hasta las caderas."),
            SeedExercise("Remo con Agarre Neutro y Mancuernas", "espalda", "principiante", ("mancuernas", "banco"),
                "Remo bilateral apoyado en banco inclinado para mayor rango.",
                "Pecho en el banco inclinado, jala las mancuernas hacia las caderas con agarre neutro."),
            SeedExercise("Reverse Snow Angels", "espalda", "principiante", ("peso_corporal",),
                "Movilidad y fuerza de retractores escapulares.",
                "Boca abajo, brazos al lado, deslízalos hacia arriba sobre la cabeza y de vuelta."),
            SeedExercise("Seal Row", "espalda", "intermedio", ("barra", "mancuernas"),
                "Remo tumbado boca abajo en banco elevado para eliminar el impulso.",
                "Banco elevado, tumbado boca abajo, rema sin usar la inercia del cuerpo."),
            SeedExercise("Dominadas con Peso", "espalda", "avanzado", ("barra_dominadas",),
                "Dominadas con peso adicional colgado del cinturón.",
                "Sube igual que la dominada estándar pero con más carga externa para mayor fuerza."),
            SeedExercise("Katana Row", "espalda", "intermedio", ("mancuernas", "banco"),
                "Remo con giro de muñeca para mayor activación del dorsal.",
                "Inicia con palma hacia atrás, al subir gira hasta palma hacia ti, codo pegado."),
            SeedExercise("Shrug con Mancuernas", "espalda", "principiante", ("mancuernas",),
                "Encogimiento de hombros con mancuernas para el trapecio.",
                "De pie, encoge los hombros hacia las orejas, pausa 1 segundo y baja lento."),

            # ══════════════════════════════════════════════════
            # HOMBROS — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("Push Press", "hombros", "intermedio", ("barra",),
                "Press overhead con impulso de piernas para mayor carga.",
                "Flexión parcial de rodillas, extiéndelas explosivo y empuja la barra sobre la cabeza."),
            SeedExercise("Band Pull-Apart", "hombros", "principiante", ("banda",),
                "Activa retractores escapulares y deltoides posterior.",
                "Sostén la banda con brazos extendidos al frente, jala hasta el pecho separando las manos."),
            SeedExercise("Handstand Push-Up (Asistido)", "hombros", "avanzado", ("peso_corporal",),
                "Press de hombros con peso corporal en posición invertida.",
                "Contra la pared, baja la cabeza al suelo y empuja. Usa banda de asistencia si es necesario."),
            SeedExercise("Cuban Press", "hombros", "principiante", ("mancuernas", "barra"),
                "Trabaja manguito rotador y deltoides en un solo movimiento.",
                "Remo alto, luego rota los codos hacia arriba y finaliza en press overhead."),
            SeedExercise("Scaption", "hombros", "principiante", ("mancuernas",),
                "Elevación en el plano escapular a 30-45° para mayor salud del hombro.",
                "Eleva las mancuernas en diagonal entre la elevación frontal y lateral, pulgares arriba."),
            SeedExercise("Elevación Frontal Alternada", "hombros", "principiante", ("mancuernas",),
                "Trabaja el deltoides anterior de forma alternada.",
                "Sube un brazo mientras el otro baja, controla la bajada y evita el balanceo."),
            SeedExercise("Press de Hombros Sentado con Barra", "hombros", "intermedio", ("barra", "banco"),
                "Press overhead sentado para mayor estabilidad y control.",
                "Barra a la altura de los hombros, empuja verticalmente sin arquear la espalda."),
            SeedExercise("Rear Delt con Banda", "hombros", "principiante", ("banda",),
                "Aislamiento del deltoides posterior con banda.",
                "Banda anclada al frente, jala hacia afuera y atrás, codos a 90°."),
            SeedExercise("L-Lateral Raise", "hombros", "intermedio", ("mancuernas",),
                "Elevación lateral con el codo a 90° para mayor tensión en el deltoides.",
                "Dobla el codo a 90°, sube hasta la altura del hombro, codo ligeramente arriba de la muñeca."),
            SeedExercise("Encogimientos con Mancuernas", "hombros", "principiante", ("mancuernas",),
                "Fortalece el trapecio superior con mancuernas.",
                "De pie, encoge los hombros hacia las orejas, pausa y baja sin girar."),

            # ══════════════════════════════════════════════════
            # BÍCEPS — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("Spider Curl", "biceps", "intermedio", ("barra", "mancuernas", "banco"),
                "Mayor tensión en el pico del bíceps.",
                "Tumbado boca abajo en banco inclinado, cuelga los brazos y curla sin impulso."),
            SeedExercise("Zottman Curl", "biceps", "intermedio", ("mancuernas",),
                "Curl que trabaja bíceps en la subida y antebrazos en la bajada.",
                "Sube con palmas arriba, en la parte alta gira a palmas abajo y baja."),
            SeedExercise("Cross Body Curl", "biceps", "principiante", ("mancuernas",),
                "Curl cruzado hacia el pecho contrario, enfoca el braquial.",
                "Sube la mancuerna cruzando hacia el pecho contrario con agarre neutro."),
            SeedExercise("Barbell Drag Curl", "biceps", "intermedio", ("barra",),
                "El codo va hacia atrás durante el curl para mayor activación del bíceps.",
                "Arrastra la barra por el cuerpo llevando los codos atrás, sin separar la barra del torso."),
            SeedExercise("Curl con Disco", "biceps", "principiante", ("disco",),
                "Curl de bíceps con disco para agarre y fuerza de dedos.",
                "Sujeta el disco por el borde, curla de forma normal, controla la bajada."),
            SeedExercise("Curl en Cable con Banda", "biceps", "principiante", ("banda",),
                "Curl con tensión constante durante todo el rango de movimiento.",
                "Pisa la banda, agarra con palmas arriba, curla controlando subida y bajada."),
            SeedExercise("Bayesian Curl con Banda", "biceps", "intermedio", ("banda",),
                "El hombro extendido hacia atrás permite mayor estiramiento y activación.",
                "Banda anclada detrás, da un paso al frente, curla con el hombro ligeramente detrás del torso."),
            SeedExercise("Reverse Curl con Barra EZ", "biceps", "intermedio", ("barra",),
                "Curl inverso con barra EZ para braquiorradial y antebrazos.",
                "Agarre prono en la barra EZ, sube sin levantar los codos, baja controlado."),

            # ══════════════════════════════════════════════════
            # TRÍCEPS — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("JM Press", "triceps", "avanzado", ("barra", "banco"),
                "Híbrido entre press cerrado y skull crusher para tríceps.",
                "Barra baja hasta la garganta doblando los codos como en skull crusher, luego empuja."),
            SeedExercise("Tate Press", "triceps", "intermedio", ("mancuernas", "banco"),
                "Aislamiento de la cabeza lateral del tríceps acostado.",
                "Acostado, mancuernas apuntan al techo, dobla los codos hacia afuera y extiende."),
            SeedExercise("Pushdown con Agarre Supino", "triceps", "principiante", ("banda",),
                "Pushdown con palmas hacia arriba para mayor activación de la cabeza larga.",
                "Banda anclada en alto, agarra con palmas arriba, extiende hacia abajo."),
            SeedExercise("Triceps Kickback Bilateral", "triceps", "principiante", ("mancuernas",),
                "Kickback con ambos brazos simultáneamente inclinado.",
                "Inclinado, codos pegados al cuerpo, extiende ambos brazos atrás y controla."),
            SeedExercise("Extensión Overhead con Mancuerna Doble", "triceps", "principiante", ("mancuernas",),
                "Extensión sobre la cabeza con ambas manos en una sola mancuerna.",
                "Sostén la mancuerna con ambas manos, codos cerca de la cabeza, extiende y baja."),
            SeedExercise("Flexiones Pike para Tríceps", "triceps", "intermedio", ("peso_corporal",),
                "Variante de pike push-up con mayor énfasis en tríceps.",
                "Caderas en alto, codos hacia afuera al doblar, extiende empujando con tríceps."),
            SeedExercise("Triceps Dip con Banda de Asistencia", "triceps", "principiante", ("banda",),
                "Fondos asistidos con banda para principiantes.",
                "Banda en el rack apoya las rodillas o los pies. Baja y sube de forma controlada."),

            # ══════════════════════════════════════════════════
            # PIERNAS — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("Zercher Squat", "piernas", "avanzado", ("barra",),
                "Sentadilla con la barra cargada en el interior de los codos.",
                "Barra en pliegue del codo, pies a anchura de hombros, baja profundo y sube."),
            SeedExercise("Hack Squat con Barra", "piernas", "avanzado", ("barra",),
                "Sentadilla con barra detrás de las piernas para enfatizar cuádriceps.",
                "Barra en el suelo detrás, toma el peso y levanta como un peso muerto invertido."),
            SeedExercise("Nordic Curl", "piernas", "avanzado", ("peso_corporal",),
                "El mejor ejercicio para los isquiotibiales excéntrico.",
                "Pies fijos (banco o pareja), baja el cuerpo lentamente resistiendo con los isquiotibiales."),
            SeedExercise("Sissy Squat", "piernas", "avanzado", ("peso_corporal",),
                "Aislamiento extremo de cuádriceps.",
                "Agárrate a algo, inclínate hacia atrás elevando los talones y dobla las rodillas."),
            SeedExercise("Box Squat", "piernas", "intermedio", ("barra", "banco"),
                "Sentadilla con pausa en la caja para técnica y fuerza.",
                "Siéntate sobre la caja completamente, pausa 1 segundo y levanta explosivo."),
            SeedExercise("Leg Extension con Banda", "piernas", "principiante", ("banda",),
                "Aislamiento de cuádriceps con banda.",
                "Sentado, banda anclada al tobillo por debajo, extiende la pierna completamente."),
            SeedExercise("Hamstring Curl con Banda", "piernas", "principiante", ("banda",),
                "Curla isquiotibial de pie con banda.",
                "Banda al tobillo anclada abajo, curla el talón hacia el glúteo y baja lento."),
            SeedExercise("Cossack Squat", "piernas", "intermedio", ("peso_corporal",),
                "Sentadilla lateral con máxima movilidad de cadera.",
                "Pies muy abiertos, baja hacia un lado doblando esa rodilla, otro pie plano o en punta."),
            SeedExercise("Reverse Lunge", "piernas", "principiante", ("peso_corporal", "mancuernas"),
                "Zancada hacia atrás, más amigable con las rodillas que la zancada frontal.",
                "Da el paso hacia atrás, baja la rodilla trasera al suelo y vuelve a la posición inicial."),
            SeedExercise("Sentadilla Pausa", "piernas", "intermedio", ("barra", "peso_corporal"),
                "Sentadilla con pausa de 2-3 segundos en el fondo para eliminar el rebote.",
                "Baja a profundidad, pausa completo, luego sube explosivo. Desarrolla fuerza real."),
            SeedExercise("Lunge con Kettelbell", "piernas", "principiante", ("kettlebell",),
                "Zancada frontal con kettlebell para mayor dificultad.",
                "Sostén el kettlebell en rack o al lado, da un paso adelante y baja la rodilla."),
            SeedExercise("Single Leg Romanian Deadlift con Banda", "piernas", "principiante", ("banda",),
                "Peso muerto unilateral con banda para equilibrio y cadena posterior.",
                "Pisa la banda con un pie, inclínate hacia adelante con la otra pierna elevada."),

            # ══════════════════════════════════════════════════
            # GLÚTEOS — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("Frog Pump", "gluteos", "principiante", ("peso_corporal",),
                "Activación de glúteos con caderas en rotación externa.",
                "Acostado, plantas de los pies juntas, empuja las caderas hacia arriba apretando glúteos."),
            SeedExercise("Glute Bridge Unilateral", "gluteos", "principiante", ("peso_corporal",),
                "Puente de glúteo a una pierna para mayor dificultad e intensidad.",
                "Una pierna en el aire, empuja con el talón del pie de apoyo, aprieta el glúteo arriba."),
            SeedExercise("Fire Hydrant", "gluteos", "principiante", ("banda",),
                "Abducción de cadera en cuadrupedia.",
                "En cuadrupedia, eleva una rodilla al lado (como un perro) sin rotar el torso."),
            SeedExercise("Donkey Kick", "gluteos", "principiante", ("banda",),
                "Extensión de cadera en cuadrupedia.",
                "En cuadrupedia, extiende una pierna hacia arriba y atrás, contrae el glúteo en el tope."),
            SeedExercise("Reverse Lunge con Rodilla al Pecho", "gluteos", "intermedio", ("peso_corporal",),
                "Combina zancada trasera con elevación de rodilla para glúteo y equilibrio.",
                "Da el paso atrás, baja la rodilla y al subir lleva la rodilla delantera al pecho."),
            SeedExercise("Cable Kickback con Banda", "gluteos", "principiante", ("banda",),
                "Extensión de cadera de pie con resistencia.",
                "Banda al tobillo anclada abajo, de pie extiende la pierna hacia atrás, contrae glúteo."),
            SeedExercise("Side Step con Banda", "gluteos", "principiante", ("banda",),
                "Desplazamiento lateral con banda para glúteo medio.",
                "Banda en tobillos o rodillas, baja ligeramente y da pasos laterales manteniendo tensión."),
            SeedExercise("Hip Thrust a 45 Grados con Banda", "gluteos", "principiante", ("banda",),
                "Hip thrust en ángulo para mayor activación del glúteo mayor.",
                "Espalda en una superficie inclinada, banda sobre las caderas, empuja al máximo."),
            SeedExercise("Puente con Pies Elevados", "gluteos", "intermedio", ("peso_corporal", "banco"),
                "Mayor rango de movimiento de la cadera que el puente estándar.",
                "Talones en el banco, empuja caderas hacia el techo apretando glúteos."),

            # ══════════════════════════════════════════════════
            # ABDOMEN — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("Flutter Kicks", "abdomen", "principiante", ("peso_corporal",),
                "Activación del abdomen inferior con piernas en movimiento alternado.",
                "Acostado, piernas a 15 cm del suelo, alterna pequeñas patadas sin tocar el piso."),
            SeedExercise("Scissor Kicks", "abdomen", "principiante", ("peso_corporal",),
                "Cruces de piernas elevadas para abdomen inferior.",
                "Piernas a 45°, cruza una sobre la otra alternando sin bajarlas al suelo."),
            SeedExercise("Reverse Crunch", "abdomen", "principiante", ("peso_corporal",),
                "Crunch que eleva la cadera en lugar del torso, enfoca el abdomen inferior.",
                "Piernas a 90°, eleva la cadera del suelo hacia el pecho y baja controlado."),
            SeedExercise("Toe Touch Crunch", "abdomen", "principiante", ("peso_corporal",),
                "Crunch con piernas verticales para mayor rango de contracción.",
                "Piernas verticales, sube intentando tocar los pies con las manos."),
            SeedExercise("Lateral Crunch", "abdomen", "principiante", ("peso_corporal",),
                "Crunch lateral para los oblicuos.",
                "Acostado de lado, eleva el hombro superior hacia la cadera, baja y repite."),
            SeedExercise("Decline Crunch", "abdomen", "intermedio", ("banco",),
                "Crunch en banco declinado para mayor rango y resistencia.",
                "Pies fijos en banco declinado, sube el torso controlado y baja sin tocar el banco."),
            SeedExercise("Crunch con Rotación", "abdomen", "principiante", ("peso_corporal",),
                "Crunch + giro para activar oblicuos.",
                "Al subir, lleva el codo hacia la rodilla contraria, alterna cada repetición."),
            SeedExercise("Crunch con Disco", "abdomen", "intermedio", ("disco",),
                "Crunch con carga adicional de un disco para mayor dificultad.",
                "Sostén el disco en el pecho o detrás de la cabeza, sube controlado y baja."),
            SeedExercise("Plank Knee to Elbow", "abdomen", "intermedio", ("peso_corporal",),
                "Desde plancha alta, lleva la rodilla al codo del mismo lado.",
                "Plancha alta, lleva cada rodilla al codo ipsilateral alternado, sin perder la línea."),

            # ══════════════════════════════════════════════════
            # CORE — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("Turkish Get-Up", "core", "avanzado", ("kettlebell", "mancuernas"),
                "Movimiento completo de suelo a de pie con peso sobre la cabeza.",
                "Paso por paso: acostado → apoyado → rodilla → de pie. Brazo con peso siempre extendido."),
            SeedExercise("Landmine Anti-Rotation", "core", "intermedio", ("barra",),
                "Resistencia a la rotación del torso con barra en landmine.",
                "Sostén el extremo de la barra, lleva de lado a lado sin girar el torso."),
            SeedExercise("Copenhagen Plank", "core", "avanzado", ("banco",),
                "Plancha lateral con pie apoyado en banco para mayor dificultad.",
                "Pie superior en el banco, cuerpo en tabla, mantén la posición."),
            SeedExercise("Stir the Pot", "core", "avanzado", ("peso_corporal",),
                "Plancha en pelota realizando círculos con los codos.",
                "Codos en la pelota de ejercicios, haz círculos sin mover la cadera."),
            SeedExercise("Windmill con Kettlebell", "core", "avanzado", ("kettlebell",),
                "Fortalece el core lateral, hombros y cadera con carga overhead.",
                "Kettlebell sobre la cabeza, inclínate al lado contrario mirando el peso."),
            SeedExercise("Ab Wheel Rollout desde Rodillas", "core", "intermedio", ("peso_corporal",),
                "Rollout de rueda abdominal desde rodillas para mayor control.",
                "Desde rodillas, rueda al frente controlando la lumbar y vuelve con el core."),
            SeedExercise("Hollow Body Rock", "core", "intermedio", ("peso_corporal",),
                "Variante dinámica del hollow body hold.",
                "Posición hollow, mécete hacia adelante y hacia atrás manteniendo la forma."),
            SeedExercise("Plank Tap Anterior", "core", "principiante", ("peso_corporal",),
                "Desde plancha alta, alterna tocarte los hombros para activar anti-rotación.",
                "Pies un poco más abiertos, lleva la mano al hombro contrario sin rotar la cadera."),
            SeedExercise("Single Arm Farmer's Carry", "core", "intermedio", ("mancuernas", "kettlebell"),
                "Caminata con un solo lado cargado. Máxima demanda de core lateral.",
                "Un peso a un lado, camina erguido resistiendo la inclinación, activa el oblicuo."),

            # ══════════════════════════════════════════════════
            # PANTORRILLAS — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("Tibial Raise", "pantorrillas", "principiante", ("peso_corporal",),
                "Fortalece el tibial anterior, músculo de la espinilla.",
                "Espalda contra la pared, pies al frente, eleva las puntas sin mover los talones."),
            SeedExercise("Donkey Calf Raise", "pantorrillas", "intermedio", ("peso_corporal",),
                "Elevación de pantorrillas con peso sobre la espalda baja.",
                "Inclinado apoyado, pareja sentada en la espalda baja, realiza las elevaciones con rango completo."),
            SeedExercise("Calf Raise en Prensa", "pantorrillas", "intermedio", ("disco",),
                "Elevación de pantorrilla en posición inclinada con peso.",
                "En posición de prensa, empuja la plataforma solo con las puntas de los pies."),
            SeedExercise("Saltitos en Punta de Pie", "pantorrillas", "principiante", ("peso_corporal",),
                "Trabajo explosivo de pantorrillas de bajo impacto.",
                "Pequeños saltos continuos usando solo la extensión del tobillo, rodillas casi extendidas."),
            SeedExercise("Elevación de Pantorrilla con Pausa", "pantorrillas", "principiante", ("peso_corporal",),
                "Añade 3 segundos de pausa en el punto más alto para mayor tensión muscular.",
                "Sube a las puntas, mantén 3 segundos, baja controlado y repite."),
            SeedExercise("Seated Calf Raise con Disco", "pantorrillas", "principiante", ("disco",),
                "Énfasis en el músculo sóleo con rodillas a 90°.",
                "Sentado, disco sobre las rodillas, eleva los talones y baja con rango completo."),

            # ══════════════════════════════════════════════════
            # ANTEBRAZOS — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("Wrist Roller", "antebrazos", "intermedio", ("peso_corporal",),
                "Dispositivo de enrollado para fuerza total del antebrazo.",
                "Sostén el rodillo con brazos extendidos al frente, enrolla y desenrolla el peso."),
            SeedExercise("Barbell Finger Rollup", "antebrazos", "intermedio", ("barra",),
                "Deja rodar la barra hasta los dedos y recúpera con solo los dedos.",
                "Sentado, barra en palmas, deja caer hasta los dedos y vuelve a apretar."),
            SeedExercise("Plate Pinch", "antebrazos", "intermedio", ("disco",),
                "Pellizca platos con los dedos para fuerza de agarre.",
                "Sostén dos platos juntos por la cara lisa con solo el pulgar y los dedos el máximo tiempo."),
            SeedExercise("Rope Climb (simulado con toalla)", "antebrazos", "avanzado", ("barra_dominadas",),
                "Escalada de cuerda simulada con toalla en dominaderas.",
                "Cuelga dos toallas de la barra, agárrate y haz dominadas sin usar los pulgares."),
            SeedExercise("Extensión de Muñeca en Pared", "antebrazos", "principiante", ("peso_corporal",),
                "Estiramiento activo de los extensores del antebrazo.",
                "Palma apoyada en la pared con dedos hacia abajo, presiona suavemente y mantén 30 s."),
            SeedExercise("Grip Crush con Mancuerna", "antebrazos", "principiante", ("mancuernas",),
                "Aprieta y suelta la mancuerna repetidamente para resistencia de agarre.",
                "Sostén la mancuerna por el extremo y aprieta el agarre 20 veces, 3 series por mano."),

            # ══════════════════════════════════════════════════
            # CARDIO — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("High Knees", "cardio", "principiante", ("peso_corporal",),
                "Carrera elevando las rodillas al máximo.",
                "Levanta cada rodilla por encima de la cadera alternando, mantén el core firme."),
            SeedExercise("Lateral Shuffles", "cardio", "principiante", ("peso_corporal",),
                "Desplazamiento lateral a baja postura para cardio y agilidad.",
                "Semiarrodillado, desplázate de lado a lado tocando el suelo con la mano."),
            SeedExercise("Jump Lunge", "cardio", "intermedio", ("peso_corporal",),
                "Zancada explosiva con salto para cardio y piernas.",
                "En posición de zancada, salta y cambia las piernas en el aire, aterriza suave."),
            SeedExercise("Inchworm", "cardio", "principiante", ("peso_corporal",),
                "Calentamiento y cardio suave que activa el cuerpo entero.",
                "De pie, dobla e inclinase hasta las manos, camina con ellas hasta plancha y vuelve."),
            SeedExercise("Speed Skaters", "cardio", "intermedio", ("peso_corporal",),
                "Salto lateral imitando el movimiento del patinador.",
                "Salta de un pie al otro, llevando el pie de apoyo detrás en un arco, toca el suelo."),
            SeedExercise("Saltar la Soga Doble Bajo (Doble Under)", "cardio", "avanzado", (),
                "La cuerda pasa dos veces por cada salto.",
                "Salto alto con muñecas girando rápido, apunta a que la cuerda pase dos veces."),
            SeedExercise("Sprints de 20 metros", "cardio", "intermedio", ("peso_corporal",),
                "Sprint de corta distancia para potencia anaeróbica.",
                "Acelera al máximo los primeros 5 metros, mantén la velocidad hasta la meta."),
            SeedExercise("Sled Push (simulado con saco)", "cardio", "avanzado", ("peso_corporal",),
                "Empuje de trineo para potencia y cardio de alta intensidad.",
                "Con un saco pesado o compañero, empuja desde atrás en posición de sprint."),
            SeedExercise("Salto a Cajón de Silla", "cardio", "intermedio", ("peso_corporal",),
                "Salto vertical a una silla o superficie elevada segura.",
                "Piernas a la anchura de los hombros, salto de dos pies, aterriza suave y baja."),
            SeedExercise("Tabata Squat", "cardio", "intermedio", ("peso_corporal",),
                "Sentadillas a máxima intensidad en intervalos de 20s trabajo / 10s descanso.",
                "8 rondas: 20 s de sentadillas explosivas + 10 s de descanso = 4 minutos totales."),

            # ══════════════════════════════════════════════════
            # MOVILIDAD — nuevos ejercicios
            # ══════════════════════════════════════════════════
            SeedExercise("Pigeon Pose", "movilidad", "principiante", ("peso_corporal",),
                "Estiramiento profundo de piriforme y rotadores externos de cadera.",
                "Una pierna cruzada al frente en el suelo, otra extendida atrás, inclínate al frente."),
            SeedExercise("Downward Dog", "movilidad", "principiante", ("peso_corporal",),
                "Estiramiento de isquiotibiales, pantorrillas y apertura de hombros.",
                "Posición de V invertida, empuja los talones al suelo y abre la espalda torácica."),
            SeedExercise("Thoracic Bridge", "movilidad", "intermedio", ("peso_corporal",),
                "Movilidad torácica y apertura de cadera en extensión.",
                "Sentado, manos detrás, eleva las caderas y extiende la columna torácica."),
            SeedExercise("Scorpion Stretch", "movilidad", "principiante", ("peso_corporal",),
                "Estiramiento de cuádriceps y rotación de cadera boca abajo.",
                "Boca abajo, lleva un pie hacia la nalga contraria girando la cadera, alternado."),
            SeedExercise("Thread the Needle", "movilidad", "principiante", ("peso_corporal",),
                "Rotación torácica en cuadrupedia.",
                "Pasa un brazo por debajo del cuerpo hasta que el hombro toque el suelo, rota."),
            SeedExercise("Seated Forward Fold", "movilidad", "principiante", ("peso_corporal",),
                "Estiramiento de isquiotibiales y espalda baja.",
                "Sentado con piernas extendidas, inclínate al frente sin doblar las rodillas."),
            SeedExercise("Wall Ankle Mobilization", "movilidad", "principiante", ("peso_corporal",),
                "Mejora la dorsiflexión de tobillo imprescindible para sentadillas.",
                "Pie a 10 cm de la pared, dobla la rodilla hacia la pared sin levantar el talón."),
            SeedExercise("3D Hip Flexor Stretch", "movilidad", "principiante", ("peso_corporal",),
                "Trabaja el psoas en tres planos de movimiento.",
                "Posición caballero, adelanta la cadera, luego inclínate lateral y luego rota."),
            SeedExercise("Shoulder Circles", "movilidad", "principiante", ("peso_corporal",),
                "Calentamiento de la articulación del hombro con círculos amplios.",
                "Brazos extendidos, traza círculos grandes hacia adelante y hacia atrás."),
            SeedExercise("Neck Rolls", "movilidad", "principiante", ("peso_corporal",),
                "Movilidad cervical suave para liberar tensión.",
                "Cabeza caída al lado, rueda lentamente por el pecho al otro lado. Evita la extensión hacia atrás."),
            SeedExercise("Standing Hamstring Stretch", "movilidad", "principiante", ("peso_corporal",),
                "Estiramiento de pie de isquiotibiales.",
                "De pie, un pie elevado en superficie, inclínate con espalda recta hasta sentir el estiramiento."),
        ]

        created = 0
        updated = 0

        for seed in seeds:
            grupo = GrupoMuscular.objects.filter(slug=seed.grupo_slug).first()
            if not grupo:
                # fallback defensivo (por si cambian slugs)
                grupo = GrupoMuscular.objects.create(
                    nombre=seed.grupo_slug.replace("_", " ").title(),
                    slug=slugify(seed.grupo_slug),
                )

            ejercicio, was_created = Ejercicio.objects.get_or_create(
                nombre=seed.nombre,
                defaults={
                    "grupo_muscular": grupo,
                    "nivel": seed.nivel,
                    "descripcion": seed.descripcion,
                    "instrucciones": seed.instrucciones,
                    "duracion_minutos": seed.duracion_minutos,
                },
            )

            # Si ya existía, actualizamos campos básicos (sin pisar si el usuario editó)
            if not was_created:
                changed = False
                if ejercicio.grupo_muscular_id is None and grupo is not None:
                    ejercicio.grupo_muscular = grupo
                    changed = True
                if ejercicio.nivel != seed.nivel:
                    ejercicio.nivel = seed.nivel
                    changed = True
                if not ejercicio.descripcion and seed.descripcion:
                    ejercicio.descripcion = seed.descripcion
                    changed = True
                if not ejercicio.instrucciones and seed.instrucciones:
                    ejercicio.instrucciones = seed.instrucciones
                    changed = True
                if seed.duracion_minutos is not None and ejercicio.duracion_minutos != seed.duracion_minutos:
                    ejercicio.duracion_minutos = seed.duracion_minutos
                    changed = True
                if changed:
                    ejercicio.save(update_fields=["grupo_muscular", "nivel", "descripcion", "instrucciones", "duracion_minutos"])
                    updated += 1
            else:
                created += 1

            if seed.equipos:
                equipos = list(Equipo.objects.filter(nombre__in=seed.equipos))
                if equipos:
                    ejercicio.equipos.add(*equipos)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed completado. Ejercicios creados: {created}. Ejercicios actualizados: {updated}."
            )
        )

