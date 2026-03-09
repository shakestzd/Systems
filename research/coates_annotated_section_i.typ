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
        align(right)[Coates · "The Case for Reparations" · Section I],
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
#let c-inv    = rgb("#C4600A")   // Named actor / inventory — amber
#let c-loss   = rgb("#B03030")   // Accumulating losses — red
#let c-policy = rgb("#1E5FA8")   // Policy / structure — blue
#let c-quote  = rgb("#6B3A9E")   // Witness quote as verdict — purple
#let c-juxt   = rgb("#207A4A")   // Juxtaposed sentence pair — green
#let c-arch   = rgb("#2C3E50")   // Architecture analysis — dark slate
#let c-note   = luma(130)        // "What he didn't do" — gray

// ── Reusable Components ─────────────────────────────────────────────────────

// Yellow highlight for key phrases within passages
#let hl(body) = highlight(fill: rgb("#FFF2A8"), extent: 1.5pt, body)

// Passage block — the quoted article text
#let passage(body) = {
  v(0.5em)
  block(
    fill: luma(250),
    stroke: (left: 3.5pt + luma(175)),
    inset: (left: 18pt, right: 16pt, top: 12pt, bottom: 12pt),
    radius: (right: 4pt),
    width: 100%,
  )[#text(size: 10pt, style: "normal")[#body]]
  v(0.2em)
}

// Technique annotation callout
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

// "What he didn't do" — secondary note
#let didnt(body) = {
  block(
    fill: luma(247),
    stroke: (left: 2pt + luma(195)),
    inset: (left: 13pt, right: 13pt, top: 8pt, bottom: 8pt),
    radius: (right: 4pt),
    width: 100%,
  )[
    #text(fill: luma(120), weight: "bold", size: 8pt, tracking: 0.5pt)[WHAT HE DIDN'T DO]
    #v(4pt)
    #text(size: 9pt, fill: luma(70), style: "italic")[#body]
  ]
  v(0.5em)
}

// Section heading
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
  #text(size: 24pt, weight: "bold", tracking: -0.5pt)[So That's Just One Of My Losses]
  #v(0.4em)
  #text(size: 11pt, style: "italic", fill: luma(60))[Section I of "The Case for Reparations"]
  #v(0.25em)
  #text(size: 9.5pt, fill: luma(110))[Ta-Nehisi Coates · _The Atlantic_ · June 2014]
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
  #text(weight: "bold", size: 8.5pt, tracking: 0.5pt)[#upper[How to use this document]]
  #v(5pt)
  #text(size: 9pt)[Passages from the article appear in shaded blocks. #hl[Yellow highlighting] marks the specific words doing structural work. Colored callouts below each passage name the technique and explain what it does. *"What he didn't do"* notes show the choice Coates made by omission — these are equally instructive. The final section maps the architecture of the whole piece.]
]

#v(0.8em)

// ── Legend ──────────────────────────────────────────────────────────────────
#text(weight: "bold", size: 8.5pt, tracking: 0.5pt)[#upper[Technique Legend]]
#v(0.4em)
#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 6pt,
  block(fill: c-inv.lighten(90%),    stroke: (left: 3pt + c-inv),    inset: (x: 10pt, y: 7pt), radius: (right: 3pt), width: 100%)[#text(fill: c-inv,    size: 8pt, weight: "bold")[Named Actor / Inventory]],
  block(fill: c-loss.lighten(90%),   stroke: (left: 3pt + c-loss),   inset: (x: 10pt, y: 7pt), radius: (right: 3pt), width: 100%)[#text(fill: c-loss,   size: 8pt, weight: "bold")[Accumulating Losses]],
  block(fill: c-policy.lighten(90%), stroke: (left: 3pt + c-policy), inset: (x: 10pt, y: 7pt), radius: (right: 3pt), width: 100%)[#text(fill: c-policy, size: 8pt, weight: "bold")[Policy / Structure]],
  block(fill: c-quote.lighten(90%),  stroke: (left: 3pt + c-quote),  inset: (x: 10pt, y: 7pt), radius: (right: 3pt), width: 100%)[#text(fill: c-quote,  size: 8pt, weight: "bold")[Witness Quote as Verdict]],
  block(fill: c-juxt.lighten(90%),   stroke: (left: 3pt + c-juxt),   inset: (x: 10pt, y: 7pt), radius: (right: 3pt), width: 100%)[#text(fill: c-juxt,   size: 8pt, weight: "bold")[Juxtaposed Sentence Pair]],
  block(fill: c-arch.lighten(90%),   stroke: (left: 3pt + c-arch),   inset: (x: 10pt, y: 7pt), radius: (right: 3pt), width: 100%)[#text(fill: c-arch,   size: 8pt, weight: "bold")[Architecture / Structure]],
)

// ═══════════════════════════════════════════════════════════════════════════
// 1. THE OPENING
// ═══════════════════════════════════════════════════════════════════════════

#section("1 · The Opening: An Inventory Before a Theft")

#passage[
  #hl[*Clyde Ross was born in 1923*, the seventh of 13 children, near *Clarksdale, Mississippi*.] Ross's parents owned and farmed a #hl[*40-acre tract of land*], flush with #hl[*cows, hogs, and mules*]. Ross's mother would drive to Clarksdale to do her shopping in a #hl[*horse and buggy*], in which she invested all the pride one might place in a Cadillac. The family owned another horse, #hl[*with a red coat*], which they gave to Clyde.
]

#callout(c-inv, "Named Actor + Specific Inventory")[
  The opening paragraph contains: a full name, a birth year, a birth order, a place name, an acreage, a list of animals, a vehicle, a coat color. Coates does not open with a thesis about systemic dispossession. He opens with a *catalog of what existed*.

  This is the inventory before the theft. Every item listed here will be taken before the section ends. The specificity feels like texture; it is actually evidence. When the authorities seize "the cows, hogs, and mules" twelve paragraphs later, the animals are already familiar to the reader.
]

#didnt[
  He did not write "A black family in Mississippi owned a farm." The abstract sentence cannot be stolen. The 40-acre tract with cows, hogs, and mules can be --- and is.
]

// ═══════════════════════════════════════════════════════════════════════════
// 2. THE HORSE
// ═══════════════════════════════════════════════════════════════════════════

#section("2 · The Horse: A Number Without Commentary")

#passage[
  Then, when Ross was 10 years old, #hl[a group of white men demanded his only childhood possession --- the horse with the red coat.] "You can't have this horse. We want it," one of the white men said. #hl[They gave Ross's father *\$17*.]
]

#callout(c-inv, "Named Antagonist + Dollar Amount")[
  The antagonists are unnamed --- "a group of white men" --- because their names don't matter; their position in the system does. What matters is the price: *\$17*. Coates does not call the amount insulting or inadequate. He places it at the end of a sentence, with no commentary after it.

  The number delivers its own verdict. The reader does the arithmetic: a horse with a red coat that a 10-year-old loved, the only thing he owned, valued at \$17. The conclusion arrives without being stated.
]

#passage[
  "I did everything for that horse," Ross told me. "#hl[*Everything.* And they took him.] Put him on the racetrack. I never did know what happened to him after that, but I know they didn't bring him back. #hl[*So that's just one of my losses.*]"
]

#callout(c-loss, "The Title Sentence as Structural Key")[
  "So that's just one of my losses" is the section's title --- and it is Ross's words, not Coates's. Coates gives Ross the title. This matters structurally: every subsequent loss in the article is measured against this one, which Ross himself frames as minor. "Just one" does analytical work that no authorial sentence could match. It tells the reader, before the section has barely begun, that there is far more to come --- and that Ross has already absorbed the accounting.
]

#didnt[
  He did not write "This was only the beginning of Ross's losses." He let Ross say it, in Ross's own voice and register, and titled the section with it.
]

// ═══════════════════════════════════════════════════════════════════════════
// 3. THE LAND SEIZURE
// ═══════════════════════════════════════════════════════════════════════════

#section("3 · The Land: Closing Every Route of Recourse")

#passage[
  When Clyde Ross was still a child, #hl[Mississippi authorities claimed his father owed *\$3,000 in back taxes*]. *The elder Ross could not read. He did not have a lawyer. He did not know anyone at the local courthouse. He could not expect the police to be impartial.* Effectively, the Ross family had no way to contest the claim and no protection under the law. #hl[The authorities *seized the land*. They *seized the buggy*. They *took the cows, hogs, and mules*.] And so for the upkeep of separate but equal, #hl[the entire Ross family was reduced to sharecropping].
]

#callout(c-loss, "Accumulating Losses + Return of the Inventory")[
  The animals listed in the opening paragraph reappear here --- seized. "The cows, hogs, and mules" means something now that it did not in the first paragraph because we watched them established first. The opening inventory was not scene-setting. It was a list of what would be taken.

  Notice the four short consecutive sentences in the middle: *"He could not read. He did not have a lawyer. He did not know anyone at the local courthouse. He could not expect the police to be impartial."* No sentence says "he was defenseless." The four sentences produce that conclusion by removing each route of recourse one at a time. The structure is the argument.
]

#didnt[
  He did not write "Ross's father had no legal recourse." That's the conclusion. Coates gives you the four conditions and withholds the stated conclusion so you have to reach it yourself. A conclusion the reader reaches holds with more conviction than a conclusion they were given.
]

// ═══════════════════════════════════════════════════════════════════════════
// 4. THE SUIT
// ═══════════════════════════════════════════════════════════════════════════

#section("4 · The Suit: Small Loss, No Commentary")

#passage[
  One year Ross's mother promised to buy him a #hl[*\$7 suit*] for a summer program at their church. She ordered the suit by mail. But that year Ross's family was paid #hl[*only five cents a pound for cotton*]. The mailman arrived with the suit. The Rosses could not pay. The suit was sent back. #hl[*Clyde Ross did not go to the church program.*]
]

#callout(c-loss, "The Small Loss — No Commentary")[
  A \$7 suit. Coates does not note the irony that a family working in cotton fields could not afford a \$7 suit. He gives you the price of the suit and the price per pound of cotton and lets you do the arithmetic. The final sentence records the only consequence: he didn't go. Not "this was humiliating." Not "this taught him that the system was rigged." Just: he didn't go.

  This is the technique applied to a minor incident. The discipline is the same as for the major ones. Every detail has a function. No sentence adds interpretation. The emotional weight arrives from the gap between the promise and the outcome.
]

// ═══════════════════════════════════════════════════════════════════════════
// 5. CHICAGO: THE RETURN LOOP
// ═══════════════════════════════════════════════════════════════════════════

#section("5 · Chicago: The Return Loop")

#passage[
  Ross was shipped off to Guam. #hl[He fought in World War II *to save the world from tyranny*.] But when he returned to Clarksdale, #hl[he found that *tyranny had followed him home*.]
]

#callout(c-arch, "The Return Loop — One Word, Two Referents")[
  Coates uses the word "tyranny" twice in consecutive sentences with opposite referents. The first: the tyranny Ross went to war to defeat. The second: the tyranny waiting for him at home. No editorializing is required. The word does the work by appearing twice in the same context. The reader's own knowledge of what tyranny means closes the gap --- and produces the conclusion that the domestic situation is as serious as the wartime one.
]

#passage[
  His journey from peonage to full citizenship #hl[*seemed* near-complete]. Only one item was missing --- a home.
]

#callout(c-arch, "The Incomplete Arrival — 'Seemed'")[
  "Seemed" is the operative word. It signals that what follows will contradict the apparent arrival. "Only one item was missing" sets up the contract-buying section --- which will show that the item was not just missing but actively withheld by a structured system. The single word "seemed" carries the tension of the entire next section before it begins.
]

// ═══════════════════════════════════════════════════════════════════════════
// 6. THE CONTRACT
// ═══════════════════════════════════════════════════════════════════════════

#section("6 · The Contract: Personal Story Before Policy Mechanism")

#passage[
  Ross had bought his house for #hl[*\$27,500*]. The seller, not the previous homeowner but a new kind of middleman, had bought it for only #hl[*\$12,000 six months before*] selling it to Ross. In a contract sale, #hl[the seller kept the deed until the contract was paid in full] --- and, unlike with a normal mortgage, Ross would acquire no equity in the meantime. If he missed a single payment, he would immediately forfeit his #hl[*\$1,000 down payment, all his monthly payments, and the property itself*].
]

#callout(c-policy, "Personal Story Before Policy Mechanism")[
  Coates explains the contract mechanism --- a legal structure --- through Ross's specific numbers. \$27,500 vs. \$12,000 is the argument. The six-month gap is the argument. He does not need to call this exploitative. The \$15,500 markup in six months says it.

  Notice the order: *personal story first, mechanism second.* Coates does not explain redlining and then give an example. He shows Ross's specific contract first, then reveals the mechanism that produced it. The policy becomes comprehensible because we already know the person it affected. The reader is invested before the explanation begins.
]

// ═══════════════════════════════════════════════════════════════════════════
// 7. THE FHA
// ═══════════════════════════════════════════════════════════════════════════

#section("7 · The FHA: The Government Describes Itself")

#passage[
  In 1934, Congress created the Federal Housing Administration. The FHA insured private mortgages, causing a drop in interest rates and a decline in the size of the down payment required to buy a house. #hl[But an insured mortgage was not a possibility for *Clyde Ross*.] The FHA had adopted a system of maps that rated neighborhoods according to their perceived stability. On the maps, green areas, rated "A," indicated "in demand" neighborhoods that, as one appraiser put it, #hl[lacked *"a single foreigner or Negro."*]
]

#callout(c-policy, "Policy Embedded in Personal Story + System Quoting Itself")[
  The FHA is introduced not as an institution but through the sentence "But an insured mortgage was not a possibility for Clyde Ross." We know Ross. The policy becomes personal before it becomes structural.

  Then Coates quotes the FHA appraiser's own language: *"lacked a single foreigner or Negro."* He does not call this racist. He quotes the system describing itself in its own words. The system's language is its own condemnation. Coates's restraint here is what makes the quote land --- if he had written "a racist standard" before showing the quote, the quote would feel redundant.
]

#passage[
  "A government offering such bounty to builders and lenders could have required compliance with a nondiscrimination policy," #hl[Charles Abrams], the urban-studies expert who helped create the New York City Housing Authority, wrote in 1955. "Instead, #hl[the FHA adopted a racial policy that could well have been culled from the Nuremberg laws]."
]

#callout(c-quote, "Attributed Judgment")[
  "The FHA's racial policy resembled the Nuremberg laws" is a strong claim. Coates does not make it himself --- he quotes a *named expert from 1955* making it. The attribution does two things simultaneously: it is not Coates's polemic, and it shows the judgment was available at the time of the events, not retrojected from the present. A contemporaneous verdict from a named source is evidence. An unattributed editorial claim from the author is opinion.
]

// ═══════════════════════════════════════════════════════════════════════════
// 8. THE SAFARI QUOTE
// ═══════════════════════════════════════════════════════════════════════════

#section("8 · The Safari Quote: Witness as Verdict")

#passage[
  "It was like people who like to go out and shoot lions in Africa. It was the same thrill," a housing attorney told the historian Beryl Satter in her 2009 book. #hl[*"The thrill of the chase and the kill."*]
]

#callout(c-quote, "Witness Quote as Verdict")[
  This is the most efficient sentence in the section. Coates has spent several paragraphs documenting the contract-selling system without calling it predatory, cruel, or exploitative. Then he quotes an insider --- a housing attorney who operated in this world --- describing it in their own words as *sport killing*.

  The quote delivers the verdict that the entire preceding section built toward. It arrives last because it can only land if the evidence has been assembled first. Placed earlier, before the reader knows what the contract system did to Ross, the quote would feel rhetorical. Placed here, it feels inevitable.
]

#didnt[
  He did not follow the quote with "This attitude captures the moral reality of contract selling." The quote is the last word on the subject. No sentence after it is needed --- and adding one would dilute the effect.
]

// ═══════════════════════════════════════════════════════════════════════════
// 9. THE PIVOT SENTENCE PAIR
// ═══════════════════════════════════════════════════════════════════════════

#section("9 · The Pivot: Two Sentences, No Connective Tissue")

#passage[
  #hl[*Contract sellers became rich. North Lawndale became a ghetto.*]
]

#callout(c-juxt, "Juxtaposed Sentence Pair — The Technique at Its Purest")[
  Two sentences. No "as a result." No "therefore." No "this is why." Two facts placed next to each other with nothing in between.

  The sentences are also parallel in structure: *"[Subject] became [outcome]."* The parallel structure makes the relationship visible without naming it. The reader supplies the causal link --- which means the reader performs the analytical act. A conclusion the reader reaches themselves is more durable than one they were given.

  These two sentences also function as a section summary. Everything before them was documentation. These two sentences are the verdict --- in fact form, not judgment form.
]

// ═══════════════════════════════════════════════════════════════════════════
// 10. ROSS'S DIALOGUE
// ═══════════════════════════════════════════════════════════════════════════

#section("10 · Ross's Dialogue: Self-Blame as Evidence")

#passage[
  "We were ashamed. We did not want anyone to know that we were that ignorant," Ross told me. "I'd come out of Mississippi where there was one mess, and come up here and got in another mess. #hl[*So how dumb am I?*] I didn't want anyone to know how dumb I was."
]

#callout(c-arch, "Dialogue as Evidence of Structural Effect")[
  Ross blames himself --- "so how dumb am I?" --- for having been systematically deceived by a structure specifically designed to deceive him. Coates does not correct Ross. He does not write "of course, Ross was not dumb; the system was designed to exploit him."

  The self-blame is itself evidence of what the system produced: victims who internalized responsibility for their own exploitation. If Coates had written "Ross blamed himself for what was in fact a systemic trap" --- that would be editorializing. Instead, Ross speaks, and his speech contains the thing Coates would have said. The reader does the correcting.
]

// ═══════════════════════════════════════════════════════════════════════════
// 11. THE FINAL SENTENCE
// ═══════════════════════════════════════════════════════════════════════════

#section("11 · The Final Sentence: Accumulated Meaning")

#passage[
  In 1968, Clyde Ross and the Contract Buyers League were no longer simply seeking the protection of the law. #hl[*They were seeking reparations.*]
]

#callout(c-arch, "The Final Word as Accumulated Meaning")[
  "Reparations" is the article's title concept --- and Coates withholds the word until the final sentence of the first section. By the time it appears, it has been earned by 4,000 words of specific losses: the horse (\$17), the land (\$3,000 tax claim), the suit (\$7), the contract house (\$27,500 vs. \$12,000), the denied mortgage, the FHA maps, the contract sellers' profits.

  The word does not introduce an argument. It names what the preceding section built from evidence. The argument is not ahead of the reader --- it is already assembled behind them.
]

#didnt[
  He did not begin the section with "Reparations are owed because..." He assembled the losses first, then named the conclusion last. This is the discipline of the whole technique: the writer's job is to arrange evidence in an order that makes the conclusion *inevitable* --- not to state it and then support it.
]

// ═══════════════════════════════════════════════════════════════════════════
// 12. ARCHITECTURE
// ═══════════════════════════════════════════════════════════════════════════

#pagebreak()
#section("12 · The Architecture of the Whole Section")

#callout(c-arch, "The Movement of Scale")[
  The section moves from small to large --- personal to structural, individual to national --- but never loses the individual. Three parallel tracks run simultaneously:

  - *Loss scale:* One horse (\$17) → land (\$3,000 claim) → one suit (\$7) → one contract house (\$27,500)
  - *Geographic scale:* One family → one neighborhood (North Lawndale) → one city (Chicago) → one national policy (FHA redlining)
  - *Collective scale:* One man's shame ("so how dumb am I?") → 500-member organization (Contract Buyers League) → one legal concept (reparations)

  Each scale transition is made through a *specific named item, person, or institution* --- never through abstraction alone. The abstraction is always arrived at, never started from.
]

#callout(c-arch, "The Word 'Protection' — Three Instances")[
  Coates uses the phrase "the protection of the law" exactly three times:

  1. *Opening:* what all black families in the Deep South desperately desired
  2. *Great Migration paragraph:* what the pilgrims north were seeking
  3. *Final paragraph:* what the Contract Buyers League was *no longer simply seeking* --- they wanted reparations

  The repetition is structural, not rhetorical. By the third use, the phrase carries the weight of everything the section documented between the first and third instances --- the horse, the land, the FHA maps, the contract sellers. "The protection of the law" is shown to be unavailable at every scale, so that when the League moves past seeking it to demanding reparations, the reader understands why without being told.
]

#callout(c-arch, "What Coates Never Says in His Own Voice")[
  Every one of the following conclusions is reached by the reader. Coates does not state any of them directly:

  - That the system was unjust
  - That Ross was not responsible for his own exploitation
  - That the FHA policy was racist
  - That contract sellers were predatory
  - That reparations are owed

  This is the core discipline. The writer's job is to assemble evidence in an order that produces the inevitable conclusion. Stating the conclusion yourself is not just redundant --- it is weaker, because a stated conclusion can be argued with. A conclusion the reader reaches from evidence cannot.
]

#v(1.5em)
#line(length: 100%, stroke: 0.5pt + luma(210))
#v(0.4em)
#align(center)[#text(size: 8.5pt, fill: luma(150))[Annotated by TZD Labs · March 2026 · For personal study use]]
