// ── Page & Typography ──────────────────────────────────────────────────────
#set page(
  paper: "us-letter",
  margin: (top: 1.8cm, bottom: 2.2cm, left: 3.2cm, right: 3.2cm),
  header: context {
    if counter(page).get().first() > 1 {
      set text(size: 8pt, fill: luma(160))
      grid(
        columns: (1fr, 1fr),
        align(left)[Annotated Reading Guide],
        align(right)[McLean · "Is Enron Overpriced?" · Fortune, March 2001],
      )
      v(-0.4em)
      line(length: 100%, stroke: 0.5pt + luma(210))
    }
  },
  footer: context {
    set text(size: 8pt, fill: luma(160))
    align(center)[#counter(page).display("1 / 1", both: true)]
  }
)

#set text(font: ("Georgia", "Linux Libertine"), size: 10.5pt, lang: "en")
#set par(justify: true, leading: 0.72em, spacing: 1.1em)

// ── Color Palette ───────────────────────────────────────────────────────────
#let c-q      = rgb("#1E5FA8")   // Unanswerable question / reported absence — blue
#let c-num    = rgb("#B03030")   // Numbers contradicting claims — red
#let c-src    = rgb("#C4600A")   // Named source (bull or bear) — amber
#let c-self   = rgb("#6B3A9E")   // Company's own words as evidence — purple
#let c-juxt   = rgb("#207A4A")   // Juxtaposed facts / comparison that collapses — green
#let c-arch   = rgb("#2C3E50")   // Architecture / structure — dark slate
#let c-proj   = rgb("#0D6E6E")   // Connection to this project — teal

// ── Components ──────────────────────────────────────────────────────────────
#let hl(body) = highlight(fill: rgb("#FFF2A8"), extent: 1.5pt, body)

#let passage(body) = {
  v(0.5em)
  block(
    fill: luma(250),
    stroke: (left: 3.5pt + luma(175)),
    inset: (left: 18pt, right: 16pt, top: 12pt, bottom: 12pt),
    radius: (right: 4pt),
    width: 100%,
  )[#text(size: 10pt)[#body]]
  v(0.2em)
}

#let callout(color, technique, body) = {
  block(
    fill: color.lighten(90%),
    stroke: (left: 3.5pt + color),
    inset: (left: 14pt, right: 14pt, top: 10pt, bottom: 10pt),
    radius: (right: 4pt),
    width: 100%,
  )[
    #text(fill: color, weight: "bold", size: 8.5pt, tracking: 0.6pt)[#upper[#technique]]
    #v(5pt)
    #text(size: 9.5pt)[#body]
  ]
  v(0.3em)
}

#let didnt(body) = {
  block(
    fill: luma(247),
    stroke: (left: 2pt + luma(195)),
    inset: (left: 13pt, right: 13pt, top: 8pt, bottom: 8pt),
    radius: (right: 4pt),
    width: 100%,
  )[
    #text(fill: luma(120), weight: "bold", size: 8pt, tracking: 0.5pt)[WHAT SHE DIDN'T DO]
    #v(4pt)
    #text(size: 9pt, fill: luma(70), style: "italic")[#body]
  ]
  v(0.5em)
}

#let project(body) = {
  block(
    fill: c-proj.lighten(92%),
    stroke: (left: 3pt + c-proj),
    inset: (left: 14pt, right: 14pt, top: 10pt, bottom: 10pt),
    radius: (right: 4pt),
    width: 100%,
  )[
    #text(fill: c-proj, weight: "bold", size: 8.5pt, tracking: 0.6pt)[#upper[Connection to this project]]
    #v(5pt)
    #text(size: 9.5pt)[#body]
  ]
  v(0.3em)
}

#let section(title) = {
  v(1.4em)
  block[
    #text(size: 12.5pt, weight: "bold")[#title]
    #v(-0.1em)
    #line(length: 100%, stroke: 0.6pt + luma(210))
  ]
  v(0.2em)
}

// ── Title Block ─────────────────────────────────────────────────────────────
#v(1.5em)
#align(center)[
  #text(size: 8.5pt, fill: luma(140), tracking: 1.5pt, weight: "bold")[#upper[Annotated Reading Guide · Structural Narration]]
  #v(0.7em)
  #text(size: 24pt, weight: "bold", tracking: -0.5pt)[Is Enron Overpriced?]
  #v(0.4em)
  #text(size: 11pt, style: "italic", fill: luma(60))[Fortune Magazine · March 5, 2001]
  #v(0.25em)
  #text(size: 9.5pt, fill: luma(110))[Bethany McLean]
  #v(1.2em)
  #line(length: 55%, stroke: 0.7pt + luma(200))
]

#v(1.2em)

// ── How to Use ──────────────────────────────────────────────────────────────
#block(
  fill: luma(245),
  inset: (x: 16pt, y: 12pt),
  radius: 4pt,
  width: 100%,
)[
  #text(weight: "bold", size: 8.5pt, tracking: 0.5pt)[#upper[How McLean's technique differs from Coates]]
  #v(5pt)
  #text(size: 9pt)[Coates assembles an inventory and shows it destroyed. McLean uses a different structure: she reports the *limits of what can be known*. Her central move is to ask a question that should have a simple answer, show that it cannot be answered from public information, and report that absence as a finding. She never accuses Enron of fraud. She reports a gap --- between the valuation and the available evidence --- and lets that gap be the argument. #hl[Yellow highlighting] marks the specific words doing structural work. Teal callouts mark connections to the dd001 analysis.]
]

#v(0.8em)

// ── Legend ──────────────────────────────────────────────────────────────────
#text(weight: "bold", size: 8.5pt, tracking: 0.5pt)[#upper[Technique Legend]]
#v(0.4em)
#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 6pt,
  block(fill: c-q.lighten(90%),    stroke: (left: 3pt + c-q),    inset: (x: 10pt, y: 7pt), radius: (right: 3pt), width: 100%)[#text(fill: c-q,    size: 8pt, weight: "bold")[Unanswerable Question]],
  block(fill: c-num.lighten(90%),  stroke: (left: 3pt + c-num),  inset: (x: 10pt, y: 7pt), radius: (right: 3pt), width: 100%)[#text(fill: c-num,  size: 8pt, weight: "bold")[Numbers Contradicting Claims]],
  block(fill: c-src.lighten(90%),  stroke: (left: 3pt + c-src),  inset: (x: 10pt, y: 7pt), radius: (right: 3pt), width: 100%)[#text(fill: c-src,  size: 8pt, weight: "bold")[Bull Source Undermining Itself]],
  block(fill: c-self.lighten(90%), stroke: (left: 3pt + c-self), inset: (x: 10pt, y: 7pt), radius: (right: 3pt), width: 100%)[#text(fill: c-self, size: 8pt, weight: "bold")[Company's Own Words]],
  block(fill: c-juxt.lighten(90%), stroke: (left: 3pt + c-juxt), inset: (x: 10pt, y: 7pt), radius: (right: 3pt), width: 100%)[#text(fill: c-juxt, size: 8pt, weight: "bold")[Comparison That Collapses]],
  block(fill: c-proj.lighten(92%), stroke: (left: 3pt + c-proj), inset: (x: 10pt, y: 7pt), radius: (right: 3pt), width: 100%)[#text(fill: c-proj, size: 8pt, weight: "bold")[Connection to This Project]],
)

// ═══════════════════════════════════════════════════════════════════════════
// 1. THE DECK
// ═══════════════════════════════════════════════════════════════════════════

#section("1 · The Deck: The Argument in Three Sentences")

#passage[
  #hl[It's in a bunch of complex businesses.] #hl[Its financial statements are nearly impenetrable.] #hl[*So why is Enron trading at such a huge multiple?*]
]

#callout(c-q, "The Unanswerable Question as Compressed Argument")[
  Most articles state a thesis in the deck. McLean asks a question. Three sentences: (1) complexity, (2) opacity, (3) the question that follows from both. The article never answers this question. That is the point. The deck performs the argument in miniature: complexity + opacity = no basis for the valuation. If the question had an answer, the article wouldn't need to be written.

  This is structurally different from stating "Enron is overvalued." That claim invites refutation. A question that cannot be answered from public information cannot be refuted --- it can only be answered, and the article shows it cannot be.
]

#didnt[
  She did not write "Enron's valuation is not justified by its fundamentals." That's a claim requiring proof. The question is more powerful because it puts the burden on Enron to answer it --- and the article shows they cannot.
]

// ═══════════════════════════════════════════════════════════════════════════
// 2. THE IT STOCK SETUP
// ═══════════════════════════════════════════════════════════════════════════

#section("2 · The Setup: Establishing the Bulls Before Undermining Them")

#passage[
  Right now, that title belongs to Enron, the Houston energy giant. While tech stocks were bombing at the box office last year, fans couldn't get enough of Enron, whose shares returned #hl[*89%*]. By almost every measure, the company turned in a virtuoso performance: #hl[Earnings increased 25%, and revenues more than doubled, to over \$100 billion]. Not surprisingly, the critics are gushing. #hl["Enron has built unique and, in our view, extraordinary franchises in several business units in very large markets," says *Goldman Sachs analyst David Fleischer*.] First Call says that #hl[13 of Enron's 18 analysts rate the stock a buy].
]

#callout(c-src, "Bull Source Establishing the Consensus — Before It Collapses")[
  McLean gives the bulls full voice before questioning them. Fleischer's quote is effusive and specific. The 13-of-18 analyst buy rating is reported as fact. At this point in the article, you are reading what appears to be a profile of a successful company. This is deliberate: the consensus has to be established before the gap can be shown.

  Notice that McLean does not say "bulls claim" or "boosters argue." She simply reports what Fleischer says and what First Call records. The framing is neutral. The neutrality is what makes the subsequent gap credible.
]

#passage[
  Along with "It" status come high multiples and high expectations. Enron now trades at roughly #hl[*55 times trailing earnings*]. That's more than 2.5 times the multiple of a competitor like Duke Energy, more than twice that of the S&P 500, and about on a par with new-economy sex symbol #hl[Cisco Systems]. At a late-January meeting with analysts in Houston, the company declared that it should be valued at #hl[*\$126 a share*, more than 50% above current levels]. "Enron has no shame in telling you what it's worth," says one portfolio manager, who describes such gatherings as #hl[*"revival meetings."*]
]

#callout(c-src, "Named Source Doing Editorial Work Without Editorial Comment")[
  The portfolio manager's phrase "revival meetings" is extraordinary. It characterizes Enron's analyst gatherings as religious performance rather than financial disclosure. McLean quotes it without comment. She doesn't call it apt or cynical. She places it at the end of the paragraph and moves on. The reader supplies the editorial response, which is more durable than if McLean had provided it.
]

#project[
  The dd001 articles are structured around the same consensus. Fourteen analysts project sustained hyperscaler capex. Spend growth has continued at 2x the historical rate. The parallel move in dd001 is to establish the scale of the spending and analyst optimism first --- and then ask whether the revenue exists to justify it. McLean's setup → gap structure is the same architecture.
]

// ═══════════════════════════════════════════════════════════════════════════
// 3. THE CENTRAL QUESTION
// ═══════════════════════════════════════════════════════════════════════════

#section("3 · The Central Question: Absence as Finding")

#passage[
  But for all the attention that's lavished on Enron, the company remains largely impenetrable to outsiders, as even some of its admirers are quick to admit. Start with a pretty straightforward question: #hl[*How exactly does Enron make its money?*] Details are hard to come by because Enron keeps many of the specifics confidential for what it terms "competitive reasons." And the numbers that Enron does present are often extremely complicated. Even quantitatively minded Wall Streeters who scrutinize the company for a living think so. #hl["If you figure it out, let me know," laughs *credit analyst Todd Shipman at S&P*.] #hl["Do you have a year?" asks *Ralph Pellecchia, Fitch's credit analyst*,] in response to the same question.
]

#callout(c-q, "The Unanswerable Question — Repeated by the Bulls Themselves")[
  "How exactly does Enron make its money?" is described as "a pretty straightforward question." That framing is precise and important. McLean is not asking an exotic analytical question. She is asking the most basic possible question about a company. The fact that it cannot be answered is reported --- not editorially characterized --- as a problem.

  More importantly: *it is Enron's own analysts who cannot answer it.* Shipman and Pellecchia are not critics or short-sellers. They scrutinize Enron professionally. Their bewilderment is not McLean's interpretation. It is quoted fact, delivered as dark comedy. McLean does not add "this is alarming." The laughter and the rhetorical question do that work themselves.
]

#callout(c-q, "Reported Absence as Information — The McLean Signature")[
  Count how many times McLean uses some variant of "no way to know," "hard to come by," "difficult to determine," or "unclear" throughout the article. Each instance is a place where a less disciplined writer would have speculated. McLean reports the *limit of available knowledge* as information about Enron's opacity.

  This is structurally rigorous: she cannot be accused of asserting what she doesn't know, because she is reporting what she doesn't know and *why* she doesn't know it. The opacity is on the record. The valuation is on the record. The gap between them is the argument.
]

#project[
  The dd001 off-balance-sheet section uses the same move: Microsoft's reported capex is \$X. Its actual infrastructure commitment includes leases that appear as operating costs, not investment. The question "how much has Microsoft actually committed?" cannot be fully answered from public filings --- and that gap is reported as a structural fact, not an accusation. McLean's "how does Enron make money?" maps directly to "how much of the infrastructure commitment is visible in the reported numbers?"
]

// ═══════════════════════════════════════════════════════════════════════════
// 4. THE GOLDMAN COMPARISON
// ═══════════════════════════════════════════════════════════════════════════

#section("4 · The Goldman Comparison: A Compliment That Collapses")

#passage[
  To some observers, Enron resembles a Wall Street firm. Indeed, people commonly refer to the company as #hl["the Goldman Sachs of energy trading."] That's meant as a compliment. But the fact that part of Goldman's business is inherently risky and impenetrable to outsiders is precisely the reason that #hl[Goldman, despite its powerful franchise, trades at *17 times trailing earnings* --- or less than one-third of Enron's P/E.] And as Long Term Capital taught us, #hl[the best-laid hedges, even those designed by geniuses, can go disastrously wrong.] "Trying to get a good grip on Enron's risk profile is challenging," says Shipman.
]

#callout(c-juxt, "Comparison That Collapses — The Compliment as Evidence Against")[
  This is McLean's most elegant structural move. She accepts the Goldman comparison at face value and follows it to its logical conclusion. *If* Enron is the Goldman Sachs of energy trading, *then* you would expect Enron to trade at Goldman's multiple --- 17x. It trades at 55x. The comparison that was offered as praise becomes evidence that the valuation is incoherent.

  McLean doesn't say "this comparison is wrong." She says "that's meant as a compliment" and then does the arithmetic. The compliment's own logic undoes the valuation claim.

  The Long Term Capital reference is equally efficient. She doesn't argue that Enron's hedges are flawed. She notes, as a fact, that the best-designed hedges can fail --- attributed to observable history, not to McLean's opinion.
]

#didnt[
  She did not write "The Goldman comparison doesn't hold up." She accepted it, followed its logic, and let the numbers produce the contradiction. Accepting the premise and following it to its consequence is more damaging than rejecting the premise outright.
]

// ═══════════════════════════════════════════════════════════════════════════
// 5. THE RETURN ON CAPITAL SENTENCE
// ═══════════════════════════════════════════════════════════════════════════

#section("5 · The Treasury Rate Sentence: One Comparison, No Comment")

#passage[
  Nor at the moment is Enron's profitability close to that of brokerages. While Wall Street firms routinely earn north of 20% returns on equity --- Goldman's ROE last year was 27% --- Enron's rate for the 12 months ended in September was #hl[*13%*]. Even less appealing is Enron's return on *invested capital* (a measure including debt), which is around #hl[*7%*]. #hl[*That's about the same rate of return you get on far less risky U.S. Treasuries.*]
]

#callout(c-num, "Numbers Contradicting Claims — The Single-Sentence Verdict")[
  "That's about the same rate of return you get on far less risky U.S. Treasuries." This sentence does not require a follow-up. It states one comparison --- ROIC of 7% against the risk-free rate --- and stops. McLean adds no interpretation, no "this means," no "therefore." The sentence is complete.

  This is the McLean technique at its most compressed: a single number placed next to a benchmark that everyone understands. The reader knows that no investor should pay a 55x P/E multiple for a company earning the Treasury rate on its capital. McLean doesn't say that. She gives you the 7% and the benchmark and moves on.
]

#project[
  The revenue gap charts in dd001 use the same move: cloud revenue vs. capex spending on the same axis. The visual is the argument. No annotation on the chart says "this is unsustainable." The two lines crossing is the finding. McLean's 7% vs. Treasuries is the prose equivalent of that chart.
]

// ═══════════════════════════════════════════════════════════════════════════
// 6. THE DEBT PARAGRAPH
// ═══════════════════════════════════════════════════════════════════════════

#section("6 · The Debt Paragraph: Claim, Then Number, Then Gap")

#passage[
  There are other concerns: #hl[Despite the fact that Enron has been *talking about reducing its debt*, in the first nine months of 2000 its debt went up substantially.] During this period, Enron issued a net #hl[*\$3.9 billion in debt*], bringing its total debt up to a net #hl[*\$13 billion*] at the end of September and its debt-to-capital ratio up to #hl[*50%*, vs. 39%] at the end of 1999. In 1999 its cash flow from operations fell from #hl[\$1.6 billion the previous year to *\$1.2 billion*]. In the first nine months of 2000, the company generated just #hl[*\$100 million in cash*]. (In fact, #hl[cash flow would have been *negative* if not for the \$410 million in tax breaks] it received from employees exercising their options.)
]

#callout(c-num, "Claim → Number → Gap — The Repeating McLean Structure")[
  This paragraph contains McLean's repeating structural unit in its purest form:

  *Step 1: Report the claim.* "Enron has been talking about reducing its debt."
  *Step 2: Report the number.* Debt went up \$3.9 billion in nine months.
  *Step 3: Stop. Let the gap be the finding.*

  She does not say "this contradicts what they told investors." She reports what they said and what the filings show. The reader performs the comparison. This structure appears at least four times in the article. Each instance adds another data point to the same pattern: the gap between Enron's narrative and its filings.

  The parenthetical about cash flow being negative without the tax break is particularly precise. It is buried in a parenthesis --- as if a minor technical footnote --- but it is the most damaging number in the paragraph.
]

#didnt[
  She did not write "Enron misled investors about its debt reduction efforts." That's an accusation requiring legal proof. She reported what Enron said and what the filing showed. The reader draws the conclusion. And unlike an accusation, a documented gap cannot be refuted by claiming the journalist misunderstood.
]

// ═══════════════════════════════════════════════════════════════════════════
// 7. ENRON'S OWN WORDS
// ═══════════════════════════════════════════════════════════════════════════

#section("7 · Enron's Own Words: The Company Describing Itself")

#passage[
  As for the details about how it makes money, Enron says that's proprietary information, sort of like Coca-Cola's secret formula. Fastow, who points out that Enron has 1,217 trading "books" for different commodities, says, #hl[*"We don't want anyone to know what's on those books. We don't want to tell anyone where we're making money."*]
]

#callout(c-self, "The Company's Own Words as Evidence — No Commentary Needed")[
  Andrew Fastow, Enron's CFO, says the company does not want anyone to know how it makes money. McLean quotes this directly and moves to the next paragraph. No comment. No "this is remarkable." No "this raises questions."

  The quote is its own argument. A publicly traded company whose CFO states that it refuses to disclose how it earns its revenue is describing, in its own words, the same opacity that McLean's central question identified. She does not need to connect those dots for the reader. The CFO has already connected them.

  This is structurally parallel to the safari quote in Coates --- an insider describing the system in their own words, with all the analysis that description requires already present in the words themselves.
]

#callout(c-src, "Skilling's Dismissal as Self-Description")[
  Earlier in the article: *"People who raise questions are people who have not gone through our business in detail and who want to throw rocks at us,"* says Skilling. McLean reports this without response. She has already shown that professional credit analysts at S&P and Fitch --- people who scrutinize Enron for a living --- cannot answer the basic question of how it makes money. Skilling's dismissal of questioners applies to his own analysts. McLean does not point this out. The sequence of the article produces the irony.
]

// ═══════════════════════════════════════════════════════════════════════════
// 8. THE BROADBAND VALUATION
// ═══════════════════════════════════════════════════════════════════════════

#section("8 · Broadband: The Valuation That Contains Its Own Refutation")

#passage[
  Included in the \$126 a share that Enron says it's worth is #hl[*\$40 a share --- or \$35 billion --- for broadband*]. Several of Enron's analysts value broadband at \$25 a share, or roughly \$22 billion (and congratulate themselves for being conservative). But #hl[\$22 billion seems like a high valuation for a business that reported *\$408 million of revenues and \$60 million of losses* in 2000]. "Valuing the broadband business is an 'extremely difficult, uncertain exercise at this point in time,'" notes Bear Stearns' Winters, who thinks that broadband, while promising, is worth some #hl[*\$5 a share today*].
]

#callout(c-num, "The Valuation Gap — \$35 Billion vs. \$408 Million in Revenue")[
  \$35 billion valuation. \$408 million in revenue. \$60 million in losses. McLean places these numbers in the same sentence with no connective commentary. The arithmetic is the argument: Enron is claiming a valuation of roughly 86 times the broadband division's revenue --- for a division losing money.

  The Bear Stearns analyst's \$5/share estimate vs. the conservative analysts' \$25/share vs. Enron's own \$40/share creates a three-point spectrum that shows the range of uncertainty without McLean having to characterize it as "extreme" or "unjustified."
]

#passage[
  But all of these expectations are based on what Wolfe, the J.P. Morgan strategist, calls #hl[*"a little bit of the China syndrome"*] --- in other words, if you get x% of y enormous market, you'll get z in revenues. #hl[The problem, as we know from innumerable failed dot-coms, is that *the y enormous market doesn't always materialize on schedule.*]
]

#callout(c-juxt, "The Dot-Com Reference — Known Pattern, No Accusation")[
  McLean introduces the dot-com comparison not as a direct accusation but as a known historical pattern. "As we know from innumerable failed dot-coms" is reported as shared knowledge, not as McLean's judgment. This is precise: it is not McLean saying Enron is like a dot-com. It is McLean noting that the logical structure of the growth thesis is the same as a category of businesses that recently failed en masse.

  The reader applies the comparison. McLean has only pointed to the pattern.
]

// ═══════════════════════════════════════════════════════════════════════════
// 9. THE FINAL SENTENCE
// ═══════════════════════════════════════════════════════════════════════════

#section("9 · The Final Sentence: One Line After the Quote")

#passage[
  "In the end, it boils down to a question of faith. #hl['Enron is no black box,' says Goldman's Fleischer. 'That's like calling Michael Jordan a black box just because you don't know what he's going to score every quarter.']" Then again, #hl[*Jordan never had to promise to hit a certain number of shots in order to please investors.*]
]

#callout(c-juxt, "The Final Sentence — One Reply, No Argument")[
  This is the most structurally instructive moment in the article. Fleischer has the last bull quote. It is a strong analogy: calling Enron a black box is like calling Jordan a black box because you don't know his scoring output in advance. The implication is that opacity is acceptable when talent is evident.

  McLean writes one sentence in reply. Not a paragraph. One sentence. *Jordan never had to promise to hit a certain number of shots in order to please investors.*

  That sentence contains the entire counter-argument: quarterly earnings guidance creates an obligation that Jordan's performance doesn't carry. The Jordan analogy fails on its own terms. McLean has not made a case against Enron --- she has accepted Fleischer's analogy, identified the one dimension on which it breaks, and stopped.

  The article ends there. No summary. No conclusion. No "therefore, investors should be cautious." The final sentence is the argument.
]

#didnt[
  She did not write "Fleischer's analogy misses the point because..." She let the analogy stand, added one true sentence about what Jordan is not required to do, and ended the piece. The conclusion is the reader's to reach.
]

// ═══════════════════════════════════════════════════════════════════════════
// 10. ARCHITECTURE
// ═══════════════════════════════════════════════════════════════════════════

#pagebreak()
#section("10 · The Architecture of the Whole Article")

#callout(c-arch, "The Repeating Structural Unit — Claim, Number, Gap")[
  McLean's article has no named sections. It moves as a single thread. But it is built from one repeating structural unit, applied six times across the piece:

  1. *Enron says* it has reduced or is reducing its debt → Debt rose \$3.9B in nine months
  2. *Enron says* broadband is worth \$35 billion → Revenue: \$408M, losses: \$60M
  3. *Analysts call* Enron "the Goldman Sachs of energy trading" → Goldman trades at 17x; Enron at 55x
  4. *Enron says* its ROIC is strong → ROIC is 7%, the Treasury rate
  5. *Enron says* cash flow will be "way down, way down" on debt → Cash flow was nearly negative without a tax break
  6. *Analysts value* future market at \$383B → "As we know from innumerable failed dot-coms..."

  Each unit follows the same logic: state the claim, report the number, stop. The accumulation of six instances is the argument. No single instance would sustain it; six instances without a clean answer to any of them is the case.
]

#callout(c-arch, "What McLean Never Argues Directly")[
  McLean does not write any of the following in her own voice:
  - That Enron is committing fraud
  - That Enron's valuation is unjustified
  - That investors should be worried
  - That analysts are wrong to recommend the stock
  - That the opacity is intentional concealment

  Eight months later, Enron collapsed in the largest bankruptcy in U.S. history to that point. Every one of those conclusions turned out to be warranted. McLean did not need to state them. The evidence she assembled from public filings made them available to any reader who followed the arithmetic.

  This is the discipline: the writer's job is to report the gap between the claim and the verifiable evidence. The reader does the rest.
]

#callout(c-arch, "The Article as a Question Article, Not a Findings Article")[
  There is a structural type McLean is working in that deserves its own name: the *question article*. It does not report findings ("we found that Enron is..."). It reports an inability to find what should be findable ("we could not determine how Enron makes its money from public filings"). The negative finding is the positive finding.

  This structure is nearly libel-proof. McLean is not claiming Enron is hiding anything --- she is reporting that the information is not available from public documents. If Enron wanted to refute the article, they would have to disclose the information that is not available. Which they refused to do, because doing so would have revealed the fraud.

  The question structure forces disclosure or silence. Either answer confirms the concern.
]

#project[
  *How this maps to the dd001 articles:*

  The off-balance-sheet section in dd001 uses the same structure: "Here is what the reported capex figures show. Here is what the filings show is not included in those figures (leases counted as operating costs). The question of how much Microsoft has actually committed cannot be answered from reported numbers alone." This is McLean's negative finding applied to infrastructure accounting.

  The revenue gap charts perform McLean's ROIC vs. Treasury move visually: cloud revenue on one line, infrastructure spending on another. The chart does not say "this is unsustainable." The crossing lines say it.

  The CoreWeave chain in dd001-risk uses Fastow's quote structure: CoreWeave's own IPO prospectus shows the dependency chain (CoreWeave → OpenAI → Microsoft) in the company's own language. The prospectus describes the concentration risk. McLean would quote it directly and move on.
]

#v(1.5em)
#line(length: 100%, stroke: 0.5pt + luma(210))
#v(0.4em)
#align(center)[#text(size: 8.5pt, fill: luma(150))[Annotated by TZD Labs · March 2026 · For personal study use]]
