from openai import OpenAI

from utils.elastic import elastic_request
import utils.anthropic_client as anthropic_client
import utils.openai_client as openai_client

CLAUDE_35 = "claude-3.5"
GPT_4O = "gpt-4o"

SEARCH_PROMPT = """
Users are playing an RPG. They will ask questions pertaining to the rules, setting, lore,
and current situation. You will accept the query and return a list of relevant keywords that
can be used to locate relevant sections of the source material.

You will NOT attempt to answer the questions yourself. Your only role is to extract useful keywords
to be used in a search. Organize them in order of likely relevance, from most relevant to least.

Return the keywords in a comma delimited format with no quote characters or extraneous punctuation.
"""

# Note: the below results in somewhat illiberal responses. it says "cannot answer the question because content says nothing".
# What we often want is more of the form: "content doesn't say you can't do it, so you can"

# Also, perhaps a "Maybe?" response is in order? for example, we get this response from "Can I cast Hunter's Mark on an entity that is Invisible?"
# "Yes, you can cast Hunter\'s Mark on an invisible enemy as long as you can see the creature. The spell states, "You choose a creature you can see within range," and since Hunter\'s Mark does not specify that the target must be visible, you can apply the mark to an invisible creature that you can see"
# There is some sense to this adjudication of "yes you can, if you can still see them" (e.g. if the invisible entity has had Fairy Fire cast upon it, or if the caster has Blindsight/Truesight)
#   but it's not exactly a clear adjudication. In 99% of situations, the answer to this question should be "No."
ADJUDICATION_PROMPT = """
Users are playing an RPG. They will ask questions pertaining to the rules, setting, lore,
and current situation. You will answer the question based on the content provided.

Use only the content provided. IMPORTANT: Do NOT base your answers on ANYTHING other than the content itself.
Quote the content verbatim if possible (but only if it is relevant to the question!).
Otherwise, keep your answer as brief as possible. Do NOT include phrases from the original question in your response.
If the content is not sufficient to answer the question, say so.
"""


def get_client(model):
    if model == "gpt-4o":
        return openai_client
    elif model == "claude-3.5":
        return anthropic_client
    else:
        raise Exception("No such model implementation")


def generate_keywords(client, question):
    return client.chat_completion(system_prompt=SEARCH_PROMPT, messages=[
        {
            "role": "user",
            "content": [{
                "type": "text",
                "text": question
            }]
        }
    ])


def query_elastic(keywords, question, settings, game):
    data = {
        "query": {
            "match": {
                "content": {
                    "query": keywords,
                    "operator": "or",
                    "boost": settings["keywordWeight"]
                }
            }
        },
        "knn": {
            "field": "content-embedding",
            "k": 10,
            "boost": settings["knnWeight"],
            "num_candidates": 10,
            "query_vector_builder": {
                "text_embedding": {
                    "model_id": "open-ai-embeddings",
                    "model_text": question
                }
            }
        }
    }

    if settings["keywordWeight"] == 0:
        del data["query"]
    if settings["knnWeight"] == 0:
        del data["knn"]

    results = elastic_request(
        url=f"{game}*/_search",
        data=data
    )

    results.raise_for_status()
    hits = results.json()["hits"]["hits"]

    return [h["_source"]["content"] for h in hits]


def generate_response(client, context, history):
    response = client.chat_completion(
        system_prompt=ADJUDICATION_PROMPT,
        messages=[
            {
                "role": "assistant",
                "content": [{"type": "text", "text": c} for c in context]
            },
            *history
        ]
    )

    return response


def query(history, knnWeight=0.4, keywordWeight=0.6, model=GPT_4O, game="dnd-5e"):
    """
    @description
    Make a ruling on a question pertaining to D&D rules, using the source material as context.

    @params
    conversation: Dict[{role: str, content: str}]
      The entire conversation the user is having with the rules. The last element is typically the question to be ruled upon

    @return
    response: str
      the response to the question

    @examples
        query("Can a Warlock acquire cantrips from another class's spell list?")
          => "Yes, if they have the Pact of the Tome. This allows the Warlock to choose three cantrips from any class's spell list, and these cantrips don't count against he number of cantrips they know."

        query("My Strength is 18. I will take a running jump. How far can I make it?")
          => "You can cover a number of feet up to your Strength score if you move at least 10 feet on foot immediately before the jump. With a Strength score of 18, you can jump up to 18 feet."
    """
    client = get_client(model)
    if not history:
        return "Please provide a question."
    question = history[-1]["content"]
    keywords = generate_keywords(
        client, question) if keywordWeight > 0 else None
    context = query_elastic(keywords, question, {
                            "knnWeight": knnWeight, "keywordWeight": keywordWeight}, game)

    return {
        "response": generate_response(client, context, history),
        "keywords": keywords,
        "context": context
    }


if __name__ == "__main__":
    conversation = []
    while True:
        question = input("Type message: ")
        if question == "exit":
            break
        conversation.append(
            {
                "role": "user",
                "content": question
            }
        )
        answer = query(conversation, model=CLAUDE_35)
        print(answer["response"])
        conversation.append(
            {
                "role": "assistant",
                "content": answer["response"]
            }
        )
