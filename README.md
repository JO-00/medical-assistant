# Session Management Technical Report


The session management module is responsible for maintaining conversational state between a doctor and the medical assistant agent

The objective is to provide the language model with the minimum required context while keeping deterministic operations outside the model whenever possible

The biggest challenge faced was a very tiny model (qwen2.5:3B) that must be multilangual, be conversational and warm, perform correct CRUD operations and correct relative time interpretation where even the biggest models make calculation mistakes

**The complete pipeline can be summarized as follows:**

                                        User Message
                                            |
                                            v
                                   +--------------------+
                                   | Session Manager    |
                                   +--------------------+
                                            |
                                            v
                                   +--------------------+
                                   | Intent Router      |
                                   | (Embedding based)  |
                                   +--------------------+
                                            |
                        +-------------------------+----------------+
                        |                                          |
                        v                                          v
                conversational                                  database
                        |                                          |
                        |                                          v
                        |                                  +----------------+
                        |                                  | Time Detection |
                        |                                  | Pipeline       |
                        |                                  +----------------+
                        +-------------+                            |
                                      |                            v
                                      v                      Time-normalized
                        Dynamic Context Injection                message
                                      |
                                      v
                                LLM Processing
                                      |
                                      v
                             Response Generation


---
#### Overview of Session:

The central object representing a conversation is:

```python
class ConversationHistory(BaseModel):
    doctor_id: int
    session_id: Optional[int]              
    content: List[tuple[str, str]]         <--  [history to be injected right after dynamic context]
    timestamp: Optional[datetime]
    dynamic_context: str                   <--  [A dynamically chosen context injected depending on the domain of the prompt]
    detected_language: Optional[str]       <--  [as we accumulate user messages over a time for a given session, at some point we detect language deterministically: meaning no ML involved]
    intent: Optional[str]                  <--  [either "conversational" or "database", it's the job of the router, if router is uncertain which is rare we call an LLM to classify]
    last_response: Optional[str]           <--  [LLM response to most recent prompt for easy access]
```
Each session is isolated using the pair: `doctor_id + session_id`
> Note that for now, a simple POST request is needed to the server of the format {"doctor_id" : 1 , "session_id" : 1 , "message" : "prompt"} so in the future we'll use JWT tokens cuz this approach obviously made for debugging not production

**This allows:**

- Each doctor to maintain multiple independent conversations that can use different languages each (even with a model as small as 3B)
- Independent context injection per session (new dynamic context every new prompt per session because model is tiny and can't handle giant global context cuz it'd exhaust context window size and make it halucinate)

> **note :** for every LLM inference, we talk to the llm_service container to ensure seperation of concerns (it has two endpoints : `/llm_service` and `/ollama`)


#### Router's job
Given the embeddings of two clouds of vectors:
- **cloud 1** : conversational-like (greet , joke etc)
- **cloud 2** : statments that query database (like naming database fields or performing CRUD)

Given a user prompt, we calculate its embedding and measure its distance between cloud 1 and cloud 2, then :

$$
\text{margin} = \left| d(\mathbf{e}_{\text{prompt}}, \mathbf{C}_1) - d(\mathbf{e}_{\text{prompt}}, \mathbf{C}_2) \right|
$$
Where:
𝒆_𝒑𝒓𝒐𝒎𝒑𝒕  = embedding vector of user input
𝑪₁         = embedding cloud for conversational intent
𝑪₂         = embedding cloud for database query intent
𝒅(·, ·)    = distance from a cloud doesnt mean distance to centroid, but rather distance to closest vector (cuz centroids include noise from far vectors lowering margin)


if the margin is big enough, we prepare the dynamic contexts related to the task

otherwise if its to small, it shows uncertainty so we call the LLM to classify (we rarely ever get to that due to a good choice of the initial clouds, we made sure they are as distinct as possible to ensure that most vectors must lay near one and far from the other)

#### Dynamic Context
for each given prompt, we append it to session object of `doctor_id` and `session_id`, then the pipeline for that specific new prompt begins :

- determine the intent of prompt : `conversational | database` via the two clouds idea 
- if we're still not certain of detected_language despite the history of the session, we give all user inputs in that session using pycld2 until it finally language is finally detected it
- if intent == `conversational`, we just fetch the conversational prompt of the right detected language (if no language detected yet we always use english), we talk to LLM and get response easily
- if it's `database`, we firstly watch out for key words like `today|next week|last month|the 3rd of july` etc and we never feed them directly to the LLM because it's always guaranteed to halucinate (even massive models might halucinate), two outcomes :
    - after a quick deterministic time indicator check (fragile but mostly accurate and will be improved) , if nothing exists we append the user prompt as it is
    - otherwise we call the LLM forcing it to output a valid json like this :
    `{'time_string_literal': "aujourd'hui", 'absolute_date': {'day': None, 'month': None}, 'weekday_target': {'weekday': None, 'is_relative_next': False}, 'relative_jump': {'unit': 'day', 'amount': 0}, 'time': {'hour': None, 'minute': None}}` and we deterministically substitute high entropy time indication with soemthing like `YYYY:MM:DD HH:MM:SS` (we mark `XX` for missing fields)
    

**How to run ?**
make sure you got ollama
```bash
docker compose up --build
curl -X POST "http://127.1:8001/session" \
  -H "Content-Type: application/json" \
  -d '{"doctor_id": 1, "session_id": 1, "message": "hmmm"}'
```
observe that language detected is still unknown, continue talking over same session
```bash
curl -X POST "http://127.1:8001/session" \
  -H "Content-Type: application/json" \
  -d '{"doctor_id": 1, "session_id": 1, "message": "les patients que je vais voir aujourd hui"}'
```





