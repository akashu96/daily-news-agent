import anthropic
from datetime import date
import sys

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env


def load_prompt():
    with open("prompt.txt", "r") as f:
        return f.read()


def get_digest():
    prompt = load_prompt()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 3  # cost safety cap per run
        }],
    )

    text_parts = [block.text for block in response.content if block.type == "text"]
    digest = "\n\n".join(text_parts)

    if not digest.strip():
        raise ValueError("Empty digest returned — check API response / stop_reason")

    return digest


if __name__ == "__main__":
    try:
        digest = get_digest()
    except Exception as e:
        print(f"❌ Failed to generate digest: {e}", file=sys.stderr)
        sys.exit(1)  # non-zero exit so GitHub Actions marks the run as failed

    filename = f"digest_{date.today().isoformat()}.md"
    with open(filename, "w") as f:
        f.write(digest)

    print(f"✅ Saved to {filename}")