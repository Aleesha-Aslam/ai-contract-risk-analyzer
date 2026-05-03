from deep_translator import GoogleTranslator

def translate_to_urdu(text):
    try:
        max_chunk = 4000
        chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]

        translated_chunks = []
        for chunk in chunks:
            translated = GoogleTranslator(source='auto', target='ur').translate(chunk)
            translated_chunks.append(translated)

        return "\n".join(translated_chunks)

    except Exception as e:
        return f"⚠️ Translation failed: {str(e)}"