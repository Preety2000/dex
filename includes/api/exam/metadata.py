from typing import List
from includes.core.security import AUTH_TOKEN, _Security
from includes.utils.exm import get_folder_key
from includes.core.globals.entry import app_context
from includes.db.models.db_exam import _ExamDetails, _TeacherProfile
from includes.utils.utils import get_post_value
from includes.db.models.utils import TimeStamp


def get_selected_classes(selected_ids: List[str]) -> List[List[str]]:
    return [item for item in exam_category if item[0] in selected_ids]


exam_category: List[List[str]] = [
    ["ssc_mts", "SSC MTS"],
    ["ssc_gd", "SSC GD Constable"],
    ["ssc", "Secondary School Certificate (SSC)"],
    ["hsc", "Higher Secondary Certificate (HSC)"],
    ["upsc", "Union Public Service Commission (UPSC)"],
    ["ias", "Indian Administrative Service (IAS)"],
    ["ips", "Indian Police Service (IPS)"],
    ["irs", "Indian Revenue Service (IRS)"],
    ["ifs", "Indian Foreign Service (IFS)"],
    ["pcs", "Provincial Civil Services (PCS)"],
    ["neet", "National Eligibility cum Entrance Test (NEET)"],
    ["jee", "Joint Entrance Examination (JEE)"],
    ["nda", "National Defence Academy (NDA)"],
    ["cds", "Combined Defence Services (CDS)"],
    ["afcat", "Air Force Common Admission Test (AFCAT)"],
    ["ssc_cgl", "SSC Combined Graduate Level (CGL)"],
    ["ssc_chsl", "SSC Combined Higher Secondary Level (CHSL)"],
    ["bank_po", "Bank Probationary Officer (Bank PO)"],
    ["ibps_po", "IBPS PO Exam"],
    ["ibps_clerk", "IBPS Clerk Exam"],
    ["rbi_grade_b", "RBI Grade B Exam"],
    ["rbi_assistant", "RBI Assistant Exam"],
    ["railway_exam", "Railway Recruitment Exam"],
    ["rrb_ntpc", "RRB NTPC Exam"],
    ["rrb_group_d", "RRB Group D Exam"],
    ["tet", "Teacher Eligibility Test (TET)"],
    ["ctet", "Central Teacher Eligibility Test (CTET)"],
    ["state_tet", "State TET Exam"],
    ["clat", "Common Law Admission Test (CLAT)"],
    ["gate", "Graduate Aptitude Test in Engineering (GATE)"],
    ["ugc_net", "UGC National Eligibility Test (NET)"],
    ["delhi_police", "Delhi Police Exam"],
]

limitStatusHtml = {
    "English": {
        "title": "🚫 Daily Test Limit Reached!",
        "content": [
            "You’ve reached your test limit for today. Upgrade to our ₹50/month plan to enjoy unlimited exam and priority support.",
            {
                "tagName": "a",
                "inner": "👉 Click here for plan details",
                "href": "/plans",
            },
        ],
    },
    "Hindi": {
        "title": "🚫 आज का टेस्ट लिमिट पूरा हो चुका है!",
        "content": [
            "आपने आज के लिए अपने टेस्ट की सीमा पूरी कर ली है। ₹50/महीने के प्लान को अपग्रेड करें और अनलिमिटेड टेस्ट एवं प्राथमिकता सहायता का लाभ उठाएं।",
            {
                "tagName": "a",
                "inner": "👉 प्लान की जानकारी के लिए यहां क्लिक करें",
                "href": "/plans",
            },
        ],
    },
    "Sanskrit": {
        "title": "🚫 दैनिक परीक्षणसीमा समाप्ता",
        "content": [
            "त्वं अद्यत् परीक्षणसीमां प्राप्तवान्। ₹५०/मासिकं योजनां उन्नयित्वा अनन्तपरीक्षणान् प्रथमताम् च सहायं लभस्व।",
            {
                "tagName": "a",
                "inner": "👉 योजनाविवरणाय अत्र स्पृष्टव्यम्",
                "href": "/plans",
            },
        ],
    },
    "Telugu": {
        "title": "🚫 దైనందిన పరీక్ష పరిమితి చేరింది",
        "content": [
            "మీరు ఈ రోజు కోసం మీ పరీక్ష పరిమితిని చేరుకున్నారు. ₹50/నెల ప్లాన్‌ను అప్‌గ్రేడ్ చేసి, అన్‌లిమిటెడ్ పరీక్షలు మరియు ప్రాధాన్యత మద్దతును పొందండి.",
            {
                "tagName": "a",
                "inner": "👉 ప్లాన్ వివరాలకు ఇక్కడ క్లిక్ చేయండి",
                "href": "/plans",
            },
        ],
    },
    "Tamil": {
        "title": "🚫 தினசரி தேர்வு வரம்பு கடந்துவிட்டது",
        "content": [
            "இன்று உங்கள் தேர்வு வரம்பை கடந்துவிட்டீர்கள். ₹50/மாத திட்டத்தை மேம்படுத்து, வரம்பற்ற தேர்வுகள் மற்றும் முன்னுரிமை ஆதரவை அனுபவிக்க.",
            {
                "tagName": "a",
                "inner": "👉 திட்ட விவரங்களுக்கு இங்கே கிளிக் செய்க",
                "href": "/plans",
            },
        ],
    },
}

AccessRestricted = {
    "English": {
        "__ac": 405,
        "title": "Access Restricted: Teacher Verification Required",
        "content": [
            "If you are indeed a teacher, please fill out the verification form below. Once the verification process is complete, you will gain full access to all the special features, resources, and plans we offer exclusively for educators.",
            "We appreciate your dedication to teaching and look forward to supporting you.",
            {
                "tagName": "a",
                "inner": "👉 Click here to fill out the Verification Form",
                "href": "/ut/accounts/teacher/verify-indentity",
            },
        ],
    },
    "Hindi": {
        "__ac": 405,
        "title": "पहुंच सीमित: शिक्षक सत्यापन आवश्यक",
        "content": [
            "यदि आप वास्तव में एक शिक्षक हैं, तो कृपया नीचे दिया गया सत्यापन फॉर्म भरें। एक बार सत्यापन प्रक्रिया पूरी हो जाने के बाद, आपको उन सभी विशेष सुविधाओं, संसाधनों और योजनाओं तक पूर्ण पहुंच मिल जाएगी जो हम केवल शिक्षकों के लिए प्रदान करते हैं।",
            "हम आपके शिक्षण के प्रति समर्पण की सराहना करते हैं और आपका समर्थन करने के लिए तत्पर हैं।",
            {
                "tagName": "a",
                "inner": "👉 सत्यापन फॉर्म भरने के लिए यहां क्लिक करें",
                "href": "/ut/accounts/teacher/verify-indentity",
            },
        ],
    },
    "Sanskrit": {
        "__ac": 405,
        "title": "प्रवेशः निरुद्धः: शिक्षक-सत्यापनम् आवश्यकम्",
        "content": [
            "यदि भवान्/भवती सत्यमेव शिक्षकः/शिक्षिका अस्ति, कृपया अधोलिखितं सत्यापन-पत्रं पूरयतु। सत्यापनप्रक्रिया समाप्ता सति, शिक्षकेभ्यः विशिष्टान् सुविधाः, साधनानि, योजनाः च पूर्णरूपेण उपलब्धाः भविष्यन्ति।",
            "शिक्षणं प्रति भवतः समर्पणम् वयं सराहामः, च शीघ्रं सहयोगं दातुं उत्सुकाः स्मः।",
            {
                "tagName": "a",
                "inner": "👉 सत्यापनपञ़ं पूरयितुं अत्र क्लिक कुर्वन्तु",
                "href": "/ut/accounts/teacher/verify-indentity",
            },
        ],
    },
    "Telugu": {
        "__ac": 405,
        "title": "ప్రవేశం పరిమితం: ఉపాధ్యాయ ధృవీకరణ అవసరం",
        "content": [
            "మీరు నిజంగా ఉపాధ్యాయుడే అయితే, దయచేసి క్రింద ఉన్న ధృవీకరణ ఫారాన్ని పూరించండి. ధృవీకరణ ప్రక్రియ పూర్తయిన తర్వాత, మేము ఉపాధ్యాయులకోసం ప్రత్యేకంగా అందించే అన్ని ప్రత్యేక లక్షణాలు, వనరులు మరియు ప్రణాళికలకు మీకు పూర్తి ప్రాప్యత లభిస్తుంది.",
            "మీ బోధనకు మీరు చూపిన నిబద్ధతకు మేము కృతజ్ఞతలు తెలియజేస్తున్నాము మరియు మద్దతు ఇవ్వడానికి ఎదురు చూస్తున్నాము.",
            {
                "tagName": "a",
                "inner": "👉 ధృవీకరణ ఫారాన్ని పూరించడానికి ఇక్కడ క్లిక్ చేయండి",
                "href": "/ut/accounts/teacher/verify-indentity",
            },
        ],
    },
    "Tamil": {
        "__ac": 405,
        "title": "அணுகல் கட்டுப்பாடு: ஆசிரியர் சரிபார்ப்பு தேவை",
        "content": [
            "நீங்கள் உண்மையில் ஒரு ஆசிரியர் எனில், கீழே உள்ள சரிபார்ப்பு படிவத்தை நிரப்பவும். சரிபார்ப்பு நடைமுறை முடிந்ததும், ஆசிரியர்களுக்கே வழங்கப்படும் அனைத்து சிறப்பு அம்சங்கள், வளங்கள் மற்றும் திட்டங்களை முழுமையாக அணுகலாம்.",
            "உங்கள் கல்வி சேவையை நாங்கள் மதிக்கிறோம், மேலும் உங்களுக்கு ஆதரவு அளிக்க விரும்புகிறோம்.",
            {
                "tagName": "a",
                "inner": "👉 சரிபார்ப்பு படிவத்தை நிரப்ப இங்கே கிளிக் செய்யவும்",
                "href": "/ut/accounts/teacher/verify-indentity",
            },
        ],
    },
}

ImportantSettingsUpload = {
    "English": {
        "__ac": 405,
        "title": "Upload",
        "content": [
            "These settings allow you to control key behaviors of your test or class. You can manage features such as late joining, re-attempts, question shuffling, and result visibility to ensure a smooth and secure experience for both students and instructors."
        ],
        "useForms": [
            {
                "listType": "input",
                "value": {
                    "type": "text",
                    "required": True,
                    "title": "🔗Enter Name",
                    "desc": "Choose how students can request to join your class. You can allow only listed students to join directly, allow listed students to send requests, or open requests to all students.",
                    "name": "_name",
                    "value": "",
                },
            },
            {
                "listType": "image",
                "value": {
                    "type": "file",
                    "accept": "image/*",
                    "required": True,
                    "title": "🔗Upload Photo",
                    "desc": "Choose how students can request to join your class. You can allow only listed students to join directly, allow listed students to send requests, or open requests to all students.",
                    "name": "_photo",
                    "value": "",
                    "info": {
                        "type": "image",
                        "x": "100x100",
                    },
                },
            },
        ],
    },
}

testSubmitted = {
    "English": {
        "title": "Test Submitted Successfully!",
        "desc": [
            "Thank you for completing the test.",
            "Your answers have been submitted successfully.",
            "You will receive your results shortly.",
        ],
    }
}

requestTimeOutMessage = {
    "English": {
        "title": "Time’s Up!",
        "desc": [
            "It looks like your request took too long and couldn’t be completed.",
            "Don't worry — you can try again.",
            "If the issue persists, contact support for help.",
        ],
    }
}


s_meta_data = {
    "req_appr_mode": {
        "English": {
            "class": "join-request-action",
            "type": "button",
            "required": True,
            "title": "Join Request Handling",
            "desc": "Choose how incoming student join requests should be handled.",
            "name": "req_appr_mode",
            "checked": "manual",
            "value": [
                {
                    "title": "Auto Accept Requests",
                    "desc": "All eligible student join requests will be approved automatically without requiring your review.",
                    "value": "auto_accept",
                },
                {
                    "title": "Auto Reject Requests",
                    "desc": "All incoming join requests will be declined automatically, preventing students from joining the class.",
                    "value": "auto_reject",
                },
                {
                    "title": "Manual Approval",
                    "desc": "Review each join request individually and decide whether to accept or reject it.",
                    "value": "manual",
                },
            ],
        },
    },
    "open_request": {
        "English": {
            "class": "join-request-expiry",
            "type": "button",
            "required": True,
            "title": "Join Request Availability",
            "desc": "Choose when students can send join requests to your class.",
            "name": "open_request",
            "checked": "active_only",
            "value": [
                {
                    "title": "Only When You're Active",
                    "desc": "Students can send join requests only while you are online or actively managing the class.",
                    "value": "active_only",
                },
                {
                    "title": "Available for 24 Hours",
                    "desc": "Students can send join requests for up to 24 hours after you share the invite.",
                    "value": "24_hours",
                },
                {
                    "title": "Available Until You Disable It",
                    "desc": "Students can send join requests at any time until you manually turn off joining.",
                    "value": "lifetime",
                },
            ],
        }
    },
    "join_mode": {
        "English": {
            "class": "join-settings",
            "type": "button",
            "required": True,
            "title": "Join Request Settings",
            "desc": "Control how students can join your class. You can limit access to listed students, allow requests, or open it to everyone.",
            "name": "join_mode",
            "checked": "openAccessRequests",
            "value": [
                {
                    "title": "Direct Access (Listed Students)",
                    "desc": "Only students pre-added to your class roster can join directly without requiring approval.",
                    "value": "directAccess",
                },
                {
                    "title": "Approval Required (Listed Students)",
                    "desc": "Only students in your roster may request access. Each request must be reviewed and approved by you.",
                    "value": "approvalRequired",
                },
                {
                    "title": "Open Access Requests",
                    "desc": "All students can submit join requests. You retain full control to review and approve each request.",
                    "value": "openAccessRequests",
                },
            ],
        }
    },
    "result_visibility": {
        "English": {
            "class": "result-visibility",
            "type": "button",
            "required": True,
            "title": "Test Result Visibility",
            "desc": "Choose how the test results will be published.",
            "name": "result_visibility",
            "checked": "manual_publish",
            "value": [
                {"title": "Auto Publish", "value": "auto_publish"},
                {"title": "Manual Publish", "value": "manual_publish"},
            ],
        }
    },
    "exam_category": {
        "English": {
            "class": "class",
            "required": True,
            "title": "Exam Class",
            "desc": "Choose the class this exam is intended for. You may also select 'Any' to allow all students to participate.",
            "name": "exam_category",
            "value": exam_category,
        }
    },
}

s_meta_value = {
    "req_appr_mode": ["auto_accept", "auto_reject", "manual"],
    "open_request": ["active_only", "24_hours", "lifetime"],
    "result_visibility": ["auto_publish", "manual_publish"],
    "join_mode": ["directAccess", "approvalRequired", "openAccessRequests"],
}


def get_class_name(code):
    for item in exam_category:
        if item[0] == code:
            return item[1]

    return "Default"


async def exam_setting_setter(record, values=None):
    update = False
    for i in ["join_mode", "open_request", "req_appr_mode", "result_visibility"]:
        optin = s_meta_value.get(i, [])
        value = values.pop(i, None) if values else await get_post_value(i)
        if value and value in optin:
            update = True
            setattr(record, i, optin.index(value))

    return update, record


def get_mode_option_title(name, value: str, language: str = "English") -> str | None:

    m = s_meta_data.get(name, {}).get(language, {}).get("value", [])
    for mode in m:
        if mode["value"] == value:
            return mode["title"]

    return None


async def build_settings_page(
    language, record: _TeacherProfile | _ExamDetails | None = None, message: bool = None
):
    behavior_items = []

    behavior_section = {
        "title": "Important Settings",
        "desc": "Configure the default settings for your exam. These preferences will be applied automatically when a new exam is created and can be changed later if needed.",
        "data": behavior_items,
    }

    account_section = {
        "title": "Complete Your Profile",
        "desc": (
            "Complete your profile by adding your name, profile photo, "
            "signature, and biography."
        ),
        "name": None,
        "img": "/media/icon/member.png",
        "signature": None,
        "biography": None,
    }

    for key, metadata in s_meta_data.items():
        setting = metadata[language].copy()

        if record is not None:
            current_value = getattr(record, key, None)

            if current_value is not None:
                value_mapper = s_meta_value.get(key)

                setting["checked"] = (
                    current_value
                    if value_mapper is None
                    else value_mapper[current_value]
                )

        if (
            key == "exam_category"
            and isinstance(record, _ExamDetails)
            and isinstance(record.teacher_record, _TeacherProfile)
        ):
            setting["css"] = {
                "gridTemplateColumns": "repeat(auto-fit, minmax(310px, 1fr))"
            }

            setting["checked"] = record.exam_category

            setting["value"] = [
                item
                for item in exam_category
                if item[0] in record.teacher_record.exam_category
            ]

            setting["value"].insert(0, ["any", "Default"])

        behavior_items.append(
            {
                "listType": "checkbox" if key == "exam_category" else "radio",
                "value": setting,
            }
        )

    if isinstance(record, _TeacherProfile):
        account_section.update(
            {
                "key": get_folder_key(record.id),
                "title": "Account Settings",
                "desc": (
                    "Manage your profile information, signature, and account details."
                ),
                "name": record.name,
                "img": record.img,
                "signature": record.signature,
                "biography": record.biography,
            }
        )

    elif isinstance(record, _ExamDetails):
        behavior_section["title"] = "Exam Settings"
        behavior_section["desc"] = (
            "Update the settings for this exam, including scheduling, notifications, student access, attempts, question behavior, and result visibility."
        )

        behavior_items.insert(
            4,
            {
                "use_update": True,
                "value": {
                    "start_timestamp": record.start_timestamp,
                    "startTimeFormat": TimeStamp.format_ts(
                        record.start_timestamp, "%d %B, %Y at %I:%M %p"
                    ),
                    "publish_timestamp": record.publish_timestamp,
                    "publishTimeFormat": TimeStamp.format_ts(
                        record.publish_timestamp, "%d %B, %Y at %I:%M %p"
                    ),
                },
            },
        )

        behavior_items.append(
            {
                "listType": "switchHolder",
                "value": {
                    "title": "Notify Students",
                    "desc": (
                        "Send a notification to students when the exam becomes available."
                    ),
                    "name": "notification",
                    "value": record.notification,
                },
            }
        )
    else:
        member = await app_context.setting.member()
        account_section["key"] = get_folder_key(int(member.get("id")))
        account_section["name"] = member.get("name")
        account_section["biography"] = member.get("biography")
        # message

    returns = {
        "__ac": 405,
        "title": "Settings",
        "account": account_section,
        "behaviors": behavior_section,
        **({"use_action": True} if record is not None else {}),
    }

    if message is True:
        returns["message"] = "Updated successfully."

    return returns
