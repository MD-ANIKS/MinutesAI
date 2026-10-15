from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decision, extract_questions


source = "https://www.youtube.com/watch?v=YdscXGJbEgQ"

print("\n -----source-------- \n", source)

chunks = process_input(source)
print("\n -----chunks-------- \n", chunks)

transcript = transcribe_all(chunks)
print("\n -----transcript-------- \n", transcript)


title = generate_title(transcript)
print("\n -----title-------- \n", title)

summary = summarize(transcript)
print("\n -----summary-------- \n", summary)


action_items = extract_action_items(transcript)
print("\n -----action items-------- \n", action_items)
decissions = extract_key_decision(transcript)
print("\n -----decissions-------- \n", decissions)
questions = extract_questions(transcript)
print("\n -----questions-------- \n", questions)