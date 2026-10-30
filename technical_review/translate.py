from .quality import check_translation

MODEL_ID = "Helsinki-NLP/opus-mt-en-es"
MODEL_REVISION = "5bc4493d463cf000c1f0b50f8d56886a392ed4ab"


class MarianTranslator:
    name = MODEL_ID
    revision = MODEL_REVISION

    def __init__(self, allow_download=False):
        import torch
        from transformers import MarianMTModel, MarianTokenizer

        self.torch = torch
        self.tokenizer = MarianTokenizer.from_pretrained(
            self.name, revision=self.revision, local_files_only=not allow_download
        )
        self.model = MarianMTModel.from_pretrained(
            self.name, revision=self.revision, local_files_only=not allow_download
        )
        self.model.eval()

    def translate(self, text):
        # Token-aware chunks; never set truncation=True or silently discard source tokens.
        words = text.split()
        chunks = []
        current = []
        for word in words:
            candidate = " ".join(current + [word])
            if len(self.tokenizer.encode(candidate)) > 450:
                if not current:
                    raise ValueError("Single word exceeds model token limit")
                chunks.append(" ".join(current))
                current = [word]
                if len(self.tokenizer.encode(word)) > 450:
                    raise ValueError("Single word exceeds model token limit")
            else:
                current.append(word)
        if current:
            chunks.append(" ".join(current))
        output = []
        for chunk in chunks:
            inputs = self.tokenizer(chunk, return_tensors="pt", truncation=False)
            with self.torch.inference_mode():
                result = self.model.generate(
                    **inputs, max_new_tokens=512, num_beams=4, do_sample=False
                )
            if result[0, -1].item() != self.tokenizer.eos_token_id:
                raise RuntimeError(
                    "Translation reached token limit without EOS; source preserved for review"
                )
            output.append(self.tokenizer.decode(result[0], skip_special_tokens=True))
        return " ".join(output)


def translate_document(data, provider, glossary=None):
    data["engine"] = {"name": provider.name, "revision": provider.revision}
    total = translated = preserved = flagged = 0
    for page in data["pages"]:
        for block in page["blocks"]:
            total += 1
            if any(
                f in block["flags"] for f in ("table_preserved", "equation_preserved")
            ):
                block["translated"] = block["text"]
                block["status"] = "preserved_for_review"
                preserved += 1
            else:
                try:
                    target = provider.translate(block["text"])
                    flags = check_translation(block["text"], target, glossary)
                    block["translated"] = target
                    block["flags"].extend(flags)
                    block["status"] = "needs_review" if block["flags"] else "draft"
                    translated += 1
                except (RuntimeError, ValueError) as exc:
                    block["translated"] = block["text"]
                    block["status"] = "preserved_after_error"
                    block["flags"].append("translation_error:" + str(exc))
                    preserved += 1
            if block["flags"]:
                flagged += 1
    data["metrics"] = {
        "extracted_blocks": total,
        "translated_blocks": translated,
        "preserved_blocks": preserved,
        "flagged_blocks": flagged,
        "unprocessed_regions": sum(len(p["warnings"]) for p in data["pages"]),
        "human_review_required": True,
    }
    return data
