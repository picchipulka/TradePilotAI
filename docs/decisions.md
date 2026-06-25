Every time we make an important architectural decision, we'll record:

Decision: e.g., "Use Supabase instead of SQLite."
Why: Explain the reasoning.
Alternatives considered: Briefly note other options.
Trade-offs: What we gain and what we give up.

Six months from now, if we wonder "Why did we choose this?" we won't have to rely on memory—we'll have a documented rationale.

I think that's going to make this project much easier to maintain as it grows.

Decision #1: Use Yahoo Finance as the initial market data provider.

Reason: It allows us to validate the market service architecture quickly without introducing API authentication, subscription, or rate-limit complexity.

Long-term direction: Replace or supplement it with Polygon or Alpaca through interchangeable provider modules. The rest of the application should not need to change when switching providers.