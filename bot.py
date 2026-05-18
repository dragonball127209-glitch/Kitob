import os
import logging
import random
from telegram import Update, Poll
from telegram.ext import (
    Application, CommandHandler, PollAnswerHandler,
    ContextTypes, ConversationHandler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ─── SAVOLLAR BAZASI ────────────────────────────────────────────────────────
QUESTIONS = [
    {"q": '2002-yilda AQSHda, "Butun jahon xristianligi tendensiyasi" kitobi nashr etildi. Unda xristianlik 2025-yilgacha erishish lozim bo\'lgan nechta asosiy maqsad sanab o\'tilgan?', "opts": ["12 ta", "2 ta", "16 ta", "8 ta"], "ans": 3},
    {"q": 'Musulmonlar etiqodicha, Alloh tomonidan Dovud payg\'ambarga yuborilgan muqaddas kitob?', "opts": ["Talmud", "Tavrot", "Zabur", "Injil"], "ans": 2},
    {"q": 'Islom dini Muhammad (s.a.v.) tomonidan qaysi yildan boshlab tashviqot qilingan?', "opts": ["570-yildan", "622-yildan", "632-yildan", "610-yildan"], "ans": 3},
    {"q": 'Xristianchilik dinining asosiy yo\'nalishlari qaysi?', "opts": ["Baptizm, protestantlik, fetishizm", "Katoliklik, pravoslavlik, protestantlik", "Lyuteranchilik, xinoyana, kalvinizm", "Totemizm, protestantchilik, xinduchilik"], "ans": 1},
    {"q": 'Qur\'onning yozma nusxasi qaysi xalifa davrida yozib tugatilgan?', "opts": ["Muhammad payg\'ambar davrida", "Abu Bakr Siddiq halifaligi davrida", "Usmon Ibn Affon halifaligi davrida", "Ali halifaligi davrida"], "ans": 2},
    {"q": 'Eng qadimgi jahon dini qaysi?', "opts": ["Buddizm", "Xristianlik", "Islom", "Iudaizm"], "ans": 3},
    {"q": 'Buddizm dini qachon paydo bo\'ldi?', "opts": ["Milodimizdan avv. V asrda", "Milodimizdan avv. VI–V asrda", "Milodimizning I asrida", "Milodimizgacha III asrda"], "ans": 1},
    {"q": 'Yahudiylik dinining muqaddas kitoblari qaysi javobda to\'g\'ri ko\'rsatilgan?', "opts": ["Tavrot, Talmud", "Tavrot, Injil", "Tavrot, Avesto", "Tavrot, Veda"], "ans": 0},
    {"q": 'Xristianlik dinidagi bo\'linish (Katolik va Pravoslav) qachon sodir bo\'ldi?', "opts": ["1054 y", "450 y", "325 y", "1526 y"], "ans": 0},
    {"q": '"ISHID fitnasi" kitobini kim yozdi?', "opts": ["Pavel Rozenko", "Evgeniy Sisoev", "Aydarbek Tulepov", "Yevgeniy Kasperski"], "ans": 3},
    {"q": 'Sahih hadislar to\'plamiga qaysi muhaddis asos solgan?', "opts": ["Najmiddin Kubro", "Bayhaqiy", "Imom al-Buxoriy", "Nishopuriy"], "ans": 2},
    {"q": 'Islom dinining sunniylik mazhablarini to\'g\'ri berilgan qatorni toping?', "opts": ["Hanafiylar, Molikiylar, Zaydiylar, Hanbaliylar", "Ismoiliylar, Hanbaliylar, Molikiylar, Ja\'fariylar", "Hanafiylar, Shofeiylar, Molikiylar, Hanbaliylar", "Molikiylar, Shofeiylar, Hanafiylar, Zaydiylar"], "ans": 2},
    {"q": 'O\'zbekistonda mavjud dinlarga qanday tamoyilga asosan munosabatda bo\'linadi?', "opts": ["Bag\'rikenglik, tolerantlikka asosan", "Dinlarning salohiyatiga asosan", "Dinlarning tarqalish me\'yorlariga asosan", "Ikkinchi javob to\'g\'ri"], "ans": 0},
    {"q": 'Daosizm asoschisi kim?', "opts": ["Pan Gu", "Lao Szi", "Kun Szi", "Shan Di"], "ans": 1},
    {"q": 'Yahudiylar uchun poklanish bayrami — qo\'chqor shoxidan yasalgan surnay chalish va cho\'ntaklarni qoqish bilan nishonlanadigan bayram?', "opts": ["Rosh-Hashona", "Shabuot", "Pasxa", "Purim"], "ans": 0},
    {"q": 'E\'tiqod qiluvchilarning miqdori jihatidan eng katta jahon dini qaysi?', "opts": ["Xristianlik", "Islom", "Xinduizm", "Buddizm"], "ans": 0},
    {"q": 'Dinning ijtimoiy vazifalari?', "opts": ["Kompensatorlik, regulyatorlik, ma\'naviylik", "Integratorlik, e\'tiqodlik, monoteistlik", "Legitimlovchilik, taskin beruvchilik, nominativlik", "Kompensatorlik, integratorlik, regulyatorlik"], "ans": 3},
    {"q": '"Butun jahon xristianligi tendensiyasi" kitobida missionerlar ulushini necha foizga ko\'tarish nazarda tutilgan?', "opts": ["33% ga", "73.1% ga", "20% ga", "40% ga"], "ans": 1},
    {"q": '930-yilda Makkaga bostirib kirib, Ka\'bani vayron qilib, Qora toshni Bahraynga olib ketgan ekstremistik oqim?', "opts": ["Azraqiylar", "Nurchilar", "Qarmatiylar", "Hashshoshiylar"], "ans": 2},
    {"q": '1980-yillardan boshlab "Ad da\'va" jurnali qaysi tashkilotning asosiy nashri?', "opts": ["IShID", "Al Ixvon al muslimun", "Boka Haram", "Al-Qoida"], "ans": 1},
    {"q": 'Xaniflar kimlar?', "opts": ["Payg\'ambarimiz safdoshlari", "Islom dinidan oldin arablar orasida yakka xudolik g\'oyasini targ\'ib qilgan ruhoniylar", "Islom dini yoyishga xizmat qilgan musulmonlar", "Sahobalar va tobeyinlar"], "ans": 1},
    {"q": '19 kunlik 19 oydan iborat diniy taqvim qabul qilingan; Umumjahon Adolat Uyi 9 kishidan tashkil topgan diniy harakat?', "opts": ["Qodiyoniylik", "Bahoiylik", "Aum-Sinrikyo", "Baxshillochilar"], "ans": 1},
    {"q": 'Avestoning to\'rtdan bir qismining eng nodir nusxasi qayerda saqlanmoqda?', "opts": ["Erondagi milliy tadqiqot institutida", "Kashmirdagi Kama Sharqshunoslik institutida", "Bombayda Kama Sharqshunoslik institutida", "Toshkentdagi Xalqaro islom akademiyasida"], "ans": 2},
    {"q": 'Animizm dinida nima ilohiylashtiriladi?', "opts": ["Kishining u dunyodagi hayoti", "Tan o\'lsa-da, jonning, ruhning o\'lmasligini", "Sehr-joduni", "Jonsiz buyumlar"], "ans": 1},
    {"q": '"Al-Adab al-mufrad" asarining muallifi?', "opts": ["Abu Homid G\'azzoliy", "Imom al-Buxoriy", "Zamaxshariy", "Moturidiy"], "ans": 1},
    {"q": 'Tasavvufdan saboq oluvchi shaxs…', "opts": ["Murid, solih, ahli dil, ahli hol, mutasavvuf", "Pir, avliyo, qutb, aqtob, abdol, abror, nujabo, nuqabo, siddiq", "Shayx, murshid, pir, eshon, xoja, mavlo, mavlono, maxdum", "Oshiq, faqir, haqir, darvesh, qalandar, zohid, orif, pir, devona"], "ans": 0},
    {"q": '«Vijdon erkinligi va diniy tashkilotlar to\'g\'risida»gi qonun (2021-yil, 5-iyul) necha moddadan iborat?', "opts": ["103 moddadan", "23 moddadan", "39 moddadan", "35 moddadan"], "ans": 2},
    {"q": '"Injil" so\'zi qanday ma\'noni anglatadi?', "opts": ["Arab «sahifalangan» ma\'nosini", "Arab «bayon qilish» ma\'nosini", "Yunon tilidan «kitob-uram» ma\'nosini", "Yunon tilidan «Xushxabar» degan ma\'noni"], "ans": 3},
    {"q": 'O\'rta asrlarda Markaziy Osiyoda tasavvuf ilmini rivojlantirishga hissa qo\'shgan allomalar?', "opts": ["Najmiddin Kubro, Arastu, Abu Nasr Farobiy", "Ahmad Yassaviy, Najmiddin Kubro, Bohouddin Naqshband", "Imom Buxoriy, Imom Dorimiy, Abdulholiq G\'ijduvoniy, Bayhaqiy", "A va B javoblar to\'g\'ri"], "ans": 1},
    {"q": '"Monoteizm"ning manosi nima?', "opts": ["Yakkaxudolik", "Ko\'pxudolik", "Ikkixudolik", "Diniy ta\'limot"], "ans": 0},
    {"q": 'Biron dinga ishongan fuqaroni majburan o\'z dinidan voz kechishga va o\'zga dinni qabul qilishga majbur qilish…', "opts": ["Prozelitizm", "Ligitimlik", "Tolerantlik", "Modernizm"], "ans": 0},
    {"q": '"Iqrornoma" asari muallifi…?', "opts": ["Lev Nikolayevich Tolstoy", "Nikolay Aleksandrovich Berdyayev", "Fyodor Dostayevskiy", "Nikola Albus"], "ans": 0},
    {"q": 'BMT Bosh Assambleyasining "Ma\'rifat va diniy bag\'rikenglik" rezolyutsiyasini qabul qilish tashabbuskor davlat?', "opts": ["AQSH", "Birlashgan Arab Amirligi", "Turkiya", "O\'zbekiston"], "ans": 3},
    {"q": 'Konfusiychilikning asoschisi kim?', "opts": ["Pan Gu", "Lao Szi", "Kun Szi", "Shan Di"], "ans": 2},
    {"q": 'Zardushtiylik dinining asosiy manbai va muqaddas kitobi qaysi?', "opts": ["Bibliya", "Tavrot", "Injil", "Avesto"], "ans": 3},
    {"q": 'Buddizmning asosiy yo\'nalishlari qaysilar?', "opts": ["Shaktizm, shivaizm, jaynizm", "Sunniylik, shialik, xorijiylik", "Pravoslaviya, katolisizm, protestantlik", "Xinayana, maxayana, lamaizm"], "ans": 3},
    {"q": '«Vijdon erkinligi va diniy tashkilotlar to\'g\'risida»gi qonunning yangi tahriri qaysi yilda qabul qilindi?', "opts": ["1990-y", "2018-y", "2000-y", "2021-y"], "ans": 3},
    {"q": '"Separatsion" model qanday model hisoblanadi?', "opts": ["Davlat dinini rasmiy belgilaydigan model", "Shariat asosida boshqariladigan model", "Davlat dindan ajratilganligiga asoslangan model", "Barcha javoblar to\'g\'ri"], "ans": 2},
    {"q": 'Buddizm ta\'limoti nechta asosiy haqiqatlardan iborat?', "opts": ["4", "2", "3", "5"], "ans": 0},
    {"q": 'Immanent ilohlar bu…?', "opts": ["Tabiatning bir bo\'lagi, insonlarga o\'xshab ketadigan, g\'ayrioddiy kuchlarga ega xudolar", "Insonlar olamidan tashqarida, nuqsonlardan xoli xudolar", "Tabiatning bir bo\'lagi sifatida insonlar", "Barcha javoblar to\'g\'ri"], "ans": 0},
    {"q": 'Muhammad (s.a.v) payg\'ambar tug\'ilgan kuniga bag\'ishlangan bayramning nomi?', "opts": ["Xatna", "Qurbon hayit", "Ramazon hayit", "Mavlud"], "ans": 3},
    {"q": 'Yangi tahrirdagi Qonunda vijdon erkinligini ta\'minlash qanday izohlangan?', "opts": ["Fuqarolarning xohlagan dinga e\'tiqod qilish yoki qilmaslik bo\'yicha kafolatlangan konstitutsiyaviy huquq", "Dinga e\'tiqod qilishga majburlashga yo\'l qo\'yilmaydi", "Faqat qonunda nazarda tutilgan cheklovlar tatbiq etiladi", "Barcha javoblar to\'g\'ri"], "ans": 3},
    {"q": '"Tavba" kitobi muallifi kim?', "opts": ["Abu Homid G\'azzoliy", "Imom al-Buxoriy", "Alisher Navoiy", "at-Termiziy"], "ans": 3},
    {"q": 'Istehson bu…?', "opts": ["Arab tilida bir narsani boshqasidan yaxshi deb bilish, ma\'qullash", "Arabcha «intilish», diniy va huquqiy masalalar bo\'yicha mustaqil fikr yuritish", "Arab tilidagi «Manfaat», «Foyda», «Naf» ma\'nolarini anglatadi", "Arabcha «taqqoslash», «solishtirish» degan ma\'noni anglatadi"], "ans": 0},
    {"q": 'Makka mushriklari e\'tiqod qilgan ilohlar?', "opts": ["Faqat Xubal", "Faqat Manot", "Faqat Lot, Uzzo", "Barcha javoblar to\'g\'ri (Xubal, Manot, Lot, Uzzo)"], "ans": 3},
    {"q": '"Irja" nima va qaysi mazhabda birinchi qo\'llanilgan?', "opts": ["«Ixtiloflarni Allohning hukmiga qoldirish» — Hanafiylik mazhabda", "«Tafsir ilmidagi izohlar» — Molikiylik mazhabda", "«Alloh kitobini tafsir qilish ilmi» — Sho\'feylik mazhabda", "«Ilmlar dengizi» — Hanbaliy mazhabda"], "ans": 0},
    {"q": 'Din qaysi paytda e\'tiqodlik xususiyatidan mahrum bo\'lib, hokimiyat quroliga aylandi?', "opts": ["Din ilohiylashtirilsa", "Din zamonaviylashtirilsa", "Din siyosatlashtirilsa", "Din insoniylashtirilsa"], "ans": 2},
    {"q": '"Baxtiyor oila" asarining muallifi kim?', "opts": ["Abu Homid G\'azzoliy", "Imom al-Buxoriy", "Muhammad Sodiq Muhammad Yusuf", "Abdurauf Fitrat"], "ans": 2},
    {"q": 'Arablarda islomgacha bo\'lgan davr qanday nomlanadi?', "opts": ["Turg\'unlik davri", "Budparastlik davri", "Ma\'rifat davri", "Johiliya davri"], "ans": 3},
    {"q": 'Diniy fundamentalizm nima?', "opts": ["Diniy ta\'limotlarni yangilashga urinish", "Dinda dogmatiklashgan tomonlarni inkor etish", "Ma\'lum din vujudga kelgan ilk davrga qaytish va shu orqali muammolarni hal qilish mumkin degan g\'oya", "A va B javob to\'g\'ri"], "ans": 2},
    {"q": 'Islom diniga tayanadigan qaysi ta\'limotga «Inson ruhiy komilligi falsafasi» deb tarif beriladi?', "opts": ["Kalom ta\'limotiga", "Tasavvuf ta\'limotiga", "Islom ta\'limotiga", "Naqshbandiya ta\'limotiga"], "ans": 1},
    {"q": 'Yahudiylar ibodatxonasi qanday nomlanadi?', "opts": ["Butxona", "Sinagoga", "Cherkov", "Ibodatxona"], "ans": 1},
    {"q": 'Bibliyaning qaysi qismi yahudiylarga ta\'luqli kitob?', "opts": ["Yangi Ahd", "Eski Ahd", "Ikkala qism ham", "Barcha javoblar to\'g\'ri"], "ans": 1},
    {"q": '«Iegov shohidlari» sektasi ko\'pincha kimlarni o\'z ta\'sir doiralariga olishga urinadi?', "opts": ["Birinchi va to\'rtinchi kurs talabalari, o\'smirlar", "Keksalar, endigina nafaqaga chiqqanlar va yolg\'iz qariyalar", "Kuchli stressni boshidan kechirayotganlar; qochoqlar va ishsizlar", "Barcha javoblar to\'g\'ri"], "ans": 3},
    {"q": 'Xristianlik qachon paydo bo\'ldi?', "opts": ["Milodimizgacha II asrda", "Milodimizning I asrida", "Milodimizgacha IV asrda", "Milodimizning V asrda"], "ans": 1},
    {"q": '«G\'arb ko\'r (ruhiy), Sharq oqsoq (iqtisodiy)» g\'oyasini ilgari surgan diniy harakat?', "opts": ["Bahoiylik harakatidan Sayid Ali Muhammad", "Krishnani anglash jamiyatidan Prabxubada", "Ahmadiylik harakatidan Mirzo G\'ulom Ahmad", "Baxshilotchilar harakatidan Baxshillo Aliev"], "ans": 2},
    {"q": '"Al-Adab al-mufrad" asari nechta hadisni o\'z ichiga olgan?', "opts": ["644 ta", "1018 ta", "1322 ta", "568 ta"], "ans": 1},
    {"q": '"Mukoshafatul qulub" asarining muallifi kim?', "opts": ["Abu Homid G\'azzoliy", "Abduxoliq G\'ijduvoniy", "Najmiddin Kubro", "Alisher Navoiy"], "ans": 0},
    {"q": 'Arabcha «ishonch», «biror narsani ikkinchisiga bog\'lash» — qoida va tartiblarni ko\'r-ko\'rona qo\'llash…', "opts": ["Fundamentalizm", "Aqidaparastlik", "Mutaassiblik", "Terrorizm"], "ans": 1},
    {"q": 'Baxodir Mamajonov qanday norasmiy islomiy jamoaga rahbarlik qilgan?', "opts": ["Ahmadiya jamoasiga", "Baxshillochilar jamoasiga", "Ma\'rifatchilar jamoasiga", "Shohidiylar jamoasiga"], "ans": 1},
    {"q": 'Quyidagilardan qaysi biri milliy dinlar toifasiga kirmaydi?', "opts": ["Sintoizm", "Konfutsizm", "Hinduizm", "Buddizm"], "ans": 3},
    {"q": 'Arab. «g\'uluv ketish» — g\'oyalarga mukkasidan berilish, boshqa firqalarni butunlay rad etish…', "opts": ["Fundamentalizm", "Aqidaparastlik", "Mutaassiblik", "Terrorizm"], "ans": 2},
    {"q": '1900-yilga kelib o\'zini «payg\'ambarlarning sarasi» deb e\'lon qilgan diniy harakat asoschisi?', "opts": ["Sayid Ali Muhammad", "Mirza Husayn Ali Nuriy", "Mirzo G\'ulom Ahmad", "Baxshillo Aliev"], "ans": 2},
    {"q": '"Muxtasar islom tarixi" risolasining muallifi kim?', "opts": ["Abu Homid G\'azzoliy", "Imom al-Buxoriy", "Muhammad Sodiq Muhammad Yusuf", "Abdurauf Fitrat"], "ans": 2},
    {"q": 'Yaratuvchi bilan insonni bog\'lab turadigan ibodat va marosimlar majmui nima deb ataladi?', "opts": ["Sur", "Kut", "Kult", "Tin"], "ans": 2},
    {"q": 'Tavrotning besh kitobini toping: 1)Borliq, 2)Matvey, 3)Chiqish, 4)Marko, 5)Levit, 6)Sonlar, 7)Luka, 8)Ikkinchi qonun, 9)Ioann', "opts": ["1,3,5,6,8", "1,3,4,6,9", "1,2,5,7,8", "3,5,6,8,9"], "ans": 0},
    {"q": 'XI asr oxirida Eronda yuzaga kelib, maxfiy ravishda ish ko\'rgan terrorchilik oqimi?', "opts": ["Qarmatiylar", "Hashshoshiylar", "Azraqiylar", "Nurchilar"], "ans": 1},
    {"q": '"Hisb-ut Tahrir" harakatining asoschisi?', "opts": ["Taqiy ad-din al-Nabahoniy", "Muhammad ibn Abdul Vahhob", "Said Nursiy Badiuzzamon", "Hasan al-Banno"], "ans": 0},
    {"q": '"Qur\'oni Karim"dagi eng katta sura?', "opts": ["Naxl", "Baqara", "Arof", "Lukmon"], "ans": 1},
    {"q": '"Din" so\'zi rus tilida qanday ataladi?', "opts": ["Vera", "Religiya", "Dana", "Dauna"], "ans": 1},
    {"q": '"Dinshunoslik" atamasini birinchi marta kim qo\'llagan?', "opts": ["Maks Myuller", "Beruniy", "Gerodot", "Dyuperon"], "ans": 0},
    {"q": 'Dinlar haqida dastlabki ma\'lumotlar qaysi tarixchi tomonidan asoslab berilgan?', "opts": ["Gerodot", "Pifagor", "Farobiy", "Zamaxshariy"], "ans": 0},
    {"q": 'Qaysi tashkilot ISHID ning tashkil topishida muhim o\'rin tutgan?', "opts": ["«Jixod ittixodi»", "«al-Qoida»", "«Tolibon»", "«Lashkari toyba»"], "ans": 1},
    {"q": 'Islomda asosiy qadriyatlardan biri?', "opts": ["Mashhurlik", "Mol-mulk", "Mansab", "Kuch"], "ans": 1},
    {"q": 'Milliy davlat dinlari ko\'rsatilgan qator?', "opts": ["Totemizm, fetishizm, xinduchilik", "Braxmanchilik, sintoizm, animizm", "Xinduchilik, braxmanchilik, sintoizm", "Javoblarning barchasi to\'g\'ri"], "ans": 2},
    {"q": 'Indulgensiya so\'zining ma\'nosi?', "opts": ["Katolik cherkovi tomonidan gunohlarni avf etish haqidagi guvohnoma", "Pravoslavlar o\'tkazadigan marosim", "Protestantlar ta\'limoti", "Katolik cherkov tomonidan chiqarilgan farmon"], "ans": 0},
    {"q": '"Tong-2000" nomli missionerlik dasturining muallifi?', "opts": ["R.Adler", "Pavlus", "J. Montgomeri", "Rixtgofen"], "ans": 2},
    {"q": 'Buddizm dini manbasi qanday nomlanadi?', "opts": ["Veda", "Tripitaka", "Samoveda", "Yajurveda"], "ans": 1},
    {"q": '"Qur\'oni Karim"ning yaratilishida bevosita ishtirok etgan shaxs?', "opts": ["Zayd ibn Xorris", "Zayd ibn Sobit", "Zayd ibn No\'mon", "Zayd ibn Xanbal"], "ans": 1},
    {"q": 'Islom arxitekturasida minora qanday vazifani bajaradi?', "opts": ["Faqat bezak uchun", "Imom yashashi uchun", "Namozga chaqirish (azon) uchun", "Kitob saqlash uchun"], "ans": 2},
    {"q": 'BMT Bosh Assambleyasi A/Res/73/128 "Ma\'rifat va diniy bag\'rikenglik" rezolyutsiyasi qachon qabul qilindi?', "opts": ["2016 y", "2017 y", "2018 y", "2019 y"], "ans": 2},
    {"q": 'Alloh taolo payg\'ambarlarga necha sahifa va necha kitob yuborgan?', "opts": ["100 sahifa va 4 kitob", "100 sahifa va 5 kitob", "200 sahifa va 4 kitob", "10 sahifa va 4 kitob"], "ans": 0},
    {"q": 'Toshkentda SHTning Mintaqaviy aksitterror tuzilmasi qachon ish boshladi?', "opts": ["2004-yil yanvardan", "2009-yil fevraldan", "2001-yil martdan", "2005-yil noyabrdan"], "ans": 0},
    {"q": 'Shialikning mazhablarini toping?', "opts": ["Shofeylik, jafariylik, molikiylik", "Zaydiylik, hanafiylik, ismoiliylik", "Molikiylik, sunniylik, jafariylik", "Ismoiliylik, ja\'fariylik, zaydiylik"], "ans": 3},
    {"q": 'Hozir O\'zbekiston Respublikasida nechta diniy konfessiya faoliyat ko\'rsatmoqda?', "opts": ["20 ta", "18 ta", "19 ta", "16 ta"], "ans": 2},
    {"q": 'Transsendent ilohlar deganda…', "opts": ["Insonlarga hech qanday aloqasi bo\'lmagan, nuqsonlardan xoli xudolar", "Tabiatning bir bo\'lagi sifatida insonlarga o\'xshab ketadigan xudolar", "Ibtidoiy xudolar", "Yahudiylar xudolari shunday atalgan"], "ans": 0},
    {"q": 'Axborot urushi atamasi dastlab kim tomonidan qo\'llanilgan?', "opts": ["Lyudovig Bax", "Jon Kalvin", "Allen Dalles", "Martin Lyuter"], "ans": 2},
    {"q": 'Konstitutsiyamizning nechanchi moddasida "Davlat diniy birlashmalarning faoliyatiga aralashmaydi" deb belgilangan?', "opts": ["57-moddada", "32-moddada", "75-moddada", "31-moddada"], "ans": 3},
    {"q": 'Markaziy Osiyodagi diniy ekstremistik oqimlarni funksiyalariga ko\'ra nechta guruhga bo\'lishimiz mumkin?', "opts": ["2 ta", "3 ta", "4 ta", "5 ta"], "ans": 1},
    {"q": 'Diniy tashkilotni davlat ro\'yxatidan o\'tkazish adliya idoralari tomonidan qancha muddatda ko\'rib chiqiladi?', "opts": ["1 yil", "6 oy", "3 oy", "1 oy"], "ans": 2},
    {"q": 'Qaysi dinda diniy marosimlarni kannushlar deb ataladigan alohida kohinlar ijro etadi?', "opts": ["Buddaviylikda", "Konfutsiychilikda", "Sintoizmda", "Daosizmda"], "ans": 2},
    {"q": 'Shariat qonun-qoidalarini o\'rganuvchi fan?', "opts": ["Kosmogoniya", "Astrologiya", "Fiqh", "Dinshunoslik"], "ans": 2},
    {"q": 'Movarounnahr kalom maktabining taraqqiyotini necha davrga bo\'lib o\'rganish mumkin?', "opts": ["3 davr", "5 davr", "8 davr", "12 davr"], "ans": 0},
    {"q": '2000-yilda Islom ta\'limotining buyuk namoyandalaridan kimning 1130 yilligi nishonlanadi?', "opts": ["Imom Termiziy", "Imom Moturidiy", "Imom Buxoriy", "Imom Samarqandiy"], "ans": 1},
    {"q": 'Urug\'-qabila dinlaridan biri?', "opts": ["Animizm", "Mazdeizm", "Lamaizm", "Jaynizm"], "ans": 0},
    {"q": 'Muhammad (s.a.v) qachon o\'zini Allohning rasuli deb e\'lon qildi?', "opts": ["610 y", "622 y", "570 y", "632 y"], "ans": 0},
    {"q": 'Qur\'onda nechta sura bor?', "opts": ["110", "114", "115", "286"], "ans": 1},
    {"q": 'Ijmo so\'zining ma\'nosi?', "opts": ["Arabcha – yakdillik", "Arabcha – taqqoslash", "Arabcha – odat, an\'ana, xatti-harakat tarzi", "Arabcha – qiyoslash"], "ans": 0},
    {"q": 'Shia mazhabida muqaddas hadislar nima deb ataladi?', "opts": ["Axbor", "Kalom", "Fiqh", "Tasavvuf"], "ans": 0},
    {"q": 'Qur\'on suralari qanday qismlarga bo\'linadi?', "opts": ["Baland va past", "Makka va Madina suralari", "Dastlabki va yangi", "Qadimiy va yangi"], "ans": 1},
]

# ─── USER SESSION ────────────────────────────────────────────────────────────
user_sessions = {}

def get_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "questions": [],
            "current": 0,
            "correct": 0,
            "wrong": 0,
            "poll_to_q": {},   # poll_id -> question index in session
            "active": False,
        }
    return user_sessions[user_id]

# ─── COMMANDS ────────────────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Dinshunoslik Test Botiga Xush Kelibsiz!*\n\n"
        "Bu bot 100 ta savoldan iborat test o'tkazadi.\n\n"
        "📌 Buyruqlar:\n"
        "/test — to'liq 100 ta savolni boshlash\n"
        "/test10 — 10 ta tasodifiy savol\n"
        "/test20 — 20 ta tasodifiy savol\n"
        "/stop — testni to'xtatish\n"
        "/natija — oxirgi natijani ko'rish",
        parse_mode="Markdown"
    )

async def begin_test(update: Update, ctx: ContextTypes.DEFAULT_TYPE, count: int = 100):
    user_id = update.effective_user.id
    sess = get_session(user_id)

    if sess["active"]:
        await update.message.reply_text("⚠️ Test allaqachon boshlangan. /stop buyrug'i bilan to'xtatishingiz mumkin.")
        return

    pool = QUESTIONS.copy()
    random.shuffle(pool)
    sess["questions"] = pool[:count]
    sess["current"] = 0
    sess["correct"] = 0
    sess["wrong"] = 0
    sess["poll_to_q"] = {}
    sess["active"] = True

    await update.message.reply_text(
        f"🚀 Test boshlandi! Jami *{count} ta* savol.\nHar bir savolda to'g'ri javobni tanlang. Omad! 🍀",
        parse_mode="Markdown"
    )
    await send_question(update.message.chat_id, ctx, user_id)

async def cmd_test(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await begin_test(update, ctx, 100)

async def cmd_test10(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await begin_test(update, ctx, 10)

async def cmd_test20(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await begin_test(update, ctx, 20)

async def cmd_stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sess = get_session(user_id)
    if not sess["active"]:
        await update.message.reply_text("Hozircha test yo'q. /test bilan boshlang.")
        return
    answered = sess["correct"] + sess["wrong"]
    pct = round(sess["correct"] / answered * 100) if answered else 0
    sess["active"] = False
    await update.message.reply_text(
        f"🛑 Test to'xtatildi.\n\n"
        f"✅ To'g'ri: {sess['correct']}\n"
        f"❌ Noto'g'ri: {sess['wrong']}\n"
        f"📊 Foiz: {pct}% ({answered} ta savolga javob berildi)"
    )

async def cmd_natija(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sess = get_session(user_id)
    answered = sess["correct"] + sess["wrong"]
    if not answered:
        await update.message.reply_text("Hali hech qanday test topshirilmagan.")
        return
    pct = round(sess["correct"] / answered * 100)
    await update.message.reply_text(
        f"📊 *Oxirgi natija:*\n"
        f"✅ To'g'ri: {sess['correct']}\n"
        f"❌ Noto'g'ri: {sess['wrong']}\n"
        f"📈 Foiz: {pct}%",
        parse_mode="Markdown"
    )

# ─── SEND QUESTION ───────────────────────────────────────────────────────────
async def send_question(chat_id, ctx, user_id):
    sess = get_session(user_id)
    idx = sess["current"]
    total = len(sess["questions"])

    if idx >= total:
        await finish_test(chat_id, ctx, user_id)
        return

    q = sess["questions"][idx]
    msg = await ctx.bot.send_poll(
        chat_id=chat_id,
        question=f"❓ {idx+1}/{total}: {q['q']}",
        options=q["opts"],
        type=Poll.QUIZ,
        correct_option_id=q["ans"],
        is_anonymous=False,
        open_period=30,
    )
    sess["poll_to_q"][msg.poll.id] = {"user_id": user_id, "q_idx": idx}

# ─── HANDLE ANSWER ───────────────────────────────────────────────────────────
async def handle_poll_answer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    answer = update.poll_answer
    poll_id = answer.poll_id
    user_id = answer.user.id
    sess = get_session(user_id)

    meta = sess.get("poll_to_q", {}).get(poll_id)
    if not meta or meta["user_id"] != user_id:
        return

    q = sess["questions"][meta["q_idx"]]
    chosen = answer.option_ids[0] if answer.option_ids else -1
    if chosen == q["ans"]:
        sess["correct"] += 1
    else:
        sess["wrong"] += 1

    sess["current"] += 1
    total = len(sess["questions"])
    answered = sess["correct"] + sess["wrong"]

    # Progress har 5 savolda
    if answered % 5 == 0 and answered < total:
        pct = round(sess["correct"] / answered * 100)
        await ctx.bot.send_message(
            chat_id=answer.user.id,
            text=f"📈 *{answered}/{total}* — hozircha: ✅ {sess['correct']} | ❌ {sess['wrong']} ({pct}%)",
            parse_mode="Markdown"
        )

    await send_question(answer.user.id, ctx, user_id)

# ─── FINISH ──────────────────────────────────────────────────────────────────
async def finish_test(chat_id, ctx, user_id):
    sess = get_session(user_id)
    total = len(sess["questions"])
    correct = sess["correct"]
    wrong = sess["wrong"]
    pct = round(correct / total * 100) if total else 0

    if pct >= 90:
        grade = "🏆 A'lo (Excellent)"
    elif pct >= 70:
        grade = "👍 Yaxshi (Good)"
    elif pct >= 50:
        grade = "📚 Qoniqarli (Satisfactory)"
    else:
        grade = "📖 Qoniqarsiz (Unsatisfactory)"

    await ctx.bot.send_message(
        chat_id=chat_id,
        text=(
            f"🎉 *Test yakunlandi!*\n\n"
            f"📝 Jami savollar: {total}\n"
            f"✅ To'g'ri javoblar: {correct}\n"
            f"❌ Noto'g'ri javoblar: {wrong}\n"
            f"📊 Natija: *{pct}%*\n"
            f"🎓 Baho: {grade}\n\n"
            f"Qayta urinish uchun /test ni bosing!"
        ),
        parse_mode="Markdown"
    )
    sess["active"] = False

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", cmd_test))
    app.add_handler(CommandHandler("test10", cmd_test10))
    app.add_handler(CommandHandler("test20", cmd_test20))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("natija", cmd_natija))
    app.add_handler(PollAnswerHandler(handle_poll_answer))

    logger.info("Bot ishga tushdi...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
