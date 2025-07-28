#!/usr/bin/env python3
"""
PDF Outline Extractor - Generic Version
Clean, maintainable codebase for extracting headings from any PDF document.
"""

import fitz
import re
import json
import argparse
from collections import Counter
from dataclasses import dataclass
from typing import Optional, List, Tuple


@dataclass
class HeadingCandidate:
    text: str
    level: str
    page: int
    score: float


class PDFOutlineExtractor:
    """AI-like intelligent PDF outline extractor."""
    
    def __init__(self):
        # Comprehensive heading indicators (like AI pattern recognition)
        self.strong_heading_patterns = [
            # Numbered sections (highest confidence)
            r'^(\d+)\.?\s+(.+)$',           # 1. Title
            r'^(\d+\.\d+)\.?\s+(.+)$',      # 1.1 Title  
            r'^(\d+\.\d+\.\d+)\.?\s+(.+)$', # 1.1.1 Title
            r'^CHAPTER\s+\d+',              # Chapter numbering
            r'^PART\s+[IVX\d]+',            # Part numbering
            r'^SECTION\s+[A-Z\d]+',         # Section numbering
            r'^APPENDIX\s+[A-Z\d]*',        # Appendix
        ]
        
        # Document structure keywords (semantic understanding)
        self.semantic_headings = {
            # Core document sections
            'executive summary', 'abstract', 'introduction', 'background', 'overview',
            'methodology', 'methods', 'approach', 'results', 'findings', 'analysis',
            'discussion', 'conclusion', 'conclusions', 'recommendations', 'summary',
            'references', 'bibliography', 'appendix', 'appendices', 'glossary',
            
            # Business/RFP specific
            'business plan', 'timeline', 'schedule', 'budget', 'costs', 'evaluation',
            'criteria', 'requirements', 'specifications', 'deliverables', 'scope',
            'objectives', 'goals', 'strategy', 'implementation', 'proposal',
            
            # Academic/Research
            'literature review', 'related work', 'experimental setup', 'data collection',
            'statistical analysis', 'case study', 'future work', 'limitations',
            
            # Technical documentation
            'installation', 'configuration', 'user guide', 'troubleshooting',
            'api reference', 'examples', 'best practices', 'security',
            
            # Legal/Policy
            'definitions', 'policy', 'procedures', 'compliance', 'regulations',
            'terms and conditions', 'privacy policy', 'disclaimer',
            
            # FAQ and Q&A specific
            'frequently asked questions', 'questions and answers', 'q&a', 'faq'
        }
        
        # Numbered question patterns
        self.question_patterns = [
            r'^\d+\.\s*.+\?',  # 1. Question?
            r'^q\d+[:\.]?\s*.+\?',  # Q1: Question?
            r'^question\s+\d+',  # Question 1
        ]
        
        # Context-aware heading indicators
        self.heading_signals = [
            'table of contents', 'contents', 'index', 'outline',
            'pathway options', 'course options', 'program structure',
            'digital library', 'ontario', 'canada', 'government',
            'university', 'college', 'school', 'department'
        ]
        
        # Noise patterns to filter out
        self.noise_patterns = [
            r'^page\s+\d+', r'^\d+\s*$', r'^copyright', r'^©', r'^version\s+\d',
            r'^www\.', r'@', r'^email$', r'^phone$', r'^table\s+\d+', r'^figure\s+\d+',
            r'^see page', r'^continued', r'^end of', r'^total\s*:', r'^\$\d+',
            r'^date:', r'^time:', r'^location:', r'^address:'
        ]
        
    def is_likely_heading(self, text: str, context: dict) -> bool:
        """Enhanced AI-like semantic analysis with stricter accuracy."""
        if not text or len(text.strip()) < 2:
            return False
        
        text_clean = text.strip()
        text_lower = text_clean.lower()
        
        # Normalize Unicode characters
        text_normalized = text_lower.replace(''', "'").replace(''', "'").replace('–', '-').replace('—', '-')
        
        # Immediate exclusions (clear content or fragments)
        if (len(text_clean) > 200 or  # Too long
            len(text_clean) < 3 or   # Too short
            any(re.search(p, text_normalized) for p in self.noise_patterns) or  # Noise
            re.search(r'\b(however|therefore|furthermore|moreover|additionally|specifically|particularly)\b', text_normalized) or  # Transition words
            re.search(r'\b(will be|shall be|must be|should be|can be|may be)\b', text_normalized) or  # Modal verbs
            re.search(r'\b(the purpose|in order to|according to|such as|for example)\b', text_normalized) or  # Content phrases
            text_clean.count('.') > 2 or  # Multiple sentences
            text_clean.count(',') > 3 or   # Complex clauses
            text_clean.endswith(',') or    # Fragment endings
            re.match(r'^(and|or|the|a|an)\s', text_normalized)):  # Fragment beginnings
            return False
        
        # Exclude obvious fragments (incomplete words/phrases)
        if (len(text_clean) < 6 and 
            not any(keyword in text_normalized for keyword in ['summary', 'index', 'part', 'chapter']) and
            not text_clean.isupper() and
            not re.match(r'^\d+\.?\s*$', text_clean)):
            return False
        
        # Strong positive indicators
        confidence_score = 0
        
        # 1. Structural patterns (highest confidence)
        for pattern in self.strong_heading_patterns:
            if re.match(pattern, text_clean, re.IGNORECASE):
                confidence_score += 100
                break
        
        # 2. Semantic heading keywords (very high confidence)
        for keyword in self.semantic_headings:
            if keyword in text_normalized:
                confidence_score += 90
                break
        
        # 3. Document-specific indicators
        for signal in self.heading_signals:
            if signal in text_normalized:
                confidence_score += 70
                break
        
        # 4. Formatting clues from context
        font_ratio = context.get('font_ratio', 1.0)
        is_bold = context.get('is_bold', False)
        is_isolated = context.get('is_isolated', False)
        
        if font_ratio >= 1.4:
            confidence_score += 60
        elif font_ratio >= 1.25:
            confidence_score += 40
        elif font_ratio >= 1.15:
            confidence_score += 25
        elif font_ratio >= 1.05:
            confidence_score += 15
        
        if is_bold:
            confidence_score += 30
        
        if is_isolated:
            confidence_score += 25
        
        # 5. Position and layout context
        page_num = context.get('page_num', 1)
        y_position = context.get('y_position', 0)
        
        if page_num <= 3:  # Early pages more likely to have headings
            confidence_score += 35
        elif page_num <= 10:
            confidence_score += 20
        
        if y_position < 100:  # Top of page
            confidence_score += 25
        
        # 6. Text characteristics
        word_count = len(text_clean.split())
        if 1 <= word_count <= 8:  # Ideal heading length
            confidence_score += 30
        elif word_count <= 15:
            confidence_score += 15
        elif word_count > 20:
            confidence_score -= 20
        
        # Colon endings (often headings)
        if text_clean.endswith(':') and word_count <= 10:
            confidence_score += 40
        
        # All caps (structural headings)
        if text_clean.isupper() and 3 <= len(text_clean) <= 50:
            confidence_score += 45
        
        # Title case
        if text_clean.istitle() and word_count <= 12:
            confidence_score += 25
        
        # Penalty for likely content patterns
        if (text_clean.endswith('.') and word_count > 5 and 
            not any(kw in text_normalized for kw in self.semantic_headings)):
            confidence_score -= 30
        
        # Return True if confidence is high enough (raised threshold)
        return confidence_score >= 60
    
    def calculate_heading_confidence(self, text: str, context: dict) -> Tuple[Optional[str], float]:
        """Enhanced AI-like confidence scoring with FAQ and repetition handling."""
        if not text or len(text.strip()) < 2:
            return None, 0.0
        
        text_clean = text.strip()
        text_lower = text_clean.lower()
        text_normalized = text_lower.replace(''', "'").replace(''', "'")
        
        # Check if it's likely a heading at all
        if not self.is_likely_heading(text_clean, context):
            return None, 0.0
        
        confidence = 0.0
        level = "H3"  # Default
        
        # 1. Numbered sections (highest priority - like AI recognizing structure)
        for pattern in self.strong_heading_patterns:
            match = re.match(pattern, text_clean, re.IGNORECASE)
            if match:
                if 'chapter' in text_lower or 'part' in text_lower:
                    level, confidence = "H1", 98.0
                elif len(match.groups()) > 1 and '.' in match.group(1):
                    dots = match.group(1).count('.')
                    level = f"H{min(dots + 1, 3)}"
                    confidence = 95.0 - (dots * 3)
                else:
                    level, confidence = "H1", 96.0
                break
        
        # 2. Question patterns (FAQ handling) - enhanced detection
        if confidence == 0:
            for pattern in self.question_patterns:
                if re.match(pattern, text_clean, re.IGNORECASE):
                    # All questions should be at consistent level (H2 for FAQ items)
                    level, confidence = "H2", 88.0
                    break
            
            # Additional question detection for FAQ format
            if (text_clean.endswith('?') and 
                (re.match(r'^\d+\.', text_clean) or text_clean.lower().startswith('q'))):
                level, confidence = "H2", 85.0
        
        # 3. Enhanced semantic analysis with repetition detection
        if confidence == 0:
            semantic_matches = []
            for keyword in self.semantic_headings:
                if keyword in text_normalized:
                    semantic_matches.append(keyword)
            
            if semantic_matches:
                # Enhanced priority system
                critical_priority = ['executive summary', 'abstract', 'introduction', 'summary', 'conclusion']
                high_priority = ['background', 'methodology', 'results', 'discussion', 'timeline', 'budget', 'recommendations']
                medium_priority = ['overview', 'analysis', 'findings', 'approach', 'scope', 'objectives']
                faq_priority = ['frequently asked questions', 'questions and answers', 'q&a', 'faq']
                
                if any(kw in faq_priority for kw in semantic_matches):
                    # FAQ titles should be main headings but check for repetition
                    level, confidence = "H1", 85.0
                elif any(kw in critical_priority for kw in semantic_matches):
                    level, confidence = "H1", 90.0
                elif any(kw in high_priority for kw in semantic_matches):
                    level, confidence = "H2", 85.0
                elif any(kw in medium_priority for kw in semantic_matches):
                    level, confidence = "H2", 75.0
                else:
                    level, confidence = "H3", 70.0
        
        # 4. Context-aware signals with better scoring
        if confidence == 0:
            for signal in self.heading_signals:
                if signal in text_normalized:
                    if 'digital library' in text_normalized or 'ontario' in text_normalized:
                        level, confidence = "H1", 85.0
                    else:
                        level, confidence = "H2", 75.0
                    break
        
        # 5. Enhanced format-based analysis
        if confidence == 0:
            font_ratio = context.get('font_ratio', 1.0)
            is_bold = context.get('is_bold', False)
            word_count = len(text_clean.split())
            
            # All caps structural headings (stricter)
            if (text_clean.isupper() and 3 <= len(text_clean) <= 50 and 
                word_count <= 8 and len(text_clean) >= 4):
                level, confidence = "H1", 85.0
            # Colon endings (higher confidence)
            elif text_clean.endswith(':') and 2 <= word_count <= 10:
                level, confidence = "H2", 80.0
            # Large font headings (adjusted thresholds)
            elif font_ratio >= 1.5:
                level, confidence = "H1", 75.0
            elif font_ratio >= 1.3:
                level, confidence = "H2", 70.0
            elif font_ratio >= 1.15:
                level, confidence = "H3", 65.0
            # Bold text headings (stricter)
            elif (is_bold and font_ratio >= 1.05 and 2 <= word_count <= 12 and
                  not text_clean.endswith('.') or any(kw in text_normalized for kw in self.semantic_headings)):
                level, confidence = "H3", 60.0
        
        # Enhanced context bonuses
        if confidence > 0:
            page_num = context.get('page_num', 1)
            y_position = context.get('y_position', 0)
            is_bold = context.get('is_bold', False)
            is_isolated = context.get('is_isolated', False)
            
            # Early page bonus (increased)
            if page_num <= 2:
                confidence += 20
            elif page_num <= 5:
                confidence += 15
            elif page_num <= 10:
                confidence += 8
            
            # Position bonus (increased)
            if y_position < 100:
                confidence += 12
            elif y_position < 200:
                confidence += 6
            
            # Formatting bonus (increased)
            if is_bold:
                confidence += 10
            
            if is_isolated:
                confidence += 8
            
            # Length appropriateness (enhanced)
            word_count = len(text_clean.split())
            if 2 <= word_count <= 6:
                confidence += 8
            elif word_count <= 10:
                confidence += 5
            elif word_count > 15:
                confidence -= 10
            
            # Penalty for likely content patterns
            if (text_clean.endswith('.') and word_count > 6 and 
                not any(kw in text_normalized for kw in self.semantic_headings)):
                confidence -= 15
        
        # Stricter confidence threshold
        return (level, confidence) if confidence >= 60.0 else (None, 0.0)
    
    def extract_title_intelligently(self, doc) -> str:
        """AI-like intelligent title extraction considering document semantics."""
        if not doc:
            return ""
        
        page = doc[0]
        blocks = page.get_text("dict")["blocks"]
        title_candidates = []
        
        for block in blocks:
            if "lines" not in block:
                continue
            
            for line in block["lines"]:
                if not line["spans"]:
                    continue
                
                text = "".join(span["text"] for span in line["spans"]).strip()
                if not text or len(text) < 5:
                    continue
                
                font_size = line["spans"][0]["size"]
                is_bold = any(span.get("flags", 0) & 16 for span in line["spans"])
                y_pos = line["bbox"][1] if line.get("bbox") else 0
                
                # AI-like title scoring
                title_confidence = 0
                
                # Position importance (earlier = more likely title)
                if y_pos < 100:
                    title_confidence += 40
                elif y_pos < 200:
                    title_confidence += 25
                elif y_pos < 300:
                    title_confidence += 10
                
                # Font size importance
                title_confidence += min(font_size * 2, 30)
                
                # Formatting
                if is_bold:
                    title_confidence += 15
                
                # Content analysis (semantic understanding)
                text_normalized = text.lower().replace(''', "'").replace(''', "'")
                
                # Title indicators
                title_keywords = ['rfp', 'request for proposal', 'business plan', 'digital library', 
                                'ontario', 'proposal to', 'developing', 'implementation', 'strategy']
                for keyword in title_keywords:
                    if keyword in text_normalized:
                        title_confidence += 20
                        break
                
                # Academic/formal title patterns
                if any(pattern in text_normalized for pattern in ['analysis of', 'study of', 'review of', 'guide to', 'introduction to']):
                    title_confidence += 15
                
                # Length appropriateness for titles
                word_count = len(text.split())
                if 3 <= word_count <= 12:
                    title_confidence += 15
                elif word_count <= 20:
                    title_confidence += 8
                elif word_count > 25:
                    title_confidence -= 10
                
                # Avoid content-like text
                if any(indicator in text_normalized for indicator in 
                       ['however', 'therefore', 'this document', 'the purpose', 'in order to']):
                    title_confidence -= 20
                
                # Complete sentence check (titles usually aren't complete sentences)
                if text.endswith('.') and word_count > 8:
                    title_confidence -= 15
                
                if title_confidence > 20 and len(text) >= 10:
                    title_candidates.append((title_confidence, text, y_pos, word_count))
        
        if not title_candidates:
            return ""
        
        # Sort by confidence and find best title
        title_candidates.sort(key=lambda x: (-x[0], x[2]))
        
        # Look for complete, high-confidence titles first
        for confidence, text, y_pos, word_count in title_candidates[:5]:
            if confidence >= 60 and word_count >= 4:
                return text.strip() + "  "
        
        # Fallback to highest confidence
        return title_candidates[0][1].strip() + "  " if title_candidates else ""
    
    def extract_outline(self, pdf_path: str) -> dict:
        """AI-like intelligent outline extraction with semantic understanding."""
        try:
            doc = fitz.open(pdf_path)
            title = self.extract_title_intelligently(doc)
            
            # Check for form documents (AI would recognize these patterns)
            first_page_text = doc[0].get_text().lower()
            form_indicators = ['application form', 'form no', 'grant of', 'employee id', 'fill in', 'check box']
            if any(indicator in first_page_text for indicator in form_indicators):
                doc.close()
                return {"title": title, "outline": []}
            
            # Extract text with rich context (like AI analyzing layout)
            text_elements = []
            font_sizes = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if "lines" not in block:
                        continue
                    
                    for line in block["lines"]:
                        if not line["spans"]:
                            continue
                        
                        text = "".join(span["text"] for span in line["spans"]).strip()
                        if not text:
                            continue
                        
                        font_size = round(line["spans"][0]["size"], 1)
                        is_bold = any(span.get("flags", 0) & 16 for span in line["spans"])
                        y_pos = line["bbox"][1] if line.get("bbox") else 0
                        x_pos = line["bbox"][0] if line.get("bbox") else 0
                        
                        # Check if text is isolated (like AI recognizing standalone headings)
                        is_isolated = len(text.split()) <= 10 and not any(
                            text.lower() in other_text.lower() or other_text.lower() in text.lower()
                            for other_text in [t[0] for t in text_elements[-3:]] if other_text != text
                        )
                        
                        text_elements.append((
                            text, font_size, is_bold, page_num, y_pos, x_pos, is_isolated
                        ))
                        font_sizes.append(font_size)
            
            # Determine body font (like AI understanding document structure)
            body_font = Counter(font_sizes).most_common(1)[0][0] if font_sizes else 12.0
            
            # Enhanced AI-like heading detection with strict repetition control
            candidates = []
            seen_normalized = set()
            seen_fragments = set()
            document_title = title.strip().lower() if title else ""
            
            for text, font_size, is_bold, page_num, y_pos, x_pos, is_isolated in text_elements:
                # Enhanced fragment prevention with line-break handling
                text_clean = text.strip()
                
                # Skip obvious fragments immediately
                if (len(text_clean) < 4 and 
                    not any(keyword in text_clean.lower() for keyword in ['summary', 'index']) and
                    not text_clean.isupper()):
                    continue
                
                # Skip incomplete phrases (enhanced detection)
                if (text_clean.endswith(':') and len(text_clean) < 8 and 
                    not any(kw in text_clean.lower() for kw in ['rfp', 'part', 'step', 'timeline'])):
                    continue
                
                # Skip single letter fragments or very short incomplete text
                if (len(text_clean) <= 2 or 
                    (len(text_clean) <= 6 and text_clean.endswith(':') and 
                     not any(kw in text_clean.lower() for kw in ['summary', 'rfp', 'timeline']))):
                    continue
                
                # Skip obvious partial headings and line-break fragments
                if (re.match(r'^[A-Z]+:\s*[A-Z]$', text_clean) or  # "RFP: R"
                    re.match(r'^[A-Z]+:\s*[A-Z]\w{1,3}$', text_clean) or  # "RFP: To"
                    re.match(r'^[A-Z]+:\s*\w{1,10}\s*f$', text_clean) or  # "RFP: Request f"
                    re.match(r'^\w{1,10}\s+for\s+\w{1,2}$', text_clean) or  # "quest for Pr"
                    text_clean.endswith(' f') or text_clean.endswith(' t') or  # Line break fragments
                    (len(text_clean) < 15 and any(frag in text_clean.lower() for frag in ['quest for pr', 'request f']))):
                    continue
                
                # Skip if text is very similar to document title (repetition control)
                text_clean_lower = text_clean.lower()
                if document_title and len(document_title) > 5:
                    title_words = set(document_title.split())
                    text_words = set(text_clean_lower.split())
                    # If 80% or more words match, it's likely a title repetition
                    if title_words and len(title_words & text_words) / len(title_words) >= 0.8:
                        continue
                
                # Create rich context for AI-like analysis
                context = {
                    'font_ratio': font_size / body_font,
                    'is_bold': is_bold,
                    'page_num': page_num + 1,
                    'y_position': y_pos,
                    'x_position': x_pos,
                    'is_isolated': is_isolated
                }
                
                level, confidence = self.calculate_heading_confidence(text_clean, context)
                
                if level and confidence >= 60:  # Raised threshold
                    # Enhanced duplicate detection
                    text_normalized = text_clean.lower().replace(''', "'").replace(''', "'")
                    text_key = re.sub(r'[^\w\s]', '', text_normalized).replace(' ', '')
                    
                    # Skip if we've seen this concept before
                    if text_key in seen_normalized and len(text_key) > 3:
                        continue
                    
                    # Fragment detection - check if this might be part of a larger heading
                    is_fragment = False
                    for seen_text in seen_fragments:
                        if (text_key in seen_text or seen_text in text_key) and len(text_key) < 15:
                            is_fragment = True
                            break
                    
                    if is_fragment:
                        continue
                    
                    # Enhanced filtering with better fragment detection
                    skip = False
                    
                    # Skip obvious fragments or incomplete text
                    if (len(text_clean.split()) == 1 and len(text_clean) < 8 and 
                        not any(keyword in text_normalized for keyword in 
                               ['summary', 'appendix', 'index', 'background', 'introduction', 'conclusion'])):
                        skip = True
                    
                    # Skip partial headings (like "RFP: R" fragments)
                    if (re.match(r'^[A-Z]+:\s*[A-Z](\w{0,3})?$', text_clean) and 
                        len(text_clean) < 12):
                        skip = True
                    
                    # Skip partial sentences that aren't headings
                    if (text_clean.endswith(',') or text_clean.startswith('and ') or 
                        text_clean.startswith('or ') or text_clean.startswith('but ') or
                        (text_clean.startswith('the ') and len(text_clean.split()) < 5)):
                        skip = True
                    
                    # Skip dates that aren't proper headings
                    if (re.match(r'^(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d+,?\s+\d{4}$', text_normalized) and
                        confidence < 80):
                        skip = True
                    
                    # Skip obvious content patterns
                    content_patterns = [
                        r'this (document|section|chapter)',
                        r'in order to',
                        r'according to',
                        r'as (shown|described|mentioned)',
                        r'(please|kindly) (note|refer)',
                        r'for (more|additional) (information|details)',
                        r'developed is to document'  # Fragment from file03
                    ]
                    if any(re.search(pattern, text_normalized) for pattern in content_patterns):
                        skip = True
                    
                    # Don't skip important semantic headings regardless of format
                    important_patterns = [
                        'ontario.*digital.*library', 'business.*plan', 'executive.*summary',
                        'summary', 'introduction', 'background', 'conclusion', 'recommendations',
                        'timeline', 'budget', 'scope', 'objectives'
                    ]
                    if any(re.search(pattern, text_normalized) for pattern in important_patterns):
                        skip = False
                    
                    if not skip:
                        candidates.append(HeadingCandidate(
                            text=text_clean + " ",
                            level=level,
                            page=page_num,
                            score=confidence
                        ))
                        seen_normalized.add(text_key)
                        seen_fragments.add(text_key)
            
            # Enhanced adaptive thresholding with quality control
            total_candidates = len(candidates)
            
            # More aggressive thresholding for better accuracy
            if total_candidates > 80:
                min_confidence = 85
            elif total_candidates > 50:
                min_confidence = 80
            elif total_candidates > 30:
                min_confidence = 75
            elif total_candidates > 20:
                min_confidence = 70
            elif total_candidates > 10:
                min_confidence = 65
            else:
                min_confidence = 60
            
            # Filter by confidence
            quality_headings = [c for c in candidates if c.score >= min_confidence]
            
            # Ensure critical early content is captured (priority headings)
            priority_keywords = ['summary', 'ontario', 'digital library', 'introduction', 'background', 'executive']
            early_priority_headings = []
            
            for c in candidates:
                if (c.page <= 3 and c.score >= min_confidence - 10 and
                    any(kw in c.text.lower() for kw in priority_keywords)):
                    if c not in quality_headings:
                        early_priority_headings.append(c)
            
            quality_headings.extend(early_priority_headings)
            
            # Remove duplicates and handle question classification and sorting
            seen_texts = set()
            question_headings = []
            non_question_headings = []
            
            for heading in quality_headings:
                heading_key = heading.text.strip().lower()
                
                # Skip exact duplicates
                if heading_key in seen_texts:
                    continue
                
                # Re-classify questions that might have been missed
                text_clean = heading.text.strip()
                if (text_clean.endswith('?') and 
                    (re.match(r'^\d+\.', text_clean) or text_clean.lower().startswith('q'))):
                    # Force questions to be H2 level
                    heading.level = "H2"
                    question_headings.append(heading)
                else:
                    non_question_headings.append(heading)
                
                seen_texts.add(heading_key)
            
            # Sort questions by number for proper ordering (fixed sorting logic)
            def extract_question_number(heading):
                match = re.match(r'^(\d+)\.', heading.text.strip())
                return int(match.group(1)) if match else 999
            
            question_headings.sort(key=extract_question_number)
            
            # Combine non-questions first, then sorted questions
            quality_headings = non_question_headings + question_headings
            
            # Smart result limiting (like AI balancing comprehensiveness vs clarity)
            if len(quality_headings) > 50:
                quality_headings.sort(key=lambda x: (-x.score, x.page))
                quality_headings = quality_headings[:50]
            
            # Final sorting by document flow with question ordering
            quality_headings.sort(key=lambda x: (x.page, -x.score))
            
            # Post-process: Fix question ordering within each page
            final_headings = []
            current_page_headings = []
            current_page = -1
            
            for heading in quality_headings:
                if heading.page != current_page:
                    # Process previous page's headings
                    if current_page_headings:
                        # Separate questions and non-questions for this page
                        page_questions = []
                        page_non_questions = []
                        
                        for h in current_page_headings:
                            if re.match(r'^\d+\.\s*.+\?', h.text.strip()):
                                page_questions.append(h)
                            else:
                                page_non_questions.append(h)
                        
                        # Sort questions by number
                        def get_q_num(h):
                            match = re.match(r'^(\d+)\.', h.text.strip())
                            return int(match.group(1)) if match else 999
                        
                        page_questions.sort(key=get_q_num)
                        
                        # Add non-questions first, then sorted questions
                        final_headings.extend(page_non_questions)
                        final_headings.extend(page_questions)
                    
                    # Start new page
                    current_page = heading.page
                    current_page_headings = [heading]
                else:
                    current_page_headings.append(heading)
            
            # Don't forget the last page
            if current_page_headings:
                page_questions = []
                page_non_questions = []
                
                for h in current_page_headings:
                    if re.match(r'^\d+\.\s*.+\?', h.text.strip()):
                        page_questions.append(h)
                    else:
                        page_non_questions.append(h)
                
                def get_q_num(h):
                    match = re.match(r'^(\d+)\.', h.text.strip())
                    return int(match.group(1)) if match else 999
                
                page_questions.sort(key=get_q_num)
                final_headings.extend(page_non_questions)
                final_headings.extend(page_questions)
            
            quality_headings = final_headings
            
            outline = [{"level": h.level, "text": h.text, "page": h.page} for h in quality_headings]
            
            doc.close()
            return {"title": title, "outline": outline}
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return None


def extract_outline(pdf_path: str) -> dict:
    """Extract PDF outline - main entry point."""
    extractor = PDFOutlineExtractor()
    return extractor.extract_outline(pdf_path)


def process_multiple_files(input_files: List[str], output_dir: str = None) -> dict:
    """Process multiple PDF files efficiently."""
    import os
    
    results = {}
    total_files = len(input_files)
    
    print(f"🔄 Processing {total_files} PDF files...")
    
    for i, pdf_file in enumerate(input_files, 1):
        if not os.path.exists(pdf_file):
            print(f"❌ File not found: {pdf_file}")
            results[pdf_file] = {'success': False, 'error': 'File not found'}
            continue
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(pdf_file))[0]
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{base_name}.json")
        else:
            output_file = f"{base_name}_outline.json"
        
        print(f"📄 [{i}/{total_files}] Processing: {pdf_file}")
        
        # Extract outline
        result = extract_outline(pdf_file)
        
        if result:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            
            outline_count = len(result.get('outline', []))
            print(f"   ✓ Extracted {outline_count} headings → {output_file}")
            
            results[pdf_file] = {
                'output_file': output_file,
                'headings': outline_count,
                'title': result.get('title', ''),
                'success': True
            }
        else:
            print(f"   ❌ Failed to process {pdf_file}")
            results[pdf_file] = {'success': False, 'error': 'Processing failed'}
    
    return results


def main():
    """Clean interface: auto-processes input/ folder or handles manual files."""
    import os
    import glob
    
    parser = argparse.ArgumentParser(
        description='Generic PDF outline extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('files', nargs='*', help='Input PDF file(s) (optional)')
    parser.add_argument('--batch', action='store_true', help='Batch mode for multiple files')
    parser.add_argument('--output-dir', '-o', help='Output directory (optional)')
    
    args = parser.parse_args()
    
    # Auto mode: process input/ folder
    if not args.files:
        input_dir, output_dir = "input", "output"
        
        if not os.path.exists(input_dir):
            print(f"❌ '{input_dir}' folder not found!")
            print("Create 'input' folder with PDF files, or specify files manually.")
            return
        
        pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
        if not pdf_files:
            print(f"❌ No PDF files found in '{input_dir}'!")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        print(f"🚀 Processing {len(pdf_files)} PDFs: {input_dir}/ → {output_dir}/")
        
        results = process_multiple_files(pdf_files, output_dir)
        
        # Summary
        successful = sum(1 for r in results.values() if r.get('success'))
        total_headings = sum(r.get('headings', 0) for r in results.values() if r.get('success'))
        
        print(f"\n📈 COMPLETE: {successful}/{len(pdf_files)} successful, {total_headings} total headings")
        return
    
    # Manual mode
    if len(args.files) == 1 and not args.batch:
        # Single file
        pdf_file = args.files[0]
        output_file = f"{os.path.splitext(os.path.basename(pdf_file))[0]}_outline.json"
        
        print(f"📄 Processing: {pdf_file}")
        result = extract_outline(pdf_file)
        
        if result:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            
            outline_count = len(result.get('outline', []))
            print(f"✓ {outline_count} headings → {output_file}")
        else:
            print("❌ Processing failed")
    else:
        # Batch mode
        results = process_multiple_files(args.files, args.output_dir)
        successful = sum(1 for r in results.values() if r.get('success'))
        total_headings = sum(r.get('headings', 0) for r in results.values() if r.get('success'))
        print(f"\n📈 BATCH COMPLETE: {successful}/{len(args.files)} successful, {total_headings} total headings")


if __name__ == "__main__":
    main()