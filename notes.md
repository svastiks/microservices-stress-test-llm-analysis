- Better way to determine next iteration. exponentially
- few shots
- look at real microservice examples
- analyzer should work both upwards and downwards (over-provished vs under-provished)
- look at cpu, mem, p95 to decide how much the reduction needs to be for next iteration (might fail the service)
- upper bound vs lower bound
- ensure we get the memory and cpu utilization to determine bottleneck

if SLO_violated & !error_rate_violdated:
still reduce
elif SLO_violated & error_rate_violdated:
terminate
lower bound and upper bound by average
look at utilization

research questions:

- intro about the problem
- related works (public) => to find baselines as well OR HPA
- methodology
  - formualas
  - architecture
  - pseudocode
- setups and experiments
- results
- conclusion

Method 1 => formula
vs
Method 2 -> LLM

Provide formula to the LLM and ask for the next recommendation.

Rewards and penalty

sampling every 10 seconds for cpu utilization, ignore the spike

and then I noticed a lot of the DOWN runs in vanialla never failed

https://dl.acm.org/doi/pdf/10.1145/3342195.3387524

CASCON due date

In two lines reply to what I'm saying, if you agree or disagree if we're going in the right direction. So when I presented my last results, which is the artifacts for vanilla and formula down and up, the main thing that came up is, oh, one side, like I already mentioned to you, one side with more resources there was lower CPU utilization and maybe everything was passing the filling, but then on the other side with even less resources, things were passing. So how can the same RPS, same service? Fail with more resources, but then pass with less resources on one side. So that's why we do the verification runs to make sure like the runs aren't wrong. So the whole point is that we, in the replay runs, we look at the CPU utilization, the memory per iteration the, the CPU per iteration, the replicas per iteration, we're looking at all the numbers and we're like, okay, is it consistent or did we make some shit up? Did the LLM make some shit up? We need to make sure that the LLM isn't making some shit up. We need to be careful, we can't just fake numbers, right? We need to make sure these are real numbers, we need to make sure there's no weird shit going on. Like the logic is, if you're running side by side on the same service, same request per second, how can one side, so the formula side, fail with more resources, but then the other side keep scaling down and keep passing until it reaches a certain point? Both sides should fail around the similar resources. Which is why the question came up, are we like measuring CPU utilization, which you said we were, because you said that we were ba-basing it off of quests, and now you're averaging it, right? So, so these things need to be compared and these things need to be fixed.

Fixes to make burn trustworthy
Warmup k6 — e.g. 60–120s load before the measured 90s window (discard warmup from metrics).
Shorter rate window — rate[1m] or irate for 90s tests instead of rate[5m].
Drop first iteration after baseline from burn/cost comparisons (or tag cold_start: true).
Paired probe — both configs in one job, back-to-back, after shared warmup (the real proof).

## CPU utilization improvements

- PASS/FAIL gate now uses request CPU percent
- Limit-based cpu_util_pct kept for diagnostics only
- Prometheus averages samples instead of window peak
- Per-pod CPU series summed for accurate burn
- Shorter one-minute rate window for ninety-second tests
- cpu_util_request_pct added to every experiment JSON
- Skip CPU gate when Prometheus telemetry untrustworthy
- Comparison tables show cpu percent req column
- Replica denominator uses mean replicas not max
- Peak CPU fields kept separately for spike debugging
- DOWN decisions use request percent not limit util
