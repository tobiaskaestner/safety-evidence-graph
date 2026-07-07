% T8 — TSF Trustable-Score recurrence as a clingo ruleset (WP-7, analysis probe).
% Reproduces the T5 hand-computed / trudag-observed numbers on the fixture DAG,
% scaled by 1e5 (integer semiring stand-in for [0,1] reals).
%
% TSF semantics reproduced:
%   score(leaf)  = SME value if reviewed, else 0   (T5b: suspect gates the score)
%   score(inner) = mean of children's scores       (T5a: mean propagation)
%
% Run: python3 -m clingo t8_clingo_score.lp     (clingo 5.x)

% -- the fixture DAG (parent supported-by child) --------------------------
link(exp_sched,    assert_lock).
link(assert_lock,  assert_coop).
link(assert_lock,  prem_impl).
link(assert_lock,  prem_test).
link(assert_coop,  prem_impl).

item(X) :- link(X, _).
item(X) :- link(_, X).
leaf(X) :- item(X), not link(X, _).

% -- ground layer: SME scores (scaled 1e5) + review status (the gate) -----
sme(prem_impl, 80000).
sme(prem_test, 60000).
reviewed(prem_impl).
reviewed(prem_test).

% -- the score calculus ----------------------------------------------------
% leaves: SME value, gated by review status (unreviewed => 0, T5b)
score(X, S) :- leaf(X), reviewed(X), sme(X, S).
score(X, 0) :- leaf(X), not reviewed(X).
score(X, 0) :- leaf(X), reviewed(X), not sme(X, _).   % unscored-is-zero

% inner nodes: arithmetic mean of children (integer division; T5a)
nchildren(X, N) :- item(X), N = #count{ C : link(X, C) }, N > 0.
score(X, S) :- nchildren(X, N),
               T = #sum{ SC, C : link(X, C), score(C, SC) },
               S = T / N.

#show score/2.
% Expected (matching trudag 0.4.0 on the fixture, T5a):
%   score(prem_impl, 80000)  score(prem_test, 60000)
%   score(assert_coop, 80000)
%   score(assert_lock, 73333)  score(exp_sched, 73333)
