# Nuhyon (nuçongə) — a Hubullu sample project

This repository is a sample project for [**Hubullu**](https://github.com/frodo821/hubullu-lang), a compiler
that turns `.hu` dictionary/grammar definition files into a queryable SQLite database and renders `.hut`
text sources (interlinear source for sentences) into fully inflected prose. The project doubles as a
real-world exercise of the toolchain: a working conlang with phonology, inflectional paradigms, a
lexicon, a 22-chapter textbook, and literary translations, all driven from `.hu`/`.hut` sources.

## The language

**Nuhyon** (endonym *nuçongə*, 日本語: ヌヒョン語) is a constructed language designed as a *descendant
of modern Japanese, projected roughly 1000 years into the future*. It is not "future Japanese" in a
playful sense — it is a typologically grounded daughter language, with regular sound changes, a
reanalyzed morphology, and an attested diachronic path from every form back to its modern Japanese
etymon.

### Typological profile

Nuhyon is a **mixed-type language in the middle of an agglutinative-to-fusional drift**. Different
grammatical domains sit at different points along that drift:

| Domain                  | Morphological type      | Notes                                                   |
| ----------------------- | ----------------------- | ------------------------------------------------------- |
| Nouns / adjectives      | Fusional                | Case + number fused; adjectives agree with heads        |
| Verb TAP (tense/aspect/person) | Fusion in progress | Old layer fused (stem = tense); new layer agglutinative (person affixes) |
| Verbal mood             | Analytic                | Prefixes joined with `~`, not yet grammaticalized       |
| Definiteness            | Analytic                | Invariant proclitic `sə` (< *sorne*)                    |

The ancestor (modern Japanese) has, strictly, only a non-past/realis opposition. Nuhyon's **three-tense
system** arose because modal and pronominal material flowed into what are now tense and person slots:
*non-past* → present, *-ta* (realis) → past, *-darou* (conjecture) → future (`dəro-`); pronominal
reductions such as *vəç* → `-w` and *karl* → `-r` became person endings.

### Phonology in brief

- Vowel inventory: **i, e, æ / ə, a / u, o, ɔ** with three-way harmony (front / back / neutral).
- Consonants include palatal **ç**, velar nasal **ŋ**, and four **syllabic nasals/liquids** (`r̃`,
  `l̃`, `ñ`, `m̃`) that act as syllable nuclei.
- Maximal syllable is CVC(C); word-final consonant clusters only.
- Nasal-contraction sandhi: `ñn, ñm → ñ`; `m̃m, m̃n → m̃`; `ŋl̃ → l̃`.
- Example: "in the book" = *hon* + *-n* → *hñ* + *-ñ* → **hñ**.

### Grammatical highlights

- **8-case nominal system** (nom, acc, dat, loc, gen, abl, all, com) × singular/plural, with
  animacy-sensitive concord.
- **6-aspect system** built around a stative axis: preparatory → inceptive → imperfective →
  terminative → perfective → resultative. Affixes are etymologically transparent: `-sm-` ← *-shimau*,
  `-tr-` ← *-te iru*, `-tk-` ← *-te oku*, `-ds-` ← *-dasu*, `-v-` ← *-oeru*.
- **Supine construction** (tense_stem + allative) for purpose clauses, tense-harmonized with the
  matrix verb.
- **Participles** `-ar` / `-ral` (active/passive) with 18-way vowel-alternation paradigm.
- **Suppletion** in high-frequency verbs (`ik`, `kur`) modeled as stem fusion.
- **Modal negation asymmetry**: synthetic negation = prohibition; periphrastic (participle + negated
  copula) = non-obligation and polite.

## Repository layout

```
main.hu               Lexicon root — re-exports all entry files.
profile.hu            Grammar root — re-exports tags, phonrules, inflections.

core/                 The grammar itself (axes, inflection paradigms, phonology).
  tags.hu               Tag axes: pos, case, tense, aspect, person, harmony, ...
  phonrules.hu          Phonological sandhi rules.
  noun_inflections.hu   Nominal paradigms by stem-final + harmony + animacy.
  verb_inflections.hu   Verbal paradigms (front/back/neutral stems, irregulars).

entries/              The lexicon (.hu dictionary entries).
  noun.hu, pronoun.hu, adjective.hu, particle.hu,
  verb.hu, verb_irregular.hu, verb_su.hu,
  textbook.hu           Vocabulary introduced by textbook chapter.
  alice.hu              Vocabulary used in the Alice translation.

textbook/             22-chapter textbook (.hut sources → rendered sentences).
  ch01.hut ... ch22.hut
  _config.json, design.md

grammatica/           Chapter-by-chapter grammar commentary (Japanese, Markdown).
  ch01.md ... ch22.md

translation/          Literary translation .hut sources.
  bible/genesis-1.hut
  books/alice-ch1.hut

contents/             Jekyll-rendered site (GitHub Pages output).
  index.html, glossary.html, textbook/, bible/, books/

booklet_4th.md        Grammar booklet (Japanese) — fullest description of the language.
TODO.md               Open design questions and outstanding lexical/translation work.

.hubullu-cache/       Hubullu compiler cache (main.huc, project.json).
```

### How the pieces connect

1. **`core/` + `entries/`** are consumed by `main.hu`, which Hubullu compiles into a single
   dictionary database.
2. **`.hut` files** (`textbook/`, `translation/`) reference `main.hu` and specify each word with its
   inflectional feature bundle — e.g.
   `alis_name[case=nom, number=sg] aen[case=com, number=sg] ... swol[tense=past, aspect=result, person=3, number=sg]`.
   Hubullu looks up stems, applies inflection paradigms, and emits fully spelled-out Nuhyon prose.
3. **`contents/`** holds the rendered HTML served by Jekyll (see `_config.yml`) for GitHub Pages.
4. **`grammatica/`** and **`booklet_4th.md`** are the human-readable grammar — not compiled, but kept
   in lockstep with the `.hu` sources.

## Reading order for newcomers

- To understand the language: [`grammatica/`](./grammatica)
  (start with [Chapter 1](./grammatica/ch01); see the
  [grammatica index](./grammatica) for the full 22-chapter tour in three parts).
- To understand the Hubullu format: [`core/tags.hu`](https://github.com/frodo821/nuchonge/blob/main/core/tags.hu) → [`core/noun_inflections.hu`](https://github.com/frodo821/nuchonge/blob/main/core/noun_inflections.hu) → [`entries/noun.hu`](https://github.com/frodo821/nuchonge/blob/main/entries/noun.hu).
- To see the compiler end-to-end: any `.hut` file in [`translation/`](https://github.com/frodo821/nuchonge/tree/main/translation) alongside its
  rendered HTML in [`contents/`](https://github.com/frodo821/nuchonge/tree/main/contents).
