import re
import spacy
from pdfminer.high_level import extract_text
from docx import Document
from spacy.util import is_package

def load_spacy_model():
    try:
        if is_package("en_core_web_md"):
            return spacy.load("en_core_web_md")
        elif is_package("en_core_web_sm"):
            print("Using small spaCy model. For better results: python -m spacy download en_core_web_md")
            return spacy.load("en_core_web_sm")
        else:
            raise ImportError("No spaCy model found. Install with: python -m spacy download en_core_web_sm")
    except Exception as e:
        raise RuntimeError(f"spaCy model loading failed: {str(e)}")

nlp = load_spacy_model()

def extract_text_from_file(file_path):
    try:
        if file_path.endswith('.pdf'):
            return extract_text(file_path)
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to extract text: {str(e)}")

def extract_entities(text):
    try:
        entities = {
            "name": "",
            "email": [],
            "phone": [],
            "skills": [],
            "education": [],
            "experience": [],
            "certifications": [],
            "achievements": []
        }

        # Name extraction (first line before separator)
        first_line = text.split('\n')[0].strip()
        if first_line and not any(sep in first_line for sep in ['---', '___', '===']):
            entities["name"] = first_line

        # Email and phone
        entities["email"] = list(set(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)))
        entities["phone"] = list(set(re.findall(r'(\+?\d[\d\s-]{8,}\d)', text)))

        # Education
        edu_pattern = re.compile(
            r'(B\.?\s?Tech|M\.?\s?Tech|MBA|B\.?\s?E|B\.?\s?Sc|B\.?\s?Com|B\.?\s?A).*?\n(.*?)\|.*?(\d{4}.*?\d{4})', 
            re.IGNORECASE
        )
        for match in edu_pattern.finditer(text):
            entities["education"].append(f"{match.group(1).title()} from {match.group(2).strip()} ({match.group(3).strip()})")

        # Comprehensive skill mapping with all provided skills and additional IT/CS skills
        skill_map = {
            # Programming Languages
            'javascript': ['javascript', 'js', 'es6', 'ecmascript'],
            'python': ['python', 'py'],
            'java': ['java', 'j2ee', 'j2se'],
            'c++': ['c++', 'cpp'],
            'c#': ['c#', 'csharp'],
            'php': ['php'],
            'ruby': ['ruby', 'ruby on rails'],
            'swift': ['swift'],
            'kotlin': ['kotlin'],
            'typescript': ['typescript', 'ts'],
            'go': ['go', 'golang'],
            'r': ['r'],
            
            # Frontend
            'html': ['html', 'html5'],
            'css': ['css', 'css3'],
            'react': ['react', 'reactjs', 'react.js'],
            'angular': ['angular', 'angularjs'],
            'vue.js': ['vue.js', 'vuejs', 'vue'],
            'bootstrap': ['bootstrap'],
            'jquery': ['jquery'],
            'sass': ['sass', 'scss'],
            'web accessibility': ['web accessibility', 'a11y'],
            
            # Backend
            'node.js': ['node.js', 'nodejs', 'node'],
            'express': ['express', 'express.js'],
            'django': ['django'],
            'flask': ['flask'],
            'spring': ['spring', 'spring boot'],
            'laravel': ['laravel'],
            'asp.net': ['asp.net', 'aspnet'],
            
            # Databases
            'mongodb': ['mongodb', 'mongo'],
            'mysql': ['mysql'],
            'postgresql': ['postgresql', 'postgres'],
            'sql': ['sql', 'structured query language'],
            'oracle': ['oracle'],
            'sqlite': ['sqlite'],
            'redis': ['redis'],
            
            # Data Science/AI
            'machine learning': ['machine learning', 'ml'],
            'deep learning': ['deep learning', 'dl'],
            'tensorflow': ['tensorflow', 'tf'],
            'pytorch': ['pytorch'],
            'pandas': ['pandas'],
            'numpy': ['numpy'],
            'scikit-learn': ['scikit-learn', 'sklearn'],
            'statistics': ['statistics', 'stats'],
            'data visualization': ['data visualization', 'dataviz'],
            'tableau': ['tableau'],
            'power bi': ['power bi', 'powerbi'],
            
            # DevOps/Cloud
            'aws': ['aws', 'amazon web services'],
            'azure': ['azure', 'microsoft azure'],
            'gcp': ['gcp', 'google cloud'],
            'docker': ['docker'],
            'kubernetes': ['kubernetes', 'k8s'],
            'terraform': ['terraform'],
            'ansible': ['ansible'],
            'jenkins': ['jenkins'],
            'git': ['git', 'github', 'gitlab'],
            'ci/cd': ['ci/cd', 'continuous integration', 'continuous deployment'],
            
            # Tools
            'jira': ['jira'],
            'figma': ['figma'],
            'excel': ['excel', 'advanced excel'],
            'photoshop': ['photoshop'],
            'illustrator': ['illustrator'],
            
            # Business/Soft Skills
            'agile': ['agile', 'scrum'],
            'project management': ['project management', 'pm'],
            'business analysis': ['business analysis', 'ba'],
            'communication': ['communication', 'communication skills'],
            
            # Digital Marketing
            'digital marketing': ['digital marketing', 'digitalmarketing', 'online marketing'],
            'seo/sem': ['seo', 'sem', 'search engine optimization', 'search engine marketing'],
            'google analytics': ['google analytics', 'ga', 'googleanalytics'],
            'social media marketing': ['social media marketing', 'smm', 'social media'],
            'content creation': ['content creation', 'content marketing', 'content strategy'],
            'market research': ['market research', 'competitive analysis']
        }

        # Extract skills from dedicated skills section
        skills_section = re.search(
            r'(?:SKILLS|TECHNICAL SKILLS|SKILL SET|EXPERTISE|COMPETENCIES)[\s:]*\n(.*?)(?=\n\n|\n[A-Z][A-Z]+|\n\w|$)',
            text, 
            re.IGNORECASE | re.DOTALL
        )
        
        if skills_section:
            skills_text = skills_section.group(1).lower()
            for standard_skill, variations in skill_map.items():
                if any(re.search(r'\b' + re.escape(variation) + r'\b', skills_text) for variation in variations):
                    if standard_skill not in entities["skills"]:
                        entities["skills"].append(standard_skill)

        # Also check entire text for skills not in dedicated section
        text_lower = text.lower()
        for standard_skill, variations in skill_map.items():
            if standard_skill not in entities["skills"]:  # Skip if already found
                if any(re.search(r'\b' + re.escape(variation) + r'\b', text_lower) for variation in variations):
                    entities["skills"].append(standard_skill)

        # Certifications - Robust extraction
        cert_sections = re.finditer(
            r'(?:CERTIFICATIONS|CERTIFICATE|LICENSES|TRAININGS)[\s:]*\n(.*?)(?=\n\n|\n[A-Z][A-Z]+|\n\w|$)',
            text, 
            re.IGNORECASE | re.DOTALL
        )
        for match in cert_sections:
            cert_lines = [line.strip() for line in match.group(1).split('\n') if line.strip()]
            for line in cert_lines:
                clean_line = re.sub(r'^[•\-*]\s*|\s*\(.*?\)', '', line).strip()
                if clean_line and len(clean_line) > 5 and not clean_line.upper() in ["CERTIFICATIONS", "CERTIFICATE", "LICENSES"]:
                    entities["certifications"].append(clean_line)

        # Achievements
        achievement_pattern = r'(?:achieved|implemented|increased|reduced|improved|optimized|saved|led|managed|developed|delivered|completed).*?\b\d+[%+]?\b'
        entities["achievements"] = list(set(
            re.findall(achievement_pattern, text, re.IGNORECASE)
        ))

        return entities

    except Exception as e:
        raise RuntimeError(f"Entity extraction failed: {str(e)}")