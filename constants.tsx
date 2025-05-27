import { ChannelUsername } from './types';

export const DEFAULT_CHANNELS: ChannelUsername[] = [
  // абсолютный топ
  'seeallochnaya',
  'denissexy',
  'data_secrets',

  // умные чувачки, часть из которых знаю лично, с частью из которых общался онлайн, а часть не знаю, но тоже найс - бывают, пишут о том о сем, о мл, о ллм, о жизни
  'tsingular',
  'cryptovalerii',
  'new_yorko_times',
  'sinecor',
  'doomgrad',
  'cryptoEssay',
  'boris_again',
  'mashkka_ds',
  'gigatrash',
  'max_about_ai',
  'singularityfm',
  'blog_toxa',

  // обычно кликбейт, но все равно бывает найс
  'whackdoor',
  'exploitex',
  'ppprompt',
  'xor_journal',
  'singularityp0int',

  // технически хардкорные, если хочется быть в курсе всяких архитектур нейросетей, или делать вид, что в курсе)
  'rybolos_channel',
  'senior_augur',
  'gonzo_ML',
  'data_analysis_ml',
  'nlpwanderer',
  'complete_ai',
  'AGI_and_RL',
  'dealerAI',
  'zheltyi_ai',
  'vikhrlabs',
  'epsiloncorrect',

  // ии-видео, фото, оживление, искусство
  'cgevent',
  'Psy_Eyes',
  'GreenNeuralRobots',
  'neuro_code',

  // приколюшки
  'lovedeathtransformers',
  'NeuralShit',

  // о том о сем, всякие новости (вот тут часто всякие дайджесты новостей ии за неделю)
  'ai4telegram',
  'ai_newz',
  'ai_machinelearning_big_data',
  'addmeto',

  // бизнес-движухи
  'aioftheday',
  'daily10',
  'its_capitan',
  'bogdanisssimo',

  // работа (помимо хх, getmatch, facancy)
  'odsjobs',
  'data_secrets_career',

  // митапы, вебинары
  'AI_meetups',
  'datafest',
  'sb_ai_lab'
];

export const AppTitle = "Агрегатор постов Telegram";

export const IconTelegram = (
  <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" strokeWidth={1.5} stroke="none" className="w-6 h-6">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.81L15.11 14.3c-.19.59-.56.72-1.01.45l-2.76-2.03-1.32.98c-.16.12-.29.21-.5.21-.24 0-.38-.09-.44-.3l-.69-2.26-2.39-.75c-.53-.17-.53-.53.11-.8l10.02-3.91c.49-.19.95.12.79.76z"/>
  </svg>
);

export const IconDownload = (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
  </svg>
);

export const IconRefresh = (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
  </svg>
);

export const IconLightBulb = (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.355a7.5 7.5 0 01-4.5 0m4.5 0v.75A2.25 2.25 0 0113.5 21h-3a2.25 2.25 0 01-2.25-2.25V18m7.5-7.5h2.25m-15 0h2.25m5.25 0h2.25m-2.25 0a3 3 0 01-3 3h-1.5a3 3 0 01-3-3H6M7.5 18A2.25 2.25 0 005.25 6H10" />
    </svg>
);