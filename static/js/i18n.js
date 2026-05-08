/**
 * SportsVision — Auto-translation based on OS/browser language
 * Detects navigator.language and replaces Spanish text with the target language.
 * Algorithm: substring replacement (longest keys first) for maximum coverage.
 */
(function () {
  var lang = (navigator.language || navigator.userLanguage || 'es').substring(0, 2).toLowerCase();
  if (lang === 'es') return;

  var T = {
    en: {
      // ── Login ──
      'INICIAR SESIÓN': 'LOG IN',
      'Iniciar sesión': 'Log in',
      'Usuario o Correo': 'Username or Email',
      'Tu usuario o correo electrónico': 'Your username or email',
      '¿Olvidaste tu contraseña?': 'Forgot your password?',
      'Tu contraseña': 'Your password',
      '¿No tienes cuenta?': "Don't have an account?",
      'Regístrate': 'Sign up',
      '← Volver al inicio': '← Back to home',
      'Volver al inicio': 'Back to home',

      // ── Registro paso 1 ──
      'CREAR CUENTA': 'CREATE ACCOUNT',
      'Crear cuenta': 'Create account',
      'Primero verificamos que el correo es tuyo.': 'First we verify that the email is yours.',
      'Te enviaremos un código de': "We'll send you a code of",
      'Correo electrónico': 'Email',
      'tu@correo.com': 'your@email.com',
      'Enviar código de verificación': 'Send verification code',
      'Enviando...': 'Sending...',
      '¿Ya tienes cuenta?': 'Already have an account?',
      'Inicia sesión': 'Log in',
      'Ingresa tu correo electrónico.': 'Enter your email address.',
      'Este correo ya se encuentra registrado. ¿Quieres iniciar sesión?': 'This email is already registered. Do you want to log in?',

      // ── Registro paso 2 (OTP) ──
      'Revisa tu correo': 'Check your email',
      'Enviamos un código de 6 dígitos a': 'We sent a 6-digit code to',
      'Verificar código': 'Verify code',
      'Reenviar código': 'Resend code',
      '← Cambiar correo': '← Change email',
      'Cambiar correo': 'Change email',
      'Verificando...': 'Verifying...',

      // ── Registro paso 3 (formulario) ──
      'verificado': 'verified',
      'Tu cuenta': 'Your account',
      'Nombre de usuario': 'Username',
      'Ej: juanfit99': 'Ex: johnfit99',
      'Mínimo 8 caracteres, no puede ser solo números.': 'Minimum 8 characters, cannot be only numbers.',
      'Mínimo 8 caracteres': 'Minimum 8 characters',
      'Contraseña': 'Password',
      'Repite tu contraseña': 'Repeat your password',
      'Las contraseñas no coinciden.': 'Passwords do not match.',
      'Siguiente': 'Next',
      'Cuéntanos sobre ti': 'Tell us about yourself',
      '¿Cómo te gustaría que te llamemos?': 'What would you like to be called?',
      'Tu nombre o apodo': 'Your name or nickname',
      'Así aparecerá en tu bienvenida y perfil.': 'This is how it will appear in your welcome and profile.',
      'Género (opcional)': 'Gender (optional)',
      'Tu objetivo': 'Your goal',
      'Esto nos ayuda a personalizar tu experiencia. Puedes cambiarlo después.': 'This helps us personalize your experience. You can change it later.',
      'Bajar de peso': 'Lose weight',
      'Quemar grasa y reducir peso': 'Burn fat and reduce weight',
      'Mantener peso': 'Maintain weight',
      'Estilo de vida saludable': 'Healthy lifestyle',
      'Ganar músculo': 'Gain muscle',
      'Aumentar masa muscular': 'Increase muscle mass',
      'Cardio y stamina': 'Cardio and stamina',
      'Movilidad y stretching': 'Mobility and stretching',
      'Deporte competitivo': 'Competitive sport',
      'Tu salud': 'Your health',
      '¿Tienes alguna condición física o lesión que debamos tener en cuenta?': 'Do you have any physical condition or injury we should know about?',
      'Esta información es opcional y nos ayuda a personalizar tu plan de entrenamiento.': 'This is optional and helps us personalize your training plan.',
      'No tengo ninguna limitación': 'I have no limitations',
      'Asma / Resp.': 'Asthma / Resp.',
      'Problemas cardíacos': 'Heart problems',
      'Hipertensión': 'Hypertension',
      'Lesión muscular': 'Muscle injury',
      'Lesión de rodilla': 'Knee injury',
      'Lesión de espalda': 'Back injury',
      'Lesión de hombro': 'Shoulder injury',
      'Articulación en riesgo': 'Joint at risk',
      'Movilidad reducida': 'Reduced mobility',
      'Embarazo / postparto': 'Pregnancy / postpartum',
      'Otra condición': 'Other condition',
      'He leído y acepto los': 'I have read and accept the',
      'de SportsVision, incluyendo la política de privacidad y el tratamiento de mis datos personales.': 'of SportsVision, including the privacy policy and the processing of my personal data.',
      'Completar registro': 'Complete registration',

      // ── Dashboard ──
      'BIENVENIDO DE VUELTA': 'WELCOME BACK',
      'Bienvenido de vuelta': 'Welcome back',
      '¿Con qué iniciamos hoy?': 'What are we starting today?',
      'ENTRENAMIENTOS': 'WORKOUTS',
      'SERIES COMPLETADAS': 'SETS COMPLETED',
      'KG LEVANTADOS': 'KG LIFTED',
      'RUTINAS': 'ROUTINES',
      'Crea tu propia rutina': 'Create your own routine',
      'Organiza tu semana': 'Organize your week',
      'Historial de entrenamientos': 'Training history',
      'Calculadoras fitness': 'Fitness calculators',
      'TUS RUTINAS': 'YOUR ROUTINES',
      'Tus rutinas': 'Your routines',
      '¿Eliminar esta rutina?': 'Delete this routine?',
      'Aún no tienes rutinas guardadas.': "You don't have any saved routines yet.",
      'Crear primera rutina': 'Create first routine',

      // ── Perfil ──
      'EDITAR PERFIL': 'EDIT PROFILE',
      'Editar perfil': 'Edit profile',
      'Panel Admin Pro': 'Admin Pro Panel',
      'Panel Profesional': 'Professional Panel',
      'Rutinas creadas': 'Created routines',
      'Series completadas': 'Sets completed',
      'Kg levantados': 'Kg lifted',
      'DATOS PERSONALES': 'PERSONAL DATA',
      'Datos personales': 'Personal data',
      'Índice de Masa Corporal': 'Body Mass Index',
      'Obesidad': 'Obesity',
      'Agrega tu peso y altura para ver el IMC': 'Add your weight and height to see your BMI',
      'Completar datos →': 'Complete data →',
      'ACTUALIZAR DATOS': 'UPDATE DATA',
      'Actualizar datos': 'Update data',
      'ACTIVIDAD RECIENTE': 'RECENT ACTIVITY',
      'Actividad Reciente': 'Recent Activity',
      'Actividad reciente': 'Recent activity',
      'Aún no hay entrenamientos registrados': 'No workouts recorded yet',
      '¡Completa tu primer entrenamiento para ver tu historial!': 'Complete your first workout to see your history!',
      'Meta calórica activa': 'Active calorie goal',
      'CALORÍAS DIARIAS': 'DAILY CALORIES',
      'kcal / día': 'kcal / day',
      'Recalcular': 'Recalculate',
      'Historial de peso': 'Weight history',
      'Foto de perfil': 'Profile photo',
      '¿Eliminar la foto de perfil?': 'Delete profile photo?',
      'Ajustar foto': 'Adjust photo',
      'Vista previa': 'Preview',
      'Arrastra para mover · Slider para zoom': 'Drag to move · Slider to zoom',
      'Aplicar y guardar': 'Apply and save',
      'La imagen no puede superar 5 MB.': 'Image cannot exceed 5 MB.',

      // ── Navegación (sidebar) ──
      'Nueva Rutina': 'New Routine',
      'Plan Semanal': 'Weekly Plan',
      'Herramientas': 'Tools',
      'Mis Dietas': 'My Diets',
      'Mi Perfil': 'My Profile',
      'Cerrar Sesión': 'Log Out',
      'Ser profesional': 'Become a Pro',
      'Panel Pro': 'Pro Panel',
      'Privacidad': 'Privacy',
      'Progreso': 'Progress',
      'Home': 'Home',

      // ── Entrenamiento activo ──
      'Finalizar entrenamiento': 'Finish workout',
      'Siguiente ejercicio': 'Next exercise',
      'Prepárate para la siguiente serie': 'Get ready for the next set',
      'Agregar serie': 'Add set',
      'Finalizar': 'Finish',
      'ANTERIOR': 'PREVIOUS',
      'Descanso': 'Rest',
      'Continuar': 'Continue',
      'Guía': 'Guide',
      'Saltar': 'Skip',
      'Terminar': 'End',
      'SERIE': 'SET',

      // ── Selección de ejercicios ──
      'Buscar ejercicio...': 'Search exercise...',
      'Agregar ejercicio': 'Add exercise',
      'Todos los ejercicios': 'All exercises',
      'Guardar rutina': 'Save routine',
      'Nombre de la rutina...': 'Routine name...',
      'Grupo Muscular': 'Muscle Group',
      'Equipamiento': 'Equipment',
      'Sin resultados para este filtro.': 'No results for this filter.',
      'Recientes': 'Recent',
      'Músculos': 'Muscles',
      'Equipo': 'Equipment',
      'Limpiar': 'Clear',
      'Crear': 'Create',

      // ── Plan semanal ──
      'PLAN SEMANAL': 'WEEKLY PLAN',
      'Lunes': 'Monday',
      'Martes': 'Tuesday',
      'Miércoles': 'Wednesday',
      'Jueves': 'Thursday',
      'Viernes': 'Friday',
      'Sábado': 'Saturday',
      'Domingo': 'Sunday',
      'Sin rutina': 'No routine',
      '¿Programar rutina?': 'Schedule routine?',
      'Elige el día o guarda sin programar.': 'Choose a day or save without scheduling.',
      'Sin programar': 'Without scheduling',
      'Programar': 'Schedule',

      // ── Herramientas ──
      'Calculadora de Calorías': 'Calorie Calculator',
      'Calculadora de IMC': 'BMI Calculator',
      'Plan Nutricional': 'Nutritional Plan',
      'Calcular': 'Calculate',
      'Resultado': 'Result',
      'Sexo': 'Sex',
      'Masculino': 'Male',
      'Femenino': 'Female',
      'Actividad': 'Activity',
      'Sedentario': 'Sedentary',
      'Ligero': 'Light',
      'Moderado': 'Moderate',
      'Intenso': 'Intense',
      'Muy intenso': 'Very intense',

      // ── General ──
      'GUARDAR CAMBIOS': 'SAVE CHANGES',
      'Guardar cambios': 'Save changes',
      'Guardar': 'Save',
      'Cancelar': 'Cancel',
      'Confirmar': 'Confirm',
      'Volver': 'Back',
      'Eliminar': 'Delete',
      'Editar': 'Edit',
      'Descargar': 'Download',
      'Completar datos': 'Complete data',
      'Sin conexión': 'No connection',
      'Verifica tu conexión a internet.': 'Check your internet connection.',
      'Reintentar': 'Retry',
      'Cargando...': 'Loading...',
      'Términos y Condiciones': 'Terms and Conditions',
      '¡Bienvenido a SportsVision!': 'Welcome to SportsVision!',
      'Siguiente paso': 'Next step',
      'Mis Rutinas': 'My Routines',
      'Dirección': 'Address',
      'Teléfono': 'Phone',
      'Restablecer contraseña': 'Reset password',
      'Nueva contraseña': 'New password',
      'Acepto los términos': 'I accept the terms',
      'Aún no hay actividad': 'No activity yet',
      'Ver todo': 'See all',
      'Hoy': 'Today',
      'Ayer': 'Yesterday',

      // ── Unidades / palabras cortas (al final para no romper frases) ──
      'ejercicios': 'exercises',
      'ejercicio': 'exercise',
      'años': 'years',
      'desde': 'since',
      'Bajo': 'Low',
      'Sobre': 'Over',
      'Normal': 'Normal',
      'Nueva': 'New',
      'Iniciar': 'Start',
      'Diabetes': 'Diabetes',
      'Resistencia': 'Endurance',
      'Flexibilidad': 'Flexibility',
      'Rendimiento': 'Performance',
      'Hipertensión': 'Hypertension',
      'Auto': 'Auto',
    },

    pt: {
      // ── Login ──
      'INICIAR SESIÓN': 'ENTRAR',
      'Iniciar sesión': 'Entrar',
      'Usuario o Correo': 'Usuário ou E-mail',
      'Tu usuario o correo electrónico': 'Seu usuário ou e-mail',
      '¿Olvidaste tu contraseña?': 'Esqueceu sua senha?',
      'Tu contraseña': 'Sua senha',
      '¿No tienes cuenta?': 'Não tem uma conta?',
      'Regístrate': 'Cadastre-se',
      '← Volver al inicio': '← Voltar ao início',

      // ── Registro ──
      'CREAR CUENTA': 'CRIAR CONTA',
      'Crear cuenta': 'Criar conta',
      'Primero verificamos que el correo es tuyo.': 'Primeiro verificamos que o e-mail é seu.',
      'Te enviaremos un código de': 'Enviaremos um código de',
      'Correo electrónico': 'E-mail',
      'Enviar código de verificación': 'Enviar código de verificação',
      'Enviando...': 'Enviando...',
      '¿Ya tienes cuenta?': 'Já tem uma conta?',
      'Inicia sesión': 'Entrar',
      'Revisa tu correo': 'Verifique seu e-mail',
      'Enviamos un código de 6 dígitos a': 'Enviamos um código de 6 dígitos para',
      'Verificar código': 'Verificar código',
      'Reenviar código': 'Reenviar código',
      '← Cambiar correo': '← Mudar e-mail',
      'Verificando...': 'Verificando...',
      'Nombre de usuario': 'Nome de usuário',
      'Contraseña': 'Senha',
      'Repite tu contraseña': 'Repita sua senha',
      'Siguiente': 'Próximo',
      'Cuéntanos sobre ti': 'Conta-nos sobre você',
      'Tu objetivo': 'Seu objetivo',
      'Bajar de peso': 'Perder peso',
      'Mantener peso': 'Manter peso',
      'Ganar músculo': 'Ganhar músculo',
      'Resistencia': 'Resistência',
      'Flexibilidad': 'Flexibilidade',
      'Rendimiento': 'Desempenho',
      'No tengo ninguna limitación': 'Não tenho nenhuma limitação',
      'Lesión de rodilla': 'Lesão no joelho',
      'Lesión de espalda': 'Lesão nas costas',
      'Lesión de hombro': 'Lesão no ombro',
      'Completar registro': 'Completar cadastro',

      // ── Dashboard ──
      'BIENVENIDO DE VUELTA': 'BEM-VINDO DE VOLTA',
      'Bienvenido de vuelta': 'Bem-vindo de volta',
      '¿Con qué iniciamos hoy?': 'Com o que começamos hoje?',
      'ENTRENAMIENTOS': 'TREINOS',
      'RUTINAS': 'ROTINAS',
      'SERIES COMPLETADAS': 'SÉRIES CONCLUÍDAS',
      'KG LEVANTADOS': 'KG LEVANTADOS',
      'Nueva Rutina': 'Nova Rotina',
      'Crea tu propia rutina': 'Crie sua própria rotina',
      'Plan Semanal': 'Plano Semanal',
      'Organiza tu semana': 'Organize sua semana',
      'Historial de entrenamientos': 'Histórico de treinos',
      'Calculadoras fitness': 'Calculadoras fitness',
      'TUS RUTINAS': 'SUAS ROTINAS',
      'Tus rutinas': 'Suas rotinas',
      'Aún no tienes rutinas guardadas.': 'Você ainda não tem rotinas salvas.',
      'Crear primera rutina': 'Criar primeira rotina',

      // ── Perfil ──
      'Editar perfil': 'Editar perfil',
      'Datos personales': 'Dados pessoais',
      'Actualizar datos': 'Atualizar dados',
      'Actividad reciente': 'Atividade recente',
      'Aún no hay entrenamientos registrados': 'Ainda não há treinos registrados',
      'Foto de perfil': 'Foto de perfil',

      // ── Navegação ──
      'Progreso': 'Progresso',
      'Herramientas': 'Ferramentas',
      'Mis Dietas': 'Minhas Dietas',
      'Mi Perfil': 'Meu Perfil',
      'Cerrar Sesión': 'Sair',
      'Ser profesional': 'Tornar-se Pro',
      'Privacidad': 'Privacidade',

      // ── Treino ──
      'Finalizar entrenamiento': 'Finalizar treino',
      'Siguiente ejercicio': 'Próximo exercício',
      'Agregar serie': 'Adicionar série',
      'Finalizar': 'Finalizar',
      'Descanso': 'Descanso',
      'Continuar': 'Continuar',
      'Saltar': 'Pular',
      'SERIE': 'SÉRIE',

      // ── Exercícios ──
      'Buscar ejercicio...': 'Buscar exercício...',
      'Agregar ejercicio': 'Adicionar exercício',
      'Todos los ejercicios': 'Todos os exercícios',
      'Guardar rutina': 'Salvar rotina',
      'Músculos': 'Músculos',
      'Limpiar': 'Limpar',

      // ── Plano semanal ──
      'PLAN SEMANAL': 'PLANO SEMANAL',
      'Lunes': 'Segunda',
      'Martes': 'Terça',
      'Miércoles': 'Quarta',
      'Jueves': 'Quinta',
      'Viernes': 'Sexta',
      'Sábado': 'Sábado',
      'Domingo': 'Domingo',

      // ── Geral ──
      'GUARDAR CAMBIOS': 'SALVAR ALTERAÇÕES',
      'Guardar cambios': 'Salvar alterações',
      'Guardar': 'Salvar',
      'Cancelar': 'Cancelar',
      'Volver': 'Voltar',
      'Eliminar': 'Excluir',
      'Editar': 'Editar',
      'Términos y Condiciones': 'Termos e Condições',
      'Mis Rutinas': 'Minhas Rotinas',
      'ejercicios': 'exercícios',
      'ejercicio': 'exercício',
      'años': 'anos',
      'Iniciar': 'Iniciar',
      'Nueva': 'Nova',
    },

    fr: {
      // ── Connexion ──
      'INICIAR SESIÓN': 'SE CONNECTER',
      'Iniciar sesión': 'Se connecter',
      'Usuario o Correo': 'Identifiant ou E-mail',
      '¿Olvidaste tu contraseña?': 'Mot de passe oublié ?',
      '¿No tienes cuenta?': 'Pas encore de compte ?',
      'Regístrate': "S'inscrire",
      '← Volver al inicio': "← Retour à l'accueil",

      // ── Inscription ──
      'CREAR CUENTA': 'CRÉER UN COMPTE',
      'Crear cuenta': 'Créer un compte',
      'Primero verificamos que el correo es tuyo.': 'Nous vérifions que cet e-mail vous appartient.',
      'Enviar código de verificación': 'Envoyer le code de vérification',
      'Enviando...': 'Envoi en cours...',
      '¿Ya tienes cuenta?': 'Déjà un compte ?',
      'Inicia sesión': 'Se connecter',
      'Revisa tu correo': 'Vérifiez votre e-mail',
      'Verificar código': 'Vérifier le code',
      'Reenviar código': 'Renvoyer le code',
      'Nombre de usuario': "Nom d'utilisateur",
      'Contraseña': 'Mot de passe',
      'Siguiente': 'Suivant',
      'Bajar de peso': 'Perdre du poids',
      'Ganar músculo': 'Prendre de la masse',
      'Completar registro': "Terminer l'inscription",

      // ── Dashboard ──
      'BIENVENIDO DE VUELTA': 'BON RETOUR',
      'Bienvenido de vuelta': 'Bon retour',
      '¿Con qué iniciamos hoy?': "Qu'est-ce qu'on commence aujourd'hui ?",
      'ENTRENAMIENTOS': 'ENTRAÎNEMENTS',
      'RUTINAS': 'ROUTINES',
      'Nueva Rutina': 'Nouvelle Routine',
      'Crea tu propia rutina': 'Créez votre propre routine',
      'Plan Semanal': 'Plan Hebdomadaire',
      'Organiza tu semana': 'Organisez votre semaine',
      'Historial de entrenamientos': "Historique d'entraînements",
      'TUS RUTINAS': 'VOS ROUTINES',
      'Aún no tienes rutinas guardadas.': "Vous n'avez pas encore de routines sauvegardées.",

      // ── Navigation ──
      'Progreso': 'Progrès',
      'Herramientas': 'Outils',
      'Mis Dietas': 'Mes Régimes',
      'Mi Perfil': 'Mon Profil',
      'Cerrar Sesión': 'Déconnexion',
      'Ser profesional': 'Devenir Pro',

      // ── Entraînement ──
      'Finalizar entrenamiento': "Terminer l'entraînement",
      'Siguiente ejercicio': 'Exercice suivant',
      'Agregar serie': 'Ajouter une série',
      'Finalizar': 'Terminer',
      'Descanso': 'Repos',
      'Continuar': 'Continuer',
      'Saltar': 'Passer',
      'SERIE': 'SÉRIE',

      // ── Plan hebdomadaire ──
      'PLAN SEMANAL': 'PLAN HEBDOMADAIRE',
      'Lunes': 'Lundi',
      'Martes': 'Mardi',
      'Miércoles': 'Mercredi',
      'Jueves': 'Jeudi',
      'Viernes': 'Vendredi',
      'Sábado': 'Samedi',
      'Domingo': 'Dimanche',

      // ── Général ──
      'Guardar': 'Enregistrer',
      'Guardar cambios': 'Enregistrer les modifications',
      'Cancelar': 'Annuler',
      'Volver': 'Retour',
      'Eliminar': 'Supprimer',
      'Editar': 'Modifier',
      'Términos y Condiciones': 'Conditions générales',
      'ejercicios': 'exercices',
      'ejercicio': 'exercice',
      'Iniciar': 'Démarrer',
      'Nueva': 'Nouveau',
    }
  };

  var dict = T[lang];
  if (!dict) return;

  // Sort keys by length descending so longer phrases match before shorter words
  var keys = Object.keys(dict).sort(function (a, b) { return b.length - a.length; });

  function translateText(text) {
    var result = text;
    for (var i = 0; i < keys.length; i++) {
      if (result.indexOf(keys[i]) !== -1) {
        result = result.split(keys[i]).join(dict[keys[i]]);
      }
    }
    return result;
  }

  function translateNode(node) {
    if (node.nodeType === 3) {
      var t = translateText(node.nodeValue);
      if (t !== node.nodeValue) node.nodeValue = t;
    } else if (node.nodeType === 1) {
      var tag = node.tagName;
      if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT') return;
      if (tag === 'INPUT' && node.type === 'hidden') return;
      if (node.placeholder) node.placeholder = translateText(node.placeholder);
      if (node.title) node.title = translateText(node.title);
      if (node.getAttribute && node.getAttribute('aria-label')) {
        node.setAttribute('aria-label', translateText(node.getAttribute('aria-label')));
      }
      for (var i = 0; i < node.childNodes.length; i++) {
        translateNode(node.childNodes[i]);
      }
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    translateNode(document.body);
    document.documentElement.lang = lang;
  });
})();
