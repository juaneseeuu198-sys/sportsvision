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
    musculos_secundarios: str = ""
    musculos_antagonistas: str = ""
    errores_comunes: str = ""
    variantes: str = ""
    comentarios: str = ""


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
            # ══════════════════════════════════════════════════
            # PECHO
            # ══════════════════════════════════════════════════
            SeedExercise(
                "Press de Banca con Barra",
                "pecho",
                "intermedio",
                ("barra", "banco"),
                "El ejercicio rey para el desarrollo de fuerza e hipertrofia del pectoral. Activa toda la superficie del pecho con énfasis en la porción esternal.",
                "1. Túmbate en el banco con los pies apoyados en el suelo.\n2. Agarra la barra con las manos a una anchura ligeramente mayor que los hombros.\n3. Retrae y deprime las escápulas, arquea ligeramente la zona lumbar.\n4. Desancla la barra y bájala de forma controlada hasta rozar la parte inferior del pecho.\n5. Empuja la barra hacia arriba y ligeramente hacia atrás hasta la extensión completa.",
                musculos_secundarios="Deltoides anterior, Tríceps braquial, Serrato anterior",
                musculos_antagonistas="Bíceps braquial, Dorsales, Romboides",
                errores_comunes="Arquear excesivamente la espalda levantando las caderas.\nNo retraer las escápulas, lo que pone en peligro el hombro.\nBajar la barra al cuello en lugar del pecho inferior.\nRebotar la barra en el pecho.",
                variantes="Press inclinado (pecho superior), Press declinado (pecho inferior), Press con mancuernas, Press cerrado (mayor énfasis en tríceps)",
                comentarios="La posición de los pies y la retracción escapular son la base de un press seguro. Una ligera inclinación del banco hacia arriba (15-20°) traslada el trabajo al pectoral mayor superior.",
            ),
            SeedExercise(
                "Press inclinado con mancuernas",
                "pecho",
                "intermedio",
                ("mancuernas", "banco"),
                "Enfatiza la porción clavicular (superior) del pectoral mayor. El uso de mancuernas permite un mayor rango de movimiento y corrección de desbalances.",
                "1. Ajusta el banco a 30-45°. Ángulos mayores transfieren el trabajo al deltoides anterior.\n2. Siéntate con las mancuernas en los muslos y tumba hacia atrás.\n3. Lleva las mancuernas al pecho con codos a 45° respecto al tronco.\n4. Empuja hacia arriba y ligeramente al interior sin chocar las mancuernas.\n5. Baja controlado hasta que los codos queden a la altura del banco.",
                musculos_secundarios="Deltoides anterior, Tríceps, Serrato anterior",
                musculos_antagonistas="Dorsales, Bíceps",
                errores_comunes="Usar un ángulo superior a 45°, lo que convierte el ejercicio en un press de hombros.\nChocar las mancuernas en la parte alta, reduciendo la tensión muscular.\nBajar demasiado rápido perdiendo el control.",
                variantes="Press inclinado con barra, Press plano con mancuernas, Aperturas inclinadas",
                comentarios="El ángulo de 30° es más efectivo para el pectoral superior que el de 45° y genera menos estrés en el hombro. Controla especialmente la fase excéntrica (bajada).",
            ),
            SeedExercise(
                "Flexiones (Push-ups)",
                "pecho",
                "principiante",
                ("peso_corporal",),
                "Ejercicio de empuje con el peso corporal que desarrolla el pectoral, tríceps y deltoides anterior. Ideal para principiantes y para entrenar en casa.",
                "1. Colócate boca abajo apoyando las manos a la anchura de los hombros.\n2. Extiende las piernas y apoya las puntas de los pies.\n3. El cuerpo debe formar una línea recta desde la cabeza hasta los talones.\n4. Activa el core y los glúteos para mantener la posición.\n5. Dobla los codos bajando el pecho hasta casi tocar el suelo.\n6. Empuja hacia arriba hasta la extensión completa.",
                musculos_secundarios="Deltoides anterior, Tríceps braquial, Serrato anterior, Core",
                musculos_antagonistas="Dorsales, Bíceps",
                errores_comunes="Hundir las caderas o elevarlas, perdiendo la línea corporal.\nColocar las manos demasiado adelantadas respecto a los hombros.\nNo descender lo suficiente, reduciendo el rango de movimiento.\nLlanar la barbilla al suelo en lugar del pecho.",
                variantes="Flexiones inclinadas (pies elevados, mayor énfasis pecho superior), Flexiones declinadas (manos elevadas, más fácil), Flexiones diamante (tríceps), Flexiones con palmada (potencia)",
                comentarios="Las flexiones con pies elevados trabajan principalmente el pecho superior y los hombros. Para mayor activación pectoral, separa ligeramente más los codos. Son el primer ejercicio de empuje a dominar.",
            ),
            SeedExercise(
                "Press con Mancuernas",
                "pecho",
                "principiante",
                ("banco", "mancuernas"),
                "Variante del press de banca que permite mayor rango de movimiento y trabaja cada lado de forma independiente, corrigiendo desbalances.",
                "1. Túmbate en el banco plano con una mancuerna en cada mano.\n2. Sube las mancuernas hasta los hombros con los codos a 45°.\n3. Empuja hacia arriba llevando las mancuernas hacia el centro sin que se toquen.\n4. Baja de forma controlada hasta que los codos queden a la altura del banco o ligeramente por debajo.",
                musculos_secundarios="Deltoides anterior, Tríceps",
                musculos_antagonistas="Bíceps, Dorsales",
                errores_comunes="Dejar caer las mancuernas sin control en la fase excéntrica.\nGirar las muñecas durante el movimiento.\nNo mantener los pies apoyados en el suelo.",
                variantes="Press inclinado, Press declinado, Aperturas con mancuernas, Press neutro (agarre paralelo)",
                comentarios="El agarre neutro (pulgares hacia arriba) es más amigable para el hombro que el agarre prono. Empieza con este si tienes molestias en la articulación.",
            ),
            SeedExercise(
                "Aperturas con Mancuernas",
                "pecho",
                "intermedio",
                ("banco", "mancuernas"),
                "Ejercicio de aislamiento que estira y contrae el pectoral mayor en todo su rango. Excelente para la definición y el desarrollo de la anchura del pecho.",
                "1. Túmbate en el banco plano con una mancuerna en cada mano, brazos extendidos hacia arriba.\n2. Mantén los codos ligeramente flexionados durante todo el movimiento.\n3. Abre los brazos en arco hacia los lados hasta sentir un estiramiento profundo en el pecho.\n4. Vuelve a la posición inicial contrayendo el pectoral, como si abrazaras un árbol grande.",
                musculos_secundarios="Deltoides anterior, Bíceps braquial (cabeza corta), Serrato anterior",
                musculos_antagonistas="Tríceps, Dorsales",
                errores_comunes="Extender excesivamente los brazos aumentando el riesgo de lesión en el hombro.\nUsar demasiado peso, lo que obliga a flexionar los codos en exceso convirtiéndolo en un press.\nNo controlar la fase excéntrica (apertura).",
                variantes="Aperturas inclinadas (pecho superior), Aperturas declinadas (pecho inferior), Cruceta o polea en cruce, Cruce de banda",
                comentarios="Las aperturas son un ejercicio de aislamiento, no de fuerza máxima. Usa pesos moderados y enfócate en sentir el estiramiento en cada repetición. Combínalas con el press para resultados óptimos.",
            ),
            # ══════════════════════════════════════════════════
            # ESPALDA
            # ══════════════════════════════════════════════════
            SeedExercise(
                "Dominadas",
                "espalda",
                "intermedio",
                ("barra_dominadas",),
                "El ejercicio de tirón con peso corporal más completo. Desarrolla el dorsal ancho, bíceps y toda la musculatura de la espalda media. Base de cualquier programa de espalda.",
                "1. Cuelga de la barra con agarre prono (palmas al frente) a la anchura de los hombros.\n2. Activa las escápulas deprimiéndolas (hombros abajo y atrás) antes de tirar.\n3. Flexiona los codos jalando el cuerpo hacia arriba hasta que la barbilla supere la barra.\n4. Visualiza que llevas los codos hacia las caderas para maximizar la activación del dorsal.\n5. Baja de forma completamente controlada hasta la extensión total de los brazos.",
                musculos_secundarios="Bíceps braquial, Braquial, Redondo mayor, Romboides, Trapecio inferior",
                musculos_antagonistas="Deltoides anterior, Pectoral, Tríceps",
                errores_comunes="No descender completamente entre repeticiones (media dominada).\nUsar el impulso del cuerpo en lugar de la fuerza de los dorsales.\nLevantar los hombros en lugar de activar las escápulas al inicio.\nDoblar excesivamente las piernas, cambiando el centro de gravedad.",
                variantes="Chin-Ups (agarre supino, mayor activación de bíceps), Dominadas neutras (agarre paralelo), Dominadas con peso, Dominadas asistidas con banda",
                comentarios="Si no puedes hacer una dominada completa, practica las negativas (baja en 5-8 segundos) o usa una banda de asistencia. Las dominadas son el criterio más honesto de la relación fuerza/peso.",
            ),
            SeedExercise(
                "Remo con Barra",
                "espalda",
                "intermedio",
                ("barra",),
                "Ejercicio fundamental de tracción horizontal para el desarrollo de la espalda media, el espesor del dorsal y el trapecio.",
                "1. Con la barra en el suelo o en rack, agárrala con un ancho ligeramente mayor que los hombros.\n2. Realiza una bisagra de cadera: espalda recta, inclinada entre 45° y paralela al suelo.\n3. Jala la barra hacia el abdomen (ombligo) apretando los codos contra el cuerpo.\n4. Pausa brevemente contrayendo las escápulas y baja de forma controlada.",
                musculos_secundarios="Bíceps, Braquiorradial, Erectores espinales, Trapecio",
                musculos_antagonistas="Pectoral, Deltoides anterior",
                errores_comunes="Redondear la espalda baja durante el movimiento.\nUsar el impulso del torso para levantar el peso (remo con balanceo).\nJalar hacia el pecho en vez de hacia el ombligo, perdiendo activación del dorsal.\nNo completar la retracción escapular.",
                variantes="Remo con mancuerna (unilateral), Remo Pendlay (desde el suelo), Remo invertido, T-Bar Row",
                comentarios="La posición de la barra al final del movimiento determina qué músculos trabajan más: hacia el ombligo activa más el dorsal; hacia el pecho, más trapecio y romboides.",
            ),
            SeedExercise(
                "Remo con Mancuerna",
                "espalda",
                "principiante",
                ("mancuernas", "banco"),
                "Remo unilateral apoyado en el banco que permite mayor rango de movimiento y carga sin estrés en la zona lumbar. Ideal para corregir asimetrías.",
                "1. Apoya una rodilla y la mano del mismo lado en el banco formando una línea.\n2. Con la mano libre sostén la mancuerna con el brazo extendido hacia el suelo.\n3. Jala la mancuerna hacia la cadera (no hacia el pecho) llevando el codo hacia el techo.\n4. Pausa contrayendo el dorsal y baja de forma controlada sin girar el torso.",
                musculos_secundarios="Bíceps, Trapecio, Romboides, Redondo mayor",
                musculos_antagonistas="Pectoral, Deltoides anterior",
                errores_comunes="Rotar el torso para ayudar a subir la mancuerna.\nJalar hacia el hombro en lugar de hacia la cadera.\nNo bajar el brazo completamente, perdiendo el rango de estiramiento.",
                variantes="Remo con barra, Remo en banco inclinado, Remo con agarre neutro, Seal Row",
                comentarios="Imagina que el brazo es solo un gancho y que el verdadero motor es el dorsal. Esto ayuda a eliminar la compensación del bíceps.",
            ),
            SeedExercise(
                "Pull-down con Banda",
                "espalda",
                "principiante",
                ("banda",),
                "Simulación del jalón al pecho con banda elástica. Ejercicio introductorio perfecto para aprender a activar el dorsal antes de las dominadas.",
                "1. Ancla la banda a un punto elevado (puerta, rack).\n2. Siéntate o arrodíllate mirando el punto de anclaje.\n3. Agarra la banda con los brazos extendidos sobre la cabeza.\n4. Jala hacia abajo y hacia el pecho llevando los codos hacia las caderas.\n5. Controla el regreso a la posición inicial.",
                musculos_secundarios="Bíceps, Redondo mayor, Trapecio inferior, Romboides",
                musculos_antagonistas="Deltoides anterior, Pectoral superior",
                errores_comunes="Jalar con los brazos sin activar primero las escápulas.\nEchar el torso hacia atrás para usar el peso corporal como ayuda.\nNo completar la extensión de los brazos en la parte alta.",
                variantes="Jalón al pecho en polea, Dominadas, Chin-Ups, Straight Arm Pulldown",
                comentarios="Antes de cada repetición, piensa en 'bajar los hombros de las orejas'. Este gesto de depresión escapular es clave para activar el dorsal correctamente.",
            ),
            # ══════════════════════════════════════════════════
            # HOMBROS
            # ══════════════════════════════════════════════════
            SeedExercise(
                "Press Militar con Barra",
                "hombros",
                "intermedio",
                ("barra",),
                "Ejercicio fundamental de empuje vertical para el desarrollo del deltoides. Uno de los mejores indicadores de la fuerza del tren superior.",
                "1. De pie, agarra la barra con un ancho ligeramente mayor que los hombros.\n2. Posiciona la barra a la altura de la clavícula con los codos por delante.\n3. Contrae glúteos y core para estabilizar la columna.\n4. Empuja la barra verticalmente sobre la cabeza hasta la extensión completa.\n5. Inclina ligeramente la cabeza hacia atrás al pasar la barra y vuelve a la posición neutra arriba.\n6. Baja de forma controlada a la posición inicial.",
                musculos_secundarios="Tríceps braquial, Trapecio, Serrato anterior, Core",
                musculos_antagonistas="Dorsales, Bíceps, Pectoral (porción inferior)",
                errores_comunes="Arquear excesivamente la zona lumbar para ayudar en el movimiento.\nNo activar el core, lo que genera inestabilidad y riesgo lumbar.\nBarrer la barra hacia adelante en lugar de empujar en línea recta.\nNo extender completamente los codos arriba.",
                variantes="Press militar sentado, Press con mancuernas, Push Press (con impulso de piernas), Press Arnold",
                comentarios="El press militar de pie activa más la musculatura estabilizadora que la versión sentada. Sin embargo, en caso de problemas lumbares, la versión sentada con respaldo es más segura.",
            ),
            SeedExercise(
                "Elevaciones laterales",
                "hombros",
                "principiante",
                ("mancuernas",),
                "Ejercicio de aislamiento para el deltoides medio (haz lateral). Responsable de dar amplitud y anchura al hombro. Imprescindible para la definición de hombros.",
                "1. De pie, sostén una mancuerna en cada mano con los brazos colgando a los lados.\n2. Mantén los codos ligeramente flexionados durante todo el movimiento.\n3. Eleva los brazos hacia los lados hasta la altura de los hombros.\n4. Los pulgares deben apuntar ligeramente hacia abajo (como vaciando una jarra) para mayor activación del deltoides medio.\n5. Baja de forma controlada sin dejar caer las mancuernas.",
                musculos_secundarios="Trapecio superior, Supraespinoso",
                musculos_antagonistas="Deltoides anterior, Pectoral",
                errores_comunes="Usar el impulso del cuerpo para subir las mancuernas.\nLevantar los hombros (encogimiento) al elevar los brazos.\nSubir las mancuernas por encima de los hombros, lo que activa más el trapecio.\nUsar un peso excesivo que impide controlar la bajada.",
                variantes="Elevaciones laterales con banda, Elevaciones con cable, L-Lateral Raise, Vuelos invertidos (deltoides posterior)",
                comentarios="Las elevaciones laterales con cable o banda generan mayor tensión en el punto de máxima contracción que las mancuernas. Considera hacer las últimas repeticiones de cada serie con cable.",
            ),
            SeedExercise(
                "Press Arnold",
                "hombros",
                "intermedio",
                ("mancuernas",),
                "Variante del press de hombros creada por Arnold Schwarzenegger que activa los tres haces del deltoides gracias a la rotación de las muñecas durante el movimiento.",
                "1. Siéntate con las mancuernas a la altura del pecho, palmas hacia ti.\n2. Al empujar las mancuernas hacia arriba, rota gradualmente las muñecas hasta que las palmas queden al frente en el punto más alto.\n3. Extiende completamente los brazos arriba.\n4. Al bajar, realiza la rotación inversa volviendo a la posición de palmas hacia dentro.",
                musculos_secundarios="Tríceps, Trapecio, Serrato anterior",
                musculos_antagonistas="Dorsales, Bíceps",
                errores_comunes="Realizar la rotación solo al final en lugar de durante todo el recorrido.\nArquear la espalda al empujar.\nBajar demasiado las mancuernas, generando tensión excesiva en los rotadores del hombro.",
                variantes="Press militar con barra, Press con mancuernas, Press unilateral, Push Press",
                comentarios="El giro característico del Press Arnold garantiza que trabajes el deltoides anterior, medio y posterior en una sola serie. Ideal para quienes quieren maximizar el volumen en poco tiempo.",
            ),
            # ══════════════════════════════════════════════════
            # BÍCEPS
            # ══════════════════════════════════════════════════
            SeedExercise(
                "Curl de Bíceps con Barra",
                "biceps",
                "principiante",
                ("barra",),
                "El ejercicio más clásico para el desarrollo del bíceps braquial. Permite cargar más peso que las mancuernas, ideal para sesiones de fuerza.",
                "1. De pie, agarra la barra con un ancho igual a los hombros y agarre supino (palmas hacia arriba).\n2. Mantén los codos pegados a los costados durante todo el movimiento.\n3. Flexiona los codos levantando la barra hasta que los bíceps estén completamente contraídos.\n4. Aguanta 1 segundo en la contracción máxima y baja de forma controlada.",
                musculos_secundarios="Braquial, Braquiorradial, Supinador largo",
                musculos_antagonistas="Tríceps braquial",
                errores_comunes="Balancear el torso hacia atrás para ayudar a subir la barra (curl con momentum).\nMover los codos hacia adelante reduciendo la activación del bíceps.\nNo bajar completamente los brazos, perdiendo el rango de movimiento.\nApretar demasiado el agarre, activando los antebrazos en exceso.",
                variantes="Curl con mancuernas, Curl con barra EZ (menor estrés en muñecas), Curl con cable, Curl 21s",
                comentarios="La barra EZ reduce la tensión en las muñecas y codos sin comprometer la activación del bíceps. Úsala si tienes molestias con la barra recta.",
            ),
            SeedExercise(
                "Curl con Mancuernas",
                "biceps",
                "principiante",
                ("mancuernas",),
                "Variante del curl que permite trabajar cada brazo de forma independiente, detectando y corrigiendo asimetrías de fuerza. Permite supinar la muñeca al subir.",
                "1. De pie, sostén una mancuerna en cada mano con los brazos extendidos y agarre neutro.\n2. Al iniciar la subida, supina la muñeca (gira la palma hacia arriba).\n3. Flexiona el codo hasta que el bíceps esté completamente contraído.\n4. Puedes alternar brazos o hacerlo simultáneamente.\n5. Baja de forma controlada volviendo al agarre neutro.",
                musculos_secundarios="Braquial, Braquiorradial",
                musculos_antagonistas="Tríceps",
                errores_comunes="No supinar la muñeca, perdiendo la contracción máxima del bíceps.\nBalancear los hombros para ayudar en la subida.\nHacer el movimiento demasiado rápido, perdiendo el control.",
                variantes="Curl martillo (agarre neutro, más braquial), Curl concentrado, Curl alternado, Curl inclinado",
                comentarios="La supinación de la muñeca al subir es lo que diferencia el curl de mancuernas del curl martillo. Asegúrate de realizarla para aprovechar la función supinadora del bíceps.",
            ),
            SeedExercise(
                "Curl martillo",
                "biceps",
                "principiante",
                ("mancuernas",),
                "Curl con agarre neutro (pulgares hacia arriba) que enfoca el trabajo en el braquial y el braquiorradial, dotando al brazo de mayor espesor y grosor.",
                "1. De pie, sostén las mancuernas con agarre neutro (pulgares hacia arriba).\n2. Mantén los codos pegados a los costados.\n3. Flexiona los codos elevando las mancuernas sin rotar las muñecas.\n4. Baja controlado manteniendo el agarre neutro.",
                musculos_secundarios="Bíceps braquial, Supinador largo",
                musculos_antagonistas="Tríceps",
                errores_comunes="Rotar la muñeca convirtiéndolo en un curl supinado.\nBalancear el cuerpo para ayudar en el movimiento.\nNo controlar la fase excéntrica.",
                variantes="Curl con barra (agarre supino), Curl Zottman, Cross Body Curl, Curl con cable neutro",
                comentarios="El curl martillo es subesvalorado. El braquial que desarrolla empuja el bíceps desde abajo, haciéndolo lucir más grande. Incluye siempre este ejercicio en tu rutina de brazos.",
            ),
            SeedExercise(
                "Curl con Banda",
                "biceps",
                "principiante",
                ("banda",),
                "Curl de bíceps con banda elástica, ideal para principiantes y para entrenar en casa. La banda ofrece tensión creciente que desafía el músculo en el punto de máxima contracción.",
                "1. Párate sobre la banda con los pies a la anchura de los hombros.\n2. Agarra los extremos con agarre supino.\n3. Flexiona los codos manteniendo los codos fijos a los costados.\n4. Contrae en el tope y baja de forma controlada manteniendo la tensión.",
                musculos_secundarios="Braquial, Braquiorradial",
                musculos_antagonistas="Tríceps",
                errores_comunes="Dejar que la banda se afloje en la parte baja, perdiendo la tensión.\nMover los codos hacia adelante.\nUtilizar una banda demasiado larga que no ofrezca suficiente resistencia.",
                variantes="Curl de bíceps con barra, Curl con mancuernas, Bayesian Curl con banda, Curl en cable",
                comentarios="La ventaja de la banda es que la resistencia aumenta a medida que el músculo se acerca a la contracción máxima, estimulando fibras que las mancuernas no alcanzan con la misma intensidad.",
            ),
            # ══════════════════════════════════════════════════
            # TRÍCEPS
            # ══════════════════════════════════════════════════
            SeedExercise(
                "Fondos en banco",
                "triceps",
                "principiante",
                ("banco",),
                "Ejercicio de peso corporal para el tríceps usando un banco. Permite introducir el patrón de empuje vertical descendente con bajo riesgo.",
                "1. Siéntate en el borde del banco, manos al lado de las caderas con los dedos hacia adelante.\n2. Desplaza las caderas hacia adelante separándolas del banco.\n3. Dobla los codos bajando las caderas hacia el suelo.\n4. Mantén la espalda próxima al banco y los hombros abajo.\n5. Empuja hasta la extensión completa de los codos.",
                musculos_secundarios="Deltoides anterior, Pectoral inferior",
                musculos_antagonistas="Bíceps, Dorsales",
                errores_comunes="Separar las caderas excesivamente del banco, girando el hombro internamente y generando lesión.\nBajar más de lo que el rango de movimiento permite, forzando los hombros.\nEncorvar los hombros durante el movimiento.",
                variantes="Fondos en paralelas (más avanzado), Fondos con pies elevados (mayor carga), Fondos asistidos con banda",
                comentarios="Mantén siempre los hombros deprimidos (abajo) durante los fondos. Si los hombros suben hacia las orejas, es señal de que estás perdiendo la activación del tríceps.",
            ),
            SeedExercise(
                "Extensión de tríceps por encima (mancuerna)",
                "triceps",
                "intermedio",
                ("mancuernas",),
                "Ejercicio que pone especial énfasis en la cabeza larga del tríceps gracias a la posición sobre la cabeza que maximiza el estiramiento.",
                "1. Sostén una mancuerna con ambas manos (o una en cada mano) sobre la cabeza con los brazos extendidos.\n2. Los codos deben apuntar al frente, no hacia los lados.\n3. Flexiona los codos bajando la mancuerna detrás de la cabeza.\n4. Extiende los codos volviendo a la posición inicial.",
                musculos_secundarios="Ancóneo",
                musculos_antagonistas="Bíceps",
                errores_comunes="Abrir los codos hacia los lados, perdiendo la tensión en la cabeza larga.\nNo bajar lo suficiente, limitando el estiramiento.\nArquear la espalda para compensar la falta de movilidad del hombro.",
                variantes="Extensión con barra EZ (French Press), Extensión con cable, Extensión unilateral, Skullcrusher",
                comentarios="La cabeza larga del tríceps es la más grande (representa cerca del 60% del volumen del tríceps) y solo se estira completamente con los brazos elevados sobre la cabeza. Incluye siempre un ejercicio overhead en tu rutina de tríceps.",
            ),
            SeedExercise(
                "Extensión de Tríceps",
                "triceps",
                "principiante",
                ("banda", "mancuernas"),
                "Extensión vertical del codo para aislar el tríceps. Con banda ofrece tensión constante y es ideal para principiantes.",
                "1. Ancla la banda en un punto elevado.\n2. De pie, agarra la banda y mantén los codos pegados al cuerpo.\n3. Extiende los codos hacia abajo hasta la extensión completa.\n4. Controla el retorno sin que los codos se separen del cuerpo.",
                musculos_secundarios="Ancóneo",
                musculos_antagonistas="Bíceps",
                errores_comunes="Mover los codos hacia adelante para ayudar en la extensión.\nNo llegar a la extensión completa del codo.\nUtilizar los hombros para impulsar el movimiento.",
                variantes="Pushdown con barra, Pushdown con cuerda, Pushdown con agarre supino (mayor cabeza larga), Extensión overhead",
                comentarios="El pushdown es excelente para calentar los codos antes de ejercicios más pesados. Usa un peso que te permita extender completamente el codo en cada repetición.",
            ),
            SeedExercise(
                "Fondos en Paralelas",
                "triceps",
                "intermedio",
                ("peso_corporal",),
                "Ejercicio compuesto de peso corporal para tríceps, pectoral inferior y deltoides anterior. La inclinación del torso determina qué músculo trabaja más.",
                "1. Agarra las paralelas y levanta el cuerpo con los brazos extendidos.\n2. Para enfatizar el tríceps: mantén el torso vertical.\n3. Baja doblando los codos hasta que los brazos formen ángulo recto (o hasta sentir estiramiento).\n4. Empuja hacia arriba hasta la extensión completa.",
                musculos_secundarios="Pectoral inferior, Deltoides anterior",
                musculos_antagonistas="Bíceps, Dorsales",
                errores_comunes="Bajar más allá de lo que la movilidad del hombro permite.\nLevantar los hombros durante el movimiento.\nInclinarse demasiado al frente si el objetivo es el tríceps.",
                variantes="Fondos en banco (más fácil), Fondos con peso (más difícil), Fondos asistidos con banda",
                comentarios="Torso vertical = más tríceps. Torso inclinado al frente = más pectoral. Elige la variante según tu objetivo del día.",
            ),
            SeedExercise(
                "Press Francés",
                "triceps",
                "intermedio",
                ("barra", "mancuernas"),
                "También llamado Skullcrusher. Ejercicio de aislamiento acostado que trabaja intensamente el tríceps con énfasis en la cabeza larga y medial.",
                "1. Túmbate en el banco con la barra o mancuernas sobre el pecho.\n2. Eleva los brazos verticalmente con los codos apuntando al techo.\n3. Flexiona los codos llevando la barra o las mancuernas hacia la frente o por encima de la cabeza.\n4. Extiende los codos volviendo a la posición vertical.",
                musculos_secundarios="Ancóneo",
                musculos_antagonistas="Bíceps",
                errores_comunes="Abrir los codos hacia los lados al bajar el peso.\nBajar la barra directamente hacia la cara (por eso se llama 'mata cacos').\nMover los hombros durante el movimiento.",
                variantes="Extensión overhead (más énfasis en cabeza larga), Skullcrusher con mancuernas, Extensión con cable, JM Press",
                comentarios="Si bajas la barra detrás de la cabeza en lugar de hacia la frente, activas más la cabeza larga y obtienes mayor estiramiento. Prueba ambas variantes.",
            ),
            # ══════════════════════════════════════════════════
            # PIERNAS
            # ══════════════════════════════════════════════════
            SeedExercise(
                "Sentadilla con Barra",
                "piernas",
                "intermedio",
                ("barra",),
                "La reina de los ejercicios. Desarrolla cuádriceps, glúteos, isquiotibiales y toda la cadena posterior. El ejercicio más completo del tren inferior.",
                "1. Coloca la barra en los trapecios (back squat) o en la parte alta de los hombros.\n2. Pies a la anchura de los hombros, ligeramente en punta hacia afuera.\n3. Activa el core y retrae las escápulas.\n4. Inicia el movimiento empujando las rodillas hacia fuera (en la dirección de los pies).\n5. Baja hasta que los muslos queden paralelos al suelo o más.\n6. Empuja el suelo con los talones para volver a subir.",
                musculos_secundarios="Glúteo mayor, Isquiotibiales, Erectores espinales, Aductores, Core",
                musculos_antagonistas="Flexores de cadera, Tibial anterior",
                errores_comunes="Rodillas en valgo (colapso hacia adentro).\nLevantar los talones del suelo, indicando falta de movilidad de tobillo.\nRedondear la espalda baja al llegar al punto más bajo.\nNo alcanzar una profundidad adecuada (sentadilla alta).",
                variantes="Sentadilla frontal (más cuádriceps), Sentadilla goblet, Sentadilla búlgara, Sentadilla Sumo, Sentadilla hack",
                comentarios="La profundidad de la sentadilla debe ser la máxima que tu movilidad permita sin comprometer la postura de la espalda. Trabaja la movilidad de cadera y tobillo para mejorarla.",
            ),
            SeedExercise(
                "Sentadilla con Peso Corporal",
                "piernas",
                "principiante",
                ("peso_corporal",),
                "Versión básica de la sentadilla sin carga adicional. Perfecta para aprender el patrón motor y para principiantes.",
                "1. De pie, pies a la anchura de los hombros con los pies ligeramente en punta.\n2. Extiende los brazos al frente para contrabalancear.\n3. Baja como si fueras a sentarte en una silla, manteniendo el torso erguido.\n4. Rodillas en la dirección de los pies, talones apoyados en todo momento.\n5. Baja hasta que los muslos queden paralelos al suelo.\n6. Empuja con los talones para subir.",
                musculos_secundarios="Glúteos, Isquiotibiales, Core",
                musculos_antagonistas="Flexores de cadera",
                errores_comunes="Inclinar excesivamente el torso hacia adelante.\nRodillas en valgo (cayendo hacia adentro).\nLevantar los talones del suelo.",
                variantes="Sentadilla con barra, Sentadilla goblet (con kettlebell), Sentadilla sumo, Sentadilla con salto",
                comentarios="Aprende primero la sentadilla sin peso antes de cargar la barra. Practica la sentadilla goblet (con kettlebell al pecho) como paso intermedio: el peso al frente te obliga a mantener el torso erguido.",
            ),
            SeedExercise(
                "Prensa con Disco",
                "piernas",
                "intermedio",
                ("disco",),
                "Versión accesible de la prensa de piernas usando un disco como resistencia. Trabaja cuádriceps y glúteos con menor estrés en la zona lumbar que la sentadilla.",
                "1. Agarra el disco firmemente con ambas manos delante del pecho.\n2. Realiza la sentadilla goblet: baja con el torso erguido y las rodillas siguiendo los pies.\n3. O utiliza el disco como lastre sujetándolo contra el pecho en sentadilla estándar.\n4. Mantén el core activo y controla el rango de movimiento.",
                musculos_secundarios="Glúteos, Isquiotibiales, Core",
                musculos_antagonistas="Flexores de cadera",
                errores_comunes="Usar un disco demasiado pesado que compromete la postura.\nNo mantener el disco pegado al cuerpo.",
                variantes="Sentadilla goblet con kettlebell, Sentadilla con barra, Sentadilla con mancuerna",
                comentarios="El disco al frente del pecho actúa como contrapeso, facilitando el mantenimiento del torso vertical. Útil para personas con movilidad torácica limitada.",
            ),
            SeedExercise(
                "Peso muerto rumano",
                "piernas",
                "intermedio",
                ("barra", "mancuernas"),
                "Variante del peso muerto que se centra en el estiramiento y contracción de los isquiotibiales. La cadera actúa como bisagra manteniendo las piernas casi extendidas.",
                "1. De pie con el peso en manos delante de los muslos.\n2. Rodillas ligeramente flexionadas durante todo el movimiento (no doblar más).\n3. Empuja las caderas hacia atrás manteniendo la espalda neutra.\n4. Baja el peso rozando las piernas hasta sentir el estiramiento en los isquiotibiales.\n5. Lleva las caderas al frente para volver a la posición inicial.",
                musculos_secundarios="Glúteo mayor, Erectores espinales, Aductores",
                musculos_antagonistas="Cuádriceps, Flexores de cadera",
                errores_comunes="Redondear la espalda baja al bajar el peso.\nDoblar las rodillas convirtiéndolo en peso muerto convencional.\nBajar el peso demasiado por debajo de las rodillas perdiendo la tensión en los isquiotibiales.",
                variantes="Peso muerto convencional, Peso muerto a una pierna (unilateral), Good Morning, Peso muerto sumo",
                comentarios="El peso muerto rumano es el mejor ejercicio para desarrollar los isquiotibiales. La clave es iniciar el movimiento desde la cadera (bisagra de cadera), no desde las rodillas.",
            ),
            SeedExercise(
                "Zancadas",
                "piernas",
                "principiante",
                ("mancuernas", "peso_corporal"),
                "Ejercicio unilateral que desarrolla fuerza en cuádriceps y glúteos mientras mejora el equilibrio y corrige asimetrías entre piernas.",
                "1. De pie, da un paso largo hacia adelante con una pierna.\n2. Baja la rodilla trasera hacia el suelo sin tocar.\n3. El torso permanece erguido durante todo el movimiento.\n4. La rodilla delantera no debe sobrepasar la punta del pie.\n5. Empuja con el talón delantero para volver a la posición inicial.",
                musculos_secundarios="Glúteos, Isquiotibiales, Core, Pantorrillas",
                musculos_antagonistas="Flexores de cadera",
                errores_comunes="Dar un paso demasiado corto, lo que lleva la rodilla más allá del pie.\nInclinar el torso hacia adelante.\nRodilla delantera en valgo (cayendo hacia adentro).",
                variantes="Zancada inversa (menor estrés en rodilla), Zancada caminando, Zancada lateral, Sentadilla búlgara (pie trasero elevado)",
                comentarios="La zancada inversa (paso atrás) es más amigable con las rodillas que la zancada frontal y aísla más el glúteo. Empieza con esta versión si tienes molestias en las rodillas.",
            ),
            SeedExercise(
                "Sentadilla con Kettlebell",
                "piernas",
                "principiante",
                ("kettlebell",),
                "La sentadilla goblet con kettlebell es la mejor variante de iniciación. El peso al frente te obliga a mantener el torso erguido y facilita la mecánica correcta.",
                "1. Sostén el kettlebell con ambas manos por el asa, a la altura del pecho.\n2. Los codos apuntan hacia abajo y hacia adentro.\n3. Pies a la anchura de los hombros con los pies ligeramente en punta.\n4. Baja manteniendo el torso erguido hasta que los muslos queden paralelos o más.\n5. Empuja con los talones y sube fuerte.",
                musculos_secundarios="Glúteos, Isquiotibiales, Core, Aductores",
                musculos_antagonistas="Flexores de cadera",
                errores_comunes="Dejar que los codos bajen y el kettlebell caiga, perdiendo la posición del torso.\nRodillas en valgo.\nNo descender lo suficiente.",
                variantes="Sentadilla goblet con mancuerna, Sentadilla con barra, Sentadilla con peso corporal",
                comentarios="La sentadilla goblet es el mejor ejercicio de entrada a la sentadilla cargada. El kettlebell como contrapeso automáticamente corrige la inclinación del torso.",
            ),
            SeedExercise(
                "Puente de glúteos",
                "gluteos",
                "principiante",
                ("peso_corporal",),
                "Ejercicio de activación del glúteo mayor. Desarrolla la fuerza de extensión de cadera y estabiliza la pelvis. Base del Hip Thrust.",
                "1. Túmbate boca arriba con las rodillas flexionadas y los pies apoyados en el suelo.\n2. Los pies deben estar debajo de las rodillas, a la anchura de las caderas.\n3. Empuja con los talones elevando las caderas hasta que formen una línea recta con el tronco.\n4. Aprieta los glúteos en el punto más alto durante 1-2 segundos.\n5. Baja controlado sin llegar a apoyar las caderas en el suelo entre repeticiones.",
                musculos_secundarios="Isquiotibiales, Core, Erectores espinales",
                musculos_antagonistas="Flexores de cadera, Cuádriceps",
                errores_comunes="Hiperextender la zona lumbar en lugar de elevar las caderas con los glúteos.\nNo apretar los glúteos en la parte alta del movimiento.\nTener los pies demasiado alejados de las caderas, transfiriendo el trabajo a los isquiotibiales.",
                variantes="Hip Thrust con barra (mayor carga), Puente unilateral (mayor dificultad), Hip Thrust con mancuerna",
                comentarios="Antes de cargar el Hip Thrust con barra, domina el puente de glúteos con peso corporal. La señal de que activas bien los glúteos es sentir la contracción en la nalga, no en la zona lumbar.",
            ),
            SeedExercise(
                "Hip Thrust con Barra",
                "gluteos",
                "intermedio",
                ("barra", "banco"),
                "El ejercicio más eficaz para el desarrollo del glúteo mayor con gran carga. Produce la mayor activación electromiográfica del glúteo mayor de todos los ejercicios.",
                "1. Apoya la parte media-alta de la espalda en el banco (zona de los omóplatos).\n2. Coloca la barra sobre las caderas con un protector o toalla para amortiguar.\n3. Los pies apoyados al suelo a la anchura de las caderas, rodillas a 90°.\n4. Empuja la barra hacia arriba extendiendo las caderas hasta que formen una línea recta.\n5. Mantén la barbilla metida, las costillas bajas y no hiperextiendas la lumbar.\n6. Baja controlado hasta casi tocar el suelo.",
                musculos_secundarios="Isquiotibiales, Cuádriceps, Core",
                musculos_antagonistas="Flexores de cadera, Recto abdominal",
                errores_comunes="Hiperextender la zona lumbar en el tope (señal de que la espalda trabaja en lugar del glúteo).\nTener los pies demasiado cerca o lejos de las caderas.\nNo mantener la barbilla metida y las costillas bajas.",
                variantes="Puente de glúteos (sin banco, menor carga), Hip Thrust con mancuerna, Hip Thrust unilateral, Hip Thrust a 45 grados",
                comentarios="La posición de los pies es crucial: si los tienes muy cerca, trabajan más los cuádriceps; más alejados, más isquiotibiales. Encuentra la posición en la que sientas más el glúteo.",
            ),
            SeedExercise(
                "Patada de Glúteo con Banda",
                "gluteos",
                "principiante",
                ("banda",),
                "Ejercicio de aislamiento del glúteo en cuadrupedia. Activa el glúteo mayor sin carga en la columna, ideal para activación y rehabilitación.",
                "1. En posición de cuadrupedia (manos y rodillas), coloca la banda en el tobillo.\n2. Mantén la espalda neutra durante todo el movimiento.\n3. Extiende una pierna hacia atrás y hacia arriba contrayendo el glúteo.\n4. Pausa en el punto de máxima contracción.\n5. Baja controlado sin apoyar la rodilla en el suelo entre repeticiones.",
                musculos_secundarios="Isquiotibiales, Erectores espinales (estabilización)",
                musculos_antagonistas="Flexores de cadera, Cuádriceps",
                errores_comunes="Arquear la espalda baja para ganar rango de movimiento.\nRotar la cadera al elevar la pierna.\nLevantar la pierna demasiado alto provocando compensación lumbar.",
                variantes="Donkey Kick con peso en tobillo, Cable Kickback, Extensión de cadera en máquina",
                comentarios="Enfócate en sentir el glúteo trabajar, no en levantar la pierna lo más alto posible. La calidad del movimiento es más importante que la amplitud.",
            ),
            # ══════════════════════════════════════════════════
            # CORE
            # ══════════════════════════════════════════════════
            SeedExercise(
                "Plancha",
                "core",
                "principiante",
                ("peso_corporal",),
                "Ejercicio isométrico fundamental para la estabilidad del core. Activa toda la musculatura estabilizadora de la columna vertebral.",
                "1. Apoya los codos en el suelo directamente bajo los hombros.\n2. Extiende las piernas apoyando las puntas de los pies.\n3. El cuerpo forma una línea recta desde la cabeza hasta los talones.\n4. Activa glúteos y abdominales para evitar que las caderas caigan o suban.\n5. Respira de forma continua sin apnea.",
                musculos_secundarios="Glúteos, Cuádriceps, Deltoides, Serrato anterior",
                musculos_antagonistas="Erectores espinales",
                errores_comunes="Hundir las caderas (señal de core débil o fatiga).\nElevar las caderas formando un triángulo.\nNo activar los glúteos, lo que genera presión en la zona lumbar.\nContraer la respiración.",
                variantes="Plancha lateral (oblicuos), Plancha con toque de hombro (anti-rotación), Plancha RKC (máxima tensión), Bear Plank (rodillas elevadas)",
                comentarios="La plancha es más efectiva con tensión total de todo el cuerpo que simplemente aguantando el tiempo. Aprieta los glúteos, empuja el suelo con los codos y comprime el abdomen al mismo tiempo.",
            ),
            SeedExercise(
                "Elevaciones de piernas",
                "core",
                "intermedio",
                ("peso_corporal",),
                "Ejercicio que activa la musculatura flexora de cadera y la zona inferior del recto abdominal mientras desafía la estabilidad lumbo-pélvica.",
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
                "Ejercicio de flexión de columna para el recto abdominal. El movimiento es corto: solo los hombros y la parte alta de la espalda se despegan del suelo.",
                "1. Túmbate boca arriba con las rodillas flexionadas.\n2. Coloca las manos detrás de la cabeza o cruzadas sobre el pecho.\n3. Exhala mientras contraes el abdomen elevando los hombros del suelo.\n4. El movimiento es corto: solo sube hasta que los omóplatos dejen el suelo.\n5. Baja de forma controlada sin relajar completamente el abdomen.",
                musculos_secundarios="Oblicuos (si hay rotación), Flexores de cadera",
                musculos_antagonistas="Erectores espinales",
                errores_comunes="Tirar del cuello con las manos, causando tensión cervical.\nSubir demasiado (sit-up completo), lo que activa más los flexores de cadera.\nNot hacer la contracción abdominal al subir.",
                variantes="Crunch con rotación (oblicuos), Crunch en banco declinado, Crunch con peso, Crunch en fitball",
                comentarios="El cruncho bien ejecutado es corto: el recto abdominal actúa en la flexión inicial de la columna. Si subes hasta sentarte, los flexores de cadera hacen la mayor parte del trabajo.",
            ),
            SeedExercise(
                "Rueda Abdominal",
                "abdomen",
                "avanzado",
                ("peso_corporal",),
                "Uno de los ejercicios más exigentes para el core. La extensión total del cuerpo desafía la estabilidad lumbo-pélvica al máximo.",
                "1. Arrodíllate y coloca la rueda bajo los hombros.\n2. Activa intensamente el core y los glúteos antes de moverse.\n3. Rueda hacia adelante extendiendo el cuerpo lo máximo que puedas sin que la zona lumbar colapse.\n4. Para cuando notes que la postura se pierde.\n5. Contrae el core para volver a la posición inicial.",
                musculos_secundarios="Dorsales, Pectoral, Tríceps, Glúteos",
                musculos_antagonistas="Erectores espinales (fase excéntrica)",
                errores_comunes="Colapsar la zona lumbar al extender el cuerpo.\nNo activar el core antes de iniciar el movimiento.\nHacer el movimiento demasiado rápido sin control.",
                variantes="Rollout con barra, Rollout parcial (rango reducido para principiantes), Dragon Flag",
                comentarios="El rollout parcial (solo un tercio del rango total) es mucho más seguro para principiantes. Progresa gradualmente aumentando el rango a medida que tu core se fortalece.",
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
                "El rey del levantamiento de fuerza. Involucra más grupos musculares que cualquier otro ejercicio: espalda, glúteos, piernas, trapecios y antebrazos.",
                "1. Párate con los pies a la anchura de las caderas, barra sobre los cordones.\n2. Agarra la barra con las manos ligeramente más separadas que los pies.\n3. Baja las caderas hasta que las espinillas toquen casi la barra.\n4. Espalda neutra (ni arqueada ni redondeada), pecho arriba.\n5. Empuja el suelo con los pies y lleva las caderas hacia adelante simultáneamente.\n6. La barra debe rozar las piernas durante todo el recorrido.\n7. Al bajar: primero las caderas atrás, luego dobla las rodillas.",
                musculos_secundarios="Cuádriceps, Glúteo mayor, Trapecio, Antebrazos, Core",
                musculos_antagonistas="Recto abdominal (fase de extensión)",
                errores_comunes="Redondear la espalda baja al iniciar el levantamiento.\nDejar que la barra se separe del cuerpo durante el recorrido.\nArquear la espalda en hipeextensión en el punto de bloqueo.\nTirar de la barra con los brazos en vez de empujar el suelo.",
                variantes="Peso muerto rumano (isquiotibiales), Peso muerto sumo (caderas más abiertas), Peso muerto trap bar, Rack Pull",
                comentarios="El peso muerto es seguro cuando se ejecuta con técnica correcta. La espalda redondeada es el error más peligroso. Graba tus series de vez en cuando para verificar tu postura."),
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
                    "musculos_secundarios": seed.musculos_secundarios,
                    "musculos_antagonistas": seed.musculos_antagonistas,
                    "errores_comunes": seed.errores_comunes,
                    "variantes": seed.variantes,
                    "comentarios": seed.comentarios,
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
                if not ejercicio.musculos_secundarios and seed.musculos_secundarios:
                    ejercicio.musculos_secundarios = seed.musculos_secundarios
                    changed = True
                if not ejercicio.musculos_antagonistas and seed.musculos_antagonistas:
                    ejercicio.musculos_antagonistas = seed.musculos_antagonistas
                    changed = True
                if not ejercicio.errores_comunes and seed.errores_comunes:
                    ejercicio.errores_comunes = seed.errores_comunes
                    changed = True
                if not ejercicio.variantes and seed.variantes:
                    ejercicio.variantes = seed.variantes
                    changed = True
                if not ejercicio.comentarios and seed.comentarios:
                    ejercicio.comentarios = seed.comentarios
                    changed = True
                if changed:
                    ejercicio.save(update_fields=[
                        "grupo_muscular", "nivel", "descripcion", "instrucciones",
                        "duracion_minutos", "musculos_secundarios", "musculos_antagonistas",
                        "errores_comunes", "variantes", "comentarios",
                    ])
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

