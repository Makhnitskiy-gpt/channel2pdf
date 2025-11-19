/**
 * Channel2PDF Translations Dictionary
 * Language support: RU (Russian) / EN (English)
 */

const translations = {
  ru: {
    // Header & Branding
    brandName: 'Channel2PDF',
    heroTitle: 'Выгрузка постов Telegram-каналов в PDF',
    heroSubtitle: 'Сохраните все посты публичного Telegram-канала за выбранный период в одном PDF — для отчётов, архива и аналитики',

    // Language Switcher
    langRu: 'RU',
    langEn: 'EN',

    // Demo Mode Alert
    demoModeTitle: 'Демо-режим:',
    demoModeText: 'Приложение работает с тестовыми данными без подключения к Telegram API. Для работы с реальными каналами установите переменные окружения ENV=production и TELEGRAM_API_ID, TELEGRAM_API_HASH.',

    // Error Alert
    errorTitle: 'Ошибка:',

    // Success State
    successTitle: 'PDF-отчёт успешно создан!',
    successChannel: 'Канал',
    successPeriod: 'Период',
    successSorting: 'Сортировка',
    downloadPdfBtn: 'Скачать PDF',
    createNewReportBtn: 'Создать новый отчёт',

    // Form Fields
    formChannelLabel: 'Канал',
    formChannelPlaceholder: '@channelname или https://t.me/channelname',
    formChannelHint: 'Например: @durov или https://t.me/durov',
    formChannelHintDemo: 'В демо-режиме используется тестовый канал',

    formDateFromLabel: 'Дата начала',
    formDateToLabel: 'Дата окончания',

    formSortTypeLabel: 'Тип сортировки',
    formSortByDate: 'По дате',
    formSortByReactions: 'По количеству реакций',
    formSortByViews: 'По количеству просмотров',

    formDirectionLabel: 'Направление',
    formDirectionDesc: 'По убыванию',
    formDirectionAsc: 'По возрастанию',

    formFilenameLabel: 'Имя PDF-файла (опционально)',
    formFilenamePlaceholder: 'report.pdf',
    formFilenameHint: 'Если не указать, имя будет сгенерировано автоматически',

    formSubmitBtn: 'Сформировать PDF',

    // How It Works Section
    howItWorksTitle: 'Как работает выгрузка',
    howItWorksStep1: 'Вставьте ссылку на публичный Telegram-канал или его @username.',
    howItWorksStep2: 'Укажите период — какие посты нужно выгрузить.',
    howItWorksStep3: 'Выберите порядок: сначала старые или новые.',
    howItWorksStep4: 'Нажмите «Сформировать PDF».',
    howItWorksStep5: 'Сервис соберёт все посты за выбранный период и объединит их в один документ.',
    howItWorksNote: 'Примечание:',
    howItWorksNoteText: 'Работает только с публичными каналами, авторизация не требуется.',

    // About Section
    aboutTitle: 'О сервисе Channel2PDF',
    aboutParagraph1: 'Channel2PDF — это удобный сервис для выгрузки всех постов из публичных Telegram-каналов в формат PDF. Он помогает быстро собрать историю канала или выбрать нужный период — например, для аналитики, подготовки отчётов, архивирования или передачи материалов клиенту. Инструмент автоматически загружает сообщения, сохраняет текст, ссылки, базовые реакции и просмотры, а затем формирует единый PDF-файл, который удобно изучать, просматривать офлайн или прикладывать к документации.',
    aboutParagraph2: 'Сервис работает без авторизации: достаточно вставить ссылку на публичный Telegram-канал, выбрать диапазон дат и нажать кнопку. PDF-архив формируется за несколько секунд, после чего его можно скачать и использовать для работы с контентом, анализа активности канала или сохранения важных публикаций.',
    aboutParagraph3: 'Решение подходит для маркетологов, аналитиков, исследователей, редакторов, агентств и всех, кому необходимо выгрузить историю Telegram-канала в удобном формате.',

    // FAQ Section
    faqTitle: 'Частые вопросы',
    faqQuestion1: 'Как выгрузить историю Telegram-канала?',
    faqAnswer1: 'Вставьте ссылку, выберите период и нажмите «Сформировать PDF».',
    faqQuestion2: 'Можно ли скачать канал полностью?',
    faqAnswer2: 'Да, если канал публичный.',
    faqQuestion3: 'Что сохраняется в PDF?',
    faqAnswer3: 'Текст постов, ссылки, реакции, просмотры.',
    faqQuestion4: 'Нужна ли авторизация?',
    faqAnswer4: 'Нет, сервис работает открыто.',
    faqQuestion5: 'Можно ли использовать PDF для отчётов?',
    faqAnswer5: 'Да, формат подходит для аналитики, архива и передачи клиентам.',

    // Footer
    footerStatusLink: 'Статус сервиса',
    footerGithubLink: 'GitHub'
  },

  en: {
    // Header & Branding
    brandName: 'Channel2PDF',
    heroTitle: 'Export Telegram Channel Posts to PDF',
    heroSubtitle: 'Save all posts from a public Telegram channel for a selected period in one PDF — for reports, archiving, and analytics',

    // Language Switcher
    langRu: 'RU',
    langEn: 'EN',

    // Demo Mode Alert
    demoModeTitle: 'Demo Mode:',
    demoModeText: 'The application is running with test data without connecting to the Telegram API. To work with real channels, set the environment variables ENV=production and TELEGRAM_API_ID, TELEGRAM_API_HASH.',

    // Error Alert
    errorTitle: 'Error:',

    // Success State
    successTitle: 'PDF Report Successfully Created!',
    successChannel: 'Channel',
    successPeriod: 'Period',
    successSorting: 'Sorting',
    downloadPdfBtn: 'Download PDF',
    createNewReportBtn: 'Create New Report',

    // Form Fields
    formChannelLabel: 'Channel',
    formChannelPlaceholder: '@channelname or https://t.me/channelname',
    formChannelHint: 'Example: @durov or https://t.me/durov',
    formChannelHintDemo: 'Demo mode uses a test channel',

    formDateFromLabel: 'Start Date',
    formDateToLabel: 'End Date',

    formSortTypeLabel: 'Sort Type',
    formSortByDate: 'By Date',
    formSortByReactions: 'By Reactions Count',
    formSortByViews: 'By Views Count',

    formDirectionLabel: 'Direction',
    formDirectionDesc: 'Descending',
    formDirectionAsc: 'Ascending',

    formFilenameLabel: 'PDF Filename (optional)',
    formFilenamePlaceholder: 'report.pdf',
    formFilenameHint: 'If not specified, the name will be generated automatically',

    formSubmitBtn: 'Generate PDF',

    // How It Works Section
    howItWorksTitle: 'How Export Works',
    howItWorksStep1: 'Paste a link to a public Telegram channel or its @username.',
    howItWorksStep2: 'Specify the period — which posts to export.',
    howItWorksStep3: 'Choose the order: oldest or newest first.',
    howItWorksStep4: 'Click "Generate PDF".',
    howItWorksStep5: 'The service will collect all posts for the selected period and combine them into one document.',
    howItWorksNote: 'Note:',
    howItWorksNoteText: 'Works only with public channels, no authorization required.',

    // About Section
    aboutTitle: 'About Channel2PDF Service',
    aboutParagraph1: 'Channel2PDF is a convenient service for exporting all posts from public Telegram channels to PDF format. It helps you quickly gather channel history or select a specific period — for example, for analytics, report preparation, archiving, or delivering materials to clients. The tool automatically downloads messages, saves text, links, basic reactions and views, and then generates a single PDF file that is easy to study, view offline, or attach to documentation.',
    aboutParagraph2: 'The service works without authorization: simply paste a link to a public Telegram channel, select a date range, and click the button. The PDF archive is generated in a few seconds, after which you can download and use it for working with content, analyzing channel activity, or saving important publications.',
    aboutParagraph3: 'The solution is suitable for marketers, analysts, researchers, editors, agencies, and anyone who needs to export Telegram channel history in a convenient format.',

    // FAQ Section
    faqTitle: 'Frequently Asked Questions',
    faqQuestion1: 'How to export Telegram channel history?',
    faqAnswer1: 'Paste the link, select the period, and click "Generate PDF".',
    faqQuestion2: 'Can I download the entire channel?',
    faqAnswer2: 'Yes, if the channel is public.',
    faqQuestion3: 'What is saved in the PDF?',
    faqAnswer3: 'Post text, links, reactions, views.',
    faqQuestion4: 'Is authorization required?',
    faqAnswer4: 'No, the service works openly.',
    faqQuestion5: 'Can I use the PDF for reports?',
    faqAnswer5: 'Yes, the format is suitable for analytics, archiving, and client delivery.',

    // Footer
    footerStatusLink: 'Service Status',
    footerGithubLink: 'GitHub'
  }
};

// Initialize language from localStorage or default to Russian
let currentLanguage = localStorage.getItem('channel2pdf_language') || 'ru';

/**
 * Get translation by key
 */
function t(key) {
  return translations[currentLanguage][key] || key;
}

/**
 * Switch language and update UI
 */
function switchLanguage(lang) {
  if (lang !== 'ru' && lang !== 'en') {
    console.error('Invalid language:', lang);
    return;
  }

  currentLanguage = lang;
  localStorage.setItem('channel2pdf_language', lang);
  updateUI();
  updateLanguageSwitcher();
}

/**
 * Update all translatable elements in the UI
 */
function updateUI() {
  // Update all elements with data-i18n attribute
  document.querySelectorAll('[data-i18n]').forEach(element => {
    const key = element.getAttribute('data-i18n');
    const translation = t(key);

    // Update text content or placeholder based on element type
    if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
      if (element.hasAttribute('placeholder')) {
        element.placeholder = translation;
      }
    } else {
      element.textContent = translation;
    }
  });

  // Update all elements with data-i18n-html attribute (for HTML content)
  document.querySelectorAll('[data-i18n-html]').forEach(element => {
    const key = element.getAttribute('data-i18n-html');
    element.innerHTML = t(key);
  });

  // Update HTML lang attribute
  document.documentElement.lang = currentLanguage;
}

/**
 * Update language switcher button states
 */
function updateLanguageSwitcher() {
  document.querySelectorAll('.lang-switch-btn').forEach(btn => {
    if (btn.dataset.lang === currentLanguage) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}

/**
 * Initialize translations on page load
 */
document.addEventListener('DOMContentLoaded', function() {
  updateUI();
  updateLanguageSwitcher();

  // Setup language switcher buttons
  document.querySelectorAll('.lang-switch-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      switchLanguage(this.dataset.lang);
    });
  });
});
