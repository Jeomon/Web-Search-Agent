You are asked to generate episodic memory by analyzing conversations to extract key elements for guiding future interactions. Your task is to review the conversation and output a memory object in JSON format. Follow these guidelines:

1. Analyze the conversation to identify meaningful and actionable insights.
2. For each field without enough information or where the field isn't relevant, use `null`.
3. Be concise and ensure each string is clear and actionable.
4. Generate specific but reusable context tags for matching similar situations.
5. Your response should only have one json object.

Your output must strictly conform to the following JSON schema:
```json
{
    "tags": [
        string, ...
    ], // 2-4 keywords to help identify similar future conversations.
    "id": string, //the id of the memmory to be filled by the user (so keep it blank)
    "summary": string, // Describes what the conversation accomplished.
    "what worked": string, // Highlights the most effective strategy used.
    "what to avoid": string // Describes the important pitfalls to avoid.
}
```