import requests
import json
import os

from openai import OpenAI

from utils.elastic import elastic_request

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


def generate_keywords(client, question):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "developer",
                "content": [{
                    "type": "text",
                    "text": SEARCH_PROMPT
                }],
            },
            {
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": question
                }]
            }
        ]
    )

    return completion.choices[0].message.content


def query_elastic(keywords, question):
    results = elastic_request(
        url="players-handbook-embedded/_search",
            data={
                "query": {
                    "match": {
                        "attachment.content": {
                            "query": keywords,
                            "operator": "or",
                            "boost": 0.7
                        }
                    }
                },
                "knn": {
                    "field": "content-embedding",
                    "k": 10,
                    "boost": 0.3,
                    "num_candidates": 10,
                    "query_vector_builder": {
                        "text_embedding": {
                            "model_id": "open-ai-embeddings",
                            "model_text": question
                        }
                    }
                }
            })

    results.raise_for_status()
    hits = results.json()["hits"]["hits"]
    # logger.debug(hits)
    return [h["_source"]["attachment"]["content"] for h in hits]


def generate_response(client, context, question):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "developer",
                "content": [{
                    "type": "text",
                    "text": ADJUDICATION_PROMPT
                }],
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": c} for c in context[0:3]]
            },
            {
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": question
                }]
            }
        ]
    )

    return response.choices[0].message.content


def query(question):
    """
    @description
    Make a ruling on a question pertaining to D&D rules, using the source material as context.

    @params
    question: Str
      the question to be ruled upon

    @return
    response: str
      the response to the question

    @examples
        query("Can a Warlock acquire cantrips from another class's spell list?")
          => "Yes, if they have the Pact of the Tome. This allows the Warlock to choose three cantrips from any class's spell list, and these cantrips don't count against he number of cantrips they know."

        query("My Strength is 18. I will take a running jump. How far can I make it?")
          => "You can cover a number of feet up to your Strength score if you move at least 10 feet on foot immediately before the jump. With a Strength score of 18, you can jump up to 18 feet."
    """
    client = OpenAI()
    keywords = generate_keywords(client, question)
    context = query_elastic(keywords, question)

    return generate_response(client, context, question)


if __name__ == "__main__":
    print(query("I rolled a 27 to hit a creature with an 18 Armor Class. Was I successful?"))
