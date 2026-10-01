import json

# Category Keyword Mapping
CATEGORY_MAP = {
    "कोशिका विज्ञान (Cytology)": [
        "कोशिका",
        "माइटोकॉन्ड्रिया",
        "राइबोसोम",
        "लाइसोसोम",
        "गोलगी",
        "केंद्रक",
    ],
    "आनुवंशिकी (Genetics)": [
        "डीएनए",
        "आरएनए",
        "जीन",
        "गुणसूत्र",
        "आनुवंशिक",
        "क्रोमोसोम",
    ],
    "मानव शरीर विज्ञान (Human Physiology)": [
        "रक्त",
        "हृदय",
        "यकृत",
        "गुर्दा",
        "मस्तिष्क",
        "न्यूरॉन",
        "पेप्सिन",
        "इंसुलिन",
    ],
    "पादप कार्यिकी (Plant Physiology)": [
        "प्रकाश संश्लेषण",
        "क्लोरोफिल",
        "जाइलम",
        "फ्लोएम",
        "पौधे",
        "पत्ती",
    ],
    "सूक्ष्मजीव विज्ञान (Microbiology)": [
        "जीवाणु",
        "विषाणु",
        "बैक्टीरिया",
        "वायरस",
        "फंगस",
        "संक्रमण",
    ],
}


def get_category(text):
    matched_category = []
    for category, keywords in CATEGORY_MAP.items():
        if any(keyword in text for keyword in keywords):
            matched_category.append(category)
    return (
        matched_category
        if matched_category
        else ["सामान्य जीव विज्ञान (General Biology)"]
    )


# Example Matching
question_title = "मानव में इंसुलिन और रक्त शर्करा का नियंत्रण कैसे होता है?"
assigned_category = get_category(question_title)

print("Question:", question_title)
print("Matched Categories:", assigned_category)
