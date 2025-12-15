# LLM Integration in CBAC: A Minimalist Approach

**LLMs are the least obvious part of this system** and the easiest place to fool yourself.

**Critical principle:**
If you don't understand why the LLM exists here, you'll either overuse it or remove the one place it's actually needed.

---

## Implementation Status

### Current State (Phase P0 - Complete)
- ✅ **Templates in use**: Basic domain-based description generation
- ✅ **Fast**: No API calls, no cost
- ✅ **Reliable**: Always works, deterministic output
- ❌ **Generic**: Not context-aware, ~30 hardcoded templates
- ❌ **Brittle**: Requires maintenance for new domains

**Current code** (`core_analyzer.py` line ~85-90):
```python
description = self._generate_description_from_template(
    domain=domain,
    cluster_size=len(cluster_behaviors)
)
# ☝️ This is running NOW (templates, not LLM)
```

### Target State (Phase P2 - Planned)
- 🎯 **LLM + Cache**: Context-aware, intelligent descriptions
- 🎯 **70-80% cache hit rate**: Most patterns reuse cached abstractions
- 🎯 **Fallback to templates**: 100% uptime even if LLM fails
- 🎯 **Cost optimized**: ~$0.025 per analysis (vs $0.10 without cache)
- 🎯 **Temperature 0.3**: Constrained, predictable output

**Target code** (Phase P2):
```python
# Check cache first (70-80% hit rate)
cached_description = await semantic_cache.get(cluster.centroid)

if cached_description:
    description = cached_description
    confidence *= 0.98  # Small penalty for cached result
else:
    try:
        # Call LLM (20-30% of time)
        description = await llm_service.generate_description(
            behaviors=cluster_behaviors,
            constraints={"max_words": 15, "temperature": 0.3}
        )
        await semantic_cache.set(cluster.centroid, description)
    except (TimeoutError, RateLimitError, APIError):
        # Fallback to template (100% uptime guarantee)
        description = self._generate_description_from_template(domain, size)
        confidence *= 0.85  # Larger penalty for template fallback
```

### Migration Path
1. Implement LLM service (keep templates as fallback) ← Next step
2. Add semantic cache with Qdrant
3. Gradually increase LLM usage as cache builds
4. Monitor cost and quality metrics
5. Keep templates for edge cases and failures

---

## What the LLM is **NOT** Doing

Let's kill wrong assumptions fast.

The LLM is **NOT**:

* discovering behaviors
* clustering data
* calculating confidence
* deciding truth
* replacing rules
* "understanding" the user

All of that is **algorithmic and deterministic**.

If you think the LLM is the brain of this system, you're wrong.

---

## Why the LLM Exists

**Because machines cannot reliably write good abstractions.**

That's it.

CBAC needs **one human-readable sentence** that represents a whole cluster of similar behaviors.

Algorithms can:

* group things
* score things
* measure similarity

They **cannot** produce a *clean, natural, general statement* that:

* covers all items
* doesn't overfit
* doesn't add meaning
* doesn't lose intent

That's the LLM's only job.

---

## The Exact Problem the LLM Solves

CBAC gets this **after clustering**:

```
Cluster 01:
- "prefers visual learning methods"
- "asks for diagrams and charts"
- "requests flowcharts for explanations"
- "learns better with visual examples"
```

The system must turn that into:

> **One stable statement**
> that can be stored, compared, versioned, and shown.

### Why Algorithms Fail Here

You could try:

* keyword intersection → ugly
* TF-IDF → incoherent
* averaging embeddings → not text
* templates → brittle (our current approach)

None of those produce:

> "Prefers visual learning approaches"

But an LLM can.

---

## Where LLM Fits in the Pipeline

The LLM is called in **Step 4** of our 9-step analysis pipeline:

```
1. Fetch behaviors from Qdrant
2. Cluster with DBSCAN
3. Load previous analysis
4. Derive core behaviors
   ├─→ Evaluate cluster (promotion logic)
   ├─→ IF PROMOTED:
   │   ├─→ Check semantic cache          ← 70-80% hit
   │   ├─→ IF NOT CACHED:
   │   │   └─→ ⚡ CALL LLM (20-30% time) ← ONLY HERE
   │   └─→ IF CACHED:
   │       └─→ Reuse cached description
   └─→ Create CoreBehavior object
5. Update versions (deterministic)
6. Calculate status (deterministic)
7. Detect changes (deterministic)
8. Calculate metrics (deterministic)
9. Save analysis (deterministic)
```

**Key point:** LLM is called **ONCE per uncached cluster**, **AFTER** promotion decision, **NEVER** for rejected clusters.

---

## Minimal Example (Step-by-Step)

### Step 1: Cluster Exists (No LLM Yet)

```
Cluster size: 4
Semantic coherence: 0.82
Credibility: 0.84
Stability: 0.78
```

Cluster **passes promotion rules** (size ≥ 3, credibility ≥ 0.65, stability ≥ 0.5, coherence ≥ 0.7).

So CBAC says:

> "Okay, this deserves to become a core behavior."

But **it still has no name**.

---

### Step 2: Check Cache First

```python
# Vector similarity search in Qdrant
similar_clusters = semantic_cache.search(
    query_vector=cluster.centroid,
    limit=1,
    score_threshold=0.92  # High similarity required
)

if similar_clusters and similar_clusters[0].score >= 0.92:
    # Found similar cluster - reuse description
    return cached["description"], 0.98
```

**Cache hit:** Return cached description (70-80% of time)
**Cache miss:** Continue to LLM (20-30% of time)

---

### Step 3: LLM is Called (If Not Cached)

The prompt is **extremely constrained** (this matters):

```
Given these related behaviors:
- prefers visual learning methods
- asks for diagrams and charts
- requests flowcharts for explanations
- learns better with visual examples

Generate a concise, general statement that captures the common pattern.

Requirements:
- One sentence only
- 8-15 words (prefer shorter)
- Present tense, active voice
- No examples or specifics
- Capture the underlying intent, not surface actions
- Use domain-appropriate vocabulary

Example formats:
"Prefers [approach] for [activity]"
"Demonstrates [pattern] when [context]"

Output ONLY the statement, no explanation.
```

LLM output:

```
"Prefers visual learning approaches"
```

That's it.

No reasoning.
No personality inference.
No creativity.

Just **controlled abstraction**.

**Settings:**
- Model: `gpt-3.5-turbo` (fast, cheap)
- Temperature: `0.3` (low variance, predictable)
- Max tokens: `50` (cost control)
- Timeout: `5 seconds` (fail fast)

---

### Step 4: Cache the Result

```python
# Store in Qdrant for future similarity searches
semantic_cache.upsert(
    id=f"cache_{cluster_id}",
    vector=cluster.centroid,
    payload={
        "description": "Prefers visual learning approaches",
        "original_size": 4,
        "domain": "learning",
        "created_at": 1765813794,
        "reuse_count": 0
    }
)
```

Next time a similar cluster appears → cache hit → skip LLM → save money.

---

### Step 5: Everything Else is Still Math

After that:

* Confidence is calculated numerically
* Stability is tracked numerically
* Evidence is linked by IDs
* Versioning is deterministic

The LLM never touches those.

---

## Semantic Cache Strategy

### Cache Hit Rates by Pattern Type

| Cluster Type | Expected Hit Rate | Why |
|--------------|------------------|-----|
| **Common patterns** | 70-80% | "Visual learner", "Step-by-step", etc. |
| **Domain-specific** | 40-60% | "Python debugging", "Recipe preferences" |
| **Unique behaviors** | 10-20% | Unusual combinations |
| **First-time domains** | 0% | No cache exists yet |

**Overall: 70-80% cache hit rate after warmup period (2-4 weeks)**

### Cache Implementation Details

```python
class SemanticCache:
    """
    Cache LLM-generated descriptions using vector similarity
    """
    
    async def get(self, cluster: BehaviorCluster) -> Optional[str]:
        """
        Find cached description for similar cluster
        """
        # Use cluster centroid as search vector
        similar_clusters = self.qdrant_client.search(
            collection_name="llm_cache",
            query_vector=cluster.centroid,
            limit=1,
            score_threshold=0.92  # High similarity required
        )
        
        if similar_clusters and similar_clusters[0].score >= 0.92:
            cached = similar_clusters[0].payload
            
            # Only reuse if cluster size is similar (±20%)
            size_ratio = cluster.size / cached["original_size"]
            if 0.8 <= size_ratio <= 1.2:
                # Update reuse count
                cached["reuse_count"] += 1
                return cached["description"]
        
        return None
    
    async def set(self, cluster: BehaviorCluster, description: str):
        """
        Cache generated description with cluster centroid
        """
        self.qdrant_client.upsert(
            collection_name="llm_cache",
            points=[{
                "id": f"cache_{cluster.cluster_id}_{int(time.time())}",
                "vector": cluster.centroid,
                "payload": {
                    "description": description,
                    "original_size": cluster.size,
                    "domain": self._extract_domain(description),
                    "created_at": int(time.time()),
                    "reuse_count": 0
                }
            }]
        )
```

### Key Considerations

1. **Cluster size matters**: A 3-behavior cluster vs 10-behavior cluster gets different descriptions
2. **Score threshold 0.92**: Balances reuse vs freshness (not too strict, not too loose)
3. **Reuse tracking**: Monitor which patterns are most common
4. **Expiry**: Old entries (6+ months) should expire (implement later)

---

## Prompt Engineering Strategy

### Keep It BORING

The prompt should be:

- ✅ Constrained (specific requirements)
- ✅ Predictable (consistent output format)
- ✅ Testable (validate against rules)
- ❌ NOT creative
- ❌ NOT conversational
- ❌ NOT exploratory

### Example BAD Prompt

```
Analyze these user behaviors and tell me what the user is really like.
Be creative and give me deep insights into their personality!
```

**Why it fails:**
- ❌ Unpredictable output length
- ❌ Adds speculation beyond data
- ❌ Non-comparable across analyses
- ❌ Can't be cached effectively
- ❌ High variance between runs

### Example GOOD Prompt

```
Given behaviors [X, Y, Z], generate ONE sentence (8-15 words, 
present tense, capture common intent). Output only the sentence.
```

**Why it works:**
- ✅ Fixed output format
- ✅ Stays close to data
- ✅ Comparable across analyses
- ✅ Cacheable effectively
- ✅ Low variance (temp=0.3)

### Temperature Settings

| Task | Temperature | Why |
|------|------------|-----|
| **Description generation** | 0.3 | Low variance, predictable |
| **Expertise justification** | 0.5 | Slight creativity allowed |
| **Never use** | 0.8+ | Too creative for CBAC |

---

## Cost Analysis

### OpenAI Pricing (December 2024)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| GPT-4 Turbo | $10.00 | $30.00 |
| GPT-3.5 Turbo | $0.50 | $1.50 |
| text-embedding-3-small | $0.02 | - |

### Cost per 1000 Analyses

| Scenario | LLM Calls | Cost | Monthly (10K users) |
|----------|-----------|------|---------------------|
| **No caching** | 1000 | $100 | $1,000 💸 |
| **70% cache hit** | 300 | $30 | $300 ✅ |
| **90% cache hit** | 100 | $10 | $100 ✅✅ |
| **Overuse (5 calls/analysis)** | 5000 | $500 | $5,000 ❌❌ |

**Target:** 70-80% cache hit rate = **$25-30 per 1000 analyses**

### Cost Optimization Strategies

1. **Semantic Caching** (saves 70-80%)
   - Reuse descriptions for similar clusters
   - Expected savings: **$70-80 per 1000 analyses**

2. **Use GPT-3.5 Turbo** (not GPT-4)
   - 20x cheaper than GPT-4
   - Quality sufficient for description generation
   - Expected savings: **$90 per 1000 analyses**

3. **Batch Processing** (saves 10-20%)
   - Process multiple behaviors in one call
   - Reduce per-request overhead
   - Expected savings: **$10-20 per 1000 analyses**

4. **Fail Fast** (saves 5-10%)
   - 5-second timeout on LLM calls
   - Fall back to templates quickly
   - Prevents cost spikes from hangs

**Combined optimization: $100 → $25-30 per 1000 analyses (70-75% savings)**

---

## Fallback Strategy (Critical)

### Three-Tier Approach

```python
async def generate_description(self, cluster, behaviors):
    """
    Multi-tier description generation with graceful degradation
    """
    
    # Tier 1: Semantic cache (fastest, free, 70-80% hit)
    cached = await self.cache.get(cluster)
    if cached:
        logger.info(f"Cache hit for cluster {cluster.cluster_id}")
        return cached, 0.98  # slight confidence penalty
    
    # Tier 2: LLM (best quality, costs money, 20-30% usage)
    try:
        description = await self.llm_service.generate(
            behaviors=behaviors,
            timeout=5.0  # fail fast
        )
        await self.cache.set(cluster, description)
        logger.info(f"LLM generated description for {cluster.cluster_id}")
        return description, 1.0
    
    except (TimeoutError, RateLimitError, APIError) as e:
        logger.warning(f"LLM failed: {e}, falling back to template")
        
    # Tier 3: Template (always works, 100% uptime guarantee)
    description = self._generate_template(cluster, behaviors)
    return description, 0.85  # larger confidence penalty
```

### Why Fallback Matters

**Scenarios where LLM fails:**
- Network timeout
- OpenAI API rate limit
- OpenAI downtime
- Invalid API key
- Budget exceeded

**Without fallback:** System crashes ❌
**With fallback:** System degrades gracefully ✅

**Key principle:** LLM is **preferred but not required** for system operation.

---

## Anti-Patterns: What NOT to Do

### ❌ DON'T: Use LLM for Clustering

**Why:** Clustering is deterministic and fast. LLM would be:
- 100x slower
- Non-reproducible
- Expensive ($1-2 per analysis)
- Unnecessary (DBSCAN works perfectly)

**Current (correct):**
```python
clusterer = DBSCAN(eps=0.5, min_samples=2)
labels = clusterer.fit_predict(embeddings)
```

**Anti-pattern (wrong):**
```python
# DON'T DO THIS
prompt = "Group these behaviors into clusters..."
clusters = await llm_service.generate(prompt)
```

---

### ❌ DON'T: Use LLM for Confidence Calculation

**Why:** Confidence must be:
- Reproducible (same inputs → same output)
- Explainable (show the formula)
- Auditable (verify calculations)
- Comparable across time

LLMs are probabilistic and opaque.

**Current (correct):**
```python
confidence = (0.35 * credibility + 
              0.25 * stability + 
              0.25 * coherence + 
              0.15 * reinforcement)
```

**Anti-pattern (wrong):**
```python
# DON'T DO THIS
prompt = "Rate confidence of this behavior pattern..."
confidence = await llm_service.generate(prompt)
```

---

### ❌ DON'T: Use LLM for Change Detection

**Why:** Change detection is:
- Exact comparison (domain matching by string)
- Numeric thresholds (confidence delta > 0.15)
- Version tracking (integer increments)

No linguistic reasoning needed.

**Current (correct):**
```python
for current in current_behaviors:
    for previous in previous_behaviors:
        if current.domain == previous.domain:
            delta = abs(current.confidence - previous.confidence)
            if delta > 0.15:
                updated.append(current)
```

**Anti-pattern (wrong):**
```python
# DON'T DO THIS
prompt = "Did this behavior change from last time?..."
changed = await llm_service.generate(prompt)
```

---

### ❌ DON'T: Use LLM for Expertise Scoring

**Why:** Expertise is calculated from:
- Reinforcement counts (numeric)
- Temporal stability (numeric)
- Confidence scores (numeric)
- Domain breadth (count)

LLM adds no value to numeric calculations.

**Correct approach:**
```python
# Calculate numerically
expertise_score = (0.30 * depth_score +
                   0.25 * breadth_score +
                   0.20 * confidence_score +
                   0.15 * stability_score +
                   0.10 * evolution_score)

# LLM only for justification text (optional)
justification = await llm_service.generate(
    f"Explain why score {expertise_score} indicates {level}"
)
```

---

### ✅ DO: Use LLM ONLY for Description Generation

**Why:** This is the ONLY place where:

- Input: Multiple similar text strings
- Output: One clean, readable sentence
- Requirement: Human-interpretable abstraction
- Benefit: Saves hundreds of brittle templates
- Can be cached: Similar clusters reuse descriptions

**This is the ONLY justified LLM use in CBAC.**

---

## Example (Non-Learning Domain)

### Cluster:

```
- "breaks problems into steps"
- "asks clarifying questions before solving"
- "confirms assumptions"
- "validates solution approach"
```

### LLM Output:

> "Uses structured, step-by-step problem solving"

### Try Generating Without LLM:

**Template approach:**
```python
f"User shows {domain} behavior pattern"
→ "User shows problem-solving behavior pattern"
```
❌ Generic, meaningless

**Keyword intersection:**
```python
common_words = ["steps", "clarifying", "assumptions", "validates"]
→ "steps clarifying assumptions validates"
```
❌ Not a sentence

**TF-IDF:**
```python
top_terms = ["solving", "questions", "approach"]
→ "solving questions approach"
```
❌ Incoherent

**LLM (constrained):**
```
"Uses structured, step-by-step problem solving"
```
✅ Clean, readable, accurate

**That's why the LLM exists.**

---

## The Decision Rule

**If the output must be:**

* one sentence
* human-readable
* stable across time
* comparable across users
* not achievable with templates

**Then the LLM is justified.**

**If it's doing anything else** — you're misusing it.

---

## Final Reality Check

### If You Removed the LLM:

* ✅ The system still runs
* ✅ The math still works
* ❌ **But your outputs become unreadable, inconsistent, and unusable**

**Current state:** Using templates (functional but brittle)
**Target state:** Using LLM with cache (better quality, scalable)

### If You Overused the LLM:

* ❌ Costs explode ($1000+ per month)
* ❌ Outputs drift (non-deterministic results)
* ❌ Trust collapses (can't reproduce analyses)
* ❌ System becomes slow (LLM calls are 100x slower than math)

### Current Design: ✅ Correct

Your design uses the LLM **correctly** — narrowly, defensively, and sparingly:

1. ✅ Only for description generation
2. ✅ Only after promotion (not for rejected clusters)
3. ✅ With semantic caching (70-80% hit rate)
4. ✅ With fallback to templates (100% uptime)
5. ✅ With low temperature (0.3 = predictable)
6. ✅ With constrained prompts (8-15 words)

**The LLM is not the brain. It's a label maker.**

---

## Implementation Checklist

When implementing LLM integration:

### Phase 1: Core Service (4-5 hours)
- [ ] Create `llm_service.py` with OpenAI client
- [ ] Implement error handling (timeout, rate limit, API errors)
- [ ] Add retry logic with exponential backoff
- [ ] Configure temperature=0.3, max_tokens=50
- [ ] Test with sample cluster

### Phase 2: Semantic Cache (3-4 hours)
- [ ] Create `semantic_cache.py` with Qdrant integration
- [ ] Implement `get()` with similarity search (threshold=0.92)
- [ ] Implement `set()` with cluster size validation
- [ ] Add reuse count tracking
- [ ] Test cache hit/miss scenarios

### Phase 3: Integration (2-3 hours)
- [ ] Update `core_analyzer.py` to call LLM service
- [ ] Add three-tier fallback (cache → LLM → template)
- [ ] Apply confidence penalties (0.98 for cache, 0.85 for template)
- [ ] Add logging for cache hits, LLM calls, fallbacks
- [ ] Test end-to-end analysis

### Phase 4: Prompt Engineering (2-3 hours)
- [ ] Design constrained prompts (8-15 words, present tense)
- [ ] Test prompts with various cluster types
- [ ] Validate output format and quality
- [ ] Create prompt templates for different domains
- [ ] Document prompt design principles

### Phase 5: Cost Monitoring (1-2 hours)
- [ ] Add cost tracking per API call
- [ ] Calculate cache hit rate
- [ ] Monitor monthly spending
- [ ] Set budget alerts
- [ ] Document cost optimization results

### Phase 6: Testing (3-4 hours)
- [ ] Test with 100+ real clusters
- [ ] Measure quality vs templates
- [ ] Validate cache effectiveness
- [ ] Test fallback scenarios
- [ ] Performance benchmarking

**Total: 15-21 hours (2-3 days full-time)**

---

## Next Steps

Ready to implement? You'll need:

1. **OpenAI API Key**
2. **Model preference** (recommend: GPT-3.5 Turbo)
3. **Budget limit** (recommend: start with $50/month)

Then we build:
- `cbac_api/app/services/llm_service.py`
- `cbac_api/app/services/semantic_cache.py`
- `cbac_api/app/config/llm_config.py`
- `cbac_api/app/prompts/behavior_synthesis.txt`

**The system transforms from templates to intelligent abstraction.**

---

*Document revised: December 15, 2025*
*Implementation status: Phase P0 complete, P2 LLM integration planned*
