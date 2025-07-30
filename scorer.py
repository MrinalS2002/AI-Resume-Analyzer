import re
from difflib import SequenceMatcher

def skill_similarity(a, b):
    """Calculate similarity between two skill names using sequence matching"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def score_resume(entities, job_skills, exp_keywords=None, raw_text=None):
    matched_skills = []
    missing_skills = []
    
    # Normalize all skills
    resume_skills = [skill.lower().strip() for skill in entities.get('skills', [])]
    job_skills = [skill.lower().strip() for skill in job_skills]

    # For each required skill, find the best match in resume
    for required_skill in job_skills:
        best_match = None
        best_score = 0
        
        # Check against each resume skill
        for resume_skill in resume_skills:
            # Exact match
            if required_skill == resume_skill:
                best_match = resume_skill
                best_score = 1.0
                break
            
            # Partial match with similarity threshold
            current_score = skill_similarity(required_skill, resume_skill)
            if current_score > best_score and current_score > 0.7:  # 0.7 similarity threshold
                best_score = current_score
                best_match = resume_skill
        
        # Also check if skill is mentioned in text but not in skills section
        if best_score < 0.8 and raw_text:
            text_lower = raw_text.lower()
            variations = [
                required_skill,
                required_skill.replace(' ', ''),
                required_skill.replace(' ', '-'),
                required_skill.replace('/', ' '),
                required_skill.replace('/', ' and ')
            ]
            if any(re.search(r'\b' + re.escape(variation) + r'\b', text_lower) for variation in variations):
                best_match = required_skill
                best_score = 1.0
        
        if best_score >= 0.7:  # Consider it a match if similarity >= 70%
            matched_skills.append(required_skill)
        else:
            missing_skills.append(required_skill)

    # Calculate percentage
    skill_percentage = (len(matched_skills) / len(job_skills)) * 100 if job_skills else 0

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "score": round(skill_percentage),
        "max_score": 100,
        "certifications": entities.get('certifications', []),
        "achievements": entities.get('achievements', [])
    }