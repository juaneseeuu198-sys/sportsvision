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
                if changed:
                    ejercicio.save(update_fields=["grupo_muscular", "nivel", "descripcion", "instrucciones"])
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

