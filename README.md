# Medical AI Assistant

## Introduction

This project implements an AI-powered medical assistant designed to help doctors interact with their information system through natural language, it is possible to either talk to the model via a **chat interface** or via a **voice call**

The system combines conversational AI with database interaction capabilities while prioritizing efficiency, low latency, and **local deployment**. Instead of relying on a single large model to handle every task, the architecture uses two extremely lightweight specialized models:

- **qwen2.5:1.5b:** A conversational model responsible for general dialogue and guiding the user.
- **qwen2.5-coder:3b:** A specialized SQL generation model responsible for translating medical requests into database operations.

Both models are intentionally kept small to minimize hardware requirements. Their combined memory footprint allows them to run simultaneously on any standard computer **locally** without requiring expensive infrastructure or dedicated AI hardware.

This approach demonstrates that efficient AI systems do not always require massive models. By combining specialized models with a carefully designed software architecture, it is possible to achieve fast responses, lower resource consumption, and reliable task execution.

## Why Small Language Models Are Sufficient

A common approach when building AI systems is to use the largest possible model and provide it with all available information. However, for database interaction tasks, this approach introduces several problems: larger context windows increase latency, consume more memory, and can make the model more likely to confuse unrelated information.

This project follows a different approach: instead of increasing the model size, the complexity of the problem is reduced through software architecture.

The database is divided into multiple specialized domains. For example, a medical database containing many tables could be organized as:
```text
Medical Database
|
├────────── Patients Domain
│             ├── patient
│             └── medical_history
│
├────────── Appointments Domain
│             ├── patient
│             └── rdv
│
├────────── Medical Acts Domain
│             └── acte_medecin
│
└────────── Notes Domain
              └── note_patient
```

Each domain has its own optimized context containing only the relevant tables, columns, relationships, and rules.

``This reduction of context size provides several advantages:
``
- **Higher accuracy:** we don't confuse the model with a huge schema of dozens of tables each containing dozens of columns + a pile of foreign key constraints
- **Lower latency:** smaller prompts require less processing time
- **Lower hardware requirements:** small specialized models can run efficiently on standard computers, therefore in local deployment, with the right hardware, you can easily run many many instances and allow multi-threading
- **Better scalability:** because each model instance requires limited resources, multiple instances can be deployed simultaneously to handle many users.

> A larger model does not automatically guarantee perfect database reasoning. Even very powerful models can make mistakes when presented with a large schema containing many tables, columns, and relationships. So we must isolate irrelevant relationships away 

> note that using smaller models means fewer constraints means more overhead in the determinisitc layer surrounding the model, but it's what makes the model behavior predictable and monitored !


## Services

The application is composed of several independent services:

### Voice Gateway
- Main API gateway of the application.
- Handles communication between the user interface, AI models, and database tools.
- Manages conversations and decides which operations should be executed.
- Speech-to-text module for converting doctor speech into text.
- Text-to-speech module for generating voice responses.

### Conversational Model
- Lightweight language model responsible for general interaction.
- Helps maintain natural conversations and guides users toward available functionalities in the UI

### SQL Generation Model
- Specialized model responsible for converting user requests into PostgreSQL queries.
- Receives only the relevant database context depending on the selected domain.

### Database Service
- PostgreSQL database storing medical information : Contains entities such as patients, appointments, medical acts, and notes.
- redis to save the messages exchanged

---
## Running the Project
Make sure you have ollama installed with the two models mentioned above as well
```bash
docker compose up --build
```
then go to:
```bash
http://127.1:3000
```