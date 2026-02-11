import modal
import re
import os

app = modal.App("cameleon-cv")

def download_models():
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from huggingface_hub import snapshot_download
    import torch
    
    BASE_MODEL = "unsloth/Meta-Llama-3.1-8B-Instruct"
    LORA_ADAPTER = "georgieslab/cameleon-cv-lora"
    
    print("Downloading tokenizer...")
    AutoTokenizer.from_pretrained(BASE_MODEL)
    
    print("Downloading LoRA adapter...")
    snapshot_download(repo_id=LORA_ADAPTER)
    
    print("Downloading base model...")
    AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        trust_remote_code=True,
    )
    
    print("All models downloaded!")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers>=4.36.0",
        "peft>=0.7.0",
        "accelerate>=0.25.0",
        "sentencepiece",
        "protobuf",
        "huggingface_hub",
        "fastapi[standard]",
        "bitsandbytes>=0.41.0",
        "anthropic>=0.18.0",
    )
    .run_function(download_models)
)

BASE_MODEL = "unsloth/Meta-Llama-3.1-8B-Instruct"
LORA_ADAPTER = "georgieslab/cameleon-cv-lora"

STYLE_GUIDES = {
    "Professional": "Professional: Business-appropriate, polished, measured confidence, formal but approachable",
    "Academic": "Academic: Scholarly precision, methodological language, formal structure, emphasizes research and analysis",
    "Confident": "Confident: Bold assertions, strong action verbs, quantified achievements, leadership focus",
    "Concise": "Concise: Maximum impact, minimum words. Short punchy sentences. No filler.",
    "Playful": "Playful: Warm and engaging, conversational tone, tasteful emojis, shows personality while staying professional"
}

@app.cls(
    image=image,
    gpu="A10G",
    timeout=600,
    container_idle_timeout=180,
    secrets=[modal.Secret.from_name("anthropic-api-key")],
)
class CameleonModel:
    @modal.enter()
    def load_model(self):
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
        from peft import PeftModel
        import anthropic
        
        print("Starting model load...")
        
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print("Loading base model with 4-bit quantization...")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        
        print("Loading LoRA adapter...")
        self.model = PeftModel.from_pretrained(self.model, LORA_ADAPTER)
        self.model.eval()
        
        print("Initializing Claude client...")
        self.claude = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        
        print("All models ready!")
    
    def verify_fact_preservation(self, original: str, generated: str) -> tuple[bool, list]:
        """Verify all key facts from original are preserved in generated."""
        
        # Extract all numbers/metrics from original
        original_numbers = set(re.findall(r'\b\d+[.,]?\d*[%+]?\b', original.lower()))
        generated_lower = generated.lower()
        
        missing_numbers = []
        for num in original_numbers:
            if num not in generated_lower:
                missing_numbers.append(num)
        
        if missing_numbers:
            print(f"Missing numbers: {missing_numbers}")
            return False, missing_numbers
        
        # Check key action verbs (with synonyms)
        verb_synonyms = {
            "developed": ["built", "created", "engineered", "designed"],
            "maintained": ["supported", "managed", "upheld", "sustained"],
            "reduced": ["decreased", "lowered", "cut", "minimized"],
            "improved": ["enhanced", "boosted", "upgraded", "increased"],
            "collaborated": ["worked with", "partnered", "teamed", "coordinated"],
            "optimized": ["streamlined", "refined", "tuned", "improved"],
        }
        
        original_lower = original.lower()
        for verb, synonyms in verb_synonyms.items():
            if verb in original_lower:
                all_forms = [verb] + synonyms
                if not any(form in generated_lower for form in all_forms):
                    print(f"Missing action verb: {verb}")
                    # Don't fail on this, just warn
        
        return True, []
    
    def clean_output(self, text: str, original: str) -> str:
        """Clean output and enforce length/content limits."""
        
        stop_markers = [
            "### Instruction", "###Instruction", "### Input", "###Input", 
            "### Response", "###Response", "(Removed", "(Note:", "(Changed",
            "Note:", "Changes:", "Original:",
        ]
        
        for marker in stop_markers:
            if marker in text:
                text = text.split(marker)[0].strip()
        
        text = re.sub(r'^\*\*[^*]+\*\*\s*', '', text)
        text = re.sub(r'://+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Ensure complete sentence
        if text and text[-1] not in '.!?':
            last_end = max(text.rfind('.'), text.rfind('!'), text.rfind('?'))
            if last_end > len(text) * 0.6:
                text = text[:last_end + 1]
        
        # Length control: max 1.8x original
        original_words = len(original.split())
        max_words = int(original_words * 1.8)
        
        words = text.split()
        if len(words) > max_words:
            truncated = ' '.join(words[:max_words])
            last_end = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
            if last_end > len(truncated) * 0.5:
                text = truncated[:last_end + 1]
            else:
                text = truncated
        
        return text.strip()
    
    def style_transform(self, cv_text: str, style: str, section_type: str) -> str:
        """Step 1: LoRA-based style transformation."""
        import torch
        
        style_guide = STYLE_GUIDES.get(style, STYLE_GUIDES["Professional"])
        
        prompt = f"""### Instruction:
Transform this CV {section_type.lower()} into {style} style.

Style Guide - {style_guide}

### Input:
{cv_text.strip()}

### Response:
"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Higher token limits to prevent truncation
        input_word_count = len(cv_text.split())
        max_new_tokens = min(200, max(80, int(input_word_count * 3)))
        
        print(f"Style transform: {input_word_count} words, max_new_tokens={max_new_tokens}")
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.1,
                top_p=0.95,
                top_k=40,
                do_sample=True,
                repetition_penalty=1.15,
                no_repeat_ngram_size=3,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "### Response:" in full_response:
            transformed = full_response.split("### Response:")[-1].strip()
        else:
            transformed = full_response[len(prompt):].strip()
        
        transformed = self.clean_output(transformed, cv_text)
        
        if not transformed or len(transformed) < 15:
            return cv_text
        
        return transformed
    
    def job_relevance(self, styled_cv: str, job_posting: str, original_cv: str) -> str:
        """Step 2: Claude-based job relevance enhancement with fact verification."""
        
        if not job_posting or len(job_posting.strip()) < 20:
            return styled_cv
        
        # Extract facts that MUST be preserved
        original_numbers = re.findall(r'\b\d+[.,]?\d*[%+]?\b', original_cv)
        
        prompt = f"""You are enhancing a CV section to match a job posting.

STRICT RULES:
1. PRESERVE ALL NUMBERS EXACTLY: {', '.join(original_numbers)}
2. NEVER add new facts, achievements, or claims not in the original
3. You may ONLY: reorder info, emphasize relevant skills, use job keywords
4. Keep similar length to input
5. Maintain the current writing style

ORIGINAL CV (source of truth):
{original_cv}

STYLED CV (maintain this tone):
{styled_cv}

JOB POSTING:
{job_posting.strip()}

OUTPUT ONLY the enhanced CV section (no explanations):"""

        try:
            response = self.claude.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=350,
                temperature=0.2,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            enhanced = response.content[0].text.strip()
            
            # Verify facts are preserved
            facts_ok, missing = self.verify_fact_preservation(original_cv, enhanced)
            
            if not facts_ok:
                print(f"Fact check failed, missing: {missing}")
                return styled_cv
            
            if len(enhanced.split()) > len(styled_cv.split()) * 1.5:
                print("Claude output too long, using styled version")
                return styled_cv
            
            return enhanced
            
        except Exception as e:
            print(f"Claude API error: {e}")
            return styled_cv
    
    @modal.method()
    def transform(self, cv_text: str, style: str, section_type: str, job_posting: str = "") -> dict:
        """Full pipeline: Style transform + Job relevance."""
        
        print(f"Transform request: style={style}, section={section_type}")
        print(f"Job posting provided: {bool(job_posting and job_posting.strip())}")
        
        if not cv_text.strip():
            return {
                "styled": "Please enter some CV text to transform.",
                "enhanced": None,
                "job_relevance_applied": False
            }
        
        # Step 1: Style transformation (LoRA)
        styled = self.style_transform(cv_text, style, section_type)
        print(f"Style transform complete: {len(styled.split())} words")
        
        # Step 2: Job relevance (Claude) with fact verification
        enhanced = None
        job_relevance_applied = False
        
        if job_posting and job_posting.strip():
            enhanced = self.job_relevance(styled, job_posting, cv_text)
            job_relevance_applied = True
            print(f"Job relevance complete: {len(enhanced.split())} words")
        
        return {
            "styled": styled,
            "enhanced": enhanced,
            "job_relevance_applied": job_relevance_applied
        }

@app.function(image=image, timeout=600, secrets=[modal.Secret.from_name("anthropic-api-key")])
@modal.web_endpoint(method="POST")
def transform_cv(item: dict):
    cv_text = item.get("cv_text", "")
    style = item.get("style", "Professional")
    section_type = item.get("section_type", "Work Experience")
    job_posting = item.get("job_posting", "")
    
    model = CameleonModel()
    result = model.transform.remote(cv_text, style, section_type, job_posting)
    
    return {
        "transformed": result["enhanced"] if result["enhanced"] else result["styled"],
        "styled_only": result["styled"],
        "job_relevance_applied": result["job_relevance_applied"],
        "style": style,
        "section_type": section_type,
        "metrics": {
            "input_words": len(cv_text.split()),
            "styled_words": len(result["styled"].split()),
            "enhanced_words": len(result["enhanced"].split()) if result["enhanced"] else 0
        }
    }