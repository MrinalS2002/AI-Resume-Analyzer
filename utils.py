import re

def display_entities(entities):
    """Display all extracted entities in a beautifully formatted markdown"""
    sections = []
    
    # Header
    sections.append("# 📄 Extracted Resume Information\n")
    
    # Basic Information
    sections.append("## 🔍 Basic Information")
    if entities["name"]:
        sections.append(f"- **Name**: {entities['name']}")
    if entities["email"]:
        sections.append(f"- **Email**: {entities['email'][0]}")
    if entities["phone"]:
        sections.append(f"- **Phone**: {entities['phone'][0]}")
    
    # Skills
    if entities["skills"]:
        sections.append("\n## 💻 Technical Skills")
        sections.append(", ".join([f"`{skill}`" for skill in sorted(entities["skills"])]))
    
    # Education
    if entities["education"]:
        sections.append("\n## 🎓 Education")
        sections.extend([f"- {edu}" for edu in entities["education"]])
    
    # Certifications (will always show if present)
    if entities["certifications"]:
        sections.append("\n## 📜 Certifications")
        sections.extend([f"- 🏅 {cert}" for cert in entities["certifications"]])
    
    # Achievements
    if entities["achievements"]:
        sections.append("\n## 🏆 Key Achievements")
        sections.extend([
            f"- ✅ {ach.strip('.').capitalize()}" 
            for ach in sorted(entities["achievements"], key=lambda x: -len(x))
        ])
    
    return "\n".join(sections)

def check_ats_compliance(text):
    """Comprehensive ATS compliance checker with detailed feedback"""
    warnings = []
    word_count = len(text.split())
    
    # Length analysis
    if word_count < 200:
        warnings.append("⚠️ **Resume Too Short**: Only {} words (Aim for 200-800 words)".format(word_count))
    elif word_count > 800:
        warnings.append("⚠️ **Resume Too Long**: {} words (Ideal is 200-800 words)".format(word_count))
    
    # Content quality checks
    if not re.search(r'\b\d+%|\b\d+\+|\$\d+|\d+\s*(years|yrs)|₹\d+', text):
        warnings.append("⚠️ **Add Quantifiable Metrics**: Include numbers like 'increased sales by 30%' or 'managed $1M budget'")
    
    if not re.search(r'\b(achieved|implemented|developed|managed|led|improved|increased)\b', text, re.IGNORECASE):
        warnings.append("⚠️ **Use Strong Action Verbs**: Start bullet points with words like 'Developed', 'Implemented', 'Led'")
    
    # Formatting checks
    formatting_issues = {
        'tables': r'\b(table|row|column)\b',
        'headers/footers': r'\b(header|footer)\b',
        'graphics': r'[■□▢▣▤▥▦▧▨▩▪▫▬▭▮▯]|⛔|█',
        'columns': r'column|text\s*box',
        'icons': r'[⚡★☆♡♥♠♣♦]'
    }
    
    for issue, pattern in formatting_issues.items():
        if re.search(pattern, text, re.IGNORECASE):
            warnings.append(f"⚠️ **Avoid {issue.replace('/', ' and ')}**: These may not parse correctly in ATS systems")
    
    return warnings