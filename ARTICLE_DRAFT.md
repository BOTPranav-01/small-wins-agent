# Weekend Agent Challenge: Small Wins

I built Small Wins for the moments when a normal to-do list makes everything feel worse.

It is a small personal AI agent for overloaded students, builders, and knowledge workers. You paste in the messy version of what is on your mind, choose your energy level, and it gives you one realistic next action that should take about ten minutes. It also gives a short explanation, a permission slip to stop after that action, and a gentle suggestion for what to do next.

The idea came from noticing that “helpful” productivity tools often create another large list. Small Wins takes the opposite approach: make the first step smaller, clearer, and less emotionally expensive. The delightful detail is the permission slip. The agent does not just say “do this next”; it says that stopping after this step is allowed. That makes the interaction feel more like a supportive nudge than a productivity lecture.

## How I built it

The frontend is a deliberately simple static page. It has a single text area, two small choices, and a result card that makes the next action easy to copy. It also has a demo mode so someone can understand the experience before connecting an AWS account.

The live API is an AWS Lambda function written in Python. The function validates the request, sends a carefully bounded prompt to Amazon Bedrock using the Converse API, parses the response as JSON, validates the required fields, and returns the plan. I used a strict output shape because a friendly interface still needs predictable data. If Bedrock returns an incomplete answer or the request fails, the API reports an error instead of pretending everything worked.

## AWS services and architecture

The agent uses Amazon Bedrock for the model response, AWS Lambda for the API logic, and Amazon API Gateway for the HTTPS endpoint. The frontend can be hosted in Amazon S3. CloudWatch Logs gives me a place to inspect failures without storing the user's thought dump in the application.

The flow is:

`Browser → API Gateway → Lambda → Amazon Bedrock → Lambda → Browser`

I chose a small serverless architecture because the important part of this challenge is the agent experience, not building a complicated platform. It is also easy to deploy with AWS SAM and easy to remove when the experiment is over.

## What I learned

The most useful lesson was that “delightful” is often a constraint, not an animation. Limiting the agent to one action made the prompt, response schema, interface, and error handling better. I also learned to treat model output as untrusted input: validate it, keep the fallback honest, and make failures visible.

The project is open source here: **[add the public GitHub URL]**.

The live demo is here: **[add the deployed URL]**.

The source code includes the SAM template, the Lambda handler, and the static frontend so the whole experiment can be reproduced.

`#agents`
