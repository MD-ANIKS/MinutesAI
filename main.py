from dotenv import load_dotenv
import sys
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decision, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

def run_pipeline(source: str) -> dict:
  print("Starting AI Video Assistant")

  chunks = process_input(source)

  transcript = transcribe_all(chunks)
  print(f"Raw transcription (first 300 characters) {transcript[:300]}")

  title = generate_title(transcript)
  summary = summarize(transcript)
  action_items = extract_action_items(transcript)
  decission = extract_key_decision(transcript)
  questions = extract_questions(transcript)

  rag_chain = build_rag_chain(transcript)

  return {
    "title": title, 
    "transcript": transcript,
    "summary": summary,
    "action_items": action_items,
    "key_decissions": decission,
    "open_questions": questions,
    "rag_chain": rag_chain
  }


def print_separator(title: str = ""):
    print("\n" + "=" * 50)
    if title:
        print(f"  {title.upper()}")
        print("=" * 50)


def display_results(results: dict):
    print_separator("Meeting / Video Summary")
    print(f"📌 Title: {results['title']}\n")
    
    print("📝 Executive Summary:")
    print(results['summary'])
    print_separator()

    if results.get('action_items'):
        print("✅ Action Items:")
        print(results['action_items'])
        print_separator()

    if results.get('key_decissions'):
        print("🎯 Key Decisions:")
        print(results['key_decissions'])
        print_separator()

    if results.get('open_questions'):
        print("❓ Open Questions:")
        print(results['open_questions'])
        print_separator()


def start_rag_chat(rag_chain):
    print_separator("AI Video Assistant - Interactive Q&A")
    print("ভিডিও সম্পর্কে যেকোনো প্রশ্ন করুন। বের হয়ে যেতে 'exit' বা 'q' লিখুন।\n")

    while True:
        try:
            user_query = input("💬 Your Question: ").strip()
            
            if not user_query:
                continue
                
            if user_query.lower() in ["exit", "quit", "q"]:
                print("\n👋 Chat Session Ended. Thank you!")
                break

            print("\n🤔 Thinking...")
            # ask_question ফাংশনে rag_chain এবং user_query পাস করা হচ্ছে
            answer = ask_question(rag_chain, user_query)
            
            print(f"\n🤖 Answer:\n{answer}\n")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}\n")


def main():
    print_separator("Welcome to AI Video Assistant")
    
    # ১. ইউজার থেকে ইনপুট বা URL নেওয়া
    if len(sys.argv) > 1:
        source = sys.argv[1]
    else:
        source = input("Enter YouTube URL or Local File Path: ").strip()

    if not source:
        print("❌ Error: No source provided. Exiting...")
        return

    try:
        results = run_pipeline(source=source)
        
        display_results(results)

        if results.get("rag_chain"):
            start_rag_chat(results["rag_chain"])
        else:
            print("⚠️ Warning: RAG chain could not be initialized.")

    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")


if __name__ == "__main__":
    main()