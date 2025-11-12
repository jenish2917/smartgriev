import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Translations for all 12 supported languages
const resources = {
  en: {
    translation: {
      common: {
        appName: 'SmartGriev',
        welcome: 'Welcome',
        tagline: 'Talk. Type. Resolve.'
      },
      navigation: {
        home: 'Home',
        login: 'Login',
        register: 'Register',
        dashboard: 'Dashboard',
        aiChat: 'AI Chat',
        myComplaints: 'My Complaints',
        profile: 'Profile',
        settings: 'Settings',
        logout: 'Logout'
      },
      dashboard: {
        welcomeBack: 'Welcome back',
        totalComplaints: 'Total Complaints',
        pending: 'Pending',
        inProgress: 'In Progress',
        resolved: 'Resolved',
        thisWeek: 'this week',
        needAttention: 'need attention',
        updatedToday: 'Updated today',
        satisfaction: 'satisfaction',
        recentComplaints: 'Recent Complaints',
        viewAll: 'View All Complaints'
      },
      chatbot: {
        greeting: "I'm your AI assistant for SmartGriev. I'll help you submit complaints through natural conversation. Just tell me about the issue, and I'll guide you through the process. You can also send photos, videos, or voice messages. What civic issue would you like to report today?",
        quickActions: 'Quick actions:',
        fileComplaint: 'File a new complaint',
        reportPothole: 'Report pothole with photo',
        garbageIssue: 'Garbage collection issue',
        streetLight: 'Street light not working',
        typeMessage: 'Type your message...',
        recording: 'Recording... Click mic button to stop',
        enableGPS: 'Enable GPS',
        enterManually: 'Enter Manually',
        aiAssistant: 'AI Assistant',
        online: 'Online',
        alwaysHelp: 'Always here to help • Smart complaint filing'
      },
      features: {
        aiChatbot: 'AI Chatbot',
        aiChatbotDesc: 'Natural conversation for complaint submission',
        languages: '12 Languages',
        languagesDesc: 'Full support for Indian languages',
        voiceVision: 'Voice & Vision',
        voiceVisionDesc: 'Multi-modal input support'
      },
      actions: {
        getStarted: 'Get Started',
        registerNow: 'Register Now'
      },
      auth: {
        login: 'Login',
        register: 'Register',
        email: 'Email',
        password: 'Password',
        confirmPassword: 'Confirm Password',
        rememberMe: 'Remember Me',
        forgotPassword: 'Forgot Password?',
        dontHaveAccount: "Don't have an account?",
        alreadyHaveAccount: 'Already have an account?',
        firstName: 'First Name',
        lastName: 'Last Name',
        username: 'Username',
        mobileNumber: 'Mobile Number',
        address: 'Address',
        language: 'Language',
        termsAccept: 'I agree to the',
        termsConditions: 'Terms and Conditions',
        privacyPolicy: 'Privacy Policy',
        and: 'and',
        creatingAccount: 'Creating account...',
        loggingIn: 'Logging in...',
        createAccount: 'Create your SmartGriev account'
      }
    }
  },
  hi: {
    translation: {
      common: {
        appName: 'स्मार्टग्रीव',
        welcome: 'स्वागत है',
        tagline: 'बात करें। टाइप करें। हल करें।'
      },
      navigation: {
        home: 'होम',
        login: 'लॉगिन',
        register: 'रजिस्टर',
        dashboard: 'डैशबोर्ड',
        aiChat: 'एआई चैट',
        myComplaints: 'मेरी शिकायतें',
        profile: 'प्रोफाइल',
        settings: 'सेटिंग्स',
        logout: 'लॉगआउट'
      },
      dashboard: {
        welcomeBack: 'वापसी में आपका स्वागत है',
        totalComplaints: 'कुल शिकायतें',
        pending: 'लंबित',
        inProgress: 'प्रगति में',
        resolved: 'हल किया गया',
        thisWeek: 'इस सप्ताह',
        needAttention: 'ध्यान देने की आवश्यकता है',
        updatedToday: 'आज अपडेट किया गया',
        satisfaction: 'संतुष्टि',
        recentComplaints: 'हाल की शिकायतें',
        viewAll: 'सभी शिकायतें देखें'
      },
      chatbot: {
        greeting: "मैं स्मार्टग्रीव के लिए आपका एआई सहायक हूं। मैं प्राकृतिक बातचीत के माध्यम से शिकायतें दर्ज करने में आपकी मदद करूंगा। बस मुझे समस्या के बारे में बताएं, और मैं आपको प्रक्रिया के माध्यम से मार्गदर्शन करूंगा। आप फोटो, वीडियो या ध्वनि संदेश भी भेज सकते हैं। आज आप कौन सी नागरिक समस्या की रिपोर्ट करना चाहेंगे?",
        quickActions: 'त्वरित क्रियाएं:',
        fileComplaint: 'नई शिकायत दर्ज करें',
        reportPothole: 'फोटो के साथ गड्ढे की रिपोर्ट करें',
        garbageIssue: 'कचरा संग्रहण समस्या',
        streetLight: 'स्ट्रीट लाइट काम नहीं कर रही',
        typeMessage: 'अपना संदेश टाइप करें...',
        recording: 'रिकॉर्डिंग... रोकने के लिए माइक बटन पर क्लिक करें',
        enableGPS: 'GPS सक्षम करें',
        enterManually: 'मैन्युअल रूप से दर्ज करें',
        aiAssistant: 'एआई सहायक',
        online: 'ऑनलाइन',
        alwaysHelp: 'हमेशा मदद के लिए यहाँ • स्मार्ट शिकायत दाखिल करना'
      },
      features: {
        aiChatbot: 'एआई चैटबॉट',
        aiChatbotDesc: 'शिकायत जमा करने के लिए प्राकृतिक बातचीत',
        languages: '12 भाषाएं',
        languagesDesc: 'भारतीय भाषाओं के लिए पूर्ण समर्थन',
        voiceVision: 'आवाज और दृष्टि',
        voiceVisionDesc: 'बहु-मोडल इनपुट समर्थन'
      },
      actions: {
        getStarted: 'शुरू करें',
        registerNow: 'अभी रजिस्टर करें'
      },
      auth: {
        login: 'लॉगिन',
        register: 'रजिस्टर',
        email: 'ईमेल',
        password: 'पासवर्ड',
        confirmPassword: 'पासवर्ड की पुष्टि करें',
        rememberMe: 'मुझे याद रखें',
        forgotPassword: 'पासवर्ड भूल गए?',
        dontHaveAccount: 'खाता नहीं है?',
        alreadyHaveAccount: 'पहले से खाता है?',
        firstName: 'पहला नाम',
        lastName: 'अंतिम नाम',
        username: 'उपयोगकर्ता नाम',
        mobileNumber: 'मोबाइल नंबर',
        address: 'पता',
        language: 'भाषा',
        termsAccept: 'मैं सहमत हूं',
        termsConditions: 'नियम और शर्तें',
        privacyPolicy: 'गोपनीयता नीति',
        and: 'और',
        creatingAccount: 'खाता बनाया जा रहा है...',
        loggingIn: 'लॉग इन हो रहा है...',
        createAccount: 'अपना स्मार्टग्रीव खाता बनाएं'
      }
    }
  },
  bn: {
    translation: {
      common: {
        appName: 'স্মার্টগ্রীভ',
        welcome: 'স্বাগতম',
        tagline: 'কথা বলুন। টাইপ করুন। সমাধান করুন।'
      },
      navigation: {
        home: 'হোম',
        login: 'লগইন',
        register: 'নিবন্ধন',
        dashboard: 'ড্যাশবোর্ড',
        aiChat: 'এআই চ্যাট',
        myComplaints: 'আমার অভিযোগ',
        profile: 'প্রোফাইল',
        settings: 'সেটিংস',
        logout: 'লগআউট'
      },
      dashboard: {
        welcomeBack: 'ফিরে এসেছেন স্বাগতম',
        totalComplaints: 'মোট অভিযোগ',
        pending: 'অপেক্ষমাণ',
        inProgress: 'অগ্রগতিতে',
        resolved: 'সমাধান হয়েছে',
        thisWeek: 'এই সপ্তাহে',
        needAttention: 'মনোযোগ প্রয়োজন',
        updatedToday: 'আজ আপডেট করা হয়েছে',
        satisfaction: 'সন্তুষ্টি',
        recentComplaints: 'সাম্প্রতিক অভিযোগ',
        viewAll: 'সমস্ত অভিযোগ দেখুন'
      },
      features: {
        aiChatbot: 'এআই চ্যাটবট',
        aiChatbotDesc: 'অভিযোগ জমা দেওয়ার জন্য প্রাকৃতিক কথোপকথন',
        languages: '১২টি ভাষা',
        languagesDesc: 'ভারতীয় ভাষাগুলির জন্য সম্পূর্ণ সমর্থন',
        voiceVision: 'ভয়েস ও ভিশন',
        voiceVisionDesc: 'মাল্টি-মোডাল ইনপুট সমর্থন'
      },
      actions: {
        getStarted: 'শুরু করুন',
        registerNow: 'এখনই নিবন্ধন করুন'
      },
      auth: {
        login: 'লগইন',
        register: 'নিবন্ধন',
        email: 'ইমেল',
        password: 'পাসওয়ার্ড',
        confirmPassword: 'পাসওয়ার্ড নিশ্চিত করুন',
        rememberMe: 'আমাকে মনে রাখুন',
        forgotPassword: 'পাসওয়ার্ড ভুলে গেছেন?',
        dontHaveAccount: 'অ্যাকাউন্ট নেই?',
        alreadyHaveAccount: 'ইতিমধ্যে অ্যাকাউন্ট আছে?',
        firstName: 'প্রথম নাম',
        lastName: 'শেষ নাম',
        username: 'ব্যবহারকারীর নাম',
        mobileNumber: 'মোবাইল নম্বর',
        address: 'ঠিকানা',
        language: 'ভাষা',
        termsAccept: 'আমি সম্মত',
        termsConditions: 'শর্তাবলী',
        privacyPolicy: 'গোপনীয়তা নীতি',
        and: 'এবং',
        creatingAccount: 'অ্যাকাউন্ট তৈরি করা হচ্ছে...',
        loggingIn: 'লগ ইন করা হচ্ছে...',
        createAccount: 'আপনার স্মার্টগ্রীভ অ্যাকাউন্ট তৈরি করুন'
      }
    }
  },
  te: {
    translation: {
      common: {
        appName: 'స్మార్ట్‌గ్రీవ్',
        welcome: 'స్వాగతం',
        tagline: 'మాట్లాడండి. టైప్ చేయండి. పరిష్కరించండి.'
      },
      navigation: {
        home: 'హోమ్',
        login: 'లాగిన్',
        register: 'రిజిస్టర్',
        dashboard: 'డ్యాష్‌బోర్డ్',
        aiChat: 'AI చాట్',
        myComplaints: 'నా ఫిర్యాదులు',
        profile: 'ప్రొఫైల్',
        settings: 'సెట్టింగులు',
        logout: 'లాగౌట్'
      },
      dashboard: {
        welcomeBack: 'తిరిగి స్వాగతం',
        totalComplaints: 'మొత్తం ఫిర్యాదులు',
        pending: 'పెండింగ్',
        inProgress: 'ప్రగతిలో',
        resolved: 'పరిష్కరించబడింది',
        thisWeek: 'ఈ వారం',
        needAttention: 'దృష్టి అవసరం',
        updatedToday: 'నేడు అప్‌డేట్ చేయబడింది',
        satisfaction: 'సంతృప్తి',
        recentComplaints: 'ఇటీవలి ఫిర్యాదులు',
        viewAll: 'అన్ని ఫిర్యాదులు చూడండి'
      },
      features: {
        aiChatbot: 'AI చాట్‌బాట్',
        aiChatbotDesc: 'ఫిర్యాదు సమర్పణ కోసం సహజ సంభాషణ',
        languages: '12 భాషలు',
        languagesDesc: 'భారతీయ భాషలకు పూర్తి మద్దతు',
        voiceVision: 'వాయిస్ & విజన్',
        voiceVisionDesc: 'మల్టీ-మోడల్ ఇన్‌పుట్ మద్దతు'
      },
      actions: {
        getStarted: 'ప్రారంభించండి',
        registerNow: 'ఇప్పుడే రిజిస్టర్ చేయండి'
      },
      auth: {
        login: 'లాగిన్',
        register: 'రిజిస్టర్',
        email: 'ఇమెయిల్',
        password: 'పాస్‌వర్డ్',
        confirmPassword: 'పాస్‌వర్డ్ నిర్ధారించండి',
        rememberMe: 'నన్ను గుర్తుంచుకోండి',
        forgotPassword: 'పాస్‌వర్డ్ మర్చిపోయారా?',
        dontHaveAccount: 'ఖాతా లేదా?',
        alreadyHaveAccount: 'ఇప్పటికే ఖాతా ఉందా?',
        firstName: 'మొదటి పేరు',
        lastName: 'చివరి పేరు',
        username: 'వినియోగదారు పేరు',
        mobileNumber: 'మొబైల్ నంబర్',
        address: 'చిరునామా',
        language: 'భాష',
        termsAccept: 'నేను అంగీకరిస్తున్నాను',
        termsConditions: 'నియమాలు మరియు షరతులు',
        privacyPolicy: 'గోప్యతా విధానం',
        and: 'మరియు',
        creatingAccount: 'ఖాతా సృష్టించబడుతోంది...',
        loggingIn: 'లాగిన్ అవుతోంది...',
        createAccount: 'మీ స్మార్ట్‌గ్రీవ్ ఖాతాను సృష్టించండి'
      }
    }
  },
  mr: {
    translation: {
      common: {
        appName: 'स्मार्टग्रीव्ह',
        welcome: 'स्वागत आहे',
        tagline: 'बोला. टाईप करा. निराकरण करा.'
      },
      navigation: {
        home: 'होम',
        login: 'लॉगिन',
        register: 'नोंदणी',
        dashboard: 'डॅशबोर्ड',
        aiChat: 'AI चॅट',
        myComplaints: 'माझ्या तक्रारी',
        profile: 'प्रोफाइल',
        settings: 'सेटिंग्ज',
        logout: 'लॉगआउट'
      },
      dashboard: {
        welcomeBack: 'परत स्वागत आहे',
        totalComplaints: 'एकूण तक्रारी',
        pending: 'प्रलंबित',
        inProgress: 'प्रगतीपथावर',
        resolved: 'निराकरण झाले',
        thisWeek: 'या आठवड्यात',
        needAttention: 'लक्ष देणे आवश्यक',
        updatedToday: 'आज अद्यतनित',
        satisfaction: 'समाधान',
        recentComplaints: 'अलीकडील तक्रारी',
        viewAll: 'सर्व तक्रारी पहा'
      },
      features: {
        aiChatbot: 'AI चॅटबॉट',
        aiChatbotDesc: 'तक्रार सादर करण्यासाठी नैसर्गिक संभाषण',
        languages: '12 भाषा',
        languagesDesc: 'भारतीय भाषांसाठी पूर्ण समर्थन',
        voiceVision: 'व्हॉइस आणि व्हिजन',
        voiceVisionDesc: 'मल्टी-मोडल इनपुट समर्थन'
      },
      actions: {
        getStarted: 'सुरू करा',
        registerNow: 'आता नोंदणी करा'
      },
      auth: {
        login: 'लॉगिन',
        register: 'नोंदणी',
        email: 'ईमेल',
        password: 'पासवर्ड',
        confirmPassword: 'पासवर्डची पुष्टी करा',
        rememberMe: 'मला लक्षात ठेवा',
        forgotPassword: 'पासवर्ड विसरलात?',
        dontHaveAccount: 'खाते नाही?',
        alreadyHaveAccount: 'आधीच खाते आहे?',
        firstName: 'पहिले नाव',
        lastName: 'आडनाव',
        username: 'वापरकर्ता नाव',
        mobileNumber: 'मोबाइल नंबर',
        address: 'पत्ता',
        language: 'भाषा',
        termsAccept: 'मी सहमत आहे',
        termsConditions: 'अटी आणि शर्ती',
        privacyPolicy: 'गोपनीयता धोरण',
        and: 'आणि',
        creatingAccount: 'खाते तयार केले जात आहे...',
        loggingIn: 'लॉग इन होत आहे...',
        createAccount: 'तुमचे स्मार्टग्रीव्ह खाते तयार करा'
      }
    }
  },
  ta: {
    translation: {
      common: {
        appName: 'ஸ்மார்ட்கிரீவ்',
        welcome: 'வரவேற்கிறோம்',
        tagline: 'பேசுங்கள். தட்டச்சு செய்யுங்கள். தீர்க்கவும்.'
      },
      navigation: {
        home: 'முகப்பு',
        login: 'உள்நுழைவு',
        register: 'பதிவு',
        dashboard: 'டாஷ்போர்டு',
        aiChat: 'AI அரட்டை',
        myComplaints: 'எனது புகார்கள்',
        profile: 'சுயவிவரம்',
        settings: 'அமைப்புகள்',
        logout: 'வெளியேறு'
      },
      dashboard: {
        welcomeBack: 'மீண்டும் வரவேற்கிறோம்',
        totalComplaints: 'மொத்த புகார்கள்',
        pending: 'நிலுவையில்',
        inProgress: 'முன்னேற்றத்தில்',
        resolved: 'தீர்க்கப்பட்டது',
        thisWeek: 'இந்த வாரம்',
        needAttention: 'கவனம் தேவை',
        updatedToday: 'இன்று புதுப்பிக்கப்பட்டது',
        satisfaction: 'திருப்தி',
        recentComplaints: 'சமீபத்திய புகார்கள்',
        viewAll: 'அனைத்து புகார்களையும் காண்க'
      },
      features: {
        aiChatbot: 'AI சாட்பாட்',
        aiChatbotDesc: 'புகார் சமர்ப்பிப்பதற்கான இயற்கையான உரையாடல்',
        languages: '12 மொழிகள்',
        languagesDesc: 'இந்திய மொழிகளுக்கான முழு ஆதரவு',
        voiceVision: 'குரல் மற்றும் பார்வை',
        voiceVisionDesc: 'பல-முறை உள்ளீடு ஆதரவு'
      },
      actions: {
        getStarted: 'தொடங்கவும்',
        registerNow: 'இப்போது பதிவு செய்யவும்'
      },
      auth: {
        login: 'உள்நுழைவு',
        register: 'பதிவு',
        email: 'மின்னஞ்சல்',
        password: 'கடவுச்சொல்',
        confirmPassword: 'கடவுச்சொல்லை உறுதிப்படுத்தவும்',
        rememberMe: 'என்னை நினைவில் கொள்ளுங்கள்',
        forgotPassword: 'கடவுச்சொல்லை மறந்துவிட்டீர்களா?',
        dontHaveAccount: 'கணக்கு இல்லையா?',
        alreadyHaveAccount: 'ஏற்கனவே கணக்கு உள்ளதா?',
        firstName: 'முதல் பெயர்',
        lastName: 'கடைசி பெயர்',
        username: 'பயனர்பெயர்',
        mobileNumber: 'மொபைல் எண்',
        address: 'முகவரி',
        language: 'மொழி',
        termsAccept: 'நான் ஒப்புக்கொள்கிறேன்',
        termsConditions: 'விதிமுறைகள் மற்றும் நிபந்தனைகள்',
        privacyPolicy: 'தனியுரிமைக் கொள்கை',
        and: 'மற்றும்',
        creatingAccount: 'கணக்கு உருவாக்கப்படுகிறது...',
        loggingIn: 'உள்நுழைகிறது...',
        createAccount: 'உங்கள் ஸ்மார்ட்கிரீவ் கணக்கை உருவாக்கவும்'
      }
    }
  },
  gu: {
    translation: {
      common: {
        appName: 'સ્માર્ટગ્રીવ',
        welcome: 'સ્વાગત છે',
        tagline: 'વાત કરો. ટાઇપ કરો. ઉકેલ કરો.'
      },
      navigation: {
        home: 'હોમ',
        login: 'લૉગિન',
        register: 'નોંધણી',
        dashboard: 'ડૅશબોર્ડ',
        aiChat: 'AI ચેટ',
        myComplaints: 'મારી ફરિયાદો',
        profile: 'પ્રોફાઇલ',
        settings: 'સેટિંગ્સ',
        logout: 'લૉગઆઉટ'
      },
      dashboard: {
        welcomeBack: 'પાછા સ્વાગત છે',
        totalComplaints: 'કુલ ફરિયાદો',
        pending: 'બાકી',
        inProgress: 'પ્રગતિમાં',
        resolved: 'ઉકેલાયેલ',
        thisWeek: 'આ અઠવાડિયે',
        needAttention: 'ધ્યાન જરૂરી છે',
        updatedToday: 'આજે અપડેટ કરેલ',
        satisfaction: 'સંતોષ',
        recentComplaints: 'તાજેતરની ફરિયાદો',
        viewAll: 'બધી ફરિયાદો જુઓ'
      },
      features: {
        aiChatbot: 'AI ચેટબોટ',
        aiChatbotDesc: 'ફરિયાદ સબમિશન માટે કુદરતી વાર્તાલાપ',
        languages: '12 ભાષાઓ',
        languagesDesc: 'ભારતીય ભાષાઓ માટે સંપૂર્ણ સપોર્ટ',
        voiceVision: 'વૉઇસ અને વિઝન',
        voiceVisionDesc: 'મલ્ટી-મોડલ ઇનપુટ સપોર્ટ'
      },
      actions: {
        getStarted: 'શરૂ કરો',
        registerNow: 'હમણાં નોંધણી કરો'
      },
      auth: {
        login: 'લૉગિન',
        register: 'નોંધણી',
        email: 'ઇમેઇલ',
        password: 'પાસવર્ડ',
        confirmPassword: 'પાસવર્ડની પુષ્ટિ કરો',
        rememberMe: 'મને યાદ રાખો',
        forgotPassword: 'પાસવર્ડ ભૂલી ગયા?',
        dontHaveAccount: 'ખાતું નથી?',
        alreadyHaveAccount: 'પહેલેથી જ ખાતું છે?',
        firstName: 'પ્રથમ નામ',
        lastName: 'છેલ્લું નામ',
        username: 'વપરાશકર્તા નામ',
        mobileNumber: 'મોબાઇલ નંબર',
        address: 'સરનામું',
        language: 'ભાષા',
        termsAccept: 'હું સંમત છું',
        termsConditions: 'નિયમો અને શરતો',
        privacyPolicy: 'ગોપનીયતા નીતિ',
        and: 'અને',
        creatingAccount: 'ખાતું બનાવાઈ રહ્યું છે...',
        loggingIn: 'લૉગ ઇન થઈ રહ્યું છે...',
        createAccount: 'તમારું સ્માર્ટગ્રીવ ખાતું બનાવો'
      }
    }
  },
  kn: {
    translation: {
      common: {
        appName: 'ಸ್ಮಾರ್ಟ್‌ಗ್ರೀವ್',
        welcome: 'ಸ್ವಾಗತ',
        tagline: 'ಮಾತನಾಡಿ. ಟೈಪ್ ಮಾಡಿ. ಪರಿಹರಿಸಿ.'
      },
      navigation: {
        home: 'ಮುಖಪುಟ',
        login: 'ಲಾಗಿನ್',
        register: 'ನೋಂದಣಿ',
        dashboard: 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
        aiChat: 'AI ಚಾಟ್',
        myComplaints: 'ನನ್ನ ದೂರುಗಳು',
        profile: 'ಪ್ರೊಫೈಲ್',
        settings: 'ಸೆಟ್ಟಿಂಗ್‌ಗಳು',
        logout: 'ಲಾಗ್‌ಔಟ್'
      },
      dashboard: {
        welcomeBack: 'ಮತ್ತೆ ಸ್ವಾಗತ',
        totalComplaints: 'ಒಟ್ಟು ದೂರುಗಳು',
        pending: 'ಬಾಕಿ',
        inProgress: 'ಪ್ರಗತಿಯಲ್ಲಿ',
        resolved: 'ಪರಿಹರಿಸಲಾಗಿದೆ',
        thisWeek: 'ಈ ವಾರ',
        needAttention: 'ಗಮನ ಬೇಕು',
        updatedToday: 'ಇಂದು ನವೀಕರಿಸಲಾಗಿದೆ',
        satisfaction: 'ತೃಪ್ತಿ',
        recentComplaints: 'ಇತ್ತೀಚಿನ ದೂರುಗಳು',
        viewAll: 'ಎಲ್ಲಾ ದೂರುಗಳನ್ನು ವೀಕ್ಷಿಸಿ'
      },
      features: {
        aiChatbot: 'AI ಚಾಟ್‌ಬಾಟ್',
        aiChatbotDesc: 'ದೂರು ಸಲ್ಲಿಕೆಗಾಗಿ ನೈಸರ್ಗಿಕ ಸಂಭಾಷಣೆ',
        languages: '12 ಭಾಷೆಗಳು',
        languagesDesc: 'ಭಾರತೀಯ ಭಾಷೆಗಳಿಗೆ ಸಂಪೂರ್ಣ ಬೆಂಬಲ',
        voiceVision: 'ಧ್ವನಿ ಮತ್ತು ದೃಷ್ಟಿ',
        voiceVisionDesc: 'ಮಲ್ಟಿ-ಮೋಡಲ್ ಇನ್‌ಪುಟ್ ಬೆಂಬಲ'
      },
      actions: {
        getStarted: 'ಪ್ರಾರಂಭಿಸಿ',
        registerNow: 'ಈಗ ನೋಂದಣಿ ಮಾಡಿ'
      },
      auth: {
        login: 'ಲಾಗಿನ್',
        register: 'ನೋಂದಣಿ',
        email: 'ಇಮೇಲ್',
        password: 'ಪಾಸ್‌ವರ್ಡ್',
        confirmPassword: 'ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ',
        rememberMe: 'ನನ್ನನ್ನು ನೆನಪಿಡಿ',
        forgotPassword: 'ಪಾಸ್‌ವರ್ಡ್ ಮರೆತಿರುವಿರಾ?',
        dontHaveAccount: 'ಖಾತೆ ಇಲ್ಲವೇ?',
        alreadyHaveAccount: 'ಈಗಾಗಲೇ ಖಾತೆ ಹೊಂದಿರುವಿರಾ?',
        firstName: 'ಮೊದಲ ಹೆಸರು',
        lastName: 'ಕೊನೆಯ ಹೆಸರು',
        username: 'ಬಳಕೆದಾರ ಹೆಸರು',
        mobileNumber: 'ಮೊಬೈಲ್ ಸಂಖ್ಯೆ',
        address: 'ವಿಳಾಸ',
        language: 'ಭಾಷೆ',
        termsAccept: 'ನಾನು ಒಪ್ಪುತ್ತೇನೆ',
        termsConditions: 'ನಿಯಮಗಳು ಮತ್ತು ಷರತ್ತುಗಳು',
        privacyPolicy: 'ಗೋಪ್ಯತಾ ನೀತಿ',
        and: 'ಮತ್ತು',
        creatingAccount: 'ಖಾತೆಯನ್ನು ರಚಿಸಲಾಗುತ್ತಿದೆ...',
        loggingIn: 'ಲಾಗಿನ್ ಆಗುತ್ತಿದೆ...',
        createAccount: 'ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್‌ಗ್ರೀವ್ ಖಾತೆಯನ್ನು ರಚಿಸಿ'
      }
    }
  },
  ml: {
    translation: {
      common: {
        appName: 'സ്മാർട്ട്ഗ്രീവ്',
        welcome: 'സ്വാഗതം',
        tagline: 'സംസാരിക്കുക. ടൈപ്പ് ചെയ്യുക. പരിഹരിക്കുക.'
      },
      navigation: {
        home: 'ഹോം',
        login: 'ലോഗിൻ',
        register: 'രജിസ്റ്റർ',
        dashboard: 'ഡാഷ്ബോർഡ്',
        aiChat: 'AI ചാറ്റ്',
        myComplaints: 'എന്റെ പരാതികൾ',
        profile: 'പ്രൊഫൈൽ',
        settings: 'ക്രമീകരണങ്ങൾ',
        logout: 'ലോഗൗട്ട്'
      },
      dashboard: {
        welcomeBack: 'തിരികെ സ്വാഗതം',
        totalComplaints: 'മൊത്തം പരാതികൾ',
        pending: 'തീർപ്പാക്കാത്തത്',
        inProgress: 'പുരോഗമിക്കുന്നു',
        resolved: 'പരിഹരിച്ചു',
        thisWeek: 'ഈ ആഴ്ച',
        needAttention: 'ശ്രദ്ധ ആവശ്യമാണ്',
        updatedToday: 'ഇന്ന് അപ്ഡേറ്റ് ചെയ്തു',
        satisfaction: 'സംതൃപ്തി',
        recentComplaints: 'സമീപകാല പരാതികൾ',
        viewAll: 'എല്ലാ പരാതികളും കാണുക'
      },
      features: {
        aiChatbot: 'AI ചാറ്റ്ബോട്ട്',
        aiChatbotDesc: 'പരാതി സമർപ്പിക്കുന്നതിനുള്ള സ്വാഭാവിക സംഭാഷണം',
        languages: '12 ഭാഷകൾ',
        languagesDesc: 'ഇന്ത്യൻ ഭാഷകൾക്കുള്ള പൂർണ്ണ പിന്തുണ',
        voiceVision: 'വോയ്‌സും വിഷനും',
        voiceVisionDesc: 'മൾട്ടി-മോഡൽ ഇൻപുട്ട് പിന്തുണ'
      },
      actions: {
        getStarted: 'ആരംഭിക്കുക',
        registerNow: 'ഇപ്പോൾ രജിസ്റ്റർ ചെയ്യുക'
      },
      auth: {
        login: 'ലോഗിൻ',
        register: 'രജിസ്റ്റർ',
        email: 'ഇമെയിൽ',
        password: 'പാസ്‌വേഡ്',
        confirmPassword: 'പാസ്‌വേഡ് സ്ഥിരീകരിക്കുക',
        rememberMe: 'എന്നെ ഓർമ്മിക്കുക',
        forgotPassword: 'പാസ്‌വേഡ് മറന്നോ?',
        dontHaveAccount: 'അക്കൗണ്ട് ഇല്ലേ?',
        alreadyHaveAccount: 'ഇതിനകം അക്കൗണ്ട് ഉണ്ടോ?',
        firstName: 'ആദ്യ പേര്',
        lastName: 'അവസാന പേര്',
        username: 'ഉപയോക്തൃനാമം',
        mobileNumber: 'മൊബൈൽ നമ്പർ',
        address: 'വിലാസം',
        language: 'ഭാഷ',
        termsAccept: 'ഞാൻ സമ്മതിക്കുന്നു',
        termsConditions: 'നിബന്ധനകളും വ്യവസ്ഥകളും',
        privacyPolicy: 'സ്വകാര്യതാ നയം',
        and: 'ഒപ്പം',
        creatingAccount: 'അക്കൗണ്ട് സൃഷ്ടിക്കുന്നു...',
        loggingIn: 'ലോഗിൻ ചെയ്യുന്നു...',
        createAccount: 'നിങ്ങളുടെ സ്മാർട്ട്ഗ്രീവ് അക്കൗണ്ട് സൃഷ്ടിക്കുക'
      }
    }
  },
  or: {
    translation: {
      common: {
        appName: 'ସ୍ମାର୍ଟଗ୍ରୀଭ୍',
        welcome: 'ସ୍ୱାଗତ',
        tagline: 'କଥା କୁହନ୍ତୁ। ଟାଇପ୍ କରନ୍ତୁ। ସମାଧାନ କରନ୍ତୁ।'
      },
      navigation: {
        home: 'ହୋମ୍',
        login: 'ଲଗଇନ୍',
        register: 'ରେଜିଷ୍ଟର',
        dashboard: 'ଡ୍ୟାସବୋର୍ଡ',
        aiChat: 'AI ଚାଟ୍',
        myComplaints: 'ମୋର ଅଭିଯୋଗ',
        profile: 'ପ୍ରୋଫାଇଲ୍',
        settings: 'ସେଟିଂସ',
        logout: 'ଲଗଆଉଟ୍'
      },
      dashboard: {
        welcomeBack: 'ଫେରି ସ୍ୱାଗତ',
        totalComplaints: 'ମୋଟ ଅଭିଯୋଗ',
        pending: 'ବିଚାରାଧୀନ',
        inProgress: 'ଅଗ୍ରଗତିରେ',
        resolved: 'ସମାଧାନ ହୋଇଛି',
        thisWeek: 'ଏହି ସପ୍ତାହ',
        needAttention: 'ଧ୍ୟାନ ଆବଶ୍ୟକ',
        updatedToday: 'ଆଜି ଅପଡେଟ୍ ହୋଇଛି',
        satisfaction: 'ସନ୍ତୋଷ',
        recentComplaints: 'ସାମ୍ପ୍ରତିକ ଅଭିଯୋଗ',
        viewAll: 'ସମସ୍ତ ଅଭିଯୋଗ ଦେଖନ୍ତୁ'
      },
      features: {
        aiChatbot: 'AI ଚାଟବଟ୍',
        aiChatbotDesc: 'ଅଭିଯୋଗ ଦାଖଲ ପାଇଁ ପ୍ରାକୃତିକ ବାର୍ତ୍ତାଳାପ',
        languages: '12 ଭାଷା',
        languagesDesc: 'ଭାରତୀୟ ଭାଷା ପାଇଁ ସମ୍ପୂର୍ଣ୍ଣ ସମର୍ଥନ',
        voiceVision: 'ଭଏସ୍ ଏବଂ ଭିଜନ୍',
        voiceVisionDesc: 'ମଲ୍ଟି-ମୋଡାଲ୍ ଇନପୁଟ୍ ସମର୍ଥନ'
      },
      actions: {
        getStarted: 'ଆରମ୍ଭ କରନ୍ତୁ',
        registerNow: 'ବର୍ତ୍ତମାନ ରେଜିଷ୍ଟର କରନ୍ତୁ'
      },
      auth: {
        login: 'ଲଗଇନ୍',
        register: 'ରେଜିଷ୍ଟର',
        email: 'ଇମେଲ୍',
        password: 'ପାସୱାର୍ଡ',
        confirmPassword: 'ପାସୱାର୍ଡ ନିଶ୍ଚିତ କରନ୍ତୁ',
        rememberMe: 'ମୋତେ ମନେରଖନ୍ତୁ',
        forgotPassword: 'ପାସୱାର୍ଡ ଭୁଲିଗଲେ?',
        dontHaveAccount: 'ଖାତା ନାହିଁ?',
        alreadyHaveAccount: 'ପୂର୍ବରୁ ଖାତା ଅଛି?',
        firstName: 'ପ୍ରଥମ ନାମ',
        lastName: 'ଶେଷ ନାମ',
        username: 'ଉପଯୋଗକର୍ତ୍ତା ନାମ',
        mobileNumber: 'ମୋବାଇଲ୍ ନମ୍ବର',
        address: 'ଠିକଣା',
        language: 'ଭାଷା',
        termsAccept: 'ମୁଁ ସହମତ',
        termsConditions: 'ନିୟମ ଏବଂ ସର୍ତ୍ତ',
        privacyPolicy: 'ଗୋପନୀୟତା ନୀତି',
        and: 'ଏବଂ',
        creatingAccount: 'ଖାତା ସୃଷ୍ଟି ହେଉଛି...',
        loggingIn: 'ଲଗଇନ୍ ହେଉଛି...',
        createAccount: 'ଆପଣଙ୍କର ସ୍ମାର୍ଟଗ୍ରୀଭ୍ ଖାତା ସୃଷ୍ଟି କରନ୍ତୁ'
      }
    }
  },
  pa: {
    translation: {
      common: {
        appName: 'ਸਮਾਰਟਗ੍ਰੀਵ',
        welcome: 'ਸੁਆਗਤ ਹੈ',
        tagline: 'ਗੱਲ ਕਰੋ। ਟਾਈਪ ਕਰੋ। ਹੱਲ ਕਰੋ।'
      },
      navigation: {
        home: 'ਹੋਮ',
        login: 'ਲੌਗਇਨ',
        register: 'ਰਜਿਸਟਰ',
        dashboard: 'ਡੈਸ਼ਬੋਰਡ',
        aiChat: 'AI ਚੈਟ',
        myComplaints: 'ਮੇਰੀਆਂ ਸ਼ਿਕਾਇਤਾਂ',
        profile: 'ਪ੍ਰੋਫਾਈਲ',
        settings: 'ਸੈਟਿੰਗਾਂ',
        logout: 'ਲੌਗਆਊਟ'
      },
      dashboard: {
        welcomeBack: 'ਵਾਪਸੀ ਤੇ ਸੁਆਗਤ ਹੈ',
        totalComplaints: 'ਕੁੱਲ ਸ਼ਿਕਾਇਤਾਂ',
        pending: 'ਬਕਾਇਆ',
        inProgress: 'ਪ੍ਰਗਤੀ ਵਿੱਚ',
        resolved: 'ਹੱਲ ਹੋ ਗਿਆ',
        thisWeek: 'ਇਸ ਹਫ਼ਤੇ',
        needAttention: 'ਧਿਆਨ ਦੀ ਲੋੜ ਹੈ',
        updatedToday: 'ਅੱਜ ਅਪਡੇਟ ਕੀਤਾ ਗਿਆ',
        satisfaction: 'ਸੰਤੁਸ਼ਟੀ',
        recentComplaints: 'ਤਾਜ਼ਾ ਸ਼ਿਕਾਇਤਾਂ',
        viewAll: 'ਸਾਰੀਆਂ ਸ਼ਿਕਾਇਤਾਂ ਦੇਖੋ'
      },
      features: {
        aiChatbot: 'AI ਚੈਟਬੋਟ',
        aiChatbotDesc: 'ਸ਼ਿਕਾਇਤ ਜਮ੍ਹਾ ਕਰਨ ਲਈ ਕੁਦਰਤੀ ਗੱਲਬਾਤ',
        languages: '12 ਭਾਸ਼ਾਵਾਂ',
        languagesDesc: 'ਭਾਰਤੀ ਭਾਸ਼ਾਵਾਂ ਲਈ ਪੂਰਾ ਸਮਰਥਨ',
        voiceVision: 'ਆਵਾਜ਼ ਅਤੇ ਦ੍ਰਿਸ਼ਟੀ',
        voiceVisionDesc: 'ਮਲਟੀ-ਮੋਡਲ ਇਨਪੁੱਟ ਸਮਰਥਨ'
      },
      actions: {
        getStarted: 'ਸ਼ੁਰੂ ਕਰੋ',
        registerNow: 'ਹੁਣੇ ਰਜਿਸਟਰ ਕਰੋ'
      },
      auth: {
        login: 'ਲੌਗਇਨ',
        register: 'ਰਜਿਸਟਰ',
        email: 'ਈਮੇਲ',
        password: 'ਪਾਸਵਰਡ',
        confirmPassword: 'ਪਾਸਵਰਡ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ',
        rememberMe: 'ਮੈਨੂੰ ਯਾਦ ਰੱਖੋ',
        forgotPassword: 'ਪਾਸਵਰਡ ਭੁੱਲ ਗਏ?',
        dontHaveAccount: 'ਖਾਤਾ ਨਹੀਂ ਹੈ?',
        alreadyHaveAccount: 'ਪਹਿਲਾਂ ਹੀ ਖਾਤਾ ਹੈ?',
        firstName: 'ਪਹਿਲਾ ਨਾਮ',
        lastName: 'ਆਖਰੀ ਨਾਮ',
        username: 'ਉਪਯੋਗਕਰਤਾ ਨਾਮ',
        mobileNumber: 'ਮੋਬਾਈਲ ਨੰਬਰ',
        address: 'ਪਤਾ',
        language: 'ਭਾਸ਼ਾ',
        termsAccept: 'ਮੈਂ ਸਹਿਮਤ ਹਾਂ',
        termsConditions: 'ਨਿਯਮ ਅਤੇ ਸ਼ਰਤਾਂ',
        privacyPolicy: 'ਗੋਪਨੀਯਤਾ ਨੀਤੀ',
        and: 'ਅਤੇ',
        creatingAccount: 'ਖਾਤਾ ਬਣਾਇਆ ਜਾ ਰਿਹਾ ਹੈ...',
        loggingIn: 'ਲੌਗ ਇਨ ਹੋ ਰਿਹਾ ਹੈ...',
        createAccount: 'ਆਪਣਾ ਸਮਾਰਟਗ੍ਰੀਵ ਖਾਤਾ ਬਣਾਓ'
      }
    }
  },
  ur: {
    translation: {
      common: {
        appName: 'سمارٹ گریو',
        welcome: 'خوش آمدید',
        tagline: 'بات کریں۔ ٹائپ کریں۔ حل کریں۔'
      },
      navigation: {
        home: 'ہوم',
        login: 'لاگ ان',
        register: 'رجسٹر',
        dashboard: 'ڈیش بورڈ',
        aiChat: 'AI چیٹ',
        myComplaints: 'میری شکایات',
        profile: 'پروفائل',
        settings: 'ترتیبات',
        logout: 'لاگ آؤٹ'
      },
      dashboard: {
        welcomeBack: 'واپسی پر خوش آمدید',
        totalComplaints: 'کل شکایات',
        pending: 'زیر التواء',
        inProgress: 'جاری',
        resolved: 'حل ہو گئی',
        thisWeek: 'اس ہفتے',
        needAttention: 'توجہ کی ضرورت ہے',
        updatedToday: 'آج اپ ڈیٹ کیا گیا',
        satisfaction: 'اطمینان',
        recentComplaints: 'حالیہ شکایات',
        viewAll: 'تمام شکایات دیکھیں'
      },
      features: {
        aiChatbot: 'AI چیٹ بوٹ',
        aiChatbotDesc: 'شکایت جمع کرانے کے لیے قدرتی گفتگو',
        languages: '12 زبانیں',
        languagesDesc: 'ہندوستانی زبانوں کے لیے مکمل معاونت',
        voiceVision: 'آواز اور بصارت',
        voiceVisionDesc: 'ملٹی موڈل ان پٹ سپورٹ'
      },
      actions: {
        getStarted: 'شروع کریں',
        registerNow: 'ابھی رجسٹر کریں'
      },
      auth: {
        login: 'لاگ ان',
        register: 'رجسٹر',
        email: 'ای میل',
        password: 'پاس ورڈ',
        confirmPassword: 'پاس ورڈ کی تصدیق کریں',
        rememberMe: 'مجھے یاد رکھیں',
        forgotPassword: 'پاس ورڈ بھول گئے?',
        dontHaveAccount: 'اکاؤنٹ نہیں ہے؟',
        alreadyHaveAccount: 'پہلے سے اکاؤنٹ ہے؟',
        firstName: 'پہلا نام',
        lastName: 'آخری نام',
        username: 'صارف نام',
        mobileNumber: 'موبائل نمبر',
        address: 'پتہ',
        language: 'زبان',
        termsAccept: 'میں متفق ہوں',
        termsConditions: 'شرائط و ضوابط',
        privacyPolicy: 'رازداری کی پالیسی',
        and: 'اور',
        creatingAccount: 'اکاؤنٹ بنایا جا رہا ہے...',
        loggingIn: 'لاگ ان ہو رہا ہے...',
        createAccount: 'اپنا سمارٹ گریو اکاؤنٹ بنائیں'
      }
    }
  }
};

// Get saved language from localStorage or default to 'en'
const savedLanguage = localStorage.getItem('language') || 'en';

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: savedLanguage,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

// Listen for language changes and save to localStorage
i18n.on('languageChanged', (lng) => {
  localStorage.setItem('language', lng);
});

export default i18n;
