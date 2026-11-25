#!/usr/bin/env python3
"""Figure of the review's steps and who did each one: the authors, an AI assistant, or a script (v0.19, 13 Nov 2026).

Asked for in the final pass (Section 3.4: "a diagram showing how the papers got retrieved and extracted, with the AI
and human involvement specified"). The steps and their actors follow the declaration of the use of AI tools (Section
10) and Sections 3.1 to 3.4 and 3.7. A step marked open (dashed border) is one the authors have still to complete;
set it to done here and rerun when it is done.
Usage: python3 -I scripts/make_fig_workflow.py figures/fig_workflow.pdf
"""
import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

OUT = sys.argv[1]
AUTH, AI, SCRIPT = '#F8D9B0', '#CFE0F5', '#E3E3E3'
WHO = {'authors': [AUTH], 'ai': [AI], 'script': [SCRIPT], 'authors+ai': [AUTH, AI], 'ai+script': [AI, SCRIPT]}

# (title, who line, actor, open)
LEFT = [
    ('Curated corpus of SMOTE papers', 'chosen by the authors', 'authors', False),
    ('Coding rules for three extractions', 'written by the authors', 'authors', False),
    ('Method, data and evaluation extractions', 'AI under the rules; an author led each', 'authors+ai', False),
    ('Section drafts of the three extractions', 'written by the authors', 'authors', False),
    ('Blind second pass of a random sample', 'AI, in separate sessions', 'ai', False),
    ('Adjudication of the disagreements', "AI, under the authors' conventions", 'ai', False),
    # v0.31: an author spot-checked 80 adjudications on the page WP3 Check (D31); the step is done
    ('Spot check of the adjudication', 'the authors, on a review page', 'authors', False),
    # v0.41 (D63): after the last AI pass the authors read, edit and approve every sentence
    ('Synthesis and text of the paper', 'written by the authors; AI helped edit', 'authors+ai', False),
]
RIGHT = [
    ('Search protocol and criteria', 'written by the authors', 'authors', False),
    ('Searches of Scopus, OpenAlex and arXiv', 'run by AI; duplicates removed by a script', 'ai+script', False),
    ('Screen of titles and abstracts', 'AI, three looks by separate sessions', 'ai', False),
    ('Independent check of the screen', 'a second AI model', 'ai', False),
    ('Rulings on the criteria', 'by the authors; applied by AI and a script', 'authors+ai', False),
    # v0.38: the authors decided not to check the screen record by record (Last Pass, 16 Nov 2026); the records left
    # unsure are excluded at the final merge (D28), so the step of their check is gone
    ('Random samples: coverage and use audit', 'drawn by a script', 'script', False),
    # v0.25 (D42): the samples are coded twice, blind, and an AI session adjudicates; v0.38: done, and an author
    # spot-checked the adjudication on review pages
    ('Full texts of the samples coded twice', 'PDFs: the authors; blind codings, adjudication: AI', 'authors+ai', False),
    ('Spot check of the adjudication', 'the authors, on review pages', 'authors', False),
]

plt.rcParams.update({'font.family': 'serif', 'font.size': 7})
fig, ax = plt.subplots(figsize=(6.6, 4.75))
ax.set_xlim(0, 6.6)
ax.set_ylim(0, 4.75)
ax.axis('off')
W, H, GAP = 3.0, 0.4, 0.105
TOP = 4.32


def box(x, y, title, who, actor, is_open):
    cols = WHO[actor]
    part = W / len(cols)
    for i, c in enumerate(cols):
        ax.add_patch(Rectangle((x + i * part, y), part, H, facecolor=c, edgecolor='none', zorder=1))
    ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle='square,pad=0', fill=False, lw=0.6,
                                linestyle=(0, (3, 2)) if is_open else '-', edgecolor='black', zorder=2))
    ax.text(x + W / 2, y + H * 0.64, title, ha='center', va='center', fontsize=6.6, fontweight='bold', zorder=3)
    ax.text(x + W / 2, y + H * 0.27, who, ha='center', va='center', fontsize=6.2, style='italic', zorder=3)


def column(x, steps, head):
    ax.text(x + W / 2, TOP + 0.24, head, ha='center', va='center', fontsize=7, fontweight='bold')
    ys = []
    for k, (title, who, actor, is_open) in enumerate(steps):
        y = TOP - H - k * (H + GAP)
        box(x, y, title, who, actor, is_open)
        ys.append(y)
    for y0, y1 in zip(ys, ys[1:]):
        ax.annotate('', xy=(x + W / 2, y1 + H), xytext=(x + W / 2, y0),
                    arrowprops=dict(arrowstyle='-|>', lw=0.6, color='black', shrinkA=0, shrinkB=0))
    return ys


column(0.15, LEFT, 'The corpus and its three extractions')
column(3.45, RIGHT, 'The systematic search and its samples')
# legend
lx, ly = 0.15, 0.0
LEGEND = [('the authors', [AUTH], False), ('an AI assistant', [AI], False), ('a script', [SCRIPT], False),
          ('both', [AUTH, AI], False)]
if any(s[3] for s in LEFT + RIGHT):   # v0.38: the dashed key only while a step is open
    LEGEND.append(('still to be completed', ['white'], True))
for label, cols, dashed in LEGEND:
    for i, c in enumerate(cols):
        ax.add_patch(Rectangle((lx + i * 0.11, ly), 0.11, 0.13, facecolor=c, edgecolor='none'))
    ax.add_patch(Rectangle((lx, ly), 0.11 * len(cols), 0.13, fill=False, lw=0.5, linestyle=(0, (3, 2)) if dashed else '-'))
    ax.text(lx + 0.11 * len(cols) + 0.06, ly + 0.065, label, va='center', fontsize=6.4)
    lx += 0.11 * len(cols) + 0.06 + 0.052 * len(label) + 0.3
fig.savefig(OUT, bbox_inches='tight', pad_inches=0.02)
print('wrote', OUT)
