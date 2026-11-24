# From 0.13 to 0.20: presentation script and Q&A

Speakers: Muhammad Husnain Rasool, Galymzhan Zaharas. 17 slides, about 15 minutes (about 50 seconds a slide). A suggested split: Husnain takes slides 1–8, Galymzhan takes 9–17, or swap at slide 9.

---

## Part 1. The problem and how we solved it (background for both speakers)

### The problem
Kaggle's *Gemma 4 Developer Agent* competition asks for an AI agent that fixes real bugs in real Python projects (fastapi, rich, requests, httpx). For each task, the agent receives a GitHub issue and a copy of the repository. It reads code, runs commands, edits files and submits a patch. Hidden unit tests then decide whether the issue is fixed. The score is the share of about 120 hidden issues solved.

The constraints make this hard:
- **Small, fixed model:** Gemma 4 31B (or the small E4B), 4-bit quantised. No GPT-class model.
- **Fixed compute:** 4 × L4 GPUs and 12 hours for all ~120 issues, so about 6 minutes of agent time per issue.
- **Configuration only:** we can change the prompt, tools, sampling settings, time and call limits, and optionally a LoRA adapter. We cannot change the harness.
- **No tests at selection time:** the agent cannot see the hidden tests, so it cannot check its own answer the way published systems do.

**Starting point.** The public *Budget-Fit* agent, which most teams used as a stable baseline: 47.9 of 118 local tasks, and 0.13 on the leaderboard.

### How we solved it
1. **Built a trustworthy local evaluation.** The public harness needs Docker, and our university cluster allows only Apptainer. We wrote a replacement and found three bugs in the public setup that silently changed scores (one let 38 tasks "pass" with an empty patch). After the fixes, our grader matches the official labels on 118 sound tasks.
2. **Measured noise first.** The same configuration solves a different number of tasks on every run (about ±5 tasks). So every comparison uses several random seeds per configuration, a paired bootstrap test over tasks, and a "screen, then confirm on fresh seeds" rule fixed in advance.
3. **Tested the three big levers,** about 15,000 agent runs in total:
   - **More test-time compute** (sample several runs and pick one): did not beat simply giving one run a bigger budget, and patch selection without tests did not generalise.
   - **Fine-tuning** (three LoRA recipes): all three made the agent worse.
   - **Agent design:** this is what worked.
4. **Improved the agent in steps.** First we adopted the strongest public workflow, *Patchsmith* (+2.3 tasks). Then we analysed 708 of its runs: on tasks that some runs solve and others fail, what do the solved runs do differently? Mostly, they check their fix after the last edit, but the prompt wrongly told the agent that pytest might not work. We changed four sentences of the prompt (*Patchsmith-check*).
5. **Result:** 47.9 → 51.9 local tasks (+4.0, 95% CI [+0.9, +7.2]); runs wasted on limits 9.2 → 2.7 per run; Kaggle 0.13 → 0.20, at the same compute.

**One-sentence version:** for a small agent on a fixed budget, the main problem is wasted and unverified runs, and fixing the agent's process beat more samples or new weights.

---

## Part 2. Full script, slide by slide

### Slide 1 — Cover: "From 0.13 to 0.20"
"Good morning. We are Muhammad Husnain Rasool and Galymzhan Zaharas. Our project is about AI coding agents: programs that use a language model to fix bugs in real software. We worked in a Kaggle competition where the model, the hardware and the time are all fixed. We started from a public agent that scored 0.13 on the leaderboard and ended at 0.20 without any extra compute. In the next fifteen minutes we will show how we got there, and what did not work along the way."

### Slide 2 — Problem: "Fix real GitHub issues with a small open model on fixed compute"
"Here is the task. The agent gets a real GitHub issue and a copy of the repository. It explores the code with shell and file tools, edits files and submits a patch. Hidden unit tests decide whether the issue is solved.

On the right are the rules. The model is Gemma 4, 31 billion parameters, quantised to 4 bits. The compute is four L4 GPUs for twelve hours, covering about 120 hidden issues, so roughly six minutes per issue. We can only change the configuration: prompt, tools, sampling, limits, and optionally a LoRA adapter. And the score is simply the share of issues solved.

Most published coding agents use frontier models, unlimited compute and tests to choose between patches. We have none of that, which makes this a realistic setting for anyone who has to run an open model locally."

### Slide 3 — Headline result
"Let us give you the result first. On the left: on our 118 local tasks, the public Budget-Fit baseline solves 47.9 per run; our final agent solves 51.9. That is four more tasks, and the 95% confidence interval, from plus 0.9 to plus 7.2, does not include zero.

In the middle: runs that end because they hit a time, call or turn limit fall from 9.2 to 2.7 per run, a 71% drop. Those runs almost never solve anything.

On the right: on Kaggle's hidden issues, the score went from 0.13 to 0.20. Same model, same limits, same time per task. The gain comes from agent design, not from more compute."

### Slide 4 — Research questions
"We organised the work around four research questions, one for each lever a practitioner has.

RQ1, measurement: how noisy is a single evaluation, and how many runs do we need? Short answer: about plus or minus five tasks per run.

RQ2, test-time compute: with the same compute, should we make one run longer or run several short ones and pick the best patch? Longer runs win.

RQ3, weights: does LoRA fine-tuning on successful runs help? No, all three versions hurt.

RQ4, agent design: can analysing the agent's traces tell us what to change, and does that transfer to hidden tasks? Yes. This gave us the final step, 0.17 to 0.20."

### Slide 5 — Related work
"Briefly, where this sits. SWE-bench defined this task format; SWE-agent, OpenHands and Agentless are well-known agent designs, all built on the ReAct pattern of reasoning plus tool calls. Test-time scaling papers such as Large Language Monkeys and CodeMonkeys show big gains from sampling many patches, but they pick the winner with tests or a trained verifier, which we do not have. Agent fine-tuning work such as SWE-Gym and SWE-smith trains on hundreds to thousands of tasks; we have fewer than fifty. And evaluation papers argue for error bars and cost-aware comparisons, which we apply to a live leaderboard. The report cites 27 papers."

### Slide 6 — Data and grader
"The competition released 129 public tasks. We applied the correct patch and an empty patch to each one and kept the tasks where the correct patch passes and the empty one fails: 118 sound tasks.

Getting a trustworthy grader was a project in itself. Our cluster does not allow Docker, so we wrote a replacement using Apptainer, and we found three bugs in the public setup that silently changed scores. First, bundled packages hid the code under test, so 38 empty patches 'passed'. Second, installing the newest library versions broke old code snapshots, so we pin the newest version released before each issue. Third, a shared cache let parallel jobs reuse the wrong environment. After the fixes, our grader matches the official labels. In total we ran more than 15,000 agent runs."

### Slide 7 — Method: "Measure, contrast traces, edit, confirm"
"This diagram is our loop. Each agent configuration runs on all 118 tasks, with several random seeds. Our grader scores the final patches, and we keep the full traces: every thought, tool call and result.

Then comes the key step, in orange. We compare solved and failed runs of the same task, turn what separates them into prompt edits, and accept an edit only if it passes a three-seed screen and then a confirmation on fresh seeds, with thresholds we fixed before looking.

Below are the details. The baseline is Budget-Fit: 8 minutes, 28 tool calls, temperature 0.2. Every comparison is paired over the same tasks, with bootstrap confidence intervals. The red box shows the other levers we tested, compute and fine-tuning."

### Slide 8 — Improvement path
"This figure shows every step against the baseline. Panel a: tasks solved, each circle one run. The baseline averages 47.9. Our budget guard and the public pub_v6 prompt were within noise. Adopting the public Patchsmith workflow brought 50.2, and our trace-guided version reached 51.9.

Panel b shows why: runs stopped by a limit drop from 9.2 to 2.7. Panel c is the hidden leaderboard, rising steadily from 0.13 to 0.20. Each single step is within leaderboard noise, shown by the error bars, but the whole path is about one and a half standard deviations. To be clear about credit: grey steps marked public are configurations we adopted; the guard and the final step are ours."

### Slide 9 — RQ1: noise
"Now the evidence for each question, starting with measurement. We ran the same configuration ten times. About half the tasks are never solved, a quarter always, and 31 tasks, about a quarter, flip between runs. If we model each task as a weighted coin, one run has a 95% range of about plus or minus five tasks, and the model predicts the spread we observe. So even with five runs per configuration, we cannot reliably detect a difference smaller than four or five tasks.

The leaderboard is noisier still: identical configurations submitted by different teams scored anywhere from 0.08 to 0.20. That is why we never trust a single run or a single submission."

### Slide 10 — RQ2: budget versus samples
"Second, test-time compute. The x-axis is the real compute spent per task, in minutes; the y-axis is tasks solved. Each line is a budget level, and points further right add more runs per task plus a selector.

The short-budget line, in blue, is below the others at every cost. One medium run beats one short run by almost five tasks. Five short runs plus a selector cost 2.6 times as much as one long run and are not better.

The reason is wasted runs. A run that ends without a usable patch, or hits a limit, never solves anything. With a bigger budget these drop from 20% to 4%, and the extra budget is cheap, because most runs finish early anyway."

### Slide 11 — RQ2: selection without tests
"Could a clever selector rescue sampling? On the first five seeds, our best rule (drop invalid runs, prefer a passing final check, then the smallest patch) recovered 72% of the possible gain. We wrote the rule down, froze it, and tested it on five new seeds. It fell to 34%, exactly the same as just dropping invalid runs, the dashed grey line. Asking Gemma itself to judge patches added nothing.

Among five long runs there is a correct patch for 70 tasks, but the best selector finds only 58. Without tests, choosing the right patch is the bottleneck, not generating one."

### Slide 12 — RQ3: LoRA
"Third, fine-tuning. We trained three LoRA adapters on successful agent runs, and each one made the agent worse, for a different reason.

Self-training on the model's own solved runs: no change on the training tasks, and minus 2.7 on held-out tasks, a significant drop.

Distillation from a stronger Qwen model: minus 22.7. The agent learned to call submit before making any edit; 1,410 of 1,550 submissions were empty, although no training example ever did that.

Distilling the 31B model into the small E4B model: minus 8.7. It fell into thinking loops, and 88 of 118 runs timed out."

### Slide 13 — RQ3: diagnosis
"This histogram explains the E4B failure. It shows how many tokens the model generates per step. The base model, in blue, tails off smoothly. The fine-tuned model, the red outline, has a spike at exactly 4,096 tokens, the thinking limit: 2,527 steps hit it, against 6 for the base model. It repeats itself until the limit cuts it off.

We audited the training labels (stop tokens, windows, chat template) and found no bug. We also saw that the Qwen adapter's training loss fell from 1.02 to 0.38 while it learned the broken behaviour, so a falling loss does not mean a better agent. The likely causes are too few distinct tasks, copying a teacher's style, and repetition in a smaller student."

### Slide 14 — RQ4: trace analysis
"Fourth, agent design. We took Patchsmith, the best public workflow, and analysed 708 of its runs. On the left is a manual audit of 30 failures. Some are hard limits of the model, like issues that do not name the API the tests expect. But the orange ones, a missed final check and edit loops, are process mistakes a prompt can fix.

The key method is a within-task comparison: on tasks solved by some runs and failed by others, what differs? A check of the behaviour after the last edit: 88% of solved runs versus 47% of failed ones. pytest worked in 94 of 134 calls, yet only 8% of runs ended with it, because the prompt said pytest might be disabled. And the popular advice to reproduce the bug first shows no effect within a task; it only looks useful because easy tasks are easier to reproduce."

### Slide 15 — RQ4: Patchsmith-check
"So we changed four sentences of the prompt: pytest works here; follow a four-step final checklist; retry failed edits differently; keep scratch files in /tmp. Nothing else changed.

The targeted behaviours moved as intended. pytest as the final check tripled, from 9% to 27% of runs, and stray scratch files disappeared. On the first screen we saw plus 3.8 tasks; on fresh seeds it shrank to plus 0.8, which is the normal regression after picking a winner. Pooled under our pre-registered rule it was plus 1.6, which passed our bar. On Kaggle it scored 0.20, our best of five submissions."

### Slide 16 — What did not help
"Here is the list of things that tied or lost, each tested with three runs against a matched baseline. Sampling with selection, all three LoRA recipes, parallel solvers, helper scripts, higher temperature, a frequency penalty, a smaller or larger thinking budget, and in our last round, a reviewer agent and an extra checklist step on top of our final agent.

The pattern is the main lesson: what helped acted on one failure mode, wasted and unverified runs. More samples, more thinking and new weights did not."

### Slide 17 — Conclusions and limitations
"To conclude. We improved a small open-weight coding agent from 0.13 to 0.20, plus four local tasks, at the same compute. Our recommendations: count real compute, not nominal limits, and spend it on a larger budget per run rather than on more samples; use several runs, paired tests and confirmation on fresh seeds; and derive agent changes by comparing solved and failed runs of the same task.

Limitations: one model family; four repositories, mostly fastapi and rich; we ran on H100s, not L4s; and the last prompt gain is small on fresh seeds alone. Thank you. We are happy to take questions."

---

## Part 3. Likely questions and answers

**Novelty and framing**

**Q: What is new here, compared with SWE-agent or Agentless?**
A: The setting and the method. Published work uses frontier models, large budgets and tests or verifiers to select patches. We study a small open model with a hard compute cap and no tests, and show which popular levers fail there. Methodologically, the within-task contrast of solved and failed traces, plus pre-registered screen-and-confirm gates, is what found the improvement.

**Q: Isn't the improvement mostly from adopting someone else's agent (Patchsmith)?**
A: Partly, and we say so: about 60% of the local gain (+2.3) came from adopting Patchsmith, and 40% (+1.6) from our change. Our contributions are the grader, the evaluation method, the negative results on compute and LoRA, and the trace-guided change that gave the last step and the best leaderboard score.

**Q: Why call it deep learning if the final change is a prompt?**
A: The system is a deep model acting as a policy; we studied test-time compute, LoRA fine-tuning (rank 16 on all attention and MLP layers, masked next-token loss, windowed training), distillation, and diagnosis of model behaviour such as repetition loops. The prompt result is the outcome of that study, not a replacement for it.

**Statistics**

**Q: Is +4.0 significant? Is +1.6?**
A: +4.0 over the baseline: yes, the 95% paired-bootstrap interval is [+0.9, +7.2]. +1.6 over Patchsmith: not on its own ([−0.8, +4.2]); it passed our pre-registered bar of +1.5, and the behaviour changes it targeted are large and clear (9% → 27% pytest as final check). We are careful not to oversell that step.

**Q: Why a paired bootstrap?**
A: Both agents run on the same tasks, and task difficulty varies far more than agent quality. Pairing by task removes that variation. We resample tasks, not runs, because tasks are the unit we want to generalise over.

**Q: Isn't 0.13 → 0.20 within leaderboard noise?**
A: Each single step is (SD 0.048). The whole path is about 1.5 SD, it is monotonic across five submissions, and it agrees with the local results, which use many runs. We rely on the local evidence and use the leaderboard as confirmation.

**Q: Did you overfit to the 118 public tasks?**
A: We used fresh seeds for confirmation and held-out tasks for LoRA. The prompt change contains no task-specific content, and it improved the hidden leaderboard, which uses different issues.

**Q: Why are local scores ~44% but Kaggle ~20%?**
A: The hidden tasks are harder. We ran 26 public tasks inside a Kaggle notebook: our predicted solve rate matched, and L4 time was 1.17× H100 time. So hardware does not explain the gap.

**Compute and selection**

**Q: Why not use more samples with majority voting?**
A: Voting needs comparable answers; patches differ syntactically even when correct. We tested consensus, heuristics and Gemma as a judge. None beat simply dropping invalid runs on fresh seeds, and five runs cost 2.6× one long run.

**Q: Could the agent write its own tests to select patches?**
A: That is what CodeMonkeys does with a large model. Within about 6 minutes per issue, a small model has little time left for that, and its generated tests are unreliable. It is a good direction for future work.

**Fine-tuning**

**Q: Why did LoRA fail, and would more data fix it?**
A: We had 126–169 episodes from at most 46 tasks, two orders of magnitude fewer than SWE-Gym or SWE-smith. Self-training mostly reinforces what the model already solves. Distillation copied the teacher's style (submitting early) or produced loops in the small student. More distinct tasks would likely help, but the competition does not provide them.

**Q: Was the training buggy?**
A: We audited it: stop tokens, window boundaries, chat template and loss masking were all correct. One possible factor we report: the training traces had no thinking text, while inference runs with thinking on.

**Q: Did you try full fine-tuning or RL?**
A: Not within the competition: submissions accept only LoRA adapters, and RL on agent runs at 6 minutes each was beyond our compute.

**The prompt change**

**Q: Why does such a small prompt change matter?**
A: It removed a false belief. The old prompt said pytest might be disabled, so the agent rarely ran the tests; but checking after the last edit is the behaviour that most separates solved from failed runs. The change made that behaviour three times more common.

**Q: What does "within-task" mean, and why does it matter?**
A: We compare solved and failed runs of the same task, so task difficulty cannot explain the difference. "Reproduce the bug first" looks helpful across tasks (64% vs 38%) but shows no effect within a task (0.53 vs 0.50): easy tasks are simply easier to reproduce. Without this control we would have optimised the wrong behaviour.

**Q: What if pytest is unavailable on Kaggle?**
A: We tested that: with pytest disabled, the new prompt cost only 0.8 tasks, and it includes a fallback instruction.

**Practical**

**Q: How long did it take, and on what hardware?**
A: Over several weeks, more than 15,000 agent runs on 2 × H100 per job on the university cluster, plus about 8 hours per LoRA training run on 4 × H100.

**Q: What about the small E4B model?**
A: The budget lesson helped it too: a 12-minute / 40-call budget raised it from 17.3 to 19.0 tasks, with no timeouts. Distilling the 31B model into it hurt (−8.7).

**Q: What would you do next?**
A: Try a lightweight verifier that is cheap enough for the budget, build training data from more repositories, and test the trace-contrast method on other models and benchmarks such as SWE-bench Lite.
