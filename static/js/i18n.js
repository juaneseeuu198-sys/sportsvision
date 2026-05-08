/**
 * SportsVision — Auto-translation based on OS/browser language
 * Detects navigator.language and replaces Spanish text with the correct language
 */
(function () {
  var lang = (navigator.language || navigator.userLanguage || 'es').substring(0, 2).toLowerCase();
  if (lang === 'es') return; // Spanish is the default, nothing to do

  var T = {
    en: {
      // Navigation
      'Home': 'Home',
      'Nueva Rutina': 'New Routine',
      'Progreso': 'Progress',
      'Plan Semanal': 'Weekly Plan',
      'Herramientas': 'Tools',
      'Mis Dietas': 'My Diets',
      'Mi Perfil': 'My Profile',
      'Cerrar Sesión': 'Log Out',
      'Ser profesional': 'Become a Pro',
      'Privacidad': 'Privacy',
      'Panel Pro': 'Pro Panel',
      // Auth
      'Crear cuenta': 'Create account',
      'CREAR CUENTA': 'CREATE ACCOUNT',
      'Iniciar sesión': 'Log in',
      'INICIAR SESIÓN': 'LOG IN',
      'Registrarse': 'Sign up',
      'Correo electrónico': 'Email',
      'CORREO ELECTRÓNICO': 'EMAIL',
      'Contraseña': 'Password',
      'CONTRASEÑA': 'PASSWORD',
      'Entrar': 'Enter',
      '¿Ya tienes cuenta?': 'Already have an account?',
      'Inicia sesión': 'Log in',
      '¿No tienes cuenta?': "Don't have an account?",
      'Primero verificamos que el correo es tuyo.': 'First we verify that the email is yours.',
      'Te enviaremos un código de': "We'll send you a code of",
      'dígitos': 'digits',
      'Enviar código de verificación': 'Send verification code',
      'Código de verificación': 'Verification code',
      'Verificar': 'Verify',
      'Reenviar código': 'Resend code',
      'Nombre de usuario': 'Username',
      'NOMBRE DE USUARIO': 'USERNAME',
      'Nombre': 'Name',
      'Edad': 'Age',
      'Peso': 'Weight',
      'Altura': 'Height',
      'Objetivo': 'Goal',
      'Nivel': 'Level',
      'Completar registro': 'Complete registration',
      // Dashboard
      'BIENVENIDO DE VUELTA': 'WELCOME BACK',
      '¿Con qué iniciamos hoy?': "What are we starting today?",
      'ENTRENAMIENTOS': 'WORKOUTS',
      'RUTINAS': 'ROUTINES',
      'SERIES COMPLETADAS': 'SETS COMPLETED',
      'KG LEVANTADOS': 'KG LIFTED',
      'Crea tu propia rutina': 'Create your own routine',
      'Organiza tu semana': 'Organize your week',
      'Tu progreso': 'Your progress',
      'Historial de entrenamientos': 'Training history',
      'Calculadoras fitness': 'Fitness calculators',
      'TUS RUTINAS': 'YOUR ROUTINES',
      'Tus rutinas': 'Your routines',
      'Iniciar': 'Start',
      'Nueva': 'New',
      'Aún no tienes rutinas guardadas.': "You don't have any saved routines yet.",
      'Crear primera rutina': 'Create first routine',
      // Profile
      'Editar perfil': 'Edit profile',
      'EDITAR PERFIL': 'EDIT PROFILE',
      'Actualizar datos': 'Update data',
      'ACTUALIZAR DATOS': 'UPDATE DATA',
      'Guardar cambios': 'Save changes',
      'GUARDAR CAMBIOS': 'SAVE CHANGES',
      'Foto de perfil': 'Profile photo',
      'Elegir foto': 'Choose photo',
      'Guardar esta foto': 'Save this photo',
      'Datos personales': 'Personal data',
      'DATOS PERSONALES': 'PERSONAL DATA',
      'Actividad Reciente': 'Recent Activity',
      'ACTIVIDAD RECIENTE': 'RECENT ACTIVITY',
      'Aún no hay entrenamientos registrados': 'No workouts recorded yet',
      'Completa tu primer entrenamiento para ver tu historial': 'Complete your first workout to see your history',
      'años': 'years',
      'desde': 'since',
      'Completar datos': 'Complete data',
      'Dirección': 'Address',
      'Teléfono': 'Phone',
      // Workout
      'Finalizar': 'Finish',
      'Guía': 'Guide',
      'Saltar': 'Skip',
      'Terminar': 'End',
      'SERIE': 'SET',
      'ANTERIOR': 'PREVIOUS',
      'Agregar serie': 'Add set',
      'Siguiente ejercicio': 'Next exercise',
      'Finalizar entrenamiento': 'Finish workout',
      'Descanso': 'Rest',
      'Prepárate para la siguiente serie': 'Get ready for the next set',
      'Continuar': 'Continue',
      // Exercise selection
      'Agregar ejercicio': 'Add exercise',
      'Crear': 'Create',
      'Buscar ejercicio...': 'Search exercise...',
      'Músculos': 'Muscles',
      'Equipo': 'Equipment',
      'Recientes': 'Recent',
      'Todos los ejercicios': 'All exercises',
      'Guardar rutina': 'Save routine',
      'Nombre de la rutina...': 'Routine name...',
      'Grupo Muscular': 'Muscle Group',
      'Equipamiento': 'Equipment',
      'Limpiar': 'Clear',
      'Sin resultados para este filtro.': 'No results for this filter.',
      // Plan semanal
      'Plan Semanal': 'Weekly Plan',
      'PLAN SEMANAL': 'WEEKLY PLAN',
      'Lunes': 'Monday',
      'Martes': 'Tuesday',
      'Miércoles': 'Wednesday',
      'Jueves': 'Thursday',
      'Viernes': 'Friday',
      'Sábado': 'Saturday',
      'Domingo': 'Sunday',
      'Descanso': 'Rest',
      'Sin rutina': 'No routine',
      // General
      'Guardar': 'Save',
      'Cancelar': 'Cancel',
      'Confirmar': 'Confirm',
      'Volver': 'Back',
      'Eliminar': 'Delete',
      'Sin conexión': 'No connection',
      'Verifica tu conexión a internet.': 'Check your internet connection.',
      'Reintentar': 'Retry',
      'Cargando...': 'Loading...',
      'Error': 'Error',
      // Herramientas
      'Calculadora de Calorías': 'Calorie Calculator',
      'Calculadora de IMC': 'BMI Calculator',
      'Plan Nutricional': 'Nutritional Plan',
      'Mis Dietas': 'My Diets',
      // Steps
      '¿Programar rutina?': 'Schedule routine?',
      'Elige el día o guarda sin programar.': 'Choose a day or save without scheduling.',
      'Sin programar': 'Without scheduling',
      'Programar': 'Schedule',
      // Bienvenido
      '¡Bienvenido a SportsVision!': 'Welcome to SportsVision!',
      'Siguiente paso': 'Next step',
      // Terminos
      'Términos y Condiciones': 'Terms and Conditions',
      'Acepto los términos': 'I accept the terms',
      // Mis rutinas
      'Mis Rutinas': 'My Routines',
      'ejercicios': 'exercises',
      'Auto': 'Auto',
    },
    pt: {
      'Home': 'Início',
      'Nueva Rutina': 'Nova Rotina',
      'Progreso': 'Progresso',
      'Plan Semanal': 'Plano Semanal',
      'Herramientas': 'Ferramentas',
      'Mis Dietas': 'Minhas Dietas',
      'Mi Perfil': 'Meu Perfil',
      'Cerrar Sesión': 'Sair',
      'Ser profesional': 'Tornar-se Pro',
      'Privacidad': 'Privacidade',
      'Crear cuenta': 'Criar conta',
      'CREAR CUENTA': 'CRIAR CONTA',
      'Iniciar sesión': 'Entrar',
      'INICIAR SESIÓN': 'ENTRAR',
      'Correo electrónico': 'E-mail',
      'CORREO ELECTRÓNICO': 'E-MAIL',
      'Contraseña': 'Senha',
      'CONTRASEÑA': 'SENHA',
      'Entrar': 'Entrar',
      'Enviar código de verificación': 'Enviar código de verificação',
      'Verificar': 'Verificar',
      'Nombre': 'Nome',
      'Edad': 'Idade',
      'Peso': 'Peso',
      'Altura': 'Altura',
      'BIENVENIDO DE VUELTA': 'BEM-VINDO DE VOLTA',
      '¿Con qué iniciamos hoy?': 'Com o que começamos hoje?',
      'ENTRENAMIENTOS': 'TREINOS',
      'RUTINAS': 'ROTINAS',
      'SERIES COMPLETADAS': 'SÉRIES CONCLUÍDAS',
      'KG LEVANTADOS': 'KG LEVANTADOS',
      'Crea tu propia rutina': 'Crie sua própria rotina',
      'Organiza tu semana': 'Organize sua semana',
      'TUS RUTINAS': 'SUAS ROTINAS',
      'Iniciar': 'Iniciar',
      'Nueva': 'Nova',
      'Editar perfil': 'Editar perfil',
      'Guardar cambios': 'Salvar alterações',
      'Finalizar': 'Finalizar',
      'Saltar': 'Pular',
      'Terminar': 'Encerrar',
      'SERIE': 'SÉRIE',
      'ANTERIOR': 'ANTERIOR',
      'Agregar serie': 'Adicionar série',
      'Siguiente ejercicio': 'Próximo exercício',
      'Finalizar entrenamiento': 'Finalizar treino',
      'Descanso': 'Descanso',
      'Continuar': 'Continuar',
      'Agregar ejercicio': 'Adicionar exercício',
      'Músculos': 'Músculos',
      'Equipo': 'Equipamento',
      'Recientes': 'Recentes',
      'Todos los ejercicios': 'Todos os exercícios',
      'Guardar rutina': 'Salvar rotina',
      'Limpiar': 'Limpar',
      'Lunes': 'Segunda',
      'Martes': 'Terça',
      'Miércoles': 'Quarta',
      'Jueves': 'Quinta',
      'Viernes': 'Sexta',
      'Sábado': 'Sábado',
      'Domingo': 'Domingo',
      'Guardar': 'Salvar',
      'Cancelar': 'Cancelar',
      'Volver': 'Voltar',
      'Eliminar': 'Excluir',
      'años': 'anos',
      'desde': 'desde',
      'ejercicios': 'exercícios',
    },
    fr: {
      'Home': 'Accueil',
      'Nueva Rutina': 'Nouvelle Routine',
      'Progreso': 'Progrès',
      'Plan Semanal': 'Plan Hebdomadaire',
      'Herramientas': 'Outils',
      'Mis Dietas': 'Mes Régimes',
      'Mi Perfil': 'Mon Profil',
      'Cerrar Sesión': 'Déconnexion',
      'Crear cuenta': 'Créer un compte',
      'CREAR CUENTA': 'CRÉER UN COMPTE',
      'Iniciar sesión': 'Se connecter',
      'Correo electrónico': 'Adresse e-mail',
      'Contraseña': 'Mot de passe',
      'Entrar': 'Entrer',
      'Enviar código de verificación': 'Envoyer le code de vérification',
      'Verificar': 'Vérifier',
      'Edad': 'Âge',
      'Peso': 'Poids',
      'Altura': 'Taille',
      'BIENVENIDO DE VUELTA': 'BON RETOUR',
      'ENTRENAMIENTOS': 'ENTRAÎNEMENTS',
      'RUTINAS': 'ROUTINES',
      'Iniciar': 'Démarrer',
      'Finalizar': 'Terminer',
      'Siguiente ejercicio': 'Exercice suivant',
      'Guardar': 'Enregistrer',
      'Cancelar': 'Annuler',
      'Volver': 'Retour',
      'Lunes': 'Lundi',
      'Martes': 'Mardi',
      'Miércoles': 'Mercredi',
      'Jueves': 'Jeudi',
      'Viernes': 'Vendredi',
      'Sábado': 'Samedi',
      'Domingo': 'Dimanche',
    }
  };

  var dict = T[lang];
  if (!dict) return;

  function translateNode(node) {
    if (node.nodeType === 3) { // Text node
      var text = node.nodeValue.trim();
      if (text && dict[text]) {
        node.nodeValue = node.nodeValue.replace(text, dict[text]);
      }
    } else if (node.nodeType === 1) {
      // Translate placeholder attributes
      if (node.placeholder && dict[node.placeholder]) {
        node.placeholder = dict[node.placeholder];
      }
      // Translate title attributes
      if (node.title && dict[node.title]) {
        node.title = dict[node.title];
      }
      // Skip script, style, input[type=hidden]
      var tag = node.tagName;
      if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT') return;
      if (tag === 'INPUT' && node.type === 'hidden') return;
      node.childNodes.forEach(translateNode);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    translateNode(document.body);

    // Also set html lang attribute
    document.documentElement.lang = lang;
  });
})();
