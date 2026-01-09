This is a dump of the things I'm reading about evals:
- [Hugging Face Guidebook](https://huggingface.co/spaces/OpenEvals/evaluation-guidebook#reasoning-and-commonsense)

Many of the evals seem to be in a MCQ format, so that's something we need to support

Questions I'm trying to answer:
1) what eval dataset formats should we allow?
2) How to manage and run these evaluations?
    - Currently, we have threads calling the running chat completion
    - the output is then judged by the LLM based on each guideline
    - logs of this is dumped to the database

What's the problem/question?
- are all real-world evals like this?
- how can we build generic platform that can support different types of evals?
    - from chat completion judged by LLM, to MCQ, etc.

What's already available?
- OpenAI evals
- HF lighteval
- ...

How are these different? what capabilities does each provide?
Can we use these, or we need to build one for ourselves?


Recreate Open LLM Leaderboard with open-source models:
- BBH
- GPQA
- IFEval
- MATH
- MMLU-Pro
- MuSR